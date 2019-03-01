#!/usr/bin/env python

'''
Program Name: make_plots_wrapper.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make plots
History Log:  Third version
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
import time
import calendar
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
 
    class ValidInitTimesPairs(object):
        __slots__ = 'valid', 'init'

    def pair_valid_init_times(self, valid_hour_list, valid_method, init_hour_list, init_method):
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

    def parse_vars_with_level_thresh_list(self):
        var_info = []
        all_conf = self.p.keys('config')
        fcst_indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
           result = regex.match(conf)
           if result is not None:
              fcst_indices.append(result.group(1))
        for n in fcst_indices:
            if self.p.has_option('config', "FCST_VAR"+n+"_NAME"):
                fcst_name = self.p.getstr('config', "FCST_VAR"+n+"_NAME")
                if self.p.has_option('config', "FCST_VAR"+n+"_LEVELS"):
                    fcst_levels = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_LEVELS"))
                else:
                    self.logger.error("FCST_VAR"+n+"_LEVELS not defined")
                    exit(1)
                if self.p.has_option('config', "FCST_VAR"+n+"_OPTIONS"):
                    fcst_extra = util.getraw_interp(self.p, 'config', "FCST_VAR"+n+"_OPTIONS")
                else:
                    fcst_extra = ""
                if self.p.has_option('config', "FCST_VAR"+n+"_THRESH"):
                    fcst_thresh = util.getlist(self.p.getstr('config', "FCST_VAR"+n+"_THRESH"))
                else:
                    fcst_thresh = ""
                if self.p.has_option('config', "OBS_VAR"+n+"_NAME"):
                    obs_name = self.p.getstr('config', "OBS_VAR"+n+"_NAME")
                else:
                    obs_name = fcst_name
                if self.p.has_option('config', "OBS_VAR"+n+"_LEVELS"):
                    obs_levels = util.getlist(self.p.getstr('config', "OBS_VAR"+n+"_LEVELS"))
                    if len(fcst_levels) != len(obs_levels):
                        self.logger.error("FCST_VAR"+n+"_LEVELS and OBS_VAR"+n+"_LEVELS do not have the same number of elements")
                        exit(1)
                else:
                    obs_levels = fcst_levels
                if self.p.has_option('config', "OBS_VAR"+n+"_OPTIONS"):
                    obs_extra = util.getraw_interp(self.p, 'config', "OBS_VAR"+n+"_OPTIONS")
                else:
                    obs_extra = ""
                if self.p.has_option('config', "OBS_VAR"+n+"_THRESH"):
                    obs_thresh = util.getlist(self.p.getstr('config', "OBS_VAR"+n+"_THRESH"))
                    if len(fcst_thresh) != len(obs_thresh):
                        self.logger.error("FCST_VAR"+n+"_THRESH and OBS_VAR"+n+"_THRESH do not have the same number of elements")
                        exit(1)
                else:
                    obs_thresh = fcst_thresh
            else:
                self.logger.error("FCST_VAR"+n+"_NAME not defined")
                exit(1)
            fo = util.FieldObj()
            fo.fcst_name = fcst_name
            fo.obs_name = obs_name
            fo.fcst_extra = fcst_extra
            fo.obs_extra = obs_extra
            fo.fcst_thresh = fcst_thresh
            fo.obs_thresh = obs_thresh
            fo.fcst_level = fcst_levels
            fo.obs_level = obs_levels
            fo.index = n
            var_info.append(fo)
        return var_info

    class FourierDecompInfo(object):
        __slots__ = 'run_fourier', 'wave_num_pairings'

    def parse_var_fourier_decomp(self):
        fourier_decom_list = []
        all_conf = self.p.keys('config')
        indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                indices.append(result.group(1))
        for n in indices:
            if self.p.has_option('config', "FCST_VAR"+n+"_NAME"):
                run_fourier = self.p.getbool('config', "VAR"+n+"_FOURIER_DECOMP", False)
                fourier_wave_num_pairs = util.getlist(self.p.getstr('config', "VAR"+n+"_WAVE_NUM_LIST", ""))
                if run_fourier == False:
                    fourier_wave_num_pairs = ""
                fd_info = self.FourierDecompInfo()
                fd_info.run_fourier = run_fourier
                fd_info.wave_num_pairings = fourier_wave_num_pairs
                fourier_decom_list.append(fd_info)
        return fourier_decom_list
    
    def parse_model_list(self):
        model_name_list = []
        model_plot_name_list = []
        all_conf = self.p.keys('config')
        model_indices = []
        regex = re.compile("MODEL(\d+)_NAME$")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                model_indices.append(result.group(1))
        for m in model_indices:
            if self.p.has_option('config', "MODEL"+m+"_NAME"):
                model_name = self.p.getstr('config', "MODEL"+m+"_NAME")
                if self.p.has_option('config', "MODEL"+m+"_NAME_ON_PLOT"):
                    model_plot_name = self.p.getstr('config', "MODEL"+m+"_NAME_ON_PLOT")
                else:
                    model_plot_name = model_name
                model_name_list.append(model_name)
                model_plot_name_list.append(model_plot_name)
        return ' '.join(model_name_list),' '.join(model_plot_name_list)
 
    def create_plots_grid2grid_pres(self, fcst_var_level_list, obs_var_level_list,
                                    fcst_var_thresh_list, obs_var_thresh_list,
                                    interp, region, lead_list, plotting_scripts_dir):
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_test.py"))
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
                    exit()
        
    def create_plots_grid2grid_anom(self, fcst_var_level_list, obs_var_level_list,
                                    fcst_var_thresh_list, obs_var_thresh_list,
                                    interp, region, lead_list, plotting_scripts_dir):
        for lead in lead_list:
            self.logger.info(lead)
            for vl in range(len(fcst_var_level_list)):
                self.logger.info(fcst_var_level_list[vl]+" "+obs_var_level_list[vl])
                for vt in range(len(fcst_var_thresh_list)):
                    self.logger.info(fcst_var_thresh_list[vt]+" "+obs_var_thresh_list[vt])
     
    def create_plots_grid2grid_sfc(self, fcst_var_level_list, obs_var_level_list,
                                   fcst_var_thresh_list, obs_var_thresh_list,
                                   interp, region, lead_list, plotting_scripts_dir):
        for lead in lead_list:
            self.logger.info(lead)
            for vl in range(len(fcst_var_level_list)):
                self.logger.info(fcst_var_level_list[vl]+" "+obs_var_level_list[vl])
                for vt in range(len(fcst_var_thresh_list)):
                    self.logger.info(fcst_var_thresh_list[vt]+" "+obs_var_thresh_list[vt])

    def create_plots_grid2obs_upper_air(self, fcst_var_level_list, obs_var_level_list,
                                        fcst_var_thresh_list, obs_var_thresh_list,
                                        interp, region, lead_list, plotting_scripts_dir):
        for lead in lead_list:
            self.logger.info(lead)
            for vl in range(len(fcst_var_level_list)):
                self.logger.info(fcst_var_level_list[vl]+" "+obs_var_level_list[vl])
                for vt in range(len(fcst_var_thresh_list)):
                    self.logger.info(fcst_var_thresh_list[vt]+" "+obs_var_thresh_list[vt])
     
    def create_plots_grid2obs_conus_sfc(self, fcst_var_level_list, obs_var_level_list,
                                        fcst_var_thresh_list, obs_var_thresh_list,
                                        interp, region, lead_list, plotting_scripts_dir):
        for lead in lead_list:
            self.logger.info(lead)
            for vl in range(len(fcst_var_level_list)):
                self.logger.info(fcst_var_level_list[vl]+" "+obs_var_level_list[vl])
                for vt in range(len(fcst_var_thresh_list)):
                    self.logger.info(fcst_var_thresh_list[vt]+" "+obs_var_thresh_list[vt])
 
    def create_plots_precip(self):
        self.logger.error("Plotting for precip not incorporated in METplus yet")
        exit(1)
        
    #{STAT_FILES_INPUT_DIR}/grid2grid/pres/gfs/valid20180601to20180610_valid000000to000000Z_init000000to180000Z/gfs_f12_fcstHGTP1000_obsHGTP1000_interpNEAREST_regionNHX.stat
    def create_plots(self, verif_case, verif_type):
        self.logger.info("Running plots for VERIF_CASE = "+verif_case+", VERIF_TYPE = "+verif_type)
        #read config
        plot_time = self.p.getstr('config', 'PLOT_TIME')
        valid_beg_YYYYmmdd = self.p.getstr('config', 'VALID_BEG', "")
        valid_end_YYYYmmdd = self.p.getstr('config', 'VALID_END', "")
        valid_hour_method = self.p.getstr('config', 'VALID_HOUR_METHOD')
        valid_hour_beg = self.p.getstr('config', 'VALID_HOUR_BEG')
        valid_hour_end = self.p.getstr('config', 'VALID_HOUR_END')
        valid_hour_increment = self.p.getstr('config', 'VALID_HOUR_INCREMENT')
        init_beg_YYYYmmdd = self.p.getstr('config', 'INIT_BEG', "")
        init_end_YYYYmmdd = self.p.getstr('config', 'INIT_END', "")
        init_hour_method = self.p.getstr('config', 'INIT_HOUR_METHOD')
        init_hour_beg = self.p.getstr('config', 'INIT_HOUR_BEG')
        init_hour_end = self.p.getstr('config', 'INIT_HOUR_END')
        init_hour_increment = self.p.getstr('config', 'INIT_HOUR_INCREMENT')
        stat_files_input_dir = self.p.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.p.getdir('PLOTTING_OUT_DIR')
        plotting_scripts_dir = self.p.getdir('PLOTTING_SCRIPTS_DIR')
        plot_stats_list = self.p.getdir('PLOT_STATS_LIST')
        ci_method = self.p.getstr('config', 'CI_METHOD')
        verif_grid = self.p.getstr('config', 'VERIF_GRID')
        event_equalization = self.p.getstr('config', "EVENT_EQUALIZATION", "True")
        var_list = self.parse_vars_with_level_thresh_list()
        fourier_decom_list = self.parse_var_fourier_decomp()
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlist(self.p.getstr('config', 'LEAD_LIST'))
        model_name_str_list, model_plot_name_str_list = self.parse_model_list()
        plot_stats_list = self.p.getdir('PLOT_STATS_LIST')
        logging_filename = self.p.getstr('config', 'LOG_METPLUS')
        logging_level = self.p.getstr('config', 'LOG_LEVEL')
        #set envir vars based on config
        self.add_env_var('PLOT_TIME', plot_time)
        if plot_time == 'valid':
            self.add_env_var('START_DATE_YYYYmmdd', valid_beg_YYYYmmdd)
            self.add_env_var('END_DATE_YYYYmmdd', valid_end_YYYYmmdd)
        else:
            self.add_env_var('START_DATE_YYYYmmdd', init_beg_YYYYmmdd)
            self.add_env_var('END_DATE_YYYYmmdd', init_end_YYYYmmdd)
        self.add_env_var('STAT_FILES_INPUT_DIR', stat_files_input_dir)
        self.add_env_var('PLOTTING_OUT_DIR', plotting_out_dir)
        self.add_env_var('PLOT_STATS_LIST', plot_stats_list)
        self.add_env_var('MODEL_NAME_LIST', model_name_str_list)
        self.add_env_var('MODEL_PLOT_NAME_LIST', model_plot_name_str_list)
        self.add_env_var('CI_METHOD', ci_method)
        self.add_env_var('VERIF_GRID', verif_grid)
        self.add_env_var('EVENT_EQUALIZATION', event_equalization)
        self.add_env_var("LOGGING_FILENAME", logging_filename)
        self.add_env_var("LOGGING_LEVEL", logging_level)
        if os.path.exists(plotting_out_dir):
            self.logger.info(plotting_out_dir+" exists, removing")
            util.rmtree(plotting_out_dir)
        util.mkdir_p(plotting_out_dir)
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
            self.add_env_var('VALID_TIME_INFO', valid_init_time_pair.valid)
            self.add_env_var('INIT_TIME_INFO', valid_init_time_pair.init)
            #loop through variable information
            for var_info in var_list:
                self.add_env_var('FCST_VAR_NAME', var_info.fcst_name)
                self.add_env_var('OBS_VAR_NAME', var_info.obs_name)
                fcst_var_level_list = var_info.fcst_level
                obs_var_level_list = var_info.obs_level
                if len(var_info.fcst_extra) == 0:
                    self.add_env_var('FCST_VAR_EXTRA', "None")
                else:
                    self.add_env_var('FCST_VAR_EXTRA', var_info.fcst_extra)
                if len(var_info.obs_extra) == 0:
                    self.add_env_var('OBS_VAR_EXTRA', "None")
                else:
                    self.add_env_var('OBS_VAR_EXTRA', var_info.obs_extra)
                if len(var_info.fcst_thresh) == 0 or len(var_info.obs_thresh) == 0:
                    fcst_var_thresh_list = [ "None" ]
                    obs_var_thresh_list = [ "None" ]
                else:
                    fcst_var_thresh_list = var_info.fcst_thresh
                    obs_var_thresh_list = var_info.obs_thresh
                #check for fourier decompositon for variable, add to interp list
                interp_list = util.getlist(self.p.getstr('config', 'INTERP', ""))
                var_fourier_decomp_info = fourier_decom_list[var_list.index(var_info)]
                if var_fourier_decomp_info.run_fourier:
                    for pair in var_fourier_decomp_info.wave_num_pairings:
                        interp_list.append("WV1_"+pair)
                #loop through interpolation information
                for interp in interp_list:
                    self.add_env_var('INTERP', interp)
                    #loop through region information
                    for region in region_list:
                        self.add_env_var('REGION', region)
                        #call specific plot definitions to make plots
                        if verif_case == "grid2grid" and verif_type in "pres":
                            self.create_plots_grid2grid_pres(fcst_var_level_list, obs_var_level_list,
                                                             fcst_var_thresh_list, obs_var_thresh_list,
                                                             interp, region, lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2grid" and verif_type in "anom":
                            self.create_plots_grid2grid_anom(fcst_var_level_list, obs_var_level_list,
                                                             fcst_var_thresh_list, obs_var_thresh_list,
                                                             interp, region, lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2grid" and verif_type in "sfc":
                            self.create_plots_grid2grid_sfc(fcst_var_level_list, obs_var_level_list,
                                                            fcst_var_thresh_list, obs_var_thresh_list,
                                                            interp, region, lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2obs" and verif_type in "upper_air":
                            self.create_plots_grid2obs_upper_air(fcst_var_level_list, obs_var_level_list,
                                                                 fcst_var_thresh_list, obs_var_thresh_list,
                                                                 interp, region, lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2obs" and verif_type in "conus_sfc":
                            self.create_plots_grid2obs_conus_sfc(fcst_var_level_list, obs_var_level_list,
                                                                 fcst_var_thresh_list, obs_var_thresh_list,
                                                                 interp, region, lead_list, plotting_scripts_dir)
                        elif verif_case == "precip":
                            self.create_plots_precip()

    def run_all_times(self):
        verif_case = self.p.getstr('config', 'VERIF_CASE')
        verif_type = self.p.getstr('config', 'VERIF_TYPE')
        self.add_env_var('VERIF_CASE', verif_case)
        self.add_env_var('VERIF_TYPE', verif_type)
        if verif_case == "grid2grid":
            if verif_type in ("pres", "anom", "sfc"): 
                run_make_plots = True
            else:
               run_make_plots = False
               self.logger.error(verif_type+" is not an accepted VERIF_TYPE option for VERIF_CASE = grid2grid")
        elif verif_case == "grid2obs":
            if verif_type in ("upper_air", "conus_sfc"):
                run_make_plots = True
            else:
                run_make_plots = False
                self.logger.error(verif_type+" is not an accepted VERIF_TYPE option for VERIF_CASE = grid2obs")
        elif verif_case == "precip":
            run_make_plots = False
            self.logger.error("Plotting is not set up for VERIF_CASE = precip at this time") 
        else:
            self.logger.error(verif_case+" is not an accepted VERIF_CASE option")
        if run_make_plots:
            self.create_plots(verif_case, verif_type)
        else:
           exit(1)
