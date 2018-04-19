#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import pytest
import produtil
import config_metplus
from tc_pairs_wrapper import TcPairsWrapper

#
# -----------Mandatory-----------
#  configuration and fixture to support METplus configuration files beyond
#  the metplus_data, metplus_system, and metplus_runtime conf files.
#


# Add a test configuration
# def pytest_addoption(parser):
#     parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
# def cmdopt(request):
#     return request.config.getoption("-c")


#
# ------------Pytest fixtures that can be used for all tests ---------------
#
@pytest.fixture
def tc_pairs_wrapper():
    """! Returns a default TCPairsWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty PointStatWrapper with some configuration values set
    # to /path/to:
    conf = metplus_config()
    return TcPairsWrapper(conf, None)


@pytest.fixture
def metplus_config():
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='PointStatWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='PointStatWrapper ')
        produtil.log.postmsg('point_stat_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'point_stat_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def test_no_empty_mod_dir():
    """ Verify that we are creating the ATCF files. """
    rtcp = tc_pairs_wrapper()
    tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
    dirs_list = os.listdir(tc_pairs_dir)
    assert len(dirs_list) == 1


def test_no_empty_tcp_dir():
    """ Verify that we are creating tc pair output"""
    rtcp = tc_pairs_wrapper()
    rtcp.run_all_times()
    tc_pairs_dir = rtcp.config.getdir('TC_PAIRS_DIR')
    assert os.listdir(tc_pairs_dir)
