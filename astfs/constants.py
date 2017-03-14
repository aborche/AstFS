# -*- coding: utf-8 -*-
"""
Setting up constants which will be used in all subroutines
"""
import time
import grp
import pwd
from astfs.logger import logger

USERNAME = 'asterisk'
GROUPNAME = 'asterisk'
FMODE = int('100440', 8)  # octal mode for regular file
DMODE = int('040550', 8)  # octal mode for directory

try:
    UID = pwd.getpwnam(USERNAME).pw_uid
except Exception as err:
    logger.error('Cannot get UID %s', err.message)
    UID = 65535	   # nobody

try:
    GID = grp.getgrnam(GROUPNAME).gr_gid
except Exception as err:
    logger.error('Cannot get UID %s', err.message)
    GID = 65535	   # nobody

try:
    STARTUPTIME = int('%d' % time.time())
except Exception as err:
    logger.error('Cannot get Startup time %s', err.message)
    STARTUPTIME = 0
