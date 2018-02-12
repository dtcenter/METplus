#!/usr/bin/env python

'''
Program Name: pcp_combine_model_wrapper.py
Contact(s): George McCabe
Abstract: Runs pcp_combine to merge multiple forecast files
History Log:  Initial version
Usage:
Parameters: None
Input Files: grib2 files
Output Files: pcp_combine files
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import produtil.setup
from produtil.run import batchexe, run, checkrun
import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
import glob
import datetime
import string_template_substitution as sts

from command_builder import CommandBuilder
from pcp_combine_wrapper import PcpCombineWrapper
from task_info import TaskInfo
from gempak_to_cf_wrapper import GempakToCFWrapper


class PcpCombineObsWrapper(PcpCombineWrapper):
    def __init__(self, p, logger):
        super(PcpCombineObsWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/pcp_combine')
        self.app_name = os.path.basename(self.app_path)
        self.inaddons = []

    def clear(self):
        super(PcpCombineObsWrapper, self).clear()
        self.inaddons = []


    def run_at_time(self, init_time):
        task_info = TaskInfo()
        task_info.init_time = init_time
        compare_vars = util.getlist(self.p.getstr('config', 'VAR_LIST'))
        lead_seq = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))
        for lead in lead_seq:
            task_info.lead = lead
            for compare_var in compare_vars:
                var_name, accum = compare_var.split("/")
                if lead < int(accum[1:]):
                    print("Lead "+str(lead)+" is less than accum "+accum[1:])
                    print("Skipping...")
                    continue
                vt = task_info.getValidTime()
                self.run_at_time_once(task_info.getValidTime(),
                                      accum[1:],
                                      var_name)

    def run_at_time_once(self, valid_time, accum,
                         compare_var, is_forecast=False):
        self.clear()
        
        input_dir = self.p.getstr('config', 'OBS_PCP_COMBINE_INPUT_DIR')
        input_template = self.p.getraw('filename_templates', 'OBS_PCP_COMBINE_INPUT_TEMPLATE')
        bucket_dir = self.p.getstr('config', 'OBS_PCP_COMBINE_OUTPUT_DIR')
        bucket_template = self.p.getraw('filename_templates',
                                        'OBS_PCP_COMBINE_OUTPUT_TEMPLATE')


        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(bucket_dir, ymd_v)):
            os.makedirs(os.path.join(bucket_dir, ymd_v))

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.set_input_dir(input_dir)
        if self.get_accumulation(valid_time[0:10], int(accum), "OBS", input_template, is_forecast) is True:
            # if success, run pcp_combine            
            infiles = self.get_input_files()            
        else:
            # if failure, check _GEMPAK_INPUT_DIR to get accumulation files
            if not self.p.has_option('config', 'OBS_GEMPAK_INPUT_DIR') or \
              not self.p.has_option('filename_templates', 'OBS_GEMPAK_TEMPLATE'):
                self.logger.warning(self.app_name + ": Could not find " \
                                    "files to compute accumulation in " \
                                    + input_dir)
                return False
            gempak_dir = self.p.getstr('config', 'OBS_GEMPAK_INPUT_DIR')
            gempak_template = self.p.getraw('filename_templates', 'OBS_GEMPAK_TEMPLATE')
            self.clear()
            self.set_input_dir(gempak_dir)
            if self.get_accumulation(valid_time[0:10], int(accum), "OBS", gempak_template, is_forecast) is True:
                #   if success, run GempakToCF, run pcp_combine
                if not os.path.exists(os.path.join(input_dir, ymd_v)):
                    os.makedirs(os.path.join(input_dir, ymd_v))
                infiles = self.get_input_files()
                for idx, infile in enumerate(infiles):
                    # replace input_dir with native_dir, check if file exists
                    nfile = infile.replace(gempak_dir, input_dir)
                    data_type = self.p.getstr('config', 'OBS_NATIVE_DATA_TYPE')
                    if data_type == "NETCDF":
                        nfile = os.path.splitext(nfile)[0] + '.nc'
                        if not os.path.isfile(nfile):
                            print("Calling GempakToCF to convert to NetCDF")
                            run_g2c = GempakToCFWrapper(self.p, self.logger)
                            run_g2c.add_input_file(infile)
                            run_g2c.set_output_path(nfile)
                            cmd = run_g2c.get_command()
                            if cmd is None:
                                print("ERROR: GempakToCF could not generate command")
                                continue
                            run_g2c.build()
                    infiles[idx] = nfile

            else:
                #   if failure, quit
                self.logger.warning(self.app_name + ": Could not find " \
                                    "files to compute accumulation in " \
                                    + gempak_dir)
                return None

        self.set_output_dir(bucket_dir)                        
        pcpSts = sts.StringSub(self.logger,
                                bucket_template,
                                valid=valid_time,
                                level=str(accum).zfill(2))
        pcp_out = pcpSts.doStringSub()
        self.set_output_filename(pcp_out)
        self.add_arg("-name " + compare_var + "_" + accum)
        cmd = self.get_command()
        if cmd is None:
            print("ERROR: pcp_combine could not generate command")
            return
        self.logger.info("")
        self.build()
        outfile = self.get_output_path()
        return outfile
