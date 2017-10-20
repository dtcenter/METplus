#!/usr/bin/env python

'''
Program Name: grid_stat_wrapper.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
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
from command_builder import CommandBuilder
from pcp_combine_wrapper import PcpCombineWrapper
from gempak_to_cf_wrapper import GempakToCFWrapper
from task_info import TaskInfo
import string_template_substitution as sts


class GridStatWrapper(CommandBuilder):

    def __init__(self, p, logger):
        super(GridStatWrapper, self).__init__(p, logger)
        met_build_base = p.getdir('MET_BUILD_BASE')
        self.app_path = os.path.join(met_build_base, 'bin/grid_stat')
        self.app_name = os.path.basename(self.app_path)

    def set_output_dir(self, outdir):
        self.outdir = "-outdir "+outdir

    def get_command(self):
        if self.app_path is None:
            self.logger.error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            self.logger.error(self.app_name+": No input filenames specified")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.param != "":
            cmd += self.param + " "

        if self.outdir == "":
            self.logger.error(self.app_name+": No output directory specified")
            return None

        cmd += self.outdir
        return cmd

    def find_model(self, model_type, lead, init_time):
        model_dir = self.p.getstr('config', model_type+'_INPUT_DIR')
        #  max_forecast = self.p.getint('config', model_type+'_MAX_FORECAST')
        forecasts = model_type+'_FORECASTS'
        max_forecast = util.getlistint(self.p.getstr('config', forecasts))[-1]
        init_interval = self.p.getint('config', model_type+'_INIT_INTERVAL')
        lead_check = lead
        time_check = init_time
        time_offset = 0
        found = False
        while lead_check <= max_forecast:
            native_template = self.p.getraw('filename_templates',
                                            model_type+'_NATIVE_TEMPLATE')
            model_ss = sts.StringSub(self.logger, native_template,
                                     init=time_check,
                                     lead=str(lead_check).zfill(2))
            model_file = model_ss.doStringSub()
            print("model file: "+model_file)
            model_path = os.path.join(model_dir, model_file)
            if os.path.exists(model_path):
                found = True
                break

            time_check = util.shift_time(time_check, -init_interval)
            lead_check = lead_check + init_interval

        if found:
            return model_path
        else:
            return ''

    def run_at_time(self, init_time):
        task_info = TaskInfo()
        task_info.init_time = init_time
        fcst_vars = util.getlist(self.p.getstr('config', 'FCST_VARS'))
        lead_seq = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))        
        for lead in lead_seq:
            task_info.lead = lead
            task_info.valid_time = -1
            for fcst_var in fcst_vars:
                task_info.fcst_var = fcst_var
                # loop over models to compare
                accums = util.getlist(self.p.getstr('config', fcst_var+"_ACCUM"))
                ob_types = util.getlist(self.p.getstr('config', fcst_var+"_OBTYPE"))
                for accum in accums:
                    task_info.level = accum
                    for ob_type in ob_types:
                        task_info.ob_type = ob_type
                        if lead < int(accum):
                            continue
                        self.run_at_time_once(task_info)


#    def run_at_time_fcst(self, init_time, lead, accum, ob_type, fcst_var):
    def run_at_time_once(self, ti):
        grid_stat_out_dir = self.p.getstr('config', 'GRID_STAT_OUT_DIR')
#        valid_time = util.shift_time(ti.init_time, ti.lead)
        valid_time = ti.getValidTime()
        init_time = ti.getInitTime()
        accum = ti.level
        model_type = self.p.getstr('config', 'MODEL_TYPE')
        regrid_dir = self.p.getstr('config', ti.ob_type+'_REGRID_DIR')
        regrid_template = self.p.getraw('filename_templates',
                                        ti.ob_type+'_REGRID_TEMPLATE')
        model_bucket_dir = self.p.getstr('config', model_type+'_BUCKET_DIR')
        obs_var = self.p.getstr('config', ti.ob_type+"_VAR")
        config_dir = self.p.getstr('config', 'CONFIG_DIR')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(grid_stat_out_dir,
                                           init_time, "grid_stat")):
            os.makedirs(os.path.join(grid_stat_out_dir,
                                     init_time, "grid_stat"))
        if not os.path.exists(os.path.join(model_bucket_dir, ymd_v)):
            os.makedirs(os.path.join(model_bucket_dir, ymd_v))

        # get model to compare
        model_dir = self.p.getstr('config', model_type+'_INPUT_DIR')
        # check if accum exists in forecast file
        # If not, run pcp_combine to create it
        # TODO: remove reliance on model_type
        if model_type == 'HREF_MEAN' or model_type == "NATIONAL_BLEND":
            native_dir = self.p.getstr('config', model_type+'_NATIVE_DIR')
            run_pcp_ob = PcpCombineWrapper(self.p, self.logger)
#            run_pcp_ob.run_at_time(valid_time, int(accum),
#                                   model_type, fcst_var, True)
            #      valid_time = util.shift_time(init_time, lead)
            run_pcp_ob.set_input_dir(model_dir)

            run_pcp_ob.set_output_dir(model_bucket_dir)
#            run_pcp_ob.get_accumulation(valid_time, int(accum),
            run_pcp_ob.get_accumulation(valid_time, accum,
                                        model_type, True)

            #  call GempakToCF if native file doesn't exist
            infiles = run_pcp_ob.get_input_files()
            for idx, infile in enumerate(infiles):
                # replace input_dir with native_dir, check if file exists
                nfile = infile.replace(model_dir, native_dir)
                if not os.path.exists(os.path.dirname(nfile)):
                    os.makedirs(os.path.dirname(nfile))
                data_type = self.p.getstr('config',
                                          ti.ob_type+'_NATIVE_DATA_TYPE')
                if data_type == "NETCDF":
                    nfile = os.path.splitext(nfile)[0]+'.nc'

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

                    run_pcp_ob.infiles[idx] = nfile

            bucket_template = self.p.getraw('filename_templates',
                                            model_type+'_BUCKET_TEMPLATE')
            pcpSts = sts.StringSub(self.logger,
                                   bucket_template,
                                   valid=valid_time,
                                   accum=str(ti.level).zfill(2))
            pcp_out = pcpSts.doStringSub()
            run_pcp_ob.set_output_filename(pcp_out)
            run_pcp_ob.add_arg("-name "+ti.fcst_var+"_"+ti.level)

            cmd = run_pcp_ob.get_command()
            if cmd is None:
                print("ERROR: pcp_combine observation could not "\
                      "generate command")
                return
            print("RUNNING: "+str(cmd))
            self.logger.info("")
            run_pcp_ob.build()
            model_path = run_pcp_ob.get_output_path()
        else:
            model_path = self.find_model(model_type, ti.lead, init_time)

        if model_path == "":
            print("ERROR: COULD NOT FIND FILE IN "+model_dir)
            return
        self.add_input_file(model_path)
        regridSts = sts.StringSub(self.logger,
                                  regrid_template,
                                  valid=valid_time,
                                  accum=str(accum).zfill(2))
        regrid_file = regridSts.doStringSub()

        regrid_path = os.path.join(regrid_dir, regrid_file)
        self.add_input_file(regrid_path)
        if self.p.getbool('config', model_type+'_IS_PROB'):
            self.set_param_file(self.p.getstr('config', 'MET_CONFIG_GSP'))
        else:
            self.set_param_file(self.p.getstr('config', 'MET_CONFIG_GSM'))
        self.set_output_dir(os.path.join(grid_stat_out_dir,
                                         init_time, "grid_stat"))

        # set up environment variables for each grid_stat run
        # get fcst and obs thresh parameters
        # verify they are the same size
        fcst_str = model_type+"_"+ti.fcst_var+"_"+accum+"_THRESH"
        fcst_threshs = util.getlistfloat(self.p.getstr('config', fcst_str))
        obs_str = ti.ob_type+"_"+ti.fcst_var+"_"+accum+"_THRESH"
        obs_threshs = util.getlistfloat(self.p.getstr('config', obs_str))
        if len(fcst_threshs) != len(obs_threshs):
            self.logger.error("run_example: Number of forecast and "\
                              "observation thresholds must be the same")
            exit

        fcst_field = ""
        obs_field = ""

        if self.p.getbool('config', model_type+'_IS_PROB'):
            for fcst_thresh in fcst_threshs:
                fcst_field += "{ name=\"PROB\"; level=\"A"+accum + \
                              "\"; prob={ name=\""+ti.fcst_var + \
                              "\"; thresh_lo="+str(fcst_thresh)+"; } },"
            for obs_thresh in obs_threshs:
                obs_field += "{ name=\""+obs_var+"_"+accum + \
                             "\"; level=\"(*,*)\"; cat_thresh=[ gt" + \
                             str(obs_thresh)+" ]; },"
        else:
            data_type = self.p.getstr('config', ti.ob_type+'_NATIVE_DATA_TYPE')
            if data_type == "NETCDF":
              fcst_field += "{ name=\""+ti.fcst_var+"_"+accum + \
                            "\"; level=\"(*,*)\"; cat_thresh=["
            else:
              fcst_field += "{ name=\""+ti.fcst_var + \
                            "\"; level=\"[A"+accum.zfill(2)+"]\"; cat_thresh=["                
            for fcst_thresh in fcst_threshs:
                fcst_field += "gt"+str(fcst_thresh)+", "
            fcst_field = fcst_field[0:-2]
            fcst_field += " ]; },"

            obs_field += "{ name=\"" + obs_var+"_" + accum + \
                         "\"; level=\"(*,*)\"; cat_thresh=[ "
            for obs_thresh in obs_threshs:
                obs_field += "gt"+str(obs_thresh)+", "
            obs_field = obs_field[0:-2]
            obs_field += " ]; },"
        # remove last comma
        fcst_field = fcst_field[0:-1]
        obs_field = obs_field[0:-1]

        self.add_env_var("MODEL", model_type)
        self.add_env_var("FCST_VAR", ti.fcst_var)
        self.add_env_var("OBS_VAR", obs_var)
        self.add_env_var("ACCUM", accum)
        self.add_env_var("OBTYPE", ti.ob_type)
        self.add_env_var("CONFIG_DIR", config_dir)
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        cmd = self.get_command()

        self.logger.debug("")
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_item("MODEL")
        self.print_env_item("FCST_VAR")
        self.print_env_item("OBS_VAR")
        self.print_env_item("ACCUM")
        self.print_env_item("OBTYPE")
        self.print_env_item("CONFIG_DIR")
        self.print_env_item("FCST_FIELD")
        self.print_env_item("OBS_FIELD")
        self.logger.debug("")
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(["MODEL", "FCST_VAR", "OBS_VAR",
                             "ACCUM", "OBTYPE", "CONFIG_DIR",
                             "FCST_FIELD", "OBS_FIELD"])
        self.logger.debug("")
        cmd = self.get_command()
        if cmd is None:
            print("ERROR: grid_stat (observation) could not generate command")
            return
        print("RUNNING: "+str(cmd))
        self.logger.info("")
        self.build()
        self.clear()
