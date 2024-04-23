import pytest
from unittest import mock

import os
import re

import produtil
import metplus.util.run_util as ru
import metplus.util.wrapper_init as wi
from metplus.wrappers.ensemble_stat_wrapper import EnsembleStatWrapper
from metplus.wrappers.grid_stat_wrapper import GridStatWrapper


EXPECTED_CONFIG_KEYS = [
    'CLOCK_TIME',
    'MET_INSTALL_DIR',
    'MET_BIN_DIR',
    'INPUT_BASE',
    'OUTPUT_BASE',
    'METPLUS_CONF',
    'TMP_DIR',
    'STAGING_DIR',
    'FILE_LISTS_DIR',
    'CONVERT',
    'GEMPAKTOCF_JAR',
    'GFDL_TRACKER_EXEC',
    'PROCESS_LIST',
    'OMP_NUM_THREADS',
    'SCRUB_STAGING_DIR',
    'LOG_METPLUS',
    'LOG_DIR',
    'LOG_TIMESTAMP_TEMPLATE',
    'LOG_TIMESTAMP_USE_DATATIME',
    'LOG_MET_OUTPUT_TO_METPLUS',
    'LOG_LEVEL',
    'LOG_LEVEL_TERMINAL',
    'LOG_MET_VERBOSITY',
    'LOG_LINE_FORMAT',
    'LOG_ERR_LINE_FORMAT',
    'LOG_DEBUG_LINE_FORMAT',
    'LOG_INFO_LINE_FORMAT',
    'LOG_LINE_DATE_FORMAT',
    'DO_NOT_RUN_EXE',
    'CONFIG_INPUT',
    'RUN_ID',
    'LOG_TIMESTAMP',
    'LOG_TO_TERMINAL_ONLY',
    'METPLUS_BASE',
    'PARM_BASE',
    'METPLUS_VERSION',
    'ALLOW_MISSING_INPUTS',
    'INPUT_THRESH',
]


def get_run_util_configs(conf_name):
    script_dir = os.path.dirname(__file__)
    return [os.path.join(script_dir, conf_name)]


def get_config_from_file(conf_file='run_util.conf'):
    """
    Make a config object from .conf file.
    Similar to fixture 'metplus_config', but calling that fixture
    interfers with how output is written. Use this instead when
    invoking pytest fixture 'capfd'.
    """
    conf_inputs = get_run_util_configs(conf_file)
    return ru.pre_run_setup(conf_inputs)

@pytest.mark.parametrize(
    "log_met_to_metplus,copyable_env",
    [
        (False, 'some text'),
        (False, ''),
        (True, 'some text'),
        (True, ''),
    ],
)
@pytest.mark.util
def test_log_header_info(tmp_path_factory, log_met_to_metplus, copyable_env):
    fake_log = tmp_path_factory.mktemp("data") / 'fake.log'
    cmd = '/my/cmd'
    ru._log_header_info(fake_log, copyable_env=copyable_env, cmd=cmd, log_met_to_metplus=log_met_to_metplus)
    with open(fake_log, 'r') as file_handle:
        file_content = file_handle.read()

    assert 'OUTPUT:' in file_content
    if not log_met_to_metplus:
        assert "COMMAND" in file_content
        assert cmd in file_content
        if copyable_env:
            assert copyable_env in file_content


@pytest.mark.parametrize(
    "cmd,skip_run,use_log_path,expected_to_fail",
    [
        (None, False, True, False),  # no command
        ('/my/cmd some args', True, True, False),  # skip run
        ('echo hello', False, True, False),  # simple command with log
        ('echo hello', False, False, False),  # simple command no log
        ('echo hello; echo hi', False, True, False),  # complex 2 commands with log
        ('echo hello; echo hi', False, False, False),  # complex 2 commands no log
        ('ls *', False, False, False),  # complex command with wildcard *
        ('ls fake_dir', False, False, True),  # failed command
    ],
)
@pytest.mark.util
def test_run_cmd(tmp_path_factory, cmd, skip_run, use_log_path, expected_to_fail):
    log_path = str(tmp_path_factory.mktemp("data") / 'fake_run_cmd.log') if use_log_path else None
    run_arguments = ru.RunArgs(
        logger=None,
        log_path=log_path,
        skip_run=skip_run,
        log_met_to_metplus=True,
        env=os.environ,
        copyable_env='some text',
    )
    actual = ru.run_cmd(cmd, run_arguments)
    assert bool(actual) == expected_to_fail

@pytest.mark.util
def test_pre_run_setup():
    actual = get_config_from_file()

    # check all config keys are set correctly
    assert sorted(actual.keys('config')) == sorted(EXPECTED_CONFIG_KEYS)

    # spot check a few specific items
    expected_stage = os.path.join(actual.get('config', 'OUTPUT_BASE'), 'stage')
    assert actual.get('config', 'STAGING_DIR') == expected_stage
    assert actual.get('user_env_vars', 'GODS_OF_WEATHER') == 'Indra_Thor_Zeus'


@pytest.mark.util
def test_pre_run_setup_env_vars():
    with mock.patch.dict('os.environ', {'MY_ENV_VAR': '42', 'OMP_NUM_THREADS': '4'}):
        conf_inputs = get_run_util_configs('run_util.conf')
        actual = ru.pre_run_setup(conf_inputs)
    assert actual.env['MY_ENV_VAR'] == '42'
    assert actual.get('config', 'OMP_NUM_THREADS') == '4'


@pytest.mark.util
def test_pre_run_setup_sed_file(capfd):
    with mock.patch.object(
        ru,
        'validate_config_variables',
        return_value=(False, ['sed command 1', 'sed command 2']),
    ):
        actual = get_config_from_file('sed_run_util.conf')
        assert actual is None

    # check sed file is written correctly
    out, err = capfd.readouterr()
    sed_err_regex = r'.*Find/Replace commands have been generated in (.*)\n'
    sed_file = None
    match = re.match(sed_err_regex, err)
    if match:
        sed_file = match.group(1)

    assert os.path.exists(sed_file)
    with open(sed_file, 'r') as f:
        assert f.read() == 'sed command 1\nsed command 2\n'

    # check correct errors logged
    expected_error_msgs = [
        f'Find/Replace commands have been generated in {sed_file}',
        'ERROR: Correct configuration variables and rerun. Exiting.',
    ]
    for msg in expected_error_msgs:
        assert msg in err


@pytest.mark.util
def test_pre_run_setup_deprecated(capfd):
    actual = get_config_from_file('sed_run_util.conf')
    assert actual is None

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
    actual = get_config_from_file('no_install_run_util.conf')
    assert actual is None

    out, err = capfd.readouterr()
    assert 'MET_INSTALL_DIR must be set correctly to run METplus' in err


@pytest.mark.util
def test_run_metplus_usage(metplus_config, capfd):
    config = metplus_config
    # Ensure any instance of 'Usage' suppresses other processes.
    config.set('config', 'PROCESS_LIST', 'GridStat,Usage')
    actual = ru.run_metplus(config)
    assert actual == 0
    out, err = capfd.readouterr()
    assert "USAGE: This text is displayed when [config] PROCESS_LIST = Usage." in out


@pytest.mark.parametrize(
    "config_dict,expected,check_err",
    [
        (
            # Check init errors raised
            {'PROCESS_LIST': 'GridStat, PCPCombine'},
            4,
            [
                'Must set either FCST_PCP_COMBINE_RUN or OBS_PCP_COMBINE_RUN',
                'OBS_GRID_STAT_INPUT_TEMPLATE required to run',
            ],
        ),
        (
            # Check correct config runs without error
            {
                'PROCESS_LIST': 'GridStat',
                'LOOP_BY': 'INIT',
                'INIT_TIME_FMT': '%Y%m%d%H',
                'INIT_BEG': '2005080700',
                'INIT_END': '2005080700',
                'INIT_INCREMENT': '12H',
                'FCST_GRID_STAT_INPUT_DIR': '{INPUT_BASE}/met_test/data/sample_fcst',
                'FCST_GRID_STAT_INPUT_TEMPLATE': '{init?fmt=%Y%m%d%H}/wrfprs_ruc13_{lead?fmt=%HH}.tm00_G212',
                'OBS_GRID_STAT_INPUT_DIR': '{INPUT_BASE}/met_test/new',
                'OBS_GRID_STAT_INPUT_TEMPLATE': 'ST2ml{valid?fmt=%Y%m%d%H}_A03h.nc',
                'GRID_STAT_OUTPUT_DIR': '{OUTPUT_BASE}/met_tool_wrapper/GridStat/GridStat',
                'GRID_STAT_OUTPUT_TEMPLATE': '{init?fmt=%Y%m%d%H}',
                'BOTH_VAR1_NAME': 'APCP',
                'BOTH_VAR1_LEVELS': 'A03',
                'BOTH_VAR1_THRESH': 'gt1, gt5',
                'INPUT_MUST_EXIST': 'False',
            },
            0,
            None,
        ),
        # More config examples can be added here.
    ],
)
@pytest.mark.util
def test_run_metplus(capfd, config_dict, expected, check_err):
    config = get_config_from_file()
    for k, v in config_dict.items():
        config.set('config', k, v)

    actual = ru.run_metplus(config)
    assert actual == expected

    out, err = capfd.readouterr()
    if check_err:
        for msg in check_err:
            assert msg in err
    else:
        assert err == ''


@pytest.mark.parametrize(
    "side_effect,return_value,check_err",
    [
        (Exception, None, "Fatal error occurred"),
        (None, [], ''),
    ],
)
@pytest.mark.util
def test_run_metplus_errors(capfd, side_effect, return_value, check_err):
    with mock.patch.object(
        ru, '_load_all_wrappers', side_effect=side_effect, return_value=return_value
    ):
        config = get_config_from_file()
        config.set('config', 'PROCESS_LIST', 'GridStat')
        actual = ru.run_metplus(config)
        assert actual == 1
        out, err = capfd.readouterr()
        if check_err:
            assert "Fatal error occurred" in err
        else:
            assert err == check_err 


@pytest.mark.util
def test_get_wrapper_instance(metplus_config):
    actual = wi.get_wrapper_instance(metplus_config, 'EnsembleStat', instance=2)
    assert isinstance(actual, EnsembleStatWrapper)
    assert actual.instance == 2


@pytest.mark.parametrize(
    'side_effect,check_err',
    [
        (AttributeError, 'There was a problem loading EnsembleStat wrapper'),
        (ModuleNotFoundError, 'Could not load EnsembleStat wrapper. '),
    ],
)
@pytest.mark.util
def test_get_wrapper_instance_raises(capfd, side_effect, check_err):
    config = get_config_from_file()
    with mock.patch.object(wi, 'import_module', side_effect=side_effect):
        actual = wi.get_wrapper_instance(config, 'EnsembleStat')
    assert actual == None
    out, err = capfd.readouterr()
    assert check_err in err


@pytest.mark.util
def test__load_all_wrappers(metplus_config):
    process_list = [('EnsembleStat', 1), ('GridStat', None)]
    actual = ru._load_all_wrappers(metplus_config, process_list)
    assert len(actual) == 2

    assert isinstance(actual[0], EnsembleStatWrapper)
    assert actual[0].instance == 1

    assert isinstance(actual[1], GridStatWrapper)
    assert actual[1].instance == None

    process_list.append(('FakeTool', 1))
    actual = ru._load_all_wrappers(metplus_config, process_list)
    assert actual == None


@pytest.mark.parametrize(
    'isOK_1, isOK_2, expected, reset_error',
    [
        (True, True, 0, False),
        (False, True, 2, False),
        (True, False, 3, False),
        (False, False, 5, False),
        (False, False, 1, True),
        (True, True, 0, True),
    ],
)
@pytest.mark.util
def test__check_wrapper_init_errors(
    metplus_config, isOK_1, isOK_2, expected, reset_error
):
    process_list = [('EnsembleStat', 1), ('GridStat', None)]
    processes = ru._load_all_wrappers(metplus_config, process_list)

    processes[0].isOK = isOK_1
    processes[1].isOK = isOK_2

    if reset_error:
        processes[0].errors = 0
        processes[1].errors = 0

    actual = ru._check_wrapper_init_errors(processes, mock.MagicMock())
    assert actual == expected


@pytest.mark.parametrize(
    'errors_1, errors_2, msgs, use_logger',
    [
        (0, 0, [], True),
        (1, 0, ['EnsembleStat had 1 error.'], True),
        (54, 1, ['EnsembleStat had 54 errors.', 'GridStat had 1 error.'], True),
        (54, 1, ['This is not called'], False),
    ],
)
@pytest.mark.util
def test__check_wrapper_run_errors(
    metplus_config, errors_1, errors_2, msgs, use_logger
):
    process_list = [('EnsembleStat', None), ('GridStat', None)]
    processes = ru._load_all_wrappers(metplus_config, process_list)

    processes[0].errors = errors_1
    processes[1].errors = errors_2

    # Make a mock logger
    mock_logger = mock.MagicMock()
    if not use_logger:
        mock_logger.__bool__.return_value = False

    actual = ru._check_wrapper_run_errors(processes, mock_logger)
    assert actual == errors_1 + errors_2

    if use_logger:
        mock_logger.error.assert_has_calls([mock.call(m) for m in msgs])
    else:
        mock_logger.error.assert_not_called()


@pytest.fixture
def post_run_config(metplus_config):
    config = metplus_config
    mock_logger = mock.MagicMock()
    config.logger = mock_logger
    return config


def _check_log_info(config, args, not_in=False):
    call = mock.call(*args)
    if not_in:
        assert call not in config.logger.info.call_args_list
    else:
        assert call in config.logger.info.call_args_list


@pytest.mark.util
def test_post_run_cleanup_scrubs(post_run_config):
    post_run_config.set('config', 'SCRUB_STAGING_DIR', True)
    post_run_config.set('config', 'STAGING_DIR', '/some/fake/dir')

    with mock.patch.object(ru.shutil, 'rmtree') as mock_rm:
        with mock.patch.object(ru.os.path, 'exists', return_value=True):
            ru.post_run_cleanup(post_run_config, 'fake_app', 0)

    assert mock_rm.called_once_with('/some/fake/dir')

    _check_log_info(post_run_config, ['Scrubbing staging dir: %s', '/some/fake/dir'])
    _check_log_info(
        post_run_config,
        ['Set SCRUB_STAGING_DIR to False to preserve intermediate files.'],
    )


@pytest.mark.util
def test_post_run_cleanup_no_errors(post_run_config):
    post_run_config.set('config', 'SCRUB_STAGING_DIR', False)
    expected_msgs = [
        'fake_app has successfully finished running as user Allan H. Murphy.',
        'Check the log file for more information: /log/file.log',
    ]

    with mock.patch.object(
        ru, 'get_user_info', return_value='Allan H. Murphy'
    ) as mock_user:
        with mock.patch.object(ru, 'get_logfile_info', return_value='/log/file.log'):
            actual = ru.post_run_cleanup(post_run_config, 'fake_app', 0)

    assert actual is True
    for msg in expected_msgs:
        _check_log_info(post_run_config, [msg])

    _check_log_info(
        post_run_config,
        ['Set SCRUB_STAGING_DIR to False to preserve intermediate files.'],
        not_in=True,
    )


@pytest.mark.util
def test_post_run_cleanup_errors(post_run_config):
    err_msg = 'fake_app has finished running as user Allan H. Murphy but had 5 errors.'
    with mock.patch.object(
        ru, 'get_user_info', return_value='Allan H. Murphy'
    ) as mock_user:
        with mock.patch.object(ru, 'get_logfile_info', return_value='/log/file.log'):
            actual = ru.post_run_cleanup(post_run_config, 'fake_app', 5)

    assert actual is False
    _check_log_info(
        post_run_config, ['Check the log file for more information: /log/file.log']
    )
    assert mock.call(err_msg) in post_run_config.logger.error.call_args_list
