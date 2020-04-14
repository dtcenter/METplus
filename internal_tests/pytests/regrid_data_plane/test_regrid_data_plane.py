#!/usr/bin/env python

import os
import sys
import re
import logging
from collections import namedtuple
import produtil
import pytest
import datetime
import config_metplus
from regrid_data_plane_wrapper import RegridDataPlaneWrapper
import met_util as util
import time_util

# --------------------TEST CONFIGURATION and FIXTURE SUPPORT -------------
#
# The test configuration and fixture support the additional configuration
# files used in METplus
#              !!!!!!!!!!!!!!!
#              !!!IMPORTANT!!!
#              !!!!!!!!!!!!!!!
# The following two methods should be included in ALL pytest tests for METplus.
#
#
#def pytest_addoption(parser):
#    parser.addoption("-c", action="store", help=" -c <test config file>")


# @pytest.fixture
#def cmdopt(request):
#    return request.config.getoption("-c")


# -----------------FIXTURES THAT CAN BE USED BY ALL TESTS----------------
#@pytest.fixture
def rdp_wrapper():
    """! Returns a default RegridDataPlane with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    config = metplus_config()
    return RegridDataPlaneWrapper(config, config.logger)

#@pytest.fixture
def metplus_config():
    """! Create a METplus configuration object that can be
    manipulated/modified to
         reflect different paths, directories, values, etc. for individual
         tests.
    """
    config = config_metplus.setup(util.baseinputconfs)
    util.get_logger(config)
    return config


# ------------------------ TESTS GO HERE --------------------------


# ------------------------
#  test_find_obs_no_dated
# ------------------------
"""
def test_find_obs_no_dated():
    pcw = grid_stat_wrapper()
    v = {}
    v['obs_level'] = "6"
    task_info = {}
    task_info['valid'] = datetime.datetime.strptime("201802010000",'%Y%m%d%H%M')
    task_info['lead'] = 0
    time_info = time_util.ti_calculate(task_info)
    
    pcw.c_dict['OBS_FILE_WINDOW_BEGIN'] = -3600
    pcw.c_dict['OBS_FILE_WINDOW_END'] = 3600
    pcw.c_dict['OBS_INPUT_DIR'] = pcw.config.getdir('METPLUS_BASE')+"/internal_tests/data/obs"
    pcw.c_dict['OBS_INPUT_TEMPLATE'] = "{valid?fmt=%Y%m%d}_{valid?fmt=%H%M}"
    obs_file = pcw.find_obs(time_info, v)
    assert(obs_file == pcw.c_dict['OBS_INPUT_DIR']+'/20180201_0045')
"""
# conf_dict is produtil config items set before creating grid_stat wrapper instance
# out_dict is grid_stat wrapper c_dict values set by initialization
@pytest.mark.parametrize(
    'conf_dict, expected_field_info_list', [

        # 0) 1 item from var list
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06"},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'}]
         ),

        # 1) 1 item with level replaced from wrapper-specific
        ({'OBS_VAR1_NAME': 'P06M_NONE',
          'OBS_VAR1_LEVELS': "\"(*,*)\"",
          'OBS_REGRID_DATA_PLANE_VAR1_INPUT_LEVEL': '"({valid?fmt=%Y%m%d_%H%M%S},*,*)"'},
         [{'index': '1', 'obs_name': 'P06M_NONE', 'obs_level': '"(20180201_000000,*,*)"'},
          ]
        ),

        # 2) 2 items from var list
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          ]
         ),

        # 3) 2 items from var list, 3rd from wrapper-specific
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",
          'OBS_REGRID_DATA_PLANE_VAR3_INPUT_FIELD_NAME': 'NAME_FOR_3'},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          {'index': '3', 'obs_name': 'NAME_FOR_3'},
          ]
         ),

        # 4) 3 items from var list, 1 replaced and 4th from wrapper-specific
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",
          'OBS_VAR3_NAME': 'ACPCP',
          'OBS_VAR3_LEVELS': "A02",
          'OBS_REGRID_DATA_PLANE_VAR3_INPUT_FIELD_NAME': 'NAME_FOR_3',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_FIELD_NAME': 'NAME_FOR_4',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_LEVEL': 'LEVEL_FOR_4'},
        [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          {'index': '3', 'obs_name': 'NAME_FOR_3', 'obs_level': 'A02'},
          {'index': '4', 'obs_name': 'NAME_FOR_4', 'obs_level': 'LEVEL_FOR_4'},
         ]
         ),

        # 5) 1 item from var list add output name
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_REGRID_DATA_PLANE_VAR1_OUTPUT_FIELD_NAME': 'OUT_NAME',},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06', 'obs_output_name': 'OUT_NAME'}]
         ),

        # 6) 3 items from var list, 1 replaced and 4th from wrapper-specific, add output name
        ({'OBS_VAR1_NAME': 'APCP',
          'OBS_VAR1_LEVELS': "A06",
          'OBS_VAR2_NAME': 'ACPCP',
          'OBS_VAR2_LEVELS': "A03",
          'OBS_VAR3_NAME': 'ACPCP',
          'OBS_VAR3_LEVELS': "A02",
          'OBS_REGRID_DATA_PLANE_VAR3_INPUT_FIELD_NAME': 'NAME_FOR_3',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_FIELD_NAME': 'NAME_FOR_4',
          'OBS_REGRID_DATA_PLANE_VAR4_INPUT_LEVEL': 'LEVEL_FOR_4',
          'OBS_REGRID_DATA_PLANE_VAR4_OUTPUT_FIELD_NAME': 'OUT_NAME_4'},
         [{'index': '1', 'obs_name': 'APCP', 'obs_level': 'A06'},
          {'index': '2', 'obs_name': 'ACPCP', 'obs_level': 'A03'},
          {'index': '3', 'obs_name': 'NAME_FOR_3', 'obs_level': 'A02'},
          {'index': '4', 'obs_name': 'NAME_FOR_4', 'obs_level': 'LEVEL_FOR_4', 'obs_output_name': 'OUT_NAME_4'},
          ]
         ),
    ]
)

def test_get_field_info_list(conf_dict, expected_field_info_list):
    config = metplus_config()
    logger = logging.getLogger("dummy")

    data_type = 'OBS'

    for key, value in conf_dict.items():
        config.set('config', key, value)

    input_dict = {'valid': datetime.datetime.strptime("201802010000", '%Y%m%d%H%M'),
                  'lead': 0}
    time_info = time_util.ti_calculate(input_dict)

    var_list = util.parse_var_list(config, time_info, data_type=data_type)

    rdp = RegridDataPlaneWrapper(config, logger)

    field_info_list = rdp.get_field_info_list(var_list, data_type, time_info)
    print(f"FIELD INFO LIST: {field_info_list}")
    print(f"EXPECTED FIELD INFO LIST: {expected_field_info_list}")
    is_good = True
    if len(field_info_list) != len(expected_field_info_list):
        assert(False)

    for actual_field, expected_field in zip(field_info_list, expected_field_info_list):
        for key, value in expected_field.items():
            if actual_field[key] != value:
                print(f"{actual_field[key]} not equal to {value}")
                is_good = False

    assert(is_good)

