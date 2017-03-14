# -*- coding: utf-8 -*-
"""
Make a file structures over Classes
"""
import errno
import logging
import json
import astfs.constants
from astfs.logger import logger

# import stat is not needed, just use fixed file type values

stat_info = {'file': {'st_mode': 0x8000 | int('0644', 8)},
             'dir': {'st_mode': 0x4000 | int('0755', 8), 'st_size': 512},
             'link': {'st_mode': 0xa000 | int('0755', 8)},
             'def': {'st_mode': 0,
                     'st_ino': 0,
                     'st_dev': 0,
                     'st_nlink': 1,
                     'st_uid': astfs.constants.UID,
                     'st_gid': astfs.constants.GID,
                     'st_size': 0,
                     'st_atime': astfs.constants.STARTUPTIME,
                     'st_mtime': astfs.constants.STARTUPTIME,
                     'st_ctime': astfs.constants.STARTUPTIME},
             'fields': ['st_mode',
                        'st_ino',
                        'st_dev',
                        'st_nlink',
                        'st_uid',
                        'st_gid',
                        'st_size',
                        'st_atime',
                        'st_mtime',
                        'st_ctime']}

class BasicTree(object):

    def __init__(self, path, inmpd, dictpart):  # *args, **kwargs):
        self.path = path
        self.mpd = inmpd
        self.filestruct = {}
        self.filestruct.update(stat_info['def'])
        self.filestruct.update(stat_info['file'])
        self.dirstruct = {}
        self.dictpart = dictpart
        self.dirstruct.update(self.filestruct)
        self.dirstruct.update(stat_info['dir'])
        self.itementry = {'info': [self.filestruct, self._getfile],
                          'stat': [self.filestruct, self._getfile]}
        self.direntry = {'__dirstat__': [self.dirstruct, '']}
        self.tree = {'help': [self.filestruct, self._getfile], 'info': [
            self.filestruct, self._getfile]}
        self.infotree = {
            'sip': {
                'credentials': ['name', 'username', 'secret',
                                'md5secret', 'fromuser', 'fromdomain',
                                'cid_name', 'remotesecret', 'fullcontact',
                                'useragent', 'regexten', 'transports'],
                'codecs': ['codecs', 't38_maxdatagram', 'rtptimeout',
                           'timer_t1', 'timerb', 'maxcallbitrate',
                           'rtpkeepalive', 'rtpholdtimeout',
                           'qualifyfreq', 'autoframing'],
                'huntgroups': ['vmexten', 'unsolicited_mailbox', 'mwi_from'],
                'contexts': ['context', 'subscribecontext'],
                'full': []},
            'iax2':
                {
                    'full': []},
        }

    def normalize(self, path):
        if path.find(self.path) != 0:
            logger.error(
                '[BasicTree.normalize] Incorrect path for object %s ,path %s, \
                     self.path %s', self, path, self.path)
            return None
        return path.replace(self.path, '').replace('/', '', 1)

    def _getfile(self, path):
        logger.debug('[BasicTree._getfile] started for path %s',
                     self.normalize(path))
        return 'just a file\n'

    def _read(self, path):
        logger.debug('[BasicTree._read] started for path %s',
                     self.normalize(path))
        pth = self.normalize(path).split('/')
        if pth[0] in self.tree:
            return self.tree[pth[0]]
        else:
            return ['', '']

    def _readlink(self, path):
        logger.debug('[BasicTree._readlink] started for path %s',
                     self.normalize(path))
        return '#'

    def _getattr(self, path):
        logger.debug('[BasicTree._getattr] started for path %s',
                     self.normalize(path))
        pth = self.normalize(path).split('/')
        # _getattr возвращает только атрибуты!
        logger.debug(
            '[BasicTree._getattr] path len %s, path %s', len(pth), pth)
        if pth[0] == '':
            ptrt = {}
            ptrt.update(self.direntry)
            logger.debug('[BasicTree._getattr] return full tree %s', ptrt)
            return ptrt
        elif len(pth) > 1:
            if pth[1] in self.tree[pth[0]]:
                fileattr = []
                fileattr.extend(x for x in self.tree[pth[0]][pth[1]])
                logger.debug('[BasicTree._getattr] fileattr %s', fileattr)
                return fileattr
            else:
                return -errno.ENOENT
        elif pth[0] in self.tree:
            return self.tree[pth[0]]
        else:
            return -errno.ENOENT

    def _readdir(self, path):
        # logger.debug('[BasicTree._readdir] started for path %s' % \
        # self.normalize(path))
        # _readdir возвращает только список файлов в директории
        pth = self.normalize(path).split('/')
        logger.debug(
            '[BasicTree._readdir] path len %s, path %s', len(pth), pth)
        if pth[0] == '':
            ptrt = dict((x, {}) for x in self.tree)
            if '__dirstat__' in ptrt:
                del ptrt['__dirstat__']
            logger.debug('[BasicTree._readdir] return full tree %s', ptrt)
            return ptrt
        elif len(pth) > 1:
            if pth[1] in self.tree[pth[0]]:
                return self.tree[pth[0]][pth[1]]
            else:
                return -errno.ENOENT
        elif pth[0] in self.tree:
            ptrt = dict((x, {}) for x in self.tree[pth[0]])
            logger.debug('[BasicTree._readdir] return part tree %s', ptrt)
            return ptrt
        else:
            return -errno.ENOENT

    @staticmethod
    def recode(param):
        if isinstance(param, unicode):
            return param.encode('utf-8', 'ignore')
        else:
            return param


