#!/usr/bin/env python

'''
Program Name: make_plots_wrapper.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make plots
History Log:  Third version
Usage: make_plots_wrapper.py 
Parameters: None
Input Files: MET .stat files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
import time
import calendar
from command_builder import CommandBuilder

class MakePlotsWrapper(CommandBuilder):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_path = 'python'
        self.app_name = 'make_plots'

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

    def parse_vars_with_level_thresh_list(self):
        """! Parse metplus_final.conf for variable information,
             collecting the variable level information as a list
             
             Args:
                
             Returns:
                 var_info - list of objects containing variable
                            information
        """
        var_info = []
        all_conf = self.config.keys('config')
        fcst_indices = []
        regex = re.compile("FCST_VAR(\d+)_NAME")
        for conf in all_conf:
           result = regex.match(conf)
           if result is not None:
              fcst_indices.append(result.group(1))
        for n in fcst_indices:
            if self.config.has_option('config', "FCST_VAR"+n+"_NAME"):
                fcst_name = self.config.getstr('config', "FCST_VAR"+n+"_NAME")
                if self.config.has_option('config', "FCST_VAR"+n+"_LEVELS"):
                    fcst_levels = util.getlist(self.config.getstr('config', "FCST_VAR"+n+"_LEVELS"))
                else:
                    self.logger.error("FCST_VAR"+n+"_LEVELS not defined")
                    exit(1)
                if self.config.has_option('config', "FCST_VAR"+n+"_OPTIONS"):
                    fcst_extra = self.config.getraw('config', "FCST_VAR"+n+"_OPTIONS")
                else:
                    fcst_extra = ""
                if self.config.has_option('config', "FCST_VAR"+n+"_THRESH"):
                    fcst_thresh = util.getlist(self.config.getstr('config', "FCST_VAR"+n+"_THRESH"))
                else:
                    fcst_thresh = ""
                if self.config.has_option('config', "OBS_VAR"+n+"_NAME"):
                    obs_name = self.config.getstr('config', "OBS_VAR"+n+"_NAME")
                else:
                    obs_name = fcst_name
                if self.config.has_option('config', "OBS_VAR"+n+"_LEVELS"):
                    obs_levels = util.getlist(self.config.getstr('config', "OBS_VAR"+n+"_LEVELS"))
                    if len(fcst_levels) != len(obs_levels):
                        self.logger.error("FCST_VAR"+n+"_LEVELS and OBS_VAR"+n+"_LEVELS do not have the same number of elements")
                        exit(1)
                else:
                    obs_levels = fcst_levels
                if self.config.has_option('config', "OBS_VAR"+n+"_OPTIONS"):
                    obs_extra = self.config.getraw('config', "OBS_VAR"+n+"_OPTIONS")
                else:
                    obs_extra = ""
                if self.config.has_option('config', "OBS_VAR"+n+"_THRESH"):
                    obs_thresh = util.getlist(self.config.getstr('config', "OBS_VAR"+n+"_THRESH"))
                    if len(fcst_thresh) != len(obs_thresh):
                        self.logger.error("FCST_VAR"+n+"_THRESH and OBS_VAR"+n+"_THRESH do not have the same number of elements")
                        exit(1)
                else:
                    obs_thresh = fcst_thresh
            else:
                self.logger.error("FCST_VAR"+n+"_NAME not defined")
                exit(1)
            fo = {}
            fo['fcst_name'] = fcst_name
            fo['obs_name'] = obs_name
            fo['fcst_extra'] = fcst_extra
            fo['obs_extra'] = obs_extra
            fo['fcst_thresh'] = fcst_thresh
            fo['obs_thresh'] = obs_thresh
            fo['fcst_level'] = fcst_levels
            fo['obs_level'] = obs_levels
            fo['index'] = n
            var_info.append(fo)
        return var_info


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
                run_fourier = self.config.getbool('config', "VAR"+n+"_FOURIER_DECOMP", False)
                fourier_wave_num_pairs = util.getlist(self.config.getstr('config', "VAR"+n+"_WAVE_NUM_LIST", ""))
                if run_fourier == False:
                    fourier_wave_num_pairs = ""
                fd_info = self.FourierDecompInfo()
                fd_info.run_fourier = run_fourier
                fd_info.wave_num_pairings = fourier_wave_num_pairs
                fourier_decom_list.append(fd_info)
        return fourier_decom_list
    
    def parse_model_list(self):
        """! Parse metplus_final.conf for model information
             
             Args:
                
             Returns:
                 model_list - list of objects containing
                              model information
        """
        model_name_list = []
        model_plot_name_list = []
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
                model_name_list.append(model_name)
                model_plot_name_list.append(model_plot_name)
        return ' '.join(model_name_list), ' '.join(model_plot_name_list)
 
    def create_plots_grid2grid_pres(self, fcst_var_level_list, obs_var_level_list,
                                    fcst_var_thresh_list, obs_var_thresh_list,
                                    lead_list, plotting_scripts_dir):
        """! Create plots for the grid-to-grid verification for variables
             on pressure levels. Runs plotting scripts: plot_time_series.py,
             plot_lead_mean.py, plot_date_by_level.py, plot_lead_by_level.py
             
             Args:
                 fcst_var_level_list - list of forecst variable level
                                       information
                 obs_var_level_list -  list of observation variable level
                                       information
                 fcst_var_thresh_list - list of forecast variable threshold
                                        information
                 obs_var_thresh_list - list of observation variable threshold
                                        information
                 lead_list - list of forecast hour leads
                 plotting_scripts_dir - directory to put images and data
                
             Returns:
        """
        self.add_env_var("LEAD_LIST", ', '.join(lead_list))
        self.add_env_var('FCST_VAR_LEVEL_LIST', ' '.join(fcst_var_level_list))
        self.add_env_var('OBS_VAR_LEVEL_LIST', ' '.join(obs_var_level_list))
        os.environ["LEAD_LIST"] = ', '.join(lead_list)
        os.environ['FCST_VAR_LEVEL_LIST'] = ' '.join(fcst_var_level_list)
        os.environ['OBS_VAR_LEVEL_LIST'] = ' '.join(obs_var_level_list)
        #time series plot
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
                os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                    os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_time_series.py"))
                    self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_time_series.py")+" with...")
                    self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                    self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                    self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                    self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                    self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                    self.logger.debug("INTERP: "+os.environ['INTERP'])
                    self.logger.debug("REGION: "+os.environ["REGION"])
                    self.logger.debug("LEAD: "+lead)
                    self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                    self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                    self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                    self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                    self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                    self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
        #lead mean plot
        for vl in range(len(fcst_var_level_list)):
            self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
            self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
            os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
            os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_mean.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_mean.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
        #date by variable levels
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_date_by_level.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_date_by_level.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("FCST VAR LEVELS: "+os.environ['FCST_VAR_LEVEL_LIST'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("OBS VAR LEVELS: "+os.environ['OBS_VAR_LEVEL_LIST'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD: "+os.environ["LEAD"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
        #lead by variable levels
        for vt in range(len(fcst_var_thresh_list)):
            self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
            self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
            os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
            os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
            self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_by_level.py"))
            self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_by_level.py")+" with...")
            self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
            self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
            self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
            self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
            self.logger.debug("FCST VAR LEVELS: "+os.environ['FCST_VAR_LEVEL_LIST'])
            self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
            self.logger.debug("OBS VAR LEVELS: "+os.environ['OBS_VAR_LEVEL_LIST'])
            self.logger.debug("INTERP: "+os.environ['INTERP'])
            self.logger.debug("REGION: "+os.environ["REGION"])
            self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
            self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
            self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
            self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
            self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
            self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                return
            self.build()
            self.clear()

    def create_plots_grid2grid_anom(self, fcst_var_level_list, obs_var_level_list,
                                    fcst_var_thresh_list, obs_var_thresh_list,
                                    lead_list, plotting_scripts_dir):
        """! Create plots for the grid-to-grid verification for variables
             on pressure levels with anomaly data. Runs plotting scripts: 
             plot_time_series.py, plot_lead_mean.py, plot_lead_by_date.py
             
             Args:
                 fcst_var_level_list - list of forecst variable level
                                       information
                 obs_var_level_list -  list of observation variable level
                                       information
                 fcst_var_thresh_list - list of forecast variable threshold
                                        information
                 obs_var_thresh_list - list of observation variable threshold
                                        information
                 lead_list - list of forecast hour leads
                 plotting_scripts_dir - directory to put images and data
                
             Returns:
        """
        self.add_env_var("LEAD_LIST", ', '.join(lead_list))
        os.environ['LEAD_LIST'] = ', '.join(lead_list)
        #time series plot
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
                os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                    os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_time_series.py"))
                    self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_time_series.py")+" with...")
                    self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                    self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                    self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                    self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                    self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                    self.logger.debug("INTERP: "+os.environ['INTERP'])
                    self.logger.debug("REGION: "+os.environ["REGION"])
                    self.logger.debug("LEAD: "+lead)
                    self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                    self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                    self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                    self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                    self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()

        #lead mean plot and lead by date plot
        for vl in range(len(fcst_var_level_list)):
            self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
            self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
            os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
            os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_mean.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_mean.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_by_date.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_by_date.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
 
    def create_plots_grid2grid_sfc(self, fcst_var_level_list, obs_var_level_list,
                                   fcst_var_thresh_list, obs_var_thresh_list,
                                   lead_list, plotting_scripts_dir):
        """! Create plots for the grid-to-grid verification for variables
             on single level. Runs plotting scripts: plot_time_series.py,
             plot_lead_mean.py
             
             Args:
                 fcst_var_level_list - list of forecst variable level
                                       information
                 obs_var_level_list -  list of observation variable level
                                       information
                 fcst_var_thresh_list - list of forecast variable threshold
                                        information
                 obs_var_thresh_list - list of observation variable threshold
                                        information
                 lead_list - list of forecast hour leads
                 plotting_scripts_dir - directory to put images and data
                
             Returns:
        """
        self.add_env_var("LEAD_LIST", ', '.join(lead_list))
        os.environ["LEAD_LIST"] = ', '.join(lead_list)
        #time series plot
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
                os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                    os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_time_series.py"))
                    self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_time_series.py")+" with...")
                    self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                    self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                    self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                    self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                    self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                    self.logger.debug("INTERP: "+os.environ['INTERP'])
                    self.logger.debug("REGION: "+os.environ["REGION"])
                    self.logger.debug("LEAD: "+lead)
                    self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                    self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                    self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                    self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                    self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                    self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])

                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
        #lead mean plot
        for vl in range(len(fcst_var_level_list)):
            self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
            self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
            os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
            os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_mean.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_mean.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()


    def create_plots_grid2obs_upper_air(self, fcst_var_level_list, obs_var_level_list,
                                        fcst_var_thresh_list, obs_var_thresh_list,
                                        lead_list, plotting_scripts_dir):
        """! Create plots for the grid-to-observations verification for variables
             on pressure levels. Runs plotting scripts: plot_time_series.py,
             plot_lead_mean.py, plot_stat_by_level.py, plot_lead_by_level.py
             
             Args:
                 fcst_var_level_list - list of forecst variable level
                                       information 
                 obs_var_level_list -  list of observation variable level
                                       information
                 fcst_var_thresh_list - list of forecast variable threshold
                                        information
                 obs_var_thresh_list - list of observation variable threshold
                                        information
                 lead_list - list of forecast hour leads
                 plotting_scripts_dir - directory to put images and data
                
             Returns:
        """
        self.add_env_var("LEAD_LIST", ', '.join(lead_list))
        self.add_env_var('FCST_VAR_LEVEL_LIST', ' '.join(fcst_var_level_list))
        self.add_env_var('OBS_VAR_LEVEL_LIST', ' '.join(obs_var_level_list))
        os.environ["LEAD_LIST"] = ', '.join(lead_list)
        os.environ['FCST_VAR_LEVEL_LIST'] = ' '.join(fcst_var_level_list)
        os.environ['OBS_VAR_LEVEL_LIST'] = ' '.join(obs_var_level_list)
        #time series plot
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
                os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                    os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_time_series.py"))
                    self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_time_series.py")+" with...")
                    self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                    self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                    self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                    self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                    self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                    self.logger.debug("INTERP: "+os.environ['INTERP'])
                    self.logger.debug("REGION: "+os.environ["REGION"])
                    self.logger.debug("LEAD: "+lead)
                    self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                    self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                    self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                    self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                    self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                    self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
        #stat by level plot
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_stat_by_level.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_stat_by_level.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("FCST VAR LEVELS: "+os.environ['FCST_VAR_LEVEL_LIST'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("OBS VAR LEVELS: "+os.environ['OBS_VAR_LEVEL_LIST'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD: "+os.environ["LEAD"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
        #lead mean plot
        for vl in range(len(fcst_var_level_list)):
            self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
            self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
            os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
            os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_mean.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_mean.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
        #lead by variable levels
        for vt in range(len(fcst_var_thresh_list)):
            self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
            self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
            os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
            os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
            self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_by_level.py"))
            self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_by_level.py")+" with...")
            self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
            self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
            self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
            self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
            self.logger.debug("FCST VAR LEVELS: "+os.environ['FCST_VAR_LEVEL_LIST'])
            self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
            self.logger.debug("OBS VAR LEVELS: "+os.environ['OBS_VAR_LEVEL_LIST'])
            self.logger.debug("INTERP: "+os.environ['INTERP'])
            self.logger.debug("REGION: "+os.environ["REGION"])
            self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
            self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
            self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
            self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
            self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
            self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                return
            self.build()
            self.clear()
 
    def create_plots_grid2obs_conus_sfc(self, fcst_var_level_list, obs_var_level_list,
                                        fcst_var_thresh_list, obs_var_thresh_list,
                                        lead_list, plotting_scripts_dir):
        """! Create plots for the grid-to-observation verification for variables
             on single level. Runs plotting scripts: plot_time_series.py,
             plot_lead_mean.py
             
             Args:
                 fcst_var_level_list - list of forecst variable level
                                       information 
                 obs_var_level_list -  list of observation variable level
                                       information
                 fcst_var_thresh_list - list of forecast variable threshold
                                        information
                 obs_var_thresh_list - list of observation variable threshold
                                        information
                 lead_list - list of forecast hour leads
                 plotting_scripts_dir - directory to put images and data
                
             Returns:
        """
        self.add_env_var("LEAD_LIST", ', '.join(lead_list))
        os.environ["LEAD_LIST"] = ', '.join(lead_list)
        #time series plot
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
                os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                    os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_time_series.py"))
                    self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_time_series.py")+" with...")
                    self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                    self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                    self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                    self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                    self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                    self.logger.debug("INTERP: "+os.environ['INTERP'])
                    self.logger.debug("REGION: "+os.environ["REGION"])
                    self.logger.debug("LEAD: "+lead)
                    self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                    self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                    self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                    self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                    self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                    self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()

        #lead mean plot
        for vl in range(len(fcst_var_level_list)):
            self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
            self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
            os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl]
            os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
            for vt in range(len(fcst_var_thresh_list)):
                self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_lead_mean.py"))
                self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_lead_mean.py")+" with...")
                self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                self.logger.debug("INTERP: "+os.environ['INTERP'])
                self.logger.debug("REGION: "+os.environ["REGION"])
                self.logger.debug("LEAD_LIST: "+os.environ["LEAD_LIST"])
                self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                cmd = self.get_command()
                if cmd is None:
                    self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                    return
                self.build()
                self.clear()
 
    def create_plots_precip(self, fcst_var_level_list, obs_var_level_list,
                            fcst_var_thresh_list, obs_var_thresh_list,
                            lead_list, plotting_scripts_dir):
        for lead in lead_list:
            self.add_env_var('LEAD', lead)
            os.environ['LEAD'] = lead
            for vl in range(len(fcst_var_level_list)):
                self.add_env_var('FCST_VAR_LEVEL', fcst_var_level_list[vl])
                self.add_env_var('OBS_VAR_LEVEL',obs_var_level_list[vl])
                os.environ['FCST_VAR_LEVEL'] = fcst_var_level_list[vl] 
                os.environ['OBS_VAR_LEVEL'] = obs_var_level_list[vl]
                for vt in range(len(fcst_var_thresh_list)):
                    self.add_env_var('FCST_VAR_THRESH', fcst_var_thresh_list[vt])
                    self.add_env_var('OBS_VAR_THRESH', obs_var_thresh_list[vt])
                    os.environ['FCST_VAR_THRESH'] = fcst_var_thresh_list[vt]
                    os.environ['OBS_VAR_THRESH'] = obs_var_thresh_list[vt]
                    self.set_plotting_script(os.path.join(plotting_scripts_dir, "plot_time_series.py"))
                    self.logger.debug("Running "+os.path.join(plotting_scripts_dir, "plot_time_series.py")+" with...")
                    self.logger.debug("DATES: "+os.environ['PLOT_TIME']+" "+os.environ['START_DATE_YYYYmmdd']+" "+os.environ['END_DATE_YYYYmmdd'])
                    self.logger.debug("VALID TIME INFO: "+os.environ['VALID_TIME_INFO'])
                    self.logger.debug("INIT TIME INFO: "+os.environ['INIT_TIME_INFO'])
                    self.logger.debug("FCST VAR: "+os.environ['FCST_VAR_NAME']+" "+fcst_var_level_list[vl]+" "+fcst_var_thresh_list[vt]+" "+os.environ['FCST_VAR_EXTRA'])
                    self.logger.debug("OBS VAR: "+os.environ['OBS_VAR_NAME']+" "+obs_var_level_list[vl]+" "+obs_var_thresh_list[vt]+" "+os.environ['OBS_VAR_EXTRA'])
                    self.logger.debug("INTERP: "+os.environ['INTERP'])
                    self.logger.debug("REGION: "+os.environ["REGION"])
                    self.logger.debug("LEAD: "+lead)
                    self.logger.debug("EVENT_EQUALIZATION: "+os.environ['EVENT_EQUALIZATION'])
                    self.logger.debug("CI_METHOD: "+os.environ['CI_METHOD'])
                    self.logger.debug("VERIF_GRID: "+os.environ['VERIF_GRID'])
                    self.logger.debug("MODEL_NAME_LIST: "+os.environ['MODEL_NAME_LIST'])
                    self.logger.debug("MODEL_PLOT_NAME_LIST: "+os.environ['MODEL_PLOT_NAME_LIST'])
                    self.logger.debug("PLOT_STATS_LIST: "+os.environ['PLOT_STATS_LIST'])
                    cmd = self.get_command()
                    if cmd is None:
                        self.logger.error("ERROR: make_plots could not generate command for "+self.plotting_script)
                        return
                    self.build()
                    self.clear()
                    exit()
 
    def create_plots(self, verif_case, verif_type):
        """! Read in metplus_final.conf variables and call function
             for the specific verification plots to run
            
             Args:
                 verif_case - string of the verification case to make
                              plots for
                 verif_type - string of the verification type to make
                              plots for
               
             Returns:
        """
        self.logger.info("Running plots for VERIF_CASE = "+verif_case+", VERIF_TYPE = "+verif_type)
        #read config
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
        stat_files_input_dir = self.config.getdir('STAT_FILES_INPUT_DIR')
        plotting_out_dir = self.config.getdir('PLOTTING_OUTPUT_DIR')
        plotting_scripts_dir = self.config.getdir('PLOTTING_SCRIPTS_DIR')
        plot_stats_list = self.config.getstr('config', 'PLOT_STATS_LIST')
        ci_method = self.config.getstr('config', 'CI_METHOD')
        verif_grid = self.config.getstr('config', 'VERIF_GRID')
        event_equalization = self.config.getstr('config', 'EVENT_EQUALIZATION', "True")
        var_list = self.parse_vars_with_level_thresh_list()
        fourier_decom_list = self.parse_var_fourier_decomp()
        region_list = util.getlist(self.config.getstr('config', 'REGION_LIST'))
        lead_list = util.getlist(self.config.getstr('config', 'LEAD_LIST'))
        model_name_str_list, model_plot_name_str_list = self.parse_model_list()
        logging_filename = self.config.getstr('config', 'LOG_METPLUS')
        logging_level = self.config.getstr('config', 'LOG_LEVEL')
        met_base = self.config.getstr('dir', 'MET_BASE')
        #set envir vars based on config
        self.add_env_var("PLOT_TIME", plot_time)
        os.environ["PLOT_TIME"] = plot_time
        if plot_time == 'valid':
            self.add_env_var('START_DATE_YYYYmmdd', valid_beg_YYYYmmdd)
            self.add_env_var('END_DATE_YYYYmmdd', valid_end_YYYYmmdd)
            os.environ['START_DATE_YYYYmmdd'] = valid_beg_YYYYmmdd
            os.environ['END_DATE_YYYYmmdd'] = valid_end_YYYYmmdd
        elif plot_time == 'init':
            self.add_env_var('START_DATE_YYYYmmdd', init_beg_YYYYmmdd)
            self.add_env_var('END_DATE_YYYYmmdd', init_end_YYYYmmdd)
            os.environ['START_DATE_YYYYmmdd'] = init_beg_YYYYmmdd
            os.environ['END_DATE_YYYYmmdd'] = init_end_YYYYmmdd
        else:
            self.logger.error("Invalid entry for PLOT_TIME, use 'valid' or 'init'")
            exit(1)
        self.add_env_var('STAT_FILES_INPUT_DIR', stat_files_input_dir)
        self.add_env_var('PLOTTING_OUT_DIR', plotting_out_dir)
        self.add_env_var('PLOT_STATS_LIST', plot_stats_list)
        self.add_env_var('MODEL_NAME_LIST', model_name_str_list)
        self.add_env_var('MODEL_PLOT_NAME_LIST', model_plot_name_str_list)
        self.add_env_var('CI_METHOD', ci_method)
        self.add_env_var('VERIF_GRID', verif_grid)
        self.add_env_var('EVENT_EQUALIZATION', event_equalization)
        self.add_env_var('LOGGING_FILENAME', logging_filename)
        self.add_env_var('LOGGING_LEVEL', logging_level)
        os.environ['STAT_FILES_INPUT_DIR'] = stat_files_input_dir
        os.environ['PLOTTING_OUT_DIR'] = plotting_out_dir
        os.environ['PLOT_STATS_LIST'] = plot_stats_list
        os.environ['MODEL_NAME_LIST'] =  model_name_str_list
        os.environ['MODEL_PLOT_NAME_LIST'] = model_plot_name_str_list
        os.environ['CI_METHOD'] = ci_method
        os.environ['VERIF_GRID'] = verif_grid
        os.environ['EVENT_EQUALIZATION'] = event_equalization
        os.environ['LOGGING_FILENAME'] = logging_filename
        os.environ['LOGGING_LEVEL'] = logging_level
        plotting_out_dir_full = os.path.join(plotting_out_dir, verif_case, verif_type)
        if os.path.exists(plotting_out_dir_full):
            self.logger.info(plotting_out_dir_full+" exists, removing")
            util.rmtree(plotting_out_dir_full)
        util.mkdir_p(os.path.join(plotting_out_dir_full, "imgs"))
        util.mkdir_p(os.path.join(plotting_out_dir_full, "data"))
        self.add_env_var('PLOTTING_OUT_DIR_FULL', plotting_out_dir_full)
        os.environ['PLOTTING_OUT_DIR_FULL'] = plotting_out_dir_full
        p = subprocess.Popen(["stat_analysis", "--version"], stdout=subprocess.PIPE)
        out, err = p.communicate()
        for line in out.split('\n'):
            if 'MET Version:' in line:
                met_verison_line = line
        met_version_str = met_verison_line.partition('MET Version:')[2].split('V')[1]
        met_version = float(met_version_str.rpartition('.')[0])
        self.add_env_var('MET_VERSION', str(met_version))
        os.environ['MET_VERSION'] = str(met_version)
        if met_version < 6.0:
             self.logger.exit("Please run with MET version >= 6.0")
             exit(1)
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
            os.environ['VALID_TIME_INFO'] = valid_init_time_pair.valid
            os.environ['INIT_TIME_INFO'] = valid_init_time_pair.init
            #loop through variable information
            for var_info in var_list:
                self.add_env_var('FCST_VAR_NAME', var_info['fcst_name'])
                self.add_env_var('OBS_VAR_NAME', var_info['obs_name'])
                os.environ['FCST_VAR_NAME'] = var_info['fcst_name']
                os.environ['OBS_VAR_NAME'] = var_info['obs_name']
                fcst_var_level_list = var_info['fcst_level']
                obs_var_level_list = var_info['obs_level']
                if len(var_info['fcst_extra']) == 0:
                    self.add_env_var('FCST_VAR_EXTRA', "None")
                    os.environ['FCST_VAR_EXTRA'] = 'None'
                else:
                    self.add_env_var('FCST_VAR_EXTRA', var_info['fcst_extra'])
                    os.environ['FCST_VAR_EXTRA'] = var_info['fcst_extra']
                if len(var_info['obs_extra']) == 0:
                    self.add_env_var('OBS_VAR_EXTRA', "None")
                    os.environ['OBS_VAR_EXTRA'] = 'None'
                else:
                    self.add_env_var('OBS_VAR_EXTRA', var_info['obs_extra'])
                    os.environ['OBS_VAR_EXTRA'] = var_info['obs_extra']
                if len(var_info['fcst_thresh']) == 0 or len(var_info['obs_thresh']) == 0:
                    fcst_var_thresh_list = [ "None" ]
                    obs_var_thresh_list = [ "None" ]
                else:
                    fcst_var_thresh_list = var_info['fcst_thresh']
                    obs_var_thresh_list = var_info['obs_thresh']
                #check for fourier decompositon for variable, add to interp list
                interp_list = util.getlist(self.config.getstr('config', 'INTERP', ""))
                var_fourier_decomp_info = fourier_decom_list[var_list.index(var_info)]
                if var_fourier_decomp_info.run_fourier:
                    for pair in var_fourier_decomp_info.wave_num_pairings:
                        interp_list.append("WV1_"+pair)
                #loop through interpolation information
                for interp in interp_list:
                    self.add_env_var('INTERP', interp)
                    os.environ['INTERP'] = interp
                    #loop through region information
                    for region in region_list:
                        self.add_env_var('REGION', region)
                        os.environ['REGION'] = region
                        #call specific plot definitions to make plots
                        if verif_case == "grid2grid" and verif_type in "pres":
                            self.create_plots_grid2grid_pres(fcst_var_level_list, obs_var_level_list,
                                                             fcst_var_thresh_list, obs_var_thresh_list,
                                                             lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2grid" and verif_type in "anom":
                            self.create_plots_grid2grid_anom(fcst_var_level_list, obs_var_level_list,
                                                             fcst_var_thresh_list, obs_var_thresh_list,
                                                             lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2grid" and verif_type in "sfc":
                            self.create_plots_grid2grid_sfc(fcst_var_level_list, obs_var_level_list,
                                                            fcst_var_thresh_list, obs_var_thresh_list,
                                                            lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2obs" and verif_type in "upper_air":
                            self.create_plots_grid2obs_upper_air(fcst_var_level_list, obs_var_level_list,
                                                                 fcst_var_thresh_list, obs_var_thresh_list,
                                                                 lead_list, plotting_scripts_dir)
                        elif verif_case == "grid2obs" and verif_type in "conus_sfc":
                            self.create_plots_grid2obs_conus_sfc(fcst_var_level_list, obs_var_level_list,
                                                                 fcst_var_thresh_list, obs_var_thresh_list,
                                                                 lead_list, plotting_scripts_dir)
                        elif verif_case == "precip":
                            self.create_plots_precip(fcst_var_level_list, obs_var_level_list,
                                                     fcst_var_thresh_list, obs_var_thresh_list,
                                                     lead_list, plotting_scripts_dir)

    def run_all_times(self):
        verif_case = self.config.getstr('config', 'VERIF_CASE')
        verif_type = self.config.getstr('config', 'VERIF_TYPE')
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
