#!/usr/bin/env python3

import pytest

import os

from metplus.wrappers.plot_data_plane_wrapper import PlotDataPlaneWrapper

obs_dir = '/some/path/obs'
input_template_one = (
    'pb2nc/ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr.tm00.nc'
)
input_template_two = (
    'pb2nc/ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr.tm00.nc,'
    'ascii2nc/trmm_{valid?fmt=%Y%m%d%H}_3hr.nc'
)

grid_dir = '/some/path/grid'
grid_template = 'nam_{init?fmt=%Y%m%d%H}_F{lead?fmt=%3H}.grib2'

output_dir = '{OUTPUT_BASE}/plot_point_obs'
output_template = 'nam_and_ndas.{valid?fmt=%Y%m%d}.t{valid?fmt=%H}z.prepbufr_CONFIG.ps'

title = 'NAM 2012040900 F12 vs NDAS 500mb RH and TRMM 3h > 0'

point_data = ['{msg_typ = "ADPSFC";obs_gc = 61;obs_thresh = > 0.0;'
              'fill_color = [0,0,255];}',
              '{msg_typ = "ADPSFC";obs_var = "RH";'
              'fill_color = [100,100,100];}']
point_data_input = ', '.join(point_data)
point_data_format = f"[{point_data_input}];"

time_fmt = '%Y%m%d%H'
run_times = ['2012040912', '2012041000']


@pytest.mark.parametrize(
    'missing, run, thresh, errors, allow_missing', [
        (6, 12, 0.5, 0, True),
        (6, 12, 0.6, 1, True),
        (6, 12, 0.5, 6, False),
    ]
)
@pytest.mark.wrapper_c
def test_plot_data_plane_missing_inputs(metplus_config, get_test_data_dir,
                                        missing, run, thresh, errors,
                                        allow_missing):
    config = metplus_config
    config.set('config', 'DO_NOT_RUN_EXE', True)
    config.set('config', 'INPUT_MUST_EXIST', True)

    config.set('config', 'PROCESS_LIST', 'PlotDataPlane')
    config.set('config', 'PLOT_DATA_PLANE_ALLOW_MISSING_INPUTS', allow_missing)
    config.set('config', 'PLOT_DATA_PLANE_INPUT_THRESH', thresh)
    config.set('config', 'LOOP_BY', 'INIT')
    config.set('config', 'INIT_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'INIT_BEG', '2017051001')
    config.set('config', 'INIT_END', '2017051003')
    config.set('config', 'INIT_INCREMENT', '2H')
    config.set('config', 'LEAD_SEQ', '1,2,3,6,9,12')
    config.set('config', 'PLOT_DATA_PLANE_INPUT_DIR', get_test_data_dir('fcst'))
    config.set('config', 'PLOT_DATA_PLANE_INPUT_TEMPLATE',
               '{init?fmt=%Y%m%d}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.grb2')
    config.set('config', 'PLOT_DATA_PLANE_OUTPUT_TEMPLATE',
               '{OUTPUT_BASE}/{init?fmt=%Y%m%d_i%H}_f{lead?fmt=%3H}_HRRRTLE_PHPT.ps')
    config.set('config', 'PLOT_DATA_PLANE_FIELD_NAME', 'APCP_12')

    wrapper = PlotDataPlaneWrapper(config)
    assert wrapper.isOK

    all_cmds = wrapper.run_all_times()
    for cmd, _ in all_cmds:
        print(cmd)

    print(f'missing: {wrapper.missing_input_count} / {wrapper.run_count}, errors: {wrapper.errors}')
    assert wrapper.missing_input_count == missing
    assert wrapper.run_count == run
    assert wrapper.errors == errors
