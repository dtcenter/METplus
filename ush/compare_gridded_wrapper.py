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
import time_util
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


    def create_c_dict(self):
        c_dict = dict()
        c_dict['var_list'] = util.parse_var_list(self.p)
        c_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))
        c_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE', 'FCST')
        c_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE', 'OBS')
        c_dict['CONFIG_DIR'] = util.getdir(self.p, 'CONFIG_DIR', '')
        c_dict['INPUT_BASE'] = util.getdir(self.p, 'INPUT_BASE', None, self.logger)
        c_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)
        c_dict['OBS_IS_PROB'] = self.p.getbool('config', 'OBS_IS_PROB', False)
        c_dict['FCST_MAX_FORECAST'] = self.p.getint('config', 'FCST_MAX_FORECAST', 24)
        c_dict['FCST_INIT_INTERVAL'] = self.p.getint('config', 'FCST_INIT_INTERVAL', 12)
        c_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        c_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)

        c_dict['OBS_WINDOW_BEGIN'] = \
          self.p.getint('config', 'OBS_WINDOW_BEGIN', -3600)
        c_dict['OBS_WINDOW_END'] = \
          self.p.getint('config', 'OBS_WINDOW_END', 3600)

        c_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'OBS_EXACT_VALID_TIME',
                                                              True)
        c_dict['FCST_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'FCST_EXACT_VALID_TIME',
                                                              True)
        c_dict['ALLOW_MULTIPLE_FILES'] = False
        util.add_common_items_to_dictionary(self.p, c_dict)
        return c_dict

#    def run_at_time(self, init_time, valid_time):
    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """

        # loop of forecast leads and process each
        lead_seq = self.c_dict['LEAD_SEQ']
        for lead in lead_seq:
            input_dict['lead_hours'] = lead

            self.logger.info("Processing forecast lead {}".format(lead))

            # set current lead time config and environment variables
            self.p.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)
            time_info = time_util.ti_calculate(input_dict)
            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(time_info)


    def run_at_time_once(self, time_info):
        """! Build MET command for a given init/valid time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
                @param var_list var_info object list containing variable information
        """

        # clear out the class variables
        self.clear()

        if self.c_dict['ONCE_PER_FIELD']:
            # loop over all fields and levels (and probability thresholds) and
            # call the app once for each
            for var_info in self.c_dict['var_list']:
                self.c_dict['CURRENT_VAR_INFO'] = var_info
                self.run_at_time_one_field(time_info, var_info)
        else:
            # loop over all variables and all them to the field list, then call the app once
            self.run_at_time_all_fields(time_info)


    def run_at_time_one_field(self, time_info, v):
        """! Build MET command for a single field for a given
             init/valid time and forecast lead combination
              Args:
                @param ti dictionary containing timing information
                @param v var_info object containing variable information
        """
        # get model to compare
        model_path = self.find_model(time_info, v)
        if model_path == None:
            self.logger.error("Could not find file in " + self.c_dict['FCST_INPUT_DIR'] +\
                              " for init time " + time_info['init_fmt'] + " f" + str(time_info['lead_hours']))
            return
        self.add_input_file(model_path)

        # get observation to compare
        obs_path = self.find_obs(time_info, v)
        if obs_path == None:
            self.logger.error("Could not find file in " + self.c_dict['OBS_INPUT_DIR'] +\
                              " for valid time " + time_info['valid_fmt'])
            return
        self.add_input_file(obs_path)

        # get field info field a single field to pass to the MET config file
        fcst_field = self.get_one_field_info(v.fcst_level, v.fcst_thresh, v.fcst_name, v.fcst_extra,
                                             model_path, 'FCST')
        obs_field = self.get_one_field_info(v.obs_level, v.obs_thresh, v.obs_name, v.obs_extra,
                                            obs_path, 'OBS')

        self.process_fields(time_info, fcst_field, obs_field)


    def run_at_time_all_fields(self, time_info):
        """! Build MET command for all of the field/level combinations for a given init/valid time and
             forecast lead combination
              Args:
                @param time_info dictionary containing timing information
        """
        # get model from first var to compare
        model_path = self.find_model(time_info, self.c_dict['var_list'][0])
        if model_path == None:
            self.logger.error("Could not find file in " + self.c_dict['FCST_INPUT_DIR'] +\
                              " for init time " + time_info['init_fmt'] + " f" + str(time_info['lead_hours']))
            return
        self.add_input_file(model_path)

        # get observation to from first var compare
        obs_path = self.find_obs(time_info, self.c_dict['var_list'][0])
        if obs_path == None:
            self.logger.error("Could not find file in " + self.c_dict['OBS_INPUT_DIR'] +\
                              " for valid time " + time_info['valid_fmt'])
            return
        self.add_input_file(obs_path)

        fcst_field_list = []
        obs_field_list = []
        for v in self.c_dict['var_list']:
            next_fcst = self.get_one_field_info(v.fcst_level, v.fcst_thresh, v.fcst_name, v.fcst_extra, model_path, 'FCST')
            next_obs = self.get_one_field_info(v.obs_level, v.obs_thresh, v.obs_name, v.obs_extra, obs_path, 'OBS')
            fcst_field_list.append(next_fcst)
            obs_field_list.append(next_obs)
        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.process_fields(time_info, fcst_field, obs_field)


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
        if self.c_dict['FCST_IS_PROB'] or self.c_dict['OBS_IS_PROB']:
            # if input being processed if probabilistic, format accordingly
            if self.c_dict[d_type+'_IS_PROB']:
                for thresh in threshs:
                    thresh_str = ""
                    comparison = util.get_comparison_from_threshold(thresh)
                    number = util.get_number_from_threshold(thresh)
                    if comparison in ["gt", "ge", ">", ">=", "==", "eq" ]:
                        thresh_str += "thresh_lo="+str(number)+"; "
                    if comparison in ["lt", "le", "<", "<=", "==", "eq" ]:
                        thresh_str += "thresh_hi="+str(number)+"; "

                    prob_cat_thresh = self.c_dict[d_type+'_PROB_THRESH']
                    # TODO: replace with better check for data type to remove path
                    # untested, need NetCDF prob fcst data
                    if self.c_dict[d_type+'_INPUT_DATATYPE'] == 'NETCDF':
#                    if path[-3:] == ".nc":
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

            field += cat_thresh + " " + v_extra+" }"
            fields.append(field)

        # combine all fields into a comma separated string and return
        field_list = ','.join(fields)
        return field_list


    def set_environment_variables(self, fcst_field, obs_field, time_info):
        # list of fields to print to log
        print_list = ["MODEL", "FCST_VAR", "OBS_VAR",
                      "LEVEL", "OBTYPE", "CONFIG_DIR",
                      "FCST_FIELD", "OBS_FIELD",
                      "INPUT_BASE", "MET_VALID_HHMM",
                      "FCST_TIME"]

        v = self.c_dict['var_list'][0]
        if 'CURRENT_VAR_INFO' in self.c_dict.keys():
            v = self.c_dict['CURRENT_VAR_INFO']

        # set environment variables needed for MET application
        self.add_env_var("MODEL", self.c_dict['MODEL_TYPE'])
        self.add_env_var("OBTYPE", self.c_dict['OB_TYPE'])
        self.add_env_var("FCST_VAR", v.fcst_name)
        self.add_env_var("OBS_VAR", v.obs_name)
        self.add_env_var("LEVEL", v.fcst_level)
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        self.add_env_var("CONFIG_DIR", self.c_dict['CONFIG_DIR'])
        self.add_env_var("MET_VALID_HHMM", time_info['valid_fmt'][4:8])
        self.add_env_var("FCST_TIME", str(time_info['lead_hours']).zfill(3))
        self.add_env_var("INPUT_BASE", self.c_dict["INPUT_BASE"])

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)



    def process_fields(self, time_info, fcst_field, obs_field):
        """! Set and print environment variables, then build/run MET command
              Args:
                @param time_info dictionary with time information
                @param fcst_field field information formatted for MET config file
                @param obs_field field information formatted for MET config file
        """
        # set config file since command is reset after each run
        self.set_param_file(self.c_dict['CONFIG_FILE'])

        # set up output dir with time info
        self.create_and_set_output_dir(time_info)

        # set environment variables needed by MET config file
        self.set_environment_variables(fcst_field, obs_field, time_info)

        # check if METplus can generate the command successfully
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        # run the MET command
        self.build()

        # clear out the class variables for the next run move to start of run
#        self.clear()


    def create_and_set_output_dir(self, time_info):
        """! Builds the full output dir path with valid or init time
              Creates output directory if it doesn't already exist
              Args:
                @param time_info dictionary with time information
        """
        base_dir = self.c_dict['OUTPUT_DIR']
        use_init = util.is_loop_by_init(self.p)
        if use_init:
            out_dir = os.path.join(base_dir,
                                   time_info['init_fmt'], self.app_name)
        else:
            out_dir = os.path.join(base_dir,
                                   time_info['valid_fmt'], self.app_name)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.set_output_dir(out_dir)


    def write_list_file(self, filename, file_list):
        list_dir = os.path.join(self.p.getdir('STAGING_DIR'), 'file_lists')
        list_path = os.path.join(list_dir, filename)

        if not os.path.exists(list_dir):
            os.makedirs(list_dir, mode=0775)

        with open(list_path, 'w') as file_handle:
            for f_path in file_list:
                file_handle.write(f_path+'\n')
        return list_path


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
