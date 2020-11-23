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

from ..util import met_util as util
from . import CommandBuilder

# handle if module can't be loaded to run wrapper
wrapper_cannot_run = False
exception_err = ''
try:
    from ush.plotting_scripts import plot_util
except Exception as err_msg:
    wrapper_cannot_run = True
    exception_err = err_msg

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

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_path = 'python'
        self.app_name = 'make_plots'
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

        if wrapper_cannot_run:
            self.log_error(f"There was a problem importing modules: {exception_err}\n")
            return

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

        # Get MET version used to run stat_analysis
        c_dict['MET_VERSION'] = str(self.get_met_version())

        return c_dict

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
        stat_analysis_exe = os.path.join(self.config.getdir('MET_BIN_DIR'),
                                         'stat_analysis')
        p = subprocess.Popen([stat_analysis_exe, "--version"],
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

    def create_plots(self, runtime_settings_dict_list):

        if self.c_dict['USER_SCRIPT_LIST']:
            self.logger.info("Running plots for user specified list of "
                             "scripts.")

        elif (self.c_dict['VERIF_CASE'] and self.c_dict['VERIF_TYPE']):
            self.logger.info("Running plots for VERIF_CASE = "
                             +self.c_dict['VERIF_CASE']+", "
                             +"VERIF_TYPE = "
                             +self.c_dict['VERIF_TYPE'])

        self.setup_output_base()

        if self.c_dict['USER_SCRIPT_LIST']:
            scripts_to_run = self.c_dict['USER_SCRIPT_LIST']
        elif self.c_dict['VERIF_CASE'] == 'precip':
            scripts_to_run = self.accepted_verif_lists.get(self.c_dict['VERIF_CASE'])
        else:
            scripts_to_run = self.accepted_verif_lists.get(self.c_dict['VERIF_CASE'])\
                .get(self.c_dict['VERIF_TYPE'])

        # Loop over run settings.
        for runtime_settings_dict in runtime_settings_dict_list:
            # set environment variables
            for name, value in runtime_settings_dict.items():
                self.add_env_var(name, value.replace('"', ''))

            for key in self.add_from_c_dict_list:
                if key not in runtime_settings_dict:
                    self.add_env_var(key, self.c_dict[key].replace('"', ''))

            self.add_env_var('MET_VERSION', self.c_dict['MET_VERSION'])

            # obtype env var is named differently in StatAnalysis wrapper
            self.add_env_var('MODEL_OBTYPE', runtime_settings_dict['OBTYPE'].replace('"', ''))

            self.add_env_var('STATS',
                             ', '.join(self.c_dict['STATS_LIST']).replace('"', ''))

            # send environment variables to logger
            self.set_environment_variables()

            for script in scripts_to_run:
                self.plotting_script = (
                    os.path.join(self.c_dict['SCRIPTS_BASE_DIR'],
                                 script)
                )

                self.build_and_run_command()
                self.clear()
