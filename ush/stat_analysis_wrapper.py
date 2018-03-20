#!/usr/bin/env python

'''
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row
Abstract: Runs stat_analysis
History Log:  Initial version
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
import string_template_substitution as sts
from task_info import TaskInfo
from command_builder import CommandBuilder


class StatAnalysisWrapper(CommandBuilder):
    def __init__(self, p, logger):
        super(StatAnalysisWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
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
    
    def grid2grid_VSDB_format(self, valid_time, init_time):
        #read config
        model_type = self.p.getstr('config', 'MODEL_TYPE')
        stat_analysis_lookin_dir = self.p.getstr('config', 'STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.p.getstr('config', 'STAT_ANALYSIS_OUT_DIR')
        #filtering times based on if files made based on init_time or valid_time
        if init_time == -1:
            filter_time = valid_time
            self.add_env_var("FCST_VALID", valid_time)
            self.add_env_var("FCST_INIT", "")
        else:
            filter_time = init_time
            self.add_env_var("FCST_VALID", "")
            self.add_env_var("FCST_INIT", init_time)
        self.logger.info("Formatting grid2grid")
        #build -lookin directory
        self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, filter_time, "grid_stat"))
        #save output like VSDB
        date_YYYYMMDD = filter_time[0:8]
        cycle = filter_time[8:10]
        if not os.path.exists(os.path.join(stat_analysis_out_dir,
                              cycle+"Z", model_type)):
           os.makedirs(os.path.join(stat_analysis_out_dir,
                                        cycle+"Z", model_type))
        dump_row_file = os.path.join(stat_analysis_out_dir,
                                     cycle+"Z", model_type, model_type+"_"+date_YYYYMMDD+".stat")
        job = "-job filter -dump_row "+dump_row_file
        self.add_env_var("JOB", job)
        #get stat_analysis config file
        self.set_param_file(self.p.getstr('config', 'STAT_ANALYSIS_CONFIG'))
        #environment
        self.logger.debug("")
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.logger.debug("")
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.logger.debug("")
        #build command
        cmd = self.get_command()
        if cmd is None:
            print("ERROR: stat_analysis could not generate command")
            return
        self.logger.info("")
        self.build()
        self.clear()

    def grid2grid_pres_plot_format(self):
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT')
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            self.add_env_var("FCST_VALID_BEG", "")
            self.add_env_var("FCST_VALID_END", "")
            self.add_env_var("FCST_INIT_BEG", start_t)
            self.add_env_var("FCST_INIT_END", end_t)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            self.add_env_var("FCST_VALID_BEG", start_t)
            self.add_env_var("FCST_VALID_END", end_t)
            self.add_env_var("FCST_INIT_BEG", "")
            self.add_env_var("FCST_INIT_END", "")
        stat_analysis_lookin_dir = self.p.getstr('config', 'STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.p.getstr('config', 'STAT_ANALYSIS_OUT_DIR')
        cycle_list = util.getlist(self.p.getstr('config', 'CYCLE_LIST'))
        var_list = util.parse_var_list(self.p)
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = util.getlist(self.p.getstr('config', 'MODEL_LIST'))  
        self.add_env_var('INTERP', 'NEAREST')
        for cycle in cycle_list:
            self.add_env_var('CYCLE', cycle)
            for model in model_list:
                self.add_env_var('MODEL', model)
                #build -lookin directory
                self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, cycle+'Z', model))
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
                            if not os.path.exists(os.path.join(stat_analysis_out_dir,
                                                  cycle+"Z", model, region)):
                               os.makedirs(os.path.join(stat_analysis_out_dir,
                                           cycle+"Z", model, region))
                            ##dump_row_file = os.path.join(stat_analysis_out_dir,
                            ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_"+fcst_var_name+fcst_var_level+".stat")
                            dump_row_file = os.path.join(stat_analysis_out_dir,
                                                         cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat")
                            ##dump_row_file = os.path.join(stat_analysis_out_dir,
                            ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+"_obs"+obs_var_name+obs_var_level+obs_var_extra+".stat")
                            job = "-job filter -dump_row "+dump_row_file
                            self.add_env_var("JOB", job)
                            #get stat_analysis config file
                            self.set_param_file(self.p.getstr('config', 'STAT_ANALYSIS_CONFIG'))
                            #environment
                            self.logger.debug("")
                            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
                            self.logger.debug("")
                            self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
                            self.logger.debug("")
                            #build command
                            cmd = self.get_command()
                            if cmd is None:
                                print("ERROR: stat_analysis could not generate command")
                                return
                            self.logger.info("")
                            self.build()
                            self.clear() 

    def grid2grid_anom_plot_format(self):
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT')
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            self.add_env_var("FCST_VALID_BEG", "")
            self.add_env_var("FCST_VALID_END", "")
            self.add_env_var("FCST_INIT_BEG", start_t)
            self.add_env_var("FCST_INIT_END", end_t)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            self.add_env_var("FCST_VALID_BEG", start_t)
            self.add_env_var("FCST_VALID_END", end_t)
            self.add_env_var("FCST_INIT_BEG", "")
            self.add_env_var("FCST_INIT_END", "")
        stat_analysis_lookin_dir = self.p.getstr('config', 'STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.p.getstr('config', 'STAT_ANALYSIS_OUT_DIR')
        cycle_list = util.getlist(self.p.getstr('config', 'CYCLE_LIST'))
        var_list = util.parse_var_list(self.p)
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = util.getlist(self.p.getstr('config', 'MODEL_LIST'))
        for cycle in cycle_list:
            self.add_env_var('CYCLE', cycle)
            for model in model_list:
                self.add_env_var('MODEL', model)
                #build -lookin directory
                self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, cycle+'Z', model))
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
                    interp_mthd = []
                    if var_info.fcst_name == 'HGT' or var_info.obs_name == 'HGT':
                        fourier_decomp_height = self.p.getbool('config', 'FOURIER_HEIGHT_DECOMP')
                        if fourier_decomp_height:
                            wave_num_beg_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_BEG_LIST'))
                            wave_num_end_list = util.getlist(self.p.getstr('config', 'WAVE_NUM_END_LIST'))
                            if len(wave_num_beg_list) != len(wave_num_end_list):
                                print("ERROR: WAVE_NUM_BEG_LIST and WAVE_NUM_END_LIST do not have the same number of elements")
                                exit(1)
                            else:
                                interp_mthd.append("NEAREST")
                                for wn in range(len(wave_num_beg_list)):
                                    wb = wave_num_beg_list[wn]
                                    we = wave_num_end_list[wn]
                                    wave_num_pairing = "WV1_"+wb+"-"+we
                                    interp_mthd.append(wave_num_pairing)
                        else:
                                interp_mthd.append("NEAREST")
                    else:
                        interp_mthd.append("NEAREST")
                    for region in region_list:
                        self.add_env_var('REGION', region)
                        for lead in lead_list:
                            if lead < 10:
                                lead_string = '0'+str(lead)
                            else:
                                lead_string = str(lead)
                            self.add_env_var('LEAD', lead_string)
                            if not os.path.exists(os.path.join(stat_analysis_out_dir,
                                                  cycle+"Z", model, region)):
                               os.makedirs(os.path.join(stat_analysis_out_dir,
                                           cycle+"Z", model, region))
                            for im in interp_mthd:
                                self.add_env_var('INTERP', im)    
                                if im == "NEAREST":                             
                                    ##dump_row_file = os.path.join(stat_analysis_out_dir,
                                    ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_"+fcst_var_name+fcst_var_level+".stat")
                                    dump_row_file = os.path.join(stat_analysis_out_dir,
                                                                 cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat")
                                    ##dump_row_file = os.path.join(stat_analysis_out_dir,
                                    ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+"_obs"+obs_var_name+obs_var_level+obs_var_extra+".stat")
                                else: 
                                    ##dump_row_file = os.path.join(stat_analysis_out_dir,
                                    ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_"+fcst_var_name+fcst_var_level+".stat")
                                    dump_row_file = os.path.join(stat_analysis_out_dir,
                                                                 cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+"_"+im+".stat")
                                    ##dump_row_file = os.path.join(stat_analysis_out_dir,
                                    ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+"_obs"+obs_var_name+obs_var_level+obs_var_extra+"_"+im+".stat")
                                job = "-job filter -dump_row "+dump_row_file
                                self.add_env_var("JOB", job)
                                #get stat_analysis config file
                                self.set_param_file(self.p.getstr('config', 'STAT_ANALYSIS_CONFIG'))
                                #environment
                                self.logger.debug("")
                                self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
                                self.logger.debug("")
                                self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
                                self.logger.debug("")
                                #build command
                                cmd = self.get_command()
                                if cmd is None:
                                    print("ERROR: stat_analysis could not generate command")
                                    return
                                self.logger.info("")
                                self.build()
                                self.clear()
 
    def grid2grid_sfc_plot_format(self):
        #read config
        use_init = self.p.getbool('config', 'LOOP_BY_INIT')
        if use_init:
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            self.add_env_var("FCST_VALID_BEG", "")
            self.add_env_var("FCST_VALID_END", "")
            self.add_env_var("FCST_INIT_BEG", start_t)
            self.add_env_var("FCST_INIT_END", end_t)
        else:
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            self.add_env_var("FCST_VALID_BEG", start_t)
            self.add_env_var("FCST_VALID_END", end_t)
            self.add_env_var("FCST_INIT_BEG", "")
            self.add_env_var("FCST_INIT_END", "")
        stat_analysis_lookin_dir = self.p.getstr('config', 'STAT_ANALYSIS_LOOKIN_DIR')
        stat_analysis_out_dir = self.p.getstr('config', 'STAT_ANALYSIS_OUT_DIR')
        cycle_list = util.getlist(self.p.getstr('config', 'CYCLE_LIST'))
        var_list = util.parse_var_list(self.p)
        region_list = util.getlist(self.p.getstr('config', 'REGION_LIST'))
        lead_list = util.getlistint(self.p.getstr('config', 'LEAD_LIST'))
        model_list = util.getlist(self.p.getstr('config', 'MODEL_LIST'))
        self.add_env_var('INTERP', 'NEAREST')
        for cycle in cycle_list:
            self.add_env_var('CYCLE', cycle)
            for model in model_list:
                self.add_env_var('MODEL', model)
                #build -lookin directory
                self.set_lookin_dir(os.path.join(stat_analysis_lookin_dir, cycle+'Z', model))
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
                            if not os.path.exists(os.path.join(stat_analysis_out_dir,
                                                  cycle+"Z", model, region)):
                               os.makedirs(os.path.join(stat_analysis_out_dir,
                                           cycle+"Z", model, region))
                            ##dump_row_file = os.path.join(stat_analysis_out_dir,
                            ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_"+fcst_var_name+fcst_var_level+".stat")
                            dump_row_file = os.path.join(stat_analysis_out_dir,
                                                         cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+"_obs"+obs_var_name+obs_var_level+".stat")
                            ##dump_row_file = os.path.join(stat_analysis_out_dir,
                            ##                             cycle+"Z", model, region, model+"_f"+lead_string+"_fcst"+fcst_var_name+fcst_var_level+fcst_var_extra+"_obs"+obs_var_name+obs_var_level+obs_var_extra+".stat")
                            job = "-job filter -dump_row "+dump_row_file
                            self.add_env_var("JOB", job)
                            #get stat_analysis config file
                            self.set_param_file(self.p.getstr('config', 'STAT_ANALYSIS_CONFIG'))
                            #environment
                            self.logger.debug("")
                            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
                            self.logger.debug("")
                            self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
                            self.logger.debug("")
                            #build command
                            cmd = self.get_command()
                            if cmd is None:
                                print("ERROR: stat_analysis could not generate command")
                                return
                            self.logger.info("")
                            self.build()
                            self.clear()

########################################################################
########################################################################
########################################################################
    def run_all_times(self):
        self.logger.info("RUNNING STAT_ANALYSIS FOR PLOTTING FORMAT")
        verif_type = self.p.getstr('config', 'VERIF_TYPE')
        verif_case = self.p.getstr('config', 'VERIF_CASE')
        if verif_type == 'grid2grid':
            if verif_case == 'pres':
                 self.logger.info("Formatting for plotting for grid2grid-pres")
                 self.grid2grid_pres_plot_format()
            elif verif_case == 'anom':
                 self.logger.info("Formatting for plotting for grid2grid-anom")
                 self.grid2grid_anom_plot_format()
            elif verif_case == 'sfc':
                 self.logger.info("Formatting for plotting for grid2grid-sfc")
                 self.grid2grid_sfc_plot_format()
            else:
                 self.logger.error("Not a valid VERIF_CASE option for grid2grid")
                 exit(1)
        elif verif_type == 'grid2obs':
            if verif_case == 'sfc':
                 self.logger.info("Formatting for plotting for grid2obs-sfc")
            elif verif_case == 'upper_air':
                 self.logger.info("Formatting for plottting for grid2grid-upper_air")
            else:
                 self.logger.error("Not a valid VERIF_CASE option for grid2obs")
                 exit(1)
        elif verif_type == 'precip':
            self.logger.info("Formatting for plotting for precip")
        else:
            self.logger.error("Not a valid VERIF_TYPE option")
            exit(1)

    def run_at_time(self, init_time, valid_time):
        self.logger.info("RUNNING STAT_ANALYSIS FOR VSDB FORMAT")
        verif_type = self.p.getstr('config', 'VERIF_TYPE')
        verif_case = self.p.getstr('config', 'VERIF_CASE')
        #parse betwen VERIF_TYPE for stat_analysis specifications
        if verif_type == 'grid2grid':
             self.logger.info("Formatting in VSDB style for grid2grid")
             self.grid2grid_VSDB_format(valid_time, init_time)
        elif verif_type == 'grid2obs':
            self.logger.info("Formatting in VSDB style for grid2obs")
        elif verif_type == 'precip':
            self.logger.info("Formatting in VSDB style for precip")
        else:
            self.logger.error("Not a valid VERIF_TYPE option for formatting")
            exit(1)
