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
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_MASK_DICT',
        'METPLUS_NBRHD_SHAPE',
        'METPLUS_NBRHD_WIDTH',
        'METPLUS_NBRHD_COV_THRESH',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_CLIMO_CDF_DICT',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_NC_PAIRS_FLAG_DICT',
        'METPLUS_INTERP_DICT',
        'METPLUS_NC_PAIRS_VAR_NAME',
        'METPLUS_GRID_WEIGHT_FLAG',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_OBS_FILE_TYPE',
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
                    'eclv',
                    'nbrctc',
                    'nbrcts',
                    'nbrcnt',
                    'grad',
                    'dmap',
                    ]

    NC_PAIRS_FLAGS = ['latlon',
                      'raw',
                      'diff',
                      'climo',
                      'climo_cdp',
                      'weight',
                      'nbrhd',
                      'fourier',
                      'gradient',
                      'distance_map',
                      'apply_mask',
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
        self.handle_climo_dict()

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

        self.handle_mask(single_value=False)

        # handle setting VERIFICATION_MASK for old wrapped MET config files
        c_dict['MASK_POLY_TEMPLATE'] = self.read_mask_poly()

        self.handle_climo_cdf_dict()

        self.handle_flags('output')
        self.handle_flags('nc_pairs')

        self.handle_interp_dict(uses_field=True)

        self.add_met_config(name='nc_pairs_var_name',
                            data_type='string',
                            metplus_configs=['GRID_STAT_NC_PAIRS_VAR_NAME'])

        self.add_met_config(name='grid_weight_flag',
                            data_type='string',
                            metplus_configs=['GRID_STAT_GRID_WEIGHT_FLAG'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type',
                            data_type='string',
                            env_var_name='FCST_FILE_TYPE',
                            metplus_configs=['GRID_STAT_FCST_FILE_TYPE',
                                             'FCST_GRID_STAT_FILE_TYPE',
                                             'GRID_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type',
                            data_type='string',
                            env_var_name='OBS_FILE_TYPE',
                            metplus_configs=['GRID_STAT_OBS_FILE_TYPE',
                                             'OBS_GRID_STAT_FILE_TYPE',
                                             'GRID_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})


        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that are referenced by the
            MET config file"""
        # set environment variables needed for MET application

        # add old method of setting env vars
        self.add_env_var("FCST_FIELD",
                         self.c_dict.get('FCST_FIELD', ''))
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))

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
