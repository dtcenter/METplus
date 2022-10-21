#!/usr/bin/env python3

import pytest

from pathlib import Path
import os
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


@pytest.mark.run_metplus
def test_run_metplus_exists():
    """! Check that run_metplus.py script exists """
    assert os.path.exists(RUN_METPLUS)


@pytest.mark.parametrize(
    'command, expected_return_code', [
        ([RUN_METPLUS], 2),  # 0 - no arguments, failure
        ([RUN_METPLUS, EXAMPLE_CONF], 2),  # 1 - minimum conf unset, failure
        ([RUN_METPLUS, EXAMPLE_CONF, MINIMUM_CONF], 0),  # 2 - success
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


@pytest.mark.run_metplus
def test_output_dir_is_created():
    """! Check that the test output directory was created after running tests
    """
    assert os.path.exists(TEST_OUTPUT_DIR)
