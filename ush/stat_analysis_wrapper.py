#!/usr/bin/env python

'''
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row
Abstract: Runs stat_analysis
History Log:  Third version
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

    def create_job_filename(self, job_name, job_args, stat_analysis_out_dir_base, stat_analysis_dump_row_info, stat_analysis_out_stat_info):
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
            if not os.path.exists(stat_analysis_out_dir):
                os.makedirs(stat_analysis_out_dir)
            self.logger.debug("dump_row output: "+stat_analysis_out_dir+"/"+stat_analysis_dump_row_filename)
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
            if not os.path.exists(stat_analysis_out_dir):
                os.makedirs(stat_analysis_out_dir)
            self.logger.debug("out_stat output: "+stat_analysis_out_dir+"/"+stat_analysis_out_stat_filename)
            job = job.replace("[out_stat_filename]", stat_analysis_out_dir+"/"+stat_analysis_out_stat_filename)
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

    class StatAnalysisOutputInfo(object):
        __slots__ = 'template_type', 'filename_template', 'filename'
        
    def create_filename_from_user_template(self, filename_template, valid_init_time_info, init_time):
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
                    self.logger.error("ERROR: Please include valid hour group times in template defined in METplus conf file using VALID_HOUR_BEG and VALID_HOUR_END")
                    exit(1)
            #build init_time_filename
            if len(time_info_init_hour) == 1:
                init_time_filename = "19000101"+time_info_init_hour[0]
                #check that init format makes sense in template
                match = re.search(r'.*\{init\?fmt=(.*?)\}', filename_template)
                if match:
                    if match.group(1) != '%H':
                        self.logger.error("ERROR: only accepted format {init?fmt=%H}")
                        exit(1)
            else:
                init_time_filename = "1900010100"
                match = re.search(r'.*\{init\?fmt=(.*?)\}', filename_template)
                if match:
                    self.logger.error("ERROR: Please include init hour group times in template defined in METplus conf file using INIT_HOUR_BEG and INIT_HOUR_END")
                    exit(1)
        else:
            init_time_filename =  time_info_init_beg
            #build init_time_filename
            if time_info_init_beg != time_info_init_end:
                match = re.search(r'.*\{init\?fmt=(.*?[%H])\}', filename_template)
                if match:
                    self.logger.error("ERROR: Please include init hour group times in template defined in METplus conf file using INIT_HOUR_BEG and INIT_HOUR_END")
                    exit(1)
            #build valid_time_filename
            if len(time_info_valid_hour) == 1:
                valid_time_filename = "19000101"+time_info_valid_hour[0]
                #check that valid format makes sense in template
                match = re.search(r'.*\{valid\?fmt=(.*?)\}', filename_template)
                if match:
                    if match.group(1) != '%H':
                        self.logger.error("ERROR: only accepted format {valid?fmt=%H}")
                        exit(1)
            else:
                valid_time_filename = "1900010100"
                match = re.search(r'.*\{valid\?fmt=(.*?)\}', filename_template)
                if match:
                    self.logger.error("ERROR: Please include valid hour group times in template defined in METplus conf file using VALID_HOUR_BEG and VALID_HOUR_END")
                    exit(1)
        #split into chunks to deal with directories
        tmpl_split = filename_template.split("/")
        filled_tmpl = ""
        for tmpl_chunk in tmpl_split:
            if "?fmt=%" in tmpl_chunk:
                tmpl_chunkSts = sts.StringSub(self.logger,
                                              tmpl_chunk,
                                              init=init_time_filename,
                                              valid=valid_time_filename)
                filled_tmpl_chunk = tmpl_chunkSts.doStringSub()
            else:
                filled_tmpl_chunk = tmpl_chunk
            filled_tmpl = os.path.join(filled_tmpl, filled_tmpl_chunk)
        return filled_tmpl

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
        line_type = util.getlist(self.p.getstr('config', 'LINE_TYPE', ""))
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
            stat_analysis_dump_row_tmpl = util.getraw_interp(self.p, 'filename_templates','STAT_ANALYSIS_DUMP_ROW_TMPL')
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
            stat_analysis_out_stat_tmpl = util.getraw_interp(self.p, 'filename_templates','STAT_ANALYSIS_OUT_STAT_TMPL')
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
            self.logger.info("stat_analysis run method: valid hour grouping, init hour looping")
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
                self.logger.debug("stat_analysis run date settings")
                for name, value in fcst_valid_init_dict.items():
                    self.logger.debug(name+": "+value)
                    self.add_env_var(name, value)
                if stat_analysis_dump_row_info.template_type == "default_template":
                    stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_now_str[0:5]+"Z_dumprow.stat"
                elif stat_analysis_dump_row_info.template_type == "user_template":
                    stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
                if stat_analysis_out_stat_info.template_type == "default_template":
                    stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_now_str[0:5]+"Z_outstat.stat"
                elif stat_analysis_out_stat_info.template_type == "user_template":
                    stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
                self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
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
                if stat_analysis_dump_row_info.template_type == "default_template":
                    stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_dumprow.stat"
                elif stat_analysis_dump_row_info.template_type == "user_template":
                    stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
                if stat_analysis_out_stat_info.template_type == "default_template":
                    stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_outstat.stat"
                elif stat_analysis_out_stat_info.template_type == "user_template":
                    stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
                self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
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
                    if stat_analysis_dump_row_info.template_type == "default_template":
                        stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_now_str[0:5]+"Z_dumprow.stat"
                    elif stat_analysis_dump_row_info.template_type == "user_template":
                        stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
                    if stat_analysis_out_stat_info.template_type == "default_template":
                        stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_now_str[0:5]+"Z"+"_init"+init_now_str[0:5]+"Z_outstat.stat"
                    elif stat_analysis_out_stat_info.template_type == "user_template":
                        stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
                    self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
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
            if stat_analysis_dump_row_info.template_type == "default_template":
                stat_analysis_dump_row_info.filename = stat_analysis_dump_row_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_dumprow.stat"
            elif stat_analysis_dump_row_info.template_type == "user_template":
                stat_analysis_dump_row_info.filename = self.create_filename_from_user_template(stat_analysis_dump_row_info.filename_template, fcst_valid_init_dict, init_time)
            if stat_analysis_out_stat_info.template_type == "default_template":
                stat_analysis_out_stat_info.filename = stat_analysis_out_stat_info.filename_template+"_valid"+valid_hour_beg+"to"+valid_hour_end+"Z"+"_init"+init_hour_beg+"to"+init_hour_end+"Z_outstat.stat"
            elif stat_analysis_out_stat_info.template_type == "user_template":
                stat_analysis_out_stat_info.filename = self.create_filename_from_user_template(stat_analysis_out_stat_info.filename_template, fcst_valid_init_dict, init_time)
            self.create_job_filename(job_name, job_args, stat_analysis_out_dir, stat_analysis_dump_row_info, stat_analysis_out_stat_info)
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
            exit(1)

    #def gather_by_info(self):
    #    #read config
    #    verif_case = self.p.getstr('config', 'VERIF_CASE')
    #    verif_type = self.p.getstr('config', 'VERIF_TYPE')
    #    ##use_init = self.p.getbool('config', 'LOOP_BY_INIT')
    #    valid_beg_YYYYMMDD = self.p.getstr('config', 'VALID_BEG', "")
    #    valid_end_YYYYMMDD = self.p.getstr('config', 'VALID_END', "")
    #    valid_hour_method = self.p.getstr('config', 'VALID_HOUR_METHOD')
    #    valid_hour_beg = self.p.getstr('config', 'VALID_HOUR_BEG')
    #    valid_hour_end = self.p.getstr('config', 'VALID_HOUR_END')
    #    valid_hour_increment = self.p.getstr('config', 'VALID_HOUR_INCREMENT')
    #    init_beg_YYYYMMDD = self.p.getstr('config', 'INIT_BEG', "")
    #    init_end_YYYYMMDD = self.p.getstr('config', 'INIT_END', "")
    #    init_hour_method = self.p.getstr('config', 'INIT_HOUR_METHOD')
    #    init_hour_beg = self.p.getstr('config', 'INIT_HOUR_BEG')
    #    init_hour_end = self.p.getstr('config', 'INIT_HOUR_END')
    #    init_hour_increment = self.p.getstr('config', 'INIT_HOUR_INCREMENT')
    #    stat_analysis_out_dir = self.p.getdir('STAT_ANALYSIS_OUT_DIR')
    #    stat_analysis_config = self.p.getstr('config', 'STAT_ANALYSIS_CONFIG')
    #    model_list = self.parse_model_list()
    #    var_list = util.parse_var_list(self.p)
    #    region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
    #    lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
    #    desc = util.getlist(self.p.getstr('config', 'DESC', ""))
    #    interp = util.getlist(self.p.getstr('config', 'INTERP', ""))
    #    interp_pts = util.getlist(self.p.getstr('config', 'INTERP_PTS', ""))
    #    fcst_thresh = util.getlist(self.p.getstr('config', 'FCST_THRESH', ""))
    #    cov_thresh = util.getlist(self.p.getstr('config', 'COV_THRESH', ""))
    #    line_type = util.getlist(self.p.getstr('config', 'LINE_TYPE', ""))
    #    for model_info in model_list:
    #        model_name = model_info.name
    #        model_dir = model_info.dir
    #        self.add_env_var('MODEL_NAME', model_name)
    #        for var_info in var_list:
    #            fcst_var_name = var_info.fcst_name
    #            fcst_var_level = var_info.fcst_level
    #            obs_var_name = var_info.obs_name
    #            obs_var_level = var_info.obs_level
    #            self.add_env_var('FCST_VAR_NAME', fcst_var_name)
    #            self.add_env_var('FCST_VAR_LEVEL', fcst_var_level)
    #            self.add_env_var('OBS_VAR_NAME', obs_var_name)
    #            self.add_env_var('OBS_VAR_LEVEL', obs_var_level)
    #            for region in region_list:
    #                self.add_env_var('REGION', region)
    #                for lead in lead_list:
    #                    lead_zfill = lead.zfill(2)
    #                    self.add_env_var('LEAD', lead_string)
    #    #set envir vars based on config
    #    ##if use_init:
    #    ##    init_beg_YYYYMMDD = self.p.getstr('config', 'INIT_BEG')
    #    ##    init_end_YYYYMMDD = self.p.getstr('config', 'INIT_END')
    #    ##    valid_beg_YYYYMMDD = ""
    #    ##    valid_end_YYYYMMDD = ""
    #    ##else:
    #    ##    init_beg_YYYYMMDD = self.p.getstr('config', 'INIT_BEG')
    #    ##    init_end_YYYYMMDD = self.p.getstr('config', 'INIT_END')
    #    ##    valid_beg_YYYYMMDD = self.p.getstr('config', 'VALID_BEG')
    #    ##    valid_end_YYYYMMDD = self.p.getstr('config', 'VALID_END')
    #      
    #def run_all_times(self):
    #    self.gather_by_info()
    #    #verif_case = self.p.getstr('config', 'VERIF_CASE')
    #    #if verif_case == 'grid2grid':
    #    #    self.grid2grid_plot_format()
    #    #elif verif_case == 'grid2obs':
    #    #    self.grid2obs_plot_format()
    #    #elif verif_case == 'precip':
    #    #    self.logger.info("Formatting for plotting for precip")
    #    #else:
    #    #    self.logger.error("Not a valid VERIF_CASE option")
    #    #    exit(1)

    def run_at_time(self, init_time, valid_time):
        self.gather_by_date(init_time, valid_time)
