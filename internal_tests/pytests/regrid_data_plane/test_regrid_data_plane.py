#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import pytest
import datetime

import produtil

from metplus.wrappers.regrid_data_plane_wrapper import RegridDataPlaneWrapper
from metplus.util import met_util as util
from metplus.util import time_util

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
#def pytest_addoption(parser):
#    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
#def cmdopt(request):
#    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
#@pytest.fixture
def rdp_wrapper(metplus_config):
    """! Returns a default RegridDataPlane with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return RegridDataPlaneWrapper(config)

# ------------------------ TESTS GO HERE --------------------------

# conf_dict is produtil config items set before creating grid_stat wrapper instance
# out_dict is grid_stat wrapper c_dict values set by initialization
@pytest.mark.parametrize(
    'conf_dict, expected_field_info_list', [

        # 0) 1 item from var list
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06"},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'}]
         ),

        # 1) 1 item with level replaced from wrapper-specific
        ({'OBS_VAR1_NAME': 'P06M_NONE',
          'OBS_VAR1_LEVELS': "\"(*,*)\"",
          'OBS_REGRID_DATA_PLANE_VAR1_INPUT_LEVEL': '"({valid?fmt=%Y%m%d_%H%M%S},*,*)"'},
         [{'index': '1', 'obs_name': 'P06M_NONE', 'obs_level': '"(20180201_000000,*,*)"'},
          ]
        ),

        # 2) 2 items from var list
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          ]
         ),

        # 3) 2 items from var list, 3rd from wrapper-specific
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",
          'OBS_REGRID_DATA_PLANE_VAR3_INPUT_FIELD_NAME': 'NAME_FOR_3'},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          {'index': '3', 'obs_name': 'NAME_FOR_3'},
          ]
         ),

        # 4) 3 items from var list, 1 replaced and 4th from wrapper-specific
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",
          'OBS_VAR3_NAME': 'ACPCP',
          'OBS_VAR3_LEVELS': "A02",
          'OBS_REGRID_DATA_PLANE_VAR3_INPUT_FIELD_NAME': 'NAME_FOR_3',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_FIELD_NAME': 'NAME_FOR_4',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_LEVEL': 'LEVEL_FOR_4'},
        [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          {'index': '3', 'obs_name': 'NAME_FOR_3', 'obs_level': 'A02'},
          {'index': '4', 'obs_name': 'NAME_FOR_4', 'obs_level': 'LEVEL_FOR_4'},
         ]
         ),

        # 5) 1 item from var list add output name
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_REGRID_DATA_PLANE_VAR1_OUTPUT_FIELD_NAME': 'OUT_NAME',},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06', 'obs_output_name': 'OUT_NAME'}]
         ),

        # 6) 3 items from var list, 1 replaced and 4th from wrapper-specific, add output name
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",
          'OBS_VAR3_NAME': 'ACPCP',
          'OBS_VAR3_LEVELS': "A02",
          'OBS_REGRID_DATA_PLANE_VAR3_INPUT_FIELD_NAME': 'NAME_FOR_3',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_FIELD_NAME': 'NAME_FOR_4',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_LEVEL': 'LEVEL_FOR_4',
          'OBS_REGRID_DATA_PLANE_VAR4_OUTPUT_FIELD_NAME': 'OUT_NAME_4'},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          {'index': '3', 'obs_name': 'NAME_FOR_3', 'obs_level': 'A02'},
          {'index': '4', 'obs_name': 'NAME_FOR_4', 'obs_level': 'LEVEL_FOR_4', 'obs_output_name': 'OUT_NAME_4'},
          ]
         ),
    ]
)

def test_get_field_info_list(metplus_config, conf_dict, expected_field_info_list):
    config = metplus_config()

    data_type = 'OBS'

    for key, value in conf_dict.items():
        config.set('config', key, value)

    input_dict = {'valid': datetime.datetime.strptime("201802010000", '%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    var_list = util.parse_var_list(config, time_info, data_type=data_type)

    rdp = RegridDataPlaneWrapper(config)

    field_info_list = rdp.get_field_info_list(var_list, data_type, time_info)
    print(f"FIELD INFO LIST: {field_info_list}")
    print(f"EXPECTED FIELD INFO LIST: {expected_field_info_list}")
    is_good = True
    if len(field_info_list) != len(expected_field_info_list):
        assert(False)

    for actual_field, expected_field in zip(field_info_list, expected_field_info_list):
        for key, value in expected_field.items():
            if actual_field[key] != value:
                print(f"{actual_field[key]} not equal to {value}")
                is_good = False

# field info is the input dictionary with name and level info to parse
# expected_arg is the argument that should be set by the function
# note: did not include OBS because they are handled the same way as FCST
@pytest.mark.parametrize(
    'field_info, expected_arg', [

        # 0) name/level
        ({'fcst_name': 'F_NAME',
          'fcst_level': "\"(1,*,*)\""},
          "-field 'name=\"F_NAME\"; level=\"(1,*,*)\";'"
         ),

        # 1) python embedding script
        ({'fcst_name': 'my_script.py some args',
          'fcst_level': ""},
         "-field 'name=\"my_script.py some args\";'"
         ),

        # 2) name/level
        ({'fcst_name': 'F_NAME',
          'fcst_level': "A06"},
         "-field 'name=\"F_NAME\"; level=\"A06\";'"
         ),

        # 3) name, no level
        ({'fcst_name': 'F_NAME',
          'fcst_level': ""},
         "-field 'name=\"F_NAME\";'"
         ),

        # 4) python embedding script
        ({'fcst_name': 'my_script.py some args',
          'fcst_level': ""},
         "-field 'name=\"my_script.py some args\";'"
         ),
    ]
)

def test_set_field_command_line_arguments(metplus_config, field_info, expected_arg):
    data_type = 'FCST'

    config = metplus_config()

    rdp = RegridDataPlaneWrapper(config)

    rdp.set_field_command_line_arguments(field_info, data_type)
    assert(rdp.args[0] == expected_arg)

@pytest.mark.parametrize(
    'field_info, input_name, expected_name', [

        # 0) use fcst name
        ({'fcst_output_name': 'F_NAME'},
         "INPUT_NAME",
          'F_NAME',
         ),

        # 1) empty fcst name, use input name
        ({'fcst_output_name': ''},
         "INPUT_NAME",
         'INPUT_NAME',
         ),

        # 2) no fcst name, use input name
        ({'fcst_name': 'F_NAME'},
         "INPUT_NAME",
         'INPUT_NAME',
         ),
    ]
)
def test_get_output_name(metplus_config, field_info, input_name, expected_name):
    data_type = 'FCST'

    config = metplus_config()
    rdp = RegridDataPlaneWrapper(config)

    assert(rdp.get_output_name(field_info, data_type, input_name) == expected_name)

def test_run_rdp_once_per_field(metplus_config):
    data_type = 'FCST'

    input_dict = {'valid': datetime.datetime.strptime("201802010000",'%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    var_list = [{'index': '1', 'fcst_name': 'FNAME1', 'fcst_level': 'A06'},
                {'index': '2', 'fcst_name': 'FNAME2', 'fcst_level': 'A03', 'fcst_output_name': 'OUTNAME2'},
                ]

    wrap = rdp_wrapper(metplus_config)
    wrap.c_dict['ONCE_PER_FIELD'] = True
    wrap.c_dict['FCST_OUTPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_accum{level?fmt=%2H}.nc'

    wrap.c_dict['FCST_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH'
    wrap.c_dict['METHOD'] = 'BUDGET'
    wrap.c_dict['WIDTH'] = 2
    wrap.c_dict['VERIFICATION_GRID'] = 'VERIF_GRID'
    wrap.c_dict['FCST_OUTPUT_DIR'] = os.path.join(wrap.config.getdir('OUTPUT_BASE'),
                                                  'RDP_test')

    wrap.run_at_time_once(time_info, var_list, data_type)

    expected_cmds = [f"{wrap.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME1\"; "
                     "level=\"A06\";' -name FNAME1 2018020100_ZENITH \"VERIF_GRID\" "
                     f"{wrap.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_accum06.nc",
                     f"{wrap.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME2\"; "
                     "level=\"A03\";' -name OUTNAME2 2018020100_ZENITH \"VERIF_GRID\" "
                     f"{wrap.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_accum03.nc",
                     ]

    test_passed = True

    if len(wrap.all_commands) != len(expected_cmds):
        print("Number of commands run is not the same as expected")
        print(f"Actual commands: {wrap.all_commands}\n")
        print(f"Expected commands: {expected_cmds}\n")
        assert(False)

    for (cmd, _), expected_cmd in zip(wrap.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert(test_passed)

def test_run_rdp_all_fields(metplus_config):
    data_type = 'FCST'

    input_dict = {'valid': datetime.datetime.strptime("201802010000",'%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    var_list = [{'index': '1', 'fcst_name': 'FNAME1', 'fcst_level': 'A06'},
                {'index': '2', 'fcst_name': 'FNAME2', 'fcst_level': 'A03', 'fcst_output_name': 'OUTNAME2'},
                ]

    wrap = rdp_wrapper(metplus_config)
    wrap.c_dict['ONCE_PER_FIELD'] = False
    wrap.c_dict['FCST_OUTPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ALL.nc'

    wrap.c_dict['FCST_INPUT_TEMPLATE'] = '{valid?fmt=%Y%m%d%H}_ZENITH'
    wrap.c_dict['METHOD'] = 'BUDGET'
    wrap.c_dict['WIDTH'] = 2
    wrap.c_dict['VERIFICATION_GRID'] = 'VERIF_GRID'
    wrap.c_dict['FCST_OUTPUT_DIR'] = os.path.join(wrap.config.getdir('OUTPUT_BASE'),
                                                  'RDP_test')

    wrap.run_at_time_once(time_info, var_list, data_type)

    expected_cmds = [f"{wrap.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME1\"; "
                     "level=\"A06\";' -field 'name=\"FNAME2\"; level=\"A03\";' "
                     "-name FNAME1,OUTNAME2 2018020100_ZENITH \"VERIF_GRID\" "
                     f"{wrap.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_ALL.nc",
                     ]

    test_passed = True

    if len(wrap.all_commands) != len(expected_cmds):
        print("Number of commands run is not the same as expected")
        assert(False)

    for (cmd, _), expected_cmd in zip(wrap.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert(test_passed)

def test_set_command_line_arguments(metplus_config):
    test_passed = True
    wrap = rdp_wrapper(metplus_config)

    expected_args = ['-width 1',]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 0 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.c_dict['GAUSSIAN_DX'] = 2

    expected_args = ['-width 1',
                     '-gaussian_dx 2',
                     ]

    wrap.args.clear()

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 1 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['METHOD'] = 'BUDGET'

    expected_args = ['-method BUDGET',
                     '-width 1',
                     '-gaussian_dx 2',
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 2 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['GAUSSIAN_RADIUS'] = 3

    expected_args = ['-method BUDGET',
                     '-width 1',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 3 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['WIDTH'] = 4

    expected_args = ['-method BUDGET',
                     '-width 4',
                     '-gaussian_dx 2',
                     '-gaussian_radius 3',
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 4 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    assert(test_passed)
