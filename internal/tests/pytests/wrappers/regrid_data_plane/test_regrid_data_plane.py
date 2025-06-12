#!/usr/bin/env python3

import pytest

from metplus.wrappers.regrid_data_plane_wrapper import RegridDataPlaneWrapper

fcst_name = 'APCP'
fcst_level = 'A03'
obs_name = 'APCP_03'
obs_level = '"(*,*)"'

WIDTH_1 = '-width 1'
GAUSSIAN_DX_2 = '-gaussian_dx 2'
METHOD_BUDGET = '-method BUDGET'

fcst_name1 = 'FNAME1'
fcst_level1 = 'A06'
fcst_name2 = 'FNAME2'
fcst_level2 = 'A03'
fcst_out2 = 'OUTNAME2'

test_var_list = [
    {'index': '1', 'fcst_name': fcst_name1, 'fcst_level': fcst_level1},
    {'index': '2', 'fcst_name': fcst_name2, 'fcst_level': fcst_level2, 'fcst_output_name': fcst_out2},
]

def set_test_configs(config):
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d')
    config.set('config', 'VALID_BEG', '20180201')
    config.set('config', 'FCST_REGRID_DATA_PLANE_VAR1_INPUT_FIELD_NAME', fcst_name1)
    config.set('config', 'FCST_REGRID_DATA_PLANE_VAR1_INPUT_LEVEL', fcst_level1)
    config.set('config', 'FCST_REGRID_DATA_PLANE_VAR2_INPUT_FIELD_NAME', fcst_name2)
    config.set('config', 'FCST_REGRID_DATA_PLANE_VAR2_INPUT_LEVEL', fcst_level2)
    config.set('config', 'FCST_REGRID_DATA_PLANE_VAR2_OUTPUT_FIELD_NAME', fcst_out2)
    config.set('config', 'FCST_REGRID_DATA_PLANE_RUN', True)
    config.set('config', 'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}_ZENITH')
    config.set('config', 'REGRID_DATA_PLANE_METHOD', 'BUDGET')
    config.set('config', 'REGRID_DATA_PLANE_WIDTH', '2')
    config.set('config', 'REGRID_DATA_PLANE_VERIF_GRID', 'VERIF_GRID')
    config.set('config', 'FCST_REGRID_DATA_PLANE_OUTPUT_DIR', '{OUTPUT_BASE}/RDP_test')

def rdp_wrapper(metplus_config):
    """! Returns a default RegridDataPlane with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    return RegridDataPlaneWrapper(config)


@pytest.mark.parametrize(
    'once_per_field, missing, run, thresh, errors, allow_missing, to_run', [
        (False, 10, 24, 0.5, 0, True, ['FCST', 'OBS']),
        (False, 10, 24, 0.6, 1, True, ['FCST', 'OBS']),
        (True, 20, 48, 0.5, 0, True, ['FCST', 'OBS']),
        (True, 20, 48, 0.6, 1, True, ['FCST', 'OBS']),
        (False, 10, 24, 0.5, 10, False, ['FCST', 'OBS']),
        (True, 20, 48, 0.5, 20, False, ['FCST', 'OBS']),
        (False, 6, 12, 0.5, 0, True, ['FCST']),
        (False, 6, 12, 0.6, 1, True, ['FCST']),
        (True, 12, 24, 0.5, 0, True, ['FCST']),
        (True, 12, 24, 0.6, 1, True, ['FCST']),
        (False, 6, 12, 0.5, 6, False, ['FCST']),
        (True, 12, 24, 0.5, 12, False, ['FCST']),
        (False, 4, 12, 0.5, 0, True, ['OBS']),
        (False, 4, 12, 0.7, 1, True, ['OBS']),
        (True, 8, 24, 0.5, 0, True, ['OBS']),
        (True, 8, 24, 0.7, 1, True, ['OBS']),
        (False, 4, 12, 0.5, 4, False, ['OBS']),
        (True, 8, 24, 0.5, 8, False, ['OBS']),
    ]
)
@pytest.mark.wrapper
def test_regrid_data_plane_missing_inputs(metplus_config, get_test_data_dir, set_init_configs,
                                          run_all_and_check_missing,
                                          once_per_field, missing, run, thresh, errors,
                                          allow_missing, to_run):
    config = metplus_config

    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'REGRID_DATA_PLANE_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'REGRID_DATA_PLANE_INPUT_THRESH', thresh)
    set_init_configs(config)

    if 'FCST' in to_run:
        config.set('config', 'FCST_REGRID_DATA_PLANE_RUN', True)
        config.set('config', 'FCST_REGRID_DATA_PLANE_INPUT_DIR', get_test_data_dir('fcst'))
        config.set('config', 'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE',
                   '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
        config.set('config', 'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE',
                   '{OUTPUT_BASE}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
        config.set('config', 'FCST_VAR1_NAME', fcst_name)
        config.set('config', 'FCST_VAR1_LEVELS', fcst_level)
        config.set('config', 'FCST_VAR2_NAME', fcst_name)
        config.set('config', 'FCST_VAR2_LEVELS', fcst_level)

    if 'OBS' in to_run:
        config.set('config', 'OBS_REGRID_DATA_PLANE_RUN', True)
        config.set('config', 'OBS_REGRID_DATA_PLANE_INPUT_DIR', get_test_data_dir('obs'))
        config.set('config', 'OBS_REGRID_DATA_PLANE_TEMPLATE',
                   '{valid?fmt=%Y%m%d}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
        config.set('config', 'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE',
                   '{OUTPUT_BASE}/qpe_{valid?fmt=%Y%m%d%H}_A06.nc')
        config.set('config', 'OBS_VAR1_NAME', obs_name)
        config.set('config', 'OBS_VAR1_LEVELS', obs_level)
        config.set('config', 'OBS_VAR2_NAME', obs_name)
        config.set('config', 'OBS_VAR2_LEVELS', obs_level)

    config.set('config', 'REGRID_DATA_PLANE_ONCE_PER_FIELD', once_per_field)

    wrapper = RegridDataPlaneWrapper(config)
    run_all_and_check_missing(wrapper, missing, run, errors)


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


def _override_c_dict(wrapper, var_list, data_type):
    wrapper.c_dict['VAR_LIST_TEMP'] = var_list
    wrapper.c_dict['DATA_SRC'] = data_type
    wrapper.c_dict['OUTPUT_DIR'] = wrapper.c_dict[f'{data_type}_OUTPUT_DIR']
    wrapper.c_dict['OUTPUT_TEMPLATE'] = wrapper.c_dict[f'{data_type}_OUTPUT_TEMPLATE']


@pytest.mark.wrapper
def test_run_rdp_once_per_field(metplus_config):
    config = metplus_config
    config.set('config', 'REGRID_DATA_PLANE_ONCE_PER_FIELD', True)
    config.set('config', 'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}_accum{level?fmt=%2H}.nc')
    set_test_configs(config)

    wrapper = RegridDataPlaneWrapper(config)
    _override_c_dict(wrapper, test_var_list, 'FCST')

    wrapper.run_all_times()

    expected_cmds = [
        f"{wrapper.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME1\"; "
        "level=\"A06\";' -name FNAME1 2018020100_ZENITH \"VERIF_GRID\" "
        f"{wrapper.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_accum06.nc",
        f"{wrapper.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME2\"; "
        "level=\"A03\";' -name OUTNAME2 2018020100_ZENITH \"VERIF_GRID\" "
       f"{wrapper.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_accum03.nc",
    ]

    assert len(wrapper.all_commands) == len(expected_cmds)
    for (cmd, _), expected_cmd in zip(wrapper.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        assert cmd == expected_cmd


@pytest.mark.wrapper
def test_run_rdp_all_fields(metplus_config):
    config = metplus_config
    config.set('config', 'REGRID_DATA_PLANE_ONCE_PER_FIELD', False)
    config.set('config', 'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}_ALL.nc')
    set_test_configs(config)

    wrapper = RegridDataPlaneWrapper(config)
    _override_c_dict(wrapper, test_var_list, 'FCST')

    wrapper.run_all_times()

    expected_cmds = [f"{wrapper.app_path} -v 2 -method BUDGET -width 2 -field 'name=\"FNAME1\"; "
                     "level=\"A06\";' -field 'name=\"FNAME2\"; level=\"A03\";' "
                     "-name FNAME1,OUTNAME2 2018020100_ZENITH \"VERIF_GRID\" "
                     f"{wrapper.config.getdir('OUTPUT_BASE')}/RDP_test/2018020100_ALL.nc",
                     ]

    test_passed = True

    assert len(wrapper.all_commands) == len(expected_cmds)
    for (cmd, _), expected_cmd in zip(wrapper.all_commands, expected_cmds):
        print(f"  ACTUAL:{cmd}")
        print(f"EXPECTED:{expected_cmd}")
        if cmd != expected_cmd:
            test_passed = False

    assert test_passed


@pytest.mark.wrapper
def test_set_command_line_arguments(metplus_config):
    test_passed = True
    wrap = rdp_wrapper(metplus_config)

    expected_args = [WIDTH_1,]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 0 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.c_dict['GAUSSIAN_DX'] = 2

    expected_args = [WIDTH_1,
                     GAUSSIAN_DX_2,
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

    expected_args = [METHOD_BUDGET,
                     WIDTH_1,
                     GAUSSIAN_DX_2,
                     ]

    wrap.set_command_line_arguments()
    if wrap.args != expected_args:
        test_passed = False
        print("Test 2 failed")
        print(f"ARGS: {wrap.args}")
        print(f"EXP: {expected_args}")

    wrap.args.clear()

    wrap.c_dict['GAUSSIAN_RADIUS'] = 3

    expected_args = [METHOD_BUDGET,
                     WIDTH_1,
                     GAUSSIAN_DX_2,
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

    expected_args = [METHOD_BUDGET,
                     '-width 4',
                     GAUSSIAN_DX_2,
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
