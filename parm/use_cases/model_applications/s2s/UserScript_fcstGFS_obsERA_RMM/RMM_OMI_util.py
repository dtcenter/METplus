import os
import numpy as np
from metplus.util import pre_run_setup, config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate, do_string_sub


def find_input_files(datetime_dictlist, inconfig, intemplate):
    template = inconfig.getraw('config',intemplate)

    file_list = []
    for outtime in datetime_dictlist:
        filepath = do_string_sub(template, **outtime)
        if os.path.exists(filepath):
            file_list.append(filepath)
        else:
            file_list.append('')

    if all('' == fn for fn in file_list):
        raise IOError('No input files found as given: '+template)

    return file_list


def find_times(inconfig, use_init):
    loop_time, end_time, time_interval = get_start_end_interval_times(inconfig)
    skip_times = get_skip_times(inconfig)

    datetime_list = []
    if use_init:
        timname = 'init'
    else:
        timname = 'valid'
    input_dict = {}
    input_dict['loop_by'] = timname
    while loop_time <= end_time:
        lead_seq = get_lead_sequence(inconfig)
        for ls in lead_seq:
            new_time = loop_time + ls
            input_dict[timname] = loop_time
            input_dict['lead'] = ls

            outtime = ti_calculate(input_dict)
            if skip_time(outtime, skip_times):
                continue
            datetime_list.append(outtime)

        loop_time += time_interval

    return datetime_list


def compute_plot_times(inconfig,use_init):
    if use_init:
        inconfig.set('compute_rmm','INIT_BEG',inconfig.getstr('compute_rmm','TIMESERIES_PLOT_INIT_BEG'))
        inconfig.set('compute_rmm','INIT_END',inconfig.getstr('compute_rmm','TIMESERIES_PLOT_INIT_END'))
    else:
        inconfig.set('compute_rmm','VALID_BEG',inconfig.getstr('compute_rmm','TIMESERIES_PLOT_VALID_BEG'))
        inconfig.set('compute_rmm','VALID_END',inconfig.getstr('compute_rmm','TIMESERIES_PLOT_VALID_END'))

    pltconfig = config_metplus.replace_config_from_section(inconfig,'compute_rmm')
    plot_alltimes = find_times(pltconfig, use_init)
    plot_time = np.array([t_obj2['valid'] for t_obj2 in plot_alltimes],dtype='datetime64')
    months = [t_obj2['valid'].month for t_obj2 in plot_alltimes]
    days = [t_obj2['valid'].day for t_obj2 in plot_alltimes]
    ntim_plot = len(plot_time)

    return plot_time, months, days, ntim_plot

