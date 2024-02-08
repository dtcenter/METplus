#!/usr/bin/env python3

import pytest

import re
from datetime import datetime

from metplus.wrappers.user_script_wrapper import UserScriptWrapper


def sub_clock_time(input_cmd, clock_time):
    """! Helper function to replace clock time from config in expected output
     commands that use the 'now' filename template tag

        @param input_cmd command to process
        @returns input command with YYYY, mm, dd, or HH substituted with
        values from clock time config variable
    """
    # for 'some SUB[YYYYmmdd] other text'
    # tuple value 1 is SUB[YYYYmmdd], value 2 is YYYYmmdd
    all_matches = re.findall(r'.*?(SUB\[(.*?)\])+.*?', input_cmd)
    if not all_matches:
        return input_cmd

    output_cmd = input_cmd

    for replace_text, time_text in all_matches:
        sub_time_text = time_text
        if 'YYYY' in time_text:
            sub_time_text = sub_time_text.replace('YYYY',
                                                  clock_time.strftime('%Y'))
        if 'mm' in input_cmd:
            sub_time_text = sub_time_text.replace('mm',
                                                  clock_time.strftime('%m'))
        if 'dd' in input_cmd:
            sub_time_text = sub_time_text.replace('dd',
                                                  clock_time.strftime('%d'))
        if 'HH' in input_cmd:
            sub_time_text = sub_time_text.replace('HH',
                                                  clock_time.strftime('%H'))
        if 'MM' in input_cmd:
            sub_time_text = sub_time_text.replace('MM',
                                                  clock_time.strftime('%M'))
        if 'SS' in input_cmd:
            sub_time_text = sub_time_text.replace('SS',
                                                  clock_time.strftime('%S'))

        output_cmd = output_cmd.replace(replace_text, sub_time_text)

    return output_cmd


def set_run_type_info(config, run_type):
    """! Set time values for init or valid time in config object

         @param config METplusConfig object
         @param run_type either 'INIT' or 'VALID'
    """
    if run_type in ['INIT', 'VALID']:
        config.set('config', 'LOOP_BY', run_type)
        config.set('config', f'{run_type}_TIME_FMT', '%Y%m%d%H%M%S')
        config.set('config', f'{run_type}_BEG', '20141031093015')
        config.set('config', f'{run_type}_END', '20141101093015')
        config.set('config', f'{run_type}_INCREMENT', '12H')

    if run_type == 'LEAD_SEQ':
        config.set('config', 'LEAD_SEQ', '0,12,24,120')
    elif run_type == 'LEAD_GROUPS':
        config.set('config', 'LEAD_SEQ_1', '0,24,48,72')
        config.set('config', 'LEAD_SEQ_1_LABEL', 'Group1')
        config.set('config', 'LEAD_SEQ_2', '96,120,144,168')
        config.set('config', 'LEAD_SEQ_2_LABEL', 'Group2')


@pytest.mark.parametrize(
    'input_configs, run_types, expected_cmds', [
        # run once simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         None,
         ['echo hello']),
        # run once now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         None,
         ['echo SUB[YYYYmmddHHMMSS]']),
        # run once init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         None,
         ['echo init_*_valid_*_lead_*.nc']),
        # run per init simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['INIT'],
         ['echo hello'] * 3),
        # run per init now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['INIT'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 3),
        # run per init init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['INIT'],
         ['echo init_20141031093015_valid_*_lead_*.nc',
          'echo init_20141031213015_valid_*_lead_*.nc',
          'echo init_20141101093015_valid_*_lead_*.nc',
          ]),
        # run per valid simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['VALID'],
         ['echo hello'] * 3),
        # run per valid now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['VALID'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 3),
        # run per valid init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['VALID'],
         ['echo init_*_valid_20141031093015_lead_*.nc',
          'echo init_*_valid_20141031213015_lead_*.nc',
          'echo init_*_valid_20141101093015_lead_*.nc',
          ]),
        # run per lead sequence simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_LEAD',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['LEAD_SEQ'],
         ['echo hello'] * 4),
        # run per lead sequence now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_LEAD',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['LEAD_SEQ'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 4),
        # run per lead sequence init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_LEAD',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['LEAD_SEQ'],
         ['echo init_*_valid_*_lead_000.nc',
          'echo init_*_valid_*_lead_012.nc',
          'echo init_*_valid_*_lead_024.nc',
          'echo init_*_valid_*_lead_120.nc',
          ]),
        # run per lead groups simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_LEAD',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['LEAD_GROUPS'],
         ['echo hello'] * 8),
        # run per lead groups now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_LEAD',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['LEAD_GROUPS'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 8),
        # run per lead groups init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_LEAD',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['LEAD_GROUPS'],
         ['echo init_*_valid_*_lead_000.nc',
          'echo init_*_valid_*_lead_024.nc',
          'echo init_*_valid_*_lead_048.nc',
          'echo init_*_valid_*_lead_072.nc',
          'echo init_*_valid_*_lead_096.nc',
          'echo init_*_valid_*_lead_120.nc',
          'echo init_*_valid_*_lead_144.nc',
          'echo init_*_valid_*_lead_168.nc',
          ]),
        # run all init/lead sequence - simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['LEAD_SEQ', 'INIT'],
         ['echo hello'] * 12),
        # run all init/lead sequence - now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['LEAD_SEQ', 'INIT'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 12),
        # run all init/lead sequence - init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['LEAD_SEQ', 'INIT'],
         ['echo init_20141031093015_valid_20141031093015_lead_000.nc',
          'echo init_20141031093015_valid_20141031213015_lead_012.nc',
          'echo init_20141031093015_valid_20141101093015_lead_024.nc',
          'echo init_20141031093015_valid_20141105093015_lead_120.nc',
          'echo init_20141031213015_valid_20141031213015_lead_000.nc',
          'echo init_20141031213015_valid_20141101093015_lead_012.nc',
          'echo init_20141031213015_valid_20141101213015_lead_024.nc',
          'echo init_20141031213015_valid_20141105213015_lead_120.nc',
          'echo init_20141101093015_valid_20141101093015_lead_000.nc',
          'echo init_20141101093015_valid_20141101213015_lead_012.nc',
          'echo init_20141101093015_valid_20141102093015_lead_024.nc',
          'echo init_20141101093015_valid_20141106093015_lead_120.nc',
          ]),
        # run all valid/lead sequence - simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['LEAD_SEQ', 'VALID'],
         ['echo hello'] * 12),
        # run all valid/lead sequence - now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['LEAD_SEQ', 'VALID'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 12),
        # run all valid/lead sequence - init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['LEAD_SEQ', 'VALID'],
         ['echo init_20141031093015_valid_20141031093015_lead_000.nc',
          'echo init_20141030213015_valid_20141031093015_lead_012.nc',
          'echo init_20141030093015_valid_20141031093015_lead_024.nc',
          'echo init_20141026093015_valid_20141031093015_lead_120.nc',
          'echo init_20141031213015_valid_20141031213015_lead_000.nc',
          'echo init_20141031093015_valid_20141031213015_lead_012.nc',
          'echo init_20141030213015_valid_20141031213015_lead_024.nc',
          'echo init_20141026213015_valid_20141031213015_lead_120.nc',
          'echo init_20141101093015_valid_20141101093015_lead_000.nc',
          'echo init_20141031213015_valid_20141101093015_lead_012.nc',
          'echo init_20141031093015_valid_20141101093015_lead_024.nc',
          'echo init_20141027093015_valid_20141101093015_lead_120.nc',
          ]),
        # run all init/lead groups - simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['LEAD_GROUPS', 'INIT'],
         ['echo hello'] * 24),
        # run all init/lead groups - now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['LEAD_GROUPS', 'INIT'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 24),
        # run all init/lead groups - init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['LEAD_GROUPS', 'INIT'],
         ['echo init_20141031093015_valid_20141031093015_lead_000.nc',
          'echo init_20141031093015_valid_20141101093015_lead_024.nc',
          'echo init_20141031093015_valid_20141102093015_lead_048.nc',
          'echo init_20141031093015_valid_20141103093015_lead_072.nc',
          'echo init_20141031093015_valid_20141104093015_lead_096.nc',
          'echo init_20141031093015_valid_20141105093015_lead_120.nc',
          'echo init_20141031093015_valid_20141106093015_lead_144.nc',
          'echo init_20141031093015_valid_20141107093015_lead_168.nc',
          'echo init_20141031213015_valid_20141031213015_lead_000.nc',
          'echo init_20141031213015_valid_20141101213015_lead_024.nc',
          'echo init_20141031213015_valid_20141102213015_lead_048.nc',
          'echo init_20141031213015_valid_20141103213015_lead_072.nc',
          'echo init_20141031213015_valid_20141104213015_lead_096.nc',
          'echo init_20141031213015_valid_20141105213015_lead_120.nc',
          'echo init_20141031213015_valid_20141106213015_lead_144.nc',
          'echo init_20141031213015_valid_20141107213015_lead_168.nc',
          'echo init_20141101093015_valid_20141101093015_lead_000.nc',
          'echo init_20141101093015_valid_20141102093015_lead_024.nc',
          'echo init_20141101093015_valid_20141103093015_lead_048.nc',
          'echo init_20141101093015_valid_20141104093015_lead_072.nc',
          'echo init_20141101093015_valid_20141105093015_lead_096.nc',
          'echo init_20141101093015_valid_20141106093015_lead_120.nc',
          'echo init_20141101093015_valid_20141107093015_lead_144.nc',
          'echo init_20141101093015_valid_20141108093015_lead_168.nc',
          ]),
        # run all valid/lead groups - simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo hello'},
         ['LEAD_GROUPS', 'VALID'],
         ['echo hello'] * 24),
        # run all valid/lead groups - now template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo {now?fmt=%Y%m%d%H%M%S}'},
         ['LEAD_GROUPS', 'VALID'],
         ['echo SUB[YYYYmmddHHMMSS]'] * 24),
        # run all valid/lead groups - init/valid/lead template
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': (
                  'echo init_{init?fmt=%Y%m%d%H%M%S}_'
                  'valid_{valid?fmt=%Y%m%d%H%M%S}_lead_{lead?fmt=%3H}.nc')},
         ['LEAD_GROUPS', 'VALID'],
         ['echo init_20141031093015_valid_20141031093015_lead_000.nc',
          'echo init_20141030093015_valid_20141031093015_lead_024.nc',
          'echo init_20141029093015_valid_20141031093015_lead_048.nc',
          'echo init_20141028093015_valid_20141031093015_lead_072.nc',
          'echo init_20141027093015_valid_20141031093015_lead_096.nc',
          'echo init_20141026093015_valid_20141031093015_lead_120.nc',
          'echo init_20141025093015_valid_20141031093015_lead_144.nc',
          'echo init_20141024093015_valid_20141031093015_lead_168.nc',
          'echo init_20141031213015_valid_20141031213015_lead_000.nc',
          'echo init_20141030213015_valid_20141031213015_lead_024.nc',
          'echo init_20141029213015_valid_20141031213015_lead_048.nc',
          'echo init_20141028213015_valid_20141031213015_lead_072.nc',
          'echo init_20141027213015_valid_20141031213015_lead_096.nc',
          'echo init_20141026213015_valid_20141031213015_lead_120.nc',
          'echo init_20141025213015_valid_20141031213015_lead_144.nc',
          'echo init_20141024213015_valid_20141031213015_lead_168.nc',
          'echo init_20141101093015_valid_20141101093015_lead_000.nc',
          'echo init_20141031093015_valid_20141101093015_lead_024.nc',
          'echo init_20141030093015_valid_20141101093015_lead_048.nc',
          'echo init_20141029093015_valid_20141101093015_lead_072.nc',
          'echo init_20141028093015_valid_20141101093015_lead_096.nc',
          'echo init_20141027093015_valid_20141101093015_lead_120.nc',
          'echo init_20141026093015_valid_20141101093015_lead_144.nc',
          'echo init_20141025093015_valid_20141101093015_lead_168.nc',
          ]),
        # run once custom loop list
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE',
          'USER_SCRIPT_COMMAND': 'echo {custom}',
          'USER_SCRIPT_CUSTOM_LOOP_LIST': 'a,b'},
         None,
         ['echo a', 'echo b']),
        # run per valid custom loop list
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': 'echo {custom}',
          'USER_SCRIPT_CUSTOM_LOOP_LIST': 'a,b'},
         ['VALID'],
         ['echo a'] * 3 + ['echo b'] * 3),
        # run per init custom loop list
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_PER_INIT_OR_VALID',
          'USER_SCRIPT_COMMAND': 'echo {custom}',
          'USER_SCRIPT_CUSTOM_LOOP_LIST': 'a,b'},
         ['INIT'],
         ['echo a'] * 3 + ['echo b'] * 3),
        # run all init/lead sequence - simple
        ({'USER_SCRIPT_RUNTIME_FREQ': 'RUN_ONCE_FOR_EACH',
          'USER_SCRIPT_COMMAND': 'echo {custom}',
          'USER_SCRIPT_CUSTOM_LOOP_LIST': 'a,b'},
         ['LEAD_SEQ', 'INIT'],
         ['echo a'] * 12 + ['echo b'] * 12),
    ]
)
@pytest.mark.wrapper
def test_run_user_script_all_times(metplus_config, input_configs,
                                   run_types, expected_cmds):
    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)

    for key, value in input_configs.items():
        config.set('config', key, value)

    # set config variables for init or valid time looping
    if run_types:
        for run_type in run_types:
            set_run_type_info(config, run_type)

    wrapper = UserScriptWrapper(config)
    all_commands = wrapper.run_all_times()

    if not all_commands:
        assert False

    clock_time = datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                   '%Y%m%d%H%M%S')

    for (actual_cmd, _), expected_cmd in zip(all_commands, expected_cmds):
        expected_cmd = sub_clock_time(expected_cmd, clock_time)
        print(f"  ACTUAL:{actual_cmd}")
        print(f"EXPECTED:{expected_cmd}")
        assert actual_cmd == expected_cmd
