#!/usr/bin/env python

'''
Program Name: make_plots_wrapper.py
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
        self.app_path = 'python'
        self.app_name = 'make_plots'
        if self.logger is None:
            self.logger = util.get_logger(self.p,sublog='MakePlots')

    def set_plotting_script(self, plotting_script_path):
        self.plotting_script = plotting_script_path

    def get_command(self):
        if self.app_path is None:
            self.logger.error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None
        cmd = self.app_path + " "
        
        if self.plotting_script == "":
            self.logger.error(self.app_name+": No plotting script specified")
            return None
        cmd += self.plotting_script

        return cmd

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
                model_list.append(model_name)
        return model_list
    
    def parse_vars_with_level_list(self):
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
                self.logger.error("ERROR: FCST_VAR"+n+"_LEVELS and OBS_VAR"+n+\
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
        return var_info_list

    def get_logging_info(self):
        logging_filename = self.p.getstr('config', 'LOG_METPLUS')
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        logging_level = self.p.getstr('config', 'LOG_LEVEL')
        self.add_env_var("LOGGING_LEVEL", logging_level)
    
    def get_grid2grid_date_info(self):
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            loop_beg_hour = self.p.getint('config', 'INIT_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'INIT_END_HOUR')
            loop_inc = self.p.getint('config', 'INIT_INCREMENT')
            date_filter_method = "Initialization"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INCREMENT')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        return loop_beg_hour, loop_end_hour, loop_inc    

    def get_grid2obs_date_info(self):
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            init_beg_hour = self.p.getstr('config', 'INIT_BEG_HOUR')
            init_end_hour = self.p.getstr('config', 'INIT_END_HOUR')
            loop_beg_hour = self.p.getint('config', 'VALID_BEG_HOUR')
            loop_end_hour = self.p.getint('config', 'VALID_END_HOUR')
            loop_inc = self.p.getint('config', 'VALID_INCREMENT')
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
            loop_inc = self.p.getint('config', 'INIT_INCREMENT')
            date_filter_method = "Valid"
            self.add_env_var("START_T", start_t)
            self.add_env_var("END_T", end_t)
            self.add_env_var("DATE_FILTER_METHOD", date_filter_method)
        return loop_beg_hour, loop_end_hour, loop_inc
       
    def get_plotting_info(self):
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        self.add_env_var("STAT_FILES_INPUT_DIR", stat_files_input_dir)
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        self.add_env_var("PLOTTING_OUT_DIR", plotting_out_dir)
        plot_stats_list = self.p.getstr('config', 'PLOT_STATS_LIST')
        self.add_env_var("PLOT_STATS_LIST", plot_stats_list)
        verif_type = self.p.getstr('config', 'VERIF_TYPE')
        plotting_out_dir_type = os.path.join(plotting_out_dir, verif_type)
        if os.path.exists(plotting_out_dir_type):
            self.logger.info(plotting_out_dir_type+" exist, removing")
            util.rmtree(plotting_out_dir_type)
        util.mkdir_p(plotting_out_dir_type)
        return plotting_scripts_dir

    def grid2grid_pres_plots(self):
        self.logger.info("Making plots for grid2grid-pres")
        #set logging info for plotting scripts
        self.get_logging_info()
        #get looping hour info and set date info
        loop_beg_hour, loop_end_hour, loop_inc = self.get_grid2grid_date_info()
        #get model info
        model_names = self.parse_model_list()
        self.add_env_var("MODEL_NAMES", ' '.join(model_names))
        #get variable info 
        var_info_list = self.parse_vars_with_level_list()
        #get lead info
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        #get region info
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        #get plotting script directory and other plotting info
        plotting_scripts_dir = self.get_plotting_info()
        #start loops to run plotting scripts 
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for v in var_info_list:
                fcst_var_levels_list = v.fcst_level
                self.add_env_var('FCST_VAR_NAME', v.fcst_name)
                self.add_env_var('FCST_VAR_LEVELS_LIST', ''.join(fcst_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                obs_var_levels_list = v.obs_level
                self.add_env_var('OBS_VAR_NAME', v.obs_name)
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
                            #build command
                            self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_ts.py"))
                            self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                            cmd = self.get_command()
                            if cmd is None:
                                self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                                return
                            self.build()
                            self.clear()
                        #build command
                        self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tp.py"))
                        self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+v.fcst_name+" obs var:"+v.obs_name)
                        cmd = self.get_command()
                        if cmd is None:
                            self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                            return
                        self.build()
                        self.clear()
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    #build command
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tsmean.py"))
                    self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+" obs var:"+v.obs_name)
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
                    #build command
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_pres_tpmean.py"))
                    self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+" obs var:"+v.obs_name)
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
            loop_hour += loop_inc

    def grid2grid_anom_plots(self):
        self.logger.info("Making plots for grid2grid-anom")
        #set logging info for plotting scripts
        self.get_logging_info()
        #get looping hour info and set date info
        loop_beg_hour, loop_end_hour, loop_inc = self.get_grid2grid_date_info()
        #get model info
        model_names = self.parse_model_list()
        self.add_env_var("MODEL_NAMES", ' '.join(model_names))
        #get variable info 
        var_info_list = self.parse_vars_with_level_list()
        #get lead info
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        #get region info
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        #get plotting script directory and other plotting info
        plotting_scripts_dir = self.get_plotting_info()
        #start loops to run plotting scripts
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for v in var_info_list:
                fcst_var_levels_list = v.fcst_level
                self.add_env_var('FCST_VAR_NAME', v.fcst_name)
                self.add_env_var('FCST_VAR_LEVELS_LIST', ''.join(fcst_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                obs_var_levels_list = v.obs_level
                self.add_env_var('OBS_VAR_NAME', v.obs_name)
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
                             #build command
                             self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_ts.py"))
                             self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                             cmd = self.get_command()
                             if cmd is None:
                                 self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                                 return
                             self.logger.info("")
                             self.build()
                             self.clear()
                             if v.fcst_name == 'HGT' or v.obs_name == 'HGT':
                                  fourier_decomp_height = self.p.getbool('config', 'FOURIER_HEIGHT_DECOMP')
                                  if fourier_decomp_height:
                                      wave_num_beg_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_BEG_LIST'))
                                      wave_num_end_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_END_LIST'))
                                      if len(wave_num_beg_list) != len(wave_num_end_list):
                                          self.logger.error("ERROR: WAVE_NUM_BEG_LIST and WAVE_NUM_END_LIST do not have the same number of elements")
                                          exit(1)
                                      else:
                                           wave_num_beg_list_str = self.p.getstr('config', 'WAVE_NUM_BEG_LIST')
                                           wave_num_end_list_str = self.p.getstr('config', 'WAVE_NUM_END_LIST')
                                           self.add_env_var('WAVE_NUM_BEG_LIST', wave_num_beg_list_str)
                                           self.add_env_var('WAVE_NUM_END_LIST', wave_num_end_list_str)
                                           #build command
                                           self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_ts_HGTfourier.py"))
                                           self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                                           cmd = self.get_command()
                                           if cmd is None:
                                               self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                                               return
                                           self.build()
                                           self.clear() 
                         self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                         #build command
                         self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_tsmean.py"))
                         self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                         cmd = self.get_command()
                         if cmd is None:
                             self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                             return
                         self.build()
                         self.clear()
                         if v.fcst_name == 'HGT' or v.obs_name == 'HGT':
                             fourier_decomp_height = self.p.getbool('config', 'FOURIER_HEIGHT_DECOMP')
                             if fourier_decomp_height:
                                 wave_num_beg_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_BEG_LIST'))
                                 wave_num_end_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_END_LIST'))
                                 if len(wave_num_beg_list) != len(wave_num_end_list):
                                      self.logger.error("ERROR: WAVE_NUM_BEG_LIST and WAVE_NUM_END_LIST do not have the same number of elements")
                                      exit(1)
                                 else:
                                      wave_num_beg_list_str = self.p.getstr('config', 'WAVE_NUM_BEG_LIST')
                                      wave_num_end_list_str = self.p.getstr('config', 'WAVE_NUM_END_LIST')
                                      self.add_env_var('WAVE_NUM_BEG_LIST', wave_num_beg_list_str)
                                      self.add_env_var('WAVE_NUM_END_LIST', wave_num_end_list_str)
                                      #build command
                                      self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_tsmean_HGTfourier.py"))
                                      self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                                      cmd = self.get_command()
                                      if cmd is None:
                                          self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                                          return
                                      self.build()
                                      self.clear()
                         #build command
                         self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_anom_timemap.py"))
                         self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                         cmd = self.get_command()
                         if cmd is None:
                             self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                             return
                         self.build()
                         self.clear()
            loop_hour += loop_inc
 
    def grid2grid_sfc_plots(self):
        self.logger.info("Making plots for grid2grid-sfc")
        #set logging info for plotting scripts
        self.get_logging_info()
        #get looping hour info and set date info
        loop_beg_hour, loop_end_hour, loop_inc = self.get_grid2grid_date_info()
        #get model info
        model_names = self.parse_model_list()
        self.add_env_var("MODEL_NAMES", ' '.join(model_names))
        #get variable info 
        var_list = util.parse_var_list(self.p)
        #get lead info
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        #get region info
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        #get plotting script directory and other plotting info
        plotting_scripts_dir = self.get_plotting_info()
        #start loops to run plotting scripts
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
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
                    for lead in lead_list:
                        if lead < 10:
                            lead_string = '0'+str(lead)
                        else:
                            lead_string = str(lead)
                        self.add_env_var('LEAD', lead_string)
                        #build command
                        self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_sfc_ts.py"))
                        self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
                        cmd = self.get_command()
                        if cmd is None:
                            self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                            return
                        self.build()
                        self.clear()
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    #build command
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2grid_sfc_tsmean.py"))
                    self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
            loop_hour += loop_inc

    def grid2obs_upper_air_plots(self):
        self.logger.info("Making plots for grid2obs-upper_air")
        #set logging info for plotting scripts
        self.get_logging_info()
        #get looping hour info and set date info
        loop_beg_hour, loop_end_hour, loop_inc = self.get_grid2obs_date_info()
        #get model info
        model_names = self.parse_model_list()
        self.add_env_var("MODEL_NAMES", ' '.join(model_names))
        #get variable info 
        var_info_list = self.parse_vars_with_level_list()
        #get lead info
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        #get region info
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        #get grid info
        regrid_to_grid = self.p.getstr('config', 'REGRID_TO_GRID')
        self.add_env_var("REGRID_TO_GRID", regrid_to_grid)
        #get plotting script directory and other plotting info
        plotting_scripts_dir = self.get_plotting_info()
        #start loops to run plotting scripts
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
            for v in var_info_list:
                fcst_var_levels_list = v.fcst_level
                self.add_env_var('FCST_VAR_NAME', v.fcst_name)
                self.add_env_var('FCST_VAR_LEVELS_LIST', ''.join(fcst_var_levels_list).replace("P", " P").lstrip().replace(" P", ", P"))
                obs_var_levels_list = v.obs_level
                self.add_env_var('OBS_VAR_NAME', v.obs_name)
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
                            #build command
                            self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_ts.py"))
                            self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+v.fcst_name+"_"+fcst_var_levels_list[vl]+" obs var:"+v.obs_name+"_"+obs_var_levels_list[vl])
                            cmd = self.get_command()
                            if cmd is None:
                                self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                                return
                            self.build()
                            self.clear()
                        #build command
                        self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_vertprof.py"))
                        self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+v.fcst_name+" obs var:"+v.obs_name)
                        cmd = self.get_command()
                        if cmd is None:
                            self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                            return
                        self.build()
                        self.clear()
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    #build command
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_tsmean.py"))
                    self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+" obs var:"+v.obs_name)
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
                    #build command
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2obs_upper_air_vertprofmean.py"))
                    self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+v.fcst_name+" obs var:"+v.obs_name)
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
            loop_hour += loop_inc

    def grid2obs_conus_sfc_plots(self):
        self.logger.info("Making plots for grid2obs-conus_sfc")
        #set logging info for plotting scripts
        self.get_logging_info()
        #get looping hour info and set date info
        loop_beg_hour, loop_end_hour, loop_inc = self.get_grid2obs_date_info()
        #get model info
        model_names = self.parse_model_list()
        self.add_env_var("MODEL_NAMES", ' '.join(model_names))
        #get variable info 
        var_list = util.parse_var_list(self.p)
        #get lead info
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        #get region info
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        #get grid info
        regrid_to_grid = self.p.getstr('config', 'REGRID_TO_GRID')
        self.add_env_var("REGRID_TO_GRID", regrid_to_grid)
        #get plotting script directory and other plotting info
        plotting_scripts_dir = self.get_plotting_info()
        #start loops to run plotting scripts
        loop_hour = loop_beg_hour
        while loop_hour <= loop_end_hour:
            loop_hour_str = str(loop_hour).zfill(2)
            self.add_env_var('CYCLE', loop_hour_str)
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
                    for lead in lead_list:
                        if lead < 10:
                            lead_string = '0'+str(lead)
                        else:
                            lead_string = str(lead)
                        self.add_env_var('LEAD', lead_string)
                        #build command
                        self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2obs_conus_sfc_ts.py"))
                        self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z lead:"+lead_string+" region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
                        cmd = self.get_command()
                        if cmd is None:
                            self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                            return
                        self.build()
                        self.clear()
                    self.add_env_var("LEAD_LIST", self.p.getstr('config', 'LEAD_LIST'))
                    #build command
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_grid2obs_conus_sfc_tsmean.py"))
                    self.logger.info("Building command for "+self.plotting_script+" cycle:"+str(loop_hour)+"Z region:"+region+" fcst var:"+fcst_var_name+"_"+fcst_var_level+" obs var:"+obs_var_name+"_"+obs_var_level)
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
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
