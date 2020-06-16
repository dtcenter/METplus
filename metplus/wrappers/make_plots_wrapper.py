#!/usr/bin/env python

'''
Program Name: make_plots_wrapper.py
Contact(s): Mallory Row
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times to make plots
History Log:  Fourth version
Usage: make_plots_wrapper.py 
Parameters: None
Input Files: MET .stat files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

import logging
import os
import copy
import re
import subprocess
import datetime
import itertools

from ..util import metplus_check_python_version
from ..util import met_util as util
from . import CommandBuilder

class MakePlotsWrapper(CommandBuilder):
    """! Wrapper to used to filter make plots from MET data
    """
    accepted_verif_lists = {
        'grid2grid': {
            'pres': ['plot_time_series.py',
                     'plot_lead_average.py',
                     'plot_date_by_level.py',
                     'plot_lead_by_level.py'],
            'anom': ['plot_time_series.py',
                     'plot_lead_average.py',
                     'plot_lead_by_date.py'],
            'sfc': ['plot_time_series.py',
                    'plot_lead_average.py'],
        },
        'grid2obs': {
            'upper_air': ['plot_time_series.py',
                          'plot_lead_average.py',
                          'plot_stat_by_level.py',
                          'plot_lead_by_level.py'],
            'conus_sfc': ['plot_time_series.py',
                          'plot_lead_average.py'],
        },
        # precip uses the same scripts for any verif case, so this value
        # is a list instead of a dictionary
        'precip': ['plot_time_series.py',
                   'plot_lead_average.py',
                   'plot_threshold_average.py',
                   'plot_threshold_by_lead.py'],
    }

    add_from_c_dict_list = [
        'VERIF_CASE', 'VERIF_TYPE', 'INPUT_BASE_DIR', 'OUTPUT_BASE_DIR',
        'SCRIPTS_BASE_DIR', 'DATE_TYPE', 'VALID_BEG', 'VALID_END',
        'INIT_BEG', 'INIT_END', 'AVERAGE_METHOD', 'CI_METHOD',
        'VERIF_GRID', 'EVENT_EQUALIZATION', 'LOG_METPLUS', 'LOG_LEVEL'
    ]

    def __init__(self, config, logger):
        self.app_path = 'python'
        self.app_name = 'make_plots'
        super().__init__(config, logger)

    def get_command(self):

        if not self.plotting_script:
            self.log_error("No plotting script specified")
            return None

        cmd = f"{self.app_path} {self.plotting_script}"

        return cmd

    def create_c_dict(self):
        """! Create a data structure (dictionary) that contains all the
             values set in the configuration files that are common for 
             make_plots_wrapper.py.
        
             Args:
 
             Returns:
                 c_dict  - a dictionary containing the settings in the
                           configuration files unique to the wrapper
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config', 'LOG_MAKE_PLOTS_VERBOSITY',
                               c_dict['VERBOSITY'])
        )
        c_dict['LOOP_ORDER'] = self.config.getstr('config', 'LOOP_ORDER')
        c_dict['PROCESS_LIST'] = self.config.getstr('config', 'PROCESS_LIST')
        c_dict['INPUT_BASE_DIR'] = self.config.getdir('MAKE_PLOTS_INPUT_DIR')
        c_dict['OUTPUT_BASE_DIR'] = self.config.getdir('MAKE_PLOTS_OUTPUT_DIR')
        c_dict['SCRIPTS_BASE_DIR'] = self.config.getdir('MAKE_PLOTS_SCRIPTS_DIR')
        c_dict['DATE_TYPE'] = self.config.getstr('config', 'DATE_TYPE')
        c_dict['VALID_BEG'] = self.config.getstr('config', 'VALID_BEG', '')
        c_dict['VALID_END'] = self.config.getstr('config', 'VALID_END', '')
        c_dict['INIT_BEG'] = self.config.getstr('config', 'INIT_BEG', '')
        c_dict['INIT_END'] = self.config.getstr('config', 'INIT_END', '')
        c_dict['GROUP_LIST_ITEMS'] = util.getlist(
            self.config.getstr('config', 'GROUP_LIST_ITEMS')
        )
        c_dict['LOOP_LIST_ITEMS'] = util.getlist(
            self.config.getstr('config', 'LOOP_LIST_ITEMS')
        )
        c_dict['VAR_LIST'] = util.parse_var_list(self.config)
        c_dict['MODEL_LIST'] = util.getlist(
            self.config.getstr('config', 'MODEL_LIST', '')
        )
        c_dict['DESC_LIST'] = util.getlist(
            self.config.getstr('config', 'DESC_LIST', '')
        )
        c_dict['FCST_LEAD_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_LEAD_LIST', '')
        )
        c_dict['OBS_LEAD_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_LEAD_LIST', '')
        )
        c_dict['FCST_VALID_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_VALID_HOUR_LIST', '')
        )
        c_dict['FCST_INIT_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_INIT_HOUR_LIST', '')
        )
        c_dict['OBS_VALID_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_VALID_HOUR_LIST', '')
        )
        c_dict['OBS_INIT_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_INIT_HOUR_LIST', '')
        )
        c_dict['VX_MASK_LIST'] = util.getlist(
            self.config.getstr('config', 'VX_MASK_LIST', '')
        )
        c_dict['INTERP_MTHD_LIST'] = util.getlist(
            self.config.getstr('config', 'INTERP_MTHD_LIST', '')
        )
        c_dict['INTERP_PNTS_LIST'] = util.getlist(
            self.config.getstr('config', 'INTERP_PNTS_LIST', '')
        )
        c_dict['COV_THRESH_LIST'] = util.getlist(
            self.config.getstr('config', 'COV_THRESH_LIST', '')
        )
        c_dict['ALPHA_LIST'] = util.getlist(
            self.config.getstr('config', 'ALPHA_LIST', '')
        )
        c_dict['LINE_TYPE_LIST'] = util.getlist(
            self.config.getstr('config', 'LINE_TYPE_LIST', '')
        )
        c_dict['USER_SCRIPT_LIST'] = util.getlist(
            self.config.getstr('config', 'MAKE_PLOTS_USER_SCRIPT_LIST', '')
        )
        c_dict['VERIF_CASE'] = self.config.getstr('config',
                                                  'MAKE_PLOTS_VERIF_CASE', '')

        if c_dict['VERIF_CASE'] not in self.accepted_verif_lists:
            self.log_error(self.c_dict['VERIF_CASE'] + " is not an"
                           + "an accepted MAKE_PLOTS_VERIF_CASE "
                           + "option. Options are "
                           + ', '.join(self.accepted_verif_lists.keys()))

        c_dict['VERIF_TYPE'] = self.config.getstr('config',
                                                  'MAKE_PLOTS_VERIF_TYPE', '')

        # if not precip case, check that verif type is an accepted verif type
        if c_dict['VERIF_CASE'] != 'precip' and c_dict['VERIF_TYPE'] not in (
                self.accepted_verif_lists.get(c_dict['VERIF_CASE'], [])
        ):
            print(f"VERIF CASE: {c_dict['VERIF_CASE']}")
            accepted_types = self.accepted_verif_lists.get(c_dict['VERIF_CASE']).keys()
            self.log_error(f"{c_dict['VERIF_TYPE']} is not "
                           "an accepted MAKE_PLOTS_VERIF_TYPE "
                           "option for MAKE_PLOTS_VERIF_CASE "
                           f"= {c_dict['VERIF_CASE']}. Options "
                           f"are {', '.join(accepted_types)}")

        if not c_dict['USER_SCRIPT_LIST'] and not(c_dict['VERIF_CASE'] or
                                                  c_dict['VERIF_TYPE']):
            self.log_error("Please defined either "
                           "MAKE_PLOTS_VERIF_CASE and "
                           "MAKE_PLOTS_VERIF_TYPE, or "
                           "MAKE_PLOTS_USER_SCRIPT_LIST")

        c_dict['STATS_LIST'] = util.getlist(
            self.config.getstr('config', 'MAKE_PLOTS_STATS_LIST', '')
        )
        c_dict['AVERAGE_METHOD'] = self.config.getstr(
            'config','MAKE_PLOTS_AVERAGE_METHOD', 'MEAN'
        )
        c_dict['CI_METHOD'] = self.config.getstr('config',
                                                 'MAKE_PLOTS_CI_METHOD',
                                                 'NONE')
        c_dict['VERIF_GRID'] = self.config.getstr('config',
                                                  'MAKE_PLOTS_VERIF_GRID')
        c_dict['EVENT_EQUALIZATION'] = (
            self.config.getstr('config', 'MAKE_PLOTS_EVENT_EQUALIZATION')
        )
        c_dict['LOG_METPLUS'] = self.config.getstr('config', 'LOG_METPLUS')
        c_dict['LOG_LEVEL'] = self.config.getstr('config', 'LOG_LEVEL')
        return c_dict

    def list_to_str(self, list_of_values):
        """! Turn a list of values into a single string so it can be 
             set to an environment variable and read by the MET 
             stat_analysis config file.
                 
             Args:
                 list_of_values - list of values
  
             Returns:
                 list_as_str    - string created from list_of_values
                                  with the values separated by commas 
        """
        list_as_str=''
        if len(list_of_values) > 0:
            for lt in range(len(list_of_values)):
                if lt == len(list_of_values)-1:
                    list_as_str = list_as_str+str(list_of_values[lt])
                else:
                    list_as_str = list_as_str+str(list_of_values[lt]+', ')
        return list_as_str

    def set_lists_loop_or_group(self, config_lists_to_group_items,
                                config_lists_to_loop_items, config_dict):
        """! Determine whether the lists from the METplus config file
             should treat the items in that list as a group or items 
             to be looped over based on user settings, the values
             in the list, and process being run.
             
             Args:
                 config_lists_to_group_items - list of the METplus 
                                               config list names
                                               to group the list's 
                                               items set by user
                 config_lists_to_loop_items  - list of the METplus 
                                               config list names
                                               to loop over the 
                                               list's items set by 
                                               user
                 config_dict                 - dictionary containing
                                               the configuration 
                                               information
             
             Returns: 
                 lists_to_group_items        - list of all the list names 
                                               whose items are being 
                                               grouped together
                 lists_to_loop_items         - list of all the list names 
                                               whose items are being
                                               looped over 
        """
        expected_config_lists = [
             'MODEL_LIST', 'DESC_LIST',
             'FCST_LEAD_LIST', 'OBS_LEAD_LIST',
             'FCST_VALID_HOUR_LIST', 'FCST_INIT_HOUR_LIST',
             'OBS_VALID_HOUR_LIST', 'OBS_INIT_HOUR_LIST',
             'FCST_VAR_LIST', 'OBS_VAR_LIST',
             'FCST_UNITS_LIST', 'OBS_UNITS_LIST',
             'FCST_LEVEL_LIST', 'OBS_LEVEL_LIST',
             'VX_MASK_LIST', 'INTERP_MTHD_LIST',
             'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
             'OBS_THRESH_LIST', 'COV_THRESH_LIST',
             'ALPHA_LIST', 'LINE_TYPE_LIST',
             'STATS_LIST'
        ]
        lists_to_group_items = config_lists_to_group_items
        lists_to_loop_items = config_lists_to_loop_items
        for config_list in expected_config_lists:
            if (not config_list in config_lists_to_group_items
                    and not config_list in config_lists_to_loop_items):
                if config_list == 'LINE_TYPE_LIST' or config_list == 'STATS_LIST':
                    lists_to_group_items.append(config_list)
                elif config_dict[config_list] == []:
                    self.logger.warning(config_list+" is empty, "
                                        +"will be treated as group.")
                    lists_to_group_items.append(config_list)
                else:
                    lists_to_loop_items.append(config_list)
            elif (config_list in config_lists_to_loop_items
                      and config_dict[config_list] == []):
                self.logger.warning(config_list+" is empty, "
                                    +"will be treated as group.")
                lists_to_group_items.append(config_list)
                lists_to_loop_items.remove(config_list)
            if (config_list == 'MODEL_LIST' 
                    or config_list == 'FCST_LEAD_LIST'
                    or config_list == 'FCST_LEVEL_LIST'
                    or config_list == 'OBS_LEVEL_LIST'
                    or config_list == 'FCST_THRESH_LIST'
                    or config_list == 'OBS_THRESH_LIST'
                    or config_list == 'FCST_UNITS_LIST'
                    or config_list == 'OBS_UNITS_LIST'):
                if config_list not in lists_to_group_items:
                    lists_to_group_items.append(config_list)
                if config_list in lists_to_loop_items:
                    lists_to_loop_items.remove(config_list)
        self.logger.debug("Items in these lists will be grouped together: "
                          +', '.join(lists_to_group_items))
        self.logger.debug("Items in these lists will be looped over: "
                          +', '.join(lists_to_loop_items))
        return lists_to_group_items, lists_to_loop_items

    def parse_model_info(self):
        """! Parse for model information.
             
             Args:
                
             Returns:
                 model_list - list of dictionaries containing
                              model information
        """
        model_info_list = []
        all_conf = self.config.keys('config')
        model_indices = []
        regex = re.compile(r'MODEL(\d+)$')
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                model_indices.append(result.group(1))
        for m in model_indices:
            if self.config.has_option('config', 'MODEL'+m):
                model_name = self.config.getstr('config', 'MODEL'+m)
                model_reference_name = (
                    self.config.getstr('config', 'MODEL'+m+'_REFERENCE_NAME',
                                       model_name)
                )
                if self.config.has_option('config', 'MODEL'+m+'_OBTYPE'):
                    model_obtype = (
                        self.config.getstr('config', 'MODEL'+m+'_OBTYPE')
                    )
                else:
                    self.log_error("MODEL"+m+"_OBTYPE was not set.")
                    exit(1)
            mod = {}
            mod['name'] = model_name
            mod['reference_name'] = model_reference_name
            mod['obtype'] = model_obtype
            model_info_list.append(mod)
        return model_info_list, model_indices

    def setup_output_base(self):
        # Set up output base
        output_base_dir = self.c_dict['OUTPUT_BASE_DIR']
        output_base_data_dir = os.path.join(output_base_dir, 'data')
        output_base_images_dir = os.path.join(output_base_dir, 'images')
        if not os.path.exists(output_base_dir):
            util.mkdir_p(output_base_dir)
            util.mkdir_p(output_base_data_dir)
            util.mkdir_p(output_base_images_dir)
        else:
            if os.path.exists(output_base_data_dir):
                if len(output_base_data_dir) > 0:
                    for rmfile in os.listdir(output_base_data_dir):
                        os.remove(os.path.join(output_base_data_dir,rmfile))

    def get_met_version(self):
        p = subprocess.Popen(["stat_analysis", "--version"],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        out = out.decode(encoding='utf-8', errors='strict')
        for line in out.split('\n'):
            if 'MET Version:' in line:
                met_verison_line = line
        met_version_str = (
            met_verison_line.partition('MET Version:')[2].split('V')[1]
        )
        if len(met_version_str) == 3:
            met_version = float(met_version_str)
        else:
            met_version = float(met_version_str.rpartition('.')[0])

        return met_version

    def create_plots_new(self, runtime_settings_dict_list):

        self.setup_output_base()

        # Get MET version used to run stat_analysis
        met_version = str(self.get_met_version())

        if self.c_dict['USER_SCRIPT_LIST']:
            scripts_to_run = self.c_dict['USER_SCRIPT_LIST']
        elif self.c_dict['VERIF_TYPE'] == 'precip':
            scripts_to_run = self.accepted_verif_lists.get(self.c_dict['VERIF_CASE'])
        else:
            scripts_to_run = self.accepted_verif_lists.get(self.c_dict['VERIF_CASE'])\
                .get(self.c_dict['VERIF_TYPE'])

        # Loop over run settings.
        for runtime_settings_dict in runtime_settings_dict_list:
            # set environment variables
            for name, value in runtime_settings_dict.items():
                self.add_env_var(name, value)

            # TODO: check if value already is set in runtime settings?
            for key in self.add_from_c_dict_list:
                if key not in runtime_settings_dict:
                    self.add_env_var(key, self.c_dict[key])

            self.add_env_var('MET_VERSION', met_version)

            # obtype env var is named differently in StatAnalysis wrapper
            self.add_env_var('MODEL_OBTYPE', runtime_settings_dict['OBTYPE'])

            self.add_env_var('STATS',
                             self.list_to_str(self.c_dict['STATS_LIST']))

            # send environment variables to logger
            self.print_all_envs()

            for script in scripts_to_run:
                self.plotting_script = (
                    os.path.join(self.c_dict['SCRIPTS_BASE_DIR'],
                                 script)
                )

                self.build_and_run_command()
                self.clear()

    def create_plots(self):
        """! Set up variables and general looping for creating
              verification plots
            
             Args:
                 verif_case - string of the verification case to make
                              plots for
                 verif_type - string of the verification type to make
                              plots for
               
             Returns:
        """
        return
        # Do some preprocessing, formatting, and gathering
        # of config information.
        formatted_c_dict = copy.deepcopy(self.c_dict)
        model_info_list, model_indices = self.parse_model_info()
        if self.c_dict['MODEL_LIST'] == []:
            if model_indices > 0:
                self.logger.warning("MODEL_LIST was left blank, "
                                    +"creating with MODELn information.")
                model_name_list = []
                for model_info in model_info_list:
                    model_name_list.append(model_info['name'])
                formatted_c_dict['MODEL_LIST'] = model_name_list
            else:
                self.log_error("No model information was found.")
                exit(1)
        model_obtype_list = []
        model_reference_name_list = []
        for model_info in model_info_list:
            model_obtype_list.append(model_info['obtype'])
            model_reference_name_list.append(model_info['reference_name'])

        # don't allow more than 8 models
        if len(formatted_c_dict['MODEL_LIST']) > 8:
            self.log_error("Number of models for plotting limited to 8.")
            exit(1)

        self.setup_output_base()

        # Get MET version used to run stat_analysis
        met_version = self.get_met_version()

        # Add additional variable information to
        # c_dict['VAR_LIST'] and make individual dictionaries
        # for each threshold
        var_info_c_dict_list = self.c_dict['VAR_LIST']
        var_info_list = []
        for var_info_c_dict in var_info_c_dict_list:
            n = var_info_c_dict['index']
            fcst_units = self.config.getstr('config',
                                            'FCST_VAR'+n+'_UNITS',
                                            '')
            obs_units = self.config.getstr('config',
                                           'OBS_VAR'+n+'_UNITS',
                                           '')
            if len(obs_units) == 0 and len(fcst_units) != 0:
                obs_units = fcst_units
            if len(fcst_units) == 0 and len(obs_units) != 0:
                fcst_units = obs_units
            run_fourier = (
                self.config.getbool('config',
                                    'VAR'+n+'_FOURIER_DECOMP',
                                    False)
            )
            fourier_wave_num_pairs = util.getlist(
                self.config.getstr('config',
                                   'VAR'+n+'_WAVE_NUM_LIST',
                                   '')
            )
            if len(var_info_c_dict['fcst_thresh']) > 0:
                for fcst_thresh in var_info_c_dict['fcst_thresh']:
                    thresh_index = (
                        var_info_c_dict['fcst_thresh'].index(fcst_thresh)
                    )
                    obs_thresh = (
                        var_info_c_dict['obs_thresh'][thresh_index]
                    )
                    if run_fourier == False:
                        var_info = {}
                        var_info['index'] = var_info_c_dict['index']
                        var_info['fcst_name'] = [
                            var_info_c_dict['fcst_name']
                        ]
                        var_info['obs_name'] = [
                            var_info_c_dict['obs_name']
                        ]
                        var_info['fcst_level'] = [
                            var_info_c_dict['fcst_level']
                        ]
                        var_info['obs_level'] = [
                            var_info_c_dict['obs_level']
                        ]
                        var_info['fcst_extra'] = [
                            var_info_c_dict['fcst_extra']
                        ]
                        var_info['obs_extra'] = [
                            var_info_c_dict['obs_extra']
                        ]
                        var_info['fcst_thresh'] = [fcst_thresh]
                        var_info['obs_thresh'] = [obs_thresh]
                        if len(fcst_units) == 0:
                            var_info['fcst_units'] = []
                        else:
                            var_info['fcst_units'] = [fcst_units]
                        if len(obs_units) == 0:
                            var_info['obs_units'] = []
                        else:
                            var_info['obs_units'] = [obs_units]
                        var_info['run_fourier'] = run_fourier
                        var_info['fourier_wave_num'] = []
                        var_info_list.append(var_info)
                    else:
                        for pair in fourier_wave_num_pairs:
                            var_info = {}
                            var_info['index'] = var_info_c_dict['index']
                            var_info['fcst_name'] = [
                                var_info_c_dict['fcst_name']
                            ]
                            var_info['obs_name'] = [
                                var_info_c_dict['obs_name']
                            ]
                            var_info['fcst_level'] = [
                                var_info_c_dict['fcst_level']
                            ]
                            var_info['obs_level'] = [
                                var_info_c_dict['obs_level']
                            ]
                            var_info['fcst_extra'] = [
                                var_info_c_dict['fcst_extra']
                            ]
                            var_info['obs_extra'] = [
                                var_info_c_dict['obs_extra']
                            ]
                            var_info['fcst_thresh'] = [fcst_thresh]
                            var_info['obs_thresh'] = [obs_thresh]
                            if len(fcst_units) == 0:
                                var_info['fcst_units'] = []
                            else:
                                var_info['fcst_units'] = [fcst_units]
                            if len(obs_units) == 0:
                                var_info['obs_units'] = []
                            else:
                                var_info['obs_units'] = [obs_units]
                            var_info['run_fourier'] = run_fourier
                            var_info['fourier_wave_num'] = ['WV1_'+pair]
                            var_info_list.append(var_info)
            else:
                if run_fourier == False:
                    var_info = {}
                    var_info['index'] = var_info_c_dict['index']
                    var_info['fcst_name'] = [var_info_c_dict['fcst_name']]
                    var_info['obs_name'] = [var_info_c_dict['obs_name']]
                    var_info['fcst_level'] = [var_info_c_dict['fcst_level']]
                    var_info['obs_level'] = [var_info_c_dict['obs_level']]
                    var_info['fcst_extra'] = [var_info_c_dict['fcst_extra']]
                    var_info['obs_extra'] = [var_info_c_dict['obs_extra']]
                    var_info['fcst_thresh'] = []
                    var_info['obs_thresh'] = []
                    if len(fcst_units) == 0:
                        var_info['fcst_units'] = []
                    else:
                        var_info['fcst_units'] = [fcst_units]
                    if len(obs_units) == 0:
                        var_info['obs_units'] = []
                    else:
                        var_info['obs_units'] = [obs_units]
                    var_info['run_fourier'] = run_fourier
                    var_info['fourier_wave_num'] = []
                    var_info_list.append(var_info)
                else:
                    for pair in fourier_wave_num_pairs:
                        var_info = {}
                        var_info['index'] = var_info_c_dict['index']
                        var_info['fcst_name'] = [
                            var_info_c_dict['fcst_name']
                        ]
                        var_info['obs_name'] = [
                            var_info_c_dict['obs_name']
                        ]
                        var_info['fcst_level'] = [
                            var_info_c_dict['fcst_level']
                        ]
                        var_info['obs_level'] = [
                            var_info_c_dict['obs_level']
                        ]
                        var_info['fcst_extra'] = [
                            var_info_c_dict['fcst_extra']
                        ]
                        var_info['obs_extra'] = [
                            var_info_c_dict['obs_extra']
                        ]
                        var_info['fcst_thresh'] = []
                        var_info['obs_thresh'] = []
                        if len(fcst_units) == 0:
                            var_info['fcst_units'] = []
                        else:
                            var_info['fcst_units'] = [fcst_units]
                        if len(obs_units) == 0:
                            var_info['obs_units'] = []
                        else:
                            var_info['obs_units'] = [obs_units]
                        var_info['run_fourier'] = run_fourier
                        var_info['fourier_wave_num'] = ['WV1_'+pair]
                        var_info_list.append(var_info)
        var_info_list_sorted = (
            sorted(var_info_list, key = lambda i: (i['index'], 
                                                   i['fourier_wave_num']))
        )
        var_group_info_list = []
        keys_to_append = [ 'fcst_level', 'obs_level', 
                           'fcst_thresh', 'obs_thresh' ]
        for group, group_info_list in \
                itertools.groupby(var_info_list_sorted, 
                                  key=lambda x:(x['index'], 
                                                x['fourier_wave_num'])):
             var_group_info = {}
             for group_info in group_info_list:
                 if len(var_group_info) == 0:
                     for key, value in group_info.items():
                         var_group_info[key] = group_info[key]
                 else:
                      for key in keys_to_append:
                          if (group_info[key] != var_group_info[key]
                              and group_info[key][0] not in var_group_info[key]):
                                  var_group_info[key].append(group_info[key][0])
             var_group_info_list.append(var_group_info)
        for fcst_valid_hour in self.c_dict['FCST_VALID_HOUR_LIST']:
            index = self.c_dict['FCST_VALID_HOUR_LIST'].index(fcst_valid_hour)
            formatted_c_dict['FCST_VALID_HOUR_LIST'][index] = (
                fcst_valid_hour.ljust(6,'0')
            )
        for fcst_init_hour in self.c_dict['FCST_INIT_HOUR_LIST']:
            index = self.c_dict['FCST_INIT_HOUR_LIST'].index(fcst_init_hour)
            formatted_c_dict['FCST_INIT_HOUR_LIST'][index] = (
                fcst_init_hour.ljust(6,'0')
            )
        for obs_valid_hour in self.c_dict['OBS_VALID_HOUR_LIST']:
            index = self.c_dict['OBS_VALID_HOUR_LIST'].index(obs_valid_hour)
            formatted_c_dict['OBS_VALID_HOUR_LIST'][index] = (
                obs_valid_hour.ljust(6,'0')
            )
        for obs_init_hour in self.c_dict['OBS_INIT_HOUR_LIST']:
            index = self.c_dict['OBS_INIT_HOUR_LIST'].index(obs_init_hour)
            formatted_c_dict['OBS_INIT_HOUR_LIST'][index] = (
                obs_init_hour.ljust(6,'0')
            )
        for fcst_lead in self.c_dict['FCST_LEAD_LIST']:
            index = self.c_dict['FCST_LEAD_LIST'].index(fcst_lead)
            if len(fcst_lead)%2 == 0:
                formatted_fcst_lead = fcst_lead.ljust(6,'0')
            else:
                formatted_fcst_lead = fcst_lead.ljust(7,'0')
            formatted_c_dict['FCST_LEAD_LIST'][index] = formatted_fcst_lead
        for obs_lead in self.c_dict['OBS_LEAD_LIST']:
            index = self.c_dict['OBS_LEAD_LIST'].index(obs_lead)
            if len(obs_lead)%2 == 0:
                formatted_obs_lead = obs_lead.ljust(6,'0')
            else:
                formatted_obs_lead = obs_lead.ljust(7,'0')
            formatted_c_dict['OBS_LEAD_LIST'][index] = formatted_obs_lead
        # Loop through variables and add information
        # to a special variable dictionary
        for var_info in var_group_info_list:
            var_info_formatted_c_dict = copy.deepcopy(formatted_c_dict)
            var_info_formatted_c_dict['FCST_VAR_LIST'] = var_info['fcst_name']
            var_info_formatted_c_dict['FCST_LEVEL_LIST'] = (
                var_info['fcst_level']
            )
            var_info_formatted_c_dict['FCST_UNITS_LIST'] = (
                var_info['fcst_units']
            )
            var_info_formatted_c_dict['OBS_VAR_LIST'] = var_info['obs_name']
            var_info_formatted_c_dict['OBS_LEVEL_LIST'] = (
                var_info['obs_level']
            )
            var_info_formatted_c_dict['OBS_UNITS_LIST'] = (
                var_info['obs_units']
            )
            var_info_formatted_c_dict['FCST_THRESH_LIST'] = (
                var_info['fcst_thresh']
            )
            var_info_formatted_c_dict['OBS_THRESH_LIST'] = (
                var_info['obs_thresh']
            )
            if var_info['run_fourier'] == True:
                for fvn in var_info['fourier_wave_num']:
                    var_info_formatted_c_dict['INTERP_MTHD_LIST'] \
                    .append(fvn)
            # Parse whether all expected METplus config _LIST variables
            # to be treated as a loop or group.
            config_lists_to_group_items = (
                var_info_formatted_c_dict['GROUP_LIST_ITEMS']
            )
            config_lists_to_loop_items = (
                var_info_formatted_c_dict['LOOP_LIST_ITEMS']
            )
            lists_to_group_items, lists_to_loop_items = (
                self.set_lists_loop_or_group(config_lists_to_group_items,
                                             config_lists_to_loop_items,
                                             var_info_formatted_c_dict)
            )
            runtime_setup_dict = {}
            add_from_c_dict_list = [
                'VERIF_CASE', 'VERIF_TYPE', 'INPUT_BASE_DIR', 'OUTPUT_BASE_DIR',
                'SCRIPTS_BASE_DIR', 'DATE_TYPE', 'VALID_BEG', 'VALID_END',
                'INIT_BEG', 'INIT_END', 'AVERAGE_METHOD', 'CI_METHOD',
                'VERIF_GRID','EVENT_EQUALIZATION', 'LOG_METPLUS', 'LOG_LEVEL'
            ]
            for key in add_from_c_dict_list:
                runtime_setup_dict[key] = [self.c_dict[key]]
            runtime_setup_dict['MET_VERSION'] = [str(met_version)]
            runtime_setup_dict['MODEL_OBTYPE'] = [
                self.list_to_str(model_obtype_list)
            ]
            runtime_setup_dict['MODEL_REFERENCE_NAME'] = [
                self.list_to_str(model_reference_name_list)
            ]
            # Fill setup dictionary for MET config variable name
            # and its value as a string for group lists.
            for list_to_group_items in lists_to_group_items:
                runtime_setup_dict_name = (
                    list_to_group_items.replace('_LIST', '')
                )
                runtime_setup_dict_value = [
                    self.list_to_str(
                        var_info_formatted_c_dict[list_to_group_items]
                    )
                ]
                runtime_setup_dict[runtime_setup_dict_name] = (
                    runtime_setup_dict_value
                )
            # Fill setup dictionary for MET config variable name
            # and its value as a list for loop lists. Some items
            # in lists need to be formatted now, others done later.
            ##gitd = [
            ##    'MODEL_LIST', 'FCST_VALID_HOUR_LIST', 'OBS_VALID_HOUR_LIST',
            ##    'FCST_INIT_HOUR_LIST','OBS_INIT_HOUR_LIST'
            ##]
            for list_to_loop_items in lists_to_loop_items:
                #if list_to_loop_items not in format_later_list:
                for item in \
                        var_info_formatted_c_dict[list_to_loop_items]:
                    index = (
                        var_info_formatted_c_dict[list_to_loop_items] \
                        .index(item)
                    )
                    var_info_formatted_c_dict[list_to_loop_items][index] \
                        = item
                runtime_setup_dict_name = list_to_loop_items.replace('_LIST', 
                                                                     '')
                runtime_setup_dict_value = (
                    var_info_formatted_c_dict[list_to_loop_items]
                )
                runtime_setup_dict[runtime_setup_dict_name] = (
                    runtime_setup_dict_value
                )
            # Create run time dictionary with all the combinations
            # of settings to be run.
            runtime_setup_dict_names = sorted(runtime_setup_dict)
            runtime_settings_dict_list = (
                [dict(zip(runtime_setup_dict_names, prod)) for prod in
                itertools.product(*(runtime_setup_dict[name] for name in
                runtime_setup_dict_names))]
            )

        if self.c_dict['USER_SCRIPT_LIST']:
            scripts_to_run = self.c_dict['USER_SCRIPT_LIST']
        elif self.c_dict['VERIF_TYPE'] == 'precip':
            scripts_to_run = self.accepted_verif_lists.get(self.c_dict['VERIF_CASE'])
        else:
            scripts_to_run = self.accepted_verif_lists.get(self.c_dict['VERIF_CASE'])\
                .get(self.c_dict['VERIF_TYPE'])

        # Loop over run settings.
        for runtime_settings_dict in runtime_settings_dict_list:
            # set environment variables
            for name, value in runtime_settings_dict.items():
                self.add_env_var(name, value)

            # send environment variables to logger
            self.print_all_envs()

            for script in scripts_to_run:
                self.plotting_script = (
                    os.path.join(runtime_settings_dict['SCRIPTS_BASE_DIR'],
                    script)
                )

                self.build_and_run_command()
                self.clear()

                
    def run_all_times(self):
        if self.c_dict['USER_SCRIPT_LIST']:
            self.logger.info("Running plots for user specified list of "
                             "scripts.")

        elif (self.c_dict['VERIF_CASE'] and self.c_dict['VERIF_TYPE']):
            self.logger.info("Running plots for VERIF_CASE = "
                             +self.c_dict['VERIF_CASE']+", "
                             +"VERIF_TYPE = "
                             +self.c_dict['VERIF_TYPE'])

        self.create_plots()

if __name__ == "__main__":
    util.run_stand_alone(__file__, "MakePlots")
