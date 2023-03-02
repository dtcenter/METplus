#!/usr/bin/env python3

import pytest

import pprint
import os
from datetime import datetime

from metplus.util import config_metplus
from metplus.util.time_util import ti_calculate
from metplus.util.config_validate import validate_config_variables

@pytest.mark.util
def test_get_default_config_list():
    test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir,
                                                 os.pardir,
                                                 os.pardir,
                                                 'data',
                                                 'config_metplus'))
    old_parm_base = os.path.join(test_data_dir, 'old')
    new_parm_base = os.path.join(test_data_dir, 'new')
    both_parm_base = os.path.join(test_data_dir, 'both')

    old_list = ['metplus_config/metplus_system.conf',
                'metplus_config/metplus_data.conf',
                'metplus_config/metplus_runtime.conf',
                'metplus_config/metplus_logging.conf']
    new_list = ['metplus_config/defaults.conf']

    # old conf files should be parsed before new if both are found
    both_list = old_list + new_list

    expected_old = [os.path.join(old_parm_base, item) for item in old_list]
    expected_new = [os.path.join(new_parm_base, item) for item in new_list]
    expected_both = [os.path.join(both_parm_base, item) for item in both_list]

    actual_old = config_metplus._get_default_config_list(old_parm_base)
    actual_new = config_metplus._get_default_config_list(new_parm_base)
    actual_both = config_metplus._get_default_config_list(both_parm_base)
    assert actual_old == expected_old
    assert actual_new == expected_new
    assert actual_both == expected_both


@pytest.mark.parametrize(
    'regex,index,id,expected_result', [
        # 0: No ID
        (r'^FCST_VAR(\d+)_NAME$', 1, None,
         {'1': [None],
          '2': [None],
          '4': [None]}),
        # 1: ID and index 2
        (r'(\w+)_VAR(\d+)_NAME', 2, 1,
         {'1': ['FCST'],
          '2': ['FCST'],
          '4': ['FCST']}),
        # 2: index 1, ID 2, multiple identifiers
        (r'^FCST_VAR(\d+)_(\w+)$', 1, 2,
         {'1': ['NAME', 'LEVELS'],
          '2': ['NAME'],
          '4': ['NAME']}),
        # 3: command that StatAnalysis wrapper uses
        (r'MODEL(\d+)$', 1, None,
         {'1': [None],
          '2': [None],}),
        # 4: TCPairs conensus logic
        (r'^TC_PAIRS_CONSENSUS(\d+)_(\w+)$', 1, 2,
         {'1': ['NAME', 'MEMBERS', 'REQUIRED', 'MIN_REQ'],
          '2': ['NAME', 'MEMBERS', 'REQUIRED', 'MIN_REQ']}),
    ]
)
@pytest.mark.util
def test_find_indices_in_config_section(metplus_config, regex, index,
                                        id, expected_result):
    config = metplus_config
    config.set('config', 'FCST_VAR1_NAME', 'name1')
    config.set('config', 'FCST_VAR1_LEVELS', 'level1')
    config.set('config', 'FCST_VAR2_NAME', 'name2')
    config.set('config', 'FCST_VAR4_NAME', 'name4')
    config.set('config', 'MODEL1', 'model1')
    config.set('config', 'MODEL2', 'model2')

    config.set('config', 'TC_PAIRS_CONSENSUS1_NAME', 'name1')
    config.set('config', 'TC_PAIRS_CONSENSUS1_MEMBERS', 'member1')
    config.set('config', 'TC_PAIRS_CONSENSUS1_REQUIRED', 'True')
    config.set('config', 'TC_PAIRS_CONSENSUS1_MIN_REQ', '1')
    config.set('config', 'TC_PAIRS_CONSENSUS2_NAME', 'name2')
    config.set('config', 'TC_PAIRS_CONSENSUS2_MEMBERS', 'member2')
    config.set('config', 'TC_PAIRS_CONSENSUS2_REQUIRED', 'True')
    config.set('config', 'TC_PAIRS_CONSENSUS2_MIN_REQ', '2')

    indices = config_metplus.find_indices_in_config_section(regex, config,
                                                            index_index=index,
                                                            id_index=id)

    pp = pprint.PrettyPrinter()
    print(f'Indices:')
    pp.pprint(indices)

    assert indices == expected_result


@pytest.mark.parametrize(
    'config_var_name, expected_indices, set_met_tool', [
        ('FCST_GRID_STAT_VAR1_NAME', ['1'], True),
        ('FCST_GRID_STAT_VAR2_INPUT_FIELD_NAME', ['2'], True),
        ('FCST_GRID_STAT_VAR3_FIELD_NAME', ['3'], True),
        ('BOTH_GRID_STAT_VAR4_NAME', ['4'], True),
        ('BOTH_GRID_STAT_VAR5_INPUT_FIELD_NAME', ['5'], True),
        ('BOTH_GRID_STAT_VAR6_FIELD_NAME', ['6'], True),
        ('FCST_VAR7_NAME', ['7'], False),
        ('FCST_VAR8_INPUT_FIELD_NAME', ['8'], False),
        ('FCST_VAR9_FIELD_NAME', ['9'], False),
        ('BOTH_VAR10_NAME', ['10'], False),
        ('BOTH_VAR11_INPUT_FIELD_NAME', ['11'], False),
        ('BOTH_VAR12_FIELD_NAME', ['12'], False),
    ]
)
@pytest.mark.util
def test_find_var_indices_fcst(metplus_config,
                               config_var_name,
                               expected_indices,
                               set_met_tool):
    config = metplus_config
    data_types = ['FCST']
    config.set('config', config_var_name, "NAME1")
    met_tool = 'grid_stat' if set_met_tool else None
    var_name_indices = config_metplus._find_var_name_indices(config,
                                                             data_types=data_types,
                                                             met_tool=met_tool)

    assert len(var_name_indices) == len(expected_indices)
    for actual_index in var_name_indices:
        assert actual_index in expected_indices


@pytest.mark.parametrize(
    'data_type, met_tool, expected_out', [
        ('FCST', None, ['FCST_',
                        'BOTH_',]),
        ('OBS', None, ['OBS_',
                       'BOTH_',]),
        ('FCST', 'grid_stat', ['FCST_GRID_STAT_',
                               'BOTH_GRID_STAT_',
                               'FCST_',
                               'BOTH_',
                               ]),
        ('OBS', 'extract_tiles', ['OBS_EXTRACT_TILES_',
                                  'BOTH_EXTRACT_TILES_',
                                  'OBS_',
                                  'BOTH_',
                                  ]),
        ('ENS', None, ['ENS_']),
        ('DATA', None, ['DATA_']),
        ('DATA', 'tc_gen', ['DATA_TC_GEN_',
                            'DATA_']),

    ]
)
@pytest.mark.util
def test_get_field_search_prefixes(data_type, met_tool, expected_out):
    assert(config_metplus.get_field_search_prefixes(data_type,
                                                    met_tool) == expected_out)


# search prefixes are valid prefixes to append to field info variables
# config_overrides are a dict of config vars and their values
# search_key is the key of the field config item to check
# expected_value is the variable that search_key is set to
@pytest.mark.parametrize(
    'search_prefixes, config_overrides, expected_value', [
        (['BOTH_', 'FCST_'],
         {'FCST_VAR1_': 'fcst_var1'},
         'fcst_var1'
         ),
        (['BOTH_', 'FCST_'], {}, None),

        (['BOTH_', 'FCST_'],
         {'FCST_VAR1_': 'fcst_var1',
          'BOTH_VAR1_': 'both_var1'},
         'both_var1'
         ),

        (['BOTH_GRID_STAT_', 'FCST_GRID_STAT_'],
         {'FCST_GRID_STAT_VAR1_': 'fcst_grid_stat_var1'},
         'fcst_grid_stat_var1'
         ),
        (['BOTH_GRID_STAT_', 'FCST_GRID_STAT_'], {}, None),
        (['BOTH_GRID_STAT_', 'FCST_GRID_STAT_'],
         {'FCST_GRID_STAT_VAR1_': 'fcst_grid_stat_var1',
          'BOTH_GRID_STAT_VAR1_': 'both_grid_stat_var1'},
         'both_grid_stat_var1'
         ),

        (['ENS_'],
         {'ENS_VAR1_': 'env_var1'},
         'env_var1'
         ),
        (['ENS_'], {}, None),

    ]
)
@pytest.mark.util
def test_get_field_config_variables(metplus_config,
                                    search_prefixes,
                                    config_overrides,
                                    expected_value):
    config = metplus_config
    index = '1'
    field_info_types = ['name', 'levels', 'thresh', 'options', 'output_names']
    for field_info_type in field_info_types:
        for key, value in config_overrides.items():
            config.set('config',
                       f'{key}{field_info_type.upper()}',
                       value)

        field_configs = config_metplus.get_field_config_variables(config,
                                                        index,
                                                        search_prefixes)

        assert field_configs.get(field_info_type) == expected_value


@pytest.mark.parametrize(
    'config_keys, field_key, expected_value', [
        (['NAME',
          ],
         'name', 'NAME'
         ),
        (['NAME',
          'INPUT_FIELD_NAME',
          ],
         'name', 'NAME'
         ),
        (['INPUT_FIELD_NAME',
          ],
         'name', 'INPUT_FIELD_NAME'
         ),
        ([], 'name', None),
        (['LEVELS',
          ],
         'levels', 'LEVELS'
         ),
        (['LEVELS',
          'FIELD_LEVEL',
          ],
         'levels', 'LEVELS'
         ),
        (['FIELD_LEVEL',
          ],
         'levels', 'FIELD_LEVEL'
         ),
         ([], 'levels', None),
        (['OUTPUT_NAMES',
          ],
         'output_names', 'OUTPUT_NAMES'
         ),
        (['OUTPUT_NAMES',
          'OUTPUT_FIELD_NAME',
          ],
         'output_names', 'OUTPUT_NAMES'
         ),
        (['OUTPUT_FIELD_NAME',
          ],
         'output_names', 'OUTPUT_FIELD_NAME'
         ),
        ([], 'output_names', None),
    ]
)
@pytest.mark.util
def test_get_field_config_variables_synonyms(metplus_config,
                                             config_keys,
                                             field_key,
                                             expected_value):
    config = metplus_config
    index = '1'
    prefix = 'BOTH_REGRID_DATA_PLANE_'
    for key in config_keys:
        config.set('config', f'{prefix}VAR{index}_{key}', key)

    field_configs = config_metplus.get_field_config_variables(config,
                                                    index,
                                                    [prefix])

    assert field_configs.get(field_key) == expected_value


# field info only defined in the FCST_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, False),
        ('FCST', True),
        ('OBS', False),
    ]
)
@pytest.mark.util
def test_parse_var_list_fcst_only(metplus_config, data_type, list_created):
    conf = metplus_config
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "NAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because OBS variables are missing
    assert not validate_config_variables(conf)[0]

    var_list = config_metplus.parse_var_list(conf, time_info=None, data_type=data_type)

    # list will be created if requesting just OBS, but it should not be created if
    # nothing was requested because FCST values are missing
    if list_created:
        assert(var_list[0]['fcst_name'] == "NAME1" and
               var_list[1]['fcst_name'] == "NAME1" and
               var_list[2]['fcst_name'] == "NAME2" and
               var_list[3]['fcst_name'] == "NAME2" and
               var_list[0]['fcst_level'] == "LEVELS11" and
               var_list[1]['fcst_level'] == "LEVELS12" and
               var_list[2]['fcst_level'] == "LEVELS21" and
               var_list[3]['fcst_level'] == "LEVELS22")
    else:
        assert not var_list


# field info only defined in the OBS_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, False),
        ('OBS', True),
        ('FCST', False),
    ]
)
@pytest.mark.util
def test_parse_var_list_obs(metplus_config, data_type, list_created):
    conf = metplus_config
    conf.set('config', 'OBS_VAR1_NAME', "NAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "NAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because FCST variables are missing
    if validate_config_variables(conf)[0]:
        assert False

    var_list = config_metplus.parse_var_list(conf, time_info=None, data_type=data_type)

    # list will be created if requesting just OBS, but it should not be created if
    # nothing was requested because FCST values are missing
    if list_created:
        assert(var_list[0]['obs_name'] == "NAME1" and
               var_list[1]['obs_name'] == "NAME1" and
               var_list[2]['obs_name'] == "NAME2" and
               var_list[3]['obs_name'] == "NAME2" and
               var_list[0]['obs_level'] == "LEVELS11" and
               var_list[1]['obs_level'] == "LEVELS12" and
               var_list[2]['obs_level'] == "LEVELS21" and
               var_list[3]['obs_level'] == "LEVELS22")
    else:
        assert not var_list


# field info only defined in the BOTH_* variables
@pytest.mark.parametrize(
    'data_type, list_created', [
        (None, 'fcst:obs'),
        ('FCST', 'fcst'),
        ('OBS', 'obs'),
    ]
)
@pytest.mark.util
def test_parse_var_list_both(metplus_config, data_type, list_created):
    conf = metplus_config
    conf.set('config', 'BOTH_VAR1_NAME', "NAME1")
    conf.set('config', 'BOTH_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'BOTH_VAR2_NAME', "NAME2")
    conf.set('config', 'BOTH_VAR2_LEVELS', "LEVELS21, LEVELS22")

    # this should not occur because BOTH variables are used
    if not validate_config_variables(conf)[0]:
        assert False

    var_list = config_metplus.parse_var_list(conf, time_info=None, data_type=data_type)
    print(f'var_list:{var_list}')
    for list_to_check in list_created.split(':'):
        if (not var_list[0][f'{list_to_check}_name'] == "NAME1" or
                not var_list[1][f'{list_to_check}_name'] == "NAME1" or
                not var_list[2][f'{list_to_check}_name'] == "NAME2" or
                not var_list[3][f'{list_to_check}_name'] == "NAME2" or
                not var_list[0][f'{list_to_check}_level'] == "LEVELS11" or
                not var_list[1][f'{list_to_check}_level'] == "LEVELS12" or
                not var_list[2][f'{list_to_check}_level'] == "LEVELS21" or
                not var_list[3][f'{list_to_check}_level'] == "LEVELS22"):
            assert False


# field info defined in both FCST_* and OBS_* variables
@pytest.mark.util
def test_parse_var_list_fcst_and_obs(metplus_config):
    conf = metplus_config
    conf.set('config', 'FCST_VAR1_NAME', "FNAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "FLEVELS11, FLEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "FNAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "FLEVELS21, FLEVELS22")
    conf.set('config', 'OBS_VAR1_NAME', "ONAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "OLEVELS11, OLEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "ONAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "OLEVELS21, OLEVELS22")

    # this should not occur because FCST and OBS variables are found
    if not validate_config_variables(conf)[0]:
        assert False

    var_list = config_metplus.parse_var_list(conf)

    assert(var_list[0]['fcst_name'] == "FNAME1" and
           var_list[0]['obs_name'] == "ONAME1" and
           var_list[1]['fcst_name'] == "FNAME1" and
           var_list[1]['obs_name'] == "ONAME1" and
           var_list[2]['fcst_name'] == "FNAME2" and
           var_list[2]['obs_name'] == "ONAME2" and
           var_list[3]['fcst_name'] == "FNAME2" and
           var_list[3]['obs_name'] == "ONAME2" and
           var_list[0]['fcst_level'] == "FLEVELS11" and
           var_list[0]['obs_level'] == "OLEVELS11" and
           var_list[1]['fcst_level'] == "FLEVELS12" and
           var_list[1]['obs_level'] == "OLEVELS12" and
           var_list[2]['fcst_level'] == "FLEVELS21" and
           var_list[2]['obs_level'] == "OLEVELS21" and
           var_list[3]['fcst_level'] == "FLEVELS22" and
           var_list[3]['obs_level'] == "OLEVELS22")


# VAR1 defined by FCST, VAR2 defined by OBS
@pytest.mark.util
def test_parse_var_list_fcst_and_obs_alternate(metplus_config):
    conf = metplus_config
    conf.set('config', 'FCST_VAR1_NAME', "FNAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "FLEVELS11, FLEVELS12")
    conf.set('config', 'OBS_VAR2_NAME', "ONAME2")
    conf.set('config', 'OBS_VAR2_LEVELS', "OLEVELS21, OLEVELS22")

    # configuration is invalid and parse var list should not give any results
    assert(not validate_config_variables(conf)[0] and not config_metplus.parse_var_list(conf))


# VAR1 defined by OBS, VAR2 by FCST, VAR3 by both FCST AND OBS
@pytest.mark.parametrize(
    'data_type, list_len, name_levels', [
        (None, 0, None),
        ('FCST', 4, ('FNAME2:FLEVELS21','FNAME2:FLEVELS22','FNAME3:FLEVELS31','FNAME3:FLEVELS32')),
        ('OBS', 4, ('ONAME1:OLEVELS11','ONAME1:OLEVELS12','ONAME3:OLEVELS31','ONAME3:OLEVELS32')),
    ]
)
@pytest.mark.util
def test_parse_var_list_fcst_and_obs_and_both(metplus_config, data_type, list_len, name_levels):
    conf = metplus_config
    conf.set('config', 'OBS_VAR1_NAME', "ONAME1")
    conf.set('config', 'OBS_VAR1_LEVELS', "OLEVELS11, OLEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "FNAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "FLEVELS21, FLEVELS22")
    conf.set('config', 'FCST_VAR3_NAME', "FNAME3")
    conf.set('config', 'FCST_VAR3_LEVELS', "FLEVELS31, FLEVELS32")
    conf.set('config', 'OBS_VAR3_NAME', "ONAME3")
    conf.set('config', 'OBS_VAR3_LEVELS', "OLEVELS31, OLEVELS32")

    # configuration is invalid and parse var list should not give any results
    if validate_config_variables(conf)[0]:
        assert False

    var_list = config_metplus.parse_var_list(conf, time_info=None, data_type=data_type)

    if len(var_list) != list_len:
        assert False

    if data_type is None:
        assert len(var_list) == 0

    if name_levels is not None:
        dt_lower = data_type.lower()
        expected = []
        for name_level in name_levels:
            name, level = name_level.split(':')
            expected.append({f'{dt_lower}_name': name,
                             f'{dt_lower}_level': level})

        for expect, reality in zip(expected,var_list):
            if expect[f'{dt_lower}_name'] != reality[f'{dt_lower}_name']:
                assert False

            if expect[f'{dt_lower}_level'] != reality[f'{dt_lower}_level']:
                assert False

        assert True


# option defined in obs only
@pytest.mark.parametrize(
    'data_type, list_len', [
        (None, 0),
        ('FCST', 2),
        ('OBS', 0),
    ]
)
@pytest.mark.util
def test_parse_var_list_fcst_only_options(metplus_config, data_type, list_len):
    conf = metplus_config
    conf.set('config', 'FCST_VAR1_NAME', "NAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "LEVELS11, LEVELS12")
    conf.set('config', 'FCST_VAR1_THRESH', ">1, >2")
    conf.set('config', 'OBS_VAR1_OPTIONS', "OOPTIONS11")

    # this should not occur because OBS variables are missing
    if validate_config_variables(conf)[0]:
        assert False

    var_list = config_metplus.parse_var_list(conf, time_info=None, data_type=data_type)

    assert len(var_list) == list_len


@pytest.mark.parametrize(
    'met_tool, indices', [
        (None, {'1': ['FCST']}),
        ('GRID_STAT', {'2': ['FCST']}),
        ('ENSEMBLE_STAT', {}),
    ]
)
@pytest.mark.util
def test_find_var_indices_wrapper_specific(metplus_config, met_tool, indices):
    conf = metplus_config
    data_type = 'FCST'
    conf.set('config', f'{data_type}_VAR1_NAME', "NAME1")
    conf.set('config', f'{data_type}_GRID_STAT_VAR2_NAME', "GSNAME2")

    var_name_indices = config_metplus._find_var_name_indices(conf,data_types=[data_type],
                                                  met_tool=met_tool)

    assert var_name_indices == indices


# ensure that the field configuration used for
# met_tool_wrapper/EnsembleStat/EnsembleStat.conf
# works as expected
@pytest.mark.util
def test_parse_var_list_ensemble(metplus_config):
    config = metplus_config
    config.set('config', 'ENS_VAR1_NAME', 'APCP')
    config.set('config', 'ENS_VAR1_LEVELS', 'A24')
    config.set('config', 'ENS_VAR1_THRESH', '>0.0, >=10.0')
    config.set('config', 'ENS_VAR2_NAME', 'REFC')
    config.set('config', 'ENS_VAR2_LEVELS', 'L0')
    config.set('config', 'ENS_VAR2_THRESH', '>35.0')
    config.set('config', 'ENS_VAR2_OPTIONS', 'GRIB1_ptv = 129;')
    config.set('config', 'ENS_VAR3_NAME', 'UGRD')
    config.set('config', 'ENS_VAR3_LEVELS', 'Z10')
    config.set('config', 'ENS_VAR3_THRESH', '>=5.0')
    config.set('config', 'ENS_VAR4_NAME', 'VGRD')
    config.set('config', 'ENS_VAR4_LEVELS', 'Z10')
    config.set('config', 'ENS_VAR4_THRESH', '>=5.0')
    config.set('config', 'ENS_VAR5_NAME', 'WIND')
    config.set('config', 'ENS_VAR5_LEVELS', 'Z10')
    config.set('config', 'ENS_VAR5_THRESH', '>=5.0')
    config.set('config', 'FCST_VAR1_NAME', 'APCP')
    config.set('config', 'FCST_VAR1_LEVELS', 'A24')
    config.set('config', 'FCST_VAR1_THRESH', '>0.01, >=10.0')
    config.set('config', 'FCST_VAR1_OPTIONS', ('ens_ssvar_bin_size = 0.1; '
                                               'ens_phist_bin_size = 0.05;'))
    config.set('config', 'OBS_VAR1_NAME', 'APCP')
    config.set('config', 'OBS_VAR1_LEVELS', 'A24')
    config.set('config', 'OBS_VAR1_THRESH', '>0.01, >=10.0')
    config.set('config', 'OBS_VAR1_OPTIONS', ('ens_ssvar_bin_size = 0.1; '
                                              'ens_phist_bin_size = 0.05;'))
    time_info = {}

    expected_ens_list = [{'index': '1',
                          'ens_name': 'APCP',
                          'ens_level': 'A24',
                          'ens_thresh': ['>0.0', '>=10.0']},
                         {'index': '2',
                          'ens_name': 'REFC',
                          'ens_level': 'L0',
                          'ens_thresh': ['>35.0']},
                         {'index': '3',
                          'ens_name': 'UGRD',
                          'ens_level': 'Z10',
                          'ens_thresh': ['>=5.0']},
                         {'index': '4',
                          'ens_name': 'VGRD',
                          'ens_level': 'Z10',
                          'ens_thresh': ['>=5.0']},
                         {'index': '5',
                          'ens_name': 'WIND',
                          'ens_level': 'Z10',
                          'ens_thresh': ['>=5.0']},
                        ]
    expected_var_list = [{'index': '1',
                          'fcst_name': 'APCP',
                          'fcst_level': 'A24',
                          'fcst_thresh': ['>0.01', '>=10.0'],
                          'fcst_extra': ('ens_ssvar_bin_size = 0.1; '
                                         'ens_phist_bin_size = 0.05;'),
                          'obs_name': 'APCP',
                          'obs_level': 'A24',
                          'obs_thresh': ['>0.01', '>=10.0'],
                          'obs_extra': ('ens_ssvar_bin_size = 0.1; '
                                        'ens_phist_bin_size = 0.05;')

                          },
                        ]

    ensemble_var_list = config_metplus.parse_var_list(config, time_info,
                                            data_type='ENS')

    # parse optional var list for FCST and/or OBS fields
    var_list = config_metplus.parse_var_list(config, time_info,
                                   met_tool='ensemble_stat')

    pp = pprint.PrettyPrinter()
    print(f'ENSEMBLE_VAR_LIST:')
    pp.pprint(ensemble_var_list)
    print(f'VAR_LIST:')
    pp.pprint(var_list)

    assert(len(ensemble_var_list) == len(expected_ens_list))
    for actual_ens, expected_ens in zip(ensemble_var_list, expected_ens_list):
        for key, value in expected_ens.items():
            assert actual_ens.get(key) == value

    assert(len(var_list) == len(expected_var_list))
    for actual_var, expected_var in zip(var_list, expected_var_list):
        for key, value in expected_var.items():
            assert actual_var.get(key) == value


@pytest.mark.util
def test_parse_var_list_series_by(metplus_config):
    config = metplus_config
    config.set('config', 'BOTH_EXTRACT_TILES_VAR1_NAME', 'RH')
    config.set('config', 'BOTH_EXTRACT_TILES_VAR1_LEVELS', 'P850, P700')
    config.set('config', 'BOTH_EXTRACT_TILES_VAR1_OUTPUT_NAMES',
               'RH_850mb, RH_700mb')

    config.set('config', 'BOTH_SERIES_ANALYSIS_VAR1_NAME', 'RH_850mb')
    config.set('config', 'BOTH_SERIES_ANALYSIS_VAR1_LEVELS', 'P850')
    config.set('config', 'BOTH_SERIES_ANALYSIS_VAR2_NAME', 'RH_700mb')
    config.set('config', 'BOTH_SERIES_ANALYSIS_VAR2_LEVELS', 'P700')
    time_info = {}

    expected_et_list = [{'index': '1',
                         'fcst_name': 'RH',
                         'fcst_level': 'P850',
                         'fcst_output_name': 'RH_850mb',
                         'obs_name': 'RH',
                         'obs_level': 'P850',
                         'obs_output_name': 'RH_850mb',
                         },
                        {'index': '1',
                         'fcst_name': 'RH',
                         'fcst_level': 'P700',
                         'fcst_output_name': 'RH_700mb',
                         'obs_name': 'RH',
                         'obs_level': 'P700',
                         'obs_output_name': 'RH_700mb',
                         },
                        ]
    expected_sa_list = [{'index': '1',
                         'fcst_name': 'RH_850mb',
                         'fcst_level': 'P850',
                         'obs_name': 'RH_850mb',
                         'obs_level': 'P850',
                         },
                        {'index': '2',
                         'fcst_name': 'RH_700mb',
                         'fcst_level': 'P700',
                         'obs_name': 'RH_700mb',
                         'obs_level': 'P700',
                         },
                        ]

    actual_et_list = config_metplus.parse_var_list(config,
                                         time_info=time_info,
                                         met_tool='extract_tiles')

    actual_sa_list = config_metplus.parse_var_list(config,
                                         met_tool='series_analysis')

    pp = pprint.PrettyPrinter()
    print(f'ExtractTiles var list:')
    pp.pprint(actual_et_list)
    print(f'SeriesAnalysis var list:')
    pp.pprint(actual_sa_list)

    assert len(actual_et_list) == len(expected_et_list)
    for actual_et, expected_et in zip(actual_et_list, expected_et_list):
        for key, value in expected_et.items():
            assert actual_et.get(key) == value

    assert(len(actual_sa_list) == len(expected_sa_list))
    for actual_sa, expected_sa in zip(actual_sa_list, expected_sa_list):
        for key, value in expected_sa.items():
            assert actual_sa.get(key) == value


@pytest.mark.parametrize(
    'start_index', [
      0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    ]
)
@pytest.mark.util
def test_parse_var_list_priority_fcst(metplus_config, start_index):
    priority_list = ['FCST_GRID_STAT_VAR1_NAME',
                     'FCST_GRID_STAT_VAR1_INPUT_FIELD_NAME',
                     'FCST_GRID_STAT_VAR1_FIELD_NAME',
                     'BOTH_GRID_STAT_VAR1_NAME',
                     'BOTH_GRID_STAT_VAR1_INPUT_FIELD_NAME',
                     'BOTH_GRID_STAT_VAR1_FIELD_NAME',
                     'FCST_VAR1_NAME',
                     'FCST_VAR1_INPUT_FIELD_NAME',
                     'FCST_VAR1_FIELD_NAME',
                     'BOTH_VAR1_NAME',
                     'BOTH_VAR1_INPUT_FIELD_NAME',
                     'BOTH_VAR1_FIELD_NAME',
                     ]
    time_info = {}
    config = metplus_config
    for key in priority_list[start_index:]:
        config.set('config', key, key.lower())

    var_list = config_metplus.parse_var_list(config, time_info=time_info,
                                             data_type='FCST',
                                             met_tool='grid_stat')
    assert len(var_list) == 1
    assert var_list[0].get('fcst_name') == priority_list[start_index].lower()


# test that if wrapper specific field info is specified, it only gets
# values from that list. All generic values should be read if no
# wrapper specific field info variables are specified
@pytest.mark.util
def test_parse_var_list_wrapper_specific(metplus_config):
    conf = metplus_config
    conf.set('config', 'FCST_VAR1_NAME', "ENAME1")
    conf.set('config', 'FCST_VAR1_LEVELS', "ELEVELS11, ELEVELS12")
    conf.set('config', 'FCST_VAR2_NAME', "ENAME2")
    conf.set('config', 'FCST_VAR2_LEVELS', "ELEVELS21, ELEVELS22")
    conf.set('config', 'FCST_GRID_STAT_VAR1_NAME', "GNAME1")
    conf.set('config', 'FCST_GRID_STAT_VAR1_LEVELS', "GLEVELS11, GLEVELS12")

    e_var_list = config_metplus.parse_var_list(conf,
                                     time_info=None,
                                     data_type='FCST',
                                     met_tool='ensemble_stat')

    g_var_list = config_metplus.parse_var_list(conf,
                                     time_info=None,
                                     data_type='FCST',
                                     met_tool='grid_stat')

    assert(len(e_var_list) == 4 and len(g_var_list) == 2 and
           e_var_list[0]['fcst_name'] == "ENAME1" and
           e_var_list[1]['fcst_name'] == "ENAME1" and
           e_var_list[2]['fcst_name'] == "ENAME2" and
           e_var_list[3]['fcst_name'] == "ENAME2" and
           e_var_list[0]['fcst_level'] == "ELEVELS11" and
           e_var_list[1]['fcst_level'] == "ELEVELS12" and
           e_var_list[2]['fcst_level'] == "ELEVELS21" and
           e_var_list[3]['fcst_level'] == "ELEVELS22" and
           g_var_list[0]['fcst_name'] == "GNAME1" and
           g_var_list[1]['fcst_name'] == "GNAME1" and
           g_var_list[0]['fcst_level'] == "GLEVELS11" and
           g_var_list[1]['fcst_level'] == "GLEVELS12")


@pytest.mark.parametrize(
    'config_overrides, expected_results', [
        # 2 levels
        ({'FCST_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d} {fcst_level}',
          'FCST_VAR1_LEVELS': 'P500,P250',
          'OBS_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d} {obs_level}',
          'OBS_VAR1_LEVELS': 'P500,P250',
          },
         ['read_data.py TMP 20200201 P500',
          'read_data.py TMP 20200201 P250',
          ]),
        ({'BOTH_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d} {fcst_level}',
          'BOTH_VAR1_LEVELS': 'P500,P250',
          },
         ['read_data.py TMP 20200201 P500',
          'read_data.py TMP 20200201 P250',
          ]),
        # no level but level specified in name
        ({'FCST_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d} {fcst_level}',
          'OBS_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d} {obs_level}',
         },
         ['read_data.py TMP 20200201 ',
          ]),
        # no level
        ({'FCST_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d}',
          'OBS_VAR1_NAME': 'read_data.py TMP {valid?fmt=%Y%m%d}',
          },
         ['read_data.py TMP 20200201',
          ]),
        # real example
        ({'BOTH_VAR1_NAME': ('myscripts/read_nc2xr.py '
                            'mydata/forecast_file.nc4 TMP '
                            '{valid?fmt=%Y%m%d_%H%M} {fcst_level}'),
         'BOTH_VAR1_LEVELS': 'P1000,P850,P700,P500,P250,P100',
          },
        [('myscripts/read_nc2xr.py mydata/forecast_file.nc4 TMP 20200201_1225'
         ' P1000'),
         ('myscripts/read_nc2xr.py mydata/forecast_file.nc4 TMP 20200201_1225'
         ' P850'),
         ('myscripts/read_nc2xr.py mydata/forecast_file.nc4 TMP 20200201_1225'
         ' P700'),
         ('myscripts/read_nc2xr.py mydata/forecast_file.nc4 TMP 20200201_1225'
         ' P500'),
         ('myscripts/read_nc2xr.py mydata/forecast_file.nc4 TMP 20200201_1225'
         ' P250'),
         ('myscripts/read_nc2xr.py mydata/forecast_file.nc4 TMP 20200201_1225'
         ' P100'),
         ]),
    ]
)
@pytest.mark.util
def test_parse_var_list_py_embed_multi_levels(metplus_config, config_overrides,
                                              expected_results):
    config = metplus_config
    for key, value in config_overrides.items():
        config.set('config', key, value)

    time_info = {'valid': datetime(2020, 2, 1, 12, 25)}
    var_list = config_metplus.parse_var_list(config,
                                   time_info=time_info,
                                   data_type=None)
    assert len(var_list) == len(expected_results)

    for var_item, expected_result in zip(var_list, expected_results):
        assert var_item['fcst_name'] == expected_result

    # run again with data type specified
    var_list = config_metplus.parse_var_list(config,
                                    time_info=time_info,
                                    data_type='FCST')
    assert len(var_list) == len(expected_results)

    for var_item, expected_result in zip(var_list, expected_results):
        assert var_item['fcst_name'] == expected_result


@pytest.mark.util
def test_getraw_sub_and_nosub(metplus_config):
    raw_string = '{MODEL}_{CURRENT_FCST_NAME}'
    sub_actual = 'FCST_NAME'

    config = metplus_config
    config.set('config', 'MODEL', 'FCST')
    config.set('config', 'CURRENT_FCST_NAME', 'NAME')
    config.set('config', 'OUTPUT_PREFIX', raw_string)
    nosub_value = config.getraw('config', 'OUTPUT_PREFIX', sub_vars=False)
    assert nosub_value == raw_string

    sub_value = config.getraw('config', 'OUTPUT_PREFIX', sub_vars=True)
    assert sub_value == sub_actual


@pytest.mark.util
def test_getraw_instance_with_unset_var(metplus_config):
    """! Replicates bug where CURRENT_FCST_NAME is substituted with
     an empty string when copied from an instance section
     """
    pytest.skip()
    instance = 'my_section'
    config = metplus_config
    config.set('config', 'MODEL', 'FCST')

    config.add_section(instance)
    config.set('config', 'CURRENT_FCST_NAME', '')
    config.set(instance, 'OUTPUT_PREFIX', '{MODEL}_{CURRENT_FCST_NAME}')
    new_config = (
        config_metplus.replace_config_from_section(config,
                                                   instance,
                                                   required=False)
    )
    new_config.set('config', 'CURRENT_FCST_NAME', 'NAME')
    assert new_config.getraw('config', 'OUTPUT_PREFIX') == 'FCST_NAME'


@pytest.mark.parametrize(
    'config_value, expected_result', [
        # 2 items semi-colon at end
        ('GRIB_lvl_typ = 234;  desc = "HI_CLOUD";',
         'GRIB_lvl_typ = 234; desc = "HI_CLOUD";'),
        # 2 items no semi-colon at end
        ('GRIB_lvl_typ = 234;  desc = "HI_CLOUD"',
         'GRIB_lvl_typ = 234; desc = "HI_CLOUD";'),
        # 1 item semi-colon at end
        ('GRIB_lvl_typ = 234;',
         'GRIB_lvl_typ = 234;'),
        # 1 item no semi-colon at end
        ('GRIB_lvl_typ = 234',
         'GRIB_lvl_typ = 234;'),
    ]
)
@pytest.mark.util
def test_format_var_items_options_semicolon(config_value,
                                            expected_result):
    time_info = {}

    field_configs = {'name': 'FNAME',
                     'levels': 'FLEVEL',
                     'options': config_value}

    var_items = config_metplus._format_var_items(field_configs, time_info)
    result = var_items.get('extra')
    assert result == expected_result


@pytest.mark.util
def test_parse_var_list_double_digit(metplus_config):
    config = metplus_config
    for n in range(1, 12, 1):
        config.set('config', f'FCST_VAR{n}_NAME', f'fcst_name{n}')
        config.set('config', f'OBS_VAR{n}_NAME', f'obs_name{n}')

    var_list = config_metplus.parse_var_list(config)
    for n, var_item in enumerate(var_list, start=1):
        assert var_item['fcst_name'] == f'fcst_name{n}'
        assert var_item['obs_name'] == f'obs_name{n}'
