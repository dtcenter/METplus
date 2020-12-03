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
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_MODE_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['CONFIG_FILE'] = self.config.getraw('config', 'MODE_CONFIG_FILE', '')
        if not c_dict['CONFIG_FILE']:
            self.log_error('MODE_CONFIG_FILE must be set')
            self.isOK = False

        c_dict['OBS_INPUT_DIR'] = \
          self.config.getdir('OBS_MODE_INPUT_DIR', '')
        c_dict['OBS_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'OBS_MODE_INPUT_TEMPLATE')
        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error('OBS_MODE_INPUT_TEMPLATE must be set')
            self.isOK = False

        c_dict['OBS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_MODE_INPUT_DATATYPE', '')
        c_dict['FCST_INPUT_DIR'] = \
          self.config.getdir('FCST_MODE_INPUT_DIR', '')
        c_dict['FCST_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'FCST_MODE_INPUT_TEMPLATE')
        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error('OBS_MODE_INPUT_TEMPLATE must be set')
            self.isOK = False

        c_dict['FCST_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'FCST_MODE_INPUT_DATATYPE', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('MODE_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error('MODE_OUTPUT_DIR must be set')
            self.isOK = False

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'MODE_OUTPUT_TEMPLATE')
        )

        c_dict['ONCE_PER_FIELD'] = True
        c_dict['QUILT'] = self.config.getbool('config', 'MODE_QUILT', False)
        fcst_conv_radius, obs_conv_radius = \
            self.handle_fcst_and_obs_field('MODE_CONV_RADIUS',
                                           'FCST_MODE_CONV_RADIUS',
                                           'OBS_MODE_CONV_RADIUS')
        c_dict['FCST_CONV_RADIUS'] = fcst_conv_radius
        c_dict['OBS_CONV_RADIUS'] = obs_conv_radius
        if fcst_conv_radius is None or obs_conv_radius is None:
            self.isOK = False

        fcst_conv_thresh, obs_conv_thresh = self.handle_fcst_and_obs_field('MODE_CONV_THRESH',
                                                                           'FCST_MODE_CONV_THRESH',
                                                                           'OBS_MODE_CONV_THRESH')

        c_dict['FCST_CONV_THRESH'] = fcst_conv_thresh
        c_dict['OBS_CONV_THRESH'] = obs_conv_thresh
        if fcst_conv_thresh is None or obs_conv_thresh is None:
            self.isOK = False

        fcst_merge_thresh, obs_merge_thresh = \
                self.handle_fcst_and_obs_field('MODE_MERGE_THRESH',
                                               'FCST_MODE_MERGE_THRESH',
                                               'OBS_MODE_MERGE_THRESH')
        c_dict['FCST_MERGE_THRESH'] = fcst_merge_thresh
        c_dict['OBS_MERGE_THRESH'] = obs_merge_thresh
        if fcst_merge_thresh is None or obs_merge_thresh is None:
            self.isOK = False

        fcst_merge_flag, obs_merge_flag = \
                self.handle_fcst_and_obs_field('MODE_MERGE_FLAG',
                                               'FCST_MODE_MERGE_FLAG',
                                               'OBS_MODE_MERGE_FLAG')

        c_dict['FCST_MERGE_FLAG'] = fcst_merge_flag
        c_dict['OBS_MERGE_FLAG'] = obs_merge_flag
        if fcst_merge_flag is None or obs_merge_flag is None:
            self.isOK = False

        c_dict['ALLOW_MULTIPLE_FILES'] = False

        c_dict['MERGE_CONFIG_FILE'] = self.config.getraw('config', 'MODE_MERGE_CONFIG_FILE', '')

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'mode')

        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'MODE_VERIFICATION_MASK_TEMPLATE')

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'MODE_REGRID_TO_GRID', '')

        # check that values are valid
        error_message = 'items must start with a comparison operator '+\
                        '(>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)'
        if not util.validate_thresholds(util.getlist(c_dict['FCST_CONV_THRESH'])):
            self.log_error('MODE_FCST_CONV_THRESH {}'.format(error_message))
            self.isOK = False
        if not util.validate_thresholds(util.getlist(c_dict['OBS_CONV_THRESH'])):
            self.log_error('MODE_OBS_CONV_THRESH {}'.format(error_message))
            self.isOK = False
        if not util.validate_thresholds(util.getlist(c_dict['FCST_MERGE_THRESH'])):
            self.log_error('MODE_FCST_MERGE_THRESH {}'.format(error_message))
            self.isOK = False
        if not util.validate_thresholds(util.getlist(c_dict['OBS_MERGE_THRESH'])):
            self.log_error('MODE_OBS_MERGE_THRESH {}'.format(error_message))
            self.isOK = False

        return c_dict

    def set_environment_variables(self, fcst_field, obs_field, time_info):
        self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)

        quilt = 'TRUE' if self.c_dict['QUILT'] else 'FALSE'

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

        self.add_env_var('OUTPUT_PREFIX', self.get_output_prefix(time_info))

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
            self.param = do_string_sub(self.c_dict['CONFIG_FILE'],
                                       **time_info)

            self.infiles.append(model_path)
            self.infiles.append(obs_path)
            self.add_merge_config_file(time_info)
            self.set_current_field_config(var_info)
            self.set_environment_variables(fcst_field, obs_field, time_info)
            if not self.find_and_check_output_file(time_info,
                                                   is_directory=True):
                return

            self.build()
            self.clear()
