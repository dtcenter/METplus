#!/usr/bin/env python

'''
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row
Abstract: Runs stat_analysis
History Log:  Third version
Usage: stat_analysis_wrapper.py
Parameters: None
Input Files: MET .stat files
Output Files: MET .stat files
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
import time
import calendar
import string_template_substitution as sts
from command_builder import CommandBuilder


class StatAnalysisWrapper(CommandBuilder):
    def __init__(self, config, logger):
        super(StatAnalysisWrapper, self).__init__(config, logger)
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin/stat_analysis')
        self.app_name = os.path.basename(self.app_path)

    def set_lookin_dir(self, lookindir):
        self.lookindir = "-lookin "+lookindir+" "
   
    def get_command(self):
        if self.app_path is None:
            self.logger.error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        if self.lookindir == "":
            self.logger.error(self.app_name+": No lookin directory specified")
            return None
        
        cmd += self.lookindir
         
        if self.param != "":
            cmd += "-config " + self.param + " "
        return cmd


    def create_job_filename(self, job_name,
                            job_args, stat_analysis_out_dir_base,
                            stat_analysis_dump_row_info,
                            stat_analysis_out_stat_info):
        """! Create the stat_analysis job command and set environment variable
             for the MET stat_analysis config file
                 
             Args:
                job_name - string containing the user requested stat_analysis job
                           to run
                job_args - string containig the user requested job related
                           arguements
                stat_analysis_out_dir_base - directory where the output from
                                             stat_analysis will be placed
                stat_analysis_dump_row_info - dictionary containing
                                              information to build a file
                                              name for a stat_analysis 
                                              dump_row file
                stat_analysis_out_stat_info - dictionary containing
                                              information to build a file
                                              name for a stat_analysis 
                                              out_stat file

             Returns:
                job - string containing the user requested job information for 
                      stat_analysis, the enivronment variable JOB is set to 
                      this and is used the MET stat_analysis config file
                       
        """
        job = "-job "+job_name+" "+job_args
        #check for dump_row
        if stat_analysis_dump_row_info.template_type != "NA":
            if "/" in stat_analysis_dump_row_info.filename:
                stat_analysis_dump_row_rpartition = stat_analysis_dump_row_info.filename.rpartition("/")
                stat_analysis_out_dir = os.path.join(stat_analysis_out_dir_base, stat_analysis_dump_row_rpartition[0])
                stat_analysis_dump_row_filename = stat_analysis_dump_row_rpartition[2]
            else:
                stat_analysis_out_dir = stat_analysis_out_dir_base
                stat_analysis_dump_row_filename = stat_analysis_dump_row_info.filename
            util.mkdir_p(stat_analysis_out_dir)
            job = job.replace("[dump_row_filename]", stat_analysis_out_dir+"/"+stat_analysis_dump_row_filename)
        #check for out_stat
        if stat_analysis_out_stat_info.template_type != "NA":
            if "/" in stat_analysis_out_stat_info.filename:
                stat_analysis_out_stat_rpartition = stat_analysis_out_stat_info.filename.rpartition("/")
                stat_analysis_out_dir = os.path.join(stat_analysis_out_dir_base, stat_analysis_out_stat_rpartition[0])
                stat_analysis_out_stat_filename = stat_analysis_out_stat_rpartition[2]
            else:
                stat_analysis_out_dir = stat_analysis_out_dir_base
                stat_analysis_out_stat_filename = stat_analysis_out_stat_info.filename
            util.mkdir_p(stat_analysis_out_dir)
            job = job.replace("[out_stat_filename]", stat_analysis_out_dir+"/"+stat_analysis_out_stat_filename)
        self.add_env_var("JOB", job)
        return job
       
    def create_hour_group_list(self, loop_hour_beg, loop_hour_end,
                               loop_hour_interval):
        """! Creates a list of hours formatted in %H%M%S
                 
             Args:
                loop_hour_beg - Unix timestamp value of the start hour
                loop_hour_end - Unix timestamp value of the end hour 
                loop_hours_interval - integer of increments to include
                                      list

             Returns:
                hour_group_list - list of hours formatted in %H%M%S
        """
        loop_hour_now = loop_hour_beg
        hour_group_list = ""
        while loop_hour_now <= loop_hour_end:
            if loop_hour_now == loop_hour_end:
                hour_group_list = hour_group_list+'"'+str(time.strftime("%H%M%S", time.gmtime(loop_hour_now))+'"')
            else:
                hour_group_list = hour_group_list+'"'+str(time.strftime("%H%M%S", time.gmtime(loop_hour_now))+'", ')
            loop_hour_now += loop_hour_interval
        return hour_group_list

    def create_variable_list(self, conf_var):
        """! Creates a string from a list to be used in the MET stat_analysis
             config file
                 
             Args:
                conf_var - list of values 

             Returns:
                conf_var_list - string that can be set as an 
                                environment variable to be read in 
                                the MET stat_analysis config_file
        """
        conf_var_list=""
        if len(conf_var) > 0:
            for lt in range(len(conf_var)):
                if lt == len(conf_var)-1:
                    conf_var_list = conf_var_list+'"'+str(conf_var[lt]+'"')
                else:
                    conf_var_list = conf_var_list+'"'+str(conf_var[lt]+'", ')
        return conf_var_list

    class StatAnalysisOutputInfo(object):
        __slots__ = 'template_type', 'filename_template', 'filename'
        
    def create_filename_from_user_template(self, filename_template, 
                                           valid_init_time_info, init_time):
        """! Creates a file name for stat_analysis output based on user 
             requested template
                 
             Args:
                filename_template - string with the string substitution
                                    information to be filled
                valid_init_time_info - dictionary containing the
                                       valid and initialization hour
                                       information
                init_time - integer for containing the initialization
                            date information (is -1 if looping over
                            valid times)

             Returns:
                filled_tmpl - string filled with the valid and 
                              initialization time information for
                              a filename
        """
        time_info_valid_beg = valid_init_time_info["FCST_VALID_BEG"].replace("_", "")
        time_info_valid_end = valid_init_time_info["FCST_VALID_END"].replace("_", "")
        time_info_valid_hour = valid_init_time_info["FCST_VALID_HOUR"].replace('"','').split(",")
        time_info_init_beg = valid_init_time_info["FCST_INIT_BEG"].replace("_", "")
        time_info_init_end = valid_init_time_info["FCST_INIT_END"].replace("_", "")
        time_info_init_hour = valid_init_time_info["FCST_INIT_HOUR"].replace('"','').split(",")
        #for init_time = -1 (looping over init date): time_info_init_beg, time_info_init_end, time_info_valid_hour are always used together
        #for init_time != -1 (looping over valid date): time_info_valid_beg, time_info_valid_end, time_info_init_hour are always used together
        #dummy date: 1900010100
        if init_time == -1:
            #build valid_time_filename
            valid_time_filename = time_info_valid_beg
            if time_info_valid_beg != time_info_valid_end:
                match = re.search(r'.*\{valid\?fmt=(.*?[%H])\}', filename_template)
                if match:
                    self.logger.error("Please include valid hour group times in template defined in METplus conf file using VALID_HOUR_BEG and VALID_HOUR_END")
                    exit(1)
            #build init_time_filename
            if len(time_info_init_hour) == 1:
                init_time_filename = "19000101"+time_info_init_hour[0]
                #check that init format makes sense in template
                match = re.search(r'.*\{init\?fmt=(.*?)\}', filename_template)
                if match:
                    if match.group(1) != '%H':
                        self.logger.error("Only accepted format {init?fmt=%H}")
                        exit(1)
            else:
                init_time_filename = "19000101000000"
                match = re.search(r'.*\{init\?fmt=(.*?)\}', filename_template)
                if match:
                    self.logger.error("Please include init hour group times in template defined in METplus conf file using INIT_HOUR_BEG and INIT_HOUR_END")
                    exit(1)
        else:
            init_time_filename =  time_info_init_beg
            #build init_time_filename
            if time_info_init_beg != time_info_init_end:
                match = re.search(r'.*\{init\?fmt=(.*?[%H])\}', filename_template)
                if match:
                    self.logger.error("Please include init hour group times in template defined in METplus conf file using INIT_HOUR_BEG and INIT_HOUR_END")
                    exit(1)
            #build valid_time_filename
            if len(time_info_valid_hour) == 1:
                valid_time_filename = "19000101"+time_info_valid_hour[0]
                #check that valid format makes sense in template
                match = re.search(r'.*\{valid\?fmt=(.*?)\}', filename_template)
                if match:
                    if match.group(1) != '%H':
                        self.logger.error("Only accepted format {valid?fmt=%H}")
                        exit(1)
            else:
                valid_time_filename = "19000101000000"
                match = re.search(r'.*\{valid\?fmt=(.*?)\}', filename_template)
                if match:
                    self.logger.error("Please include valid hour group times in template defined in METplus conf file using VALID_HOUR_BEG and VALID_HOUR_END")
                    exit(1)
        #split into chunks to deal with directories
        tmpl_time_info = {"valid": datetime.datetime.strptime(valid_time_filename, "%Y%m%d%H%M%S"),
                          "init": datetime.datetime.strptime(init_time_filename, "%Y%m%d%H%M%S")
                         }
        tmpl_split = filename_template.split("/")
        filled_tmpl = ""
        for tmpl_chunk in tmpl_split:
            if "?fmt=%" in tmpl_chunk:
                tmpl_chunkSts = sts.StringSub(self.logger,
                                              tmpl_chunk,
                                              **tmpl_time_info)
                filled_tmpl_chunk = tmpl_chunkSts.doStringSub()
            else:
                filled_tmpl_chunk = tmpl_chunk
            filled_tmpl = os.path.join(filled_tmpl, filled_tmpl_chunk)
        return filled_tmpl
    
    class ValidInitTimesPairs(object):
        __slots__ = 'valid', 'init'

    def pair_valid_init_times(self, valid_hour_list, valid_method,
                              init_hour_list, init_method):
        """! Pairs the valid and initialization hour information
                 
             Args:
                valid_hour_list - foramatted valid hours from
                                  create_hour_group_list
                valid_method - string of how to treat valid hour
                               information, either GROUP or LOOP
                init_hour_list - foramatted initialization hours from
                                 create_hour_group_list
                init_method - string of how to treat initialization hour
                              information, either GROUP or LOOP

             Returns:
                valid_init_time_pairs - list of objects with the 
                                        valid and initialization hour
                                        information
        """
        valid_init_time_pairs = []
        if valid_method == "GROUP" and init_method == "LOOP":
            for init_hour in init_hour_list.split(", "):
                pair = self.ValidInitTimesPairs()
                pair.valid = valid_hour_list
                pair.init = init_hour
                valid_init_time_pairs.append(pair)
        elif valid_method == "LOOP" and init_method == "GROUP":
            for valid_hour in valid_hour_list.split(", "):
                pair = self.ValidInitTimesPairs()
                pair.valid = valid_hour
                pair.init = init_hour_list
                valid_init_time_pairs.append(pair)
        elif valid_method == "LOOP" and init_method == "LOOP":
            for init_hour in init_hour_list.split(", "):
                for valid_hour in valid_hour_list.split(", "):
                    pair = self.ValidInitTimesPairs()
                    pair.valid = valid_hour
                    pair.init = init_hour
                    valid_init_time_pairs.append(pair)
        elif valid_method == "GROUP" and init_method == "GROUP":
            pair = self.ValidInitTimesPairs()
            pair.valid = valid_hour_list
            pair.init = init_hour_list
            valid_init_time_pairs.append(pair)
        return valid_init_time_pairs


    class FieldObj(object):
        __slots__ = 'name', 'plot_name', 'dir', 'obs'

    def parse_model_list(self):
        """! Parse metplus_final.conf for model information
             
             Args:
                
             Returns:
                 model_list - list of objects containing
                              model information
        """
        model_list = []
        all_conf = self.config.keys('config')
        model_indices = []
        regex = re.compile("MODEL(\d+)_NAME$")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                model_indices.append(result.group(1))
        for m in model_indices:
            if self.config.has_option('config', "MODEL"+m+"_NAME"):
                model_name = self.config.getstr('config', "MODEL"+m+"_NAME")
                if self.config.has_option('config', "MODEL"+m+"_NAME_ON_PLOT"):
                    model_plot_name = self.config.getstr('config', "MODEL"+m+"_NAME_ON_PLOT")
                else:
                    model_plot_name = model_name
                if self.config.has_option('config', "MODEL"+m+"_STAT_DIR"):
                    model_dir = self.config.getraw('config', "MODEL"+m+"_STAT_DIR")
                else:
                    self.logger.error("MODEL"+m+"_STAT_DIR not defined in METplus conf file")
                    exit(1)
                if self.config.has_option('config', "MODEL"+m+"_OBS_NAME"):
                    model_obs_name = self.config.getstr('config', "MODEL"+m+"_OBS_NAME") 
                else:
                    self.logger.error("MODEL"+m+"_OBS_NAME not defined in METplus conf file")
                    exit(1)
            else:
                self.logger.error("MODEL"+m+"_NAME not defined in METplus conf file")
                exit(1)

            mod = self.FieldObj()
            mod.name = model_name
            mod.plot_name = model_plot_name
            mod.dir = model_dir
            mod.obs = model_obs_name
            model_list.append(mod)
        return model_list
    
    class FourierDecompInfo(object):
        __slots__ = 'run_fourier', 'wave_num_pairings'

    def parse_var_fourier_decomp(self):
        """! Parse metplus_final.conf for variable information
             on the Fourier decomposition
             
             Args:
                
             Returns:
                 fourier_decom_list - list of objects containing
                                      Fourier decomposition information
                                      for the variables
        """
        fourier_decom_list = []
        all_conf = self.config.keys('config')
        indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                indices.append(result.group(1))
        for n in indices:
            if self.config.has_option('config', "FCST_VAR"+n+"_NAME"):
                levels = util.getlist(self.config.getstr('config', "FCST_VAR"+n+"_LEVELS"))
                run_fourier = self.config.getbool('config', "VAR"+n+"_FOURIER_DECOMP", False)
                fourier_wave_num_pairs = util.getlist(self.config.getstr('config', "VAR"+n+"_WAVE_NUM_LIST", ""))
                if run_fourier == False:
                    fourier_wave_num_pairs = ""
                for level in levels:
                    fd_info = self.FourierDecompInfo()
                    fd_info.run_fourier = run_fourier
                    fd_info.wave_num_pairings = fourier_wave_num_pairs
                    fourier_decom_list.append(fd_info)
        return fourier_decom_list
   
    def thresh_format(self, thresh):
        """! Format the variable threshhold information using symbols and
             letters
 
             Args:
                 thresh - string containing the threshold information
                
             Returns:
                 thresh_symbol - string containing the threshold 
                                 formatted using symbols
                 thresh_letters - string containing the threshold 
                                  formatted using letters
        """
        if "ge" or ">=" in thresh:
            thresh_value = thresh.replace("ge", "").replace(">=", "")
            thresh_symbol = ">="+thresh_value
            thresh_letters = "ge"+thresh_value
        elif "gt" or ">" in thresh:
            thresh_value = thresh.replace("gt", "").replace(">", "")
            thresh_symbol = ">"+thresh_value
            thresh_letters = "gt"+thresh_value
        elif "le" or "<=" in thresh:
            thresh_value = thresh.replace("le", "").replace("<=", "")
            thresh_symbol = "<="+thresh_value
            thresh_letters = "le"+thresh_value
        elif "lt" or "<" in thresh:
            thresh_value = thresh.replace("lt", "").replace("<", "")
            thresh_symbol = "<"+thresh_value
            thresh_letters = "lt"+thresh_value
        elif "eq" or "==" in thresh:
            thresh_value = thresh.replace("eq", "").replace("==", "")
            thresh_symbol = "=="+thresh_value
            thresh_letters = "eq"+thresh_value
        elif "ne" or "!=" in thresh:
            thresh_value = thresh.replace("ne", "").replace("!=", "")
            thresh_symbol = "!="+thresh_value
            thresh_letters = "ne"+thresh_value
        else:
             self.logger.error("Threshold operator not valid "+thresh)
             exit(1)
        return thresh_symbol, thresh_letters
 
    def gather_by_date(self, init_time, valid_time):
        """! Runs with run_at_time. Runs stat_analysis filtering file
             stat information for a single date
 
             Args:
                 init_time - string containing the initialization time
                             as %Y%m%d%H%M%S, set to -1 if looping
                             over valid time
                 valid_time - string containing the valid time as 
                              %Y%m%d%H%M%S, set to -1 if looping
                              over initialization time
                
             Returns:
        """
        #read config
        model_name = self.config.getstr('config', 'MODEL')
        obs_name = self.config.getstr('config', 'OBTYPE')
        valid_hour_method = self.config.getstr('config', 'VALID_HOUR_METHOD')
        valid_hour_beg = self.config.getstr('config', 'VALID_HOUR_BEG')
        valid_hour_end = self.config.getstr('config', 'VALID_HOUR_END')
        valid_hour_increment = self.config.getstr('config', 'VALID_HOUR_INCREMENT')
        init_hour_method = self.config.getstr('config', 'INIT_HOUR_METHOD')
        init_hour_beg = self.config.getstr('config', 'INIT_HOUR_BEG')
        init_hour_end = self.config.getstr('config', 'INIT_HOUR_END')
        init_hour_increment = self.config.getstr('config', 'INIT_HOUR_INCREMENT')
        stat_analysis_lookin_dir = self.config.getdir('STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.config.getdir('STAT_ANALYSIS_OUTPUT_DIR')
        stat_analysis_config = self.config.getstr('config', 'STAT_ANALYSIS_CONFIG')
        job_name = self.config.getstr('config', 'JOB_NAME')
        job_args = self.config.getstr('config', 'JOB_ARGS')
        desc = util.getlist(self.config.getstr('config', 'DESC', ""))
        fcst_lead = util.getlist(self.config.getstr('config', 'FCST_LEAD', ""))
        fcst_var_name = util.getlist(self.config.getstr('config', 'FCST_VAR_NAME', ""))
        fcst_var_level = util.getlist(self.config.getstr('config', 'FCST_VAR_LEVEL', ""))
        obs_var_name = util.getlist(self.config.getstr('config', 'OBS_VAR_NAME', ""))
        obs_var_level = util.getlist(self.config.getstr('config', 'OBS_VAR_LEVEL', ""))
        region = util.getlist(self.config.getstr('config', 'REGION', ""))
        interp = util.getlist(self.config.getstr('config', 'INTERP', ""))
        interp_pts = util.getlist(self.config.getstr('config', 'INTERP_PTS', ""))
        fcst_thresh_from_config = util.getlist(self.config.getstr('config', 'FCST_THRESH', ""))
        fcst_thresh = []
        for ft in fcst_thresh_from_config:
            fcst_thresh_symbol, fcst_thresh_letters = self.thresh_format(ft)
            fcst_thresh.append(fcst_thresh_symbol)
        fcst_thresh = ', '.join(fcst_thresh)
        cov_thresh = util.getlist(self.config.getstr('config', 'COV_THRESH', ""))
        line_type = util.getlist(self.config.getstr('config', 'LINE_TYPE', ""))
        #set envir vars based on config
        self.add_env_var('MODEL', '"'+model_name+'"')
        self.add_env_var('OBS_NAME', '"'+obs_name+'"')
        self.add_env_var('DESC', self.create_variable_list(desc))
        self.add_env_var('FCST_LEAD', self.create_variable_list(fcst_lead))
        self.add_env_var('FCST_VAR_NAME', self.create_variable_list(fcst_var_name))
        self.add_env_var('FCST_VAR_LEVEL', self.create_variable_list(fcst_var_level))
        self.add_env_var('OBS_VAR_NAME', self.create_variable_list(obs_var_name))
        self.add_env_var('OBS_VAR_LEVEL', self.create_variable_list(obs_var_level))
        self.add_env_var('REGION', self.create_variable_list(region))
        self.add_env_var('INTERP', self.create_variable_list(interp))
        self.add_env_var('INTERP_PTS', self.create_variable_list(interp_pts))
        self.add_env_var('FCST_THRESH', fcst_thresh)
        self.add_env_var('COV_THRESH', self.create_variable_list(cov_thresh))
        self.add_env_var('LINE_TYPE', self.create_variable_list(line_type))
        #set up lookin agrument
        if "*" in stat_analysis_lookin_dir: 
            for_stat_analysis_lookin = subprocess.check_output("ls -d "+stat_analysis_lookin_dir, shell=True).rstrip('\n')
        else:
            for_stat_analysis_lookin = stat_analysis_lookin_dir
        self.set_lookin_dir(for_stat_analysis_lookin)
        #set up stat_analysis output options based conf file info
        stat_analysis_dump_row_info = self.StatAnalysisOutputInfo()
        if "-dump_row" in job_args:
            stat_analysis_dump_row_tmpl = self.config.getraw('filename_templates','STAT_ANALYSIS_DUMP_ROW_TMPL')
            if len(stat_analysis_dump_row_tmpl) == 0:
                self.logger.debug("-dump_row requested but no STAT_ANALYSIS_DUMP_ROW_TMPL in conf file under filename_templates....using code default")
                stat_analysis_dump_row_info.template_type = "default_template"
                if init_time == -1:
                    stat_analysis_dump_row_info.filename_template = model_name+"_"+obs_name+"_valid"+valid_time[0:8]
                else:
                    stat_analysis_dump_row_info.filename_template = model_name+"_"+obs_name+"_init"+init_time[0:8]
            else:
                self.logger.debug("Using user customed STAT_ANALYSIS_DUMP_ROW_TMPL defined in conf file under filename_templates")
                stat_analysis_dump_row_info.template_type = "user_template"
                stat_analysis_dump_row_info.filename_template = stat_analysis_dump_row_tmpl
                stat_analysis_dump_row_info.filename = ""
        else:
            stat_analysis_dump_row_info.template_type = "NA"
            stat_analysis_dump_row_info.filename_template = "NA"
            stat_analysis_dump_row_info.filename = "NA"
        stat_analysis_out_stat_info = self.StatAnalysisOutputInfo()
        if "-out_stat" in job_args:
            stat_analysis_out_stat_tmpl = self.config.getraw('filename_templates','STAT_ANALYSIS_OUT_STAT_TMPL')
            if len(stat_analysis_out_stat_tmpl) == 0:
                self.logger.debug("-out_stat requested but no STAT_ANALYSIS_OUT_STAT_TMPL in conf file under filename_templates....using code default")
                stat_analysis_out_stat_info.template_type = "default_template"
                stat_analysis_out_stat_info.filename_template = ""
                if init_time == -1:
                    stat_analysis_out_stat_info.filename_template = model_name+"_"+obs_name+"_valid"+valid_time[0:8]
                else:
                    stat_analysis_out_stat_info.filename_template = model_name+"_"+obs_name+"_init"+init_time[0:8]
            else:
                self.logger.debug("Using user customed STAT_ANALYSIS_OUT_STAT_TMPL defined in conf file under filename_templates")
                stat_analysis_out_stat_info.template_type = "user_template"
                stat_analysis_out_stat_info.filename_template = stat_analysis_out_stat_tmpl
                stat_analysis_out_stat_info.filename = ""
        else:
            stat_analysis_out_stat_info.template_type = "NA"
            stat_analysis_out_stat_info.filename_template = "NA"
            stat_analysis_out_stat_info.filename = "NA"
        #set up valid and initialization information for MET config file and run stat_analysis
        valid_beg = calendar.timegm(time.strptime(valid_hour_beg, "%H%M"))
        valid_end = calendar.timegm(time.strptime(valid_hour_end, "%H%M"))
        valid_interval = int(valid_hour_increment)
        init_beg = calendar.timegm(time.strptime(init_hour_beg, "%H%M"))
        init_end = calendar.timegm(time.strptime(init_hour_end, "%H%M"))
        init_interval = int(init_hour_increment)
        if valid_hour_method == "GROUP" and init_hour_method == "LOOP":
            init_now = init_beg
            while init_now <= init_end:
                init_now_str = str(time.strftime("%H%M%S", time.gmtime(init_now)))
                if init_time == -1:
                    fcst_valid_init_dict = {
                        "FCST_VALID_BEG": str(valid_time[0:8])+'_'+valid_hour_beg+"00",
                        "FCST_VALID_END": str(valid_time[0:8])+'_'+valid_hour_end+"00",
                        "FCST_VALID_HOUR": "",
                        "FCST_INIT_BEG": "",
                        "FCST_INIT_END": "",
                        "FCST_INIT_HOUR": '"'+init_now_str+'"'
                    }
                else:
                    valid_hour_group_list = self.create_hour_group_list(valid_beg, valid_end, valid_interval)
                    fcst_valid_init_dict = {
                        "FCST_VALID_BEG": "",
                        "FCST_VALID_END": "",
                        "FCST_VALID_HOUR": valid_hour_group_list,
                        "FCST_INIT_BEG": str(init_time[0:8])+'_'+init_now_str,
                        "FCST_INIT_END": str(init_time[0:8])+'_'+init_now_str,
                        "FCST_INIT_HOUR": ""
                    }
                if stat_analysis_dump_row_info.template_type == "default_template":
                    stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_now_str[0:5]+"Z_dumprow.stat"
                elif stat_analysis_dump_row_info.template_type == "user_template":
                    stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
                if stat_analysis_out_stat_info.template_type == "default_template":
                    stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_now_str[0:5]+"Z_outstat.stat"
                elif stat_analysis_out_stat_info.template_type == "user_template":
                    stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
                job = self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
                self.set_param_file(stat_analysis_config)
                #print stat_analysis run settings
                self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
                for name, value in fcst_valid_init_dict.items():
                    self.add_env_var(name, value)
                    self.logger.debug(name+": "+value)
                self.logger.debug('MODEL: '+'"'+model_name+'"')
                self.logger.debug('OBTYPE: '+'"'+obs_name+'"')
                self.logger.debug('DESC: '+self.create_variable_list(desc))
                self.logger.debug('FCST_LEAD: '+self.create_variable_list(fcst_lead))
                self.logger.debug('FCST_VAR_NAME: '+self.create_variable_list(fcst_var_name))
                self.logger.debug('FCST_VAR_LEVEL: '+self.create_variable_list(fcst_var_level))
                self.logger.debug('OBS_VAR_NAME: '+self.create_variable_list(obs_var_name))
                self.logger.debug('OBS_VAR_LEVEL: '+self.create_variable_list(obs_var_level))
                self.logger.debug('REGION: '+self.create_variable_list(region))
                self.logger.debug('INTERP: '+self.create_variable_list(interp))
                self.logger.debug('INTERP_PTS: '+self.create_variable_list(interp_pts))
                self.logger.debug('FCST_THRESH: '+fcst_thresh)
                self.logger.debug('COV_THRESH: '+self.create_variable_list(cov_thresh))
                self.logger.debug('LINE_TYPE: '+self.create_variable_list(line_type))
                self.logger.debug("JOB: "+job)
                self.logger.debug("lookin directory: "+for_stat_analysis_lookin)
                #build command
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("stat_analysis could not generate command")
                    return
                self.build()
                self.clear()
                init_now += init_interval
        elif valid_hour_method == "LOOP" and init_hour_method == "GROUP":
            valid_now = valid_beg
            while valid_now <= valid_end:
                valid_now_str = str(time.strftime("%H%M%S", time.gmtime(valid_now)))
                if init_time == -1:
                    init_hour_group_list = self.create_hour_group_list(init_beg, init_end, init_interval)
                    fcst_valid_init_dict = {
                        "FCST_VALID_BEG": str(valid_time[0:8])+'_'+valid_now_str,
                        "FCST_VALID_END": str(valid_time[0:8])+'_'+valid_now_str,
                        "FCST_VALID_HOUR": "",
                        "FCST_INIT_BEG": "",
                        "FCST_INIT_END": "",
                        "FCST_INIT_HOUR": init_hour_group_list
                    }
                else:
                    fcst_valid_init_dict = {
                        "FCST_VALID_BEG": "",
                        "FCST_VALID_END": "",
                        "FCST_VALID_HOUR": '"'+valid_now_str+'"',
                        "FCST_INIT_BEG": str(init_time[0:8])+'_'+init_hour_beg+"00",
                        "FCST_INIT_END": str(init_time[0:8])+'_'+init_hour_end+"00",
                        "FCST_INIT_HOUR": ""
                    }
                if stat_analysis_dump_row_info.template_type == "default_template":
                    stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_dumprow.stat"
                elif stat_analysis_dump_row_info.template_type == "user_template":
                    stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
                if stat_analysis_out_stat_info.template_type == "default_template":
                    stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_outstat.stat"
                elif stat_analysis_out_stat_info.template_type == "user_template":
                    stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
                job = self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
                self.set_param_file(stat_analysis_config)
                #print stat_analysis run settings
                self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
                for name, value in fcst_valid_init_dict.items():
                    self.add_env_var(name, value)
                    self.logger.debug(name+": "+value)
                self.logger.debug('MODEL: '+'"'+model_name+'"')
                self.logger.debug('OBTYPE: '+'"'+obs_name+'"')
                self.logger.debug('DESC: '+self.create_variable_list(desc))
                self.logger.debug('FCST_LEAD: '+self.create_variable_list(fcst_lead))
                self.logger.debug('FCST_VAR_NAME: '+self.create_variable_list(fcst_var_name))
                self.logger.debug('FCST_VAR_LEVEL: '+self.create_variable_list(fcst_var_level))
                self.logger.debug('OBS_VAR_NAME: '+self.create_variable_list(obs_var_name))
                self.logger.debug('OBS_VAR_LEVEL: '+self.create_variable_list(obs_var_level))
                self.logger.debug('REGION: '+self.create_variable_list(region))
                self.logger.debug('INTERP: '+self.create_variable_list(interp))
                self.logger.debug('INTERP_PTS: '+self.create_variable_list(interp_pts))
                self.logger.debug('FCST_THRESH: '+fcst_thresh)
                self.logger.debug('COV_THRESH: '+self.create_variable_list(cov_thresh))
                self.logger.debug('LINE_TYPE: '+self.create_variable_list(line_type))
                self.logger.debug("JOB: "+job)
                self.logger.debug("lookin directory: "+for_stat_analysis_lookin)
                #build command
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("stat_analysis could not generate command")
                    return
                self.build()
                self.clear()
                valid_now += valid_interval
        elif valid_hour_method == "LOOP" and init_hour_method == "LOOP":
            init_now = init_beg
            while init_now <= init_end:
                init_now_str = str(time.strftime("%H%M%S", time.gmtime(init_now)))
                valid_now = valid_beg
                while valid_now <= valid_end:
                    valid_now_str = str(time.strftime("%H%M%S", time.gmtime(valid_now)))
                    if init_time == -1:
                        fcst_valid_init_dict = {
                            "FCST_VALID_BEG": str(valid_time[0:8])+'_'+valid_now_str,
                            "FCST_VALID_END": str(valid_time[0:8])+'_'+valid_now_str,
                            "FCST_VALID_HOUR": "",
                            "FCST_INIT_BEG": "",
                            "FCST_INIT_END": "",
                            "FCST_INIT_HOUR": '"'+init_now_str+'"'
                        }
                    else:
                        fcst_valid_init_dict = {
                            "FCST_VALID_BEG": "",
                            "FCST_VALID_END": "",
                            "FCST_VALID_HOUR": '"'+valid_now_str+'"',
                            "FCST_INIT_BEG": str(init_time[0:8])+'_'+init_now_str,
                            "FCST_INIT_END": str(init_time[0:8])+'_'+init_now_str,
                            "FCST_INIT_HOUR": ""
                        }
                    if stat_analysis_dump_row_info.template_type == "default_template":
                        stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_now_str[0:5]+"Z_dumprow.stat"
                    elif stat_analysis_dump_row_info.template_type == "user_template":
                        stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
                    if stat_analysis_out_stat_info.template_type == "default_template":
                        stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_now_str[0:5]+"Z_outstat.stat"
                    elif stat_analysis_out_stat_info.template_type == "user_template":
                        stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
                    job = self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
                    self.set_param_file(stat_analysis_config)
                    #print stat_analysis run settings
                    self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
                    for name, value in fcst_valid_init_dict.items():
                        self.add_env_var(name, value)
                        self.logger.debug(name+": "+value)
                    self.logger.debug('MODEL: '+'"'+model_name+'"')
                    self.logger.debug('OBTYPE: '+'"'+obs_name+'"')
                    self.logger.debug('DESC: '+self.create_variable_list(desc))
                    self.logger.debug('FCST_LEAD: '+self.create_variable_list(fcst_lead))
                    self.logger.debug('FCST_VAR_NAME: '+self.create_variable_list(fcst_var_name))
                    self.logger.debug('FCST_VAR_LEVEL: '+self.create_variable_list(fcst_var_level))
                    self.logger.debug('OBS_VAR_NAME: '+self.create_variable_list(obs_var_name))
                    self.logger.debug('OBS_VAR_LEVEL: '+self.create_variable_list(obs_var_level))
                    self.logger.debug('REGION: '+self.create_variable_list(region))
                    self.logger.debug('INTERP: '+self.create_variable_list(interp))
                    self.logger.debug('INTERP_PTS: '+self.create_variable_list(interp_pts))
                    self.logger.debug('FCST_THRESH: '+fcst_thresh)
                    self.logger.debug('COV_THRESH: '+self.create_variable_list(cov_thresh))
                    self.logger.debug('LINE_TYPE: '+self.create_variable_list(line_type))
                    self.logger.debug("JOB: "+job)
                    self.logger.debug("lookin directory: "+for_stat_analysis_lookin)
                    #build command
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("stat_analysis could not generate command")
                        return
                    self.build()
                    self.clear()
                    valid_now += valid_interval
                init_now += init_interval
        elif valid_hour_method == "GROUP" and init_hour_method == "GROUP":
            if init_time == -1:
                init_hour_group_list = self.create_hour_group_list(init_beg, init_end, init_interval)
                fcst_valid_init_dict = {
                    "FCST_VALID_BEG": str(valid_time[0:8])+'_'+valid_hour_beg+"00",
                    "FCST_VALID_END": str(valid_time[0:8])+'_'+valid_hour_end+"00",
                    "FCST_VALID_HOUR": "",
                    "FCST_INIT_BEG": "",
                    "FCST_INIT_END": "",
                    "FCST_INIT_HOUR": init_hour_group_list
                }
            else:
                valid_hour_group_list = self.create_hour_group_list(valid_beg, valid_end, valid_interval)
                fcst_valid_init_dict = {
                    "FCST_VALID_BEG": "",
                    "FCST_VALID_END": "",
                    "FCST_VALID_HOUR": valid_hour_group_list,
                    "FCST_INIT_BEG": str(init_time[0:8])+'_'+init_hour_beg+"00",
                    "FCST_INIT_END": str(init_time[0:8])+'_'+init_hour_end+"00",
                    "FCST_INIT_HOUR": ""
                }
            if stat_analysis_dump_row_info.template_type == "default_template":
                stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_dumprow.stat"
            elif stat_analysis_dump_row_info.template_type == "user_template":
                stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
            if stat_analysis_out_stat_info.template_type == "default_template":
                stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_outstat.stat"
            elif stat_analysis_out_stat_info.template_type == "user_template":
                stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
            job = self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
            self.set_param_file(stat_analysis_config)
            #print stat_analysis run settings
            self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
            for name, value in fcst_valid_init_dict.items():
                self.add_env_var(name, value)
                self.logger.debug(name+": "+value)
            self.logger.debug('MODEL: '+'"'+model_name+'"')
            self.logger.debug('OBTYPE: '+'"'+obs_name+'"')
            self.logger.debug('DESC: '+self.create_variable_list(desc))
            self.logger.debug('FCST_LEAD: '+self.create_variable_list(fcst_lead))
            self.logger.debug('FCST_VAR_NAME: '+self.create_variable_list(fcst_var_name))
            self.logger.debug('FCST_VAR_LEVEL: '+self.create_variable_list(fcst_var_level))
            self.logger.debug('OBS_VAR_NAME: '+self.create_variable_list(obs_var_name))
            self.logger.debug('OBS_VAR_LEVEL: '+self.create_variable_list(obs_var_level))
            self.logger.debug('REGION: '+self.create_variable_list(region))
            self.logger.debug('INTERP: '+self.create_variable_list(interp))
            self.logger.debug('INTERP_PTS: '+self.create_variable_list(interp_pts))
            self.logger.debug('FCST_THRESH: '+fcst_thresh)
            self.logger.debug('COV_THRESH: '+self.create_variable_list(cov_thresh))
            self.logger.debug('LINE_TYPE: '+self.create_variable_list(line_type))
            self.logger.debug("JOB: "+job)
            self.logger.debug("lookin directory: "+for_stat_analysis_lookin)
            #build command
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("stat_analysis could not generate command")
                return
            self.build()
            self.clear()
        else:
            self.logger.error("Invalid conf entry for VALID_HOUR_METHOD or INIT_HOUR_METHOD, use 'GROUP' or 'LOOP'")
            exit(1)


    def gather_by_info(self):
        """! Runs with run_all_times. Runs stat_analysis filtering file
             stat information for a span of dates looking for specific
             criteria
 
             Args:
 
             Returns:
        """
        #read config
        verif_case = self.config.getstr('config', 'VERIF_CASE')
        verif_type = self.config.getstr('config', 'VERIF_TYPE')
        plot_time = self.config.getstr('config', 'PLOT_TIME')
        valid_beg_YYYYmmdd = self.config.getstr('config', 'VALID_BEG', "")
        valid_end_YYYYmmdd = self.config.getstr('config', 'VALID_END', "")
        valid_hour_method = self.config.getstr('config', 'VALID_HOUR_METHOD')
        valid_hour_beg = self.config.getstr('config', 'VALID_HOUR_BEG')
        valid_hour_end = self.config.getstr('config', 'VALID_HOUR_END')
        valid_hour_increment = self.config.getstr('config', 'VALID_HOUR_INCREMENT')
        init_beg_YYYYmmdd = self.config.getstr('config', 'INIT_BEG', "")
        init_end_YYYYmmdd = self.config.getstr('config', 'INIT_END', "")
        init_hour_method = self.config.getstr('config', 'INIT_HOUR_METHOD')
        init_hour_beg = self.config.getstr('config', 'INIT_HOUR_BEG')
        init_hour_end = self.config.getstr('config', 'INIT_HOUR_END')
        init_hour_increment = self.config.getstr('config', 'INIT_HOUR_INCREMENT')
        stat_analysis_out_dir = self.config.getdir('STAT_ANALYSIS_OUTPUT_DIR')
        stat_analysis_config = self.config.getstr('config', 'STAT_ANALYSIS_CONFIG')
        model_list = self.parse_model_list()
        var_list = util.parse_var_list(self.config)
        fourier_decom_list = self.parse_var_fourier_decomp()
        region_list = util.getlist(self.config.getstr('config', 'REGION_LIST'))
        lead_list = util.getlist(self.config.getstr('config', 'LEAD_LIST'))
        line_type = util.getlist(self.config.getstr('config', 'LINE_TYPE', ""))
        #set envir vars based on config
        util.mkdir_p(stat_analysis_out_dir)
        self.add_env_var('LINE_TYPE', self.create_variable_list(line_type))
        #build valid and init hour information
        valid_beg_HHMMSS = calendar.timegm(time.strptime(valid_hour_beg, "%H%M"))
        valid_end_HHMMSS = calendar.timegm(time.strptime(valid_hour_end, "%H%M"))
        init_beg_HHMMSS = calendar.timegm(time.strptime(init_hour_beg, "%H%M"))
        init_end_HHMMSS = calendar.timegm(time.strptime(init_hour_end, "%H%M"))
        valid_hour_list = self.create_hour_group_list(valid_beg_HHMMSS, valid_end_HHMMSS, int(valid_hour_increment))
        init_hour_list = self.create_hour_group_list(init_beg_HHMMSS, init_end_HHMMSS, int(init_hour_increment))
        valid_init_time_pairs = self.pair_valid_init_times(valid_hour_list, valid_hour_method, init_hour_list, init_hour_method)
        #loop through time information
        for valid_init_time_pair in valid_init_time_pairs:
            valid_time_info = valid_init_time_pair.valid
            init_time_info = valid_init_time_pair.init
            if plot_time == 'valid':
                 fcst_valid_init_dict = {
                        "FCST_INIT_BEG": "",
                        "FCST_INIT_END": "",
                        "FCST_INIT_HOUR": init_time_info,
                        "FCST_VALID_HOUR": valid_time_info
                        }
                 stat_analysis_out_dir_date = "valid"+valid_beg_YYYYmmdd+"to"+valid_end_YYYYmmdd
                 if len(init_time_info.split(", ")) == 1:
                     stat_analysis_out_dir_init_time = "init"+init_time_info.replace('"', "")+"to"+init_time_info.replace('"', "")+"Z"
                 else:
                     stat_analysis_out_dir_init_time = "init"+init_time_info.replace('"', "").split(", ")[0]+"to"+init_time_info.replace('"', "").split(", ")[-1]+"Z"
                 if len(valid_time_info.split(", ")) == 1:
                     fcst_valid_init_dict['FCST_VALID_BEG'] = valid_beg_YYYYmmdd+"_"+valid_time_info.replace('"', "")
                     fcst_valid_init_dict['FCST_VALID_END'] = valid_end_YYYYmmdd+"_"+valid_time_info.replace('"', "")
                     stat_analysis_out_dir_valid_time = "valid"+valid_time_info.replace('"', "")+"to"+valid_time_info.replace('"', "")+"Z"
                 else:
                     fcst_valid_init_dict['FCST_VALID_BEG'] = valid_beg_YYYYmmdd+"_"+valid_time_info.replace('"', "").split(", ")[0]
                     fcst_valid_init_dict['FCST_VALID_END'] = valid_end_YYYYmmdd+"_"+valid_time_info.replace('"', "").split(", ")[-1]
                     stat_analysis_out_dir_valid_time = "valid"+valid_time_info.replace('"', "").split(", ")[0]+"to"+valid_time_info.replace('"', "").split(", ")[-1]+"Z"
            elif plot_time == 'init':
                 fcst_valid_init_dict = {
                        "FCST_VALID_BEG": "",
                        "FCST_VALID_END": "",
                        "FCST_VALID_HOUR": valid_time_info,
                        "FCST_INIT_HOUR": init_time_info
                        }
                 stat_analysis_out_dir_date = "init"+init_beg_YYYYmmdd+"to"+init_end_YYYYmmdd
                 if len(valid_time_info.split(", ")) == 1:
                     stat_analysis_out_dir_valid_time = "valid"+valid_time_info.replace('"', "")+"to"+valid_time_info.replace('"', "")+"Z"
                 else:
                     stat_analysis_out_dir_valid_time = "valid"+valid_time_info.replace('"', "").split(", ")[0]+"to"+valid_time_info.replace('"', "").split(", ")[-1]+"Z"
                 if len(init_time_info.split(", ")) == 1:
                     fcst_valid_init_dict['FCST_INIT_BEG'] = init_beg_YYYYmmdd+"_"+init_time_info.replace('"', "")
                     fcst_valid_init_dict['FCST_INIT_END'] = init_end_YYYYmmdd+"_"+init_time_info.replace('"', "")
                     stat_analysis_out_dir_init_time = "init"+init_time_info.replace('"', "")+"to"+init_time_info.replace('"', "")+"Z"
                 else:
                     fcst_valid_init_dict['FCST_INIT_BEG'] = init_beg_YYYYmmdd+"_"+init_time_info.replace('"', "").split(", ")[0]
                     fcst_valid_init_dict['FCST_INIT_END'] = init_end_YYYYmmdd+"_"+init_time_info.replace('"', "").split(", ")[-1]
                     stat_analysis_out_dir_init_time = "init"+init_time_info.replace('"', "").split(", ")[0]+"to"+init_time_info.replace('"', "").split(", ")[-1]+"Z"
            else:
                 self.logger.error("Invalid entry for PLOT_TIME, use 'valid' or 'init'")
                 exit(1)
            #loop through variable information
            for var_info in var_list:
                fcst_var_name = var_info.fcst_name
                fcst_var_level = var_info.fcst_level
                fcst_var_thresh_list = var_info.fcst_thresh
                fcst_var_extra = var_info.fcst_extra
                obs_var_name = var_info.obs_name
                obs_var_level = var_info.obs_level
                obs_var_thresh_list = var_info.obs_thresh
                obs_var_extra = var_info.obs_extra
                var_info_index = var_info.index
                self.add_env_var('FCST_VAR_NAME', '"'+fcst_var_name+'"')
                self.add_env_var('FCST_VAR_LEVEL', '"'+fcst_var_level+'"')
                self.add_env_var('OBS_VAR_NAME', '"'+obs_var_name+'"')
                self.add_env_var('OBS_VAR_LEVEL', '"'+obs_var_level+'"')
                #loop through thresholds, need to include if list is empty as these settings are optional
                if fcst_var_thresh_list == [] or obs_var_thresh_list == []:
                    fcst_var_thresh_list = ['']
                    obs_var_thresh_list = ['']
                for fcst_thresh in fcst_var_thresh_list:
                    stat_analysis_dump_row_filename_fcstvar = "fcst"+fcst_var_name+fcst_var_level+fcst_var_extra.replace(" ", "").replace("=","").replace(";","").replace('"','').replace("'","").replace(",","-").replace("_","")
                    stat_analysis_dump_row_filename_obsvar = "obs"+obs_var_name+obs_var_level+obs_var_extra.replace(" ", "").replace("=","").replace(";","").replace('"','').replace("'","").replace(",","-").replace("_","")
                    if len(fcst_thresh) != 0:
                        obs_thresh = obs_var_thresh_list[fcst_var_thresh_list.index(fcst_thresh)]
                        fcst_thresh_symbol, fcst_thresh_letters = self.thresh_format(fcst_thresh)
                        obs_thresh_symbol, obs_thresh_letters = self.thresh_format(obs_thresh)
                        self.add_env_var('FCST_THRESH', fcst_thresh_symbol)
                        self.add_env_var('OBS_THRESH', obs_thresh_symbol)
                        stat_analysis_dump_row_filename_fcstvar = stat_analysis_dump_row_filename_fcstvar+fcst_thresh_letters
                        stat_analysis_dump_row_filename_obsvar = stat_analysis_dump_row_filename_obsvar+obs_thresh_letters
                    else:
                        self.add_env_var('FCST_THRESH', "")
                        self.add_env_var('OBS_THRESH', "")
                    #check for fourier decompositon for variable, add to interp list
                    interp_list = util.getlist(self.config.getstr('config', 'INTERP', ""))
                    var_fourier_decomp_info = fourier_decom_list[var_list.index(var_info)]
                    if var_fourier_decomp_info.run_fourier:
                        for pair in var_fourier_decomp_info.wave_num_pairings:
                            interp_list.append("WV1_"+pair)
                    #loop through interpolation
                    for interp in interp_list:
                        self.add_env_var('INTERP', '"'+interp+'"')
                        stat_analysis_dump_row_filename_interp = "interp"+interp
                        #loop through region information 
                        for region in region_list:
                            self.add_env_var('REGION', '"'+region+'"')
                            stat_analysis_dump_row_filename_region = "region"+region
                            #loop through lead information
                            for lead in lead_list:
                                self.add_env_var('FCST_LEAD', '"'+lead+'"')
                                stat_analysis_dump_row_filename_lead = "f"+lead
                                #loop through model information
                                for model_info in model_list:
                                    model_name = model_info.name
                                    self.add_env_var('MODEL', '"'+model_name+'"')
                                    obs_name = model_info.obs
                                    self.add_env_var('OBS_NAME', '"'+obs_name+'"')
                                    model_dir = model_info.dir
                                    model_dir_split = model_dir.split("/")
                                    model_plot_name = model_info.plot_name
                                    if model_dir[0] == "/":
                                        filled_model_dir = "/"
                                    else:
                                        filled_model_dir = ""
                                    #check to see if string subsitution requested, check formmatting, and fill
                                    if "{valid?fmt=" or "{init?fmt=" in model_dir:
                                        if valid_hour_method == "LOOP" and "{valid?fmt=" in model_dir and "{valid?fmt=%H}" in model_dir:
                                            valid_string_sub_date = "19000101"+valid_time_info.replace('"', "")
                                        elif  valid_hour_method == "LOOP" and "{valid?fmt=" in model_dir and "{valid?fmt=%H}" not in model_dir:
                                            self.logger.error("Invalid use of {valid?fmt= in directory for model "+model_name+"... use {valid?fmt=%H}")
                                            exit(1)
                                        elif valid_hour_method == "GROUP" and "{valid?fmt=" in model_dir:
                                            self.logger.error("Only use {valid?fmt= if VALID_HOUR_METHOD = LOOP")
                                            exit(1)
                                        else:
                                            valid_string_sub_date = "19000101000000"
                                        if init_hour_method == "LOOP" and "{init?fmt=" in model_dir and "{init?fmt=%H}" in model_dir:
                                            init_string_sub_date = "19000101"+init_time_info.replace('"', "")
                                        elif  init_hour_method == "LOOP" and "{init?fmt=" in model_dir and "{init?fmt=%H}" not in model_dir:
                                            self.logger.error("Init use of {init?fmt= in directory for model "+model_name+"... use {init?fmt=%H}")
                                            exit(1)
                                        elif init_hour_method == "GROUP" and "{init?fmt=" in model_dir:
                                            self.logger.error("Only use {init?fmt= if INIT_HOUR_METHOD = LOOP")
                                            exit(1)
                                        else:
                                            init_string_sub_date = "19000101000000"
                                        model_dir_time_info =  {"valid": datetime.datetime.strptime(valid_string_sub_date, "%Y%m%d%H%M%S"),
                                                                "init": datetime.datetime.strptime(init_string_sub_date, "%Y%m%d%H%M%S")
                                                               } 
                                        for model_dir_chunk in model_dir_split:
                                            if "?fmt=%" in model_dir_chunk:
                                                model_dir_chunkSts = sts.StringSub(self.logger,
                                                                                   model_dir_chunk,
                                                                                   **model_dir_time_info)
                                                filled_model_dir_chunk = model_dir_chunkSts.doStringSub()
                                            else:
                                                filled_model_dir_chunk = model_dir_chunk
                                            filled_model_dir = os.path.join(filled_model_dir, filled_model_dir_chunk)
                                    else:
                                        filled_model_dir = model_dir
                                    #check and fill wildcard* directory paths
                                    if "*" in model_dir:
                                        for_stat_analysis_lookin = subprocess.check_output("ls -d "+filled_model_dir, shell=True).rstrip('\n')
                                    else:
                                        for_stat_analysis_lookin = filled_model_dir
                                    #set up lookin agrument
                                    self.set_lookin_dir(for_stat_analysis_lookin)
                                    #set up output directory, job, and dump_row filename
                                    model_stat_analysis_output_dir = os.path.join(stat_analysis_out_dir, verif_case, verif_type, model_plot_name, stat_analysis_out_dir_date+"_"+stat_analysis_out_dir_valid_time+"_"+stat_analysis_out_dir_init_time)
                                    util.mkdir_p(model_stat_analysis_output_dir)
                                    stat_analysis_dump_row_filename = model_plot_name+"_"+stat_analysis_dump_row_filename_lead+"_"+stat_analysis_dump_row_filename_fcstvar+"_"+stat_analysis_dump_row_filename_obsvar+"_"+stat_analysis_dump_row_filename_interp+"_"+stat_analysis_dump_row_filename_region+".stat"
                                    job = "-job filter -dump_row "+os.path.join(model_stat_analysis_output_dir, stat_analysis_dump_row_filename)
                                    self.add_env_var('JOB', job)
                                    self.set_param_file(stat_analysis_config)
                                    #print stat_analysis run settings
                                    self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
                                    for name, value in fcst_valid_init_dict.items():
                                        self.add_env_var(name, value)
                                        self.logger.debug(name+": "+value)
                                    if len(fcst_var_extra) != 0 and len(obs_var_extra) != 0:
                                        self.logger.debug("FCST_VAR_NAME: "+fcst_var_name)
                                        self.logger.debug("FCST_VAR_LEVEL: "+fcst_var_level)
                                        self.logger.debug("FCST_VAR_OPTIONS: "+fcst_var_extra)
                                        self.logger.debug("OBS_VAR_NAME: "+obs_var_name)
                                        self.logger.debug("OBS_VAR_LEVEL: "+obs_var_level)
                                        self.logger.debug("OBS_VAR_OPTIONS: "+obs_var_extra)
                                    elif len(fcst_var_extra) != 0 and len(obs_var_extra) == 0:
                                        self.logger.debug("FCST_VAR_NAME: "+fcst_var_name)
                                        self.logger.debug("FCST_VAR_LEVEL: "+fcst_var_level)
                                        self.logger.debug("FCST_VAR_OPTIONS: "+fcst_var_extra)
                                        self.logger.debug("OBS_VAR_NAME: "+obs_var_name)
                                        self.logger.debug("OBS_VAR_LEVEL: "+obs_var_level)
                                    elif len(fcst_var_extra) == 0 and len(obs_var_extra) != 0:
                                        self.logger.debug("FCST_VAR_NAME: "+fcst_var_name)
                                        self.logger.debug("FCST_VAR_LEVEL: "+fcst_var_level)
                                        self.logger.debug("OBS_VAR_NAME: "+obs_var_name)
                                        self.logger.debug("OBS_VAR_LEVEL: "+obs_var_level)
                                        self.logger.debug("OBS_VAR_OPTIONS: "+obs_var_extra)
                                    elif len(fcst_var_extra) == 0 and len(obs_var_extra) == 0:
                                        self.logger.debug("FCST_VAR_NAME: "+fcst_var_name)
                                        self.logger.debug("FCST_VAR_LEVEL: "+fcst_var_level)
                                        self.logger.debug("OBS_VAR_NAME: "+obs_var_name)
                                        self.logger.debug("OBS_VAR_LEVEL: "+obs_var_level)
                                    if len(fcst_thresh) != 0:
                                        self.logger.debug("FCST_THRESH: "+fcst_thresh_symbol)
                                        self.logger.debug("OBS_THRESH: "+obs_thresh_symbol)
                                    self.logger.debug("INTERP: "+interp) 
                                    self.logger.debug("REGION: "+region)
                                    self.logger.debug("FCST_LEAD: "+lead)
                                    self.logger.debug("MODEL: "+model_name)
                                    self.logger.debug("OBTYPE: "+obs_name)
                                    self.logger.debug("LINE_TYPE: "+self.create_variable_list(line_type))
                                    self.logger.debug("JOB: "+job)
                                    self.logger.debug("lookin directory: "+for_stat_analysis_lookin)
                                    #build command
                                    cmd = self.get_command()
                                    if cmd is None:
                                        self.logger.error("stat_analysis could not generate command")
                                        return
                                    self.build()
                                    self.clear()

    def run_all_times(self):
        self.gather_by_info()

    def run_at_time(self, input_dict):
        if "valid" in input_dict.keys():
            init_time = -1
            valid_time = input_dict["valid"].strftime("%Y%m%d%H%M%S")
        elif "init" in input_dict.keys():
            init_time = input_dict["valid"].strftime("%Y%m%d%H%M%S")
            valid_time = -1
        else:
            self.logger.error("LOOP_BY must be VALID or INIT")
            exit(1)
        self.gather_by_date(init_time, valid_time)
