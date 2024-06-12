'''
Program Name: mode_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

import os

from ..util import do_string_sub
from . import CompareGriddedWrapper

class MODEWrapper(CompareGriddedWrapper):
    """!Wrapper for the mode MET tool"""

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_OBTYPE',
        'METPLUS_REGRID_DICT',
        'METPLUS_QUILT',
        'METPLUS_FCST_FIELD',
        'METPLUS_FCST_CONV_RADIUS',
        'METPLUS_FCST_CONV_THRESH',
        'METPLUS_FCST_MERGE_THRESH',
        'METPLUS_FCST_MERGE_FLAG',
        'METPLUS_FCST_FILTER_ATTR_NAME',
        'METPLUS_FCST_FILTER_ATTR_THRESH',
        'METPLUS_FCST_CENSOR_THRESH',
        'METPLUS_FCST_CENSOR_VAL',
        'METPLUS_FCST_VLD_THRESH',
        'METPLUS_OBS_FIELD',
        'METPLUS_OBS_CONV_RADIUS',
        'METPLUS_OBS_CONV_THRESH',
        'METPLUS_OBS_MERGE_THRESH',
        'METPLUS_OBS_MERGE_FLAG',
        'METPLUS_OBS_FILTER_ATTR_NAME',
        'METPLUS_OBS_FILTER_ATTR_THRESH',
        'METPLUS_OBS_CENSOR_THRESH',
        'METPLUS_OBS_CENSOR_VAL',
        'METPLUS_OBS_VLD_THRESH',
        'METPLUS_MASK_DICT',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_GRID_RES',
        'METPLUS_MASK_MISSING_FLAG',
        'METPLUS_MATCH_FLAG',
        'METPLUS_WEIGHT_DICT',
        'METPLUS_NC_PAIRS_FLAG_DICT',
        'METPLUS_MAX_CENTROID_DIST',
        'METPLUS_TOTAL_INTEREST_THRESH',
        'METPLUS_INTEREST_FUNCTION_CENTROID_DIST',
        'METPLUS_INTEREST_FUNCTION_BOUNDARY_DIST',
        'METPLUS_INTEREST_FUNCTION_CONVEX_HULL_DIST',
        'METPLUS_PS_PLOT_FLAG',
        'METPLUS_CT_STATS_FLAG',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_MULTIVAR_LOGIC',
        'METPLUS_MULTIVAR_INTENSITY_COMPARE_FCST',
        'METPLUS_MULTIVAR_INTENSITY_COMPARE_OBS',
        'METPLUS_FCST_MULTIVAR_NAME',
        'METPLUS_FCST_MULTIVAR_LEVEL',
        'METPLUS_OBS_MULTIVAR_NAME',
        'METPLUS_OBS_MULTIVAR_LEVEL',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'MODEL',
        'OBTYPE',
        'REGRID_TO_GRID',
        'VERIF_MASK',
        'FCST_FIELD',
        'OBS_FIELD',
        'QUILT',
        'FCST_CONV_RADIUS',
        'OBS_CONV_RADIUS',
        'FCST_CONV_THRESH',
        'OBS_CONV_THRESH',
        'FCST_MERGE_THRESH',
        'OBS_MERGE_THRESH',
        'FCST_MERGE_FLAG',
        'OBS_MERGE_FLAG',
        'OUTPUT_PREFIX',
    ]

    WEIGHTS = {
        'centroid_dist': 'float',
        'boundary_dist': 'float',
        'convex_hull_dist': 'float',
        'angle_diff': 'float',
        'aspect_diff': 'float',
        'area_ratio': 'float',
        'int_area_ratio': 'float',
        'curvature_ratio': 'float',
        'complexity_ratio': 'float',
        'inten_perc_ratio': 'float',
        'inten_perc_value': 'int',
    }

    NC_PAIRS_FLAGS = [
        'latlon',
        'raw',
        'object_raw',
        'object_id',
        'cluster_id',
        'polylines',
    ]

    DEFAULT_VALUES = {
        'FCST_CONV_RADIUS': '60.0/grid_res',
        'OBS_CONV_RADIUS': '60.0/grid_res',
        'MAX_CENTROID_DIST': '800.0/grid_res',
        'INTEREST_FUNCTION_CENTROID_DIST': ('((0.0,1.0)'
                                            '(60.0/grid_res,1.0)'
                                            '(600.0/grid_res,0.0))'),
        'INTEREST_FUNCTION_BOUNDARY_DIST': ('((0.0,1.0)'
                                            '(400.0/grid_res,0.0))'),
        'INTEREST_FUNCTION_CONVEX_HULL_DIST': ('((0.0,1.0)'
                                               '(400.0/grid_res,0.0))'),
    }

    def __init__(self, config, instance=None):
        self.app_name = 'mode'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def set_command_line_arguments(self, time_info):
        """!If merge config file is defined, add it to the command"""
        if self.c_dict['MERGE_CONFIG_FILE']:
            merge_config_file = do_string_sub(self.c_dict['MERGE_CONFIG_FILE'],
                                              **time_info)
            self.args.append('-config_merge {}'.format(merge_config_file))

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # variable to substitute for wrapper name, i.e. MODE
        tool = self.app_name.upper()

        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 f'LOG_{tool}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('MODEConfig_wrapped')

        # MODE can only process a single pair of fcst/obs fields at a time
        # unless it is a multi-variate MODE run
        mv_logic = self.config.getstr('config', f'{tool}_MULTIVAR_LOGIC', '')
        if not mv_logic:
            c_dict['ONCE_PER_FIELD'] = True
            c_dict['ALLOW_MULTIPLE_FILES'] = False
        else:
            c_dict['ONCE_PER_FIELD'] = False
            c_dict['ALLOW_MULTIPLE_FILES'] = True
            self.add_met_config(name='multivar_logic', data_type='string')
            self.logger.info(f'{tool}_MULTIVAR_LOGIC was set, so running '
                             'multi-variate MODE')

        # observation input file info
        c_dict['OBS_INPUT_DIR'] = (
            self.config.getdir(f'OBS_{tool}_INPUT_DIR', '')
        )
        c_dict['OBS_INPUT_TEMPLATE'] = (
          self.config.getraw('config', f'OBS_{tool}_INPUT_TEMPLATE')
        )
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error(f'OBS_{tool}_INPUT_TEMPLATE must be set')

        c_dict['OBS_INPUT_DATATYPE'] = (
          self.config.getstr('config', f'OBS_{tool}_INPUT_DATATYPE', '')
        )

        # forecast input file info
        c_dict['FCST_INPUT_DIR'] = (
          self.config.getdir(f'FCST_{tool}_INPUT_DIR', '')
        )
        c_dict['FCST_INPUT_TEMPLATE'] = (
          self.config.getraw('config', f'FCST_{tool}_INPUT_TEMPLATE')
        )
        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error(f'FCST_{tool}_INPUT_TEMPLATE must be set')

        c_dict['FCST_INPUT_DATATYPE'] = (
          self.config.getstr('config', f'FCST_{tool}_INPUT_DATATYPE', '')
        )

        # output info
        c_dict['OUTPUT_DIR'] = self.config.getdir(f'{tool}_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error(f'{tool}_OUTPUT_DIR must be set')

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', f'{tool}_OUTPUT_TEMPLATE')
        )

        self.add_met_config(name='quilt', data_type='bool')

        self.add_met_config(name='grid_res', data_type='float')

        # if MODE_GRID_RES is not set, then unset the default values
        defaults = self.DEFAULT_VALUES.copy()
        if not self.env_var_dict.get('METPLUS_GRID_RES'):
            for default_key in self.DEFAULT_VALUES:
                defaults[default_key] = None

        # read forecast and observation field variables
        for data_type in ['FCST', 'OBS']:
            self.add_met_config(
                name='conv_radius',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_CONV_RADIUS',
                metplus_configs=[f'{data_type}_{tool}_CONV_RADIUS',
                                 f'{tool}_{data_type}_CONV_RADIUS',
                                 f'{tool}_CONV_RADIUS'
                                 ],
                extra_args={
                    'remove_quotes': True,
                    'default': defaults.get(f'{data_type}_CONV_RADIUS')
                }
            )

            self.add_met_config(
                name='conv_thresh',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_CONV_THRESH',
                metplus_configs=[f'{data_type}_{tool}_CONV_THRESH',
                                 f'{tool}_{data_type}_CONV_THRESH',
                                 f'{tool}_CONV_THRESH'
                                 ],
                extra_args={
                    'remove_quotes': True,
                }
            )

            self.add_met_config(
                name='merge_thresh',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_MERGE_THRESH',
                metplus_configs=[f'{data_type}_{tool}_MERGE_THRESH',
                                 f'{tool}_{data_type}_MERGE_THRESH',
                                 f'{tool}_MERGE_THRESH'
                                 ],
                extra_args={
                    'remove_quotes': True,
                }
            )

            self.add_met_config(
                name='merge_flag',
                data_type='string',
                env_var_name=f'METPLUS_{data_type}_MERGE_FLAG',
                metplus_configs=[f'{data_type}_{tool}_MERGE_FLAG',
                                 f'{tool}_{data_type}_MERGE_FLAG',
                                 f'{tool}_MERGE_FLAG'
                                 ],
                extra_args={
                    'remove_quotes': True,
                    'uppercase': True,
                }
            )

            self.add_met_config(
                name='filter_attr_name',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_FILTER_ATTR_NAME',
                metplus_configs=[f'{data_type}_{tool}_FILTER_ATTR_NAME',
                                 f'{tool}_{data_type}_FILTER_ATTR_NAME',
                                 f'{tool}_FILTER_ATTR_NAME'
                                 ],
            )

            self.add_met_config(
                name='filter_attr_thresh',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_FILTER_ATTR_THRESH',
                metplus_configs=[f'{data_type}_{tool}_FILTER_ATTR_THRESH',
                                 f'{tool}_{data_type}_FILTER_ATTR_THRESH',
                                 f'{tool}_FILTER_ATTR_THRESH'
                                 ],
                extra_args={
                    'remove_quotes': True,
                }
            )

            self.add_met_config(
                name='censor_thresh',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_CENSOR_THRESH',
                metplus_configs=[f'{data_type}_{tool}_CENSOR_THRESH',
                                 f'{tool}_{data_type}_CENSOR_THRESH',
                                 f'{tool}_CENSOR_THRESH'
                                 ],
                extra_args={
                    'remove_quotes': True,
                }
            )

            self.add_met_config(
                name='censor_val',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_CENSOR_VAL',
                metplus_configs=[f'{data_type}_{tool}_CENSOR_VAL',
                                 f'{tool}_{data_type}_CENSOR_VAL',
                                 f'{data_type}_{tool}_CENSOR_VALUE',
                                 f'{tool}_{data_type}_CENSOR_VALUE',
                                 f'{tool}_CENSOR_VAL',
                                 f'{tool}_CENSOR_VALUE',
                                 ],
                extra_args={
                    'remove_quotes': True,
                }
            )

            self.add_met_config(
                name='vld_thresh',
                data_type='float',
                env_var_name=f'METPLUS_{data_type}_VLD_THRESH',
                metplus_configs=[f'{data_type}_{tool}_VLD_THRESH',
                                 f'{tool}_{data_type}_VLD_THRESH',
                                 f'{data_type}_{tool}_VALID_THRESH',
                                 f'{tool}_{data_type}_VALID_THRESH',
                                 f'{tool}_VLD_THRESH',
                                 f'{tool}_VALID_THRESH'
                                 ],
            )

        self.add_met_config(
            name='mask_missing_flag',
            data_type='string',
            extra_args={
                'remove_quotes': True,
                'uppercase': True,
            }
        )

        self.add_met_config(
            name='match_flag',
            data_type='string',
            extra_args={
                'remove_quotes': True,
                'uppercase': True,
            }
        )

        self.add_met_config_dict('weight', self.WEIGHTS)
        self.handle_flags('nc_pairs')

        self.add_met_config(name='total_interest_thresh',
                            data_type='float',
                            metplus_configs=[f'{tool}_TOTAL_INTEREST_THRESH'])

        self.add_met_config(
            name='max_centroid_dist',
            data_type='string',
            metplus_configs=[f'{tool}_MAX_CENTROID_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('MAX_CENTROID_DIST')
            }
        )
        self.add_met_config(
            name='centroid_dist',
            data_type='string',
            env_var_name='INTEREST_FUNCTION_CENTROID_DIST',
            metplus_configs=[f'{tool}_INTEREST_FUNCTION_CENTROID_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('INTEREST_FUNCTION_CENTROID_DIST')
            }
        )
        self.add_met_config(
            name='boundary_dist',
            data_type='string',
            env_var_name='INTEREST_FUNCTION_BOUNDARY_DIST',
            metplus_configs=[f'{tool}_INTEREST_FUNCTION_BOUNDARY_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('INTEREST_FUNCTION_BOUNDARY_DIST')
            }
        )
        self.add_met_config(
            name='convex_hull_dist',
            data_type='string',
            env_var_name='INTEREST_FUNCTION_CONVEX_HULL_DIST',
            metplus_configs=[f'{tool}_INTEREST_FUNCTION_CONVEX_HULL_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('INTEREST_FUNCTION_CONVEX_HULL_DIST')
            }
        )

        self.add_met_config(name='ps_plot_flag', data_type='bool')
        self.add_met_config(name='ct_stats_flag', data_type='bool')

        self.add_met_config(name='file_type',
                            data_type='string',
                            env_var_name='FCST_FILE_TYPE',
                            metplus_configs=[f'{tool}_FCST_FILE_TYPE',
                                             f'FCST_{tool}_FILE_TYPE',
                                             f'{tool}_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type',
                            data_type='string',
                            env_var_name='OBS_FILE_TYPE',
                            metplus_configs=[f'{tool}_OBS_FILE_TYPE',
                                             f'OBS_{tool}_FILE_TYPE',
                                             f'{tool}_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='multivar_name', data_type='string',
                            env_var_name='FCST_MULTIVAR_NAME',
                            metplus_configs=[f'{tool}_FCST_MULTIVAR_NAME'])
        self.add_met_config(name='multivar_level', data_type='string',
                            env_var_name='FCST_MULTIVAR_LEVEL',
                            metplus_configs=[f'{tool}_FCST_MULTIVAR_LEVEL'])

        self.add_met_config(name='multivar_name', data_type='string',
                            env_var_name='OBS_MULTIVAR_NAME',
                            metplus_configs=[f'{tool}_OBS_MULTIVAR_NAME'])
        self.add_met_config(name='multivar_level', data_type='string',
                            env_var_name='OBS_MULTIVAR_LEVEL',
                            metplus_configs=[f'{tool}_OBS_MULTIVAR_LEVEL'])

        c_dict['MERGE_CONFIG_FILE'] = (
            self.config.getraw('config', f'{tool}_MERGE_CONFIG_FILE', '')
            )

        self.handle_mask(single_value=True, get_flags=True)

        self.add_met_config(name='multivar_intensity_compare_fcst',
                            data_type='list',
                            extra_args={'remove_quotes': True})
        self.add_met_config(name='multivar_intensity_compare_obs',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

    def run_at_time_one_field(self, time_info, var_info):
        """! Runs mode once for each fcst/obs threshold.
         Overrides run_at_time_one_field function in compare_gridded_wrapper.py

            @param time_info dictionary containing timing information
            @param var_info object containing variable information
        """
        # if no thresholds are specified, run once
        fcst_thresh_list = []
        obs_thresh_list = []

        # if probabilistic forecast and no thresholds specified, error and skip
        if self.c_dict['FCST_IS_PROB']:

            # set thresholds for fcst and obs if prob
            fcst_thresh_list = var_info['fcst_thresh']
            obs_thresh_list = var_info['obs_thresh']

        fcst_field_list = self.get_field_info(v_name=var_info['fcst_name'],
                                              v_level=var_info['fcst_level'],
                                              v_extra=var_info['fcst_extra'],
                                              v_thresh=fcst_thresh_list,
                                              d_type='FCST')

        obs_field_list = self.get_field_info(v_name=var_info['obs_name'],
                                             v_level=var_info['obs_level'],
                                             v_extra=var_info['obs_extra'],
                                             v_thresh=obs_thresh_list,
                                             d_type='OBS')

        if fcst_field_list is None or obs_field_list is None:
            return

        # loop through fields and call MODE
        for fcst_field, obs_field in zip(fcst_field_list, obs_field_list):
            self.clear(clear_input_files=False)
            self.format_field('FCST', fcst_field, is_list=False)
            self.format_field('OBS', obs_field, is_list=False)
            self.param = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
            self.set_command_line_arguments(time_info)
            self.set_current_field_config(var_info)
            self.set_environment_variables(time_info)
            if not self.find_and_check_output_file(time_info,
                                                   is_directory=True):
                return

            self.build()
