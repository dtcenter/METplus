#!/usr/bin/env python3

import pytest

import os
from datetime import datetime

from metplus.wrappers.tc_pairs_wrapper import TCPairsWrapper

bdeck_template = 'b{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}'
adeck_template = 'a{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}'
edeck_template = 'e{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}'

output_template = '{basin?fmt=%s}q{date?fmt=%Y%m%d%H}.gfso.{cyclone?fmt=%s}'

time_fmt = '%Y%m%d%H'
run_times = ['2014121318']


def get_data_dir(config):
    return os.path.join(config.getdir('METPLUS_BASE'),
                        'internal', 'tests', 'data', 'tc_pairs')


def set_minimum_config_settings(config, loop_by='INIT'):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCPairs')
    config.set('config', 'LOOP_BY', loop_by)
    config.set('config', f'{loop_by}_TIME_FMT', time_fmt)
    config.set('config', f'{loop_by}_BEG', run_times[0])
    config.set('config', f'{loop_by}_END', run_times[-1])
    config.set('config', f'{loop_by}_INCREMENT', '12H')
    config.set('config', 'TC_PAIRS_CONFIG_FILE',
               '{PARM_BASE}/met_config/TCPairsConfig_wrapped')
    config.set('config', 'TC_PAIRS_BDECK_TEMPLATE', bdeck_template)

    config.set('config', 'TC_PAIRS_OUTPUT_DIR',
               '{OUTPUT_BASE}/TCPairs/output')
    config.set('config', 'TC_PAIRS_OUTPUT_TEMPLATE', output_template)

    config.set('config', 'TC_PAIRS_READ_ALL_FILES', False)

    # can set adeck or edeck variables
    config.set('config', 'TC_PAIRS_ADECK_TEMPLATE', adeck_template)


@pytest.mark.parametrize(
    'config_overrides, isOK', [
        ({}, True),
        ({'TC_PAIRS_BASIN': 'AL, ML'}, True),
        ({'TC_PAIRS_CYCLONE': '0104'}, True),
        ({'TC_PAIRS_BASIN': 'AL, ML',
          'TC_PAIRS_CYCLONE': '0104'}, True),
        ({'TC_PAIRS_STORM_ID': 'AL092011'}, True),
        ({'TC_PAIRS_STORM_ID': 'AL092011',
          'TC_PAIRS_BASIN': 'AL, ML'}, False),
        ({'TC_PAIRS_STORM_ID': 'AL092011',
          'TC_PAIRS_CYCLONE': '0104'}, False),
        ({'TC_PAIRS_STORM_ID': 'AL092011',
          'TC_PAIRS_BASIN': 'AL, ML',
          'TC_PAIRS_CYCLONE': '0104'}, False),
    ]
)
def test_read_storm_info(metplus_config, config_overrides, isOK):
    """! Check if error is thrown if storm_id and basin or cyclone are set """
    config = metplus_config
    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCPairsWrapper(config)
    assert wrapper.isOK == isOK

@pytest.mark.parametrize(
    'storm_id,basin,cyclone', [
        ('AL092011', 'al', '09'),
        ('ML072011', 'ml', '07'),
        ('ML072011', 'ml', '07'),
        # storm ID doesn't match format, so use wildcards
        ('L092011', 'wildcard', 'wildcard'),
        ('2020100700_F000_261N_1101W_FOF', 'wildcard', 'wildcard'),
    ]
)
@pytest.mark.wrapper
def test_parse_storm_id(metplus_config, storm_id, basin, cyclone):
    """! Check that storm ID is parsed properly to get basin and cyclone.
    Check that it returns wildcard expressions basin and cyclone cannot be
    parsed from storm ID
    """
    config = metplus_config

    set_minimum_config_settings(config)

    wrapper = TCPairsWrapper(config)

    actual_basin, actual_cyclone = wrapper._parse_storm_id(storm_id)

    # get wildcard expression if test input is 'wildcard'
    if basin == 'wildcard':
        expected_basin = wrapper.WILDCARDS['basin']
    else:
        expected_basin = basin

    if cyclone == 'wildcard':
        expected_cyclone = wrapper.WILDCARDS['cyclone']
    else:
        expected_cyclone = cyclone

    assert actual_basin == expected_basin
    assert actual_cyclone == expected_cyclone


@pytest.mark.parametrize(
    'basin,cyclone,expected_files,expected_wildcard', [
        ('al', '0104', ['get_bdeck_balq2014123118.gfso.0104'], False),
        ('ml', '0104', ['get_bdeck_bmlq2014123118.gfso.0104'], False),
        ('ml', '0105', ['get_bdeck_bmlq2014123118.gfso.0105'], False),
        ('al', '0105', [], False),
        ('??', '0104', ['get_bdeck_bmlq2014123118.gfso.0104',
                        'get_bdeck_balq2014123118.gfso.0104'], True),
        ('al', '*', ['get_bdeck_balq2014123118.gfso.0104'], True),
        ('ml', '*', ['get_bdeck_bmlq2014123118.gfso.0104',
                     'get_bdeck_bmlq2014123118.gfso.0105'], True),
        ('??', '*', ['get_bdeck_balq2014123118.gfso.0104',
                     'get_bdeck_bmlq2014123118.gfso.0104',
                     'get_bdeck_bmlq2014123118.gfso.0105'], True),
    ]
)
@pytest.mark.wrapper
def test_get_bdeck(metplus_config, basin, cyclone, expected_files,
                   expected_wildcard):
    """! Checks that the correct list of empty test files are found and the
    correct boolean to signify if wildcards were used for different
    combinations of basin/cyclone inputs
    """
    time_info = {'date': datetime(2014, 12, 31, 18)}
    config = metplus_config

    set_minimum_config_settings(config)

    test_data_dir = get_data_dir(config)
    bdeck_dir = os.path.join(test_data_dir, 'bdeck')
    config.set('config', 'TC_PAIRS_BDECK_INPUT_DIR', bdeck_dir)

    get_bdeck_template = (
        'get_bdeck_b{basin?fmt=%s}q{date?fmt=%Y%m%d%H}.gfso.{cyclone?fmt=%s}'
    )
    config.set('config', 'TC_PAIRS_BDECK_TEMPLATE',
               get_bdeck_template)

    wrapper = TCPairsWrapper(config)
    actual_files, actual_wildcard = wrapper._get_bdeck(basin, cyclone,
                                                       time_info)
    assert actual_wildcard == expected_wildcard
    assert len(actual_files) == len(expected_files)
    for actual_file, expected_file in zip(sorted(actual_files),
                                          sorted(expected_files)):
        assert os.path.basename(actual_file) == expected_file


@pytest.mark.parametrize(
    'template, filename,other_basin,other_cyclone', [
        ('b{basin?fmt=%s}{cyclone?fmt=%s}{date?fmt=%Y}.dat',
         'bal10092014.dat', None, None),
        ('{date?fmt=%Y%m}/b{basin?fmt=%s}q{date?fmt=%Y%m}*.gfso.{cyclone?fmt=%s}',
         '201412/balq2014123118.gfso.1009', None, None),
        ('{cyclone?fmt=%s}_b{basin?fmt=%s}_{date?fmt=%Y}.dat',
         '1009_bal_2014.dat', None, None),
        ('{cyclone?fmt=%s}_b{basin?fmt=%s}_{date?fmt=%Y}.dat',
         '009_bal_2014.dat', None, '009'),
        ('{cyclone?fmt=%s}_b{basin?fmt=%s}_{date?fmt=%Y}.dat',
         '09_bal_2014.dat', None, '09'),
        ('b{basin?fmt=%s}{date?fmt=%Y}{cyclone?fmt=%s}.dat',
         'bal20141009.dat', None, None),
        ('{cyclone?fmt=%s}{date?fmt=%Y}b{basin?fmt=%s}.dat',
         '10092014bal.dat', None, None),
        ('{date?fmt=%Y}{cyclone?fmt=%s}b{basin?fmt=%s}.dat',
         '20141009bal.dat', None, None),
        ('{date?fmt=%Y}{cyclone?fmt=%s}b{basin?fmt=%s}.dat',
         '20141009bml.dat', 'ml', None),
    ]
)
@pytest.mark.wrapper
def test_get_basin_cyclone_from_bdeck(metplus_config, template, filename,
                                      other_cyclone, other_basin):
    fake_dir = '/fake/dir'
    expected_basin = other_basin if other_basin else 'al'
    expected_cyclone = other_cyclone if other_cyclone else '1009'
    time_info = {'date': datetime(2014, 12, 31, 18)}
    config = metplus_config

    set_minimum_config_settings(config)
    wrapper = TCPairsWrapper(config)
    wrapper.c_dict['BDECK_DIR'] = fake_dir
    wrapper.c_dict['BDECK_TEMPLATE'] = template
    full_filename = os.path.join(fake_dir, filename)

    for wildcard_used in [True, False]:
        if wildcard_used:
            basin = wrapper.WILDCARDS['basin']
            cyclone = wrapper.WILDCARDS['cyclone']
        else:
            basin = expected_basin
            cyclone = expected_cyclone

        actual_basin, actual_cyclone = (
                wrapper._get_basin_cyclone_from_bdeck(full_filename,
                                                      wildcard_used,
                                                      basin,
                                                      cyclone,
                                                      time_info)
        )
        assert actual_basin == expected_basin
        assert actual_cyclone == expected_cyclone


@pytest.mark.parametrize(
    'config_overrides, storm_type, values_to_check', [
        # 0: storm_id
        ({'TC_PAIRS_STORM_ID': 'AL092019, ML102019'},
         'storm_id', ['AL092019', 'ML102019']),
        # 1: basin
        ({'TC_PAIRS_BASIN': 'AL, ML'},
         'basin', ['AL', 'AL', 'ML', 'ML']),
        # 2: cyclone
        ({'TC_PAIRS_CYCLONE': '09, 10'},
         'cyclone', ['09', '09', '10', '10']),
        # 3: both, check basin
        ({'TC_PAIRS_BASIN': 'AL, ML',
          'TC_PAIRS_CYCLONE': '09, 10'},
         'basin', ['AL', 'AL', 'ML', 'ML']),
        # 4: both, check cyclone - basin is outer loop, so alternate cyclones
        ({'TC_PAIRS_BASIN': 'AL, ML',
          'TC_PAIRS_CYCLONE': '09, 10'},
         'cyclone', ['09', '10', '09', '10']),
    ]
)
@pytest.mark.wrapper
def test_tc_pairs_storm_id_lists(metplus_config, config_overrides,
                                 storm_type, values_to_check):
    config = metplus_config

    set_minimum_config_settings(config)


    config.set('config', 'INIT_TIME_FMT', '%Y')
    config.set('config', 'INIT_BEG', '2019')
    config.set('config', 'INIT_END', '2019')

    test_data_dir = get_data_dir(config)
    bdeck_dir = os.path.join(test_data_dir, 'bdeck')
    edeck_dir = os.path.join(test_data_dir, 'edeck')

    config.set('config', 'TC_PAIRS_BDECK_INPUT_DIR', bdeck_dir)
    config.set('config', 'TC_PAIRS_EDECK_INPUT_DIR', edeck_dir)
    config.set('config', 'TC_PAIRS_BDECK_TEMPLATE',
               'storm_id_b{basin?fmt=%s}{cyclone?fmt=%s}{date?fmt=%Y}.dat')
    config.set('config', 'TC_PAIRS_EDECK_TEMPLATE',
               'storm_id_e{basin?fmt=%s}{cyclone?fmt=%s}{date?fmt=%Y}.dat')

    # LOOP_ORDER processes runs once, times runs once per time
    config.set('config', 'LOOP_ORDER', 'processes')

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCPairsWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS:")
    for idx, (cmd, env_list) in enumerate(all_cmds):
        print(f"CMD{idx}: {cmd}")
        print(f"ENV{idx}: {env_list}")

    assert len(all_cmds) == len(values_to_check)

    for (cmd, env_vars), value_to_check in zip(all_cmds, values_to_check):
        env_var_key = f'METPLUS_{storm_type.upper()}'

        match = next((item for item in env_vars if
                      item.startswith(env_var_key)), None)
        assert match is not None
        print(f"Checking env var: {env_var_key}")
        actual_value = match.split('=', 1)[1]
        expected_value = f'{storm_type} = ["{value_to_check}"];'

        assert actual_value == expected_value


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0: no config overrides that set env vars
        ({}, {}),
        # 1: description
        ({'TC_PAIRS_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),
        # 2: only basin that corresponds to existing test file is used
        ({'TC_PAIRS_BASIN': 'AL, ML'},
         {'METPLUS_BASIN': 'basin = ["ML"];'}),
        # 3: only cyclone that corresponds to existing test file is used
        ({'TC_PAIRS_CYCLONE': '1005, 0104'},
         {'METPLUS_CYCLONE': 'cyclone = ["0104"];'}),
        # 4: model list
        ({'MODEL': 'MOD1, MOD2'},
         {'METPLUS_MODEL': 'model = ["MOD1", "MOD2"];'}),
        # 5: init begin
        ({'TC_PAIRS_INIT_BEG': '20141031_14'},
         {'METPLUS_INIT_BEG': 'init_beg = "20141031_14";'}),
        # 6: init end
        ({'TC_PAIRS_INIT_END': '20151031_14'},
         {'METPLUS_INIT_END': 'init_end = "20151031_14";'}),
        # 7: dland file
        ({'TC_PAIRS_DLAND_FILE': 'my_dland.nc'},
         {'METPLUS_DLAND_FILE': 'dland_file = "my_dland.nc";'}),
        # 8: init_exc
        ({'TC_PAIRS_INIT_EXCLUDE': '20141031_14'},
         {'METPLUS_INIT_EXC': 'init_exc = ["20141031_14"];'}),
        # 9: init_inc
        ({'TC_PAIRS_INIT_INCLUDE': '20141031_14'},
         {'METPLUS_INIT_INC': 'init_inc = ["20141031_14"];'}),
        # 10: storm name
        ({'TC_PAIRS_STORM_NAME': 'KATRINA, OTHER'},
         {'METPLUS_STORM_NAME': 'storm_name = ["KATRINA", "OTHER"];'}),
        # 11: valid begin
        ({'TC_PAIRS_VALID_BEG': '20141031_14'},
         {'METPLUS_VALID_BEG': 'valid_beg = "20141031_14";'}),
        # 12: valid end
        ({'TC_PAIRS_VALID_END': '20141031_14'},
         {'METPLUS_VALID_END': 'valid_end = "20141031_14";'}),
        # 13: consensus 1 dictionary
        ({'TC_PAIRS_CONSENSUS1_NAME': 'name1',
          'TC_PAIRS_CONSENSUS1_MEMBERS': 'member1a, member1b',
          'TC_PAIRS_CONSENSUS1_REQUIRED': 'true, false',
          'TC_PAIRS_CONSENSUS1_MIN_REQ': '1'},
         {'METPLUS_CONSENSUS_LIST': (
        'consensus = [{name = "name1";members = ["member1a", "member1b"];'
        'required = [true, false];min_req = 1;}];'
         )}),
        # 14: consensus 2 dictionaries
        ({'TC_PAIRS_CONSENSUS1_NAME': 'name1',
          'TC_PAIRS_CONSENSUS1_MEMBERS': 'member1a, member1b',
          'TC_PAIRS_CONSENSUS1_REQUIRED': 'true, false',
          'TC_PAIRS_CONSENSUS1_MIN_REQ': '1',
          'TC_PAIRS_CONSENSUS2_NAME': 'name2',
          'TC_PAIRS_CONSENSUS2_MEMBERS': 'member2a, member2b',
          'TC_PAIRS_CONSENSUS2_REQUIRED': 'false, true',
          'TC_PAIRS_CONSENSUS2_MIN_REQ': '2'
          },
         {'METPLUS_CONSENSUS_LIST': (
                 'consensus = ['
                 '{name = "name1";members = ["member1a", "member1b"];'
                 'required = [true, false];min_req = 1;}'
                 '{name = "name2";members = ["member2a", "member2b"];'
                 'required = [false, true];min_req = 2;}];'
         )}),
        # 15: valid_exc
        ({'TC_PAIRS_VALID_EXCLUDE': '20141031_14'},
         {'METPLUS_VALID_EXC': 'valid_exc = ["20141031_14"];'}),
        # 16: valid_inc
        ({'TC_PAIRS_VALID_INCLUDE': '20141031_14'},
         {'METPLUS_VALID_INC': 'valid_inc = ["20141031_14"];'}),
        # 17: write_valid
        ({'TC_PAIRS_WRITE_VALID': '20141031_14'},
         {'METPLUS_WRITE_VALID': 'write_valid = ["20141031_14"];'}),
        # 18: check_dup
        ({'TC_PAIRS_CHECK_DUP': 'False', },
         {'METPLUS_CHECK_DUP': 'check_dup = FALSE;'}),
        # 19: interp12
        ({'TC_PAIRS_INTERP12': 'replace', },
         {'METPLUS_INTERP12': 'interp12 = REPLACE;'}),
        # 20 match_points
        ({'TC_PAIRS_MATCH_POINTS': 'False', },
         {'METPLUS_MATCH_POINTS': 'match_points = FALSE;'}),

    ]
)
@pytest.mark.wrapper
def test_tc_pairs_loop_order_processes(metplus_config, config_overrides,
                                       env_var_values):
    my_config = metplus_config
    # run using init and valid time variables
    for loop_by in ['INIT', 'VALID']:
        remove_beg = remove_end = remove_match_points = False
        #config = metplus_config_files([])
        config = my_config.copy()

        set_minimum_config_settings(config, loop_by)

        test_data_dir = get_data_dir(config)
        bdeck_dir = os.path.join(test_data_dir, 'bdeck')
        adeck_dir = os.path.join(test_data_dir, 'adeck')

        config.set('config', 'TC_PAIRS_BDECK_INPUT_DIR', bdeck_dir)
        config.set('config', 'TC_PAIRS_ADECK_INPUT_DIR', adeck_dir)

        # LOOP_ORDER processes runs once, times runs once per time
        config.set('config', 'LOOP_ORDER', 'processes')

        # set config variable overrides
        for key, value in config_overrides.items():
            config.set('config', key, value)

        if f'METPLUS_{loop_by}_BEG' not in env_var_values:
            env_var_values[f'METPLUS_{loop_by}_BEG'] = (
                f'{loop_by.lower()}_beg = "{run_times[0]}";'
            )
            remove_beg = True

        if f'METPLUS_{loop_by}_END' not in env_var_values:
            env_var_values[f'METPLUS_{loop_by}_END'] = (
                f'{loop_by.lower()}_end = "{run_times[-1]}";'
            )
            remove_end = True

        if f'METPLUS_MATCH_POINTS' not in env_var_values:
            env_var_values[f'METPLUS_MATCH_POINTS'] = (
                'match_points = TRUE;'
            )
            remove_match_points = True

        wrapper = TCPairsWrapper(config)
        assert wrapper.isOK

        app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
        verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
        config_file = wrapper.c_dict.get('CONFIG_FILE')
        out_dir = wrapper.c_dict.get('OUTPUT_DIR')
        expected_cmds = [(f"{app_path} {verbosity} "
                          f"-bdeck {bdeck_dir}/bmlq2014123118.gfso.0104 "
                          f"-adeck {adeck_dir}/amlq2014123118.gfso.0104 "
                          f"-config {config_file} "
                          f"-out {out_dir}/mlq2014121318.gfso.0104"),
                         ]

        all_cmds = wrapper.run_all_times()
        print(f"ALL COMMANDS: {all_cmds}")
        assert len(all_cmds) == len(expected_cmds)

        for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
            # ensure commands are generated as expected
            assert cmd == expected_cmd

            # check that environment variables were set properly
            for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS:
                match = next((item for item in env_vars if
                              item.startswith(env_var_key)), None)
                assert match is not None
                print(f'Checking env var: {env_var_key}')
                actual_value = match.split('=', 1)[1]
                assert env_var_values.get(env_var_key, '') == actual_value

        if remove_beg:
            del env_var_values[f'METPLUS_{loop_by}_BEG']
        if remove_end:
            del env_var_values[f'METPLUS_{loop_by}_END']
        if remove_match_points:
            del env_var_values['METPLUS_MATCH_POINTS']


@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0: no config overrides that set env vars
        ({}, {}),
        # 1: storm_id list
        ({'TC_PAIRS_STORM_ID': 'AL092014, ML082015'},
         {'METPLUS_STORM_ID': 'storm_id = ["AL092014", "ML082015"];'}),
        # 2: basin list
        ({'TC_PAIRS_BASIN': 'AL, ML'},
         {'METPLUS_BASIN': 'basin = ["AL", "ML"];'}),
        # 3: cyclone list
        ({'TC_PAIRS_CYCLONE': '1005, 0104'},
         {'METPLUS_CYCLONE': 'cyclone = ["1005", "0104"];'}),
    ]
)
@pytest.mark.wrapper
def test_tc_pairs_read_all_files(metplus_config_files, config_overrides,
                                 env_var_values):
    # run using init and valid time variables
    for loop_by in ['INIT', 'VALID']:
        config = metplus_config_files([])

        set_minimum_config_settings(config, loop_by)

        test_data_dir = get_data_dir(config)
        bdeck_dir = os.path.join(test_data_dir, 'bdeck')
        adeck_dir = os.path.join(test_data_dir, 'adeck')

        config.set('config', 'TC_PAIRS_BDECK_INPUT_DIR', bdeck_dir)
        config.set('config', 'TC_PAIRS_ADECK_INPUT_DIR', adeck_dir)

        # LOOP_ORDER processes runs once, times runs once per time
        config.set('config', 'LOOP_ORDER', 'processes')

        config.set('config', 'TC_PAIRS_READ_ALL_FILES', True)
        config.set('config', 'TC_PAIRS_OUTPUT_TEMPLATE', '')

        # set config variable overrides
        for key, value in config_overrides.items():
            config.set('config', key, value)

        env_var_values[f'METPLUS_{loop_by}_BEG'] = (
            f'{loop_by.lower()}_beg = "{run_times[0]}";'
        )

        env_var_values[f'METPLUS_{loop_by}_END'] = (
            f'{loop_by.lower()}_end = "{run_times[-1]}";'
        )

        env_var_values['METPLUS_MATCH_POINTS'] = (
            'match_points = TRUE;'
        )

        wrapper = TCPairsWrapper(config)
        assert wrapper.isOK

        app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
        verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
        config_file = wrapper.c_dict.get('CONFIG_FILE')
        out_dir = wrapper.c_dict.get('OUTPUT_DIR')
        expected_cmds = [(f"{app_path} {verbosity} "
                          f"-bdeck {bdeck_dir} "
                          f"-adeck {adeck_dir} "
                          f"-config {config_file} "
                          f"-out {out_dir}/tc_pairs"),
                         ]

        all_cmds = wrapper.run_all_times()
        print(f"ALL COMMANDS: {all_cmds}")
        assert len(all_cmds) == len(expected_cmds)

        for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
            # check that environment variables were set properly
            for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS:
                match = next((item for item in env_vars if
                              item.startswith(env_var_key)), None)
                assert match is not None
                print(f'Checking env var: {env_var_key}')
                actual_value = match.split('=', 1)[1]
                assert env_var_values.get(env_var_key, '') == actual_value

        # unset begin and end for next loop
        del env_var_values[f'METPLUS_{loop_by}_BEG']
        del env_var_values[f'METPLUS_{loop_by}_END']


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config
    config.set('config', 'INIT_TIME_FMT', time_fmt)
    config.set('config', 'INIT_BEG', run_times[0])
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'TCPairsConfig_wrapped')

    wrapper = TCPairsWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'TC_PAIRS_CONFIG_FILE', fake_config_name)
    wrapper = TCPairsWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
