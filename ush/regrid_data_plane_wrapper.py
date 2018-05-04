#!/usr/bin/env python

'''
Program Name: regrid_data_plane.py
Contact(s): George McCabe
Abstract: Runs regrid_data_plane
History Log:  Initial version
Usage: 
Parameters: None
Input Files: nc files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
import string_template_substitution as sts
from task_info import TaskInfo
from command_builder import CommandBuilder


class RegridDataPlaneWrapper(CommandBuilder):
    def __init__(self, p, logger):
        super(RegridDataPlaneWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/regrid_data_plane')
        self.app_name = os.path.basename(self.app_path)

    def run_at_time(self, init_time, valid_time):
        task_info = TaskInfo()
        task_info.init_time = init_time
        task_info.valid_time = valid_time
        var_list = util.parse_var_list(self.p)        
        lead_seq = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))
        for lead in lead_seq:
            task_info.lead = lead
            task_info.valid_time = -1
            for var_info in var_list:
                level = var_info.obs_level
                if level[0].isalpha():
                    level = var_info.obs_level[1:]                       
                self.run_at_time_once(task_info.getValidTime(),
                                      level, var_info.obs_name)


    def run_at_time_once(self, valid_time, level, compare_var):
        bucket_dir = self.p.getdir('OBS_REGRID_DATA_PLANE_INPUT_DIR')
        input_template = self.p.getraw('filename_templates',
                                        'OBS_REGRID_DATA_PLANE_TEMPLATE')
        regrid_dir = self.p.getdir('OBS_REGRID_DATA_PLANE_OUTPUT_DIR')
        regrid_template = self.p.getraw('filename_templates',
                                        'OBS_REGRID_DATA_PLANE_TEMPLATE')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(regrid_dir, ymd_v)):
            os.makedirs(os.path.join(regrid_dir, ymd_v))

        pcpSts = sts.StringSub(self.logger,
                               input_template,
                               valid=valid_time,
                               level=str(level).zfill(2))
        outfile = os.path.join(bucket_dir, pcpSts.doStringSub())

        self.add_input_file(outfile)
        self.add_input_file(self.p.getstr('config', 'VERIFICATION_GRID'))
        regridSts = sts.StringSub(self.logger,
                                  regrid_template,
                                  valid=valid_time,
                                  level=str(level).zfill(2))
        regrid_file = regridSts.doStringSub()
        self.set_output_path(os.path.join(regrid_dir, regrid_file))
        field_name = "{:s}_{:s}".format(compare_var, str(level).zfill(2))
        self.add_arg("-field 'name=\"{:s}\"; level=\"(*,*)\";'".format(
            field_name))
        self.add_arg("-method BUDGET")
        self.add_arg("-width 2")
        self.add_arg("-name " + field_name)
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("regrid_data_plane could not generate command")
            return
        self.logger.info("")
        self.build()
        self.clear()
