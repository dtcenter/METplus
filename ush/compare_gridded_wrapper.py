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
        self.cg_dict = self.create_cg_dict()


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

        # loop of forecast leads and process each
        lead_seq = self.cg_dict['LEAD_SEQ']
        for lead in lead_seq:
            task_info.lead = lead

            self.logger.info("Processing forecast lead {}".format(lead))

            # set current lead time config and environment variables
            self.p.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(task_info, var_list)


    def run_at_time_once(self, task_info, var_list):
        """! Build MET command for a given init/valid time and forecast lead combination
              Args:
                @param task_info task_info object containing timing information
                @param var_list var_info object list containing variable information
        """
        if self.cg_dict['ONCE_PER_FIELD']:
            # loop over all fields and levels (and probability thresholds) and
            # call the app once for each
            for var_info in var_list:
                self.run_at_time_one_field(task_info, var_info)
        else:
            # loop over all variables and all them to the field list, then call the app once
            self.run_at_time_all_fields(task_info, var_list)


    def run_at_time_one_field(self, ti, v):
        """! Build MET command for a single field for a given
             init/valid time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
        """
        # get model to compare
        model_path = self.find_model(ti, v)
        if model_path == None:
            self.logger.error("Could not find file in " + self.cg_dict['FCST_INPUT_DIR'] +\
                              " for init time " + ti.getInitTime() + " f" + str(ti.lead))
            return
        self.add_input_file(model_path)

        # get observation to compare
        obs_path = self.find_obs(ti, v)
        if obs_path == None:
            self.logger.error("Could not find file in " + self.cg_dict['OBS_INPUT_DIR'] +\
                              " for valid time " + ti.getValidTime())
            return
        self.add_input_file(obs_path)

        # get field info field a single field to pass to the MET config file
        fcst_field = self.get_one_field_info(v.fcst_level, v.fcst_thresh, v.fcst_name, v.fcst_extra,
                                             model_path, 'FCST')
        obs_field = self.get_one_field_info(v.obs_level, v.obs_thresh, v.obs_name, v.obs_extra,
                                            obs_path, 'OBS')

        self.process_fields(ti, v, fcst_field, obs_field)


    def run_at_time_all_fields(self, task_info, var_list):
        """! Build MET command for all of the field/level combinations for a given init/valid time and
             forecast lead combination
              Args:
                @param task_info task_info object containing timing information
                @param var_list list of var_infoo objects containing variable information
        """
        # get model from first var to compare
        model_path = self.find_model(task_info, var_list[0])
        if model_path == None:
            self.logger.error("Could not find file in " + self.cg_dict['FCST_INPUT_DIR'] +\
                              " for init time " + task_info.getInitTime() + " f" + str(task_info.lead))
            return
        self.add_input_file(model_path)

        # get observation to from first var compare
        obs_path = self.find_obs(task_info, var_list[0])
        if obs_path == None:
            self.logger.error("Could not find file in " + self.cg_dict['OBS_INPUT_DIR'] +\
                              " for valid time " + task_info.getValidTime())
            return
        self.add_input_file(obs_path)

        fcst_field_list = []
        obs_field_list = []
        for v in var_list:
            next_fcst = self.get_one_field_info(v.fcst_level, v.fcst_thresh, v.fcst_name, v.fcst_extra, model_path, 'FCST')
            next_obs = self.get_one_field_info(v.obs_level, v.obs_thresh, v.obs_name, v.obs_extra, obs_path, 'OBS')
            fcst_field_list.append(next_fcst)
            obs_field_list.append(next_obs)
        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.process_fields(task_info, v, fcst_field, obs_field)


    def find_model(self, ti, v):
        """! Finds the model file to compare
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @rtype string
                @return Returns the path to an model file
        """
        return self.find_data(ti, v, "FCST")

    def find_obs(self, ti, v):
        """! Finds the observation file to compare
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @rtype string
                @return Returns the path to an observation file
        """
        return self.find_data(ti, v, "OBS")


    def find_data(self, ti, v, data_type):
        """! Finds the data file to compare
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @param data_type type of data to find (FCST or OBS)
                @rtype string
                @return Returns the path to an observation file
        """
        # get time info
        lead = ti.getLeadTime()
        valid_time = ti.getValidTime()
        init_time = ti.getInitTime()

        # set level based on input data type
        if data_type == "OBS":
            v_level = v.obs_level
        else:
            v_level = v.fcst_level

        # separate character from beginning of numeric level value if applicable
        level_type, level = util.split_level(v_level)

        # set level to 0 character if it is not a number
        if not level.isdigit():
            level = '0'

        template = self.cg_dict[data_type+'_INPUT_TEMPLATE']
        data_dir = self.cg_dict[data_type+'_INPUT_DIR']

        # if looking for a file with an exact time match:
        if self.cg_dict[data_type+'_EXACT_VALID_TIME']:
            # perform string substitution
            dSts = sts.StringSub(self.logger,
                                   template,
                                   valid=valid_time,
                                   init=init_time,
                                   lead=str(lead).zfill(2),
                                   level=str(level.split('-')[0]).zfill(2))
            filename = dSts.doStringSub()

            # build full path with data directory and filename
            path = os.path.join(data_dir, filename)

            # check if desired data file exists and if it needs to be preprocessed
            path = util.preprocess_file(path,
                                        self.cg_dict[data_type+'_INPUT_DATATYPE'],
                                        self.p, self.logger)
            return path

        # if looking for a file within a time window:
        # convert valid_time to unix time
        valid_seconds = int(datetime.datetime.strptime(valid_time, "%Y%m%d%H%M").strftime("%s"))
        # get time of each file, compare to valid time, save best within range
        closest_file = None
        closest_time = 9999999

        # get range of times that will be considered
        valid_range_lower = self.cg_dict['WINDOW_RANGE_BEG']
        valid_range_upper = self.cg_dict['WINDOW_RANGE_END']
        lower_limit = int(datetime.datetime.strptime(util.shift_time_seconds(valid_time, valid_range_lower),
                                                 "%Y%m%d%H%M").strftime("%s"))
        upper_limit = int(datetime.datetime.strptime(util.shift_time_seconds(valid_time, valid_range_upper),
                                                 "%Y%m%d%H%M").strftime("%s"))

        # step through all files under input directory in sorted order
        for dirpath, dirnames, all_files in os.walk(data_dir):
            for filename in sorted(all_files):
                fullpath = os.path.join(dirpath, filename)

                # remove input data directory to get relative path
                f = fullpath.replace(data_dir+"/", "")

                # extract time information from relative path using template
                se = util.get_time_from_file(self.logger, f, template)
                if se is not None:
                    # get valid time and check if it is within the time range
                    file_valid_time = se.getValidTime("%Y%m%d%H%M")
                    # skip if could not extract valid time
                    if file_valid_time == '':
                        continue
                    file_valid_dt = datetime.datetime.strptime(file_valid_time, "%Y%m%d%H%M")
                    file_valid_seconds = int(file_valid_dt.strftime("%s"))
                    # skip if outside time range
                    if file_valid_seconds < lower_limit or file_valid_seconds > upper_limit:
                        continue

                    # check if file is closer to desired valid time than previous match
                    diff = abs(valid_seconds - file_valid_seconds)
                    if diff < closest_time:
                        closest_time = diff
                        closest_file = fullpath

        # check if file needs to be preprocessed before returning the path
        return util.preprocess_file(closest_file,
                                    self.cg_dict[data_type+'_INPUT_DATATYPE'],
                                    self.p, self.logger)


    def get_one_field_info(self, v_level, v_thresh, v_name, v_extra, path, d_type):
        """! Format field information into format expected by MET config file
              Args:
                @param v_level level of data to extract
                @param v_thresh threshold value to use in comparison
                @param v_name name of field to process
                @param v_extra additional field information to add if available
                @param path full path of field to process (used to determine if NetCDF)
                @param d_type type of data to find (FCST or OBS)
                @rtype string
                @return Returns formatted field information
        """
        # separate character from beginning of numeric level value if applicable
        level_type, level = util.split_level(v_level)

        # list to hold field information
        fields = []

        # get cat thresholds if available
        cat_thresh = ""
        threshs = []
        if len(v_thresh) != 0:
            threshs = v_thresh
            cat_thresh = "cat_thresh=[ " + ','.join(threshs) + " ];"

        # if either input is probabilistic, create separate item for each threshold
        if self.cg_dict['FCST_IS_PROB'] or self.cg_dict['OBS_IS_PROB']:
            # if input being processed if probabilistic, format accordingly
            if self.cg_dict[d_type+'_IS_PROB']:
                for thresh in threshs:
                    thresh_str = ""
                    comparison = util.get_comparison_from_threshold(thresh)
                    number = util.get_number_from_threshold(thresh)
                    if comparison in ["gt", "ge", ">", ">=", "==", "eq" ]:
                        thresh_str += "thresh_lo="+str(number)+"; "
                    if comparison in ["lt", "le", "<", "<=", "==", "eq" ]:
                        thresh_str += "thresh_hi="+str(number)+"; "

                    prob_cat_thresh = self.cg_dict[d_type+'_PROB_THRESH']
                    # TODO: replace with better check for data type to remove path
                    # untested, need NetCDF prob fcst data
                    if path[-3:] == ".nc":
                        field = "{ name=\"" + v_name + "\"; level=\"" + \
                          level+"\"; prob=TRUE; cat_thresh=["+prob_cat_thresh+"];}"
                    else:
                        field = "{ name=\"PROB\"; level=\""+level_type + \
                                level + "\"; prob={ name=\"" + \
                                v_name + \
                                "\"; "+thresh_str+"} cat_thresh=["+prob_cat_thresh+"];"
                    field += v_extra + "}"
                    fields.append(field)
            else:
                # if input being processed is not probabilistic but the other input is
                for thresh in threshs:
                    # if pcp_combine was run, use name_level, (*,*) format
                    # if not, use user defined name/level combination
                    if self.p.getbool('config', d_type+'_PCP_COMBINE_RUN', False):
                        field = "{ name=\""+v_name+"_"+level + \
                                     "\"; level=\"(*,*)\"; cat_thresh=[ " + \
                                     str(thresh)+" ]; }"
                    else:
                        field = "{ name=\""+v_name + \
                                     "\"; level=\""+v_level+"\"; cat_thresh=[ " + \
                                     str(thresh)+" ]; }"
                    fields.append(field)
        else:
            # if neither input is probabilistic, add all cat thresholds to same field info item
            # if pcp_combine was run, use name_level, (*,*) format
            # if not, use user defined name/level combination
            if self.p.getbool('config', d_type+'_PCP_COMBINE_RUN', False):
                field = "{ name=\"" + v_name+"_" + level + \
                             "\"; level=\"(*,*)\"; "
            else:
                field = "{ name=\""+v_name + \
                             "\"; level=\""+v_level+"\"; "

            field += cat_thresh + " " + v_extra+"}"
            fields.append(field)

        # combine all fields into a comma separated string and return
        field_list = ','.join(fields)
        return field_list


    def process_fields(self, ti, v, fcst_field, obs_field):
        """! Set and print environment variables, then build/run MET command
              Args:
                @param ti task_info object with time information
                @param v var_info object with field information
                @param fcst_field field information formatted for MET config file
                @param obs_field field information formatted for MET config file
        """
        # set config file since command is reset after each run
        self.set_param_file(self.cg_dict['CONFIG_FILE'])

        # set up output dir with time info
        self.create_and_set_output_dir(ti)

        # list of fields to print to log
        print_list = ["MODEL", "FCST_VAR", "OBS_VAR",
                      "LEVEL", "OBTYPE", "CONFIG_DIR",
                      "FCST_FIELD", "OBS_FIELD",
                      "INPUT_BASE", "MET_VALID_HHMM",
                      "FCST_TIME"]

        # set environment variables needed for MET application
        self.add_env_var("MODEL", self.cg_dict['MODEL_TYPE'])
        self.add_env_var("OBTYPE", self.cg_dict['OB_TYPE'])
        self.add_env_var("FCST_VAR", v.fcst_name)
        self.add_env_var("OBS_VAR", v.obs_name)
        self.add_env_var("LEVEL", v.fcst_level)
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        self.add_env_var("CONFIG_DIR", self.cg_dict['CONFIG_DIR'])
        self.add_env_var("MET_VALID_HHMM", ti.getValidTime()[4:8])
        self.add_env_var("FCST_TIME", str(ti.lead).zfill(3))
        self.add_env_var("INPUT_BASE", self.cg_dict["INPUT_BASE"])

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

        # check if METplus can generate the command successfully
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        # run the MET command
        self.build()

        # clear out the class variables for the next run
        self.clear()


    def create_and_set_output_dir(self, ti):
        """! Builds the full output dir path with valid or init time
              Creates output directory if it doesn't already exist
              Args:
                @param ti task_info object with time information
        """
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


    def set_output_dir(self, outdir):
        """! Sets the output dir and adds -output in front
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
            self.logger.error("No app path specified. "\
                              "You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            self.logger.error("No input filenames specified")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.param != "":
            cmd += self.param + " "

        if self.outdir == "":
            self.logger.error("No output directory specified")
            return None

        cmd += self.outdir
        return cmd
