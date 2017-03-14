"""
A module which can be used for creating any virtual file systems
with callbacks to each virtual directory
"""
import multiprocessing as mp
import time
import sys
import json
#import asterisk.manager
from fuse import Fuse
from astfs import constants, fusefscore, fsstruct
#from astfs.ami import getpeersdata
from astfs.logger import logger

class ProcessClass(mp.Process):
    """ Process Class """
    # self, group=None, target=None, name=None, args=(), kwargs={}

    def __init__(self, group=None, target=None, name=None, *args, **kwargs):
        """ Process init """
        mp.Process.__init__(self, group, target, name, *args, **kwargs)
        logger.info(
            '[ProcessClass.__init__] Process %s initiated', self._name)
        self.exit = mp.Event()

    def shutdown(self):
        """ Process shutdown """
        logger.info(
            '[ProcessClass.shutdown] Shutdown process %s initiated', self._name)
        self.exit.set()


if __name__ == '__main__':
    # pylint: disable=C0103

    # Init shared variables manager
    manager = mp.Manager()
    # Create a dict object
    mpd = manager.dict()
    if 'pids' not in mpd:
        mpd['pids'] = {}

    root = {
        'helpfilefunc': [fsstruct.stat_info['file'], fusefscore.returnhelp],
        'link_to_tmp': [fsstruct.stat_info['link'], '/tmp'],
        'staticfile': [fsstruct.stat_info['file'], 'contents of staticfile'],
        'customchmodfile': [{'st_mode': 0x8000 | int('0600', 8), 'st_uid': 0, 'st_gid': 0}, 'contents of customchmodfile'],
        'nulldir': {},
        'nullfile': [{}, ''],
        'demotreeclass': fsstruct.BasicTree('/demotreeclass', mpd),
        'tree': {'peer': [{'st_mode': 0x8000 | int('0644', 8)}, 'contents of peer'], 'friend': {}, 'user': {}}
    }

    pcore = mp.current_process()
    logger.info('[fusefsprocess] started. PID:%s', pcore.pid)
    mpd['fusefsprocess'] = pcore.pid
    logger.debug('[fusefsprocess] Shared Dict: %s', dict(mpd))
    Fuse.fuse_python_api = (0, 2)
    usage = """Asterisk Realtime Filesystem""" + Fuse.fusage
    server = fusefscore.AstFS(
        version="%prog ",
        usage=usage,
        dash_s_do='setsingle')
    server.parse([
        '/mnt',
        '-f',
        '-oac_attr_timeout=1,remember=1,allow_other,entry_timeout=1'], errex=1)
    server.logger = logger
    server.root = root
    server.mpd = mpd
    server.main()
    logger.info('[fusefsprocess] main stopped. PID:%s', pcore.pid)
    manager.shutdown()
