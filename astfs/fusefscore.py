#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains subroutines for work with fuse kernel module
"""

from __future__ import with_statement

import os
import errno

# from astfs.constants import USERNAME, GROUPNAME, FMODE,\
# 	DMODE, UID, GID, STARTUPTIME
import logging
from time import time
import fuse
from fuse import Fuse
from astfs.fsstruct import stat_info
from astfs.isobject import isobject
from astfs.logger import logger

fuse.fuse_python_api = (0, 2)

class AstFS(Fuse):
    """
    Core class for Virtual File System
    """
    def __init__(self, **kwargs):
        Fuse.__init__(self, **kwargs)
        # self.mountpoint = self.fuse_args.mountpoint

    def _full_path(self, partial):
        return '%s%s' % (self.fuse_args.mountpoint, partial)

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        """
         access(const char* path, mask)
        This is the same as the access(2) system call.  It returns -ENOENT if
        the path doesn't exist, -EACCESS if the requested permission isn't
        available, or 0 for success.  Note that it can be called on files,
        directories, or any other object that appears in the filesystem.  This
        call is not required but is highly recommended.
        """
        self.logger.info('[FuseFSCore.access] %s:%s. Context: %s', path, mode, self.GetContext())
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            return -errno.EACCES

    def chmod(self, path, mode):
        """
         chmod(const char* path, mode_t mode)
        Change the mode (permissions) of the given object to the given new
        permissions.  Only the permissions bits of mode should be examined.
        See chmod(2) for details.
        """
        self.logger.error('[FuseFSCore.chmod] Unavail option. Chmod %s for \
                           path %s. Context: %s', mode, path, self.GetContext())
        return -errno.EPERM
#        full_path = self._full_path(path)
#        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        """
         chown(const char* path, uid_t uid, gid_t gid
        Change the given object's owner and group to the provided values.  See
        chown(2) for details.
        NOTE: FUSE doesn't deal particularly well with file ownership, since
        it usually runs as an unprivileged user and this call is restricted to
        the superuser.  It's often easier to pretend that all files are owned
        by the user who mounted the filesystem, and to skip implementing this
        function.
        """
        self.logger.error('[FuseFSCore.chown] Unavail option. Chown %s:%s for \
                            %s. Context: %s', uid, gid, path, self.GetContext())
        return -errno.EPERM
#        full_path = self._full_path(path)
#        return os.chown(full_path, uid, gid)

    def getattr(self, path, fhandle=None):
        """
         getattr(const char* path, struct stat* stbuf)
        Return file attributes.  The "stat" structure is described in detail
        in the stat(2) manual page.  For the given pathname, this should fill
        in the elements of the "stat" structure.  If a field is meaningless or
        semi-meaningless (e.g., st_ino) then it should be set to 0 or given a
        "reasonable" value.  This call is pretty much required for a usable
        filesystem.
        =====================================================================
        getattr procedure must return stat object for
        requested path or -errno.ENOENT if path is not found
        """
        self.logger.debug('[FuseFSCore.getattr] path %s fh %s. Context: %s', path, fhandle,self.GetContext())
        #
        # returntree procedure make a recurse search over root object tree
        # returntree can return many types of object
        # object(class) - proceed path with found object(class)
        # callable(function) - proceed path with found callable(function)
        # int - error or status
        # list - static record from root tree
        # dict - static directory record from root tree
        #
        srctree = self.returntree(path, self.root, False)
        self.logger.debug(
            '[FuseFSCore.getattr] Found data %s for path %s',
            srctree, path)
        if isobject(srctree):
            dirtree = srctree._getattr(path)
            self.logger.debug(
                '[FuseFSCore.getattr] Object %s return dirtree %s',
                srctree, dirtree)
        else:
            dirtree = srctree

        attrstat = {}

        if callable(dirtree):
            #
            # dirtree can be a function
            # function must return a list with structure
            # [ {} , '' ]
            # part with index 0 - stat info for object
            # part with index 1 - object data(for object size calculation)
            #
            attrstat.update(stat_info['def'])
            attrstat.update(dirtree()[0])
            attrstat.update(
                {'st_size': len(dirtree()[1]), 'st_mtime': int('%d' % time())})
            self.logger.debug(
                '[FuseFSCore.getattr] dirtree callable %s' % attrstat)
        elif isinstance(dirtree, int):
            #
            # if dirtree type is negative int - error occured or
            # object not found in root tree
            #
            if dirtree < 0:
                return dirtree
            else:
                attrstat.update(stat_info['def'])
        elif isinstance(dirtree, list):
            #
            # if dirtree type is list, use structure
            # [ {} , '' ]
            # part with index 0 - stat info for object
            # part with index 1 - object data(for object size calculation)
            #
            attrstat.update(dirtree[0])
            ###########
            if callable(dirtree[1]):
                #
                # if dirtree part with index 1 is callable
                # request length of data from this callable
                #
                attrstat.update({'st_size': len(dirtree[1](path))})
            elif attrstat['st_size'] == 0:
                attrstat.update({'st_size': len(dirtree[1])})
            ###########
            self.logger.debug('[FuseFSCore.getattr] List %s:%s' %
                              (type(attrstat), attrstat))
        elif isinstance(dirtree, dict):
            #
            # if dirtree type is dict, object is directory
            # and key '__dirstat__' used for object stat,
            # other keys in dirtree object used as count of
            # linked items to this directory objects
            # __dirstat__ key has a structure
            # [ {} , '' ]
            # part with index 0 - stat info for directory object
            # part with index 1 - None or ''
            #
            if '__dirstat__' in dirtree:
                attrstat.update(dirtree['__dirstat__'][0])
                if attrstat['st_nlink'] == 1:
                    attrstat.update({'st_nlink': len(dirtree)})
            else:
                attrstat.update(stat_info['def'])
                attrstat.update(stat_info['file'])

        elif dirtree is None:
            #
            # if dirtree is None - object not found in root tree
            #
            return -errno.ENOENT
        else:
            #
            # any other types for dirtree return stat as file
            #
            attrstat.update(stat_info['def'])
            attrstat.update(stat_info['file'])

        self.logger.debug(
            '[FuseFSCore.getattr] Attrstat Result for object %s is %s:%s',
            path, type(attrstat), attrstat)
        fusest = fuse.Stat()
        for key in attrstat:
            setattr(fusest, key, attrstat[key])
        return fusest

    def readdir(self, path, fhandle=None):
        """
         readdir(const char* path, void* buf, fuse_fill_dir_t filler, off_t
                 offset, struct fuse_file_info* fi)
        Return one or more directory entries (struct dirent) to the caller.
        This is one of the most complex FUSE functions.  It is related to, but
        not identical to, the readdir(2) and getdents(2) system calls, and the
        readdir(3) library function.  Because of its complexity, it is
        described separately below.  Required for essentially any filesystem,
        since it's what makes ls and a whole bunch of other things work.
        """
        self.logger.debug('[FuseFSCore.readdir] Path %s:%s. Context: %s', path, fhandle, self.GetContext())
        srctree = self.returntree(path, self.root, False)
        self.logger.debug(
            '[FuseFSCore.readdir] Found data %s for path %s',
            srctree, path)
        if isobject(srctree):
            dirtree = srctree._readdir(path)
            self.logger.debug(
                '[FuseFSCore.readdir] Object %s return dirtree %s',
                srctree, dirtree)
        else:
            dirtree = srctree

        self.logger.debug(
            '[FuseFSCore.readdir] SrcTree: %s, DirTree: %s:%s',
            srctree, type(dirtree), dirtree)

        dirents = ['.', '..']
        dirents.extend(dirtree.keys())
        for entry in dirents:
            if entry == '__dirstat__':
                continue
            yield fuse.Direntry(entry)

    def readlink(self, path):
        """
         readlink(const char* path, char* buf, size_t size)
        If path is a symbolic link, fill buf with its target, up to size.
        See readlink(2) for how to handle a too-small buffer and for error
        codes.  Not required if you don't support symbolic links.
        NOTE: Symbolic-link support requires only readlink and symlink.  FUSE
        itself will take care of tracking symbolic links in paths, so your
        path-evaluation code doesn't need to worry about it.
        """
        self.logger.debug('[FuseFSCore.readlink] path: %s. Context: %s', path, self.GetContext())
        srctree = self.returntree(path, self.root, True)
        if isobject(srctree):
            dirtree = srctree._readlink(path)
            self.logger.debug('[FuseFSCore.readlink] readlink %s', srctree)
            # dirtree._readlink(path))
            # return None
        else:
            dirtree = srctree
        self.logger.debug('[FuseFSCore.readlink] FoundTree: %s', dirtree)
        if len(dirtree) > 1:
            return dirtree[1]
        else:
            return None

    def mknod(self, path, mode, dev):
        """
         mknod(const char* path, mode_t mode, dev_t rdev)
        Make a special (device) file, FIFO, or socket. See mknod(2) for details.
        This function is rarely needed, since it's uncommon to make these
        objects inside special-purpose filesystems.
        """
        self.logger.error('[FuseFSCore.mknod] Unavail option path %s mode %s \
                            dev %s. Context: %s', path, mode, dev, self.GetContext())
        return -errno.EPERM

    def rmdir(self, path):
        """
         rmdir(const char* path)
        Remove the given directory.  This should succeed only if the directory
        is empty (except for "." and "..").  See rmdir(2) for details.
        """
        self.logger.error('[FuseFSCore.rmdir] Unavail option for path %s. Context: %s', path, self.GetContext())
        return -errno.EPERM

    def mkdir(self, path, mode):
        """
         mkdir(const char* path, mode_t mode)
        Create a directory with the given name.  The directory permissions are
        encoded in mode.  See mkdir(2) for details.  This function is needed
        for any reasonable read/write filesystem.
        """
        self.logger.error('[FuseFSCore.mkdir] Unavail option for path %s\
                            with mode %s. Context: %s', path, mode, self.GetContext())
        return -errno.EPERM

    def statfs(self):
        """
         statfs(const char* path, struct statvfs* stbuf)
        Return statistics about the filesystem.  See statvfs(2) for a
        description of the structure contents.  Usually, you can ignore the
        path.  Not required, but handy for read/write filesystems since this
        is how programs like df determine the free space.
        """
        self.logger.debug('[FuseFSCore.statfs] Request FileSystem Info. Context: %s', self.GetContext())
        stv = fuse.StatVfs()
        setattr(stv, 'f_bsize', 512)
        setattr(stv, 'f_frsize', 512)
        return stv

    def unlink(self, path):
        """
         unlink(const char* path)
        Remove (delete) the given file, symbolic link, hard link, or special
        node.  Note that if you support hard links, unlink only deletes the
        data when the last hard link is removed.  See unlink(2) for details.
        """
        self.logger.error('[FuseFSCore.unlink] Unavail option for path %s. Context: %s', path, self.GetContext())
        return -errno.EPERM

    def symlink(self, name, target):
        """
         symlink(const char* to, const char* from)
        Create a symbolic link named "from" which, when evaluated, will lead
        to "to".  Not required if you don't support symbolic links.  NOTE:
        Symbolic-link support requires only readlink and symlink.  FUSE itself
        will take care of tracking symbolic links in paths, so your
        path-evaluation code doesn't need to worry about it.
        """
        self.logger.error('[FuseFSCore.symlink] Unavail option symlink from name\
                            %s to target %s. Context:', name, target, self.GetContext())
        return -errno.EPERM
#        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        """
         rename(const char* from, const char* to)
        Rename the file, directory, or other object "from" to the target "to".
        Note that the source and target don't have to be in the same
        directory, so it may be necessary to move the source to an entirely
        new directory.  See rename(2) for full details.
        """
        self.logger.error('[FuseFSCore.rename] Unavail option rename from %s to\
                             %s. Context: %s', old, new, self.GetContext())
        return -errno.EPERM
#        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        """
         link(const char* from, const char* to)
        Create a hard link between "from" and "to".  Hard links aren't
        required for a working filesystem, and many successful filesystems
        don't support them.  If you do implement hard links, be aware that
        they have an effect on how unlink works.  See link(2) for details.
        """
        self.logger.error('[FuseFSCore.link] Unavail option link from %s to\
                             %s. Context: %s', target, name, self.GetContext())
        return -errno.EPERM
#        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        """
         utimens(const char* path, const struct timespec ts[2]
        Update the last access time of the given object from ts[0] and the
        last modification time from ts[1].  Both time specifications are given
        to nanosecond resolution, but your filesystem doesn't have to be that
        precise; see utimensat(2) for full details.  Note that the time
        specifications are allowed to have certain special values; however, I
        don't know if FUSE functions have to support them.  This function
        isn't necessary but is nice to have in a fully functional filesystem.
        """
        self.logger.debug('[FuseFSCore.utimens] %s. Context: %s',
                          os.utime(self._full_path(path), times), self.GetContext())
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        """
         open(const char* path, struct fuse_file_info* fi)
        Open a file.  If you aren't using file handles, this function should
        just check for existence and permissions and return either success or
        an error code.  If you use file handles, you should also allocate any
        necessary structures and set fi->fh.  In addition, fi has some other
        fields that an advanced filesystem might find useful; see the
        structure definition in fuse_common.h for very brief commentary.
        """
        self.logger.debug('[FuseFSCore.open] %s:%s. Context: %s', path, flags, self.GetContext())
        fusest = fuse.FuseFileInfo()
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES
        setattr(fusest, 'direct_io', True)
#        setattr(st,'keep',True)
        return fusest

    def create(self, path, mode, fhandle=None):
        """
        FuseFS create function
        """
        self.logger.error('[FuseFSCore.create] Unavail option create for path %s \
                            mode %s and fhandle %s. Context: %s', path, mode, fhandle, self.GetContext())
        return -errno.EPERM
#        full_path = self._full_path(path)
#        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset):
        """
         read(const char* path, char *buf, size_t size, off_t offset, struct
        fuse_file_info* fi)
        Read sizebytes from the given file into the buffer buf, beginning
        offset bytes into the file.  See read(2) for full details.  Returns
        the number of bytes transferred, or 0 if offset was at or beyond the
        end of the file.  Required for any sensible filesystem.
        """
        self.logger.debug('[FuseFSCore.read] read file %s:%s:%s. Context: %s',
                          path, length, offset, self.GetContext())
        srctree = self.returntree(path, self.root, True)
        self.logger.debug(
            '[FuseFSCore.read] dirtree data %s for path %s', srctree, path)
        if isobject(srctree):
            if hasattr(srctree, '_read'):
                self.logger.debug(
                    '[FuseFSCore.read] srctree %s has attr _read', srctree)
                dirtree = srctree._read(path)
            else:
                dirtree = srctree._getattr(path)
            self.logger.debug('[FuseFSCore.read] get path %s', dirtree)
        else:
            dirtree = srctree
#        dirtree=self.returntree(path,self.root,True)
        self.logger.debug('[FuseFSCore.read] FoundTree: %s', dirtree)
        if callable(dirtree):
            retval = dirtree()[1]
            return retval[offset:length]
        elif len(dirtree) > 1:
            if callable(dirtree[1]):
                return dirtree[1](path)[offset:length]
            else:
                return dirtree[1][offset:length]
        else:
            return None

    def write(self, path, buf, offset):
        """
         write(const char* path, char *buf, size_t size, off_t offset, struct
        fuse_file_info* fi)
        As for read above, except that it can't return 0.
        """
        self.logger.error('[FuseFSCore.write] Unavail option write for path \
                            %s buf %s offset %s. Context: %s', path, buf, offset, self.GetContext())
        return -errno.EPERM

    def truncate(self, path, length, fhandle=None):
        """
         truncate(const char* path, off_t size)
        Truncate or extend the given file so that it is precisely size bytes
        long.  See truncate(2) for details.  This call is required for
        read/write filesystems, because recreating a file will first truncate
        it.
        """
        self.logger.debug('[FuseFSCore.truncate] %s:%s:%s. Context: %s',
                          path, length, fhandle, self.GetContext())
        return 0

    def flush(self, path, fhandle=None):
        """
         flush(const char* path, struct fuse_file_info* fi)
        Called on each close so that the filesystem has a chance to report
        delayed errors.  Important: there may be more than one flush call for
        each open.
        NOTE: There is no guarantee that flush will ever be called
        at all!
        """
        self.logger.debug('[FuseFSCore.flush] %s:%s. Context: %s',
                          path, fhandle, self.GetContext())
#        return os.fsync(fh)

    def release(self, path, fhandle):
        """
         release(const char* path, struct fuse_file_info *fi)
        This is the only FUSE function that doesn't have a directly
        corresponding system call, although close(2) is related.  Release is
        called when FUSE is completely done with a file; at that point, you
        can free up any temporarily allocated data structures.  The IBM
        document claims that there is exactly one release per open, but I
        don't know if that is true.
        """
        self.logger.debug('[FuseFSCore.release] %s:%s. Context: %s',
                          path, fhandle, self.GetContext())
        return os.close(fhandle)

    def fsync(self, path, fdatasync, fhandle):
        """
         fsync(const char* path, int isdatasync, struct fuse_file_info* fi)
        Flush any dirty information about the file to disk.  If isdatasync is
        nonzero, only data, not metadata, needs to be flushed.  When this call
        returns, all file data should be on stable storage.  Many filesystems
        leave this call unimplemented, although technically that's a Bad Thing
        since it risks losing data.  If you store your filesystem inside a
        plain file on another filesystem, you can implement this by calling
        fsync(2) on that file, which will flush too much data (slowing
        performance) but achieve the desired guarantee.
        """
        self.logger.debug('[FuseFSCore.fsync] %s:%s:%s. Context: %s',
                          path, fdatasync, fhandle, self.GetContext())
        return self.flush(path, fhandle)

    # @profile
    def returntree(self, path, tree, withdata=False):
        """
        return filetree as dict for fusefs functions
        """
        #    global lpd
        #    lpd=mpd
        #    logger.debug('[returntree] MPD %s'%mpd)
        pathlist = [pathpart for pathpart in path.split('/') if pathpart != '']
        # перепаковываем непустые элементы пути в массив
        if len(pathlist) == 0:
                # если длина массива = 0, то обрабатываем всё дерево
            data = tree
        else:
            # если длина массива отлична от 0, то ищем ветку в дереве
            data = self.recursepath(pathlist, tree, withdata)

        #    dirtree = {}
        if isinstance(data, dict):
            # logger.debug('[returntree] Dict Data %s'%data)
            #
            # если результат поиска "словарь", значит это ветка файловой
            # системы со списком директорий и файлов.
            dirstat = {}
            map(lambda x: dirstat.update(x), [
                stat_info['def'], stat_info['dir']])
            #
            # процедура обхода дерева файлов универсальна и используется
            # в различных процедурах
            #
            # readdir - возвращает системе список объектов
            # 		в запрошенной ветке файловой системы
            # getattr - возвращает системе структуру tuple
            # 		с характеристиками объекта
            #
            # ВАЖНО! readdir не передаёт никаких характеристик объектов
            # вся информация получается путём дальнейшего опроса данных
            # объектов процедурой getattr
            #
            # для хранения информации используется древовидная структура
            # в виде словаря dict()
            #
            # в поле значения которой, для каждого объекта используется
            # список list()
            #
            # первым элементом которого хранится именованный словарь
            # параметров для файловой системы объекта, во втором элементе
            # хранится содержимое объекта:
            #
            # directory - первый элемент объекта это словарь параметров,
            # второй элемент равен None
            #
            # regular file - первый элемент объекта это словарь параметров,
            # второй элемент - содержимое файла
            #
            # symlink - первый элемент объекта это словарь параметров,
            # второй элемент - путь до реального объекта
            #
            # т.к. информация о запрашиваемой директории не хранится в явном
            # виде в дереве объектов, необходимо при возврате данных описать
            # параметры директории. Для этого, для корня указанного "словаря"
            # необходимо добавить ключ __dirstat__, содержащий описанную выше
            # структуру параметров для директории

            retdict = dict((k, []) for k in data)
            retdict['__dirstat__'] = []
            retdict['__dirstat__'].append(dirstat)
            logger.debug(
                '[FuseFSCore.returntree] Instance Dict > retdict: %s\n',
                retdict)
            return retdict

        elif isinstance(data, list):
            # если результатом поиска объекта в дереве является список list(),
            # значит данный объект не содержит дочерних объектов и является
            # файлом. Для статичных файлов и объектов типа symlink, размер
            # файла может меняться, поэтому при возврате атрибутов файла
            # необходимо скорректировать параметр 'st_size'. Т.к. symlink не
            # отличается от обычного файла, то в дереве объектов в его
            # параметрах необходимо добавить структуру stat_info['link']
            # после чего данная структура автоматом будет дополнена
            # необходимыми параметрами
            itemstat = {}
            itemstat.update(data[0])
            map(lambda x: data[0].update(x), [
                stat_info['def'], stat_info['file'], itemstat])
            logger.debug(
                '[FuseFSCore.returntree] Instance List > itemstat:%s',
                itemstat)
            logger.debug('[FuseFSCore.returntree] data: %s\n', data)
            # print path,data
        return data

        # @profile

    def recursepath(self, path, tree, withdata):
        """
        recursive search a path in existing tree
        """
        # print 'Path %s length %s tree %s'%(path,len(path),tree)
        # !logger.debug('[recursepath] Path %s length %s WithData:
        # %s'%(path,len(path),withdata))
        if path[0] not in tree:
            # print 'Path not found'
            return None
        else:
            # print 'Tree %s'%tree
            if not isobject(tree[path[0]]):
                if len(path) == 1:
                    if isobject(tree[path[0]]):
                        logger.debug(
                            '[FuseFSCore.recursepath] object found %s',
                            tree[path[0]])
                        return tree[path[0]]
                    elif callable(tree[path[0]]):
                        logger.debug(
                            '[FuseFSCore.recursepath] callable dir %s',
                            dir(tree[path[0]]))
        # return { '1234' : { '12345' : [stat_info['def'],None] } }
                        logger.debug('[FuseFSCore.recursepath] Callable \
                        Path found %s at %s:%s', path, tree[path[0]], withdata)
                        dictpath = dict((x, {})
                                        for x in tree[path[0]](withdata))
                        logger.debug(
                            '[FuseFSCore.recursepath] --------- Callable \
                            Path result %s', len(dictpath))
                        return dictpath
                    else:
                        return tree[path[0]]
                else:
                    for part in path:
                        # print '\n[recursepath] Path part %s'%part
                        # print '\n[recursepath] Path %s length
                        # %s:%s'%(path,len(path),withdata)

                        if callable(tree[part]):
                            # print '[recursepath] callable %s at path
                            # %s'%(tree[part],path)
                            data = tree[part](withdata, path[1:])
                            # print '[recursepath] Plain callable data for
                            # path %s tree %s'%(path,data)
                            return data
                        else:
                            # print 'recurse %s tree %s'%(part,tree[part])
                            # pathkey = '/'.join(path)
                            # if pathkey in cache:
                            # data = cache[pathkey]
                            # print '\n%s\n[recursepath] Cached data tree
                            # for path %s is %s'%('='*30,path,data)
                            # else:
                            # cache.expire()
                            data = self.recursepath(
                                path[1:], tree[part], withdata)
                            # cache.set(pathkey, data, expire=15)
                            # print '\n%s\n[recursepath] Plain ordinal data
                            # tree for path %s is %s'%('='*30,path,data)
                            return data
            else:
                return tree[path[0]]


def returnhelp(path=None):
    """
    return help contents for file
    """
    return 'help file contents %s\n' % path
