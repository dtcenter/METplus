#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.tcmpr_plotter_wrapper import TCMPRPlotterWrapper

EXPECTED_INPUT_FILES = [
    'another_fake_filter_20141214_00.tcst',
    'empty_filter.tcst',
    'fake_filter_20141214_00.tcst',
]
TIME_FMT = '%Y%m%d%H'
RUN_TIME = '20141214'


def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set('config', 'DO_NOT_RUN_EXE', True)

    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'TCMPRPlotter')
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', TIME_FMT)
    config.set('config', 'INIT_BEG', RUN_TIME)
    config.set('config', 'INIT_END', RUN_TIME)
    config.set('config', 'INIT_INCREMENT', '12H')
    config.set('config', 'LOOP_ORDER', 'processes')
    config.set('config', 'TCMPR_PLOTTER_CONFIG_FILE',
               ('{PARM_BASE}/use_cases/met_tool_wrapper/'
                'TCMPRPlotter/TCMPRPlotterConfig_Customize'))
    config.set('config', 'TCMPR_PLOTTER_PLOT_OUTPUT_DIR',
               '{OUTPUT_BASE}/TCMPRPlotter/tcmpr_plots')


@pytest.mark.parametrize(
    'config_overrides,expected_loop_args', [
        # 0: no loop args
        ({},
         {'dep': [('', '')], 'plot': [('', '')]}),
        # 1: 1 dep arg
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1'},
         {'dep': [('item1', 'item1')], 'plot': [('', '')]}),
        # 2: 2 dep args
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1, item2'},
         {'dep': [('item1', 'item1'), ('item2', 'item2')],
          'plot': [('', '')]}),
        # 3: 1 dep arg, 1 dep label
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1',
          'TCMPR_PLOTTER_DEP_LABELS': 'Label 1'},
         {'dep': [('item1', 'Label 1')], 'plot': [('', '')]}),
        # 4: 2 dep args, 2 dep labels
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1, item2',
          'TCMPR_PLOTTER_DEP_LABELS': 'Label 1, Label 2'},
         {'dep': [('item1', 'Label 1'), ('item2', 'Label 2')],
          'plot': [('', '')]}),
        # 5: 2 dep args, 1 dep label (error)
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1, item2',
          'TCMPR_PLOTTER_DEP_LABELS': 'Label 1'},
         None),
        # 6: 1 dep arg, 2 dep labels (error)
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1',
          'TCMPR_PLOTTER_DEP_LABELS': 'Label 1, Label 2'},
         None),
        # 7: 1 plot arg
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1'},
         {'plot': [('item1', 'item1')], 'dep': [('', '')]}),
        # 8: 2 plot args
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1, item2'},
         {'plot': [('item1', 'item1'), ('item2', 'item2')],
          'dep': [('', '')]}),
        # 9: 1 plot arg, 1 plot label
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1',
          'TCMPR_PLOTTER_PLOT_LABELS': 'Label 1'},
         {'plot': [('item1', 'Label 1')], 'dep': [('', '')]}),
        # 10: 2 plot args, 2 plot labels
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1, item2',
          'TCMPR_PLOTTER_PLOT_LABELS': 'Label 1, Label 2'},
         {'plot': [('item1', 'Label 1'), ('item2', 'Label 2')],
          'dep': [('', '')]}),
        # 11: 2 plot args, 1 plot label (error)
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1, item2',
          'TCMPR_PLOTTER_PLOT_LABELS': 'Label 1'},
         None),
        # 12: 1 plot arg, 2 plot labels (error)
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1',
          'TCMPR_PLOTTER_PLOT_LABELS': 'Label 1, Label 2'},
         None),
        # 13: 2 dep args, 2 plot args, 2 plot labels
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1, item2',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1, pitem2',
          'TCMPR_PLOTTER_PLOT_LABELS': 'P Label 1, P Label 2'
          },
         {'dep': [('item1', 'item1'), ('item2', 'item2')],
          'plot': [('pitem1', 'P Label 1'), ('pitem2', 'P Label 2')]}),
    ]
)
@pytest.mark.plotting
def test_read_loop_info(metplus_config, config_overrides, expected_loop_args):
    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    wrapper = TCMPRPlotterWrapper(config)
    assert wrapper.read_loop_info() == expected_loop_args


@pytest.mark.parametrize(
    'config_overrides,expected_strings', [
        # 0: no optional arguments
        ({}, ['']),
        # 1: 1 dep
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1'}, ['-dep ditem1']),
        # 2: 2 dep
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1, ditem2'}, ['-dep ditem1',
                                                        '-dep ditem2']),
        # 3: 1 plot
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1'}, ['-plot pitem1']),
        # 4: 2 plots
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1, pitem2'}, ['-plot pitem1',
                                                          '-plot pitem2']),
        # 5: 1 dep, 1 plot
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1'}, ['-dep ditem1 -plot pitem1']),
        # 6: 2 deps, 1 plot
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1, ditem2',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1'}, ['-dep ditem1 -plot pitem1',
                                                  '-dep ditem2 -plot pitem1']),
        # 7: 1 dep, 2 plots
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1, pitem2'},
         ['-dep ditem1 -plot pitem1',
          '-dep ditem1 -plot pitem2']),
        # 8: 2 deps, 2 plots
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1, ditem2',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1, pitem2'},
         ['-dep ditem1 -plot pitem1',
          '-dep ditem1 -plot pitem2',
          '-dep ditem2 -plot pitem1',
          '-dep ditem2 -plot pitem2'
          ]),
        # 9: 1 dep, 1 dep label, use label in ylab
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1',
          'TCMPR_PLOTTER_DEP_LABELS': 'D Label 1',
          'TCMPR_PLOTTER_YLAB': '{dep_label}A'},
         ['-ylab "D Label 1A" -dep ditem1']),
        # 10: 1 dep/label, 1 plot/label use both labels in title
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1',
          'TCMPR_PLOTTER_DEP_LABELS': 'D Label 1',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1',
          'TCMPR_PLOTTER_PLOT_LABELS': 'P Label 1',
          'TCMPR_PLOTTER_TITLE': '{dep_label}A {plot_label}B'},
         ['-title "D Label 1A P Label 1B" -dep ditem1 -plot pitem1']),
        # 10: 1 dep/label, 1 plot/label use labels in title, value in prefix
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1',
          'TCMPR_PLOTTER_DEP_LABELS': 'D Label 1',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1',
          'TCMPR_PLOTTER_PLOT_LABELS': 'P Label 1',
          'TCMPR_PLOTTER_TITLE': '{dep_label}A {plot_label}B',
          'TCMPR_PLOTTER_PREFIX': 'Eta_{dep}_{plot}'},
         [('-prefix "Eta_ditem1_pitem1" -title "D Label 1A P Label 1B" '
           '-dep ditem1 -plot pitem1')]),
        # 11: 1 dep/label, 1 plot/label use labels in title/prefix
        #     spaces change to underscores in prefix
        ({'TCMPR_PLOTTER_DEP_VARS': 'ditem1',
          'TCMPR_PLOTTER_DEP_LABELS': 'D Label 1',
          'TCMPR_PLOTTER_PLOT_TYPES': 'pitem1',
          'TCMPR_PLOTTER_PLOT_LABELS': 'P Label 1',
          'TCMPR_PLOTTER_TITLE': '{dep_label}A {plot_label}B',
          'TCMPR_PLOTTER_PREFIX': 'Eta_{dep_label}_{plot_label}'},
         [('-prefix "Eta_D_Label_1_P_Label_1" -title "D Label 1A P Label 1B" '
           '-dep ditem1 -plot pitem1')]),
    ]
)
@pytest.mark.plotting
def test_tcmpr_plotter_loop(metplus_config, config_overrides,
                            expected_strings):
    config = metplus_config

    set_minimum_config_settings(config)

    # set config variable overrides
    for key, value in config_overrides.items():
        config.set('config', key, value)

    test_data = os.path.join(config.getdir('METPLUS_BASE'),
                             'internal', 'tests',
                             'data',
                             'stat_data')

    config.set('config', 'TCMPR_PLOTTER_TCMPR_DATA_DIR', test_data)

    wrapper = TCMPRPlotterWrapper(config)
    assert wrapper.isOK

    app_path = wrapper.c_dict.get('TCMPR_SCRIPT')
    config_file = wrapper.c_dict.get('CONFIG_FILE')
    out_dir = wrapper.c_dict.get('OUTPUT_DIR')

    input_files = []
    for input_file in EXPECTED_INPUT_FILES:
        input_files.append(os.path.join(test_data, input_file))

    expected_cmds = []
    for expected_string in expected_strings:
        # add a space before value if expected string has a value
        if expected_string:
            expected_string = f' {expected_string}'

        expected_cmds.append(f"Rscript {app_path} -config {config_file}"
                             f"{expected_string}"
                             f" -lookin {' '.join(input_files)}"
                             f" -outdir {out_dir}")

    all_cmds = wrapper.run_all_times()
    print(f"ALL COMMANDS: {all_cmds}")

    for (actual_cmd, _), expected_cmd in zip(all_cmds, expected_cmds):
        # ensure commands are generated as expected
        assert actual_cmd == expected_cmd


@pytest.mark.parametrize(
    'config_overrides,expected_string', [
        # no optional arguments
        ({}, ''),
        # strings
        ({'TCMPR_PLOTTER_PREFIX': 'my_string'}, '-prefix "my_string"'),
        ({'TCMPR_PLOTTER_XLIM': 'my_string'}, '-xlim my_string'),
        ({'TCMPR_PLOTTER_YLIM': 'my_string'}, '-ylim my_string'),
        ({'TCMPR_PLOTTER_FILTERED_TCST_DATA_FILE': 'my_string'},
         '-tcst my_string'),
        ({'TCMPR_PLOTTER_SCATTER_X': 'my_string'}, '-scatter_x my_string'),
        ({'TCMPR_PLOTTER_SCATTER_Y': 'my_string'}, '-scatter_y my_string'),
        ({'TCMPR_PLOTTER_SKILL_REF': 'my_string'}, '-skill_ref my_string'),
        ({'TCMPR_PLOTTER_SERIES': 'my_string'}, '-series my_string'),
        ({'TCMPR_PLOTTER_SERIES_CI': 'my_string'}, '-series_ci my_string'),
        ({'TCMPR_PLOTTER_LEAD': 'my_string'}, '-lead my_string'),
        ({'TCMPR_PLOTTER_RP_DIFF': 'my_string'}, '-rp_diff my_string'),
        ({'TCMPR_PLOTTER_DEMO_YR': 'my_string'}, '-demo_yr my_string'),
        ({'TCMPR_PLOTTER_HFIP_BSLN': 'my_string'}, '-hfip_bsln my_string'),
        ({'TCMPR_PLOTTER_PLOT_CONFIG_OPTS': 'my_string'},
         '-plot_config my_string'),
        ({'TCMPR_PLOTTER_SAVE_DATA': 'my_string'}, '-save_data my_string'),
        # booleans True
        ({'TCMPR_PLOTTER_FOOTNOTE_FLAG': 'True'}, '-footnote_flag'),
        ({'TCMPR_PLOTTER_NO_EE': 'True'}, '-no_ee'),
        ({'TCMPR_PLOTTER_NO_LOG': 'True'}, '-no_log'),
        ({'TCMPR_PLOTTER_SAVE': 'True'}, '-save'),
        # booleans False
        ({'TCMPR_PLOTTER_FOOTNOTE_FLAG': 'False'}, ''),
        ({'TCMPR_PLOTTER_NO_EE': 'False'}, ''),
        ({'TCMPR_PLOTTER_NO_LOG': 'False'}, ''),
        ({'TCMPR_PLOTTER_SAVE': 'False'}, ''),
        # strings add quotes
        ({'TCMPR_PLOTTER_TITLE': 'my_string'}, '-title "my_string"'),
        ({'TCMPR_PLOTTER_SUBTITLE': 'my_string'}, '-subtitle "my_string"'),
        ({'TCMPR_PLOTTER_XLAB': 'my_string'}, '-xlab "my_string"'),
        ({'TCMPR_PLOTTER_YLAB': 'my_string'}, '-ylab "my_string"'),
        ({'TCMPR_PLOTTER_FILTER': '-amodel GFSO,EMX,CMC'},
         '-filter "-amodel GFSO,EMX,CMC"'),
        ({'TCMPR_PLOTTER_LEGEND': 'my_string'}, '-legend "my_string"'),
        # looped arguments (single item)
        ({'TCMPR_PLOTTER_DEP_VARS': 'item1'}, '-dep item1'),
        ({'TCMPR_PLOTTER_PLOT_TYPES': 'item1'}, '-plot item1'),
    ]
)
@pytest.mark.plotting
def test_tcmpr_plotter(metplus_config, config_overrides, expected_string):
    # add a space before value if expected string has a value
    if expected_string:
        expected_string = f' {expected_string}'

    for single_file in [True, False]:
        config = metplus_config

        set_minimum_config_settings(config)

        # set config variable overrides
        for key, value in config_overrides.items():
            config.set('config', key, value)

        test_data = os.path.join(config.getdir('METPLUS_BASE'),
                                 'internal', 'tests',
                                 'data',
                                 'stat_data')
        if single_file:
            test_data = os.path.join(test_data, 'fake_filter_20141214_00.tcst')

        config.set('config', 'TCMPR_PLOTTER_TCMPR_DATA_DIR', test_data)

        wrapper = TCMPRPlotterWrapper(config)
        assert wrapper.isOK

        app_path = wrapper.c_dict.get('TCMPR_SCRIPT')
        config_file = wrapper.c_dict.get('CONFIG_FILE')
        out_dir = wrapper.c_dict.get('OUTPUT_DIR')

        input_files = []
        if single_file:
            input_files.append(test_data)
        else:
            for input_file in EXPECTED_INPUT_FILES:
                input_files.append(os.path.join(test_data, input_file))

        expected_cmds = [(f"Rscript {app_path} -config {config_file}"
                          f"{expected_string}"
                          f" -lookin {' '.join(input_files)}"
                          f" -outdir {out_dir}"),
                         ]

        all_cmds = wrapper.run_all_times()
        print(f"ALL COMMANDS: {all_cmds}")

        for (actual_cmd, _), expected_cmd in zip(all_cmds, expected_cmds):
            # ensure commands are generated as expected
            assert actual_cmd == expected_cmd
