#!/usr/bin/env python3

import pytest

import os
import re

from datetime import datetime
from dateutil.relativedelta import relativedelta

from metplus.wrappers.grid_diag_wrapper import GridDiagWrapper

time_fmt = '%Y%m%d%H'
run_times = ['2016092900', '2016092906']
data_dir = '/some/path/data'

data_name_1 = 'APCP'
data_level = 'L0'
data_options_1 = 'n_bins = 55; range  = [0, 55];'
data_name_2 = 'PWAT'
data_options_2 = 'n_bins = 35; range  = [35, 70];'
data_fmt = ('data = {field = [ '
            f'{{ name="{data_name_1}"; level="{data_level}"; {data_options_1} }},'
            f'{{ name="{data_name_2}"; level="{data_level}"; {data_options_2} }}'
            ' ];}')


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'GridDiag')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '6H')
    config.set('config', 'LEAD_SEQ', '141, 144, 147')
    config.set('config', 'GRID_DIAG_RUNTIME_FREQ',
               'RUN_ONCE_PER_INIT_OR_VALID')
    config.set('config', 'GRID_DIAG_CONFIG_FILE',
               '{PARM_BASE}/met_config/GridDiagConfig_wrapped')
    config.set('config', 'GRID_DIAG_INPUT_DIR', data_dir)
    config.set('config', 'GRID_DIAG_INPUT_TEMPLATE',
               ('gfs.subset.t00z.pgrb2.0p25.f{lead?fmt=%H}, '
                'gfs.subset.t00z.pgrb2.0p25.f{lead?fmt=%H}'))
    config.set('config', 'GRID_DIAG_OUTPUT_DIR',
               '{OUTPUT_BASE}/grid_diag/output')
    config.set('config', 'GRID_DIAG_OUTPUT_TEMPLATE',
               'grid_diag.{valid?fmt=%Y%m%d%H}.nc')
    config.set('config', 'BOTH_VAR1_NAME', data_name_1)
    config.set('config', 'BOTH_VAR1_LEVELS', data_level)
    config.set('config', 'BOTH_VAR1_OPTIONS', data_options_1)
    config.set('config', 'BOTH_VAR2_NAME', data_name_2)
    config.set('config', 'BOTH_VAR2_LEVELS', data_level)
    config.set('config', 'BOTH_VAR2_OPTIONS', data_options_2)


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing, runtime_freq', [
        (0, 1, 0.5, 0, True, 'RUN_ONCE'),
        (0, 1, 0.5, 0, False, 'RUN_ONCE'),
        (0, 2, 0.5, 0, True, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (0, 2, 0.5, 0, False, 'RUN_ONCE_PER_INIT_OR_VALID'),
        (2, 7, 1.0, 1, True, 'RUN_ONCE_PER_LEAD'),
        (2, 7, 1.0, 2, False, 'RUN_ONCE_PER_LEAD'),
        (8, 14, 1.0, 1, True, 'RUN_ONCE_FOR_EACH'),
        (8, 14, 1.0, 8, False, 'RUN_ONCE_FOR_EACH'),
    ]
)
@pytest.mark.wrapper
def test_grid_diag_missing_inputs(metplus_config, get_test_data_dir,
                                  missing, run, thresh, errors, allow_missing,
                                  runtime_freq):
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', 'INPUT_MUST_EXIST', True)
    config.set('config', 'GRID_DIAG_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'GRID_DIAG_INPUT_THRESH', thresh)
    config.set('config', 'GRID_DIAG_RUNTIME_FREQ', runtime_freq)
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12,15')
    config.set('config', 'GRID_DIAG_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'GRID_DIAG_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')

    wrapper = GridDiagWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors


@pytest.mark.parametrize(
    'runtime_freq,init_or_valid,expected_subset', [
        # run once
        ('RUN_ONCE', 'INIT',
         [['init_20141031213015_valid_20141031213015_lead_000.nc',
          'init_20141031213015_valid_20141101213015_lead_024.nc',
          'init_20141101093015_valid_20141101093015_lead_000.nc',
          'init_20141101093015_valid_20141102093015_lead_024.nc',
          ]]),
        # once per init
        ('RUN_ONCE_PER_INIT_OR_VALID', 'INIT',
         [['init_20141031213015_valid_20141031213015_lead_000.nc',
           'init_20141031213015_valid_20141101213015_lead_024.nc', ],
          ['init_20141101093015_valid_20141101093015_lead_000.nc',
           'init_20141101093015_valid_20141102093015_lead_024.nc',
           ]]),

        # once per valid
        ('RUN_ONCE_PER_INIT_OR_VALID', 'VALID',
         [['init_20141031213015_valid_20141031213015_lead_000.nc',
           'init_20141030213015_valid_20141031213015_lead_024.nc'],
          ['init_20141101093015_valid_20141101093015_lead_000.nc',
           'init_20141031093015_valid_20141101093015_lead_024.nc'],
          ]),
        # once per lead
        ('RUN_ONCE_PER_LEAD', 'INIT',
         [['init_20141031213015_valid_20141031213015_lead_000.nc',
           'init_20141101093015_valid_20141101093015_lead_000.nc'],
          ['init_20141031213015_valid_20141101213015_lead_024.nc',
           'init_20141101093015_valid_20141102093015_lead_024.nc',
           ]]),
        # once for each
        ('RUN_ONCE_FOR_EACH', 'INIT',
         [['init_20141031213015_valid_20141031213015_lead_000.nc'],
          ['init_20141031213015_valid_20141101213015_lead_024.nc'],
          ['init_20141101093015_valid_20141101093015_lead_000.nc'],
          ['init_20141101093015_valid_20141102093015_lead_024.nc'],
         ]),
    ]
)
@pytest.mark.wrapper
def test_grid_diag_runtime_freq(metplus_config, runtime_freq, init_or_valid, expected_subset):
    """! Test to ensure that get_all_files only gets the files that are
    relevant to the runtime settings and not every file in the directory
    """
    config = metplus_config
    config.set('config', 'LOOP_BY', init_or_valid)
    config.set('config', 'GRID_DIAG_RUNTIME_FREQ', runtime_freq)
    config.set('config', f'{init_or_valid}_TIME_FMT', '%Y%m%d%H%M%S')
    config.set('config', f'{init_or_valid}_INCREMENT', '12H')
    config.set('config', f'{init_or_valid}_BEG', '20141031213015')
    config.set('config', f'{init_or_valid}_END', '20141101093015')
    config.set('config', 'LEAD_SEQ', '0H, 24H')
    config.set('config', 'FCST_VAR1_NAME', 'FCST')
    config.set('config', 'FCST_VAR1_LEVELS', 'L0')

    input_dir = os.path.join(config.getdir('METPLUS_BASE'),
                             'internal', 'tests',
                             'data',
                             'user_script')
    config.set('config', 'GRID_DIAG_INPUT_DIR', input_dir)
    config.set('config', 'GRID_DIAG_INPUT_TEMPLATE',
               ('init_{init?fmt=%Y%m%d%H%M%S}_valid_{valid?fmt=%Y%m%d%H%M%S}_'
                'lead_{lead?fmt=%3H}.nc')
               )
    config.set('config', 'GRID_DIAG_OUTPUT_DIR', config.getdir('OUTPUT_BASE'))

    wrapper = GridDiagWrapper(config)
    wrapper.run_all_times()
    assert len(wrapper.all_commands) == len(expected_subset)
    file_list_files = []
    print(wrapper.all_commands)
    pattern = r'-data\s+([^\s]+)'
    for cmd, _ in wrapper.all_commands:
        match = re.search(pattern, cmd)
        if match:
            file_list_files.append(match.group(1))

    assert len(file_list_files) == len(expected_subset)
    for actual_file, expected_files in zip(file_list_files, expected_subset):
        expected_files_full = [os.path.join(input_dir, item) for item in expected_files]
        if len(expected_files) == 1:
            assert actual_file == expected_files_full[0]
        else:
            with open(actual_file, 'r') as file_handle:
                file_list = file_handle.read().splitlines()[1:]
            print(f'ACTUAL: {file_list}')
            assert sorted(file_list) == sorted(expected_files_full)


@pytest.mark.parametrize(
    'time_info, expected_filename', [
        # all wildcard
        ({'init': '*', 'valid': '*', 'lead': '*'},
         'grid_diag_files_input0_init_ALL_valid_ALL_lead_ALL.txt'),
        # valid/lead wildcard
        ({'init': datetime(2014, 10, 31, 9, 30, 15), 'valid': '*', 'lead': '*'},
         'grid_diag_files_input0_init_20141031093015_valid_ALL_lead_ALL.txt'),
        # init/lead wildcard
        ({'init': '*', 'valid': datetime(2014, 10, 31, 9, 30, 15), 'lead': '*'},
         'grid_diag_files_input0_init_ALL_valid_20141031093015_lead_ALL.txt'),
        # init/valid wildcard integer lead
        ({'init': '*', 'valid': '*', 'lead': 86400},
         'grid_diag_files_input0_init_ALL_valid_ALL_lead_86400.txt'),
        # init/valid wildcard relativedelta lead
        ({'init': '*', 'valid': '*', 'lead': relativedelta(hours=24)},
         'grid_diag_files_input0_init_ALL_valid_ALL_lead_86400.txt'),
        # init wildcard integer lead
        ({'init': '*',
          'valid': datetime(2014, 10, 31, 9, 30, 15),
          'lead': 86400},
         'grid_diag_files_input0_init_ALL_valid_20141031093015_lead_86400.txt'),
        # init wildcard relativedelta lead
        ({'init': '*',
          'valid': datetime(2014, 10, 31, 9, 30, 15),
          'lead': relativedelta(hours=24)},
         'grid_diag_files_input0_init_ALL_valid_20141031093015_lead_86400.txt'),
        # valid wildcard integer lead
        ({'init': datetime(2014, 10, 31, 9, 30, 15),
          'valid': '*',
          'lead': 86400},
         'grid_diag_files_input0_init_20141031093015_valid_ALL_lead_86400.txt'),
        # valid wildcard relativedelta lead
        ({'init': datetime(2014, 10, 31, 9, 30, 15),
          'valid': '*',
          'lead': relativedelta(hours=24)},
         'grid_diag_files_input0_init_20141031093015_valid_ALL_lead_86400.txt'),
        # no wildcard integer lead
        ({'init': datetime(2014, 10, 31, 9, 30, 15),
          'valid': datetime(2014, 11, 1, 9, 30, 15),
          'lead': 86400},
         'grid_diag_files_input0_init_20141031093015_valid_20141101093015_lead_86400.txt'),
        # no wildcard relativedelta lead
        ({'init': datetime(2014, 10, 31, 9, 30, 15),
          'valid': datetime(2014, 11, 1, 9, 30, 15),
          'lead': relativedelta(hours=24)},
         'grid_diag_files_input0_init_20141031093015_valid_20141101093015_lead_86400.txt'),
    ]
)
@pytest.mark.wrapper
def test_get_list_file_name(metplus_config, time_info, expected_filename):
    wrapper = GridDiagWrapper(metplus_config)
    assert(wrapper.get_list_file_name(time_info, 'input0') == expected_filename)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'GridDiagConfig_wrapped')

    wrapper = GridDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'GRID_DIAG_CONFIG_FILE', fake_config_name)
    wrapper = GridDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'GRID_DIAG_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'GRID_DIAG_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_CENSOR_THRESH': 'censor_thresh = [>12000, <5000];'}),

        ({'GRID_DIAG_CENSOR_VAL': '12000, 5000', },
         {'METPLUS_CENSOR_VAL': 'censor_val = [12000, 5000];'}),

        ({'GRID_DIAG_MASK_GRID': 'FULL', },
         {'METPLUS_MASK_DICT': 'mask = {grid = "FULL";}'}),

        ({'GRID_DIAG_MASK_POLY': 'MET_BASE/poly/EAST.poly', },
         {'METPLUS_MASK_DICT': 'mask = {poly = "MET_BASE/poly/EAST.poly";}'}),

        ({'GRID_DIAG_MASK_GRID': 'FULL',
          'GRID_DIAG_MASK_POLY': 'MET_BASE/poly/EAST.poly',},
         {'METPLUS_MASK_DICT': ('mask = {grid = "FULL";'
                                'poly = "MET_BASE/poly/EAST.poly";}')}),

        ({'GRID_DIAG_REGRID_TO_GRID': 'FCST',},
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        ({'GRID_DIAG_REGRID_METHOD': 'NEAREST',},
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'GRID_DIAG_REGRID_WIDTH': '1',},
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'GRID_DIAG_REGRID_VLD_THRESH': '0.5',},
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'GRID_DIAG_REGRID_SHAPE': 'SQUARE',},
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'GRID_DIAG_REGRID_CONVERT': '2*x', },
         {'METPLUS_REGRID_DICT': 'regrid = {convert(x) = 2*x;}'}),

        ({'GRID_DIAG_REGRID_CENSOR_THRESH': '>12000,<5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_thresh = [>12000, <5000];}'}),

        ({'GRID_DIAG_REGRID_CENSOR_VAL': '12000,5000', },
         {'METPLUS_REGRID_DICT': 'regrid = {censor_val = [12000, 5000];}'}),

        ({'GRID_DIAG_REGRID_TO_GRID': 'FCST',
          'GRID_DIAG_REGRID_METHOD': 'NEAREST',
          'GRID_DIAG_REGRID_WIDTH': '1',
          'GRID_DIAG_REGRID_VLD_THRESH': '0.5',
          'GRID_DIAG_REGRID_SHAPE': 'SQUARE',
          'GRID_DIAG_REGRID_CONVERT': '2*x',
          'GRID_DIAG_REGRID_CENSOR_THRESH': '>12000,<5000',
          'GRID_DIAG_REGRID_CENSOR_VAL': '12000,5000',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;'
                                  'convert(x) = 2*x;'
                                  'censor_thresh = [>12000, <5000];'
                                  'censor_val = [12000, 5000];}'
                                  )}),

    ]
)
@pytest.mark.wrapper
def test_grid_diag(metplus_config, config_overrides, env_var_values,
                   compare_command_and_env_vars):
    config = metplus_config
    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = GridDiagWrapper(config)
    assert wrapper.isOK

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    file_list_dir = wrapper.config.getdir('FILE_LISTS_DIR')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    expected_cmds = [
        (f"{app_path} -data {file_list_dir}/grid_diag_files_input0_init_20160929000000_valid_ALL_lead_ALL.txt"
         f" -data {file_list_dir}/grid_diag_files_input1_init_20160929000000_valid_ALL_lead_ALL.txt"
         f" -config {config_file} -out {out_dir}/grid_diag.all.nc {verbosity}"),
        (f"{app_path} -data {file_list_dir}/grid_diag_files_input0_init_20160929060000_valid_ALL_lead_ALL.txt"
         f" -data {file_list_dir}/grid_diag_files_input1_init_20160929060000_valid_ALL_lead_ALL.txt"
         f" -config {config_file} -out {out_dir}/grid_diag.all.nc {verbosity}"),
    ]

    all_cmds = wrapper.run_all_times()
    special_values = {
        'METPLUS_DATA_DICT': data_fmt,
    }
    compare_command_and_env_vars(all_cmds, expected_cmds, env_var_values,
                                 wrapper, special_values)
