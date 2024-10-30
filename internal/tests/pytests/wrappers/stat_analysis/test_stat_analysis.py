#!/usr/bin/env python3

import pytest

import os
import datetime
import pprint
from dateutil.relativedelta import relativedelta

from metplus.wrappers.stat_analysis_wrapper import StatAnalysisWrapper
from metplus.util import handle_tmp_dir

METPLUS_BASE = os.getcwd().split('/internal')[0]

TEST_CONF = os.path.join(os.path.dirname(__file__), 'test.conf')

pp = pprint.PrettyPrinter()

JOB_ARGS = '-job filter'

def stat_analysis_wrapper(metplus_config):
    """! Returns a default StatAnalysisWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""
    config = metplus_config

    handle_tmp_dir(config)
    config.set('config', 'PROCESS_LIST', 'StatAnalysis')
    config.set('config', 'STAT_ANALYSIS_OUTPUT_DIR',
               '{OUTPUT_BASE}/stat_analysis')
    config.set('config', 'MODEL1_STAT_ANALYSIS_LOOKIN_DIR',
               '{METPLUS_BASE}/internal/tests/data/stat_data')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d')
    config.set('config', 'VALID_BEG', '20190101')
    config.set('config', 'VALID_END', '20190101')
    config.set('config', 'VALID_INCREMENT', '86400')
    config.set('config', 'MODEL1', 'MODEL_TEST')
    config.set('config', 'MODEL1_REFERENCE_NAME', 'MODELTEST')
    config.set('config', 'MODEL1_OBTYPE', 'MODEL_TEST_ANL')
    config.set('config', 'STAT_ANALYSIS_CONFIG_FILE',
               '{PARM_BASE}/met_config/STATAnalysisConfig_wrapped')
    config.set('config', 'STAT_ANALYSIS_JOB_NAME', 'filter')
    config.set('config', 'STAT_ANALYSIS_JOB_ARGS', '-dump_row [dump_row_file]')
    config.set('config', 'MODEL_LIST', '{MODEL1}')
    config.set('config', 'FCST_VALID_HOUR_LIST', '00')
    config.set('config', 'FCST_INIT_HOUR_LIST', '00, 06, 12, 18')
    config.set('config', 'GROUP_LIST_ITEMS', 'FCST_INIT_HOUR_LIST')
    config.set('config', 'LOOP_LIST_ITEMS', 'FCST_VALID_HOUR_LIST, MODEL_LIST')
    config.set('config', 'MODEL1_STAT_ANALYSIS_DUMP_ROW_TEMPLATE',
               ('{fcst_valid_hour?fmt=%H}Z/{MODEL1}/'
                '{MODEL1}_{valid?fmt=%Y%m%d}.stat'))
    config.set('config', 'MODEL1_STAT_ANALYSIS_OUT_STAT_TEMPLATE',
               ('{model?fmt=%s}_{obtype?fmt=%s}_valid{valid?fmt=%Y%m%d}'
                '{valid_hour?fmt=%H}_init{fcst_init_hour?fmt=%s}.stat'))
    return StatAnalysisWrapper(config)


def _set_config_dict_values():
    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = ''
    config_dict['FCST_VAR'] = ''
    config_dict['FCST_LEVEL'] = ''
    config_dict['INTERP_MTHD'] = ''
    config_dict['MODEL'] = '"MODEL_TEST"'
    config_dict['VX_MASK'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict['COV_THRESH'] = ''
    config_dict['OBS_UNITS'] = ''
    config_dict['FCST_THRESH'] = ''
    config_dict['OBS_VAR'] = ''
    config_dict['FCST_INIT_HOUR'] = ''
    config_dict['INTERP_PNTS'] = ''
    config_dict['FCST_LEAD'] = ''
    config_dict['LINE_TYPE'] = ''
    config_dict['FCST_UNITS'] = ''
    config_dict['DESC'] = ''
    config_dict['OBS_LEAD'] = ''
    config_dict['OBS_THRESH'] = ''
    config_dict['OBTYPE'] = '"MODEL_TEST_ANL"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['ALPHA'] = ''
    config_dict['OBS_LEVEL'] = ''
    return config_dict


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'StatAnalysis')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d')
    config.set('config', 'INIT_BEG', '20221014')
    config.set('config', 'INIT_END', '20221014')
    config.set('config', 'STAT_ANALYSIS_OUTPUT_DIR',
               '{OUTPUT_BASE}/StatAnalysis/output')
    config.set('config', 'STAT_ANALYSIS_OUTPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}')
    config.set('config', 'GROUP_LIST_ITEMS', 'DESC_LIST')
    config.set('config', 'LOOP_LIST_ITEMS', 'MODEL_LIST')
    config.set('config', 'MODEL_LIST', 'MODEL_A')
    config.set('config', 'STAT_ANALYSIS_JOB1', JOB_ARGS)
    config.set('config', 'MODEL1', 'MODEL_A')
    config.set('config', 'MODEL1_STAT_ANALYSIS_LOOKIN_DIR',
               '{METPLUS_BASE}/internal/tests/data/stat_data')

    # not required, can be unset for certain tests
    config.set('config', 'STAT_ANALYSIS_CONFIG_FILE',
               '{PARM_BASE}/met_config/STATAnalysisConfig_wrapped')


@pytest.mark.parametrize(
    'config_overrides, expected_env_vars', [
        # 0
        ({}, {}),
        # 1 - fcst valid beg
        ({'STAT_ANALYSIS_FCST_VALID_BEG': '{fcst_valid_beg?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_FCST_VALID_BEG': 'fcst_valid_beg = "20221014_000000";'}),
        # 2 - fcst valid end
        ({'STAT_ANALYSIS_FCST_VALID_END': '{fcst_valid_end?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_FCST_VALID_END': 'fcst_valid_end = "20221015_235959";'}),
        # 3 - fcst valid end with shift
        ({'STAT_ANALYSIS_FCST_VALID_END': '{fcst_valid_end?fmt=%Y%m%d?shift=1d}_000000'},
         {'METPLUS_FCST_VALID_END': 'fcst_valid_end = "20221016_000000";'}),
        # 4 - obs valid beg
        ({'STAT_ANALYSIS_OBS_VALID_BEG': '{obs_valid_beg?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_OBS_VALID_BEG': 'obs_valid_beg = "20221014_000000";'}),
        # 5 - obs valid end
        ({'STAT_ANALYSIS_OBS_VALID_END': '{obs_valid_end?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_OBS_VALID_END': 'obs_valid_end = "20221015_235959";'}),
        # 6 fcst init beg
        ({'STAT_ANALYSIS_FCST_INIT_BEG': '{fcst_init_beg?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_FCST_INIT_BEG': 'fcst_init_beg = "20221014_000000";'}),
        # 7 - fcst init end
        ({'STAT_ANALYSIS_FCST_INIT_END': '{fcst_init_end?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_FCST_INIT_END': 'fcst_init_end = "20221015_235959";'}),
        # 8 - fcst valid hour single
        ({'FCST_VALID_HOUR_LIST': '12'},
         {'METPLUS_FCST_VALID_HOUR': 'fcst_valid_hour = ["120000"];'}),
        # 9 - fcst valid hour multiple
        ({'FCST_VALID_HOUR_LIST': '12,108'},
         {'METPLUS_FCST_VALID_HOUR': 'fcst_valid_hour = ["120000", "1080000"];'}),
        # 10 - obs init beg
        ({'STAT_ANALYSIS_OBS_INIT_BEG': '{obs_init_beg?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_OBS_INIT_BEG': 'obs_init_beg = "20221014_000000";'}),
        # 11 - obs init end
        ({'STAT_ANALYSIS_OBS_INIT_END': '{obs_init_end?fmt=%Y%m%d_%H%M%S}'},
         {'METPLUS_OBS_INIT_END': 'obs_init_end = "20221015_235959";'}),
        # 12 - generic valid beg
        ({'STAT_ANALYSIS_VALID_BEG': '{fcst_valid_beg?fmt=%Y%m%d}_12'},
         {'METPLUS_FCST_VALID_BEG': 'fcst_valid_beg = "20221014_12";',
          'METPLUS_OBS_VALID_BEG': 'obs_valid_beg = "20221014_12";'}),
        # 13 - generic valid end
        ({'STAT_ANALYSIS_VALID_END': '{fcst_valid_end?fmt=%Y%m%d}_12'},
         {'METPLUS_FCST_VALID_END': 'fcst_valid_end = "20221015_12";',
          'METPLUS_OBS_VALID_END': 'obs_valid_end = "20221015_12";'}),
        # 14 - generic init beg
        ({'STAT_ANALYSIS_INIT_BEG': '{fcst_init_beg?fmt=%Y%m%d}_12'},
         {'METPLUS_FCST_INIT_BEG': 'fcst_init_beg = "20221014_12";',
          'METPLUS_OBS_INIT_BEG': 'obs_init_beg = "20221014_12";'}),
        # 15 - generic init end
        ({'STAT_ANALYSIS_INIT_END': '{fcst_init_end?fmt=%Y%m%d}_12'},
         {'METPLUS_FCST_INIT_END': 'fcst_init_end = "20221015_12";',
          'METPLUS_OBS_INIT_END': 'obs_init_end = "20221015_12";'}),
        # 16 - custom in MODEL1
        ({'STAT_ANALYSIS_CUSTOM_LOOP_LIST': 'CUSTOM_MODEL',
          'MODEL1': '{custom}',
          'MODEL_LIST': '{custom}'},
         {'METPLUS_MODEL': 'model = ["CUSTOM_MODEL"];'}),
        # 17 - fcst_lev
        ({'FCST_LEVEL_LIST': 'R5'},
         {'METPLUS_FCST_LEVEL': 'fcst_lev = ["R5"];'}),
        # 17 - obs_lev
        ({'OBS_LEVEL_LIST': 'R7'},
         {'METPLUS_OBS_LEVEL': 'obs_lev = ["R7"];'}),
    ]
)
@pytest.mark.wrapper_d
def test_valid_init_env_vars(metplus_config, config_overrides,
                             expected_env_vars):
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config', 'INIT_END', '20221015')
    for key, value in config_overrides.items():
        config.set('config', key, value)

    if 'METPLUS_MODEL' not in expected_env_vars:
        expected_env_vars['METPLUS_MODEL'] = 'model = ["MODEL_A"];'

    if 'METPLUS_JOBS' not in expected_env_vars:
        expected_env_vars['METPLUS_JOBS'] = f'jobs = ["{JOB_ARGS}"];'

    wrapper = StatAnalysisWrapper(config)
    assert wrapper.isOK

    time_input = {
        'custom': config_overrides.get('STAT_ANALYSIS_CUSTOM_LOOP_LIST', '')
    }
    runtime_settings_dict_list = wrapper._get_all_runtime_settings(time_input)
    assert runtime_settings_dict_list

    first_runtime_only = runtime_settings_dict_list[0]
    wrapper._run_stat_analysis_job(first_runtime_only)
    all_cmds = wrapper.all_commands

    print(f"ALL COMMANDS: {all_cmds}")
    _, actual_env_vars = all_cmds[0]

    missing_env = [item for item in expected_env_vars
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]
    env_var_keys = wrapper.WRAPPER_ENV_VAR_KEYS + missing_env

    for env_var_key in env_var_keys:
        match = next((item for item in actual_env_vars if
                      item.startswith(env_var_key)), None)
        assert match is not None
        actual_value = match.split('=', 1)[1]
        print(f"ENV VAR: {env_var_key}")
        assert expected_env_vars.get(env_var_key, '') == actual_value


@pytest.mark.parametrize(
    'config_overrides, expected_result', [
        ({}, True),
        ({'STAT_ANALYSIS_JOB1': '-job filter -dump_row [dump_row_file]'},
         False),
        ({'STAT_ANALYSIS_JOB1': '-job filter -dump_row [dump_row_file]',
          'MODEL1_STAT_ANALYSIS_DUMP_ROW_TEMPLATE': 'some/template'},
         True),
        ({'STAT_ANALYSIS_JOB1': '-job filter -out_stat [out_stat_file]'},
         False),
        ({'STAT_ANALYSIS_JOB1': '-job filter -out_stat [out_stat_file]',
          'MODEL1_STAT_ANALYSIS_OUT_STAT_TEMPLATE': 'some/template'},
         True),
        ({'STAT_ANALYSIS_JOB1': '-job filter -dump_row [dump_row_file]',
          'STAT_ANALYSIS_JOB2': '-job filter -out_stat [out_stat_file]',
          'MODEL1_STAT_ANALYSIS_DUMP_ROW_TEMPLATE': 'some/template'},
         False),
        ({'STAT_ANALYSIS_JOB1': '-job filter -dump_row [dump_row_file]',
          'STAT_ANALYSIS_JOB2': '-job filter -out_stat [out_stat_file]',
          'MODEL1_STAT_ANALYSIS_DUMP_ROW_TEMPLATE': 'some/template',
          'MODEL1_STAT_ANALYSIS_OUT_STAT_TEMPLATE': 'some/template'},
         True),
    ]
)
@pytest.mark.wrapper_d
def test_check_required_job_template(metplus_config, config_overrides,
                                     expected_result):
    config = metplus_config
    set_minimum_config_settings(config)
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = StatAnalysisWrapper(config)
    print(wrapper.c_dict['JOBS'])
    print(wrapper.c_dict['MODEL_INFO_LIST'])
    assert wrapper.isOK == expected_result


@pytest.mark.parametrize(
    'c_dict, expected_result', [
      # 0
      ({
           'GROUP_LIST_ITEMS': ['MODEL_LIST', 'FCST_LEAD_LIST'],
           'LOOP_LIST_ITEMS': [],
           'MODEL_LIST': ['"MODEL1"', '"MODEL2"'],
           'FCST_LEAD_LIST': ['0', '24'],
       },
       [
           {'MODEL': '"MODEL1", "MODEL2"',
            'FCST_LEAD': '0, 24'
            }
       ]
       ),
      # 1
      ({
           'GROUP_LIST_ITEMS': ['FCST_LEAD_LIST'],
           'LOOP_LIST_ITEMS': ['MODEL_LIST'],
           'MODEL_LIST': ['"MODEL1"', '"MODEL2"'],
           'FCST_LEAD_LIST': ['0', '24'],
       },
       [
           {'MODEL': '"MODEL1"', 'FCST_LEAD': '0, 24'},
           {'MODEL': '"MODEL2"', 'FCST_LEAD': '0, 24'},
       ]
       ),
      # 2
      ({
         'GROUP_LIST_ITEMS': [],
         'LOOP_LIST_ITEMS': ['MODEL_LIST', 'FCST_LEAD_LIST'],
         'MODEL_LIST': ['"MODEL1"', '"MODEL2"'],
         'FCST_LEAD_LIST': ['0', '24'],
       },
       [
           {'MODEL': '"MODEL1"', 'FCST_LEAD': '0'},
           {'MODEL': '"MODEL2"', 'FCST_LEAD': '0'},
           {'MODEL': '"MODEL1"', 'FCST_LEAD': '24'},
           {'MODEL': '"MODEL2"', 'FCST_LEAD': '24'},
       ]
       ),
      # 3
      ({
         'GROUP_LIST_ITEMS': ['DESC_LIST'],
         'LOOP_LIST_ITEMS': ['MODEL_LIST', 'FCST_LEAD_LIST',
                             'FCST_THRESH_LIST'],
         'MODEL_LIST': ['"MODEL1"', '"MODEL2"'],
         'FCST_LEAD_LIST': ['0', '24'],
         'FCST_THRESH_LIST': ['gt3', 'ge4'],
         'DESC_LIST': ['"ONE_DESC"'],
       },
       [
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '0', 'FCST_THRESH': 'gt3', 'MODEL': '"MODEL1"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '0', 'FCST_THRESH': 'gt3', 'MODEL': '"MODEL2"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '0', 'FCST_THRESH': 'ge4', 'MODEL': '"MODEL1"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '0', 'FCST_THRESH': 'ge4', 'MODEL': '"MODEL2"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '24', 'FCST_THRESH': 'gt3', 'MODEL': '"MODEL1"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '24', 'FCST_THRESH': 'gt3', 'MODEL': '"MODEL2"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '24', 'FCST_THRESH': 'ge4', 'MODEL': '"MODEL1"'},
           {'DESC': '"ONE_DESC"',
            'FCST_LEAD': '24', 'FCST_THRESH': 'ge4', 'MODEL': '"MODEL2"'},
       ]
       ),
    ]
)
@pytest.mark.wrapper_d
def test_get_runtime_settings(metplus_config, c_dict, expected_result):
    config = metplus_config
    wrapper = StatAnalysisWrapper(config)

    runtime_settings = wrapper._get_runtime_settings(c_dict)

    pp.pprint(runtime_settings)
    assert runtime_settings == expected_result

@pytest.mark.parametrize(
    'list_name, config_overrides, expected_value', [
      ('FCST_LEAD_LIST', {'FCST_LEAD_LIST': '12'}, ['12']),
      ('FCST_LEAD_LIST', {'FCST_LEAD_LIST': '12,24'}, ['12', '24']),
      ('FCST_LEAD_LIST',
       {'FCST_LEAD_LIST1': '12,24', 'FCST_LEAD_LIST2': '48,96'},
       ['12,24', '48,96']),
      ('FCST_LEAD_LIST',
       {'FCST_LEAD_LIST1': 'begin_end_incr(12,24,12)',
        'FCST_LEAD_LIST2': 'begin_end_incr(48,96,48)'},
       ['12,24', '48,96']),
    ]
)
@pytest.mark.wrapper_d
def test_format_conf_list(metplus_config, list_name, config_overrides,
                          expected_value):
    config = metplus_config
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = StatAnalysisWrapper(config)

    assert wrapper._format_conf_list(list_name) == expected_value


@pytest.mark.wrapper_d
def test_get_command(metplus_config):
    # Independently test that the stat_analysis command
    # is being put together correctly with
    # the full path to stat_analysis, the 
    # lookin dir, and config file
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_command = (
        st.config.getdir('MET_BIN_DIR', '')
        +'/stat_analysis -v 2 '
        +'-lookin /path/to/lookin_dir '
        +'-config /path/to/STATAnalysisConfig'
    )
    st.c_dict['LOOKIN_DIR'] = '/path/to/lookin_dir'
    st.args.append('-config /path/to/STATAnalysisConfig')
    test_command = st.get_command()
    assert expected_command == test_command


@pytest.mark.wrapper_d
def test_create_c_dict(metplus_config):
    # Independently test that c_dict is being created
    # and that the wrapper and config reader 
    # is setting the values as expected
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    c_dict = st.create_c_dict()

    actual_config = os.path.join(METPLUS_BASE, 'parm', 'met_config',
                                 'STATAnalysisConfig_wrapped')
    actual_outdir = os.path.join(st.config.getdir('OUTPUT_BASE'),
                                 'stat_analysis')
    assert os.path.realpath(c_dict['CONFIG_FILE']) == actual_config
    assert c_dict['OUTPUT_DIR'] == actual_outdir
    assert 'FCST_INIT_HOUR_LIST' in c_dict['GROUP_LIST_ITEMS']
    assert 'FCST_VALID_HOUR_LIST' in c_dict['LOOP_LIST_ITEMS']
    assert 'MODEL_LIST' in c_dict['LOOP_LIST_ITEMS']
    assert c_dict['VAR_LIST'] == []
    assert c_dict['MODEL_LIST'] == ['"MODEL_TEST"']
    assert c_dict['DESC_LIST'] == []
    assert c_dict['FCST_LEAD_LIST'] == []
    assert c_dict['OBS_LEAD_LIST'] == []
    assert c_dict['FCST_VALID_HOUR_LIST'] == ['00']
    assert c_dict['FCST_INIT_HOUR_LIST'] == ['00', '06', '12', '18']
    assert c_dict['OBS_VALID_HOUR_LIST'] == []
    assert c_dict['OBS_INIT_HOUR_LIST'] == []
    assert c_dict['VX_MASK_LIST'] == []
    assert c_dict['INTERP_MTHD_LIST'] == []
    assert c_dict['INTERP_PNTS_LIST'] == []
    assert c_dict['COV_THRESH_LIST'] == []
    assert c_dict['ALPHA_LIST'] == []
    assert c_dict['LINE_TYPE_LIST'] == []


@pytest.mark.wrapper_d
def test_set_lists_as_loop_or_group(metplus_config):
    # Independently test that the lists that are set
    # in the config file are being set 
    # accordingly based on their place 
    # in GROUP_LIST_ITEMS and LOOP_LIST_ITEMS 
    # and those not set are set to GROUP_LIST_ITEMS
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_lists_to_group_items = ['FCST_INIT_HOUR_LIST', 'DESC_LIST',
                                     'FCST_LEAD_LIST', 'OBS_LEAD_LIST',
                                     'OBS_VALID_HOUR_LIST',
                                     'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST',
                                     'OBS_VAR_LIST', 'FCST_UNITS_LIST',
                                     'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                                     'OBS_LEVEL_LIST', 'VX_MASK_LIST',
                                     'INTERP_MTHD_LIST', 'INTERP_PNTS_LIST',
                                     'FCST_THRESH_LIST', 'OBS_THRESH_LIST',
                                     'COV_THRESH_LIST', 'ALPHA_LIST',
                                     'LINE_TYPE_LIST']
    expected_lists_to_loop_items = ['FCST_VALID_HOUR_LIST', 'MODEL_LIST']
    config_dict = {}
    config_dict['LOOP_ORDER'] = 'times'
    config_dict['PROCESS_LIST'] = 'StatAnalysis'
    config_dict['CONFIG_FILE'] = (
        'PARM_BASE/grid_to_grid/met_config/STATAnalysisConfig'
    )
    config_dict['OUTPUT_DIR'] = 'OUTPUT_BASE/stat_analysis'
    config_dict['GROUP_LIST_ITEMS'] = ['FCST_INIT_HOUR_LIST']
    config_dict['LOOP_LIST_ITEMS'] = ['FCST_VALID_HOUR_LIST', 'MODEL_LIST']
    config_dict['FCST_VAR_LIST'] = []
    config_dict['OBS_VAR_LIST'] = []
    config_dict['FCST_LEVEL_LIST'] = []
    config_dict['OBS_LEVEL_LIST'] = []
    config_dict['FCST_UNITS_LIST'] = []
    config_dict['OBS_UNITS_LIST'] = []
    config_dict['FCST_THRESH_LIST'] = []
    config_dict['OBS_THRESH_LIST'] = []
    config_dict['MODEL_LIST'] = ['MODEL_TEST']
    config_dict['DESC_LIST'] = []
    config_dict['FCST_LEAD_LIST'] = []
    config_dict['OBS_LEAD_LIST'] = []
    config_dict['FCST_VALID_HOUR_LIST'] = ['00', '06', '12', '18']
    config_dict['FCST_INIT_HOUR_LIST'] = ['00', '06', '12', '18']
    config_dict['OBS_VALID_HOUR_LIST'] = []
    config_dict['OBS_INIT_HOUR_LIST'] = []
    config_dict['VX_MASK_LIST'] = []
    config_dict['INTERP_MTHD_LIST'] = []
    config_dict['INTERP_PNTS_LIST'] = []
    config_dict['COV_THRESH_LIST'] = []
    config_dict['ALPHA_LIST'] = []
    config_dict['LINE_TYPE_LIST'] = []
    config_dict = st._set_lists_loop_or_group(config_dict)
    test_lists_to_loop_items = config_dict['LOOP_LIST_ITEMS']
    test_lists_to_group_items = config_dict['GROUP_LIST_ITEMS']

    assert(all(elem in expected_lists_to_group_items
               for elem in test_lists_to_group_items))
    assert(all(elem in expected_lists_to_loop_items 
               for elem in test_lists_to_loop_items))


@pytest.mark.parametrize(
    'lists_to_loop,c_dict_overrides,config_dict_overrides,expected_values', [
        # Test 0
        (['FCST_VALID_HOUR_LIST', 'MODEL_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190105', 'DATE_TYPE': 'VALID'},
         {'FCST_VALID_HOUR': '0', 'FCST_INIT_HOUR': '0, 6, 12, 18'},
         {'valid_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'valid_end': datetime.datetime(2019, 1, 5, 0, 0, 0),
          'fcst_valid_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_valid_end': datetime.datetime(2019, 1, 5, 0, 0, 0),
          'fcst_valid_hour': relativedelta(),
          'valid_hour': relativedelta(),
          'fcst_valid_hour_beg': relativedelta(),
          'fcst_valid_hour_end': relativedelta(),
          'valid_hour_beg': relativedelta(),
          'valid_hour_end': relativedelta(),
          'model': 'MODEL_TEST',
          'obtype': 'MODEL_TEST_ANL',
          'fcst_init_hour': '000000_060000_120000_180000',
          'fcst_init_hour_beg': relativedelta(),
          'fcst_init_hour_end': relativedelta(hours=18),
          'init_hour_beg': relativedelta(),
          'init_hour_end': relativedelta(hours=18),
          'fcst_var': '',
          'fcst_level': '',
          'fcst_units': '',
          'fcst_thresh': '',
          'desc': '',
          },
         ),
        # Test 1
        (['FCST_VALID_HOUR_LIST', 'MODEL_LIST', 'FCST_LEAD_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190101', 'DATE_TYPE': 'VALID'},
         {'FCST_VALID_HOUR': '0', 'FCST_INIT_HOUR': '0, 6, 12, 18',
          'FCST_LEAD': '24'},
         {'valid': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_valid': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_lead_totalsec': '86400',
          'fcst_lead_hour': '24',
          'fcst_lead_min': '00',
          'fcst_lead_sec': '00',
          'fcst_lead': '240000',
          'lead_totalsec': '86400',
          'lead_hour': '24',
          'lead_min': '00',
          'lead_sec': '00',
          'lead': '240000',
          },
         ),
        # Test 2
        (['FCST_VALID_HOUR_LIST', 'MODEL_LIST', 'FCST_LEAD_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190101', 'DATE_TYPE': 'VALID'},
         {'FCST_VALID_HOUR': '0', 'FCST_INIT_HOUR': '0, 6, 12, 18',
          'FCST_LEAD': '120'},
         {'valid': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_valid': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_lead_totalsec': '432000',
          'fcst_lead_hour': '120',
          'fcst_lead_min': '00',
          'fcst_lead_sec': '00',
          'fcst_lead': '1200000',
          'lead_totalsec': '432000',
          'lead_hour': '120',
          'lead_min': '00',
          'lead_sec': '00',
          'lead': '1200000',
          },
         ),
        # Test 3
        (['FCST_VALID_HOUR_LIST', 'MODEL_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190105', 'DATE_TYPE': 'INIT'},
         {'FCST_VALID_HOUR': '0', 'FCST_INIT_HOUR': '0, 6, 12, 18'},
         {'init_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'init_end': datetime.datetime(2019, 1, 5, 18, 0, 0),
          'fcst_init_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_init_end': datetime.datetime(2019, 1, 5, 18, 0, 0),
          'fcst_init_hour_beg': relativedelta(),
          'fcst_init_hour_end': relativedelta(hours=18),
          'init_hour_beg': relativedelta(),
          'init_hour_end': relativedelta(hours=18),
          },
         ),
        # Test 4
        (['FCST_VALID_HOUR_LIST', 'MODEL_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190101', 'DATE_TYPE': 'INIT'},
         {'FCST_VALID_HOUR': '0', 'FCST_INIT_HOUR': '', 'FCST_LEAD': ''},
         {'init_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'init_end': datetime.datetime(2019, 1, 1, 23, 59, 59),
          'fcst_init_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'fcst_init_end': datetime.datetime(2019, 1, 1, 23, 59, 59),
          'obs_init_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'obs_init_end': datetime.datetime(2019, 1, 1, 23, 59, 59),
          'fcst_init_hour_beg': relativedelta(),
          'fcst_init_hour_end': relativedelta(hours=23, minutes=59, seconds=59),
          'obs_init_hour_beg': relativedelta(),
          'obs_init_hour_end': relativedelta(hours=23, minutes=59, seconds=59),
          },
         ),
        # Test 5 - check computed init_beg/end
        (['FCST_LEAD_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190105',
          'DATE_TYPE': 'VALID'},
         {'FCST_VALID_HOUR': '0', 'FCST_LEAD': '12,24'},
         {'valid_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'valid_end': datetime.datetime(2019, 1, 5, 0, 0, 0),
          'init_beg': datetime.datetime(2018, 12, 31, 0, 0, 0),
          'init_end': datetime.datetime(2019, 1, 4, 12, 0, 0),
          },
         ),
        # Test 6 - check computed valid_beg/end
        (['FCST_LEAD_LIST'],
         {'DATE_BEG': '20190101', 'DATE_END': '20190105',
          'DATE_TYPE': 'INIT'},
         {'FCST_INIT_HOUR': '0', 'FCST_LEAD': '12,24'},
         {'init_beg': datetime.datetime(2019, 1, 1, 0, 0, 0),
          'init_end': datetime.datetime(2019, 1, 5, 0, 0, 0),
          'valid_beg': datetime.datetime(2019, 1, 1, 12, 0, 0),
          'valid_end': datetime.datetime(2019, 1, 6, 0, 0, 0),
          },
         ),
    ]
)
@pytest.mark.wrapper_d
def test_build_stringsub_dict(metplus_config, lists_to_loop, c_dict_overrides,
                              config_dict_overrides, expected_values):
    # Independently test the building of 
    # the dictionary used in the stringtemplate
    # substitution and the values are being set
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = _set_config_dict_values()

    # Test 1
    for key, value in c_dict_overrides.items():
        if key in ('DATE_BEG', 'DATE_END'):
            st.c_dict[key] = datetime.datetime.strptime(value, '%Y%m%d')
        else:
            st.c_dict[key] = value

    for key, value in config_dict_overrides.items():
        config_dict[key] = value

    lists_to_group = [item for item in st.EXPECTED_CONFIG_LISTS
                      if item not in lists_to_loop]
    config_dict['LISTS_TO_GROUP'] = lists_to_group
    config_dict['LISTS_TO_LOOP'] = lists_to_loop

    test_stringsub_dict = st._build_stringsub_dict(config_dict)

    print(test_stringsub_dict)
    for key, value in expected_values.items():
        print(f'key: {key}')
        assert test_stringsub_dict[key] == value


@pytest.mark.parametrize(
    'filename_template, output_type, expected_output', [
        (('{fcst_valid_hour?fmt=%H}Z/{model?fmt=%s}/'
          '{model?fmt=%s}_{valid?fmt=%Y%m%d}.stat'),
         'dump_row', '00Z/MODEL_TEST/MODEL_TEST_20190101.stat'),
        (('{model?fmt=%s}_{obtype?fmt=%s}_valid{valid?fmt=%Y%m%d}_'
          'fcstvalidhour000000Z_dump_row.stat'),
         'dump_row', ('MODEL_TEST_MODEL_TEST_ANL_valid20190101_'
                      'fcstvalidhour000000Z_dump_row.stat')
        ),
        (('{model?fmt=%s}_{obtype?fmt=%s}_valid{valid?fmt=%Y%m%d}'
          '{valid_hour?fmt=%H}_init{fcst_init_hour?fmt=%s}.stat'),
         'out_stat', ('MODEL_TEST_MODEL_TEST_ANL_valid2019010100'
                      '_init000000_060000_120000_180000.stat')
         ),
    ]
)
@pytest.mark.wrapper_d
def test_get_output_filename(metplus_config, filename_template, output_type,
                             expected_output):
    # Independently test the building of
    # the output file name 
    # using string template substitution
    # and test the values is
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = _set_config_dict_values()
    config_dict['FCST_VALID_HOUR'] = '0'
    config_dict['FCST_INIT_HOUR'] = '0, 6, 12, 18'

    st.c_dict['DATE_BEG'] = datetime.datetime.strptime('20190101', '%Y%m%d')
    st.c_dict['DATE_END'] = datetime.datetime.strptime('20190101', '%Y%m%d')
    st.c_dict['DATE_TYPE'] = 'VALID'

    stringsub_dict = st._build_stringsub_dict(config_dict)
    test_output_filename = st._get_output_filename(output_type,
                                                   filename_template,
                                                   stringsub_dict)
    assert expected_output == test_output_filename


@pytest.mark.wrapper_d
def test_get_lookin_dir(metplus_config):
    # Independently test the building of
    # the lookin directory
    # using string template substitution
    # and wildcard filling
    # and test the value is
    # as expected
    st = stat_analysis_wrapper(metplus_config)
    config_dict = {}
    config_dict['FCST_VALID_HOUR'] = '0'
    config_dict['FCST_VAR'] = ''
    config_dict['FCST_LEVEL'] = ''
    config_dict['INTERP_MTHD'] = ''
    config_dict['MODEL'] = '"MODEL_TEST"'
    config_dict['VX_MASK'] = ''
    config_dict['OBS_INIT_HOUR'] = ''
    config_dict['COV_THRESH'] = ''
    config_dict['OBS_UNITS'] = ''
    config_dict['FCST_THRESH'] = ''
    config_dict['OBS_VAR'] = ''
    config_dict['FCST_INIT_HOUR'] = '0, 6, 12, 18'
    config_dict['INTERP_PNTS'] = ''
    config_dict['FCST_LEAD'] = ''
    config_dict['LINE_TYPE'] = ''
    config_dict['FCST_UNITS'] = ''
    config_dict['DESC'] = ''
    config_dict['OBS_LEAD'] = ''
    config_dict['OBS_THRESH'] = ''
    config_dict['OBTYPE'] = '"MODEL_TEST_ANL"'
    config_dict['OBS_VALID_HOUR'] = ''
    config_dict['ALPHA'] = ''
    config_dict['OBS_LEVEL'] = ''
    st.c_dict['DATE_BEG'] = datetime.datetime.strptime('20180201', '%Y%m%d')
    st.c_dict['DATE_END'] = datetime.datetime.strptime('20180201', '%Y%m%d')
    st.c_dict['DATE_TYPE'] = 'VALID'

    lists_to_group = ['FCST_INIT_HOUR_LIST', 'DESC_LIST', 'FCST_LEAD_LIST',
                      'OBS_LEAD_LIST', 'OBS_VALID_HOUR_LIST',
                      'OBS_INIT_HOUR_LIST', 'FCST_VAR_LIST', 'OBS_VAR_LIST',
                      'FCST_UNITS_LIST', 'OBS_UNITS_LIST', 'FCST_LEVEL_LIST',
                      'OBS_LEVEL_LIST', 'VX_MASK_LIST', 'INTERP_MTHD_LIST',
                      'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
                      'OBS_THRESH_LIST', 'COV_THRESH_LIST', 'ALPHA_LIST',
                      'LINE_TYPE_LIST']
    lists_to_loop = ['FCST_VALID_HOUR_LIST', 'MODEL_LIST']
    config_dict['LISTS_TO_GROUP'] = lists_to_group
    config_dict['LISTS_TO_LOOP'] = lists_to_loop

    pytest_data_dir = os.path.join(os.path.dirname(__file__), os.pardir,
                                   os.pardir, os.pardir, 'data')
    # Test 1
    expected_lookin_dir = os.path.join(pytest_data_dir, 'fake/20180201')
    dir_path = os.path.join(pytest_data_dir, 'fake/*')

    test_lookin_dir = st._get_lookin_dir(dir_path, config_dict)
    assert expected_lookin_dir == test_lookin_dir

    # Test 2
    expected_lookin_dir = os.path.join(pytest_data_dir, 'fake/20180201')
    dir_path = os.path.join(pytest_data_dir, 'fake/{valid?fmt=%Y%m%d}')

    test_lookin_dir = st._get_lookin_dir(dir_path, config_dict)
    assert expected_lookin_dir == test_lookin_dir

    # Test 3 - no matches for lookin dir wildcard
    expected_lookin_dir = ''
    dir_path = os.path.join(pytest_data_dir, 'fake/*nothingmatches*')

    test_lookin_dir = st._get_lookin_dir(dir_path, config_dict)
    assert expected_lookin_dir == test_lookin_dir

    # Test 4 - 2 paths, one with wildcard
    expected_lookin_dir = os.path.join(pytest_data_dir, 'fake/20180201')
    expected_lookin_dir = f'{expected_lookin_dir} {expected_lookin_dir}'
    dir_path = os.path.join(pytest_data_dir, 'fake/*')
    dir_path = f'{dir_path}, {dir_path}'

    test_lookin_dir = st._get_lookin_dir(dir_path, config_dict)
    assert expected_lookin_dir == test_lookin_dir


@pytest.mark.parametrize(
    'c_dict_overrides, config_dict_overrides, expected_values', [
        # Test 0
        ({'DATE_BEG': '20190101', 'DATE_END': '20190105', 'DATE_TYPE': 'VALID'},
         {'FCST_VALID_HOUR': '0', 'FCST_INIT_HOUR': '0, 12',
          'OBS_VALID_HOUR': '', 'OBS_INIT_HOUR': ''},
         {'FCST_VALID_BEG': '20190101_000000',
          'FCST_VALID_END': '20190105_000000',
          'FCST_VALID_HOUR': '"000000"',
          'FCST_INIT_HOUR': '"000000", "120000"',
          'OBS_VALID_BEG': '20190101_000000',
          'OBS_VALID_END': '20190105_235959',
          },
         ),
        # Test 1
        (
        {'DATE_BEG': '20190101', 'DATE_END': '20190105', 'DATE_TYPE': 'VALID'},
        {'FCST_VALID_HOUR': '0, 12', 'FCST_INIT_HOUR': '0, 12',
         'OBS_VALID_HOUR': '', 'OBS_INIT_HOUR': ''},
        {'FCST_VALID_BEG': '20190101_000000',
         'FCST_VALID_END': '20190105_120000',
         'FCST_VALID_HOUR': '"000000", "120000"',
         'FCST_INIT_HOUR': '"000000", "120000"',
         'OBS_VALID_BEG': '20190101_000000',
         'OBS_VALID_END': '20190105_235959',
         },
        ),
        # Test 2
        (
        {'DATE_BEG': '20190101', 'DATE_END': '20190101', 'DATE_TYPE': 'VALID'},
        {'FCST_VALID_HOUR': '', 'FCST_INIT_HOUR': '',
         'OBS_VALID_HOUR': '000000', 'OBS_INIT_HOUR': '0, 12'},
        {'OBS_VALID_BEG': '20190101_000000',
         'OBS_VALID_END': '20190101_000000',
         'OBS_VALID_HOUR': '"000000"',
         'OBS_INIT_HOUR': '"000000", "120000"',
         'FCST_VALID_BEG': '20190101_000000',
         'FCST_VALID_END': '20190101_235959',
         },
        ),
        # Test 3
        ({'DATE_BEG': '20190101', 'DATE_END': '20190101', 'DATE_TYPE': 'INIT'},
         {'FCST_VALID_HOUR': '', 'FCST_INIT_HOUR': '',
          'OBS_VALID_HOUR': '000000', 'OBS_INIT_HOUR': '0, 12'},
         {'OBS_INIT_BEG': '20190101_000000',
          'OBS_INIT_END': '20190101_120000',
          'OBS_VALID_HOUR': '"000000"',
          'OBS_INIT_HOUR': '"000000", "120000"',
          'FCST_INIT_BEG': '20190101_000000',
          'FCST_INIT_END': '20190101_235959',
          },
        ),
    ]
)
@pytest.mark.wrapper_d
def test_format_valid_init(metplus_config, c_dict_overrides,
                           config_dict_overrides, expected_values):
    # Independently test the formatting 
    # of the valid and initialization date and hours
    # from the METplus config file for the MET
    # config file and that they are formatted
    # correctly
    st = stat_analysis_wrapper(metplus_config)

    for key, value in c_dict_overrides.items():
        if key in ('DATE_BEG', 'DATE_END'):
            st.c_dict[key] = datetime.datetime.strptime(value, '%Y%m%d')
        else:
            st.c_dict[key] = value

    config_dict = {}
    for key, value in config_dict_overrides.items():
        config_dict[key] = value

    stringsub_dict = st._build_stringsub_dict(config_dict)
    output_dict = st._format_valid_init(config_dict, stringsub_dict)
    print(output_dict)
    for key, value in output_dict.items():
        print(key)
        if key not in expected_values:
            assert value == ''
        else:
            assert value == expected_values[key]


@pytest.mark.wrapper_d
def test_parse_model_info(metplus_config):
    # Independently test the creation of 
    # the model information dictionary
    # and the reading from the config file
    # are as expected
    st = stat_analysis_wrapper(metplus_config)
    # Test 1
    expected_name = '"MODEL_TEST"'
    expected_obtype = '"MODEL_TEST_ANL"'
    expected_dump_row_filename_template = (
        '{fcst_valid_hour?fmt=%H}Z/MODEL_TEST/'
        +'MODEL_TEST_{valid?fmt=%Y%m%d}.stat'
    )
    expected_dump_row_filename_type = 'user'
    expected_out_stat_filename_template = (
        '{model?fmt=%s}_'
        '{obtype?fmt=%s}_valid'
        '{valid?fmt=%Y%m%d}{valid_hour?fmt=%H}_init'
        '{fcst_init_hour?fmt=%s}.stat'
    )

    expected_out_stat_filename_type = 'user'
    test_model_info_list = st._parse_model_info()
    assert test_model_info_list[0]['name'] == expected_name
    assert test_model_info_list[0]['obtype'] == expected_obtype
    assert (test_model_info_list[0]['dump_row_filename_template'] ==
            expected_dump_row_filename_template)
    assert (test_model_info_list[0]['out_stat_filename_template']
            == expected_out_stat_filename_template)


@pytest.mark.parametrize(
    'data_type, config_list, expected_list', [
      ('FCST', '\"0,*,*\"', ['"0,*,*"']),
      ('FCST', '\"(0,*,*)\"', ['"0,*,*"']),
      ('FCST', '\"0,*,*\", \"1,*,*\"', ['"0,*,*"', '"1,*,*"']),
      ('FCST', '\"(0,*,*)\", \"(1,*,*)\"', ['"0,*,*"', '"1,*,*"']),
      ('OBS', '\"0,*,*\"', ['"0,*,*"']),
      ('OBS', '\"(0,*,*)\"', ['"0,*,*"']),
      ('OBS', '\"0,*,*\", \"1,*,*\"', ['"0,*,*"', '"1,*,*"']),
      ('OBS', '\"(0,*,*)\", \"(1,*,*)\"', ['"0,*,*"', '"1,*,*"']),
    ]
)
@pytest.mark.wrapper_d
def test_get_level_list(metplus_config, data_type, config_list, expected_list):
    config = metplus_config
    config.set('config', f'{data_type}_LEVEL_LIST', config_list)

    saw = StatAnalysisWrapper(config)

    assert saw._get_level_list(data_type) == expected_list


@pytest.mark.wrapper_d
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'
    config = metplus_config
    config.set('config', 'INPUT_MUST_EXIST', False)

    wrapper = StatAnalysisWrapper(config)
    assert not wrapper.c_dict['CONFIG_FILE']

    config.set('config', 'STAT_ANALYSIS_CONFIG_FILE', fake_config_name)
    wrapper = StatAnalysisWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
