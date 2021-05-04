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

from ..util import met_util as util
from . import CompareGriddedWrapper
from ..util import do_string_sub

class MODEWrapper(CompareGriddedWrapper):
    """!Wrapper for the mode MET tool"""

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
        'METPLUS_MATCH_FLAG',
        'METPLUS_WEIGHT_DICT',
        'METPLUS_NC_PAIRS_FLAG_DICT',
        'METPLUS_MAX_CENTROID_DIST',
        'METPLUS_TOTAL_INTEREST_THRESH',
        'METPLUS_INTEREST_FUNCTION_CENTROID_DIST',
        'METPLUS_INTEREST_FUNCTION_BOUNDARY_DIST',
        'METPLUS_INTEREST_FUNCTION_CONVEX_HULL_DIST',
    ]

    WEIGHTS = [
        ('centroid_dist', 'float'),
        ('boundary_dist', 'float'),
        ('convex_hull_dist', 'float'),
        ('angle_diff', 'float'),
        ('aspect_diff', 'float'),
        ('area_ratio', 'float'),
        ('int_area_ratio', 'float'),
        ('curvature_ratio', 'float'),
        ('complexity_ratio', 'float'),
        ('inten_perc_ratio', 'float'),
        ('inten_perc_value', 'int'),
    ]

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

    def __init__(self, config, instance=None, config_overrides={}):
        # only set app variables if not already set by MTD (subclass)
        if not hasattr(self, 'app_name'):
            self.app_name = 'mode'
            self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                         self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def add_merge_config_file(self, time_info):
        """!If merge config file is defined, add it to the command"""
        if self.c_dict['MERGE_CONFIG_FILE'] != '':
            merge_config_file = do_string_sub(self.c_dict['MERGE_CONFIG_FILE'],
                                              **time_info)
            self.args.append('-config_merge {}'.format(merge_config_file))

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_MODE_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['CONFIG_FILE'] = self.config.getraw('config',
                                                   'MODE_CONFIG_FILE',
                                                   '')
        if not c_dict['CONFIG_FILE']:
            self.log_error('MODE_CONFIG_FILE must be set')

        c_dict['OBS_INPUT_DIR'] = \
          self.config.getdir('OBS_MODE_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'OBS_MODE_INPUT_TEMPLATE')
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error('OBS_MODE_INPUT_TEMPLATE must be set')

        c_dict['OBS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_MODE_INPUT_DATATYPE', '')
        c_dict['FCST_INPUT_DIR'] = \
          self.config.getdir('FCST_MODE_INPUT_DIR', '')
        c_dict['FCST_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'FCST_MODE_INPUT_TEMPLATE')
        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error('OBS_MODE_INPUT_TEMPLATE must be set')

        c_dict['FCST_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'FCST_MODE_INPUT_DATATYPE', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('MODE_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error('MODE_OUTPUT_DIR must be set')

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'MODE_OUTPUT_TEMPLATE')
        )

        c_dict['ONCE_PER_FIELD'] = True
        self.set_met_config_bool(self.env_var_dict,
                                 'MODE_QUILT',
                                 'quilt',
                                 'METPLUS_QUILT')

        self.set_met_config_float(self.env_var_dict,
                                  'MODE_GRID_RES',
                                  'grid_res',
                                  'METPLUS_GRID_RES')

        # if MODE_GRID_RES is not set, then unset the default values
        defaults = self.DEFAULT_VALUES.copy()
        if not self.env_var_dict.get('METPLUS_GRID_RES'):
            for default_key in self.DEFAULT_VALUES:
                defaults[default_key] = None

        # read forecast and observation field variables
        for data_type in ['FCST', 'OBS']:
            self.set_met_config_list(
                self.env_var_dict,
                [f'{data_type}_MODE_CONV_RADIUS',
                 f'MODE_{data_type}_CONV_RADIUS',
                 'MODE_CONV_RADIUS'],
                'conv_radius',
                f'METPLUS_{data_type}_CONV_RADIUS',
                remove_quotes=True,
                default=defaults.get(f'{data_type}_CONV_RADIUS'),
            )

            self.set_met_config_list(self.env_var_dict,
                                     [f'{data_type}_MODE_CONV_THRESH',
                                      f'MODE_{data_type}_CONV_THRESH',
                                      'MODE_CONV_THRESH'],
                                     'conv_thresh',
                                     f'METPLUS_{data_type}_CONV_THRESH',
                                     remove_quotes=True)

            self.set_met_config_list(self.env_var_dict,
                                     [f'{data_type}_MODE_MERGE_THRESH',
                                      f'MODE_{data_type}_MERGE_THRESH',
                                      'MODE_MERGE_THRESH'],
                                     'merge_thresh',
                                     f'METPLUS_{data_type}_MERGE_THRESH',
                                     remove_quotes=True)

            self.set_met_config_string(self.env_var_dict,
                                       [f'{data_type}_MODE_MERGE_FLAG',
                                        f'MODE_{data_type}_MERGE_FLAG',
                                        'MODE_MERGE_FLAG'],
                                       'merge_flag',
                                       f'METPLUS_{data_type}_MERGE_FLAG',
                                       remove_quotes=True,
                                       uppercase=True)

            self.set_met_config_list(self.env_var_dict,
                                     [f'{data_type}_MODE_FILTER_ATTR_NAME',
                                      f'MODE_{data_type}_FILTER_ATTR_NAME',
                                      'MODE_FILTER_ATTR_NAME'],
                                     'filter_attr_name',
                                     f'METPLUS_{data_type}_FILTER_ATTR_NAME')

            self.set_met_config_list(self.env_var_dict,
                                     [f'{data_type}_MODE_FILTER_ATTR_THRESH',
                                      f'MODE_{data_type}_FILTER_ATTR_THRESH',
                                      'MODE_FILTER_ATTR_THRESH'],
                                     'filter_attr_thresh',
                                     f'METPLUS_{data_type}_FILTER_ATTR_THRESH',
                                     remove_quotes=True)

            self.set_met_config_list(self.env_var_dict,
                                     [f'{data_type}_MODE_CENSOR_THRESH',
                                      f'MODE_{data_type}_CENSOR_THRESH',
                                      'MODE_CENSOR_THRESH'],
                                     'censor_thresh',
                                     f'METPLUS_{data_type}_CENSOR_THRESH',
                                     remove_quotes=True)

            self.set_met_config_list(self.env_var_dict,
                                     [f'{data_type}_MODE_CENSOR_VAL',
                                      f'MODE_{data_type}_CENSOR_VAL',
                                      f'{data_type}_MODE_CENSOR_VALUE',
                                      f'MODE_{data_type}_CENSOR_VALUE',
                                      'MODE_CENSOR_VAL',
                                      'MODE_CENSOR_VALUE'],
                                     'censor_val',
                                     f'METPLUS_{data_type}_CENSOR_VAL',
                                     remove_quotes=True)

            self.set_met_config_float(self.env_var_dict,
                                      [f'{data_type}_MODE_VLD_THRESH',
                                       f'{data_type}_MODE_VALID_THRESH',
                                       f'MODE_{data_type}_VLD_THRESH',
                                       f'MODE_{data_type}_VALID_THRESH'],
                                      'vld_thresh',
                                      f'METPLUS_{data_type}_VLD_THRESH')

            # set c_dict values for old method of setting env vars
            for name in ['CONV_RADIUS',
                         'CONV_THRESH',
                         'MERGE_THRESH',
                         'MERGE_FLAG']:
                value = self.get_env_var_value(f'METPLUS_{data_type}_{name}')
                c_dict[f'{data_type}_{name}'] = value

        self.set_met_config_string(self.env_var_dict,
                                   ['MODE_MATCH_FLAG'],
                                   'match_flag',
                                   'METPLUS_MATCH_FLAG',
                                   remove_quotes=True,
                                   uppercase=True)

        self.handle_weight()
        self.handle_flags('nc_pairs')

        self.add_met_config(name='total_interest_thresh',
                            data_type='float',
                            metplus_configs=['MODE_TOTAL_INTEREST_THRESH'])

        self.add_met_config(
            name='max_centroid_dist',
            data_type='string',
            metplus_configs=['MODE_MAX_CENTROID_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('MAX_CENTROID_DIST')
            }
        )
        self.add_met_config(
            name='centroid_dist',
            data_type='string',
            env_var_name='INTEREST_FUNCTION_CENTROID_DIST',
            metplus_configs=['MODE_INTEREST_FUNCTION_CENTROID_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('INTEREST_FUNCTION_CENTROID_DIST')
            }
        )
        self.add_met_config(
            name='boundary_dist',
            data_type='string',
            env_var_name='INTEREST_FUNCTION_BOUNDARY_DIST',
            metplus_configs=['MODE_INTEREST_FUNCTION_BOUNDARY_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('INTEREST_FUNCTION_BOUNDARY_DIST')
            }
        )
        self.add_met_config(
            name='convex_hull_dist',
            data_type='string',
            env_var_name='INTEREST_FUNCTION_CONVEX_HULL_DIST',
            metplus_configs=['MODE_INTEREST_FUNCTION_CONVEX_HULL_DIST'],
            extra_args={
                'remove_quotes': True,
                'default': defaults.get('INTEREST_FUNCTION_CONVEX_HULL_DIST')
            }
        )

        c_dict['ALLOW_MULTIPLE_FILES'] = False

        c_dict['MERGE_CONFIG_FILE'] = (
            self.config.getraw('config',
                               'MODE_MERGE_CONFIG_FILE', '')
            )

        self.handle_mask(single_value=True,
                         get_flags=True)

        # handle setting VERIFICATION_MASK for old wrapped MET config files
        c_dict['MASK_POLY_TEMPLATE'] = self.read_mask_poly()
        c_dict['MASK_POLY_IS_LIST'] = False

        return c_dict

    def handle_weight(self):
        """! Read weight dictionary values and set them into env_var_list

        """
        app = self.app_name.upper()

        dict_name = 'weight'
        dict_items = []

        for name, data_type in self.WEIGHTS:
            dict_items.append(
                self.get_met_config(
                    name=name,
                    data_type=data_type,
                    metplus_configs=[f'{app}_WEIGHT_{name.upper()}'],
                )
            )

        self.handle_met_config_dict(dict_name, dict_items)

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read set when running this
          tool.

            @param time_info dictionary containing timing info for current run
        """

        # support old method of setting env vars in MET config files
        self.add_env_var("FCST_FIELD",
                         self.c_dict.get('FCST_FIELD', ''))
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))

        quilt = self.get_env_var_value('METPLUS_QUILT')
        if not quilt:
            quilt = 'FALSE'

        self.add_env_var("QUILT", quilt)
        self.add_env_var("FCST_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"])
        self.add_env_var("OBS_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"])
        self.add_env_var("FCST_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"])
        self.add_env_var("OBS_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"])
        self.add_env_var("FCST_MERGE_THRESH", self.c_dict["FCST_MERGE_THRESH"])
        self.add_env_var("OBS_MERGE_THRESH", self.c_dict["OBS_MERGE_THRESH"])
        self.add_env_var("FCST_MERGE_FLAG", self.c_dict["FCST_MERGE_FLAG"])
        self.add_env_var("OBS_MERGE_FLAG", self.c_dict["OBS_MERGE_FLAG"])
        self.add_env_var('VERIF_MASK', self.c_dict.get('VERIFICATION_MASK',
                                                       '""'))

        super().set_environment_variables(time_info)

    def run_at_time_one_field(self, time_info, var_info):
        """! Runs mode instances for a given time and forecast lead combination
              Overrides run_at_time_one_field function in compare_gridded_wrapper.py
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
        """
        # get model to compare
        model_path = self.find_model(time_info, var_info)
        if model_path is None:
            return

        # get observation to compare
        obs_path = self.find_obs(time_info, var_info)
        if obs_path is None:
            return

        # loop over all variables and levels (and probability thresholds) and call the app for each
        self.process_fields_one_thresh(time_info, var_info, model_path, obs_path)

    def process_fields_one_thresh(self, time_info, var_info, model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param model_path forecast file
                @param obs_path observation file
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
            self.clear()
            self.format_field('FCST',
                              fcst_field,
                              is_list=False)
            self.format_field('OBS',
                              obs_field,
                              is_list=False)

            self.param = do_string_sub(self.c_dict['CONFIG_FILE'],
                                       **time_info)

            self.infiles.append(model_path)
            self.infiles.append(obs_path)
            self.add_merge_config_file(time_info)
            self.set_current_field_config(var_info)
            self.set_environment_variables(time_info)
            if not self.find_and_check_output_file(time_info,
                                                   is_directory=True):
                return

            self.build()
