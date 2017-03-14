# -*- coding: utf-8 -*-
"""
Make a file structures over Classes
"""
import errno
import logging
import json
import astfs.constants
from astfs.fsstruct import BasicTree, stat_info
from astfs.logger import logger

# import stat is not needed, just use fixed file type values

class RealTimeSIPTree(BasicTree):

    def __init__(self, path, rtstmpd, dictpart):  # *args, **kwargs):
        # super(BasicTree,self).__init__()
        BasicTree.__init__(self, path, rtstmpd, dictpart)
        self.path = path
        self.mpd = rtstmpd
        self.dictpart = 'realtimesip'
        self.dictpart = dictpart
        self.name = 'RealTimeSIPTree'

#    def normalize(self, path):
#        if path.find(self.path) != 0:
# 		logger.error('[RealTimeSIPTree.normalize] Incorrect path for \
# 		object %s ,path %s, self.path %s', self, path, self.path)
#            return None
#        return path.replace(self.path, '').replace('/', '', 1)

    def _findobj(self, path):
        pth = self.normalize(path).split('/')
        logger.debug('[%s._findobj] InPath %s', self.name, path)
        try:
            fulltree = json.loads(self.mpd[self.dictpart])
        except:
            fulltree = {}
        parttree = fulltree

        if pth[0] == '':
            logger.debug('[%s._findobj] Request Root tree', self.name)
#            print type(parttree),parttree
            ptrt = dict((x.encode('utf-8', 'replace'), {})
                        for x in parttree.keys())
            ptrt.update(self.direntry)
            for customs in '_online', '_offline':
                ptrt.update({customs: self.direntry['__dirstat__']})
            logger.debug('[%s._findobj] Returned Tree %s:%s',
                         self.name, type(ptrt), ptrt)
            return ptrt
        else:
            logger.debug('[%s._findobj] Requested PartTree %s:%s',
                         self.name, type(pth), pth)
            if len(pth) == 1 and pth[0] in parttree:
                # self.peerstruct={'credentials': [], 'full': [], \
                #  'codecs': [], 'huntgroups': [], 'contexts': []}
                logger.debug(
                    '[%s._findobj] Request info for peer %s',
                    self.name, pth[0])
                peerstruct = {}
                peerstruct.update(self.infotree['sip'])
                peerstruct.update(self.direntry)
                return peerstruct
            elif len(pth) >= 2 and pth[0] in parttree \
                    and pth[1] in self.infotree['sip']:
                # self.peerstruct={'credentials': [], 'full': [], \
                # 'codecs': [], 'huntgroups': [], 'contexts': []}
                if pth[1] != 'full':
                    return [self.filestruct, self._infotree(parttree[pth[0]],
                                                            self.infotree['sip'][pth[1]])]
                else:
                    return [self.filestruct, self._infotree(parttree[pth[0]],
                                                            parttree[pth[0]].keys())]
            elif len(pth) >= 1 and pth[0] in ['_online', '_offline']:
                logger.debug(
                    '[%s._findobj] Request info for peer %s',
                    self.name, pth)
                if len(pth) >= 2 and pth[1] in parttree.keys():
                    if (parttree[pth[1]]['fullcontact'] != '' and pth[0] == '_online') or (parttree[pth[1]]['fullcontact'] == '' and pth[0] == '_offline'):
                        peerstruct = {}
                        peerstruct.update(stat_info['def'])
                        peerstruct.update(stat_info['link'])
                        logger.debug('[%s._findobj] peerstruct %s',
                                     self.name, peerstruct)
                        return [peerstruct, '../%s' % pth[1]]
                    else:
                        return -errno.ENOENT
                    # self._infotree(parttree[pt[0]],parttree[pt[0]].keys()) ]
                else:
                    peerstruct = {}
                # peerstruct.update(self.peerstruct)
                # peerstruct.update(self.infotree['sip'])
                    peerstruct.update(self.direntry)
                    for peer in parttree.keys():
                        if pth[0] == '_online':
                            # > 0 and parttree[peer]['lastms'] < 4294967295:
                            # and parttree[peer]['status'] == 'OK':
                            if parttree[peer]['fullcontact'] != '':
                                peerstruct.update({peer: {}})
                        elif pth[0] == '_offline':
                            # or parttree[peer]['fullcontact'] == None:
                            # #parttree[peer]['lastms'] == 0 or
                            # parttree[peer]['lastms'] == 4294967295 :
                            if parttree[peer]['fullcontact'] == '':
                                peerstruct.update({peer: {}})
                    return peerstruct
            else:
                return -errno.ENOENT

#    def _makecred(self, tree, peer):
#        #return self.recode(json.dumps(tree[peer]))
#        logger.debug('[RealTimeSIPTree._makecred] %s', type(tree))
#        arr = []
#        for param in tree[peer]:
#        # logger.debug('[RealTimeSIPTree._makecred] %s=%s'%
# 		(self.recode(param),self.recode(tree[peer][param])))
# 		arr.append('%s=%s'%(self.recode(param),
# 		self.recode(tree[peer][param])))
#        return '\n'.join(arr)
# 	 '%s=%s'%(self.recode(i),self.recode(tree[peer][i])) for i in tree[peer])

    def _infotree(self, tree, paramslist):
        structtree = []
        for param in paramslist:
            paramitem = param
            if paramitem in tree:
                paramvalue = tree[paramitem]
            else:
                paramvalue = None
            structtree.append('%s=%s' % (self.recode(
                paramitem), self.recode(paramvalue)))
        structtree.append('')
        return '\n'.join(structtree)

    def _getattr(self, path):
        obj = self._findobj(path)
        if isinstance(obj, dict):
            retobj = {}
            retobj.update({'__dirstat__': obj['__dirstat__']})
            retobj['__dirstat__'][0].update({'st_nlink': len(obj.keys())})
            logger.debug('[%s._getattr] Dict %s:%s',
                         self.name, type(retobj), retobj)
            return retobj
        elif isinstance(obj, list):
            obj[0].update({'st_size': len(obj[1])})
            obj[1] = ''
            logger.debug('[%s._getattr] List %s:%s', self.name, type(obj), obj)
            return obj
        else:
            return obj

    def _readdir(self, path):
        obj = self._findobj(path)
        if isinstance(obj, dict):
            return dict((x.encode('utf-8', 'replace'), {}) for x in obj.keys())
        else:
            return -errno.ENOENT

    def _read(self, path):
        obj = self._findobj(path)
        if isinstance(obj, list):
            obj[0].update({'st_size': len(obj[1])})
            logger.debug('[%s._read] %s:%s', self.name, type(obj), obj)
            return obj
        else:
            return obj

    def _readlink(self, path):
        obj = self._findobj(path)
        if isinstance(obj, list):
            obj[0].update({'st_size': len(obj[1])})
            logger.debug('[%s._readlink] %s:%s', self.name, type(obj), obj)
            return obj
        else:
            return obj


class RealTimeIAXTree(BasicTree):

    def __init__(self, path, rtiaxmpd, dictpart):  # *args, **kwargs):
        # super(BasicTree,self).__init__()
        BasicTree.__init__(self, path, rtiaxmpd, dictpart)
        self.path = path
        self.mpd = rtiaxmpd
        self.dictpart = dictpart
        self.name = 'RealTimeIAXTree'

#    def normalize(self, path):
#        if path.find(self.path) != 0:
#            logger.error('[RealTimeIAXTree.normalize] Incorrect path for
# 		object %s, path %s, self.path %s', self, path, self.path)
#            return None
#        return path.replace(self.path, '').replace('/', '', 1)

    def _findobj(self, path):
        pth = self.normalize(path).split('/')
        logger.debug('[%s._findobj] InPath %s', self.name, path)
        try:
            fulltree = json.loads(self.mpd[self.dictpart])
        except:
            fulltree = {}
        parttree = fulltree

        if pth[0] == '':
            logger.debug('[%s._findobj] Request Root tree', self.name)
            # print type(parttree),parttree
            ptrt = dict((x.encode('utf-8', 'replace'), {})
                        for x in parttree.keys())
            ptrt.update(self.direntry)
            logger.debug('[%s._findobj] Returned Tree %s:%s',
                         self.name, type(ptrt), ptrt)
            return ptrt
        else:
            logger.debug('[%s._findobj] Requested PartTree %s:%s',
                         self.name, type(pth), pth)

            if len(pth) == 1 and pth[0] in parttree:
                # self.peerstruct={'credentials': [], 'full': [],
                # 'codecs': [], 'huntgroups': [], 'contexts': []}
                logger.debug(
                    '[%s._findobj] Request info for peer %s',
                    self.name, pth[0])
                peerstruct = {}
                # peerstruct.update(self.peerstruct)
                peerstruct.update(self.infotree['iax2'])
                peerstruct.update(self.direntry)
                return peerstruct
                # elif len(pt) >= 2 and pt[0] in parttree and pt[1] in
                # self.peerstruct:
            elif len(pth) >= 2 and pth[0] in parttree\
                    and pth[1] in self.infotree['iax2']:
                # self.peerstruct={'credentials': [], 'full': [],
                # 'codecs': [], 'huntgroups': [], 'contexts': []}
                if pth[1] != 'full':
                    return [self.filestruct, self._infotree(parttree[pth[0]],
                                                            self.infotree['iax2'][pth[1]])]
                else:
                    # return [ self.filestruct, 'full\n' ]
                    return [self.filestruct, self._infotree(parttree[pth[0]],
                                                            parttree[pth[0]].keys())]
            else:
                return -errno.ENOENT

#    def _makecred(self, tree, peer):
#        #return self.recode(json.dumps(tree[peer]))
#        logger.debug('[RealTimeIAXTree._makecred] %s', type(tree))
#        arr = []
#        for param in tree[peer]:
#        # logger.debug('[RealTimeIAXTree._makecred] %s=%s'
# 	 %(self.recode(param),self.recode(tree[peer][param])))
#            arr.append('%s=%s'%(self.recode(param),
# 		self.recode(tree[peer][param])))
#        return '\n'.join(arr)
#        # '%s=%s'%(self.recode(i),self.recode(tree[peer][i]))
# 	 for i in tree[peer])

    def _infotree(self, tree, paramslist):
        structtree = []
        for param in paramslist:
            paramitem = param
            if paramitem in tree:
                paramvalue = tree[paramitem]
            else:
                paramvalue = None
            structtree.append('%s=%s' % (self.recode(
                paramitem), self.recode(paramvalue)))
        structtree.append('')
        return '\n'.join(structtree)

    def _getattr(self, path):
        obj = self._findobj(path)
        if isinstance(obj, dict):
            retobj = {}
            retobj.update({'__dirstat__': obj['__dirstat__']})
            retobj['__dirstat__'][0].update({'st_nlink': len(obj)})
            logger.debug('[%s._getattr] Dict %s:%s',
                         self.name, type(retobj), retobj)
            return retobj
        elif isinstance(obj, list):
            obj[0].update({'st_size': len(obj[1])})
            obj[1] = ''
            logger.debug('[%s._getattr] List %s:%s', self.name, type(obj), obj)
            return obj
        else:
            return obj

    def _readdir(self, path):
        obj = self._findobj(path)
        if isinstance(obj, dict):
            return dict((x.encode('utf-8', 'replace'), {}) for x in obj.keys())
        else:
            return -errno.ENOENT

    def _read(self, path):
        obj = self._findobj(path)
        if isinstance(obj, list):
            obj[0].update({'st_size': len(obj[1])})
            logger.debug('[%s._read] %s:%s', self.name, type(obj), obj)
            return obj
        else:
            return obj

#    def _getattr(self,path):
#        obj=self._findobj(path)
#        logger.debug('[RealTimeIAXTree._getattr] %s:%s'%(type(obj),obj))
#        if isinstance(obj,dict):
#            return obj
#        else:
#            return obj
#
#    def _readdir(self,path):
#        obj=self._findobj(path)
#        if isinstance(obj,dict):
#            return obj
#        else:
#            return -errno.ENOENT
#
#    def _read(self,path):
#        obj=self._findobj(path)
