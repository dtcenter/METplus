#!/usr/bin/env python3

import pytest

import os
import sys
import datetime

from metplus.wrappers.tc_stat_wrapper import TCStatWrapper
from metplus.util import ti_calculate

loop_by = 'INIT'
run_times = ['20150301', '20150301']
config_init_beg = '20170705'
config_init_end = '20170901'

def get_config(metplus_config):
    # extra_configs = []
    # extra_configs.append(os.path.join(os.path.dirname(__file__),
    #                                   'tc_stat_conf.conf'))
    config = metplus_config

    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    config.set('config', 'PROCESS_LIST', 'TCStat')
    config.set('config', 'LOOP_BY', loop_by)
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d')
    config.set('config', 'INIT_BEG', run_times[0])
    config.set('config', 'INIT_END', run_times[-1])
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'TC_STAT_INIT_BEG', config_init_beg)
    config.set('config', 'TC_STAT_INIT_END', config_init_end)
    config.set('config', 'TC_STAT_INIT_HOUR', '00')
    config.set('config', 'TC_STAT_JOB_ARGS',
               ("-job summary -line_type TCMPR -column "
                "'ABS(AMAX_WIND-BMAX_WIND)' "
                "-dump_row {OUTPUT_BASE}/tc_stat/tc_stat_summary.tcst"))
    config.set('config', 'TC_STAT_LOOKIN_DIR',
               '{INPUT_BASE}/met_test/tc_pairs')
    config.set('config', 'TC_STAT_OUTPUT_DIR', '{OUTPUT_BASE}/tc_stat')
    return config


def tc_stat_wrapper(metplus_config):
    """! Returns a default TCStatWrapper with /path/to entries in the
         metplus_system.conf and metplus_runtime.conf configuration
         files.  Subsequent tests can customize the final METplus configuration
         to over-ride these /path/to values."""

    # Default, empty TcStatWrapper with some configuration values set
    # to /path/to:
    config = get_config(metplus_config)
    return TCStatWrapper(config)

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        # 0: no config overrides that set env vars
        ({}, {}),
        # 1 amodel
        ({'TC_STAT_AMODEL': 'AMODEL1,AMODEL2'},
         {'METPLUS_AMODEL': 'amodel = ["AMODEL1", "AMODEL2"];'}),
        # 2 bmodel
        ({'TC_STAT_BMODEL': 'BMODEL1,BMODEL2'},
         {'METPLUS_BMODEL': 'bmodel = ["BMODEL1", "BMODEL2"];'}),
        # 3 desc
        ({'TC_STAT_DESC': 'DESC1,DESC2'},
         {'METPLUS_DESC': 'desc = ["DESC1", "DESC2"];'}),
        # 4 storm_id
        ({'TC_STAT_STORM_ID': 'AL092011, EP082022'},
         {'METPLUS_STORM_ID': 'storm_id = ["AL092011", "EP082022"];'}),
        # 5 basin
        ({'TC_STAT_BASIN': 'AL,EP'},
         {'METPLUS_BASIN': 'basin = ["AL", "EP"];'}),
        # 6 cyclone
        ({'TC_STAT_CYCLONE': '01,02,03'},
         {'METPLUS_CYCLONE': 'cyclone = ["01", "02", "03"];'}),
        # 7 storm_name
        ({'TC_STAT_STORM_NAME': 'KATRINA, SANDY'},
         {'METPLUS_STORM_NAME': 'storm_name = ["KATRINA", "SANDY"];'}),
        # 8 init_beg
        ({'TC_STAT_INIT_BEG': '19870201'},
         {'METPLUS_INIT_BEG': 'init_beg = "19870201";'}),
        # 9 init_end
        ({'TC_STAT_INIT_END': '20221109'},
         {'METPLUS_INIT_END': 'init_end = "20221109";'}),
        # 10 init_inc
        ({'TC_STAT_INIT_INC': '19870201_06, 20001231_23'},
         {'METPLUS_INIT_INC': 'init_inc = ["19870201_06", "20001231_23"];'}),
        # 11 init_exc
        ({'TC_STAT_INIT_EXC': '19870201_12, 20001231_09'},
         {'METPLUS_INIT_EXC': 'init_exc = ["19870201_12", "20001231_09"];'}),
        # 12 valid_beg
        ({'TC_STAT_VALID_BEG': '19870201'},
         {'METPLUS_VALID_BEG': 'valid_beg = "19870201";'}),
        # 13 valid_end
        ({'TC_STAT_VALID_END': '20221109'},
         {'METPLUS_VALID_END': 'valid_end = "20221109";'}),
        # 14 valid_inc
        ({'TC_STAT_VALID_INC': '19870201_06, 20001231_23'},
         {'METPLUS_VALID_INC': 'valid_inc = ["19870201_06", "20001231_23"];'}),
        # 15 valid_exc
        ({'TC_STAT_VALID_EXC': '19870201_12, 20001231_09'},
         {'METPLUS_VALID_EXC': 'valid_exc = ["19870201_12", "20001231_09"];'}),
        # 16 init_hour
        ({'TC_STAT_INIT_HOUR': '00,06,12,18'},
         {'METPLUS_INIT_HOUR': 'init_hour = ["00", "06", "12", "18"];'}),
        # 17 valid_hour
        ({'TC_STAT_VALID_HOUR': '00,06,12,18'},
         {'METPLUS_VALID_HOUR': 'valid_hour = ["00", "06", "12", "18"];'}),
        # 18 lead
        ({'TC_STAT_LEAD': '00,062359'},
         {'METPLUS_LEAD': 'lead = ["00", "062359"];'}),
        # 19 lead_req
        ({'TC_STAT_LEAD_REQ': '00,062359'},
         {'METPLUS_LEAD_REQ': 'lead_req = ["00", "062359"];'}),
        # 20 init_mask
        ({'TC_STAT_INIT_MASK': 'MET_BASE/poly/EAST.poly'},
         {'METPLUS_INIT_MASK': 'init_mask = ["MET_BASE/poly/EAST.poly"];'}),
        # 21 valid_mask
        ({'TC_STAT_VALID_MASK': 'MET_BASE/poly/EAST.poly'},
         {'METPLUS_VALID_MASK': 'valid_mask = ["MET_BASE/poly/EAST.poly"];'}),
        # 22 line_type
        ({'TC_STAT_LINE_TYPE': 'TCMPR'},
         {'METPLUS_LINE_TYPE': 'line_type = ["TCMPR"];'}),
        # 23 track_watch_warn
        ({'TC_STAT_TRACK_WATCH_WARN': 'HUWATCH, HUWARN'},
         {'METPLUS_TRACK_WATCH_WARN': 'track_watch_warn = ["HUWATCH", "HUWARN"];'}),
        # 24 column_thresh_name
        ({'TC_STAT_COLUMN_THRESH_NAME': 'ADLAND, BDLAND'},
         {'METPLUS_COLUMN_THRESH_NAME': 'column_thresh_name = ["ADLAND", "BDLAND"];'}),
        # 25 column_thresh_val
        ({'TC_STAT_COLUMN_THRESH_VAL': '>200, >200'},
         {'METPLUS_COLUMN_THRESH_VAL': 'column_thresh_val = [>200, >200];'}),
        # 26 column_str_name
        ({'TC_STAT_COLUMN_STR_NAME': 'LEVEL, LEVEL'},
         {'METPLUS_COLUMN_STR_NAME': 'column_str_name = ["LEVEL", "LEVEL"];'}),
        # 27 column_str_val
        ({'TC_STAT_COLUMN_STR_VAL': 'HU, TS'},
         {'METPLUS_COLUMN_STR_VAL': 'column_str_val = ["HU", "TS"];'}),
        # 28 column_str_exc_name
        ({'TC_STAT_COLUMN_STR_EXC_NAME': 'LEVEL, LEVEL'},
         {'METPLUS_COLUMN_STR_EXC_NAME': 'column_str_exc_name = ["LEVEL", "LEVEL"];'}),
        # 29 column_str_exc_val
        ({'TC_STAT_COLUMN_STR_EXC_VAL': 'HU, TS'},
         {'METPLUS_COLUMN_STR_EXC_VAL': 'column_str_exc_val = ["HU", "TS"];'}),
        # 30 init_thresh_name
        ({'TC_STAT_INIT_THRESH_NAME': 'ADLAND, BDLAND'},
         {'METPLUS_INIT_THRESH_NAME': 'init_thresh_name = ["ADLAND", "BDLAND"];'}),
        # 31 init_thresh_val
        ({'TC_STAT_INIT_THRESH_VAL': '>200, >200'},
         {'METPLUS_INIT_THRESH_VAL': 'init_thresh_val = [>200, >200];'}),
        # 32 init_str_name
        ({'TC_STAT_INIT_STR_NAME': 'LEVEL, LEVEL'},
         {'METPLUS_INIT_STR_NAME': 'init_str_name = ["LEVEL", "LEVEL"];'}),
        # 33 init_str_val
        ({'TC_STAT_INIT_STR_VAL': 'HU, TS'},
         {'METPLUS_INIT_STR_VAL': 'init_str_val = ["HU", "TS"];'}),
        # 34 init_str_exc_name
        ({'TC_STAT_INIT_STR_EXC_NAME': 'LEVEL, LEVEL'},
         {'METPLUS_INIT_STR_EXC_NAME': 'init_str_exc_name = ["LEVEL", "LEVEL"];'}),
        # 35 init_str_exc_val
        ({'TC_STAT_INIT_STR_EXC_VAL': 'HU, TS'},
         {'METPLUS_INIT_STR_EXC_VAL': 'init_str_exc_val = ["HU", "TS"];'}),
        # 36 diag_thresh_name
        ({'TC_STAT_DIAG_THRESH_NAME': 'ADLAND, BDLAND'},
         {'METPLUS_DIAG_THRESH_NAME': 'diag_thresh_name = ["ADLAND", "BDLAND"];'}),
        # 37 diag_thresh_val
        ({'TC_STAT_DIAG_THRESH_VAL': '>200, >200'},
         {'METPLUS_DIAG_THRESH_VAL': 'diag_thresh_val = [>200, >200];'}),
        # 38 water_only
        ({'TC_STAT_WATER_ONLY': 'true'},
         {'METPLUS_WATER_ONLY': 'water_only = TRUE;'}),
        # 39 landfall
        ({'TC_STAT_LANDFALL': 'true'},
         {'METPLUS_LANDFALL': 'landfall = TRUE;'}),
        # 40 landfall_beg
        ({'TC_STAT_LANDFALL_BEG': '-24'},
         {'METPLUS_LANDFALL_BEG': 'landfall_beg = "-24";'}),
        # 41 landfall_end
        ({'TC_STAT_LANDFALL_END': '00'},
         {'METPLUS_LANDFALL_END': 'landfall_end = "00";'}),
        # 42 match_points
        ({'TC_STAT_MATCH_POINTS': 'true'},
         {'METPLUS_MATCH_POINTS': 'match_points = TRUE;'}),
        # 43 event_equal
        ({'TC_STAT_EVENT_EQUAL': 'true'},
         {'METPLUS_EVENT_EQUAL': 'event_equal = TRUE;'}),
        # 44 event_equal_lead
        ({'TC_STAT_EVENT_EQUAL_LEAD': '06,12'},
         {'METPLUS_EVENT_EQUAL_LEAD': 'event_equal_lead = ["06", "12"];'}),
        # 45 out_init_mask
        ({'TC_STAT_OUT_INIT_MASK': 'MET_BASE/poly/EAST.poly', },
         {'METPLUS_OUT_INIT_MASK': 'out_init_mask = "MET_BASE/poly/EAST.poly";'}),
        # 46 out_valid_mask
        ({'TC_STAT_OUT_VALID_MASK': 'MET_BASE/poly/EAST.poly', },
         {'METPLUS_OUT_VALID_MASK': 'out_valid_mask = "MET_BASE/poly/EAST.poly";'}),

    ]
)
@pytest.mark.wrapper
def test_tc_stat_run(metplus_config, config_overrides, env_var_values):
    config = get_config(metplus_config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    if f'METPLUS_{loop_by}_BEG' not in env_var_values:
        env_var_values[f'METPLUS_{loop_by}_BEG'] = (
            f'{loop_by.lower()}_beg = "{config_init_beg}";'
        )

    if f'METPLUS_{loop_by}_END' not in env_var_values:
        env_var_values[f'METPLUS_{loop_by}_END'] = (
            f'{loop_by.lower()}_end = "{config_init_end}";'
        )

    if 'METPLUS_INIT_HOUR' not in env_var_values:
        env_var_values['METPLUS_INIT_HOUR'] = f'init_hour = ["00"];'

    wrapper = TCStatWrapper(config)
    assert wrapper.isOK

    if 'METPLUS_JOBS' not in env_var_values:
        jobs = f"jobs = {wrapper.c_dict.get('JOBS')};"
        env_var_values['METPLUS_JOBS'] = jobs

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    lookin_dir = wrapper.c_dict.get('LOOKIN_DIR')
    out_temp = wrapper.c_dict.get('OUTPUT_TEMPLATE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    out_arg = f' -out {out_dir}/{out_temp}' if out_temp else ''

    expected_cmds = [
        (f"{app_path} {verbosity} -lookin {lookin_dir} "
         f"-config {config_file}{out_arg}"),
    ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")
    assert len(all_cmds) == len(expected_cmds)

    missing_env = [item for item in env_var_values
                   if item not in wrapper.WRAPPER_ENV_VAR_KEYS]

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert cmd == expected_cmd

        # check that environment variables were set properly
        for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS + missing_env:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert match is not None
            print(f'Checking env var: {env_var_key}')
            actual_value = match.split('=', 1)[1]
            assert env_var_values.get(env_var_key, '') == actual_value


@pytest.mark.parametrize(
        'overrides, c_dict', [
            ({'TC_STAT_INIT_BEG': '20150301',
              'TC_STAT_INIT_END': '20150304',
              'TC_STAT_BASIN': 'ML', },
             {'INIT_BEG': 'init_beg = "20150301";',
              'INIT_END': 'init_end = "20150304";',
              'BASIN': 'basin = ["ML"];',
              'CYCLONE': None,
              'STORM_NAME': None,}),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150304',
          'TC_STAT_CYCLONE': '030020', },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150304";',
          'BASIN': None,
          'CYCLONE': 'cyclone = ["030020"];',
          'STORM_NAME': None, }),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150325',
          'TC_STAT_STORM_NAME': '123', },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150325";',
          'INIT_HOUR': 'init_hour = ["00"];', # from config file
          'BASIN': None,
          'CYCLONE': None,
          'STORM_NAME': 'storm_name = ["123"];', }),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150325',
          'TC_STAT_STORM_ID': 'ML032015',
          'TC_STAT_INIT_HOUR': '',
         },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150325";',
          'INIT_HOUR': None,
          'BASIN': None,
          'CYCLONE': None,
          'STORM_ID': 'storm_id = ["ML032015"];', }),

        ({'TC_STAT_INIT_BEG': '20150301',
          'TC_STAT_INIT_END': '20150304',
          'TC_STAT_INIT_HOUR': '',
          'TC_STAT_CYCLONE': '030020',
          'TC_STAT_BASIN': 'ML', },
         {'INIT_BEG': 'init_beg = "20150301";',
          'INIT_END': 'init_end = "20150304";',
          'INIT_HOUR': None,
          'BASIN': 'basin = ["ML"];',
          'CYCLONE': 'cyclone = ["030020"];',
          'STORM_NAME': None, }),

        ({'TC_STAT_JOB_ARGS': '-job filter -dump_row filter_201401214_00.tcst',},
         {'JOBS': ['-job filter -dump_row filter_201401214_00.tcst']}),

        ({'TC_STAT_JOB_ARGS': ('-job filter -dump_row filter_201401214_00.tcst,'
                              '-job summary -dump_row summary.tcst  '), },
         {'JOBS': ['-job filter -dump_row filter_201401214_00.tcst',
                   '-job summary -dump_row summary.tcst']}),

        ({'TC_STAT_MATCH_POINTS': 'yes', },
         {'MATCH_POINTS': 'match_points = TRUE;'}),

        ({'TC_STAT_LOOKIN_DIR': '/my/new/input/dir', },
         {'LOOKIN_DIR': '/my/new/input/dir'}),

        ({'TC_STAT_COLUMN_STR_EXC_NAME': 'WATCH_WARN',
          'TC_STAT_COLUMN_STR_EXC_VAL': 'TSWATCH',},
         {'COLUMN_STR_EXC_NAME': 'column_str_exc_name = ["WATCH_WARN"];',
          'COLUMN_STR_EXC_VAL': 'column_str_exc_val = ["TSWATCH"];'}),

        ({'TC_STAT_INIT_STR_EXC_NAME': 'WATCH_WARN',
          'TC_STAT_INIT_STR_EXC_VAL': 'HUWARN',},
         {'INIT_STR_EXC_NAME': 'init_str_exc_name = ["WATCH_WARN"];',
          'INIT_STR_EXC_VAL': 'init_str_exc_val = ["HUWARN"];'}),

    ]
)
@pytest.mark.wrapper
def test_override_config_in_c_dict(metplus_config, overrides, c_dict):
    config = get_config(metplus_config)
    instance = 'tc_stat_overrides'
    if not config.has_section(instance):
        config.add_section(instance)
    for key, value in overrides.items():
        config.set(instance, key, value)
    wrapper = TCStatWrapper(config, instance=instance)
    for key, expected_value in c_dict.items():
        assert (wrapper.env_var_dict.get(f'METPLUS_{key}') == expected_value or
                wrapper.c_dict.get(key) == expected_value)


@pytest.mark.parametrize(
    'jobs, init_dt, expected_output', [
        # single fake job
            (['job1'],
             None,
             'jobs = ["job1"];'
            ),
        # 2 jobs, no time info
            (['-job filter -dump_row <output_dir>/filt.tcst',
              '-job rirw -line_type TCMPR '],
             None,
             'jobs = ["-job filter -dump_row <output_dir>/filt.tcst",'
             '"-job rirw -line_type TCMPR"];'
            ),

        # 2 jobs, time info sub
        (['-job filter -dump_row <output_dir>/{init?fmt=%Y%m%d%H}.tcst',
          '-job rirw -line_type TCMPR '],
         datetime.datetime(2019, 10, 31, 12),
         'jobs = ["-job filter -dump_row <output_dir>/2019103112.tcst",'
         '"-job rirw -line_type TCMPR"];'
         ),
    ]
)
@pytest.mark.wrapper
def test_handle_jobs(metplus_config, jobs, init_dt, expected_output):
    if init_dt:
        time_info = ti_calculate({'init': init_dt})
    else:
        time_info = None

    wrapper = tc_stat_wrapper(metplus_config)
    output_base = wrapper.config.getdir('OUTPUT_BASE')
    output_dir = os.path.join(output_base, 'test_handle_jobs')

    wrapper.c_dict['JOBS'] = []
    for job in jobs:
        wrapper.c_dict['JOBS'].append(job.replace('<output_dir>', output_dir))

    output = wrapper.handle_jobs(time_info)
    assert output == expected_output.replace('<output_dir>', output_dir)


def cleanup_test_dirs(parent_dirs, output_dir):
    if parent_dirs:
        for parent_dir in parent_dirs:
            parent_dir_sub = parent_dir.replace('<output_dir>', output_dir)
            if os.path.exists(parent_dir_sub):
                os.removedirs(parent_dir_sub)


@pytest.mark.parametrize(
    'jobs, init_dt, expected_output, parent_dirs', [
        # single fake job, no parent dir
            (['job1'],
             None,
             'jobs = ["job1"];',
             None
            ),
        # 2 jobs, no time info, 1 parent dir
            (['-job filter -dump_row <output_dir>/filt.tcst',
              '-job rirw -line_type TCMPR '],
             None,
             'jobs = ["-job filter -dump_row <output_dir>/filt.tcst",'
             '"-job rirw -line_type TCMPR"];',
             ['<output_dir>'],
            ),

        # 2 jobs, time info sub, 1 parent dir
        (['-job filter -dump_row <output_dir>/{init?fmt=%Y%m%d%H}.tcst',
          '-job rirw -line_type TCMPR '],
         datetime.datetime(2019, 10, 31, 12),
         'jobs = ["-job filter -dump_row <output_dir>/2019103112.tcst",'
         '"-job rirw -line_type TCMPR"];',
         ['<output_dir>'],
         ),

        # 2 jobs, no time info, 2 parent dirs
        (['-job filter -dump_row <output_dir>/subdir1/filt.tcst',
          '-job filter -dump_row <output_dir>/subdir2/filt2.tcst '],
         None,
         'jobs = ["-job filter -dump_row <output_dir>/subdir1/filt.tcst",'
         '"-job filter -dump_row <output_dir>/subdir2/filt2.tcst"];',
         ['<output_dir>/subdir1',
          '<output_dir>/subdir2',
          ],
         ),

        # 2 jobs, time info sub, 2 parent dirs
        (['-job filter -dump_row <output_dir>/sub1/{init?fmt=%Y%m%d%H}.tcst',
          '-job filter -dump_row <output_dir>/sub2/{init?fmt=%Y%m%d}.tcst '],
         datetime.datetime(2019, 10, 31, 12),
         'jobs = ["-job filter -dump_row <output_dir>/sub1/2019103112.tcst",'
         '"-job filter -dump_row <output_dir>/sub2/20191031.tcst"];',
         ['<output_dir>/sub1',
          '<output_dir>/sub2',],
         ),
    ]
)
@pytest.mark.wrapper
def test_handle_jobs_create_parent_dir(metplus_config, jobs, init_dt,
                                       expected_output, parent_dirs):
    # if init time is provided, calculate other time dict items
    if init_dt:
        time_info = ti_calculate({'init': init_dt})
    else:
        time_info = None

    config = get_config(metplus_config)
    config.set('config', 'DO_NOT_RUN_EXE', False)
    wrapper = TCStatWrapper(config)

    # create directory path relative to OUTPUT_BASE to test that function
    # creates parent directories properly
    # Used to replace <output_dir> string found in test arguments
    output_base = wrapper.config.getdir('OUTPUT_BASE')
    output_dir = os.path.join(output_base, 'test_handle_jobs')

    # remove parent dirs if they exist
    cleanup_test_dirs(parent_dirs, output_dir)

    wrapper.c_dict['JOBS'] = []
    for job in jobs:
        wrapper.c_dict['JOBS'].append(job.replace('<output_dir>', output_dir))

    output = wrapper.handle_jobs(time_info)
    if output != expected_output.replace('<output_dir>', output_dir):
        assert False

    # check if parent dir was created
    if parent_dirs:
        for parent_dir in parent_dirs:
            parent_dir_sub = parent_dir.replace('<output_dir>', output_dir)
            if not os.path.exists(parent_dir_sub):
                assert False

    # remove parent dirs to clean up for next run
    cleanup_test_dirs(parent_dirs, output_dir)


@pytest.mark.wrapper
def test_get_config_file(metplus_config):
    fake_config_name = '/my/config/file'

    config = metplus_config

    default_config_file = os.path.join(config.getdir('PARM_BASE'),
                                       'met_config',
                                       'TCStatConfig_wrapped')

    wrapper = TCStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == default_config_file

    config.set('config', 'TC_STAT_CONFIG_FILE', fake_config_name)
    wrapper = TCStatWrapper(config)
    assert wrapper.c_dict['CONFIG_FILE'] == fake_config_name
