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


class PcpCombineModelWrapper(PcpCombineWrapper):
    def __init__(self, p, logger):
        super(PcpCombineModelWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/pcp_combine')
        self.app_name = os.path.basename(self.app_path)
        self.inaddons = []

    def clear(self):
        super(PcpCombineModelWrapper, self).clear()
        self.inaddons = []


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
                levels = util.getlist(self.p.getstr('config', fcst_var+"_LEVEL"))
                for level in levels:
                    task_info.level = level
                    if lead < int(level):
                        continue
                    self.run_at_time_once(task_info.getValidTime(),
                                          task_info.level,
                                          task_info.fcst_var)

    # NOTE: Currently expects Gempak data to exist in *_GEMPAK_INPUT_DIR
    #  If NetCDF output from GempakToCF exists, GempakToCF will not run
    #  if data is already in NetCDF or GRIB format, set _GEMPAK_INPUT_DIR
    # to the same directory as _PCP_COMBINE_INPUT_DIR 
    def run_at_time_once(self, valid_time, accum,
                         fcst_var, is_forecast=False):
        self.clear()
        model_type = self.p.getstr('config', 'MODEL_TYPE')        
        input_dir = self.p.getstr('config',
                                      model_type+'_PCP_COMBINE_INPUT_DIR')
        input_template = self.p.getraw('filename_templates',
                                      model_type+'_PCP_COMBINE_INPUT_TEMPLATE')        

        model_bucket_dir = self.p.getstr('config',
                                         model_type+'_PCP_COMBINE_OUTPUT_DIR')
        
        if not os.path.exists(os.path.join(model_bucket_dir,valid_time[0:8])):
          os.makedirs(os.path.join(model_bucket_dir,valid_time[0:8]))

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.set_input_dir(input_dir)
        if self.get_accumulation(valid_time, accum, model_type, input_template, True) is True:
            # if success, run pcp_combine            
            infiles = self.get_input_files()            
        else:
            # if failure, check _GEMPAK_INPUT_DIR to get accumulation files

            if not self.p.hasoption('config', model_type + '_GEMPAK_INPUT_DIR') or \
               not self.p.hasoption('filename_templates', model_type + '_GEMPAK_TEMPLATE'):
                self.logger.warning(self.app_name + ": Could not find " \
                                    "files to compute accumulation in " \
                                    + input_dir)
                return False            
            gempak_dir = self.p.getstr('config', model_type+'_GEMPAK_INPUT_DIR')
            gempak_template = self.p.getraw('filename_templates', model_type+'_GEMPAK_TEMPLATE')                 
            self.set_input_dir(gempak_dir)
            if self.get_accumulation(valid_time, accum,
                              model_type, gempak_template, True) is True:
                # if success, run GempakToCF, run pcp_combinae
               infiles = self.get_input_files()
               for idx, infile in enumerate(infiles):
                    # replace gempak_dir with pcp_input_dir, check if file exists
                    nfile = infile.replace(gempak_dir, input_dir)
                    if not os.path.exists(os.path.dirname(nfile)):
                        os.makedirs(os.path.dirname(nfile))
                    data_type = self.p.getstr('config',
                                              model_type+'_NATIVE_DATA_TYPE')
                    if data_type == "NETCDF":
                        nfile = os.path.splitext(nfile)[0]+'.nc'
                        # call GempakToCF if pcp input file doesn't exist
                        if not os.path.isfile(nfile):
                            print("Calling GempakToCF to convert model to NetCDF")
                            run_g2c = GempakToCFWrapper(self.p, self.logger)
                            run_g2c.add_input_file(infile)
                            run_g2c.set_output_path(nfile)
                            cmd = run_g2c.get_command()
                            if cmd is None:
                                print("ERROR: GempakToCF could not generate command")
                                return
                            print("RUNNING: "+str(cmd))
                            run_g2c.build()

                    self.infiles[idx] = nfile

        bucket_template = self.p.getraw('filename_templates',
                                        model_type+'_PCP_COMBINE_OUTPUT_TEMPLATE')
#        bucket_template = self.p.getraw('filename_templates',
#                                            model_type+'_BUCKET_TEMPLATE')        
        pcpSts = sts.StringSub(self.logger,
                                bucket_template,
                                valid=valid_time,
                                level=str(accum).zfill(2))
        pcp_out = pcpSts.doStringSub()
        self.set_output_dir(model_bucket_dir)        
        self.set_output_filename(pcp_out)
        self.add_arg("-name "+fcst_var+"_"+accum)

        cmd = self.get_command()
        if cmd is None:
            print("ERROR: pcp_combine model could not "\
                    "generate command")
            return
        self.logger.info("")
        self.build()
