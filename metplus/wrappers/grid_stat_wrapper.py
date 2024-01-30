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

from . import CompareGriddedWrapper

# pylint:disable=pointless-string-statement
"""!@namespace GridStatWrapper
@brief Wraps the MET tool grid_stat to compare gridded datasets
@endcode
"""


class GridStatWrapper(CompareGriddedWrapper):
    """!Wraps the MET tool grid_stat to compare gridded datasets"""

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

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
        'METPLUS_HSS_EC_VALUE',
        'METPLUS_DISTANCE_MAP_DICT',
        'METPLUS_FOURIER_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_SEEPS_P1_THRESH',
        'METPLUS_CAT_THRESH',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'MODEL',
        'OBTYPE',
        'REGRID_TO_GRID',
        'CLIMO_MEAN_FILE',
        'CLIMO_STDEV_FILE',
        'VERIF_MASK',
        'FCST_FIELD',
        'OBS_FIELD',
        'FCST_TIME',
        'INPUT_BASE',
        'NEIGHBORHOOD_WIDTH',
        'NEIGHBORHOOD_SHAPE',
        'NEIGHBORHOOD_COV_THRESH',
        'OUTPUT_PREFIX',
    ]

    OUTPUT_FLAGS = [
        'fho',
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
        'seeps',
    ]

    NC_PAIRS_FLAGS = [
        'latlon',
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
        'seeps',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'grid_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GRID_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('GridStatConfig_wrapped')

        self.get_input_templates(c_dict, [('FCST_GRID_STAT', 'FCST'),
                                          ('OBS_GRID_STAT', 'OBS')])

        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("OBS_GRID_STAT_INPUT_TEMPLATE required to run")

        c_dict['OBS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_GRID_STAT_INPUT_DATATYPE', '')

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

        self.add_met_config(name='cov_thresh', data_type='list',
                            env_var_name='METPLUS_NBRHD_COV_THRESH',
                            metplus_configs=[
                                'GRID_STAT_NEIGHBORHOOD_COV_THRESH'
                            ],
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='width', data_type='list',
                            env_var_name='METPLUS_NBRHD_WIDTH',
                            metplus_configs=[
                                'GRID_STAT_NEIGHBORHOOD_WIDTH'
                            ],
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='shape', data_type='string',
                            env_var_name='METPLUS_NBRHD_SHAPE',
                            metplus_configs=[
                                'GRID_STAT_NEIGHBORHOOD_SHAPE'
                            ],
                            extra_args={'remove_quotes': True})

        # handle legacy environment variables used by old MET configs
        c_dict['NEIGHBORHOOD_WIDTH'] = (
            self.config.getstr('config',
                               'GRID_STAT_NEIGHBORHOOD_WIDTH', '1')
        )
        c_dict['NEIGHBORHOOD_SHAPE'] = (
            self.config.getstr('config',
                               'GRID_STAT_NEIGHBORHOOD_SHAPE', 'SQUARE')
        )

        self.handle_mask(single_value=False)

        self.handle_climo_cdf_dict()

        self.handle_flags('output')
        self.handle_flags('nc_pairs')

        self.handle_interp_dict(uses_field=True)

        self.add_met_config(name='nc_pairs_var_name', data_type='string',
                            metplus_configs=['GRID_STAT_NC_PAIRS_VAR_NAME'])

        self.add_met_config(name='grid_weight_flag', data_type='string',
                            metplus_configs=['GRID_STAT_GRID_WEIGHT_FLAG'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='FCST_FILE_TYPE',
                            metplus_configs=['GRID_STAT_FCST_FILE_TYPE',
                                             'FCST_GRID_STAT_FILE_TYPE',
                                             'GRID_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='OBS_FILE_TYPE',
                            metplus_configs=['GRID_STAT_OBS_FILE_TYPE',
                                             'OBS_GRID_STAT_FILE_TYPE',
                                             'GRID_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='hss_ec_value', data_type='float',
                            metplus_configs=['GRID_STAT_HSS_EC_VALUE'])

        self.add_met_config_dict('distance_map', {
            'baddeley_p': 'int',
            'baddeley_max_dist': 'float',
            'fom_alpha': 'float',
            'zhu_weight': 'float',
            'beta_value(n)': ('string', 'remove_quotes'),
        })

        self.add_met_config_dict('fourier', {
            'wave_1d_beg': ('list', 'remove_quotes'),
            'wave_1d_end': ('list', 'remove_quotes'),
        })

        self.add_met_config(name='censor_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='censor_val', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='cat_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='seeps_p1_thresh', data_type='string',
                            extra_args={'remove_quotes': True})
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict
