#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.wrappers.pb2nc_wrapper import PB2NCWrapper
from metplus.util import met_util as util
from metplus.util import time_util
from metplus.util import do_string_sub

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


def cmdopt(request):
    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
def pb2nc_wrapper(metplus_config):
    """! Returns a default PB2NCWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # PB2NCWrapper with configuration values determined by what is set in
    # the pb2nc_test.conf file.
    extra_configs = []
    extra_configs.append(os.path.join(os.path.dirname(__file__), 'conf1'))
    config = metplus_config(extra_configs)
    return PB2NCWrapper(config)

# ------------------------ TESTS GO HERE --------------------------

# ---------------------
# test_reformat_grid_id
# ---------------------
@pytest.mark.parametrize(
    # key = grid_id, value = expected reformatted grid id
        'key, value', [
            ('G1', 'G001'),
            ('G100', 'G100'),
            ('G10', 'G010'),
            ('123', '123'),
            ('G1234', None),
            ('GG', None),
            ('G', None),
        ]
)
def test_reformat_grid_id(metplus_config, key, value):
    # Verify that reformatting of the grid id is correct
    pb = pb2nc_wrapper(metplus_config)
    reformatted = pb.reformat_grid_id(key)
    assert value == reformatted

# ---------------------
# test_find_and_check_output_file_skip
# test that find_and_check_output_file returns correctly based on
# if file exists and if 'skip if exists' is turned on
# ---------------------
@pytest.mark.parametrize(
    # key = grid_id, value = expected reformatted grid id
        'exists, skip, run', [
            (True, True, False),
            (True, False, True),
            (False, True, True),
            (False, False, True),
        ]
)
def test_find_and_check_output_file_skip(metplus_config, exists, skip, run):
    pb = pb2nc_wrapper(metplus_config)
    exist_file = 'wackyfilenametocreate'
    non_exist_file = 'wackyfilethatdoesntexist'

    # create fake file to test
    create_fullpath = os.path.join(pb.config.getdir('OUTPUT_BASE'), exist_file)
    open(create_fullpath, 'a').close()

    # set time_info, output template/dir, skip if output exists flag
    time_info = { 'valid' : datetime.datetime(2019, 2, 1, 0) }
    pb.c_dict['OUTPUT_DIR'] = pb.config.getdir('OUTPUT_BASE')

    pb.c_dict['SKIP_IF_OUTPUT_EXISTS'] = skip

    if exists:
        pb.c_dict['OUTPUT_TEMPLATE'] = exist_file
    else:
        pb.c_dict['OUTPUT_TEMPLATE'] = non_exist_file

    result = pb.find_and_check_output_file(time_info)

    # cast result to bool because None isn't equal to False
    assert bool(result) == run

# ---------------------
# test_get_command
# test that command is generated correctly
# ---------------------
@pytest.mark.parametrize(
    # list of input files
        'infiles', [
            [],
            ['file1'],
            ['file1', 'file2'],
            ['file1', 'file2', 'file3'],
        ]
)
def test_get_command(metplus_config, infiles):
    pb = pb2nc_wrapper(metplus_config)
    pb.outfile = 'outfilename.txt'
    pb.outdir = pb.config.getdir('OUTPUT_BASE')
    outpath = os.path.join(pb.outdir, pb.outfile)
    pb.infiles = infiles
    config_file = pb.c_dict['CONFIG_FILE']
    cmd = pb.get_command()
    if not infiles:
        expected_cmd = None
    else:
        expected_cmd = pb.app_path + ' -v 2 ' + infiles[0] + ' ' + outpath + ' ' + config_file
        if len(infiles) > 1:
            for infile in infiles[1:]:
                expected_cmd += ' -pbfile ' + infile

    assert cmd == expected_cmd

# ---------------------
# test_find_input_files
# test files can be found with find_input_files with varying offset lists
# ---------------------
@pytest.mark.parametrize(
    # offset = list of offsets to search
    # offset_to_find = expected offset file to find, None if no files should be found
        'offsets, offset_to_find', [
            ([6, 5, 4, 3], 5),
            ([6, 4, 3], 3),
            ([2, 3, 4, 5, 6], 3),
            ([2, 4, 6], None),
        ]
)
def test_find_input_files(metplus_config, offsets, offset_to_find):
    pb = pb2nc_wrapper(metplus_config)
    # for valid 20190201_12, offsets 3 and 5, create files to find
    # in the fake input directory based on input template
    input_dict = { 'valid' : datetime.datetime(2019, 2, 1, 12) }
    fake_input_dir = os.path.join(pb.config.getdir('OUTPUT_BASE'), 'pbin')

    if not os.path.exists(fake_input_dir):
        os.makedirs(fake_input_dir)

    pb.c_dict['OBS_INPUT_DIR'] = fake_input_dir

    for offset in [3, 5]:
        input_dict['offset'] = int(offset * 3600)
        time_info = time_util.ti_calculate(input_dict)

        create_file = do_string_sub(pb.c_dict['OBS_INPUT_TEMPLATE'],
                                    **time_info)
        create_fullpath = os.path.join(fake_input_dir, create_file)
        open(create_fullpath, 'a').close()


    # unset offset in time dictionary so it will be computed
    del input_dict['offset']

    # set offset list
    pb.c_dict['OFFSETS'] = offsets

    # look for input files based on offset list
    result = pb.find_input_files(input_dict)

    # check if correct offset file was found, if None expected, check against None
    if offset_to_find is None:
        assert result is None
    else:
        assert result['offset_hours'] == offset_to_find
