#!/usr/bin/env python

'''
Program Name: make_plots_mallory_wrapper.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make plots
History Log:  Initial version
Usage: 
Parameters: None
Input Files: ASCII files
Output Files: .png images
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
import string_template_substitution as sts
from task_info import TaskInfo
from command_builder import CommandBuilder


class MakePlotsWrapper(CommandBuilder):
    def __init__(self, p, logger):
        super(MakePlotsWrapper, self).__init__(p, logger)
        if self.logger is None:
            self.logger = util.get_logger(self.p,sublog='MakePlots')
    #    self.app_path = os.path.join(self.p.getdir('PYTHON_INSTALL_DIR'),
    #                                 'bin/python')
    #    self.app_name = os.path.basename(self.app_path)
    #
    #def set_python_script(self, pythonscript):
    #    self.pythonscript = pythonscript
    #
    #def get_command(self):
    #    if self.app_path is None:
    #        self.logger.error(self.app_name + ": No app path specified. \
    #                          You must use a subclass")
    #        return None
    #
    #    cmd = self.app_path + " "
    #    for a in self.args:
    #        cmd += a + " "
    #
    #    if self.pythonscript == "":
    #        self.logger.error(self.app_name+": No python script specified")
    #        return None
    #
    #    cmd += self.pythonscript
    #
    #    return cmd

    def grid2grid_pres_plots(self):
        self.logger.info("Making plots for grid2grid-pres")
        logging_filename = self.logger.handlers[0].baseFilename
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            loop_beg_hour = self.p.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'INIT_END_HOUR')
            loop_inc = self.p.getint('config', 'INIT_INC')
            date_filter_method = "Initialization"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INC')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        if os.path.exists(plotting_out_dir):
            self.logger.info(plotting_out_dir+" exist, removing")
            util.rmtree(plotting_out_dir)
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = self.p.getstr('config', 'MODEL_LIST')
        plot_stats_list = self.p.getstr('config', 'PLOT_STATS_LIST')
        self.add_env_var("STAT_FILES_INPUT_DIR", stat_files_input_dir)
        self.add_env_var("PLOTTING_OUT_DIR", plotting_out_dir)
        self.add_env_var("MODEL_LIST", model_list)
        self.add_env_var("PLOT_STATS_LIST", plot_stats_list)
        #need to grab var info in special way that differs from util.parse_var_list
        #need variables with cooresponding list of levels; logic derived from util.parse_var_list
        var_info_list = []
        # find all FCST_VARn_NAME keys in the conf files
        all_conf = self.p.keys('config')
        fcst_indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
           result = regex.match(conf)
           if result is not None:
              fcst_indices.append(result.group(1))
        # loop over all possible variables and add them to list
        for n in fcst_indices:
            # get fcst var info if available
            if self.p.has_option('config', "FCST_VAR"+n+"_NAME"):
                fcst_name = self.p.getstr('config', "FCST_VAR"+n+"_NAME")

            fcst_extra = ""
            if self.p.has_option('config', "FCST_VAR"+n+"_OPTIONS"):
                fcst_extra = util.getraw_interp(self.p, 'config', "FCST_VAR"+n+"_OPTIONS")

            fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            # if OBS_VARn_X does not exist, use FCST_VARn_X
            if self.p.has_option('config', "OBS_VAR"+n+"_NAME"):
                obs_name = self.p.getstr('config', "OBS_VAR"+n+"_NAME")
            else:
                obs_name = fcst_name

            obs_extra = ""
            if self.p.has_option('config', "OBS_VAR"+n+"_OPTIONS"):
                obs_extra = util.getraw_interp(self.p, 'config', "OBS_VAR"+n+"_OPTIONS")
            ##else:
            ##    obs_extra = fcst_extra
            ##fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            if self.p.has_option('config', "OBS_VAR"+n+"_LEVELS"):
                obs_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            else:
                obs_levels = fcst_levels
            
            if len(fcst_levels) != len(obs_levels):
                print("ERROR: FCST_VAR"+n+"_LEVELS and OBS_VAR"+n+\
                          "_LEVELS do not have the same number of elements")
                exit(1)
            fo = util.FieldObj()
            fo.fcst_name = fcst_name
            fo.obs_name = obs_name
            fo.fcst_extra = fcst_extra
            fo.obs_extra = obs_extra
            fo.fcst_level = fcst_levels
            fo.obs_level = obs_levels
            var_info_list.append(fo)
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for v in var_info_list:
                fcst_var_levels_list = v.fcst_level
                self.add_env_var('FCST_VAR_NAME', v.fcst_name)
                #self.add_env_var('FCST_VAR_EXTRA', v.fcst_extra)
                self.add_env_var('FCST_VAR_LEVELS_LIST', ''.join(fcst_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                obs_var_levels_list = v.obs_level
                self.add_env_var('OBS_VAR_NAME', v.obs_name)
                #self.add_env_var('OBS_VAR_EXTRA', v.obs_extra)
                self.add_env_var('OBS_VAR_LEVELS_LIST', ''.join(obs_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                for region in region_list:
                    self.add_env_var('REGION', region)
                    for lead in lead_list:
                        if lead < 10:
                            lead_string = '0'+str(lead)
                        else:
                            lead_string = str(lead)
                        self.add_env_var('LEAD', lead_string)
                        for vl in range(len(fcst_var_levels_list)):
                            self.add_env_var('FCST_VAR_LEVEL', fcst_var_levels_list[vl])
                            self.add_env_var('OBS_VAR_LEVEL', obs_var_levels_list[vl])
                            py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_ts.py")
                            process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                            process.wait() 
                            print("")
                        ####py_cmd = os.path.join("python3")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tp.py") #add python3 at top of script
                        py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tp.py")
                        process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                        process.wait()
                        print("")
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tsmean.py")
                    process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                    process.wait()
                    print("")
                    ####py_cmd = os.path.join("python3")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tpmean.py") #add python3 at top of script
                    py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tpmean.py")
                    process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                    process.wait()
                    print("")
            loop_hour += loop_inc

    def grid2grid_anom_plots(self):
        self.logger.info("Making plots for grid2grid-anom")
        logging_filename = self.logger.handlers[0].baseFilename
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            loop_beg_hour = self.p.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'INIT_END_HOUR')
            loop_inc = self.p.getint('config', 'INIT_INC')
            date_filter_method = "Initialization"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INC')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        if os.path.exists(plotting_out_dir):
            self.logger.info(plotting_out_dir+" exist, removing")
            util.rmtree(plotting_out_dir)
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = self.p.getstr('config', 'MODEL_LIST')
        plot_stats_list = self.p.getstr('config', 'PLOT_STATS_LIST')
        self.add_env_var("STAT_FILES_INPUT_DIR", stat_files_input_dir)
        self.add_env_var("PLOTTING_OUT_DIR", plotting_out_dir)
        self.add_env_var("MODEL_LIST", model_list)
        self.add_env_var("PLOT_STATS_LIST", plot_stats_list)
        #need to grab var info in special way that differs from util.parse_var_list
        #need variables with cooresponding list of levels; logic derived from util.parse_var_list
        var_info_list = []
        # find all FCST_VARn_NAME keys in the conf files
        all_conf = self.p.keys('config')
        fcst_indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
           result = regex.match(conf)
           if result is not None:
              fcst_indices.append(result.group(1))
        # loop over all possible variables and add them to list
        for n in fcst_indices:
            # get fcst var info if available
            if self.p.has_option('config', "FCST_VAR"+n+"_NAME"):
                fcst_name = self.p.getstr('config', "FCST_VAR"+n+"_NAME")

            fcst_extra = ""
            if self.p.has_option('config', "FCST_VAR"+n+"_OPTIONS"):
                fcst_extra = util.getraw_interp(self.p, 'config', "FCST_VAR"+n+"_OPTIONS")

            fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            # if OBS_VARn_X does not exist, use FCST_VARn_X
            if self.p.has_option('config', "OBS_VAR"+n+"_NAME"):
                obs_name = self.p.getstr('config', "OBS_VAR"+n+"_NAME")
            else:
                obs_name = fcst_name

            obs_extra = ""
            if self.p.has_option('config', "OBS_VAR"+n+"_OPTIONS"):
                obs_extra = util.getraw_interp(self.p, 'config', "OBS_VAR"+n+"_OPTIONS")
            ##else:
            ##    obs_extra = fcst_extra
            ##fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            if self.p.has_option('config', "OBS_VAR"+n+"_LEVELS"):
                obs_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            else:
                obs_levels = fcst_levels

            if len(fcst_levels) != len(obs_levels):
                print("ERROR: FCST_VAR"+n+"_LEVELS and OBS_VAR"+n+\
                          "_LEVELS do not have the same number of elements")
                exit(1)
            fo = util.FieldObj()
            fo.fcst_name = fcst_name
            fo.obs_name = obs_name
            fo.fcst_extra = fcst_extra
            fo.obs_extra = obs_extra
            fo.fcst_level = fcst_levels
            fo.obs_level = obs_levels
            var_info_list.append(fo)
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            #filtering times based on if files made based on init_time or valid_time
            self.add_env_var('CYCLE', loop_hour_str)
            for v in var_info_list:
                fcst_var_levels_list = v.fcst_level
                self.add_env_var('FCST_VAR_NAME', v.fcst_name)
                #self.add_env_var('FCST_VAR_EXTRA', v.fcst_extra)
                self.add_env_var('FCST_VAR_LEVELS_LIST', ''.join(fcst_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                obs_var_levels_list = v.obs_level
                self.add_env_var('OBS_VAR_NAME', v.obs_name)
                #self.add_env_var('OBS_VAR_EXTRA', v.obs_extra)
                self.add_env_var('OBS_VAR_LEVELS_LIST', ''.join(obs_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                for region in region_list:
                    self.add_env_var('REGION', region)
                    for vl in range(len(fcst_var_levels_list)):
                         self.add_env_var('FCST_VAR_LEVEL', fcst_var_levels_list[vl])
                         self.add_env_var('OBS_VAR_LEVEL', obs_var_levels_list[vl])
                         for lead in lead_list:
                             if lead < 10:
                                 lead_string = '0'+str(lead)    
                             else:
                                 lead_string = str(lead)
                             self.add_env_var('LEAD', lead_string)
                             py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_ts.py")
                             process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                             process.wait()
                             print("")
                             if v.fcst_name == 'HGT' or v.obs_name == 'HGT':
                                  fourier_decomp_height = self.p.getbool('config', 'FOURIER_HEIGHT_DECOMP')
                                  if fourier_decomp_height:
                                      wave_num_beg_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_BEG_LIST'))
                                      wave_num_end_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_END_LIST'))
                                      if len(wave_num_beg_list) != len(wave_num_end_list):
                                          print("ERROR: WAVE_NUM_BEG_LIST and WAVE_NUM_END_LIST do not have the same number of elements")
                                          exit(1)
                                      else:
                                           wave_num_beg_list_str = self.p.getstr('config', 'WAVE_NUM_BEG_LIST')
                                           wave_num_end_list_str = self.p.getstr('config', 'WAVE_NUM_END_LIST')
                                           self.add_env_var('WAVE_NUM_BEG_LIST', wave_num_beg_list_str)
                                           self.add_env_var('WAVE_NUM_END_LIST', wave_num_end_list_str) 
                                           py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_ts_HGTfourier.py")
                                           process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                                           process.wait()
                                           print("") 
                         self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                         py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_tsmean.py")
                         process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                         process.wait()
                         print("")
                         if v.fcst_name == 'HGT' or v.obs_name == 'HGT':
                             fourier_decomp_height = self.p.getbool('config', 'FOURIER_HEIGHT_DECOMP')
                             if fourier_decomp_height:
                                 wave_num_beg_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_BEG_LIST'))
                                 wave_num_end_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_END_LIST'))
                                 if len(wave_num_beg_list) != len(wave_num_end_list):
                                      print("ERROR: WAVE_NUM_BEG_LIST and WAVE_NUM_END_LIST do not have the same number of elements")
                                      exit(1)
                                 else:
                                      wave_num_beg_list_str = self.p.getstr('config', 'WAVE_NUM_BEG_LIST')
                                      wave_num_end_list_str = self.p.getstr('config', 'WAVE_NUM_END_LIST')
                                      self.add_env_var('WAVE_NUM_BEG_LIST', wave_num_beg_list_str)
                                      self.add_env_var('WAVE_NUM_END_LIST', wave_num_end_list_str)
                                      py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_tsmean_HGTfourier.py")
                                      process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                                      process.wait()
                                      print("")
                         ####py_cmd = os.path.join("python3")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_timemap.py") #add python3 at top of script
                         py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_timemap.py")
                         process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                         process.wait()
                         print("")       
            loop_hour += loop_inc
 
    def grid2grid_sfc_plots(self):
        self.logger.info("Making plots for grid2grid-sfc")
        logging_filename = self.logger.handlers[0].baseFilename
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            loop_beg_hour = self.p.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'INIT_END_HOUR')
            loop_inc = self.p.getint('config', 'INIT_INC')
            date_filter_method = "Initialization"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INC')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        if os.path.exists(plotting_out_dir):
            self.logger.info(plotting_out_dir+" exist, removing")
            util.rmtree(plotting_out_dir)
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = self.p.getstr('config', 'MODEL_LIST')
        plot_stats_list = self.p.getstr('config', 'PLOT_STATS_LIST')
        self.add_env_var("STAT_FILES_INPUT_DIR", stat_files_input_dir)
        self.add_env_var("PLOTTING_OUT_DIR", plotting_out_dir)
        self.add_env_var("MODEL_LIST", model_list)
        self.add_env_var("PLOT_STATS_LIST", plot_stats_list)
        var_list = util.parse_var_list(self.p)
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for var_info in var_list:
                fcst_var_name = var_info.fcst_name
                fcst_var_level = var_info.fcst_level
                #fcst_var_extra =  var_info.fcst_extra.replace(" = ", "").rstrip(";")
                obs_var_name = var_info.obs_name
                obs_var_level = var_info.obs_level
                #obs_var_extra =  var_info.obs_extra.replace(" = ", "").rstrip(";")
                self.add_env_var('FCST_VAR_NAME', fcst_var_name)
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level)
                self.add_env_var('OBS_VAR_NAME', obs_var_name)
                self.add_env_var('OBS_VAR_LEVEL', obs_var_level)
                for region in region_list:
                    self.add_env_var('REGION', region)
                    for lead in lead_list:
                        if lead < 10:
                            lead_string = '0'+str(lead)
                        else:
                            lead_string = str(lead)
                        self.add_env_var('LEAD', lead_string)
                        py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_sfc_ts.py")
                        process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                        process.wait()
                        print("")
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2grid_sfc_tsmean.py")
                    process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                    process.wait()
                    print("")
            loop_hour += loop_inc

    def grid2obs_upper_air_plots(self):
        self.logger.info("Making plots for grid2obs-upper_air")
        try:
            logging_filename = self.logger.parent.handlers[0].baseFilename
        except:
            logging_filename = self.logger.handlers[0].baseFilename
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            init_beg_hour = self.p.getstr('config', 'INIT_BEG_HOUR')
            init_end_hour = self.p.getstr('config', 'INIT_END_HOUR')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INC')
            date_filter_method = "Initialization"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            valid_beg_hour = self.p.getstr('config', 'VALID_BEG_HOUR')
            valid_end_hour = self.p.getstr('config', 'VALID_END_HOUR')
            loop_beg_hour = self.p.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'INIT_END_HOUR')
            loop_inc = self.p.getint('config', 'INIT_INC')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        if os.path.exists(plotting_out_dir):
            self.logger.info(plotting_out_dir+" exist, removing")
            util.rmtree(plotting_out_dir)
        regrid_to_grid = self.p.getstr('config', 'REGRID_TO_GRID')
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = self.p.getstr('config', 'MODEL_LIST')
        plot_stats_list = self.p.getstr('config', 'PLOT_STATS_LIST')
        self.add_env_var("REGRID_TO_GRID", regrid_to_grid)
        self.add_env_var("STAT_FILES_INPUT_DIR", stat_files_input_dir)
        self.add_env_var("PLOTTING_OUT_DIR", plotting_out_dir)
        self.add_env_var("MODEL_LIST", model_list)
        self.add_env_var("PLOT_STATS_LIST", plot_stats_list)
        #need to grab var info in special way that differs from util.parse_var_list
        #need variables with cooresponding list of levels; logic derived from util.parse_var_list
        var_info_list = []
        # find all FCST_VARn_NAME keys in the conf files
        all_conf = self.p.keys('config')
        fcst_indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
           result = regex.match(conf)
           if result is not None:
              fcst_indices.append(result.group(1))
        # loop over all possible variables and add them to list
        for n in fcst_indices:
            # get fcst var info if available
            if self.p.has_option('config', "FCST_VAR"+n+"_NAME"):
                fcst_name = self.p.getstr('config', "FCST_VAR"+n+"_NAME")

            fcst_extra = ""
            if self.p.has_option('config', "FCST_VAR"+n+"_OPTIONS"):
                fcst_extra = util.getraw_interp(self.p, 'config', "FCST_VAR"+n+"_OPTIONS")

            fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            # if OBS_VARn_X does not exist, use FCST_VARn_X
            if self.p.has_option('config', "OBS_VAR"+n+"_NAME"):
                obs_name = self.p.getstr('config', "OBS_VAR"+n+"_NAME")
            else:
                obs_name = fcst_name

            obs_extra = ""
            if self.p.has_option('config', "OBS_VAR"+n+"_OPTIONS"):
                obs_extra = util.getraw_interp(self.p, 'config', "OBS_VAR"+n+"_OPTIONS")
            ##else:
            ##    obs_extra = fcst_extra
            ##fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            if self.p.has_option('config', "OBS_VAR"+n+"_LEVELS"):
                obs_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
            else:
                obs_levels = fcst_levels

            if len(fcst_levels) != len(obs_levels):
                print("ERROR: FCST_VAR"+n+"_LEVELS and OBS_VAR"+n+\
                          "_LEVELS do not have the same number of elements")
                exit(1)
            fo = util.FieldObj()
            fo.fcst_name = fcst_name
            fo.obs_name = obs_name
            fo.fcst_extra = fcst_extra
            fo.obs_extra = obs_extra
            fo.fcst_level = fcst_levels
            fo.obs_level = obs_levels
            var_info_list.append(fo)
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for v in var_info_list:
                fcst_var_levels_list = v.fcst_level
                self.add_env_var('FCST_VAR_NAME', v.fcst_name)
                #self.add_env_var('FCST_VAR_EXTRA', v.fcst_extra)
                self.add_env_var('FCST_VAR_LEVELS_LIST', ''.join(fcst_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                obs_var_levels_list = v.obs_level
                self.add_env_var('OBS_VAR_NAME', v.obs_name)
                #self.add_env_var('OBS_VAR_EXTRA', v.obs_extra)
                self.add_env_var('OBS_VAR_LEVELS_LIST', ''.join(obs_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                for region in region_list:
                    self.add_env_var('REGION', region)
                    for lead in lead_list:
                        if lead < 10:
                            lead_string = '0'+str(lead)
                        else:
                            lead_string = str(lead)
                        self.add_env_var('LEAD', lead_string)
                        for vl in range(len(fcst_var_levels_list)):
                            self.add_env_var('FCST_VAR_LEVEL', fcst_var_levels_list[vl])
                            self.add_env_var('OBS_VAR_LEVEL', obs_var_levels_list[vl])
                            py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_ts.py")
                            process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                            process.wait()
                            print("")
                        ####py_cmd = os.path.join("python3")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_vertprof.py") #add python3 at top of script
                        py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_vertprof.py")
                        process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                        process.wait()
                        print("")
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_tsmean.py")
                    process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                    process.wait()
                    print("")
                    ####py_cmd = os.path.join("python3")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_verfprofmean.py") #add python3 at top of script
                    py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_vertprofmean.py")
                    process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                    process.wait()
            print("")
            loop_hour += loop_inc

    def grid2obs_conus_sfc_plots(self):
        self.logger.info("Making plots for grid2obs-conus_sfc")
        try:
            logging_filename = self.logger.parent.handlers[0].baseFilename
        except:
            logging_filename = self.logger.handlers[0].baseFilename
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            init_beg_hour = self.p.getstr('config', 'INIT_BEG_HOUR')
            init_end_hour = self.p.getstr('config', 'INIT_END_HOUR')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INC')
            date_filter_method = "Initialization"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            valid_beg_hour = self.p.getstr('config', 'VALID_BEG_HOUR')
            valid_end_hour = self.p.getstr('config', 'VALID_END_HOUR')
            loop_beg_hour = self.p.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'INIT_END_HOUR')
            loop_inc = self.p.getint('config', 'INIT_INC')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        if os.path.exists(plotting_out_dir):
            self.logger.info(plotting_out_dir+" exist, removing")
            util.rmtree(plotting_out_dir)
        regrid_to_grid = self.p.getstr('config', 'REGRID_TO_GRID')
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = self.p.getstr('config', 'MODEL_LIST')
        plot_stats_list = self.p.getstr('config', 'PLOT_STATS_LIST')
        self.add_env_var("REGRID_TO_GRID", regrid_to_grid)
        self.add_env_var("STAT_FILES_INPUT_DIR", stat_files_input_dir)
        self.add_env_var("PLOTTING_OUT_DIR", plotting_out_dir)
        self.add_env_var("MODEL_LIST", model_list)
        self.add_env_var("PLOT_STATS_LIST", plot_stats_list)
        var_list = util.parse_var_list(self.p)
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for var_info in var_list:
                fcst_var_name = var_info.fcst_name
                fcst_var_level = var_info.fcst_level
                #fcst_var_extra =  var_info.fcst_extra.replace(" = ", "").rstrip(";")
                obs_var_name = var_info.obs_name
                obs_var_level = var_info.obs_level
                #obs_var_extra =  var_info.obs_extra.replace(" = ", "").rstrip(";")
                self.add_env_var('FCST_VAR_NAME', fcst_var_name)
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level)
                self.add_env_var('OBS_VAR_NAME', obs_var_name)
                self.add_env_var('OBS_VAR_LEVEL', obs_var_level)
                for region in region_list:
                    self.add_env_var('REGION', region)
                    for lead in lead_list:
                        if lead < 10:
                            lead_string = '0'+str(lead)
                        else:
                            lead_string = str(lead)
                        self.add_env_var('LEAD', lead_string)
                        py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_conus_sfc_ts.py")
                        process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                        process.wait()
                        print("")
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    py_cmd = os.path.join("python")+" "+os.path.join(plotting_scripts_dir, "plot_grid2obs_conus_sfc_tsmean.py")
                    process = subprocess.Popen(py_cmd, env=self.env, shell=True)
                    process.wait()
                    print("")
            loop_hour += loop_inc

########################################################################
########################################################################
########################################################################
    def run_all_times(self):
        self.logger.info("RUNNING SCRIPTS FOR PLOTTING")
        verif_case = self.p.getstr('config', 'VERIF_CASE')
        verif_type = self.p.getstr('config', 'VERIF_TYPE')
        if verif_case == 'grid2grid':
            if verif_type == 'pres':
                 self.grid2grid_pres_plots()
            elif verif_type == 'anom':
                 self.grid2grid_anom_plots()
            elif verif_type == 'sfc':
                 self.grid2grid_sfc_plots()
            else:
                 self.logger.error("Not a valid VERIF_TYPE option for grid2grid")
                 exit(1)
        elif verif_case == 'grid2obs':
            if verif_type == 'conus_sfc':
                 self.grid2obs_conus_sfc_plots()
            elif verif_type == 'upper_air':
                 self.grid2obs_upper_air_plots()
            else:
                 self.logger.error("Not a valid VERIF_TYPE option for grid2obs")
                 exit(1)
        elif verif_case == 'precip':
            self.logger.info("Formatting for plotting for precip")
        else:
            self.logger.error("Not a valid VERIF_CASE option")
            exit(1)
