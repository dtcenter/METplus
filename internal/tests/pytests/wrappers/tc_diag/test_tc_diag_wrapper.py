#!/usr/bin/env python3

import pytest

import os
from datetime import datetime

from metplus.wrappers.tc_diag_wrapper import TCDiagWrapper

deck_template = 'aal14{date?fmt=%Y}_short.dat'
input_template = 'gfs.subset.t00z.pgrb2.0p25.f*'
output_template = '{date?fmt=%Y}'

time_fmt = '%Y%m%d%H'
run_times = ['2016092900']

data_fmt = (
    'field = [{ name="PRMSL"; level="L0"; },'
    '{ name="TMP"; level="P1000"; },'
    '{ name="TMP"; level="P900"; },'
    '{ name="TMP"; level="P800"; },'
    '{ name="TMP"; level="P700"; },'
    '{ name="TMP"; level="P500"; },'
    '{ name="TMP"; level="P100"; }];'
)

input_domain = 'parent'
input_tech_id_list = 'GFSO'


def get_data_dir(config):
    return os.path.join(config.getdir('METPLUS_BASE'),
                        'internal', 'tests', 'data', 'tc_pairs')


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCDiag')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '6H')
    config.set('config', 'TC_DIAG_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCDiagConfig_wrapped')
    config.set('config', 'TC_DIAG_DECK_TEMPLATE', deck_template)
    config.set('config', 'TC_DIAG_INPUT1_TEMPLATE', input_template)
    config.set('config', 'TC_DIAG_INPUT1_DOMAIN', input_domain)
    config.set('config', 'TC_DIAG_INPUT1_TECH_ID_LIST', input_tech_id_list)
    config.set('config', 'TC_DIAG_OUTPUT_DIR',
               '{OUTPUT_BASE}/tc_diag')
    config.set('config', 'TC_DIAG_OUTPUT_TEMPLATE', output_template)

    config.set('config', 'BOTH_VAR1_NAME', 'PRMSL')
    config.set('config', 'BOTH_VAR1_LEVELS', 'L0')
    config.set('config', 'BOTH_VAR2_NAME', 'TMP')
    config.set('config', 'BOTH_VAR2_LEVELS', 'P1000, P900, P800, P700, P500, P100')


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({}, {}),
        ({'MODEL': 'GFSO,  OFCL'}, {'METPLUS_MODEL': 'model = ["GFSO", "OFCL"];'}),
        ({'TC_DIAG_STORM_ID': 'AL092022'}, {'METPLUS_STORM_ID': 'storm_id = "AL092022";'}),
        ({'TC_DIAG_BASIN': 'AL'}, {'METPLUS_BASIN': 'basin = "AL";'}),
        ({'TC_DIAG_CYCLONE': '14'}, {'METPLUS_CYCLONE': 'cyclone = "14";'}),
        ({'TC_DIAG_INIT_INC': '20220924_00', }, {'METPLUS_INIT_INCLUDE': 'init_inc = "20220924_00";'}),

        ({'TC_DIAG_VALID_BEG': '20220924_00', }, {'METPLUS_VALID_BEG': 'valid_beg = "20220924_00";'}),

        ({'TC_DIAG_VALID_END': '20220924_00', }, {'METPLUS_VALID_END': 'valid_end = "20220924_00";'}),

        ({'TC_DIAG_VALID_INC': '20220924_00, 20220924_18', },
         {'METPLUS_VALID_INCLUDE_LIST': 'valid_inc = ["20220924_00", "20220924_18"];'}),

        ({'TC_DIAG_VALID_EXC': '20220924_00, 20220924_18', },
         {'METPLUS_VALID_EXCLUDE_LIST': 'valid_exc = ["20220924_00", "20220924_18"];'}),

        ({'TC_DIAG_VALID_HOUR': '12, 18', }, {'METPLUS_VALID_HOUR_LIST': 'valid_hour = ["12", "18"];'}),

        ({'LEAD_SEQ': '0,6,12,18,24', }, {'METPLUS_LEAD_LIST': 'lead = ["00", "06", "12", "18", "24"];'}),

        ({'TC_DIAG_DIAG_SCRIPT': 'MET_BASE/python/tc_diag/compute_tc_diagnostics.py', },
         {'METPLUS_DIAG_SCRIPT': 'diag_script = ["MET_BASE/python/tc_diag/compute_tc_diagnostics.py"];'}),
        # domain_info 1 dictionary in list
        ({'TC_DIAG_DOMAIN_INFO1_DOMAIN': 'parent', },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{domain = "parent";}];'}),

        ({'TC_DIAG_DOMAIN_INFO1_N_RANGE': '150', },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{n_range = 150;}];'}),

        ({'TC_DIAG_DOMAIN_INFO1_N_AZIMUTH': '8', },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{n_azimuth = 8;}];'}),

        ({'TC_DIAG_DOMAIN_INFO1_DELTA_RANGE_KM': '10.0', },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{delta_range_km = 10.0;}];'}),
        ({'TC_DIAG_DOMAIN_INFO1_DIAG_SCRIPT': 'MET_BASE/python/tc_diag/compute_all_diagnostics.py,MET_BASE/python/tc_diag/compute_custom_diagnostics.py', },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{diag_script = ["MET_BASE/python/tc_diag/compute_all_diagnostics.py", "MET_BASE/python/tc_diag/compute_custom_diagnostics.py"];}];'}),
        ({'TC_DIAG_DOMAIN_INFO1_DOMAIN': 'parent',
          'TC_DIAG_DOMAIN_INFO1_N_RANGE': '150',
          'TC_DIAG_DOMAIN_INFO1_N_AZIMUTH': '8',
          'TC_DIAG_DOMAIN_INFO1_DELTA_RANGE_KM': '10.0',
          'TC_DIAG_DOMAIN_INFO1_DIAG_SCRIPT': 'MET_BASE/python/tc_diag/compute_all_diagnostics.py,MET_BASE/python/tc_diag/compute_custom_diagnostics.py',
         },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{domain = "parent";n_range = 150;n_azimuth = 8;delta_range_km = 10.0;diag_script = ["MET_BASE/python/tc_diag/compute_all_diagnostics.py", "MET_BASE/python/tc_diag/compute_custom_diagnostics.py"];}];'}),
        # domain_info 2 dictionaries in list
        ({'TC_DIAG_DOMAIN_INFO1_DOMAIN': 'parent',
          'TC_DIAG_DOMAIN_INFO1_N_RANGE': '150',
          'TC_DIAG_DOMAIN_INFO1_N_AZIMUTH': '8',
          'TC_DIAG_DOMAIN_INFO1_DELTA_RANGE_KM': '10.0',
          'TC_DIAG_DOMAIN_INFO1_DIAG_SCRIPT': 'MET_BASE/python/tc_diag/compute_all_diagnostics.py,MET_BASE/python/tc_diag/compute_custom_diagnostics.py',
          'TC_DIAG_DOMAIN_INFO2_DOMAIN': 'nest',
          'TC_DIAG_DOMAIN_INFO2_N_RANGE': '100',
          'TC_DIAG_DOMAIN_INFO2_N_AZIMUTH': '7',
          'TC_DIAG_DOMAIN_INFO2_DELTA_RANGE_KM': '12.0',
          'TC_DIAG_DOMAIN_INFO2_DIAG_SCRIPT': 'MET_BASE/python/tc_diag/compute_sst_diagnostics.py',
         },
         {'METPLUS_DOMAIN_INFO_LIST': 'domain_info = [{domain = "parent";n_range = 150;n_azimuth = 8;delta_range_km = 10.0;diag_script = ["MET_BASE/python/tc_diag/compute_all_diagnostics.py", "MET_BASE/python/tc_diag/compute_custom_diagnostics.py"];},{domain = "nest";n_range = 100;n_azimuth = 7;delta_range_km = 12.0;diag_script = ["MET_BASE/python/tc_diag/compute_sst_diagnostics.py"];}];'}),

        ({'TC_DIAG_DATA_DOMAIN': 'parent,nest', },
         {'METPLUS_DATA_DOMAIN': 'domain = ["parent", "nest"];'}),

        ({'TC_DIAG_DATA_LEVEL': 'P500,   P850', },
         {'METPLUS_DATA_LEVEL': 'level = ["P500", "P850"];'}),

        ({'TC_DIAG_REGRID_METHOD': 'NEAREST',},
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'TC_DIAG_REGRID_WIDTH': '1',},
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'TC_DIAG_REGRID_VLD_THRESH': '0.5',},
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'TC_DIAG_REGRID_SHAPE': 'SQUARE',},
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'TC_DIAG_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'TC_DIAG_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'TC_DIAG_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'TC_DIAG_REGRID_METHOD': 'NEAREST',
          'TC_DIAG_REGRID_WIDTH': '1',
          'TC_DIAG_REGRID_VLD_THRESH': '0.5',
          'TC_DIAG_REGRID_SHAPE': 'SQUARE',
          'TC_DIAG_REGRID_CONVERT': '2*x',
          'TC_DIAG_REGRID_CENSOR_THRESH': '>12000,<5000',
          'TC_DIAG_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  )
          }),

        ({'TC_DIAG_COMPUTE_TANGENTIAL_AND_RADIAL_WINDS': 'true', },
         {'METPLUS_COMPUTE_TANGENTIAL_AND_RADIAL_WINDS': 'compute_tangential_and_radial_winds = TRUE;'}),

        ({'TC_DIAG_U_WIND_FIELD_NAME': 'UGRD', },
         {'METPLUS_U_WIND_FIELD_NAME': 'u_wind_field_name = "UGRD";'}),

        ({'TC_DIAG_V_WIND_FIELD_NAME': 'VGRD', },
         {'METPLUS_V_WIND_FIELD_NAME': 'v_wind_field_name = "VGRD";'}),

        ({'TC_DIAG_TANGENTIAL_VELOCITY_FIELD_NAME': 'VT', },
         {'METPLUS_TANGENTIAL_VELOCITY_FIELD_NAME': 'tangential_velocity_field_name = "VT";'}),

        ({'TC_DIAG_TANGENTIAL_VELOCITY_LONG_FIELD_NAME': 'Tangential Velocity', },
         {'METPLUS_TANGENTIAL_VELOCITY_LONG_FIELD_NAME': 'tangential_velocity_long_field_name = "Tangential Velocity";'}),

        ({'TC_DIAG_RADIAL_VELOCITY_FIELD_NAME': 'VR', },
         {'METPLUS_RADIAL_VELOCITY_FIELD_NAME': 'radial_velocity_field_name = "VR";'}),

        ({'TC_DIAG_RADIAL_VELOCITY_LONG_FIELD_NAME': 'Radial Velocity', },
         {'METPLUS_RADIAL_VELOCITY_LONG_FIELD_NAME': 'radial_velocity_long_field_name = "Radial Velocity";'}),

        ({'TC_DIAG_VORTEX_REMOVAL': 'False', }, {'METPLUS_VORTEX_REMOVAL': 'vortex_removal = FALSE;'}),

        ({'TC_DIAG_NC_CYL_GRID_FLAG': 'true', }, {'METPLUS_NC_CYL_GRID_FLAG': 'nc_cyl_grid_flag = TRUE;'}),

        ({'TC_DIAG_NC_DIAG_FLAG': 'true', }, {'METPLUS_NC_DIAG_FLAG': 'nc_diag_flag = TRUE;'}),

        ({'TC_DIAG_CIRA_DIAG_FLAG': 'True', }, {'METPLUS_CIRA_DIAG_FLAG': 'cira_diag_flag = TRUE;'}),

        ({'TC_DIAG_OUTPUT_BASE_FORMAT': 's{storm_id}_{technique}_doper_{init_ymdh}', }, {'METPLUS_OUTPUT_BASE_FORMAT': 'output_base_format = "s{storm_id}_{technique}_doper_{init_ymdh}";'}),
        ({'TC_DIAG_ONE_TIME_PER_FILE_FLAG': 'false', },
         {'METPLUS_ONE_TIME_PER_FILE_FLAG': 'one_time_per_file_flag = FALSE;'}),
    ]
)
@pytest.mark.wrapper
def test_tc_diag_run(metplus_config, config_overrides,
                     env_var_values):
    config = metplus_config

    set_minimum_config_settings(config)

    test_data_dir = get_data_dir(config)
    deck_dir = os.path.join(test_data_dir, 'bdeck')

    config.set('config', 'TC_DIAG_DECK_INPUT_DIR', deck_dir)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCDiagWrapper(config)
    assert wrapper.isOK

    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    file_list_file = f"{file_list_dir}/aal142016_short.dat_data_files.txt"
    if os.path.exists(file_list_file):
        os.remove(file_list_file)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    expected_cmds = [
        (f"{app_path} -deck {deck_dir}/aal142016_short.dat "
         f"-data {input_domain} {input_tech_id_list} {file_list_file} "
         f"-config {config_file} -outdir {out_dir}/2016/ {verbosity}"),
    ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    missing_env = [item for item in env_var_values
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]
    env_var_keys = wrapper.WRAPPER_ENV_VAR_KEYS + missing_env

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

        # check that environment variables were set properly
        for env_var_key in env_var_keys:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert match is not None
            print(f'Checking env var: {env_var_key}')
            actual_value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_DATA_FIELD':
                assert actual_value == data_fmt
            else:
                assert env_var_values.get(env_var_key, '') == actual_value


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'TCDiagConfig_wrapped')

    wrapper = TCDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'TC_DIAG_CONFIG_FILE', fake_config_name)
    wrapper = TCDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
