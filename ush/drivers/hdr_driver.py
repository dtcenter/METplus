#! /usr/bin/env python3

import sys
import os

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir)))

from metplus.util import pre_run_setup
from metplus.wrappers import GridStatWrapper

import parm.use_cases.model_applications.tc_and_extra_tc.tdr_utils as tdr_utils

if len(sys.argv) < 2:
    print("Must supply config files as arguments to script")
    sys.exit(1)

mission_ids = sys.argv[1].split(',')
print(f"Config args: {sys.argv[2:]}")
config_args = sys.argv[2:]

config = pre_run_setup(config_args)

tc_radar_file = config.getstr('config', 'TC_RADAR_FILE')

log_file = config.getstr('config', 'LOG_METPLUS')
print(f"Logging to {log_file}")

for mission_id in mission_ids:
    print(f"Processing mission ID: {mission_id}")
    config.set('config', 'CUSTOM_LOOP_LIST', mission_id)
    valid_time = tdr_utils.get_valid_time(tc_radar_file, mission_id)
    print(f"VALID TIME: {valid_time}")

    config.set('config', 'VALID_BEG', valid_time)
    config.set('config', 'VALID_END', valid_time)
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d%H%M')

    grid_stat_wrapper = GridStatWrapper(config)
    grid_stat_wrapper.run_all_times()
