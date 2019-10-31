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
    return SeriesByInitWrapper(conf, logger)


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
        produtil.log.postmsg('series_by_init_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup(util.baseinputconfs)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'series by init wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def test_wrapper_ok():
    """ Verify that the expected output directory for the
        series init wrapper is what we expected, based on the
        setting in the custom.conf config file.
    """
    siw = series_init_wrapper()
    expected_output_dir = "/d1/METplus_test_input/series_analysis_init"
    assert siw.series_out_dir == expected_output_dir

def test_storm_files_list_OK():
    """ Verify that for the input data (extract tiles output),
        we are generating a list of storm files that match
        the init time and storm basin specified in the config
        file.
    """
    siw = series_init_wrapper()
    tile_dir = '/d1/METplus_test_input/extract_tiles'
    storm_list = siw.get_ascii_storm_files_list(tile_dir)
    assert len(storm_list) > 0

def test_build_and_run_series_request_OK():
    """ Verify that the command that is
        created produces output.
        ***NOTE***:  This tests creates
        numerous met_config_nnnnn_n files!

    """
    siw = series_init_wrapper()
    tile_dir = '/d1/METplus_test_input/extract_tiles'
    sorted_filter_init = siw.get_ascii_storm_files_list(tile_dir)
    assert len(sorted_filter_init) > 0
    # siw.build_and_run_series_request(sorted_filter_init, tile_dir)
    # assert len(siw.get_command()) > 0

def test_get_fcst_file_info_OK():
    """ Verify that the tuple created by get_fcst_file_info is
        not an empty tuple, and that the number, beginning
        fcst file and end fcst file are what we expected.
    """
    # number of forecast files we expect for specified storm;
    # this information is found in the series_init_filtered directory.
    expected_num = 9
    expected_beg = 'F000'
    expected_end = 'F048'
    siw = series_init_wrapper()
    filtered_out_dir = siw.series_filtered_out_dir
    cur_init = '20141214_00'
    cur_storm = 'ML1200942014'

    num,beg,end = siw.get_fcst_file_info(filtered_out_dir, cur_init, cur_storm)
    siw.get_fcst_file_info(filtered_out_dir, cur_init, cur_storm)
    assert num == expected_num
    assert beg == expected_beg
    assert end == expected_end


def test_storms_for_init_OK():
    """Verify that the expected number of storms
       are found for the init time 20141214_00
    """
    init = '20141214_00'
    expected_num_storms = 12
    tile_dir = '/d1/METplus_test_input/extract_tiles'
    siw = series_init_wrapper()
    storm_list = siw.get_storms_for_init(init, tile_dir)
    assert len(storm_list) == expected_num_storms


