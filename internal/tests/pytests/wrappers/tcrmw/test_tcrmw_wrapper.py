#!/usr/bin/env python3

import pytest

import os
from datetime import datetime

from metplus.wrappers.tcrmw_wrapper import TCRMWWrapper

deck_template = 'aal14{date?fmt=%Y}_short.dat'
input_template = 'gfs.subset.t00z.pgrb2.0p25.f*'
output_template = 'tc_rmw_aal14{date?fmt=%Y}.nc'

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


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCRMW')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '6H')
    config.set('config', 'TC_RMW_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCRMWConfig_wrapped')
    config.set('config', 'TC_RMW_DECK_TEMPLATE', deck_template)
    config.set('config', 'TC_RMW_INPUT_TEMPLATE', input_template)
    config.set('config', 'TC_RMW_OUTPUT_DIR', '{OUTPUT_BASE}/TCRMW/output')
    config.set('config', 'TC_RMW_OUTPUT_TEMPLATE', output_template)

    config.set('config', 'BOTH_VAR1_NAME', 'PRMSL')
    config.set('config', 'BOTH_VAR1_LEVELS', 'L0')
    config.set('config', 'BOTH_VAR2_NAME', 'TMP')
    config.set('config', 'BOTH_VAR2_LEVELS', 'P1000, P900, P800, P700, P500, P100')


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({}, {}),
        ({'MODEL': 'GFSO'}, {'METPLUS_MODEL': 'model = "GFSO";'}),
        ({'TC_RMW_STORM_ID': 'AL092022'}, {'METPLUS_STORM_ID': 'storm_id = "AL092022";'}),
        ({'TC_RMW_BASIN': 'AL'}, {'METPLUS_BASIN': 'basin = "AL";'}),
        ({'TC_RMW_CYCLONE': '14'}, {'METPLUS_CYCLONE': 'cyclone = "14";'}),
        ({'TC_RMW_INIT_INC': '20220924_00', }, {'METPLUS_INIT_INCLUDE': 'init_inc = "20220924_00";'}),

        ({'TC_RMW_VALID_BEG': '20220924_00', }, {'METPLUS_VALID_BEG': 'valid_beg = "20220924_00";'}),

        ({'TC_RMW_VALID_END': '20220924_00', }, {'METPLUS_VALID_END': 'valid_end = "20220924_00";'}),

        ({'TC_RMW_VALID_INC': '20220924_00, 20220924_18', },
         {'METPLUS_VALID_INCLUDE_LIST': 'valid_inc = ["20220924_00", "20220924_18"];'}),

        ({'TC_RMW_VALID_EXC': '20220924_00, 20220924_18', },
         {'METPLUS_VALID_EXCLUDE_LIST': 'valid_exc = ["20220924_00", "20220924_18"];'}),

        ({'TC_RMW_VALID_HOUR': '12, 18', }, {'METPLUS_VALID_HOUR_LIST': 'valid_hour = ["12", "18"];'}),

        ({'LEAD_SEQ': '0,6,12,18,24', }, {'METPLUS_LEAD_LIST': 'lead = ["00", "06", "12", "18", "24"];'}),

        ({'TC_RMW_REGRID_METHOD': 'NEAREST',},
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'TC_RMW_REGRID_WIDTH': '1',},
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'TC_RMW_REGRID_VLD_THRESH': '0.5',},
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'TC_RMW_REGRID_SHAPE': 'SQUARE',},
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'TC_RMW_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'TC_RMW_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'TC_RMW_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'TC_RMW_REGRID_METHOD': 'NEAREST',
          'TC_RMW_REGRID_WIDTH': '1',
          'TC_RMW_REGRID_VLD_THRESH': '0.5',
          'TC_RMW_REGRID_SHAPE': 'SQUARE',
          'TC_RMW_REGRID_CONVERT': '2*x',
          'TC_RMW_REGRID_CENSOR_THRESH': '>12000,<5000',
          'TC_RMW_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  )
          }),
        ({'TC_RMW_N_RANGE': '10', },
         {'METPLUS_N_RANGE': 'n_range = 10;'}),

        ({'TC_RMW_N_AZIMUTH': '12', },
         {'METPLUS_N_AZIMUTH': 'n_azimuth = 12;'}),

        ({'TC_RMW_DELTA_RANGE_KM': '14', },
         {'METPLUS_DELTA_RANGE_KM': 'delta_range_km = 14.0;'}),

        ({'TC_RMW_RMW_SCALE': '15', },
         {'METPLUS_RMW_SCALE': 'rmw_scale = 15.0;'}),

    ]
)
@pytest.mark.wrapper
def test_tc_rmw_run(metplus_config, get_test_data_dir, config_overrides,
                     env_var_values, compare_command_and_env_vars):
    config = metplus_config

    set_minimum_config_settings(config)

    test_data_dir = get_test_data_dir('tc_pairs')
    deck_dir = os.path.join(test_data_dir, 'bdeck')

    config.set('config', 'TC_RMW_DECK_INPUT_DIR', deck_dir)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCRMWWrapper(config)
    assert wrapper.isOK

    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    file_list_file = f"{file_list_dir}/aal142016_short.dat_data_files.txt"
    if os.path.exists(file_list_file):
        os.remove(file_list_file)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    expected_cmds = [(f"{app_path} "
                      f"-adeck {deck_dir}/aal142016_short.dat "
                      f"-data {file_list_file} "
                      f"-config {config_file} "
                      f"-out {out_dir}/tc_rmw_aal142016.nc "
                      f"{verbosity}"),
                     ]

    all_cmds = wrapper.run_all_times()
    special_values = {
        'METPLUS_DATA_FIELD': data_fmt,
    }
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values,
                                 wrapper, special_values)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'TCRMWConfig_wrapped')

    wrapper = TCRMWWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'TC_RMW_CONFIG_FILE', fake_config_name)
    wrapper = TCRMWWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
