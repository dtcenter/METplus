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

from ..util import getlistint
from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import CompareGriddedWrapper

class PointStatWrapper(CompareGriddedWrapper):
    """! Wrapper to the MET tool, Point-Stat."""

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_FCST_FIELD',
        'METPLUS_OBS_FIELD',
        'METPLUS_MESSAGE_TYPE',
        'METPLUS_OBS_WINDOW_DICT',
        'METPLUS_MASK_GRID',
        'METPLUS_MASK_POLY',
        'METPLUS_MASK_SID',
        'METPLUS_MASK_LLPNT',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_CLIMO_CDF_DICT',
        'METPLUS_OBS_QUALITY_INC',
        'METPLUS_OBS_QUALITY_EXC',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_INTERP_DICT',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_HSS_EC_VALUE',
        'METPLUS_HIRA_DICT',
        'METPLUS_MESSAGE_TYPE_GROUP_MAP',
    ]

    # handle deprecated env vars used pre v4.0.0
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'CLIMO_MEAN_FILE',
        'CLIMO_STDEV_FILE',
    ]

    OUTPUT_FLAGS = ['fho',
                    'ctc',
                    'cts',
                    'mctc',
                    'mcts',
                    'cnt',
                    'sl1l2',
                    'sal1l2',
                    'vl1l2',
                    'val1l2',
                    'vcnt',
                    'pct',
                    'pstd',
                    'pjc',
                    'prc',
                    'ecnt',
                    'rps',
                    'eclv',
                    'mpr',
                    'orank',
                    ]

    def __init__(self, config, instance=None, config_overrides=None):
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
        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               'LOG_POINT_STAT_VERBOSITY',
                                c_dict['VERBOSITY'])
        )
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['OFFSETS'] = getlistint(
            self.config.getstr('config',
                               'POINT_STAT_OFFSETS',
                               '0')
        )
        c_dict['FCST_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'FCST_POINT_STAT_INPUT_TEMPLATE',
                               '')
        )

        c_dict['OBS_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'OBS_POINT_STAT_INPUT_TEMPLATE',
                               '')
        )

        c_dict['FCST_INPUT_DATATYPE'] = (
            self.config.getstr('config', 'FCST_POINT_STAT_INPUT_DATATYPE', '')
        )
        c_dict['OBS_INPUT_DATATYPE'] = (
            self.config.getstr('config', 'OBS_POINT_STAT_INPUT_DATATYPE', '')
        )

        c_dict['FCST_INPUT_DIR'] = (
            self.config.getdir('FCST_POINT_STAT_INPUT_DIR','')
        )

        c_dict['OBS_INPUT_DIR'] = (
            self.config.getdir('OBS_POINT_STAT_INPUT_DIR','')
        )

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('POINT_STAT_OUTPUT_DIR', '')
        )

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'POINT_STAT_OUTPUT_TEMPLATE')
        )

        # get climatology config variables
        self.handle_climo_dict()

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('PointStatConfig_wrapped')

        self.add_met_config_window('obs_window')
        self.handle_obs_window_legacy(c_dict)

        self.add_met_config(name='grid',
                            data_type='list',
                            env_var_name='METPLUS_MASK_GRID',
                            metplus_configs=['POINT_STAT_MASK_GRID',
                                             'POINT_STAT_GRID'],
                            extra_args={'allow_empty': True})

        self.add_met_config(name='poly',
                            data_type='list',
                            env_var_name='METPLUS_MASK_POLY',
                            metplus_configs=['POINT_STAT_MASK_POLY',
                                             'POINT_STAT_POLY'],
                            extra_args={'allow_empty': True})

        self.add_met_config(name='sid',
                            data_type='list',
                            env_var_name='METPLUS_MASK_SID',
                            metplus_configs=['POINT_STAT_MASK_SID',
                                             'POINT_STAT_STATION_ID'],
                            extra_args={'allow_empty': True})

        self.add_met_config(name='llpnt',
                            data_type='list',
                            env_var_name='METPLUS_MASK_LLPNT',
                            metplus_configs=['POINT_STAT_MASK_LLPNT'],
                            extra_args={'allow_empty': True,
                                        'remove_quotes': True})

        self.add_met_config(name='message_type',
                            data_type='list')

        self.handle_climo_cdf_dict()

        c_dict['OBS_VALID_BEG'] = (
            self.config.getraw('config', 'POINT_STAT_OBS_VALID_BEG', '')
        )
        c_dict['OBS_VALID_END'] = (
            self.config.getraw('config', 'POINT_STAT_OBS_VALID_END', '')
        )

        c_dict['MASK_POLY_TEMPLATE'] = self.read_mask_poly()

        c_dict['FCST_PROB_THRESH'] = (
            self.config.getstr('config',
                               'FCST_POINT_STAT_PROB_THRESH', '==0.1')
        )
        c_dict['OBS_PROB_THRESH'] = (
            self.config.getstr('config',
                               'OBS_POINT_STAT_PROB_THRESH', '==0.1')
        )

        c_dict['ONCE_PER_FIELD'] = (
            self.config.getbool('config',
                                'POINT_STAT_ONCE_PER_FIELD',
                                False)
        )

        self.add_met_config(name='obs_quality_inc',
                            data_type='list',
                            metplus_configs=['POINT_STAT_OBS_QUALITY_INC',
                                             'POINT_STAT_OBS_QUALITY_INCLUDE',
                                             'POINT_STAT_OBS_QUALITY'])
        self.add_met_config(name='obs_quality_exc',
                            data_type='list',
                            metplus_configs=['POINT_STAT_OBS_QUALITY_EXC',
                                             'POINT_STAT_OBS_QUALITY_EXCLUDE'])

        self.handle_flags('output')

        self.handle_interp_dict()

        self.add_met_config(
            name='time_interp_method',
            data_type='string',
            env_var_name='CLIMO_MEAN_TIME_INTERP_METHOD',
            metplus_configs=['POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD'],
            extra_args={'remove_quotes': True,
                        'uppercase': True,
                        },
        )
        self.add_met_config(
            name='time_interp_method',
            data_type='string',
            env_var_name='CLIMO_STDEV_TIME_INTERP_METHOD',
            metplus_configs=['POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD'],
            extra_args={'remove_quotes': True,
                        'uppercase': True,
                        },
        )

        self.add_met_config(name='hss_ec_value',
                            data_type='float',
                            metplus_configs=['POINT_STAT_HSS_EC_VALUE'])

        self.add_met_config_dict('hira', {
            'flag': 'bool',
            'width': ('list', 'remove_quotes'),
            'vld_thresh': 'float',
            'cov_thresh': ('list', 'remove_quotes'),
            'shape': ('string', 'remove_quotes, uppercase'),
            'prob_cat_thresh': ('list', 'remove_quotes'),
        })

        self.add_met_config(name='message_type_group_map',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error('Must set FCST_POINT_STAT_INPUT_TEMPLATE '
                           'in config file')

        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error('Must set OBS_POINT_STAT_INPUT_TEMPLATE '
                           'in config file')

        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set POINT_STAT_OUTPUT_DIR in config file')

        return c_dict

    def add_obs_valid_args(self, time_info):
        for ext in ['BEG', 'END']:
            if self.c_dict[f'OBS_VALID_{ext}']:
                obs_valid = do_string_sub(self.c_dict[f'OBS_VALID_{ext}'],
                                          **time_info)
                self.args.append(f"-obs_valid_{ext.lower()} {obs_valid}")

    def set_environment_variables(self, time_info=None):
        """! Set all the environment variables in the MET config
             file to the corresponding values in the METplus config file.

             Args:

             Returns: None - invokes parent class, CommandBuilder add_env_var
                             to add each environment variable to run the

        """
        # handle old method of setting env vars in MET config files
        # pull out value after equals sign before the last semi-colon of
        # each value. If not set, then set the value to an empty string
        point_stat_poly = self.get_env_var_value('METPLUS_MASK_POLY')
        if not point_stat_poly:
            point_stat_poly = '[]'
        point_stat_grid = self.get_env_var_value('METPLUS_MASK_GRID')
        if not point_stat_grid:
            point_stat_grid = '[]'
        point_stat_sid = self.get_env_var_value('METPLUS_MASK_SID')
        if not point_stat_sid:
            point_stat_sid = '[]'

        point_stat_message_type = (
            self.get_env_var_value('METPLUS_MESSAGE_TYPE')
        )

        if not point_stat_message_type:
            point_stat_message_type = '[]'

        self.add_env_var('POINT_STAT_POLY',
                         point_stat_poly)

        self.add_env_var('POINT_STAT_GRID',
                         point_stat_grid)

        self.add_env_var('POINT_STAT_STATION_ID',
                         point_stat_sid)

        self.add_env_var('POINT_STAT_MESSAGE_TYPE',
                         point_stat_message_type)

        # add old method of setting env vars
        self.add_env_var("FCST_FIELD",
                         self.c_dict.get('FCST_FIELD', ''))
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))

        # Set the environment variables corresponding to the obs_window
        # dictionary.
        self.add_env_var('OBS_WINDOW_BEGIN',
                         str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var('OBS_WINDOW_END', str(self.c_dict['OBS_WINDOW_END']))

        # add additional env vars if they are specified
        self.add_env_var('VERIF_MASK',
                         self.c_dict.get('VERIFICATION_MASK', ''))

        super().set_environment_variables(time_info)
