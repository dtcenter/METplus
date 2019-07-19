#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import config_metplus
from pb2nc_wrapper import PB2NCWrapper
from config_wrapper import ConfigWrapper
import met_util as util


# --------------------TEST CONFIGURATION and FIXTURE SUPPORT -------------
#
# The test configuration and fixture support the additional configuration
# files used in METplus
#              !!!!!!!!!!!!!!!
#              !!!IMPORTANT!!!
#              !!!!!!!!!!!!!!!
# The following two methods should be included in ALL pytest tests for METplus.
#
#
def pytest_addoption(parser):
    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
def cmdopt(request):
    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
@pytest.fixture
def pb2nc_wrapper():
    """! Returns a default PB2NCWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    config = metplus_config()
    return PB2NCWrapper(config, config.logger)


@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='PB2NCWrapper ',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='PB2NCWrapper ')
        produtil.log.postmsg('pb2nc_wrapper  is starting')

        # Read in the configuration object CONFIG
        config = config_metplus.setup()
        logger = util.get_logger(config)
        config = ConfigWrapper(config, logger)
        return config

    except Exception as e:
        produtil.log.jlogger.critical(
            'pb2nc_wrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


# ------------------------ TESTS GO HERE --------------------------


@pytest.mark.parametrize(
   'key, value', [
       ('NC_FILE_TMPL', 'nam.t{init?fmt=%HH}z.prepbufr.tm{lead?fmt=%HH}'),
       ('NC_FILE_TMPL', 'prepbufr.gdas.{valid?fmt=%Y%m%d%HH}')
   ]
)
def test_set_attribute_after_wrapper_creation(key, value):
    # Test that we can change the attribute defined in the config file
    pb = pb2nc_wrapper()
    pb.c_dict['NC_FILE_TMPL'] = value
    p_attr = pb.c_dict[key]
    assert (p_attr == value)


# Get all seven values set in the PB2NC_OBS_BUFR_VAR_LIST in the test config file
# and verify that we get what is expected.
@pytest.mark.parametrize(
    'element', [
        pb2nc_wrapper().c_dict['BUFR_VAR_LIST'][0],
        pb2nc_wrapper().c_dict['BUFR_VAR_LIST'][1]
    ]
)
def test_get_obs_bufr_var_list(element):
    # See if we can retrieve the BUFR_VAR_LIST and check that this is
    # what we expect currently we have the following in the pb2nc_test.conf:
    # PB2NC_OBS_BUFR_VAR_LIST = QOB, TOB
    # verify that we have found each of these in the BUFR_VAR_LIST list.
    var_list_conus_sfc = ['PMO', 'TOB']
    var_list_upper_air = ['QOB', 'TOB']
    # Determine if this is upper air or conus surface from the VERTICAL_LOCATION setting
    print('element ', element)
    pb = pb2nc_wrapper()
#    vert_loc = pb.c_dict['VERTICAL_LOCATION']
    vert_loc = pb.config.getstr('config', 'PB2NC_VERTICAL_LOCATION')

    if vert_loc == 'upper_air':
        assert (element in var_list_upper_air)
    if vert_loc == 'conus_sfc':
        assert (element in var_list_conus_sfc)


# -----------------------------
# test_output_dir_name_creation
# # -----------------------------
def test_output_dir_name_creation_for_nam():
    # Verify that the output directory name is being assembled correctly
    pytest.skip('Function no longer used')
    wrapper = pb2nc_wrapper()
    wrapper.c_dict['PB2NC_OUTPUT_DIR'] = \
        '/d1/minnawin/pb2nc_crow_test/nam/conus_sfc'
    wrapper.c_dict['PREPBUFR_DIR_REGEX'] = '.*nam.(2[0-9]{7})'
    wrapper.c_dict['PREPBUFR_FILE_REGEX'] = \
        '.*nam.t([0-9]{2})z.prepbufr.tm([0-9]{2})'
    wrapper.c_dict['NC_FILE_TMPL'] = 'prepbufr.nam.{init?fmt=%Y%m%d}.t{cycle?fmt=%HH}z.tm{offset?fmt=%HH}.nc'
    date = '20170617'
    cycle = '12'
    offset = '00'
    # full file path for test data is:
    full_filepath = '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170617/nam' \
                    '.t12z.prepbufr.tm00'
    expected_outdir = wrapper.c_dict['OUTPUT_BASE']
    expected_model = wrapper.c_dict['PREPBUFR_MODEL_DIR_NAME']
    expected_loc = wrapper.c_dict['VERTICAL_LOCATION']
    expected_filename = str(
        wrapper.c_dict['PB2NC_OUTPUT_DIR']) + '/' + 'prepbufr.nam.' + date + '.t12z' + '.tm' + offset + '.nc'
    expected_outfile = os.path.join(expected_outdir,
                                    expected_model, expected_loc,
                                    expected_filename)
    pbFileInfo = namedtuple('pbFileInfo', 'full_filepath, date, cycle, offset')
    relevant_pb_file = pbFileInfo(full_filepath, date, cycle, offset)
    out_filename = wrapper.generate_output_nc_filename(relevant_pb_file)
    assert (out_filename == expected_outfile)


def test_output_dir_name_creation_for_gdas():
    pytest.skip('Function no longer used')
    # Verify that the output directory name is being assembled correctly
    wrapper = pb2nc_wrapper()
    date = '2017060918'
    input_filename = "prepbufr.gdas.2017060918"
    cycle = None
    offset = None
    # full file path for test data is:
    full_filepath = '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas' \
                    '.2017060918'
    expected_outdir = wrapper.c_dict['OUTPUT_BASE']
    expected_model = wrapper.c_dict['PREPBUFR_MODEL_DIR_NAME']
    expected_loc = wrapper.c_dict['VERTICAL_LOCATION']
    expected_filename = 'prepbufr.gdas.' + date + '.nc'
    expected_outfile = os.path.join(expected_outdir,
                                    expected_model, expected_loc,
                                    expected_filename)
    pbFileInfo = namedtuple('pbFileInfo', 'full_filepath, date, cycle, offset')
    relevant_pb_file = pbFileInfo(full_filepath, date, cycle, offset)
    out_filename = wrapper.generate_output_nc_filename(relevant_pb_file)
    assert (out_filename == expected_outfile)


def test_output_dir_name_creation_for_gdas_vsdb():
    pytest.skip('Function no longer used')
    # Verify that the output directory name is being assembled correctly for
    # VSDB files of the format:
    # /tmp/gpfs/hps/nco/ops/com/gfs/prod/gdas.20180706/gdas.t00z.prepbufr
    wrapper = pb2nc_wrapper()
    date = '20180706'
    cycle = '00'
    offset = None
    wrapper.c_dict[
        'PB2NC_OUTPUT_DIR'] = \
        '/tmp/gpfs/hps/nco/ops/com/gfs/prod/gdas.20180706'
    wrapper.c_dict['PREPBUFR_DIR_REGEX'] = \
        '.gpfs/hps/nco/ops/com/gfs/prod/gdas.(2[0-9]{7})'
    wrapper.c_dict['PREPBUFR_FILE_REGEX'] = \
        'gdas.t([0-9]{2})z.prepbufr'
    wrapper.c_dict['NC_FILE_TMPL'] = 'gdas.t{cycle?fmt=%HH}z.nc'
    full_filepath = \
        '/gpfs/hps/nco/ops/com/gfs/prod/gdas.20180706/gdas.t00z.prepbufr'
    expected_outdir = '/tmp/gpfs/hps/nco/ops/com/gfs/prod'
    expected_model = 'gdas.' + date
    expected_filename = 'gdas.t00z.nc'
    expected_outfile = os.path.join(expected_outdir,
                                    expected_model,
                                    expected_filename)

    pbFileInfo = namedtuple('pbFileInfo', 'full_filepath, date, cycle, offset')
    relevant_pb_file = pbFileInfo(full_filepath, date, cycle, offset)
    out_filename = wrapper.generate_output_nc_filename(relevant_pb_file)
    # print('expected filename: ', expected_outfile)
    # print('out filename: ', out_filename)
    assert (out_filename == expected_outfile)

# ---------------------
# test_reformat_grid_id
# ---------------------
@pytest.mark.parametrize(
    # key = grid_id, value = expected reformatted grid id
        'key, value', [
            ('G1', 'G001'),
            ('G100', 'G100'),
            ('G10', 'G010')
        ]
)
def test_reformat_grid_id(key, value):
    # Verify that reformatting of the grid id is correct
    pb = pb2nc_wrapper()
    reformatted = pb.reformat_grid_id(key)
    assert value == reformatted

# -------------------
# test_full_filepath
# -------------------
@pytest.mark.parametrize(
    # key = subdir, value = fname
    'key, value', [
        ('nam.20170601', 'nam.t00z.prepbufr.tm03'),
        ('', 'prepbufr.gdas.2018010106')
    ]
)
def test_full_filepath(key, value):
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    subdir = key
    fname = value
    expected = os.path.join(pb.c_dict['OBS_INPUT_DIR'], subdir, fname)
    full_fpath = pb.create_full_filepath(fname, subdir)
    assert full_fpath == expected


# --------------------------
# test_pb_info_with_subdir
# -------------------------
def test_pb_info_with_subdir():
    # Verify that the prepbufr file information is correctly
    # curated into a list of named tuples. Testing on data that
    # is separated into ymd dated subdirs. Perform test on only
    # one subdirectory's worth of data.
    pytest.skip('Function no longer used')
    # Make sure we are dealing with the GDAS data
    pb = pb2nc_wrapper()
    pb.c_dict['PREPBUFR_FILE_REGEX'] =\
        'nam.t([0-9]{2})z.prepbufr.tm([0-9]{2})'
    pb.c_dict['NC_FILE_TMPL'] =\
        'prepbufr.{valid?fmt=%Y%m%d%H}.t{cycle?fmt=%HH}z.nc'
    expected_file_subdir =\
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170615'
    expected_files = ['nam.t00z.prepbufr.tm00', 'nam.t00z.prepbufr.tm03',
                      'nam.t06z.prepbufr.tm00', 'nam.t06z.prepbufr.tm03',
                      'nam.t12z.prepbufr.tm00', 'nam.t12z.prepbufr.tm03',
                      'nam.t18z.prepbufr.tm00',  'nam.t18z.prepbufr.tm03']
    # expected_ymd = '20170615'
    num_expected_files = 8
    expected_full_filepaths = []
    for expected_file in expected_files:
        expected_full_filepaths.append(os.path.join(expected_file_subdir,
                                                   expected_file))

    # Get the ymd of the first subdirectory
    subdir = '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170615'
    ymd_match = re.match(r'.*(2[0-9]{7}).*', subdir)
    ymd = ymd_match.group(1)
    file_regex = 'nam.t([0-9]{2})z.prepbufr.tm([0-9]{2})'
    logger = logging.getLogger("temp_log")
    pb_files = util.get_files(subdir, file_regex, logger)
    time_method = 'valid'
    all_pb_info = []
    for pb_file in pb_files:
        pb_info = pb.retrieve_pb_time_info(pb_file, time_method, ymd)
        all_pb_info.append(pb_info)

    if len(all_pb_info) != num_expected_files:
        # Fail there should be one entry for each file
        assert True is False

    for expected_full_filepath in expected_full_filepaths:
        if expected_full_filepath not in pb_files:
            assert True is False


# ------------------------
# test_pb_info_no_subdir
# -----------------------
def test_pb_info_no_subdir():
    # Verify that the prepbufr file information is correctly
    # curated into a list of named tuples. Testing on data that
    # is separated into ymd dated subdirs. Test against the 20170601
    # data file: prepbufr.gdas.2017060100
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    # Make sure we are dealing with the GDAS data
    pb.c_dict['PREPBUFR_FILE_REGEX'] = 'prepbufr.gdas.(2[0-9]{9})'
    pb.c_dict['NC_FILE_TMPL'] = 'prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc]'
    num_expected_files = 117
    data_dir = '/d1/METplus_Mallory/data/prepbufr/gdas'
    file_regex = 'prepbufr.gdas.2[0-9]{9}'
    logger = logging.getLogger("test_log")
    pb_files = util.get_files(data_dir, file_regex, logger)
    time_method = 'valid'

    test_file = os.path.join(data_dir, 'prepbufr.gdas.2017060100')
    pb_info_list = []
    for pb_file in pb_files:
        pb_info = pb.retrieve_pb_time_info(pb_file, time_method)
        pb_info_list.append(pb_info)

    actual_full_filepaths = []
    if len(pb_info_list) != num_expected_files:
        # Fail, number of files is not what was expected
        assert True is False

    for pb_info in pb_info_list:
        actual_full_filepaths.append(pb_info.full_filepath)

    if test_file not in actual_full_filepaths:
        # Fail, expected file not found
        assert True is False


def test_valid_times_nam():
    # Verify that NAM files that are being used are within the correct valid
    # time window. NAM files are separated into dated subdir (YMD) with
    # cycle and offset times incorporated into their filenames.  The YMD,
    # cycle, and offset information is used to determine the init time or
    # valid time.
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    pb.c_dict['TIME_METHOD'] = 'BY_INIT'
    pb.c_dict['PREPBUFR_DATA_DIR'] = '/d1/METplus_Mallory/data/prepbufr'
    pb.c_dict['PREPBUFR_MODEL_DIR_NAME'] = 'nam'
    pb.c_dict['PREPBUFR_DIR_REGEX'] = '.*nam.(2[0-9]{7})'
    pb.c_dict['PREPBUFR_FILE_REGEX'] = \
        '.*nam.t([0-9]{2})z.prepbufr.tm([0-9]{2})'
    pb.c_dict[
        'NC_FILE_TMPL'] = 'prepbufr.{valid?fmt=%Y%m%d%H}.t{' \
                          'cycle?fmt=%HH}z.nc.tm{offset?fmt=%HH}.nc'
    pb.c_dict['PREPBUFR_DATA_DIR'] = '/d1/METplus_Mallory/data/prepbufr'
    pb.c_dict['START_DATE'] = '2017060100'
    pb.c_dict['END_DATE'] = '2017060112'
    pb.c_dict['INTERVAL_TIME'] = '03'
    relevant_pb_files = pb.get_pb_files_by_time()
    print(relevant_pb_files)
    expected_pb_files = [
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t00z'
        '.prepbufr.tm00',
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t00z'
        '.prepbufr.tm03',
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t06z'
        '.prepbufr.tm00',
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t06z'
        '.prepbufr.tm03',
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t12z'
        '.prepbufr.tm03',
        '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t12z'
        '.prepbufr.tm00']

    # First, check if the number of relevant files equals the number
    # of expected files
    if len(relevant_pb_files) == len(expected_pb_files):
        # Next, check that the files returned are what we expected for
        # this particular set of data
        for relevant_pb_file in relevant_pb_files:
            if relevant_pb_file in expected_pb_files:
                expected_pb_files.remove(relevant_pb_file)
        if len(expected_pb_files) != 0:
            # Fail, there are some files that were returned that were
            # unexpected
            assert True is False
    else:
        # Fail, number of relevant files are not what we were expecting
        assert True is False


def test_valid_times_gdas():
    # Verify that GDAS files that are being used are within the correct valid
    # time window. GDAS files have their valid times (YMDH) incorporated into
    # their filenames.
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    pb.c_dict['TIME_METHOD'] = 'BY_VALID'
    pb.c_dict['PREPBUFR_DATA_DIR'] = '/d1/METplus_Mallory/data/prepbufr'
    pb.c_dict['PREPBUFR_MODEL_DIR_NAME'] = 'gdas'
    pb.c_dict['PREPBUFR_DIR_REGEX'] = ''
    pb.c_dict['PREPBUFR_FILE_REGEX'] = 'prepbufr.gdas.(2[0-9]{9})'
    pb.c_dict[
        'NC_FILE_TMPL'] = 'prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc'
    pb.c_dict['START_DATE'] = '2017060100'
    pb.c_dict['END_DATE'] = '2017060118'
    pb.c_dict['INTERVAL_TIME'] = '06'
    relevant_pb_files = pb.get_pb_files_by_time()
    expected_pb_files = [
        '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas.2017060100',
        '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas.2017060106',
        '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas.2017060112',
        '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas.2017060118'
        ]

    # First, check if the number of relevant files equals the number
    # of expected files
    if len(relevant_pb_files) == len(expected_pb_files):
        # Next, check that the files returned are what we expected for
        # this particular set of data
        for relevant_pb_file in relevant_pb_files:
            if relevant_pb_file in expected_pb_files:
                expected_pb_files.remove(relevant_pb_file)
        if len(expected_pb_files) != 0:
            # Fail, there are some files that were returned that were
            # unexpected
            assert True is False
    else:
        # Fail, number of relevant files are not what we were expecting
        assert True is False
    assert True is True


def test_by_valid_for_nam_single_expected():
    # Verify that NAM files that are being used are within the
    # correct valid
    # time window. NAM files are separated into dated subdir (YMD) with
    # cycle and offset times incorporated into their filenames.  The YMD,
    # cycle, and offset information is used to determine the init time or
    # valid time.
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    pb.c_dict['TIME_METHOD'] = 'BY_VALID'
    pb.c_dict['PREPBUFR_DATA_DIR'] = '/d1/METplus_Mallory/data/prepbufr'
    pb.c_dict['PREPBUFR_MODEL_DIR_NAME'] = 'nam'
    pb.c_dict['PREPBUFR_DIR_REGEX'] = '.*nam.(2[0-9]{7})'
    pb.c_dict['PREPBUFR_FILE_REGEX'] = \
        '.*nam.t([0-9]{2})z.prepbufr.tm([0-9]{2})'
    pb.c_dict[
        'NC_FILE_TMPL'] = 'prepbufr.{valid?fmt=%Y%m%d%H}.t{' \
                          'cycle?fmt=%HH}z.nc.tm{offset?fmt=%HH}.nc'
    pb.c_dict['START_DATE'] = '2017053100'
    pb.c_dict['END_DATE'] = '2017053123'
    pb.c_dict['INTERVAL_TIME'] = 1
    relevant_pb_files = pb.get_pb_files_by_time()
    expected_file =\
        ['/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam.t00z.prepbufr.tm03']
    if len(relevant_pb_files) == len(expected_file):
        for relevant_pb_file in relevant_pb_files:
            if relevant_pb_file in expected_file:
                expected_file.remove(relevant_pb_file)
        if len(expected_file) != 0:
            # Didn't have exact match of actual and expected files
            assert True is False
    else:
        # Fail, didn't return the expected number of results
        assert True is False
    assert True


def test_by_valid_for_nam_multiple_expected():
    # Verify that NAM files that are being used are within the
    # correct valid time window. NAM files are separated into dated
    # subdir (# YMD) with cycle and offset times incorporated into their
    # filenames.  The YMD, cycle, and offset information is used to
    # determine the init time or valid time.
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    pb.c_dict['TIME_METHOD'] = 'BY_VALID'
    pb.c_dict['PREPBUFR_DATA_DIR'] = '/d1/METplus_Mallory/data/prepbufr'
    pb.c_dict['PREPBUFR_MODEL_DIR_NAME'] = 'nam'
    pb.c_dict['PREPBUFR_DIR_REGEX'] = '.*nam.(2[0-9]{7})'
    pb.c_dict['PREPBUFR_FILE_REGEX'] = \
        '.*nam.t([0-9]{2})z.prepbufr.tm([0-9]{2})'
    pb.c_dict[
        'NC_FILE_TMPL'] = 'prepbufr.{valid?fmt=%Y%m%d%H}.t{' \
                          'cycle?fmt=%HH}z.nc.tm{offset?fmt=%HH}.nc'
    pb.c_dict['START_DATE'] = '2017060100'
    pb.c_dict['END_DATE'] = '2017060106'
    pb.c_dict['INTERVAL_TIME'] = '06'
    relevant_pb_files = pb.get_pb_files_by_time()
    expected_file = ['/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam'
                     '.t00z.prepbufr.tm00',
                     '/d1/METplus_Mallory/data/prepbufr/nam/nam.20170601/nam'
                     '.t06z.prepbufr.tm00']
    if len(relevant_pb_files) == len(expected_file):
        for relevant_pb_file in relevant_pb_files:
            if relevant_pb_file in expected_file:
                expected_file.remove(relevant_pb_file)
        if len(expected_file) != 0:
            # Didn't have exact match of actual and expected files
            assert True is False
    else:
        # Fail, didn't return the expected number of results
        assert True is False
    assert True


def test_by_valid_for_gdas_multiple_expected():
    # Test that the correct GDAS prepbufr files are selected when
    # given valid begin and end times. GDAS files have the valid time
    # incorporated in the filename.
    pytest.skip('Function no longer used')
    pb = pb2nc_wrapper()
    pb.c_dict['TIME_METHOD'] = 'BY_VALID'
    pb.c_dict['PREPBUFR_DATA_DIR'] = '/d1/METplus_Mallory/data/prepbufr'
    pb.c_dict['PREPBUFR_MODEL_DIR_NAME'] = 'gdas'
    pb.c_dict['PREPBUFR_DIR_REGEX'] = ''
    pb.c_dict['PREPBUFR_FILE_REGEX'] = \
        '.*prepbufr.gdas.(2[0-9]{9})'
    pb.c_dict[
        'NC_FILE_TMPL'] = 'prepbufr.gdas.{valid?fmt=%Y%m%d%H}.nc'
    pb.c_dict['START_DATE'] = '2017061200'
    pb.c_dict['END_DATE'] = '2017061309'
    pb.c_dict['INTERVAL_TIME'] = 24
    relevant_pb_files = pb.get_pb_files_by_time()
    expected_file = [
        '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas.2017061200',
        '/d1/METplus_Mallory/data/prepbufr/gdas/prepbufr.gdas.2017061300']

    if len(relevant_pb_files) == len(expected_file):
        for relevant_pb_file in relevant_pb_files:
            if relevant_pb_file in expected_file:
                expected_file.remove(relevant_pb_file)
        if len(expected_file) != 0:
            # Didn't have exact match of actual and expected files
            assert True is False
    else:
        # Fail, didn't return the expected number of results
        assert True is False
    assert True

