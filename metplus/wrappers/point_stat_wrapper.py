"""
Program Name: point_stat_wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET point_stat
History Log:  Initial version
Usage: point_stat_wrapper.py
Parameters: None
Input Files: netCDF data files
Output Files: ascii files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import CompareGriddedWrapper

class PointStatWrapper(CompareGriddedWrapper):
    """! Wrapper to the MET tool, Point-Stat."""

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'point_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        """! Create a dictionary that holds all the values set in the
             METplus config file for the point-stat wrapper.

             Returns:
                 c_dict   - A dictionary containing the key-value pairs set
                             in the METplus configuration file.
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_POINT_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['OFFSETS'] = util.getlistint(self.config.getstr('config',
                                                               'POINT_STAT_OFFSETS',
                                                               '0'))
        c_dict['FCST_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'FCST_POINT_STAT_INPUT_TEMPLATE',
                               '')
        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error("FCST_POINT_STAT_INPUT_TEMPLATE required to run")

        c_dict['OBS_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'OBS_POINT_STAT_INPUT_TEMPLATE',
                               '')
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("OBS_POINT_STAT_INPUT_TEMPLATE required to run")

        c_dict['FCST_INPUT_DATATYPE'] = \
            self.config.getstr('config', 'FCST_POINT_STAT_INPUT_DATATYPE', '')
        c_dict['OBS_INPUT_DATATYPE'] = \
            self.config.getstr('config', 'OBS_POINT_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DIR'] = self.config.getdir('FCST_POINT_STAT_INPUT_DIR','')

        c_dict['OBS_INPUT_DIR'] = self.config.getdir('OBS_POINT_STAT_INPUT_DIR','')

        c_dict['OUTPUT_DIR'] = \
            self.config.getdir('POINT_STAT_OUTPUT_DIR', '')

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'POINT_STAT_OUTPUT_TEMPLATE')
        )

        # get climatology config variables
        self.read_climo_wrapper_specific('POINT_STAT', c_dict)

        # Configuration
        c_dict['CONFIG_FILE'] = \
            self.config.getraw('config', 'POINT_STAT_CONFIG_FILE', '')

        c_dict['MODEL'] = self.config.getstr('config', 'MODEL')

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'POINT_STAT_REGRID_TO_GRID', '')

        c_dict['POINT_STAT_GRID'] = self.config.getstr('config', 'POINT_STAT_GRID')
        c_dict['POINT_STAT_POLY'] = self.config.getstr('config', 'POINT_STAT_POLY', '')
        c_dict['POINT_STAT_STATION_ID'] = self.config.getstr('config', 'POINT_STAT_STATION_ID', '')
        c_dict['POINT_STAT_MESSAGE_TYPE'] = self.config.getstr('config', 'POINT_STAT_MESSAGE_TYPE', '')

        c_dict['OBS_VALID_BEG'] = self.config.getraw('config', 'POINT_STAT_OBS_VALID_BEG', '')
        c_dict['OBS_VALID_END'] = self.config.getraw('config', 'POINT_STAT_OBS_VALID_END', '')

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'point_stat')

        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'POINT_STAT_VERIFICATION_MASK_TEMPLATE',
                               '')

        c_dict['FCST_PROB_THRESH'] = self.config.getstr('config',
                                                        'FCST_POINT_STAT_PROB_THRESH', '==0.1')
        c_dict['OBS_PROB_THRESH'] = self.config.getstr('config',
                                                       'OBS_POINT_STAT_PROB_THRESH', '==0.1')

        c_dict['ONCE_PER_FIELD'] = self.config.getbool('config',
                                                       'POINT_STAT_ONCE_PER_FIELD',
                                                       False)

        if c_dict['FCST_INPUT_TEMPLATE'] == '':
            self.log_error('Must set FCST_POINT_STAT_INPUT_TEMPLATE in config file')

        if c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.log_error('Must set OBS_POINT_STAT_INPUT_TEMPLATE in config file')

        if c_dict['OUTPUT_DIR'] == '':
            self.log_error('Must set POINT_STAT_OUTPUT_DIR in config file')

        if not c_dict['CONFIG_FILE']:
            self.log_error("POINT_STAT_CONFIG_FILE must be set.")

        return c_dict

    def add_obs_valid_args(self, time_info):
        for ext in ['BEG', 'END']:
            if self.c_dict[f'OBS_VALID_{ext}']:
                obs_valid = do_string_sub(self.c_dict[f'OBS_VALID_{ext}'],
                                          **time_info)
                self.args.append(f"-obs_valid_{ext.lower()} {obs_valid}")

    def set_environment_variables(self, fcst_field=None, obs_field=None, time_info=None):
        """! Set all the environment variables in the MET config
             file to the corresponding values in the METplus config file.

             Args:

             Returns: None - invokes parent class, CommandBuilder add_env_var
                             to add each environment variable to run the

        """
        # MET accepts a list of values for POINT_STAT_POLY, POINT_STAT_GRID,
        # POINT_STAT_STATION_ID, and POINT_STAT_MESSAGE_TYPE. If these
        # values are not set in the METplus config file, assign them to "[]" so
        # MET recognizes that these are empty lists, resulting in the
        # expected behavior.
        self.add_env_var('POINT_STAT_POLY',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_POLY'])}]")

        self.add_env_var('POINT_STAT_GRID',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_GRID'])}]")

        self.add_env_var('POINT_STAT_STATION_ID',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_STATION_ID'])}]")

        self.add_env_var('POINT_STAT_MESSAGE_TYPE',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_MESSAGE_TYPE'])}]")

        self.add_env_var('FCST_FIELD', fcst_field)
        self.add_env_var('OBS_FIELD', obs_field)

        # Set the environment variables corresponding to the obs_window
        # dictionary.
        self.add_env_var('OBS_WINDOW_BEGIN',
                         str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var('OBS_WINDOW_END', str(self.c_dict['OBS_WINDOW_END']))

        # add additional env vars if they are specified
        self.add_env_var('VERIF_MASK',
                         self.c_dict.get('VERIFICATION_MASK', ''))

        self.add_env_var('OUTPUT_PREFIX', self.get_output_prefix(time_info))

        # set climatology environment variables
        self.set_climo_env_vars()

        self.add_common_envs()

        super().set_environment_variables(time_info)
