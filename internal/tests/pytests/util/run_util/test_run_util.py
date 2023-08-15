import os
import pytest
from unittest import mock
import metplus.util.run_util as ru

EXPECTED_CONFIG_KEYS = ['CLOCK_TIME', 'MET_INSTALL_DIR', 'MET_BIN_DIR',
                        'INPUT_BASE', 'OUTPUT_BASE', 'METPLUS_CONF',
                        'TMP_DIR', 'STAGING_DIR', 'FILE_LISTS_DIR', 'CONVERT',
                        'GEMPAKTOCF_JAR', 'GFDL_TRACKER_EXEC', 
                        'PROCESS_LIST', 'OMP_NUM_THREADS',
                        'SCRUB_STAGING_DIR', 'LOG_METPLUS', 'LOG_DIR',
                        'LOG_TIMESTAMP_TEMPLATE', 'LOG_TIMESTAMP_USE_DATATIME',
                        'LOG_MET_OUTPUT_TO_METPLUS', 'LOG_LEVEL',
                        'LOG_LEVEL_TERMINAL', 'LOG_MET_VERBOSITY',
                        'LOG_LINE_FORMAT', 'LOG_ERR_LINE_FORMAT',
                        'LOG_DEBUG_LINE_FORMAT', 'LOG_INFO_LINE_FORMAT',
                        'LOG_LINE_DATE_FORMAT', 'DO_NOT_RUN_EXE', 'CONFIG_INPUT',
                        'RUN_ID', 'LOG_TIMESTAMP', 'METPLUS_BASE', 'PARM_BASE',
                        'METPLUS_VERSION']


def get_run_util_configs(conf_name):
    script_dir = os.path.dirname(__file__)
    return [os.path.join(script_dir, conf_name)]


@pytest.mark.util
def test_pre_run_setup():
    conf_inputs = get_run_util_configs('run_util.conf')
    actual = ru.pre_run_setup(conf_inputs)
    
    # check all config keys are set correctly
    assert sorted(actual.keys('config')) == sorted(EXPECTED_CONFIG_KEYS)
    
    # spot check a few specific items
    expected_stage = os.path.join(actual.get('config', 'OUTPUT_BASE'), 'stage')
    assert actual.get('config', 'STAGING_DIR') == expected_stage
    assert actual.get('user_env_vars', 'GODS_OF_WEATHER', 'Indra_Thor_Zeus') 
    
    
@pytest.mark.util
def test_pre_run_setup_env_vars():
    with mock.patch.dict('os.environ', {'MY_ENV_VAR': '42','OMP_NUM_THREADS': '4'}):
        conf_inputs = get_run_util_configs('run_util.conf')
        actual = ru.pre_run_setup(conf_inputs)
    assert actual.env['MY_ENV_VAR'] == '42'
    assert actual.get('config', 'OMP_NUM_THREADS') == '4'


@pytest.mark.util
def test_pre_run_setup_sed_file(capfd):
    conf_inputs = get_run_util_configs('sed_run_util.conf')
    
    with mock.patch.object(ru.sys, 'exit') as mock_sys:
        with mock.patch.object(ru, 'validate_config_variables', return_value=(False, ['sed command 1', 'sed command 2'])):
            actual = ru.pre_run_setup(conf_inputs)
            mock_sys.assert_called_with(1)
    
    # check sed file is written correctly
    sed_file = os.path.join(actual.getdir('OUTPUT_BASE'), 'sed_commands.txt')
    assert os.path.exists(sed_file)
    with open(sed_file, 'r') as f:
        assert f.read() == 'sed command 1\nsed command 2\n'
    
    # check correct errors logged
    out, err = capfd.readouterr()
    expected_error_msgs = [f'Find/Replace commands have been generated in {sed_file}',
                           'ERROR: Correct configuration variables and rerun. Exiting.']
    for msg in expected_error_msgs:
        assert msg in err 


@pytest.mark.util
def test_pre_run_setup_deprecated(capfd):
    conf_inputs = get_run_util_configs('sed_run_util.conf')
    
    with mock.patch.object(ru.sys, 'exit') as mock_sys:
        actual = ru.pre_run_setup(conf_inputs)
        mock_sys.assert_called_with(1)
    
    out, err = capfd.readouterr()

    expected_error_msgs = [
        'ERROR: DEPRECATED CONFIG ITEMS WERE FOUND. PLEASE FOLLOW THE INSTRUCTIONS TO UPDATE THE CONFIG FILES',
        'ERROR: ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON should be removed',
        'ERROR: ENSEMBLE_STAT_NBRHD_PROB_WIDTH should be removed',
                          ]
    for msg in expected_error_msgs:
        assert msg in err 

@pytest.mark.util
def test_pre_run_setup_no_install(capfd):
    conf_inputs = get_run_util_configs('no_install_run_util.conf')
    
    with mock.patch.object(ru.sys, 'exit') as mock_sys:
        actual = ru.pre_run_setup(conf_inputs)
        mock_sys.assert_called_with(1)
    
    out, err = capfd.readouterr()
    assert 'MET_INSTALL_DIR must be set correctly to run METplus' in err 
