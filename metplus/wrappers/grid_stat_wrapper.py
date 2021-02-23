'''
Program Name: grid_stat_wrapper.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

import os

from ..util import met_util as util
from . import CompareGriddedWrapper

# pylint:disable=pointless-string-statement
"""!@namespace GridStatWrapper
@brief Wraps the MET tool grid_stat to compare gridded datasets
@endcode
"""

class GridStatWrapper(CompareGriddedWrapper):
    '''!Wraps the MET tool grid_stat to compare gridded datasets
    '''

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_OBTYPE',
        'METPLUS_REGRID_DICT',
        'METPLUS_FCST_FIELD',
        'METPLUS_OBS_FIELD',
        'METPLUS_CLIMO_MEAN_FILE',
        'METPLUS_CLIMO_STDEV_FILE',
        'METPLUS_MASK_DICT',
        'METPLUS_NBRHD_SHAPE',
        'METPLUS_NBRHD_WIDTH',
        'METPLUS_NBRHD_COV_THRESH',
        'METPLUS_OUTPUT_PREFIX',
    ]

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'grid_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GRID_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['CONFIG_FILE'] = self.config.getraw('config',
                                                   'GRID_STAT_CONFIG_FILE', '')
        c_dict['OBS_INPUT_DIR'] = \
          self.config.getdir('OBS_GRID_STAT_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'OBS_GRID_STAT_INPUT_TEMPLATE')
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("OBS_GRID_STAT_INPUT_TEMPLATE required to run")

        c_dict['OBS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_GRID_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DIR'] = \
          self.config.getdir('FCST_GRID_STAT_INPUT_DIR', '')
        c_dict['FCST_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'FCST_GRID_STAT_INPUT_TEMPLATE')

        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error("FCST_GRID_STAT_INPUT_TEMPLATE required to run")

        c_dict['FCST_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'FCST_GRID_STAT_INPUT_DATATYPE', '')

        # get climatology config variables
        self.read_climo_wrapper_specific('GRID_STAT', c_dict)

        c_dict['OUTPUT_DIR'] = self.config.getdir('GRID_STAT_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set GRID_STAT_OUTPUT_DIR")

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'GRID_STAT_OUTPUT_TEMPLATE')
        )
        c_dict['ONCE_PER_FIELD'] = (
            self.config.getbool('config',
                                'GRID_STAT_ONCE_PER_FIELD',
                                False)
        )
        c_dict['FCST_PROB_THRESH'] = (
            self.config.getstr('config',
                               'FCST_GRID_STAT_PROB_THRESH', '==0.1')
        )
        c_dict['OBS_PROB_THRESH'] = (
            self.config.getstr('config',
                               'OBS_GRID_STAT_PROB_THRESH', '==0.1')
        )

        c_dict['ALLOW_MULTIPLE_FILES'] = False


        self.set_met_config_list(self.env_var_dict,
                                 f'GRID_STAT_NEIGHBORHOOD_COV_THRESH',
                                 'cov_thresh',
                                 'METPLUS_NBRHD_COV_THRESH',
                                 remove_quotes=True)

        self.set_met_config_list(self.env_var_dict,
                                 f'GRID_STAT_NEIGHBORHOOD_WIDTH',
                                 'width',
                                 'METPLUS_NBRHD_WIDTH',
                                 remove_quotes=True)

        self.set_met_config_string(self.env_var_dict,
                                   'GRID_STAT_NEIGHBORHOOD_SHAPE',
                                   'shape',
                                   'METPLUS_NBRHD_SHAPE',
                                   remove_quotes=True)

        c_dict['NEIGHBORHOOD_WIDTH'] = (
            self.config.getstr('config',
                               'GRID_STAT_NEIGHBORHOOD_WIDTH', '1')
        )
        c_dict['NEIGHBORHOOD_SHAPE'] = (
            self.config.getstr('config',
                               'GRID_STAT_NEIGHBORHOOD_SHAPE', 'SQUARE')
        )


        self.set_met_config_list(c_dict,
                                 'GRID_STAT_MASK_GRID',
                                 'grid',
                                 'MASK_GRID',
                                 allow_empty=True)

        c_dict['MASK_POLY_TEMPLATE'] = self.read_mask_poly()

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that are referenced by the
            MET config file"""
        # set environment variables needed for MET application

        mask_dict_string = self.format_met_config_dict(self.c_dict,
                                                       'mask',
                                                       ['MASK_GRID',
                                                        'MASK_POLY'])
        self.env_var_dict["METPLUS_MASK_DICT"] = mask_dict_string

        # add old method of setting env vars
        self.add_env_var("FCST_FIELD",
                         self.c_dict.get('FCST_FIELD', ''))
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))

        # set climatology environment variables
        self.set_climo_env_vars()

        self.add_env_var("FCST_TIME", str(time_info['lead_hours']).zfill(3))
        self.add_env_var("INPUT_BASE", self.c_dict["INPUT_BASE"])

        self.add_env_var('NEIGHBORHOOD_WIDTH',
                         self.c_dict['NEIGHBORHOOD_WIDTH'])

        self.add_env_var('NEIGHBORHOOD_SHAPE',
                         self.c_dict['NEIGHBORHOOD_SHAPE'])

        self.add_env_var('NEIGHBORHOOD_COV_THRESH',
                         self.c_dict.get('NBRHD_COV_THRESH', ''))

        self.add_env_var('VERIF_MASK',
                         self.c_dict.get('VERIFICATION_MASK', ''))

        super().set_environment_variables(time_info)
