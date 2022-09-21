#!/usr/bin/env python3

import pytest

import os

from datetime import datetime
from dateutil.relativedelta import relativedelta

from metplus.wrappers.grid_diag_wrapper import GridDiagWrapper


@pytest.mark.parametrize(
    'time_info, expected_subset', [
        # all files
        ({'init': '*', 'valid': '*', 'lead': '*'},
         ['init_20141031213015_valid_20141031213015_lead_000.nc',
          'init_20141031213015_valid_20141101213015_lead_024.nc',
          'init_20141101093015_valid_20141101093015_lead_000.nc',
          'init_20141101093015_valid_20141102093015_lead_024.nc',
          ]),
        # specific init
        ({'init': datetime(2014, 10, 31, 21, 30, 15), 'valid': '*', 'lead': '*'},
         ['init_20141031213015_valid_20141031213015_lead_000.nc',
          'init_20141031213015_valid_20141101213015_lead_024.nc',
          ]),
        # specific valid
        ({'init': '*', 'valid': datetime(2014, 11, 1, 9, 30, 15), 'lead': '*'},
         ['init_20141101093015_valid_20141101093015_lead_000.nc',
          ]),
        # specific lead integer zero
        ({'init': '*', 'valid': '*', 'lead': 0},
         ['init_20141031213015_valid_20141031213015_lead_000.nc',
          'init_20141101093015_valid_20141101093015_lead_000.nc',
          ]),
        # specific lead relativedelta non-zero
        ({'init': '*', 'valid': '*', 'lead': relativedelta(hours=24)},
          ['init_20141031213015_valid_20141101213015_lead_024.nc',
          'init_20141101093015_valid_20141102093015_lead_024.nc',
          ]),
        # specific lead integer non-zero
        ({'init': '*', 'valid': '*', 'lead': 86400},
          ['init_20141031213015_valid_20141101213015_lead_024.nc',
          'init_20141101093015_valid_20141102093015_lead_024.nc',
          ]),
        # specific init/valid/lead integer zero
        ({'init': datetime(2014, 10, 31, 21, 30, 15),
          'valid': datetime(2014, 10, 31, 21, 30, 15),
          'lead': 0},
         ['init_20141031213015_valid_20141031213015_lead_000.nc',
          ]),
        # specific init/valid/lead relativedelta non-zero
        ({'init': datetime(2014, 10, 31, 21, 30, 15),
          'valid': datetime(2014, 11, 1, 21, 30, 15),
          'lead': relativedelta(hours=24)},
         ['init_20141031213015_valid_20141101213015_lead_024.nc',
          ]),
        # specific init/valid/lead integer non-zero
        ({'init': datetime(2014, 10, 31, 21, 30, 15),
          'valid': datetime(2014, 11, 1, 21, 30, 15),
          'lead': 86400},
         ['init_20141031213015_valid_20141101213015_lead_024.nc',
          ]),
    ]
)
@pytest.mark.wrapper
def test_get_all_files_and_subset(metplus_config, time_info, expected_subset):
    """! Test to ensure that get_all_files only gets the files that are
    relevant to the runtime settings and not every file in the directory
    """
    config = metplus_config()
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'GRID_DIAG_RUNTIME_FREQ', 'RUN_ONCE')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H%M%S')
    config.set('config', 'INIT_BEG', '20141031213015')
    config.set('config', 'INIT_END', '20141101093015')
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '0H, 24H')

    input_dir = os.path.join(config.getdir('METPLUS_BASE'),
                             'internal', 'tests',
                             'data',
                             'user_script')
    config.set('config', 'GRID_DIAG_INPUT_DIR', input_dir)
    config.set('config', 'GRID_DIAG_INPUT_TEMPLATE',
               ('init_{init?fmt=%Y%m%d%H%M%S}_valid_{valid?fmt=%Y%m%d%H%M%S}_'
                'lead_{lead?fmt=%3H}.nc')
               )

    expected_files = []
    for init, valid, lead in [('20141031213015', '20141031213015', '000'),
                              ('20141031213015', '20141101213015', '024'),
                              ('20141101093015', '20141101093015', '000'),
                              ('20141101093015', '20141102093015', '024')]:
        filename = f'init_{init}_valid_{valid}_lead_{lead}.nc'
        expected_files.append(os.path.join(input_dir,
                                           filename))

    wrapper = GridDiagWrapper(config)
    assert(wrapper.get_all_files())

    # convert list of lists into a single list to compare to expected results

    actual_files = [item['input0'] for item in wrapper.c_dict['ALL_FILES']]
    actual_files = [item for sub in actual_files for item in sub]
    assert(actual_files == expected_files)

    file_list_dict = wrapper.subset_input_files(time_info)
    assert file_list_dict
    with open(file_list_dict['input0'], 'r') as file_handle:
        file_list = file_handle.readlines()

    file_list = file_list[1:]
    assert(len(file_list) == len(expected_subset))

    for actual_file, expected_file in zip(file_list, expected_subset):
        actual_file = actual_file.strip()
        assert(os.path.basename(actual_file) == expected_file)


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
    wrapper = GridDiagWrapper(metplus_config())
    assert(wrapper.get_list_file_name(time_info, 'input0') == expected_filename)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config()
    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'GridDiagConfig_wrapped')

    wrapper = GridDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'GRID_DIAG_CONFIG_FILE', fake_config_name)
    wrapper = GridDiagWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
