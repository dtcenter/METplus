#!/usr/bin/env python

'''
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row
Abstract: Runs stat_analysis
History Log:  Second version
Usage: 
Parameters: None
Input Files: ASCII files
Output Files: ASCII files
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
import time
import calendar
import string_template_substitution as sts
from task_info import TaskInfo
from command_builder import CommandBuilder


class StatAnalysisWrapper(CommandBuilder):
    def __init__(self, p, logger):
        super(StatAnalysisWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/stat_analysis')
        self.app_name = os.path.basename(self.app_path)
        if self.logger is None:
            self.logger = util.get_logger(self.p,sublog='StatAnalysis')
   
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

    def create_job_filename(self, job_name, job_args, stat_analysis_out_dir, filename_template):
        if not os.path.exists(os.path.join(stat_analysis_out_dir)):
            os.makedirs(os.path.join(stat_analysis_out_dir))
        job = "-job "+job_name+" "+job_args
        if "-dump_row [dump_row_filename]" in job:
            job = job.replace("[dump_row_filename]", stat_analysis_out_dir+"/"+filename_template+"_dumprow.stat")
        if "-out_stat [out_stat_filename]" in job:
            job = job.replace("[out_stat_filename]", stat_analysis_out_dir+"/"+filename_template+"_outstat.stat")
        self.add_env_var("JOB", job)
       
    def create_hour_group_list(self, loop_hour_beg, loop_hour_end, loop_hour_interval):
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
        conf_var_list=""
        if len(conf_var) > 0:
            for lt in range(len(conf_var)):
                if lt+1 == len(conf_var):
                    conf_var_list = conf_var_list+'"'+str(conf_var[lt]+'"')
                else:
                    con_var_list = conf_var_list+'"'+str(conf_var[lt]+'", ')
        return conf_var_list

    def gather_by_date(self, init_time, valid_time):
        #read config
        model_name = self.p.getstr('config', 'MODEL_NAME')
        obs_name = self.p.getstr('config', 'OBS_NAME')
        valid_hour_method = self.p.getstr('config', 'VALID_HOUR_METHOD')
        valid_hour_beg = self.p.getstr('config', 'VALID_HOUR_BEG')
        valid_hour_end = self.p.getstr('config', 'VALID_HOUR_END')
        valid_hour_increment = self.p.getstr('config', 'VALID_HOUR_INCREMENT')
        init_hour_method = self.p.getstr('config', 'INIT_HOUR_METHOD')
        init_hour_beg = self.p.getstr('config', 'INIT_HOUR_BEG')
        init_hour_end = self.p.getstr('config', 'INIT_HOUR_END')
        init_hour_increment = self.p.getstr('config', 'INIT_HOUR_INCREMENT')
        stat_analysis_lookin_dir = self.p.getdir('STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.p.getdir('STAT_ANALYSIS_OUT_DIR')
        stat_analysis_config = self.p.getstr('config', 'STAT_ANALYSIS_CONFIG')
        job_name = self.p.getstr('config', 'JOB_NAME')
        job_args = self.p.getstr('config', 'JOB_ARGS')
        desc = util.getlist(self.p.getstr('config', 'DESC', ""))
        fcst_lead = util.getlist(self.p.getstr('config', 'FCST_LEAD', ""))
        fcst_var_name = util.getlist(self.p.getstr('config', 'FCST_VAR_NAME', ""))
        fcst_var_level = util.getlist(self.p.getstr('config', 'FCST_VAR_LEVEL', ""))
        obs_var_name = util.getlist(self.p.getstr('config', 'OBS_VAR_NAME', ""))
        obs_var_level = util.getlist(self.p.getstr('config', 'OBS_VAR_LEVEL', ""))
        region = util.getlist(self.p.getstr('config', 'REGION', ""))
        interp = util.getlist(self.p.getstr('config', 'INTERP', ""))
        interp_pts = util.getlist(self.p.getstr('config', 'INTERP_PTS', ""))
        fcst_thresh = util.getlist(self.p.getstr('config', 'FCST_THRESH', ""))
        cov_thresh = util.getlist(self.p.getstr('config', 'COV_THRESH', ""))
        line_type = util.getlist(self.p.getstr('config', 'LINE_TYPE_LIST', ""))
        #set envir vars based on config
        self.add_env_var("MODEL_NAME", '"'+model_name+'"')
        self.add_env_var("OBS_NAME", '"'+obs_name+'"')
        self.add_env_var("DESC", self.create_variable_list(desc))
        self.add_env_var("FCST_LEAD", self.create_variable_list(fcst_lead))
        self.add_env_var('FCST_VAR_NAME', self.create_variable_list(fcst_var_name))
        self.add_env_var('FCST_VAR_LEVEL', self.create_variable_list(fcst_var_level))
        self.add_env_var('OBS_VAR_NAME', self.create_variable_list(obs_var_name))
        self.add_env_var('OBS_VAR_LEVEL', self.create_variable_list(obs_var_level))
        self.add_env_var('REGION', self.create_variable_list(region))
        self.add_env_var('INTERP', self.create_variable_list(interp))
        self.add_env_var('INTERP_PTS', self.create_variable_list(interp_pts))
        self.add_env_var('FCST_THRESH', self.create_variable_list(fcst_thresh))
        self.add_env_var('COV_THRESH', self.create_variable_list(cov_thresh))
        self.add_env_var('LINE_TYPE_LIST', self.create_variable_list(line_type))
        #set up lookin agrument
        if "*" in stat_analysis_lookin_dir: 
            for_stat_analysis_lookin = subprocess.check_output("ls -d "+stat_analysis_lookin_dir, shell=True).rstrip('\n')
        else:
             for_stat_analysis_lookin = stat_analysis_lookin_dir
        self.set_lookin_dir(for_stat_analysis_lookin)
        #set up filename base for stat_analysis output
        if init_time == -1:
            filename_template_base = model_name+"_"+obs_name+"_valid"+valid_time[0:8]
        else:
            filename_template_base = model_name+"_"+obs_name+"_init"+init_time[0:8]
        #set up valid and initialization information for MET config file and run stat_analysis
        valid_beg = calendar.timegm(time.strptime(valid_hour_beg, "%H%M"))
        valid_end = calendar.timegm(time.strptime(valid_hour_end, "%H%M"))
        valid_interval = int(valid_hour_increment)
        init_beg = calendar.timegm(time.strptime(init_hour_beg, "%H%M"))
        init_end = calendar.timegm(time.strptime(init_hour_end, "%H%M"))
        init_interval = int(init_hour_increment)
        if valid_hour_method == "GROUP" and init_hour_method == "LOOP":
            self.logger.info("stat_analysis run method: valid hour grouping, init hour looping")
            init_now = init_beg
            while init_now <= init_end:
                init_now_str = str(time.strftime("%H%M%S", time.gmtime(init_now)))
                filename_template = filename_template_base+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_now_str[0:5]+"Z"
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
                self.logger.debug("stat_analysis run date settings")
                for name, value in fcst_valid_init_dict.items():
                    self.logger.debug(name+": "+value)
                    self.add_env_var(name, value)  
                self.create_job_filename(job_name, job_args, stat_analysis_out_dir, filename_template)
                self.set_param_file(stat_analysis_config)
                #build command
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: stat_analysis could not generate command")
                    return
                self.build()
                self.clear()
                init_now += init_interval
        elif valid_hour_method == "LOOP" and init_hour_method == "GROUP":
            self.logger.info("stat_analysis run method: valid hour looping, init hour grouping")
            valid_now = valid_beg
            while valid_now <= valid_end:
                valid_now_str = str(time.strftime("%H%M%S", time.gmtime(valid_now)))
                filename_template = filename_template_base+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z"
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
                self.logger.debug("stat_analysis run date settings")
                for name, value in fcst_valid_init_dict.items():
                    self.logger.debug(name+": "+value)
                    self.add_env_var(name, value)
                self.create_job_filename(job_name, job_args, stat_analysis_out_dir, filename_template)
                self.set_param_file(stat_analysis_config)
                #build command
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: stat_analysis could not generate command")
                    return
                self.build()
                self.clear()
                valid_now += valid_interval
        elif valid_hour_method == "LOOP" and init_hour_method == "LOOP":
            self.logger.info("stat_analysis run method: valid hour looping, init hour looping")
            init_now = init_beg
            while init_now <= init_end:
                init_now_str = str(time.strftime("%H%M%S", time.gmtime(init_now)))
                valid_now = valid_beg
                while valid_now <= valid_end:
                    valid_now_str = str(time.strftime("%H%M%S", time.gmtime(valid_now)))
                    filename_template = filename_template_base+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_now_str[0:5]+"Z"
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
                    self.logger.debug("stat_analysis run date settings")
                    for name, value in fcst_valid_init_dict.items():
                        self.logger.debug(name+": "+value)
                        self.add_env_var(name, value)
                    self.create_job_filename(job_name, job_args, stat_analysis_out_dir, filename_template)
                    self.set_param_file(stat_analysis_config)
                    #build command
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: stat_analysis could not generate command")
                        return
                    self.build()
                    self.clear()
                    valid_now += valid_interval
                init_now += init_interval
        elif valid_hour_method == "GROUP" and init_hour_method == "GROUP":
            self.logger.info("stat_analysis run method: valid hour grouping, init hour grouping")
            filename_template = filename_template_base+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z"
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
            self.logger.debug("stat_analysis run date settings")
            for name, value in fcst_valid_init_dict.items():
                self.logger.debug(name+": "+value)
                self.add_env_var(name, value)
            self.create_job_filename(job_name, job_args, stat_analysis_out_dir, filename_template)
            self.set_param_file(stat_analysis_config)
            #build command
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("ERROR: stat_analysis could not generate command")
                return
            self.build()
            self.clear()
        else:
            self.logger.error("ERROR: invalid conf entry for VALID_HOUR_METHOD or INIT_HOUR_METHOD")
            exit

    class FieldObj(object):
        __slots__ = 'name', 'dir'

    def parse_model_list(self):
        model_list = []
        all_conf = self.p.keys('config')
        model_indices = []
        regex = re.compile("MODEL(\d+)_NAME")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                model_indices.append(result.group(1))
        for m in model_indices:
            if self.p.has_option('config', "MODEL"+m+"_NAME"):
                model_name = self.p.getstr('config', "MODEL"+m+"_NAME")
                model_dir = ""
                if self.p.has_option('config', "MODEL"+m+"_STAT_DIR"):
                    model_dir = self.p.getstr('config', "MODEL"+m+"_STAT_DIR")
            mod = self.FieldObj()
            mod.name = model_name
            mod.dir = model_dir
            model_list.append(mod)
        return model_list

    def run_all_times(self):
        self.logger.info("RUNNING STAT_ANALYSIS FOR PLOTTING FORMAT")
        verif_case = self.p.getstr('config', 'VERIF_CASE')
        if verif_case == 'grid2grid':
            self.grid2grid_plot_format()
        elif verif_case == 'grid2obs':
            self.grid2obs_plot_format()
        elif verif_case == 'precip':
            self.logger.info("Formatting for plotting for precip")
        else:
            self.logger.error("Not a valid VERIF_CASE option")
            exit(1)

    def run_at_time(self, init_time, valid_time):
        self.gather_by_date(init_time, valid_time)
