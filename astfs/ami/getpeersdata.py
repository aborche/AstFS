"""
Example to get list of active channels
"""

import logging
import yaml

logger = logging.getLogger('__main__')


# noinspection PyPep8Naming
def handle_PeerEntry(event, amimanager):
    logger.debug(event, "")


def realtimesippeers(amimanager, filter):
    """
    Get a list of SIP peers
    """
    try:
        # logger.debug('[realtimesippeers] realtime load sippeers')
        response = amimanager.command('realtime load sippeers 1 1')
        realtimepeerlist = []
        for i in response.data.split('\n')[2:-2]:
            left = i[:30].lstrip()
            right = i[32:].rstrip()
            if left == 'name':
                realtimepeerlist.append(right)
            #              print "\n\n"
            #            print ("%s : %s"%(left,right or 'none'))
            #        response = manager.command('sip show peers')
            #        pprint.pprint(response.data.split('\n')[1:-3])

            #        logger.debug('[realtimesippeers] sip show peer')
        for rtpeer in realtimepeerlist:
            response = amimanager.command('sip show peer %s load' % rtpeer)

        #        logger.debug('[realtimesippeers] data get /asterisk/channel/sip/peers')
        response = amimanager.command('data get /asterisk/channel/sip/peers %s'%filter)
        #        response = manager.command('data get /asterisk/channel/iax2/peers')
        #        print response.data

        treelinepatched = []
        peer_counter = 0
        codec_counter = 0
        for treeline in response.data.split('\n')[:-2]:
            # check out recursive level
            treeline = treeline.rstrip()
            if len(treeline.lstrip().rstrip()) == 0:
                continue
            if treeline.find(': ') < 0:
                treelineappend = treeline.rstrip()
                if treelineappend.lstrip() == 'peer':
                    treelineappend += str(peer_counter)
                    codec_counter = 0
                    peer_counter += 1
                if treelineappend.lstrip() == 'codec':
                    treelineappend += str(codec_counter)
                    codec_counter += 1
                treelinepatched.append('%s:' % treelineappend)
            else:
                treelinepatched.append(treeline.rstrip())

        # logger.debug('[realtimesippeers] mydict %s'%('\n'.join(treelinepatched)))
        mydict = yaml.load('\n'.join(treelinepatched))
        if mydict['peers'] is None:
            mydict = {'peers': {}}
        peerslist = {}
        # logger.debug('[realtimesippeers] mydict peers')
        # logger.debug('[realtimesippeers] mydict %s'%mydict)
        for i in mydict['peers']:
            peerslist[mydict['peers'][i]['name']] = mydict['peers'][i]

        mydict.clear()
        return peerslist

    except Exception as exc:
        logger.error('[realtimesippeers] Error %s', exc)


# except manager.ManagerSocketException as e:
#        logger.error("Error connecting to the manager: %s" % e.strerror)
#        sys.exit(1)
#    except manager.ManagerAuthException as e:
#        logger.error("Error logging in to the manager: %s" % e.strerror)
#        sys.exit(1)
#        pass
#    except manager.ManagerException as e:
#        logger.error("Error: %s" % e.strerror)
#        pass
#        sys.exit(1)


def realtimeiaxpeers(amimanager):
    """
    Get a list of IAX2 peers
    """
    try:
        response = amimanager.command('data get /asterisk/channel/iax2/peers')

        treelinepatched = []
        peer_counter = 0
        codec_counter = 0
        for treeline in response.data.split('\n')[:-2]:
            # check out recursive level
            treeline = treeline.rstrip()
            if len(treeline.lstrip().rstrip()) == 0:
                continue
            if treeline.find(': ') < 0:
                treelineappend = treeline.rstrip()
                if treelineappend.lstrip() == 'peer':
                    treelineappend += str(peer_counter)
                    codec_counter = 0
                    peer_counter += 1
                if treelineappend.lstrip() == 'codec':
                    treelineappend += str(codec_counter)
                    codec_counter += 1
                treelinepatched.append('%s:' % treelineappend)
            else:
                treelinepatched.append(treeline.rstrip())

        mydict = yaml.load('\n'.join(treelinepatched))
        peerslist = {}

        for i in mydict['peers']:
            peerslist[mydict['peers'][i]['name']] = mydict['peers'][i]

        mydict.clear()
        return peerslist

    except Exception as exc:
        logger.error('[realtimeiax2peers] Error %s', exc)

def realtimeiaxusers(amimanager):
    """
    Get a list of IAX2 peers
    """
    try:
        response = amimanager.command('data get /asterisk/channel/iax2/users')

        treelinepatched = []
        peer_counter = 0
        codec_counter = 0
        for treeline in response.data.split('\n')[:-2]:
            # check out recursive level
            treeline = treeline.rstrip()
            if len(treeline.lstrip().rstrip()) == 0:
                continue
            if treeline.find(': ') < 0:
                treelineappend = treeline.rstrip()
                if treelineappend.lstrip() == 'user':
                    treelineappend += str(peer_counter)
                    codec_counter = 0
                    peer_counter += 1
                if treelineappend.lstrip() == 'codec':
                    treelineappend += str(codec_counter)
                    codec_counter += 1
                treelinepatched.append('%s:' % treelineappend)
            else:
                treelinepatched.append(treeline.rstrip())

        mydict = yaml.load('\n'.join(treelinepatched))
        peerslist = {}

        for i in mydict['users']:
            peerslist[mydict['users'][i]['name']] = mydict['users'][i]

        mydict.clear()
        return peerslist

    except Exception as exc:
        logger.error('[realtimeiax2users] Error %s', exc)
