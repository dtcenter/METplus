#!/usr/bin/env python

'''
Program Name: compare_gridded_wrapper.py
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
import datetime
import glob
from command_builder import CommandBuilder
from task_info import TaskInfo
import string_template_substitution as sts

'''!@namespace CompareGriddedWrapper
@brief Common functionality to wrap similar MET applications
that compare gridded data
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''
class CompareGriddedWrapper(CommandBuilder):
    """!Common functionality to wrap similar MET applications
that reformat gridded data
    """
    def __init__(self, p, logger):
        super(CompareGriddedWrapper, self).__init__(p, logger)
        met_install_dir = p.getdir('MET_INSTALL_DIR')
        self.cg_dict = self.create_cg_dict()


    def set_output_dir(self, outdir):
        """! Sets the output directory
              Args:
                @param outdir directory to set
        """        
        self.outdir = "-outdir "+outdir


    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
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

    def find_model(self, ti, v):
        """! Finds the model file to compare
              Args:
                @param lead forecast lead value
                @param init_time initialization time
                @param level
                @rtype string
                @return Returns the path to a model file
        """
        lead = ti.getLeadTime()
        init_time = ti.getInitTime()
        level_type, level = self.split_level(v.fcst_level)
        model_dir = self.cg_dict['FCST_INPUT_DIR']
        model_template = self.cg_dict['FCST_INPUT_TEMPLATE']
        max_forecast = self.cg_dict['FCST_MAX_FORECAST']
        init_interval = self.cg_dict['FCST_INIT_INTERVAL']
        lead_check = lead
        time_check = init_time
        time_offset = 0
        found = False
        while lead_check <= max_forecast:
            # split by - to handle a level that is a range, such as 0-10
            model_ss = sts.StringSub(self.logger, model_template,
                                     init=time_check,
                                     lead=str(lead_check).zfill(2),
                                     level=str(level.split('-')[0]).zfill(2))
            model_file = model_ss.doStringSub()
            model_path = os.path.join(model_dir, model_file)
            model_path = util.preprocess_file(model_path,
                                              self.p.getdir('STAGING_DIR'),
                                              self.p, self.logger)
            if model_path != None:
                found = True
                break

            time_check = util.shift_time(time_check, -init_interval)
            lead_check = lead_check + init_interval            

        if found:
            return model_path
        else:
            return ''


    def find_obs(self, ti, v):
        """! Finds the observation file to compare
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @rtype string
                @return Returns the path to an observation file
        """
        valid_time = ti.getValidTime()
        init_time = ti.getInitTime()
        obs_level_type, obs_level = self.split_level(v.obs_level)
        obs_template = self.cg_dict['OBS_INPUT_TEMPLATE']
        obs_dir = self.cg_dict['OBS_INPUT_DIR']
        if self.cg_dict['OBS_EXACT_VALID_TIME']:
            obsSts = sts.StringSub(self.logger,
                                   obs_template,
                                   valid=valid_time,
                                   init=init_time,
                                   level=str(obs_level.split('-')[0]).zfill(2))
            obs_file = obsSts.doStringSub()

            obs_path = os.path.join(obs_dir, obs_file)
            obs_path = util.preprocess_file(obs_path,
                                            self.p.getdir('STAGING_DIR'),
                                            self.p, self.logger)
            return obs_path

                       
        # convert valid_time to unix time
        valid_seconds = int(datetime.datetime.strptime(valid_time, "%Y%m%d%H%M").strftime("%s"))
        # get time of each file, compare to valid time, save best within range
        closest_file = ""
        closest_time = 9999999

        valid_range_lower = self.cg_dict['WINDOW_RANGE_BEG']
        valid_range_upper = self.cg_dict['WINDOW_RANGE_END']
        lower_limit = int(datetime.datetime.strptime(util.shift_time_seconds(valid_time, valid_range_lower),
                                                 "%Y%m%d%H%M").strftime("%s"))
        upper_limit = int(datetime.datetime.strptime(util.shift_time_seconds(valid_time, valid_range_upper),
                                                 "%Y%m%d%H%M").strftime("%s"))

        for dirpath, dirnames, all_files in os.walk(obs_dir):
            for filename in sorted(all_files):
                fullpath = os.path.join(dirpath, filename)
                f = fullpath.replace(obs_dir+"/", "")
                # check depth of template to crop filepath
                se = util.get_time_from_file(self.logger, f, obs_template)
                if se is not None:
                    file_valid_time = se.getValidTime("%Y%m%d%H%M")
                    if file_valid_time == '':
                        continue
                    file_valid_dt = datetime.datetime.strptime(file_valid_time, "%Y%m%d%H%M")
                    file_valid_seconds = int(file_valid_dt.strftime("%s"))
                    if file_valid_seconds < lower_limit or file_valid_seconds > upper_limit:
                        continue
                    diff = abs(valid_seconds - file_valid_seconds)
                    if diff < closest_time:
                        closest_time = diff
                        closest_file = fullpath

        if closest_file != "":
            return util.preprocess_file(closest_file, self.p.getdir('STAGING_DIR'), self.p, self.logger)
        else:
            return None

    def get_field_info(self, v, model_path, obs_path):
        fcst_level_type, fcst_level = self.split_level(v.fcst_level)
        obs_level_type, obs_level = self.split_level(v.obs_level)

        fcst_cat_thresh = ""
        fcst_threshs = []
        if v.fcst_thresh != "":
            fcst_threshs = v.fcst_thresh
            fcst_cat_thresh = "cat_thresh=[ "
            for fcst_thresh in fcst_threshs:
                fcst_cat_thresh += str(fcst_thresh)+", "
            fcst_cat_thresh = fcst_cat_thresh[0:-2]+" ];"

        obs_cat_thresh = ""
        obs_threshs = []
        if v.obs_thresh != "":
            obs_threshs = v.obs_thresh
            obs_cat_thresh = "cat_thresh=[ "
            for obs_thresh in obs_threshs:
                obs_cat_thresh += str(obs_thresh)+", "
            obs_cat_thresh = obs_cat_thresh[0:-2]+" ];"

        if len(fcst_threshs) != len(obs_threshs):
            self.logger.error("Number of forecast and "\
                            "observation thresholds must be the same")
            exit(1)

        # TODO: Allow NetCDF level with more than 2 dimensions i.e. (1,*,*)
        # TODO: Need to check data type for PROB fcst? non PROB obs?

        fcst_field = ""
        obs_field = ""
        if self.cg_dict['FCST_IS_PROB']:
            for fcst_thresh in fcst_threshs:
                thresh_str = ""
                comparison = util.get_comparison_from_threshold(fcst_thresh)
                number = util.get_number_from_threshold(fcst_thresh)
                if comparison in ["gt", "ge", ">", ">=" ]:
                    thresh_str += "thresh_lo="+str(number)+";"
                elif comparison in ["lt", "le", "<", "<=" ]:
                    thresh_str += "thresh_hi="+str(number)+";"

                fcst_field += "{ name=\"PROB\"; level=\""+fcst_level_type + \
                              fcst_level + "\"; prob={ name=\"" + \
                                v.fcst_name + \
                                "\"; "+thresh_str+" } },"
            # TODO: if pcp_combine was run on obs, use name_level, (*,*) format
            # if not, use user defined name/level combination. name should include _level
            for obs_thresh in obs_threshs:
                obs_field += "{ name=\""+v.obs_name+"_"+obs_level + \
                             "\"; level=\"(*,*)\"; cat_thresh=[ " + \
                             str(obs_thresh)+" ]; },"
        else:
            obs_data_type = util.get_filetype(obs_path)
            model_data_type = util.get_filetype(model_path)
            if obs_data_type == "NETCDF":
                obs_field += "{ name=\"" + v.obs_name+"_" + obs_level + \
                             "\"; level=\"(*,*)\"; "
            else:
                obs_field += "{ name=\""+v.obs_name + \
                             "\"; level=\"["+obs_level_type + \
                            obs_level+"]\"; "

            if model_data_type == "NETCDF":
                fcst_field += "{ name=\""+v.fcst_name+"_"+fcst_level + \
                              "\"; level=\"(*,*)\"; "
            else:
                fcst_field += "{ name=\""+v.fcst_name + \
                              "\"; level=\"["+fcst_level_type + \
                              fcst_level+"]\"; "

            fcst_field += fcst_cat_thresh+" },"
            obs_field += obs_cat_thresh+ " },"

        # remove last comma and } to be added back after extra options
        fcst_field = fcst_field[0:-2] + v.fcst_extra+"}"
        obs_field = obs_field[0:-2] + v.obs_extra+"}"
        return fcst_field, obs_field

    def split_level(self, level):
        level_type = ""
        if(level[0].isalpha()):
            level_type = level[0]
            level = level[1:].zfill(2)
        return level_type, level

    def run_at_time(self, init_time, valid_time):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """        
        task_info = TaskInfo()
        task_info.init_time = init_time
        task_info.valid_time = valid_time        
        var_list = util.parse_var_list(self.p)
        
        lead_seq = self.cg_dict['LEAD_SEQ']
        for lead in lead_seq:
            task_info.lead = lead
            self.run_at_time_once(task_info, var_list)


    def run_at_time_all_fields(self, task_info, var_list):
        """! Build a single call to MET application with all of the field/level combinations
              Args:
                @param task_info task_info object containing timing information
                @param var_list list of var_infoo objects containing variable information
        """
        # get model from first var to compare
        model_path = self.find_model(task_info, var_list[0])
        if model_path == "":
            self.logger.error("COULD NOT FIND FILE IN "+self.cg_dict['FCST_INPUT_DIR']+" FOR INIT "+task_info.getInitTime()+" f"+str(task_info.lead))
            return
        self.add_input_file(model_path)

        # get observation to from first var compare
        obs_path = self.find_obs(task_info, var_list[0])
        if obs_path == None:
            self.logger.error("COULD NOT FIND FILE IN "+self.cg_dict['OBS_INPUT_DIR']+" FOR INIT "+task_info.getInitTime()+" f"+str(task_info.lead))
            return
        self.add_input_file(obs_path)

        fcst_field_list = []
        obs_field_list = []
        for v in var_list:
            next_fcst, next_obs = self.get_field_info(v, model_path, obs_path)
            fcst_field_list.append(next_fcst)
            obs_field_list.append(next_obs)
        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.process_fields(task_info, v, fcst_field, obs_field)

    def run_at_time_once(self, task_info, var_list):
        # run app once for each field with all levels in each
        # TODO: implement method to add all fields and levels to a single call
        if self.cg_dict['ONCE_PER_FIELD']:
            for var_info in var_list:
                self.run_at_time_one_field(task_info, var_info)
        else:
            self.run_at_time_all_fields(task_info, var_list)

    def create_and_set_output_dir(self, ti):
        base_dir = self.cg_dict['OUTPUT_DIR']
        if self.cg_dict['LOOP_BY_INIT']:
            out_dir = os.path.join(base_dir,
                                   ti.getInitTime(), self.app_name)
        else:
            out_dir = os.path.join(base_dir,
                                   ti.getValidTime(), self.app_name)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.set_output_dir(out_dir)

    def process_fields(self, ti, v, fcst_field, obs_field):
        # set up environment variables for each run
        # get fcst and obs thresh parameters
        # verify they are the same size
        self.set_param_file(self.cg_dict['CONFIG_FILE'])
        self.create_and_set_output_dir(ti)
        
        self.add_env_var("MODEL", self.cg_dict['MODEL_TYPE'])
        self.add_env_var("OBTYPE", self.cg_dict['OB_TYPE'])
        self.add_env_var("FCST_VAR", v.fcst_name)
        self.add_env_var("OBS_VAR", v.obs_name)
        self.add_env_var("LEVEL", v.fcst_level)
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        self.add_env_var("CONFIG_DIR", self.cg_dict['CONFIG_DIR'])
        self.add_env_var("MET_VALID_HHMM", ti.getValidTime()[4:8])

        self.logger.debug("")
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        self.print_env_item("MODEL")
        self.print_env_item("OBTYPE")
        self.print_env_item("FCST_VAR")
        self.print_env_item("OBS_VAR")
        self.print_env_item("LEVEL")
        self.print_env_item("FCST_FIELD")
        self.print_env_item("OBS_FIELD")
        self.print_env_item("CONFIG_DIR")
        self.print_env_item("MET_VALID_HHMM")

        self.do_wrapper_specific_operations()

        cmd = self.get_command()
        if cmd is None:
            self.logger.error(self.app_name+\
                              " could not generate command")
            return
        self.logger.info("")
        self.build()
        self.clear()

            
    def run_at_time_one_field(self, ti, v):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
        """
        # get model to compare
        model_path = self.find_model(ti, v)
        if model_path == "":
            self.logger.error("COULD NOT FIND FILE IN "+self.cg_dict['FCST_INPUT_DIR']+" FOR INIT "+ti.getInitTime()+" f"+str(ti.lead))
            return
        self.add_input_file(model_path)

        # get observation to compare
        obs_path = self.find_obs(ti, v)
        if obs_path == None:
            self.logger.error("COULD NOT FIND FILE IN "+self.cg_dict['OBS_INPUT_DIR']+" FOR INIT "+ti.getInitTime()+" f"+str(ti.lead))
            return
        self.add_input_file(obs_path)

        # for grid_stat, loop over all variables and all them to the field list, then call the app once
        # for mode, loop over all variables and levels (and probability thresholds) and call the app for each
        fcst_field, obs_field = self.get_field_info(v, model_path, obs_path)
        self.process_fields(ti, v, fcst_field, obs_field)
        

