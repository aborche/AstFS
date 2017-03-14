"""
Logger Module
"""
import logging

logger = logging.getLogger('__main__')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# create console handler and set level to debug
#    """
sth = logging.StreamHandler()
sth.setLevel(logging.DEBUG)
# create formatter
#    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
sth.setFormatter(formatter)
# add ch to logger
logger.addHandler(sth)
#    """ and None
if 1 == 0:
    lfh = logging.FileHandler('mpfuse.log', 'w')
    lfh.setFormatter(formatter)
    logger.addHandler(lfh)
