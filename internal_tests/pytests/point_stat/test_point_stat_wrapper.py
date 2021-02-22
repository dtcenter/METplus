#!/usr/bin/env python

import os
import pytest

from metplus.wrappers.point_stat_wrapper import PointStatWrapper


def point_stat_wrapper(metplus_config):
    """! Returns a default PointStatWrapper """

    config = metplus_config()
    return PointStatWrapper(config)

@pytest.mark.parametrize(
    'config_overrides, env_var_values', [
        ({'MODEL': 'my_model'},
         {'METPLUS_MODEL': 'model = "my_model";'}),

        ({'POINT_STAT_DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'DESC': 'my_desc'},
         {'METPLUS_DESC': 'desc = "my_desc";'}),

        ({'OBTYPE': 'my_obtype'},
         {'METPLUS_OBTYPE': 'obtype = "my_obtype";'}),

        ({'POINT_STAT_REGRID_TO_GRID': 'FCST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {to_grid = FCST;}'}),

        ({'POINT_STAT_REGRID_METHOD': 'NEAREST',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {method = NEAREST;}'}),

        ({'POINT_STAT_REGRID_WIDTH': '1',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {width = 1;}'}),

        ({'POINT_STAT_REGRID_VLD_THRESH': '0.5',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {vld_thresh = 0.5;}'}),

        ({'POINT_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': 'regrid = {shape = SQUARE;}'}),

        ({'POINT_STAT_REGRID_TO_GRID': 'FCST',
          'POINT_STAT_REGRID_METHOD': 'NEAREST',
          'POINT_STAT_REGRID_WIDTH': '1',
          'POINT_STAT_REGRID_VLD_THRESH': '0.5',
          'POINT_STAT_REGRID_SHAPE': 'SQUARE',
          },
         {'METPLUS_REGRID_DICT': ('regrid = {to_grid = FCST;method = NEAREST;'
                                  'width = 1;vld_thresh = 0.5;shape = SQUARE;}'
                                  )}),

        ({'POINT_STAT_CLIMO_MEAN_INPUT_TEMPLATE':
              '/some/path/climo/filename.nc',
          },
         {'METPLUS_CLIMO_MEAN_FILE':
              'file_name = ["/some/path/climo/filename.nc"];',
          }),
        ({'POINT_STAT_CLIMO_STDEV_INPUT_TEMPLATE':
              '/some/path/climo/stdfile.nc',
          },
         {'METPLUS_CLIMO_STDEV_FILE':
              'climo_stdev = { file_name = ["/some/path/climo/stdfile.nc"]; }',
         }),
        # mask grid and poly (old config var)
        ({'POINT_STAT_MASK_GRID': 'FULL',
          'POINT_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_GRID': 'grid = ["FULL"];',
          'METPLUS_MASK_POLY': 'poly = ["one","two"];',
          }),
        # mask grid and poly (new config var)
        ({'POINT_STAT_MASK_GRID': 'FULL',
          'POINT_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_GRID': 'grid = ["FULL"];',
          'METPLUS_MASK_POLY': 'poly = ["one","two"];',
          }),
        # mask grid value
        ({'POINT_STAT_MASK_GRID': 'FULL',
          },
         {'METPLUS_MASK_GRID':
              'grid = ["FULL"];',
          }),
        # mask grid empty string (should create empty list)
        ({'POINT_STAT_MASK_GRID': '',
          },
         {'METPLUS_MASK_GRID':
              'grid = [];',
          }),
        # mask poly (old config var)
        ({'POINT_STAT_VERIFICATION_MASK_TEMPLATE': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one","two"];',
          }),
        # mask poly (new config var)
        ({'POINT_STAT_MASK_POLY': 'one, two',
          },
         {'METPLUS_MASK_POLY':
              'poly = ["one","two"];',
          }),

        ({'POINT_STAT_MASK_SID': 'one, two',
          },
         {'METPLUS_MASK_SID':
              'sid = ["one", "two"];',
          }),

        ({'POINT_STAT_NEIGHBORHOOD_COV_THRESH': '>=0.5'},
         {'METPLUS_NBRHD_COV_THRESH': 'cov_thresh = [>=0.5];'}),

        ({'POINT_STAT_NEIGHBORHOOD_WIDTH': '1,2'},
         {'METPLUS_NBRHD_WIDTH': 'width = [1, 2];'}),

        ({'POINT_STAT_NEIGHBORHOOD_SHAPE': 'CIRCLE'},
         {'METPLUS_NBRHD_SHAPE': 'shape = CIRCLE;'}),

        ({'POINT_STAT_OUTPUT_PREFIX': 'my_output_prefix'},
         {'METPLUS_OUTPUT_PREFIX': 'output_prefix = "my_output_prefix";'}),

        ({'POINT_STAT_MESSAGE_TYPE': 'ADPUPA, ADPSFC'},
         {'METPLUS_MESSAGE_TYPE': 'message_type = ["ADPUPA", "ADPSFC"];'}),

        ({'OBS_POINT_STAT_WINDOW_BEGIN': '-2700',
          'OBS_POINT_STAT_WINDOW_END': '2700',
          },
         {'METPLUS_OBS_WINDOW_DICT':
              'obs_window = {beg = -2700;end = 2700;}',
          }),


    ]
)
def test_point_stat_all_fields(metplus_config, config_overrides,
                               env_var_values):
    level_no_quotes = '(*,*)'
    level_with_quotes = f'"{level_no_quotes}"'

    fcst_dir = '/some/path/fcst'
    obs_dir = '/some/path/obs'

    fcsts = [{'name': 'TMP',
              'level': 'P750-900',
              'thresh': '<=273,>273'},
              {'name': 'UGRD',
               'level': 'Z10',
               'thresh': '>=5'},
              # {'name': 'VGRD',
              #  'level': 'Z10',
              #  'thresh': '>=5'},
             ]
    obss = [{'name': 'TMP',
            'level': level_no_quotes,
            'thresh': '<=273,>273'},
            {'name': 'UGRD',
             'level': 'Z10',
             'thresh': '>=5'},
            # {'name': 'VGRD',
            #  'level': 'Z10',
            #  'thresh': '>=5'},
           ]

    fcst_fmts = []
    obs_fmts = []
    for fcst, obs in zip(fcsts, obss):
        fcst_name = fcst['name']
        fcst_level = fcst['level']
        fcst_thresh = fcst['thresh']
        obs_name = obs['name']
        obs_level = obs['level']
        obs_thresh = obs['thresh']

        fcst_fmt = (f'{{ name="{fcst_name}"; level="{fcst_level}"; '
                    f'cat_thresh=[ {fcst_thresh} ]; }}')
        obs_fmt = (f'{{ name="{obs_name}"; level="{obs_level}"; '
                    f'cat_thresh=[ {obs_thresh} ]; }}')
        fcst_fmts.append(fcst_fmt)
        obs_fmts.append(obs_fmt)


    config = metplus_config()

    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', False)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'PointStat')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2005080700')
    config.set('config', 'INIT_END', '2005080712')
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LEAD_SEQ', '12H')
    config.set('config', 'LOOP_ORDER', 'times')

    config.set('config', 'POINT_STAT_CONFIG_FILE',
               '{PARM_BASE}/met_config/PointStatConfig_wrapped')
    config.set('config', 'FCST_POINT_STAT_INPUT_DIR', fcst_dir)
    config.set('config', 'OBS_POINT_STAT_INPUT_DIR', obs_dir)
    config.set('config', 'FCST_POINT_STAT_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d%H}/fcst_file_F{lead?fmt=%3H}')
    config.set('config', 'OBS_POINT_STAT_INPUT_TEMPLATE',
               '{valid?fmt=%Y%m%d%H}/obs_file')
    config.set('config', 'POINT_STAT_OUTPUT_DIR',
               '{OUTPUT_BASE}/GridStat/output')
    config.set('config', 'POINT_STAT_OUTPUT_TEMPLATE', '{valid?fmt=%Y%m%d%H}')

    for index, (fcst, obs) in enumerate(zip(fcsts, obss)):
        idx = index + 1
        if obs['level'] == level_no_quotes:
            obs['level'] = level_with_quotes
        config.set('config', f'FCST_VAR{idx}_NAME', fcst['name'])
        config.set('config', f'FCST_VAR{idx}_LEVELS', fcst['level'])
        config.set('config', f'FCST_VAR{idx}_THRESH', fcst['thresh'])
        config.set('config', f'OBS_VAR{idx}_NAME', obs['name'])
        config.set('config', f'OBS_VAR{idx}_LEVELS', obs['level'])
        config.set('config', f'OBS_VAR{idx}_THRESH', obs['thresh'])

    config.set('config', 'POINT_STAT_ONCE_PER_FIELD', False)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = PointStatWrapper(config)
    assert(wrapper.isOK)

    app_path = os.path.join(config.getdir('MET_BIN_DIR'), wrapper.app_name)
    verbosity = f"-v {wrapper.c_dict['VERBOSITY']}"
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')
    expected_cmds = [(f"{app_path} {verbosity} "
                      f"{fcst_dir}/2005080700/fcst_file_F012 "
                      f"{obs_dir}/2005080712/obs_file "
                      f"{config_file} -outdir {out_dir}/2005080712"),
                     (f"{app_path} {verbosity} "
                      f"{fcst_dir}/2005080712/fcst_file_F012 "
                      f"{obs_dir}/2005080800/obs_file "
                      f"{config_file} -outdir {out_dir}/2005080800"),
                     ]

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")

    fcst_fmt = f"field = [{','.join(fcst_fmts)}];"
    obs_fmt = f"field = [{','.join(obs_fmts)}];"

    for (cmd, env_vars), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert(cmd == expected_cmd)

        # check that environment variables were set properly
        for env_var_key in wrapper.WRAPPER_ENV_VAR_KEYS:
            match = next((item for item in env_vars if
                          item.startswith(env_var_key)), None)
            assert(match is not None)
            value = match.split('=', 1)[1]
            if env_var_key == 'METPLUS_FCST_FIELD':
                assert(value == fcst_fmt)
            elif env_var_key == 'METPLUS_OBS_FIELD':
                assert (value == obs_fmt)
            else:
                assert(env_var_values.get(env_var_key, '') == value)

