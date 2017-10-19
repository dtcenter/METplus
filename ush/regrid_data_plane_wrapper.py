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
        self.app_path = os.path.join(self.p.getdir('MET_BUILD_BASE'),
                                     'bin/regrid_data_plane')
        self.app_name = os.path.basename(self.app_path)

    def run_at_time(self, init_time):
        task_info = TaskInfo()
        task_info.init_time = init_time
        fcst_vars = util.getlist(self.p.getstr('config', 'FCST_VARS'))
        lead_seq = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))
        for lead in lead_seq:
            task_info.lead = lead
            for fcst_var in fcst_vars:
                task_info.fcst_var = fcst_var
                # loop over models to compare
                accums = util.getlist(
                    self.p.getstr('config', fcst_var + "_ACCUM"))
                ob_types = util.getlist(
                    self.p.getstr('config', fcst_var + "_OBTYPE"))
                for accum in accums:
                    task_info.level = accum
                    for ob_type in ob_types:
                        task_info.ob_type = ob_type
                        if lead < int(accum):
                            continue
                        #                        self.run_at_time_fcst(task_info)
                        self.run_at_time_once(task_info.getValidTime(),
                                              task_info.level,
                                              task_info.ob_type)

    def run_at_time_once(self, valid_time, accum, ob_type):
        obs_var = self.p.getstr('config', ob_type + "_VAR")
        bucket_dir = self.p.getstr('config', ob_type + '_BUCKET_DIR')
        bucket_template = self.p.getraw('filename_templates',
                                        ob_type + '_BUCKET_TEMPLATE')
        regrid_dir = self.p.getstr('config', ob_type + '_REGRID_DIR')
        regrid_template = self.p.getraw('filename_templates',
                                        ob_type + '_REGRID_TEMPLATE')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(regrid_dir, ymd_v)):
            os.makedirs(os.path.join(regrid_dir, ymd_v))

        pcpSts = sts.StringSub(self.logger,
                               bucket_template,
                               valid=valid_time,
                               accum=str(accum).zfill(2))
        outfile = os.path.join(bucket_dir, pcpSts.doStringSub())

        self.add_input_file(outfile)
        self.add_input_file(self.p.getstr('config', 'VERIFICATION_GRID'))
        regridSts = sts.StringSub(self.logger,
                                  regrid_template,
                                  valid=valid_time,
                                  accum=str(accum).zfill(2))
        regrid_file = regridSts.doStringSub()
        self.set_output_path(os.path.join(regrid_dir, regrid_file))
        field_name = "{:s}_{:s}".format(obs_var, str(accum).zfill(2))
        self.add_arg("-field 'name=\"{:s}\"; level=\"(*,*)\";'".format(
            field_name))
        self.add_arg("-method BUDGET")
        self.add_arg("-width 2")
        self.add_arg("-name " + field_name)
        cmd = self.get_command()
        if cmd is None:
            print("ERROR: regrid_data_plane could not generate command")
            return
        print("RUNNING: " + str(cmd))
        self.logger.info("")
        self.build()
        self.clear()
