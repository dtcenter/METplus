#!/usr/bin/env python

'''
Program Name: compare_ensemble_wrapper.py
Contact(s): metplus-dev
Abstract: Initial template based on compare_ensemble_wrapper by George McCabe
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

'''!@namespace CompareEnsembleWrapper
@brief Common functionality to wrap similar MET applications
that compare ensemble data
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''
class CompareEnsembleWrapper(CommandBuilder):
    """!Common functionality to wrap similar MET applications
that compares ensemble data
    """
    def __init__(self, p, logger):
        super(CompareEnsembleWrapper, self).__init__(p, logger)
        #self.met_install_dir = p.getdir('MET_INSTALL_DIR')
        #self.ce_dict = self.create_ce_dict()

    def clear(self):
        """!Unset class variables to prepare for next run time
        """
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""
        self.point_obs_files = []

    def set_output_dir(self, outdir):
        """! Sets the output directory
              Args:
                @param outdir directory to set
        """        
        self.outdir = "-outdir "+outdir

    def set_input_file_num(self, filenum):
        """! Sets the number of ensemble members, Use this when
        passing the ensemble member list on the command line.
            Args:
                @param filenum - the number of ensemble members
        """
        self.input_file_num = filenum

    def add_point_obs_file(self,point_obs_file):
        """!Add a point obs file to MET application command line
            Args:
                @param point_obs_file
        """
        self.point_obs_files.append(point_obs_file)

    def get_point_obs_files(self):
        """!Returns list of the point obs files passed to MET application
        """
        return self.point_obs_files


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

        cmd += self.input_file_num + " "

        if len(self.infiles) == 0:
            self.logger.error(self.app_name+": No input filenames specified")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.param != "":
            cmd += self.param + " "

        for f in self.point_obs_files:
            cmd += "-point_obs " + f + " "

        if self.outdir == "":
            self.logger.error(self.app_name+": No output directory specified")
            return None

        cmd += self.outdir
        return cmd

    def find_model_members(self, lead, init_time, level=None):
        """! Finds the model member files to compare
              Args:
                @param lead forecast lead value
                @param init_time initialization time
                @param level
                @rtype string
                @return Returns a list of the paths to the ensemble model files
        """
        app_name_caps = self.app_name.upper()
        model_dir = self.ce_dict['FCST_INPUT_DIR']

        # model_template is a list of 1 or more.
        ens_members_template = self.ce_dict['FCST_INPUT_TEMPLATE']
        max_forecast = self.ce_dict['FCST_MAX_FORECAST']
        init_interval = self.ce_dict['FCST_INIT_INTERVAL']
        lead_check = lead
        time_check = init_time
        time_offset = 0
        found = False
#        while lead_check <= max_forecast:
            # split by - to handle a level that is a range, such as 0-10

        ens_members_path = []
        # This is for all the members defined in the template.
        for ens_member_template in ens_members_template:
            if level:
                model_ss = sts.StringSub(self.logger, ens_member_template,
                                             init=time_check,
                                             lead=str(lead_check).zfill(2),
                                             level=str(level.split('-')[0]).zfill(2))
            else:
                model_ss = sts.StringSub(self.logger, ens_member_template,
                                             init=time_check,
                                             lead=str(lead_check).zfill(2))
            member_file = model_ss.doStringSub()
            member_path = os.path.join(model_dir, member_file)

            ens_members_path.append(member_path)


        # TODO: jtf Harden and review this requirement/assumption that the
        # member_path after a String Template Substitution contains wildcards
        # that can be globbed to return all the members for this lead time.
        # It may contain wild cards, it may contain a produtil conf variable
        # of the number of ensemble members as well as format and padding
        # info. For now we are assuming member_path has wild cards that can
        # be globbed.

        # This is if FCST_INPUT_TEMPLATE on has 1 item in its template list
        #  and the template has filename wild cards to glob and match files.
        # /somevalidpath/postprd_mem000?/wrfprs_conus_mem000?_00.grib2
        if int(self.ce_dict['N_ENSEMBLE_MEMBERS']) > 1 \
                and len(ens_members_template) == 1:
            ens_members_path = sorted(glob.glob(member_path))
            self.logger.debug('Ensemble Members File pattern: %s'%
                              ens_members_template[0])
            self.logger.debug('Number of Members matching File Pattern: ' +
                              str(len(ens_members_path)))

        # check that all the members exist.
        all_members_exist = True
        for member_path in ens_members_path:
            if not os.path.exists(member_path):
                self.logger.error("MISSING ensemble member: %s"%member_path)
                all_members_exist = False

# TODO: jtf Review this block - do we need it, it was in grid_stat_wrapper.py
#            util.decompress_file(model_path, self.logger)
#            if os.path.exists(model_path):
#                found = True
#                break

#            time_check = util.shift_time(time_check, -init_interval)
#            lead_check = lead_check + init_interval

        if all_members_exist:
            return ens_members_path
        else:
            return []

    # TODO: jtf BROKEN This does not seem to work with ensembles - figure it out.
    def find_obs(self, ti):
        """! Finds the observation file to compare
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @rtype string
                @return Returns the path to an observation file
        """        
        app_name_caps = self.app_name.upper()        
        valid_time = ti.getValidTime()
        obs_dir = self.ce_dict['OBS_INPUT_DIR']
        obs_template = self.ce_dict['OBS_INPUT_TEMPLATE']
        # convert valid_time to unix time
        valid_seconds = int(datetime.datetime.strptime(valid_time, "%Y%m%d%H%M").strftime("%s"))
        # get time of each file, compare to valid time, save best within range
        closest_file = ""
        closest_time = 9999999

        valid_range_lower = self.ce_dict['WINDOW_RANGE_BEG']
        valid_range_upper = self.ce_dict['WINDOW_RANGE_END']
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
            return closest_file
        else:
            return None
        

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
        
        lead_seq = self.ce_dict['LEAD_SEQ']
        for lead in lead_seq:
            task_info.lead = lead

            # if var_list is empty [], we infer that means the ens, fcst, obs
            # fields are defined in the MET conf file instead.
            if var_list:
                for var_info in var_list:
                    self.run_at_time_once(task_info, var_info)
            else:
                self.run_at_time_once_no_var_list(task_info)

    def run_at_time_once(self, ti, v):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
        """
        app_name_caps = self.app_name.upper()        
        valid_time = ti.getValidTime()
        init_time = ti.getInitTime()
        base_dir = self.ce_dict['OUTPUT_DIR']
        if self.ce_dict['LOOP_BY_INIT']:
            out_dir = os.path.join(base_dir,
                                   init_time, self.app_name)
        else:
            out_dir = os.path.join(base_dir,
                                   valid_time, self.app_name)
        fcst_level = v.fcst_level
        fcst_level_type = ""
        if(fcst_level[0].isalpha()):
            fcst_level_type = fcst_level[0]
            fcst_level = fcst_level[1:]
        obs_level = v.obs_level
        obs_level_type = ""
        if(obs_level[0].isalpha()):
            obs_level_type = obs_level[0]
            obs_level = obs_level[1:]            
        model_type = self.ce_dict['MODEL_TYPE']
        obs_dir = self.ce_dict['OBS_INPUT_DIR']
        obs_template = self.ce_dict['OBS_INPUT_TEMPLATE']
        model_dir = self.ce_dict['FCST_INPUT_DIR']
        config_dir = self.ce_dict['CONFIG_DIR']

        ymd_v = valid_time[0:8]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # get model to compare
        model_member_paths =  self.find_model_members(ti.lead, init_time,
                                                      fcst_level)

        if not model_member_paths:
            self.logger.error("Missing Ensemble Member FILEs IN "
                              +model_dir+" FOR "+init_time+" f"+str(ti.lead))
            return

        if int(self.ce_dict['N_ENSEMBLE_MEMBERS']) != \
                len(model_member_paths):
            self.logger.error("MISMATCH: Members matching File Pattern: %s "
                              "vs. conf N_ENSEMBLE_MEMBERS: %s " %
                              (len(model_member_paths),
                               self.ce_dict['N_ENSEMBLE_MEMBERS']))
            return

        # TODO: jtf add ensemble file list file
        # if N_ENSEMBLE_MEMBERS is not defined, use that as
        # a trigger to indicate a file with list of members will be
        # used instead.

        # Add the number of ensemble members to the MET command
        self.set_input_file_num(self.ce_dict['N_ENSEMBLE_MEMBERS'])

        # Add each member to create a space seperated list on the command line
        for member in model_member_paths:
            self.add_input_file(member)

        # TODO: jtf STS fundamental. We need to know what keys to pass in
        # from the filename_template. if the keys change, the call
        # must change in the code. Therefore, we need to specify in
        # the conf file which sts keys are supported for subject
        # template.

        if self.ce_dict['OBS_EXACT_VALID_TIME']:
            #original call from compare_grid_wrapper.py
            #obsSts = sts.StringSub(self.logger,
            #                       obs_template,
            #                       valid=valid_time,
            #                       init=init_time,
            #                       level=str(obs_level.split('-')[0]).zfill(2))
            #obsSts = sts.StringSub(self.logger,
            #                       obs_template,
            #                       cycle=str(ti.lead),
            #                       valid=valid_time,
            #                       init=init_time,
            #                       level=str(obs_level.split('-')[0]).zfill(2))
            obsSts = sts.StringSub(self.logger,
                                   obs_template,
                                   lead=str(ti.lead),
                                   valid=valid_time,
                                   init=init_time,
                                   level=str(obs_level.split('-')[0]).zfill(2))

            obs_file = obsSts.doStringSub()

            obs_path = os.path.join(obs_dir, obs_file)
        else:
            obs_path = self.find_obs(ti)

        self.add_point_obs_file(obs_path)
        self.set_param_file(self.ce_dict['CONFIG_FILE'])
        self.set_output_dir(out_dir)

        # set up environment variables for each run
        # get fcst and obs thresh parameters
        # verify they are the same size
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

        # TODO: gm Allow NetCDF level with more than 2 dimensions i.e. (1,*,*)
        # TODO: gm Need to check data type for PROB fcst? non PROB obs?

        fcst_field = ""
        obs_field = ""
        # TODO: gm change PROB mode to put all cat thresh values in 1 item
        if self.ce_dict['FCST_IS_PROB']:
            for fcst_thresh in fcst_threshs:
                thresh_str = ""
                comparison = util.get_comparison_from_threshold(fcst_thresh)
                number = util.get_number_from_threshold(fcst_thresh)
                if comparison in ["gt", "ge", ">", ">=" ]:
                    thresh_str += "thresh_lo="+str(number)+";"
                elif comparison in ["lt", "le", "<", "<=" ]:
                    thresh_str += "thresh_hi="+str(number)+";"

                thresh = util.get_number_from_threshold(fcst_thresh)
                fcst_field += "{ name=\"PROB\"; level=\""+fcst_level_type + \
                              fcst_level.zfill(2) + "\"; prob={ name=\"" + \
                              v.fcst_name + \
                              "\"; "+thresh_str+" } },"
            for obs_thresh in obs_threshs:
                obs_field += "{ name=\""+v.obs_name+"_"+obs_level.zfill(2) + \
                             "\"; level=\"(*,*)\"; cat_thresh=[ " + \
                             str(obs_thresh)+" ]; },"
        else:
            obs_data_type = util.get_filetype(obs_path)
            #Note: this check for model_data_type checks
            #only the first member and assumes all the others are the same.
            model_data_type = util.get_filetype(model_member_paths[0])

            if obs_data_type == "NETCDF":

              obs_field += "{ name=\"" + v.obs_name+"_" + obs_level.zfill(2) + \
                           "\"; level=\"(*,*)\"; "

            else:
              obs_field += "{ name=\""+v.obs_name + \
                            "\"; level=\"["+obs_level_type + \
                            obs_level.zfill(2)+"]\"; "

            if model_data_type == "NETCDF":
                fcst_field += "{ name=\""+v.fcst_name+"_"+fcst_level.zfill(2) + \
                              "\"; level=\"(*,*)\"; "
            else:
                fcst_field += "{ name=\""+v.fcst_name + \
                              "\"; level=\"["+fcst_level_type + \
                              fcst_level.zfill(2)+"]\"; "

            fcst_field += fcst_cat_thresh+" },"

            obs_field += obs_cat_thresh+ " },"

        # remove last comma and } to be added back after extra options
        fcst_field = fcst_field[0:-2]
        obs_field = obs_field[0:-2]

        fcst_field += v.fcst_extra+"}"
        obs_field += v.obs_extra+"}"

        ob_type = self.ce_dict["OB_TYPE"]
        input_base = self.ce_dict["INPUT_BASE"]

        self.add_env_var("MODEL", model_type)
        self.add_env_var("FCST_VAR", v.fcst_name)
        self.add_env_var("OBS_VAR", v.obs_name)
        self.add_env_var("LEVEL", v.fcst_level)
        self.add_env_var("OBTYPE", ob_type)
        self.add_env_var("CONFIG_DIR", config_dir)
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        self.add_env_var("INPUT_BASE", input_base)
        self.add_env_var("MET_VALID_HHMM", valid_time[4:8])
        cmd = self.get_command()

        self.logger.debug("")
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_item("MODEL")
        self.print_env_item("FCST_VAR")
        self.print_env_item("OBS_VAR")
        self.print_env_item("LEVEL")
        self.print_env_item("OBTYPE")
        self.print_env_item("CONFIG_DIR")
        self.print_env_item("FCST_FIELD")
        self.print_env_item("OBS_FIELD")
        self.print_env_item("INPUT_BASE")
        self.print_env_item("MET_VALID_HHMM")        
        self.logger.debug("")
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(["MODEL", "FCST_VAR", "OBS_VAR",
                             "LEVEL", "OBTYPE", "CONFIG_DIR",
                             "FCST_FIELD", "OBS_FIELD",
                             "INPUT_BASE",
                             "MET_VALID_HHMM"])
        self.logger.debug("")
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("ERROR: "+self.app_name+\
                              " could not generate command")
            return
        self.logger.info("")
        self.build()
        #self.logger.info('=====================================================================')
        #self.logger.info("{:s}".format(cmd))
        #for arg in cmd.split():
        #    self.logger.info("{:s}".format(arg))
        #self.clear()

    def run_at_time_once_no_var_list(self, ti):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
        """
        app_name_caps = self.app_name.upper()
        valid_time = ti.getValidTime()
        init_time = ti.getInitTime()
        base_dir = self.ce_dict['OUTPUT_DIR']
        if self.ce_dict['LOOP_BY_INIT']:
            out_dir = os.path.join(base_dir,
                                   init_time, self.app_name)
        else:
            out_dir = os.path.join(base_dir,
                                   valid_time, self.app_name)

        model_type = self.ce_dict['MODEL_TYPE']
        obs_dir = self.ce_dict['OBS_INPUT_DIR']
        obs_template = self.ce_dict['OBS_INPUT_TEMPLATE']
        model_dir = self.ce_dict['FCST_INPUT_DIR']
        config_dir = self.ce_dict['CONFIG_DIR']

        ymd_v = valid_time[0:8]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # get model to compare
        model_member_paths = self.find_model_members(ti.lead, init_time)

        if not model_member_paths:
            self.logger.error("Missing Ensemble Member FILEs IN "
                              + model_dir + " FOR " + init_time + " f" + str(ti.lead))
            return

        if int(self.ce_dict['N_ENSEMBLE_MEMBERS']) != \
                len(model_member_paths):
            self.logger.error("MISMATCH: Members matching File Pattern: %s "
                              "vs. conf N_ENSEMBLE_MEMBERS: %s " %
                              (len(model_member_paths),
                               self.ce_dict['N_ENSEMBLE_MEMBERS']))
            return

        # TODO: jtf add ensemble file list file
        # if N_ENSEMBLE_MEMBERS is not defined, use that as
        # a trigger to indicate a file with list of members will be
        # used instead.

        # Add the number of ensemble members to the MET command
        self.set_input_file_num(self.ce_dict['N_ENSEMBLE_MEMBERS'])

        # Add each member to create a space seperated list on the command line
        for member in model_member_paths:
            self.add_input_file(member)

        # TODO: jtf STS fundamental. We need to know what keys to pass in
        # from the filename_template. if the keys change, the call
        # must change in the code. Therefore, we need to specify in
        # the conf file which sts keys are supported for subject
        # template.

        if self.ce_dict['OBS_EXACT_VALID_TIME']:
            obsSts = sts.StringSub(self.logger,
                                   obs_template,
                                   lead=str(ti.lead),
                                   valid=valid_time,
                                   init=init_time)

            obs_file = obsSts.doStringSub()

            obs_path = os.path.join(obs_dir, obs_file)
        else:
            obs_path = self.find_obs(ti)

        self.add_point_obs_file(obs_path)
        self.set_param_file(self.ce_dict['CONFIG_FILE'])
        self.set_output_dir(out_dir)

        # set up environment variables for each run
        # get fcst and obs thresh parameters
        # verify they are the same size


        ob_type = self.ce_dict["OB_TYPE"]
        input_base = self.ce_dict["INPUT_BASE"]

        self.add_env_var("MODEL", model_type)
        self.add_env_var("OBTYPE", ob_type)
        self.add_env_var("CONFIG_DIR", config_dir)
        self.add_env_var("INPUT_BASE", input_base)
        self.add_env_var("MET_VALID_HHMM", valid_time[4:8])
        cmd = self.get_command()

        self.logger.debug("")
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_item("MODEL")
        self.print_env_item("OBTYPE")
        self.print_env_item("CONFIG_DIR")
        self.print_env_item("INPUT_BASE")
        self.print_env_item("MET_VALID_HHMM")
        self.logger.debug("")
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(["MODEL", "OBTYPE", "CONFIG_DIR",
                             "INPUT_BASE", "MET_VALID_HHMM"])
        self.logger.debug("")
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("ERROR: " + self.app_name + \
                              " could not generate command")
            return
        self.logger.info("")
        #self.build()
        #self.logger.info('=====================================================================')
        #self.logger.info("{:s}".format(cmd))
        #for arg in cmd.split():
        #    self.logger.info("{:s}".format(arg))
        self.clear()
