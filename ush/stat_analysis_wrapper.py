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
from task_info import TaskInfo
from command_builder import CommandBuilder


class StatAnalysisWrapper(CommandBuilder):
    def __init__(self, p, logger):
        super(StatAnalysisWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.cu.getdir('MET_INSTALL_DIR'),
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
    
    def grid2grid_VSDB_format(self, valid_time, init_time):
        self.logger.info("Formatting in VSDB style for grid2grid")
        #read config
        model_type = self.cu.getstr('config', 'MODEL')
        ob_type = self.cu.getstr('config', 'OB_TYPE')
        self.add_env_var("MODEL", model_type)
        self.add_env_var("OB_TYPE", ob_type)
        stat_analysis_lookin_dir = self.cu.getdir('STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.cu.getdir('STAT_ANALYSIS_OUT_DIR')
        #filtering times based on if files made based on init_time or valid_time
        if init_time == -1:
            self.logger.info("Valid on: "+valid_time)
            filter_time = valid_time
            date_YYYYMMDD = filter_time[0:8]
            cycle = filter_time[8:10]
            self.add_env_var("FCST_VALID_BEG", valid_time)
            self.add_env_var("FCST_VALID_END", valid_time)
            self.add_env_var("FCST_VALID_HOUR", '"'+cycle+'"')
            self.add_env_var("FCST_INIT_BEG", "")
            self.add_env_var("FCST_INIT_END", "")
            self.add_env_var("FCST_INIT_HOUR", "")
        else:
            self.logger.info("Initialized on: "+init_time)
            filter_time = init_time
            date_YYYYMMDD = filter_time[0:8]
            cycle = filter_time[8:10]
            self.add_env_var("FCST_VALID_BEG", "")
            self.add_env_var("FCST_VALID_END", "")
            self.add_env_var("FCST_VALID_HOUR", "")
            self.add_env_var("FCST_INIT_BEG", init_time)
            self.add_env_var("FCST_INIT_END", init_time)
            self.add_env_var("FCST_INIT_HOUR", '"'+cycle+'"')
        #build -lookin directory
        self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, filter_time, "grid_stat"))
        #save output like VSDB
        verif_type = self.cu.getstr('config', "VERIF_TYPE")
        if not os.path.exists(os.path.join(stat_analysis_out_dir,
                              verif_type ,cycle+"Z", model_type)):
           os.makedirs(os.path.join(stat_analysis_out_dir,
                                    verif_type, cycle+"Z", model_type))
        dump_row_file = os.path.join(stat_analysis_out_dir,
                                     verif_type, cycle+"Z", model_type, model_type+"_"+date_YYYYMMDD+".stat")
        job = "-job filter -dump_row "+dump_row_file
        self.add_env_var("JOB", job)
        #get stat_analysis config file
        self.set_param_file(self.cu.getstr('config', 'STAT_ANALYSIS_CONFIG'))
        #build command
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("ERROR: stat_analysis could not generate command")
            return
        self.logger.info("")
        self.build()
        self.clear()

    def grid2obs_VSDB_format(self, valid_time, init_time):
        #read config
        self.logger.info("Formatting in VSDB style for grid2obs")
        model_type = self.cu.getstr('config', 'MODEL')
        ob_type = self.cu.getstr('config', 'OB_TYPE')
        self.add_env_var("MODEL", model_type)
        self.add_env_var("OB_TYPE", ob_type)
        stat_analysis_lookin_dir = self.cu.getdir('STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.cu.getdir('STAT_ANALYSIS_OUT_DIR')
        if init_time == -1:
            date_YYYYMMDD = valid_time[0:8]
            valid_beg_hour = self.cu.getstr('config', 'VALID_BEG_HOUR')
            valid_end_hour = self.cu.getstr('config', 'VALID_END_HOUR')
            self.logger.info("Valid on: "+date_YYYYMMDD+" between "+valid_beg_hour+"-"+valid_end_hour)
            loop_beg_hour = self.cu.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.cu.getint('config', 'INIT_END_HOUR')
            loop_inc = self.cu.getint('config', 'INIT_INCREMENT')
        else:
            date_YYYYMMDD = init_time[0:8]
            init_beg_hour = self.cu.getstr('config', 'INIT_BEG_HOUR')
            init_end_hour = self.cu.getstr('config', 'INIT_END_HOUR')
            self.logger.info("Initialized on: "+date_YYYYMMDD+" between "+init_beg_hour+"-"+init_end_hour)
            loop_beg_hour = self.cu.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.cu.getint('config', 'VALID_END_HOUR')
            loop_inc = self.cu.getint('config', 'VALID_INCREMENT')
        loop_hour = loop_beg_hour 
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            #filtering times based on if files made based on init_time or valid_time
            if init_time == -1:
                self.logger.info("Any model forecasts initialized at: "+loop_hour_str)
                self.add_env_var("FCST_VALID_BEG", date_YYYYMMDD+"_"+valid_beg_hour+"0000")
                self.add_env_var("FCST_VALID_END", date_YYYYMMDD+"_"+valid_end_hour+"0000")
                self.add_env_var("FCST_VALID_HOUR", "")
                self.add_env_var("FCST_INIT_BEG", "")
                self.add_env_var("FCST_INIT_END", "")
                self.add_env_var("FCST_INIT_HOUR", '"'+loop_hour_str+'"')
            else:
                self.logger.info("Any model forecasts valid at: "+loop_hour_str)
                self.add_env_var("FCST_VALID_BEG", "")
                self.add_env_var("FCST_VALID_END", "")
                self.add_env_var("FCST_VALID_HOUR", '"'+loop_hour_str+'"')
                self.add_env_var("FCST_INIT_BEG", date_YYYYMMDD+"_"+init_beg_hour+"0000")
                self.add_env_var("FCST_INIT_END", date_YYYYMMDD+"_"+init_end_hour+"0000")
                self.add_env_var("FCST_INIT_HOUR", "")
            #build -lookin directory
            self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir))
            #save output like VSDB
            verif_type = self.cu.getstr('config', "VERIF_TYPE")
            if not os.path.exists(os.path.join(stat_analysis_out_dir,
                                  verif_type, loop_hour_str+"Z", model_type)):
               os.makedirs(os.path.join(stat_analysis_out_dir,
                                        verif_type, loop_hour_str+"Z", model_type))
            dump_row_file = os.path.join(stat_analysis_out_dir,
                                         verif_type, loop_hour_str+"Z", model_type, model_type+"_"+date_YYYYMMDD+".stat")
            job = "-job filter -dump_row "+dump_row_file
            self.add_env_var("JOB", job)
            #get stat_analysis config file
            self.set_param_file(self.cu.getstr('config', 'STAT_ANALYSIS_CONFIG'))
            #build command
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("ERROR: stat_analysis could not generate command")
                return
            self.logger.info("")
            self.build()
            self.clear()
            loop_hour += loop_inc

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
                model_name = self.cu.getstr('config', "MODEL"+m+"_NAME")
                model_dir = ""
                if self.p.has_option('config', "MODEL"+m+"_STAT_DIR"):
                    model_dir = self.cu.getstr('config', "MODEL"+m+"_STAT_DIR")
            mod = self.FieldObj()
            mod.name = model_name
            mod.dir = model_dir
            model_list.append(mod)
        return model_list

    def grid2grid_plot_format(self):
        verif_type = self.cu.getstr('config', 'VERIF_TYPE')
        if verif_type == 'pres' or verif_type == 'anom' or verif_type == 'sfc':
            self.logger.info("Formatting for plotting for grid2grid-"+verif_type)
            use_init = util.is_loop_by_init(self.p)
            if use_init:
                start_t = self.cu.getstr('config', 'INIT_BEG')
                end_t = self.cu.getstr('config', 'INIT_END')
                self.add_env_var("FCST_VALID_BEG", "")
                self.add_env_var("FCST_VALID_END", "")
                self.add_env_var("FCST_INIT_BEG", start_t)
                self.add_env_var("FCST_INIT_END", end_t)
                loop_beg_hour = self.cu.getint('config', 'INIT_BEG_HOUR')
                loop_end_hour = self.cu.getint('config', 'INIT_END_HOUR')
                loop_inc = self.cu.getint('config', 'INIT_INCREMENT')
            else:
                start_t = self.cu.getstr('config', 'VALID_BEG')
                end_t = self.cu.getstr('config', 'VALID_END')
                self.add_env_var("FCST_VALID_BEG", start_t)
                self.add_env_var("FCST_VALID_END", end_t)
                self.add_env_var("FCST_INIT_BEG", "")
                self.add_env_var("FCST_INIT_END", "")
                loop_beg_hour = self.cu.getint('config', 'VALID_BEG_HOUR')
                loop_end_hour = self.cu.getint('config', 'VALID_END_HOUR')
                loop_inc = self.cu.getint('config', 'VALID_INCREMENT')
            stat_analysis_out_dir = self.cu.getdir('STAT_ANALYSIS_OUT_DIR')
            region_list = util.getlist(self.cu.getstr('config', 'REGION_LIST'))
            lead_list = util.getlistint(self.cu.getstr('config', 'LEAD_LIST'))
            model_list = self.parse_model_list()
            var_list = util.parse_var_list(self.cu)
            interp_list = [ 'NEAREST' ]
            #start looping to run stat_analysis
            loop_hour = loop_beg_hour
            while loop_hour <= loop_end_hour:
               loop_hour_str = str(loop_hour).zfill(2)
               if use_init:
                    start_t = self.cu.getstr('config', 'INIT_BEG')
                    end_t = self.cu.getstr('config', 'INIT_END')
                    self.add_env_var("FCST_VALID_BEG", "")
                    self.add_env_var("FCST_VALID_END", "")
                    self.add_env_var("FCST_VALID_HOUR", "")
                    self.add_env_var("FCST_INIT_BEG", start_t+"_"+loop_hour_str+"0000")
                    self.add_env_var("FCST_INIT_END", end_t+"_"+loop_hour_str+"0000")
                    self.add_env_var("FCST_INIT_HOUR", '"'+loop_hour_str+'"')
               else:
                    start_t = self.cu.getstr('config', 'VALID_BEG')
                    end_t = self.cu.getstr('config', 'VALID_END')
                    self.add_env_var("FCST_VALID_BEG", start_t+"_"+loop_hour_str+"0000")
                    self.add_env_var("FCST_VALID_END", end_t+"_"+loop_hour_str+"0000")
                    self.add_env_var("FCST_VALID_HOUR", '"'+loop_hour_str+'"')
                    self.add_env_var("FCST_INIT_BEG", "")
                    self.add_env_var("FCST_INIT_END", "")
                    self.add_env_var("FCST_INIT_HOUR", "")
               for model_info in model_list:
                   model = model_info.name
                   self.add_env_var('MODEL', model)
                   stat_analysis_lookin_dir = model_info.dir
                   self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, verif_type, loop_hour_str+'Z', model))
                   for var_info in var_list:
                       fcst_var_name = var_info.fcst_name
                       fcst_var_level = var_info.fcst_level
                       obs_var_name = var_info.obs_name
                       obs_var_level = var_info.obs_level
                       self.add_env_var('FCST_VAR_NAME', fcst_var_name)
                       self.add_env_var('FCST_VAR_LEVEL', fcst_var_level)
                       self.add_env_var('OBS_VAR_NAME', obs_var_name)
                       self.add_env_var('OBS_VAR_LEVEL', obs_var_level)
                       if verif_type == 'anom':
                          if fcst_var_name == 'HGT' or obs_var_name == 'HGT':
                              fourier_decomp_height = self.cu.getbool('config', 'FOURIER_HEIGHT_DECOMP')
                              if fourier_decomp_height:
                                  wave_num_beg_list = util.getlist(self.cu.getstr('config', 'WAVE_NUM_BEG_LIST'))
                                  wave_num_end_list = util.getlist(self.cu.getstr('config', 'WAVE_NUM_END_LIST'))
                                  if len(wave_num_beg_list) != len(wave_num_end_list):
                                      self.logger.error("ERROR: WAVE_NUM_BEG_LIST and WAVE_NUM_END_LIST do not have the same number of elements")
                                      exit(1)
                                  else:
                                      for wn in range(len(wave_num_beg_list)):
                                          wb = wave_num_beg_list[wn]
                                          we = wave_num_end_list[wn]
                                          wave_num_pairing = "WV1_"+wb+"-"+we
                                          interp_list.append(wave_num_pairing)
                       for region in region_list:
                           self.add_env_var('REGION', region)
                           if not os.path.exists(os.path.join(stat_analysis_out_dir,
                                                 verif_type, loop_hour_str+"Z", model, region)):
                               util.mkdir_p(os.path.join(stat_analysis_out_dir,verif_type, loop_hour_str+"Z", model, region))
                           for lead in lead_list:
                               if lead < 10:
                                   lead_string = '0'+str(lead)
                               else:
                                   lead_string = str(lead)
                               self.add_env_var('LEAD', lead_string)
                               for interp in interp_list:
                                   self.add_env_var('INTERP', interp)
                                   if interp == "NEAREST":
                                       dump_row_file = os.path.join(stat_analysis_out_dir,
                                                                    verif_type, loop_hour_str+"Z", model, region, 
                                                                    model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat")
                                   else:
                                       dump_row_file = os.path.join(stat_analysis_out_dir,
                                                                    verif_type, loop_hour_str+"Z", model, region, 
                                                                    model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+interp+".stat")
                                   job = "-job filter -dump_row "+dump_row_file
                                   self.add_env_var("JOB", job)
                                   self.set_param_file(self.cu.getstr('config', 'STAT_ANALYSIS_CONFIG'))
                                   #build command
                                   cmd = self.get_command()
                                   if cmd is None:
                                       self.logger.error("ERROR: stat_analysis could not generate command")
                                       return
                                   self.logger.info("")
                                   self.build()
                                   self.clear()
               loop_hour += loop_inc
        else:
            self.logger.error(verif_type+" not a valid VERIF_TYPE option for grid2grid")
            exit(1)

    def grid2obs_plot_format(self):
        verif_type = self.cu.getstr('config', 'VERIF_TYPE')
        if verif_type == 'upper_air' or verif_type == 'conus_sfc':
           self.logger.info("Formatting for plotting for grid2obs-"+verif_type)
           use_init = util.is_loop_by_init(self.p)
           self.add_env_var('INTERP', 'BILIN')
           if use_init:
               init_beg_hour = self.cu.getstr('config', 'INIT_BEG_HOUR')
               init_end_hour = self.cu.getstr('config', 'INIT_END_HOUR')
               loop_beg_hour = self.cu.getint('config', 'VALID_BEG_HOUR')
               loop_end_hour = self.cu.getint('config', 'VALID_END_HOUR')
               loop_inc = self.cu.getint('config', 'VALID_INCREMENT')
           else:
               valid_beg_hour = self.cu.getstr('config', 'VALID_BEG_HOUR')
               valid_end_hour = self.cu.getstr('config', 'VALID_END_HOUR')
               loop_beg_hour = self.cu.getint('config', 'INIT_BEG_HOUR')
               loop_end_hour = self.cu.getint('config', 'INIT_END_HOUR')
               loop_inc = self.cu.getint('config', 'INIT_INCREMENT')
           stat_analysis_out_dir = self.cu.getdir('STAT_ANALYSIS_OUT_DIR')
           region_list = util.getlist(self.cu.getstr('config', 'REGION_LIST'))
           lead_list = util.getlistint(self.cu.getstr('config', 'LEAD_LIST'))
           model_list = self.parse_model_list()
           var_list = util.parse_var_list(self.cu)
           self.add_env_var('INTERP', 'BILIN')
           #start looping to run stat_analysis
           loop_hour = loop_beg_hour
           while loop_hour <= loop_end_hour:
               loop_hour_str = str(loop_hour).zfill(2)
               #filtering times based on if files made based on init_time or valid_time
               if use_init:
                   start_t = self.cu.getstr('config', 'INIT_BEG')
                   end_t = self.cu.getstr('config', 'INIT_END')
                   self.add_env_var("FCST_VALID_BEG", "")
                   self.add_env_var("FCST_VALID_END", "")
                   self.add_env_var("FCST_VALID_HOUR", '"'+loop_hour_str+'"')
                   self.add_env_var("FCST_INIT_BEG", start_t+"_"+init_beg_hour+"0000")
                   self.add_env_var("FCST_INIT_END", end_t+"_"+init_end_hour+"0000")
                   self.add_env_var("FCST_INIT_HOUR", "")
               else:
                   start_t = self.cu.getstr('config', 'VALID_BEG')
                   end_t = self.cu.getstr('config', 'VALID_END')
                   self.add_env_var("FCST_VALID_BEG", start_t+"_"+valid_beg_hour+"0000")
                   self.add_env_var("FCST_VALID_END", end_t+"_"+valid_end_hour+"0000")
                   self.add_env_var("FCST_VALID_HOUR", "")
                   self.add_env_var("FCST_INIT_BEG", "")
                   self.add_env_var("FCST_INIT_END", "")
                   self.add_env_var("FCST_INIT_HOUR", '"'+loop_hour_str+'"')
               for model_info in model_list:
                   model = model_info.name
                   self.add_env_var('MODEL', model)
                   stat_analysis_lookin_dir = model_info.dir
                   self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, verif_type, loop_hour_str+'Z', model))
                   for var_info in var_list:
                       fcst_var_name = var_info.fcst_name
                       fcst_var_level = var_info.fcst_level
                       obs_var_name = var_info.obs_name
                       obs_var_level = var_info.obs_level
                       self.add_env_var('FCST_VAR_NAME', fcst_var_name)
                       self.add_env_var('FCST_VAR_LEVEL', fcst_var_level)
                       self.add_env_var('OBS_VAR_NAME', obs_var_name)
                       self.add_env_var('OBS_VAR_LEVEL', obs_var_level)
                       for region in region_list:
                           self.add_env_var('REGION', region)
                           if not os.path.exists(os.path.join(stat_analysis_out_dir,
                                              verif_type, loop_hour_str+"Z", model, region)):
                               util.mkdir_p(os.path.join(stat_analysis_out_dir,verif_type, loop_hour_str+"Z", model, region))
                           for lead in lead_list:
                               if lead < 10:
                                   lead_string = '0'+str(lead)
                               else:
                                   lead_string = str(lead)
                               self.add_env_var('LEAD', lead_string)
                               dump_row_file = os.path.join(stat_analysis_out_dir,
                                                            verif_type, loop_hour_str+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat")
                               job = "-job filter -dump_row "+dump_row_file
                               self.add_env_var("JOB", job)
                               self.set_param_file(self.cu.getstr('config', 'STAT_ANALYSIS_CONFIG'))
                               #build command
                               cmd = self.get_command()
                               if cmd is None:
                                    self.logger.error("ERROR: stat_analysis could not generate command")
                                    return
                               self.logger.info("")
                               self.build()
                               self.clear()
               loop_hour += loop_inc
        else:
           self.logger.error(verif_type+" not a valid VERIF_TYPE option for grid2obs")
           exit(1)
########################################################################
########################################################################
########################################################################
    def run_all_times(self):
        self.logger.info("RUNNING STAT_ANALYSIS FOR PLOTTING FORMAT")
        verif_case = self.cu.getstr('config', 'VERIF_CASE')
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
        self.logger.info("RUNNING STAT_ANALYSIS FOR VSDB FORMAT")
        verif_case = self.cu.getstr('config', 'VERIF_CASE')
        if verif_case == 'grid2grid':
             self.grid2grid_VSDB_format(valid_time, init_time)
        elif verif_case == 'grid2obs':
            self.grid2obs_VSDB_format(valid_time, init_time)
        elif verif_case == 'precip':
            self.logger.info("Formatting in VSDB style for precip")
        else:
            self.logger.error("Not a valid VERIF_CASE option for formatting")
            exit(1)
