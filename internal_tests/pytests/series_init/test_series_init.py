import pytest
import os
import sys
import logging
import produtil
import config_metplus
import met_util as util
from series_by_init_wrapper import SeriesByInitWrapper

#  To support the METplus config files
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")

def series_init_wrapper():
    conf = metplus_config()
    logger = logging.getLogger("dummy1")
    conf.set('config', 'LOOP_ORDER', 'processes')
    sbi = SeriesByInitWrapper(conf, logger)
    sbi.run_all_times()

def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='ExtractTilesWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='ExtractTilesWrapper ')
        produtil.log.postmsg('extract_tiles_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'extract tiles wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def test_dummy():
    assert True


