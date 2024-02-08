#!/usr/bin/env python3

import pytest

import os
import datetime

from metplus.wrappers.regrid_data_plane_wrapper import RegridDataPlaneWrapper
from metplus.util import time_util

fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level = '"(*,*)"'


def rdp_wrapper(metplus_config):
    """! Returns a default RegridDataPlane with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return RegridDataPlaneWrapper(config)


@pytest.mark.parametrize(
    'once_per_field, missing, run, thresh, errors, allow_missing', [
        (False, 10, 24, 0.5, 0, True),
        (False, 10, 24, 0.6, 1, True),
        (True, 10, 24, 0.5, 0, True),
        (True, 10, 24, 0.6, 1, True),
        (False, 10, 24, 0.5, 10, False),
        (True, 10, 24, 0.5, 10, False),
    ]
)
@pytest.mark.wrapper
def test_regrid_data_plane_missing_inputs(metplus_config, get_test_data_dir,
                                         once_per_field, missing, run, thresh, errors,
                                         allow_missing):
    config = metplus_config

    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'REGRID_DATA_PLANE_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'REGRID_DATA_PLANE_INPUT_THRESH', thresh)
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'FCST_REGRID_DATA_PLANE_RUN', True)
    config.set('config', 'OBS_REGRID_DATA_PLANE_RUN', True)
    config.set('config', 'FCST_REGRID_DATA_PLANE_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'OBS_REGRID_DATA_PLANE_INPUT_DIR', get_test_data_dir('obs'))
    config.set('config', 'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
    config.set('config', 'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')

    config.set('config', 'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE',
               '{OUTPUT_BASE}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
    config.set('config', 'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE',
               '{OUTPUT_BASE}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
    # add 2nd set of fields to test ONCE_PER_FIELD
    config.set('config', 'FCST_VAR1_NAME', fcst_name)
    config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR1_NAME', obs_name)
    config.set('config', 'OBS_VAR1_LEVELS', obs_level)
    config.set('config', 'FCST_VAR2_NAME', fcst_name)
    config.set('config', 'FCST_VAR2_LEVELS', fcst_level)
    config.set('config', 'OBS_VAR2_NAME', obs_name)
    config.set('config', 'OBS_VAR2_LEVELS', obs_level)
    config.set('config', 'REGRID_DATA_PLANE_ONCE_PER_FIELD', once_per_field)

    wrapper = RegridDataPlaneWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


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
@pytest.mark.wrapper
def test_set_field_command_line_arguments(metplus_config, field_info, expected_arg):
    data_type = 'FCST'

    config = metplus_config

    rdp = RegridDataPlaneWrapper(config)

    rdp.set_field_command_line_arguments(field_info, data_type)
    assert rdp.args[0] == expected_arg


@pytest.mark.parametrize(
    'var_list, expected_names', [

        # 0) use output names
        ([{'fcst_name': 'FCST_NAME_1',
           'fcst_level': 'FCST_LEVEL_1',
           'fcst_output_name': 'FCST_OUTPUT_NAME_1', },
          {'fcst_name': 'FCST_NAME_2',
           'fcst_level': 'FCST_LEVEL_2',
           'fcst_output_name': 'FCST_OUTPUT_NAME_2', }],
         ['FCST_OUTPUT_NAME_1','FCST_OUTPUT_NAME_2']
         ),
        # 1) use input names because no output name specified
        ([{'fcst_name': 'FCST_NAME_1',
           'fcst_level': 'FCST_LEVEL_1', },
          {'fcst_name': 'FCST_NAME_2',
           'fcst_level': 'FCST_LEVEL_2', }],
         ['FCST_NAME_1', 'FCST_NAME_2']
         ),

        # 2) use input name for one and output name for other
        ([{'fcst_name': 'FCST_NAME_1',
           'fcst_level': 'FCST_LEVEL_1', },
          {'fcst_name': 'FCST_NAME_2',
           'fcst_level': 'FCST_LEVEL_2',
           'fcst_output_name': 'FCST_OUTPUT_NAME_2', }],
         ['FCST_NAME_1', 'FCST_OUTPUT_NAME_2']
         ),
        # 3) use name_level because duplicates exist
        ([{'fcst_name': 'FCST_NAME_1',
           'fcst_level': 'FCST_LEVEL_1',
           'fcst_output_name': 'FCST_OUTPUT_NAME', },
          {'fcst_name': 'FCST_NAME_2',
           'fcst_level': 'FCST_LEVEL_2',
           'fcst_output_name': 'FCST_OUTPUT_NAME', }],
         ['FCST_NAME_1_FCST_LEVEL_1', 'FCST_NAME_2_FCST_LEVEL_2']
         ),
        # 4) use name_level because duplicates exist and uses input name
        ([{'fcst_name': 'FCST_NAME',
           'fcst_level': 'FCST_LEVEL_1', },
          {'fcst_name': 'FCST_NAME',
           'fcst_level': 'FCST_LEVEL_2', }],
         ['FCST_NAME_FCST_LEVEL_1', 'FCST_NAME_FCST_LEVEL_2']
         ),

        # 5) rename NetCDF level
        ([{'fcst_name': 'FCST_NAME',
           'fcst_level': '0,*,*', },
          {'fcst_name': 'FCST_NAME',
           'fcst_level': '1,*,*', }],
         ['FCST_NAME_0_all_all', 'FCST_NAME_1_all_all']
         ),

    ]
)
@pytest.mark.wrapper
def test_get_output_names(metplus_config, var_list, expected_names):
    data_type = 'FCST'

    rdp = RegridDataPlaneWrapper(metplus_config)

    assert rdp.get_output_names(var_list, data_type) == expected_names


@pytest.mark.wrapper
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

    wrap.c_dict['VAR_LIST'] = var_list
    wrap.c_dict['DATA_SRC'] = data_type
    wrap.run_at_time_once(time_info)

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
        assert False

    for (cmd, _), expected_cmd in zip(wrap.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert test_passed


@pytest.mark.wrapper
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
    wrap.c_dict['VAR_LIST'] = var_list
    wrap.c_dict['DATA_SRC'] = data_type
    wrap.run_at_time_once(time_info)

    expected_cmds = [f"{wrap.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME1\"; "
                     "level=\"A06\";' -field 'name=\"FNAME2\"; level=\"A03\";' "
                     "-name FNAME1,OUTNAME2 2018020100_ZENITH \"VERIF_GRID\" "
                     f"{wrap.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_ALL.nc",
                     ]

    test_passed = True

    if len(wrap.all_commands) != len(expected_cmds):
        print("Number of commands run is not the same as expected")
        assert False

    for (cmd, _), expected_cmd in zip(wrap.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert test_passed


@pytest.mark.wrapper
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

    assert test_passed
