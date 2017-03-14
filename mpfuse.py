"""
A module which can be used for creating any virtual file systems
with callbacks to each virtual directory
"""
import multiprocessing as mp
import time
import sys
import json
import asterisk.manager
from fuse import Fuse
from astfs import constants, fusefscore, fsstruct, realtime
from astfs.ami import getpeersdata
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


class AMI(object):
    """
    Asterisk Management Interface Object
    for importing asterisk internal variables
    to programm
    """
    def __init__(self, host=None, amiuser=None, amipassword=None, sdict=None):
        self.manager = asterisk.manager.Manager()
        self.manager.connect(host)
        self.manager.login(amiuser, amipassword)
        self.manager.sdict = sdict
        self.obj = self
        self.exit = mp.Event()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print self, exc_type, exc_value, traceback
        self.manager.logoff()
        self.manager.close()

    def handle_peerstatus(self,amievent,amimanager):
        logger.info('[handle_peerstatus] %s:%s', amievent.headers, amimanager)
        try:
            mpd['realtimesippeers'] = json.dumps(
                getpeersdata.realtimesippeers(amimanager,'/peers/peer/type=peer'))
            mpd['realtimesipfriends'] = json.dumps(
                getpeersdata.realtimesippeers(amimanager,'/peers/peer/type=friend'))
            mpd['realtimesipusers'] = json.dumps(
                getpeersdata.realtimesippeers(amimanager,'/peers/peer/type=user'))
            mpd['realtimeiax2'] = json.dumps(
                getpeersdata.realtimeiaxpeers(amimanager))
            mpd['usersiax2'] = json.dumps(
                getpeersdata.realtimeiaxusers(amimanager))
            logger.debug('[amiprocess] RealtimePeers Update is OK')
        except Exception as exc:
            logger.error(
                        '[amiprocess] RealtimePeers Update Exception %s', exc)

def amiprocess(globalmpd):
    """
    Asterisk Management Interface Init
    """
#    import json
    amiconn = AMI('localhost', 'agiadmin', 'Agi02022016', globalmpd)
    pami = mp.current_process()
    logger.info('[%s] started. PID:%s', pami.name, pami.pid)
    globalmpd['amiprocess'] = pami.pid
    renewcounter = 0
    setattr(amiconn,'headers',{})
    amiconn.handle_peerstatus(amiconn,amiconn.manager)
    amiconn.manager.register_event('PeerStatus', amiconn.handle_peerstatus)
#    amiconn.manager.register_event('*', handle_event)
    pami.exit = mp.Event()

    while not pami.exit.is_set():
        time.sleep(1)
        try:
            response = amiconn.manager.ping()
            amiconn.manager.sdict['Timestamp'] = response.headers['Timestamp']
#            if renewcounter % 20 == 0:
#                try:
#                    # logger.debug(json.dumps(realtimepeers(ami.manager)))
#                    mpd['realtimesip'] = json.dumps(
#                        getpeersdata.realtimesippeers(amiconn.manager))
#                    mpd['realtimeiax2'] = json.dumps(
#                        getpeersdata.realtimeiaxpeers(amiconn.manager))
#                    logger.debug('[amiprocess] RealtimePeers Update is OK')
#                    # logger.debug('[amiprocess] mpd %s'%mpd)
#                except Exception as exc:
#                    logger.error(
#                        '[amiprocess] RealtimePeers Update Exception %s', exc)
#            renewcounter += 1
            # logger.info('[%s] ami.manager.dict:%s'%(p.name,ami.manager.sdict))
            # print response.headers
        except Exception as exc:
            logger.error('[%s] trying restore connection', vars(exc))
            if exc.message == 'Not connected' :
                try:
                    logger.warning('[%s] trying close connection', pami.name)
                    amiconn.manager.close()
                    logger.warning('[%s] trying restore connection', pami.name)
                    amiconn = AMI('localhost', 'agiadmin', 'Agi02022016', globalmpd)
                    amiconn.manager.register_event('PeerStatus', amiconn.handle_peerstatus)
#                    amiconn.manager.register_event('*', handle_event)
                except Exception as exc:
                    logger.error('[%s] New connection fail %s', pami.name, exc)
#            elif exc == 'Broken pipe': # Broken Pipe
#                    pami.exit.set()
            elif hasattr(exc,'strerror'):
                if exc.strerror == 'Broken pipe': # Broken Pipe
                    pami.exit.set()
            else:
                logger.error('[%s] %s :: %s', pami.name, exc, exc.message)
    amiconn.manager.logoff()
    amiconn.manager.close()


def handle_event(event, amimanager):
    """ Handle Any Asterisk Events """
    logger.info('[handle_event] %s:%s', event.headers, amimanager)
    # logger.info('[handle_event] manager dict: %s'%manager.sdict)

if __name__ == '__main__':
    # pylint: disable=C0103

    # Init shared variables manager
    manager = mp.Manager()
    # Create a dict object
    mpd = manager.dict()
    mpd['realtimesip'] = ''
    mpd['realtimeiax2'] = ''
    mpd['usersiax2'] = ''
    if 'pids' not in mpd:
        mpd['pids'] = {}

    amip = ProcessClass(name='amiprocess', args=(mpd,), target=amiprocess)
    amip.daemon = False
    amip.start()

    root = {
        'peers':
            {
                'sip': realtime.RealTimeSIPTree('/peers/sip', mpd, 'realtimesippeers'),
                'iax2': realtime.RealTimeIAXTree('/peers/iax2', mpd, 'realtimeiax2')
            },
        'config': [fsstruct.stat_info['link'], '/usr/local/etc/asterisk'],
        'users':
            {
                'sipusers'	: realtime.RealTimeSIPTree('/users/sipusers', mpd, 'realtimesipusers'),
                'sipfriends'	: realtime.RealTimeSIPTree('/users/sipfriends', mpd, 'realtimesipfriends'),
                'iax2': realtime.RealTimeIAXTree('/users/iax2', mpd, 'usersiax2')
            },
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
    amip.exit.set()
    logger.info('[fusefsprocess] main stopped. PID:%s', pcore.pid)
    manager.shutdown()
