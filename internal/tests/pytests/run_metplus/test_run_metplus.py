#!/usr/bin/env python3

import pytest

from pathlib import Path
import os
import shutil
from subprocess import run

# get METplus directory relative to this file
# from this script's directory, go up 4 directories
METPLUS_DIR = str(Path(__file__).parents[4])
RUN_METPLUS = os.path.join(METPLUS_DIR, 'ush', 'run_metplus.py')
EXAMPLE_CONF = os.path.join(METPLUS_DIR, 'parm', 'use_cases',
                            'met_tool_wrapper', 'Example', 'Example.conf')
MINIMUM_CONF = os.path.join(METPLUS_DIR, 'internal', 'tests', 'pytests',
                            'minimum_pytest.conf')
TEST_OUTPUT_DIR = os.path.join(os.environ['METPLUS_TEST_OUTPUT_BASE'],
                               'test_output')
NEW_OUTPUT_BASE = os.path.join(TEST_OUTPUT_DIR, 'run_metplus')
OUTPUT_BASE_OVERRIDE = f"config.OUTPUT_BASE={NEW_OUTPUT_BASE}"

# test that a list of values specified in a command line config override
# will no longer cause an error in the run. The list can be specified without
# quotes if no spaces are present or with quotes if spaces are present
LIST_CONFIG_OVERRIDE_1 = 'config.LEAD_SEQ=3H,6H'
LIST_CONFIG_OVERRIDE_2 = 'config.LEAD_SEQ="3H, 6H"'

@pytest.mark.run_metplus
def test_run_metplus_exists():
    """! Check that run_metplus.py script exists """
    assert os.path.exists(RUN_METPLUS)


@pytest.mark.parametrize(
    'command, expected_return_code', [
        ([RUN_METPLUS], 2),
        ([RUN_METPLUS, EXAMPLE_CONF], 2),
        ([RUN_METPLUS, EXAMPLE_CONF, MINIMUM_CONF, OUTPUT_BASE_OVERRIDE], 0),
        ([RUN_METPLUS, EXAMPLE_CONF, MINIMUM_CONF, LIST_CONFIG_OVERRIDE_1], 0),
        ([RUN_METPLUS, EXAMPLE_CONF, MINIMUM_CONF, LIST_CONFIG_OVERRIDE_2], 0),
    ]
)
@pytest.mark.run_metplus
def test_run_metplus_check_return_code(command, expected_return_code):
    """! Call run_metplus.py without various arguments and check that the
    expected value is returned by the script. A successful run should return
    0 and a failed run should return a non-zero return code, typically 2.
    """
    process = run(command)
    assert process.returncode == expected_return_code

    if os.path.exists(NEW_OUTPUT_BASE):
        shutil.rmtree(NEW_OUTPUT_BASE)


@pytest.mark.run_metplus
def test_output_dir_is_created():
    """! Check that the test output directory was created after running tests
    """
    assert os.path.exists(TEST_OUTPUT_DIR)
