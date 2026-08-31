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
from ..util import do_string_sub
from . import CompareGriddedWrapper


class PointStatWrapper(CompareGriddedWrapper):
    """! Wrapper to the MET tool, Point-Stat."""
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_FCST_FIELD',
        'METPLUS_FCST_CLIMO_MEAN_DICT',
        'METPLUS_FCST_CLIMO_STDEV_DICT',
        'METPLUS_OBS_FIELD',
        'METPLUS_OBS_CLIMO_MEAN_DICT',
        'METPLUS_OBS_CLIMO_STDEV_DICT',
        'METPLUS_MESSAGE_TYPE',
        'METPLUS_LAND_MASK_DICT',
        'METPLUS_TOPO_MASK_DICT',
        'METPLUS_LAPSE_RATE_CORRECTION_DICT',
        'METPLUS_MSL_AGL_CONVERSION_DICT',
        'METPLUS_OBS_WINDOW_DICT',
        'METPLUS_MASK_DICT',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_CLIMO_CDF_DICT',
        'METPLUS_OBS_QUALITY_INC',
        'METPLUS_OBS_QUALITY_EXC',
        'METPLUS_DUPLICATE_FLAG',
        'METPLUS_OBS_SUMMARY',
        'METPLUS_OBS_PERC_VALUE',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_INTERP_DICT',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_HSS_EC_VALUE',
        'METPLUS_HIRA_DICT',
        'METPLUS_MESSAGE_TYPE_GROUP_MAP',
        'METPLUS_OBTYPE_AS_GROUP_VAL_FLAG',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_SEEPS_P1_THRESH',
        'METPLUS_UGRID_DATASET',
        'METPLUS_UGRID_MAX_DISTANCE_KM',
        'METPLUS_UGRID_COORDINATES_FILE',
        'METPLUS_POINT_WEIGHT_FLAG',
        'METPLUS_KDE_REF_ANGLE',
        'METPLUS_WRITE_WEIGHTS',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'MODEL',
        'OBTYPE',
        'REGRID_TO_GRID',
        'CLIMO_MEAN_FILE',
        'CLIMO_STDEV_FILE',
        'FCST_FIELD',
        'OBS_FIELD',
        'OBS_WINDOW_BEGIN',
        'OBS_WINDOW_END',
        'POINT_STAT_POLY',
        'POINT_STAT_GRID',
        'POINT_STAT_STATION_ID',
        'POINT_STAT_MESSAGE_TYPE',
        'OUTPUT_PREFIX',
        'METPLUS_MASK_GRID',  # deprecated in v5.1.0
        'METPLUS_MASK_POLY',  # deprecated in v5.1.0
        'METPLUS_MASK_SID',  # deprecated in v5.1.0
        'METPLUS_MASK_LLPNT',  # deprecated in v5.1.0
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
        'ecnt',
        'orank',
        'rps',
        'eclv',
        'mpr',
        'seeps',
        'seeps_mpr',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'point_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """! Create a dictionary that holds all the values set in the
             METplus config file for the point-stat wrapper.

             Returns:
                 c_dict   - A dictionary containing the key-value pairs set
                             in the METplus configuration file.
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config', 'LOG_POINT_STAT_VERBOSITY',
                               c_dict['VERBOSITY'])
        )
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['SUPPORTS_FILE_LIST'] = False

        c_dict['OFFSETS'] = getlistint(
            self.config.getstr('config', 'POINT_STAT_OFFSETS', '0')
        )
        self.get_input_templates(c_dict, {
            'FCST': {'prefix': ('POINT_STAT_FCST', 'FCST_POINT_STAT'), 'required': True},
            'OBS': {'prefix': ('POINT_STAT_OBS', 'OBS_POINT_STAT'), 'required': True},
        })

        c_dict['FCST_INPUT_DATATYPE'] = (
            self.config.getstr('config', 'FCST_POINT_STAT_INPUT_DATATYPE', '')
        )
        c_dict['OBS_INPUT_DATATYPE'] = (
            self.config.getstr('config', 'OBS_POINT_STAT_INPUT_DATATYPE', '')
        )

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('POINT_STAT_OUTPUT_DIR', '')
        )

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'POINT_STAT_OUTPUT_TEMPLATE')
        )

        # get climatology config variables
        self.handle_climo_dict()

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('PointStatConfig_wrapped')

        # get optional ugrid config file if requested
        c_dict['UGRID_CONFIG_FILE'] = (
            self.config.getraw('config', 'POINT_STAT_UGRID_CONFIG_FILE')
        )

        self.add_met_config_window('obs_window')

        self.handle_mask(get_point=True)

        self.add_met_config(name='message_type', data_type='list')

        self.handle_file_type(type_list=('FCST', 'OBS'))

        self.handle_climo_cdf_dict()

        self.handle_land_mask()
        self.handle_topo_mask()

        self.add_met_config_dict('lapse_rate_correction', {
            'apply_to': ('string', 'constant'),
            'value': ('string', 'remove_quotes'),
        })

        self.add_met_config_dict('msl_agl_conversion', {
            'apply_to': ('string', 'constant'),
            'apply_from': ('string', 'constant'),
            'thresh': ('string', 'remove_quotes'),
            'msl_to_agl': 'bool',
        })

        c_dict['OBS_VALID_BEG'] = (
            self.config.getraw('config', 'POINT_STAT_OBS_VALID_BEG', '')
        )
        c_dict['OBS_VALID_END'] = (
            self.config.getraw('config', 'POINT_STAT_OBS_VALID_END', '')
        )

        c_dict['FCST_PROB_THRESH'] = (
            self.config.getstr('config', 'FCST_POINT_STAT_PROB_THRESH', '==0.1')
        )
        c_dict['OBS_PROB_THRESH'] = (
            self.config.getstr('config', 'OBS_POINT_STAT_PROB_THRESH', '==0.1')
        )

        c_dict['ONCE_PER_FIELD'] = (
            self.config.getbool('config', 'POINT_STAT_ONCE_PER_FIELD', False)
        )

        self.add_met_config(name='obs_quality_inc', data_type='list',
                            metplus_configs=['POINT_STAT_OBS_QUALITY_INC',
                                             'POINT_STAT_OBS_QUALITY_INCLUDE',
                                             'POINT_STAT_OBS_QUALITY'])
        self.add_met_config(name='obs_quality_exc', data_type='list',
                            metplus_configs=['POINT_STAT_OBS_QUALITY_EXC',
                                             'POINT_STAT_OBS_QUALITY_EXCLUDE'])

        self.add_met_config(name='duplicate_flag', data_type='string',
                            extra_args={'constant': True})
        self.add_met_config(name='obs_summary', data_type='string',
                            extra_args={'constant': True})

        self.add_met_config(name='obs_perc_value', data_type='int')

        self.handle_flags('output')

        self.handle_interp_dict()

        self.add_met_config(
            name='time_interp_method', data_type='string',
            env_var_name='CLIMO_MEAN_TIME_INTERP_METHOD',
            metplus_configs=['POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD'],
            extra_args={'constant': True},
        )
        self.add_met_config(
            name='time_interp_method', data_type='string',
            env_var_name='CLIMO_STDEV_TIME_INTERP_METHOD',
            metplus_configs=['POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD'],
            extra_args={'constant': True},
        )

        self.add_met_config(name='hss_ec_value', data_type='float',
                            metplus_configs=['POINT_STAT_HSS_EC_VALUE'])

        self.add_met_config_dict('hira', {
            'flag': 'bool',
            'width': ('list', 'remove_quotes'),
            'vld_thresh': 'float',
            'cov_thresh': ('list', 'remove_quotes'),
            'shape': ('string', 'constant'),
            'prob_cat_thresh': ('list', 'remove_quotes'),
        })

        self.add_met_config(name='message_type_group_map', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='obtype_as_group_val_flag', data_type='bool')

        self.add_met_config(name='seeps_p1_thresh', data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='ugrid_dataset', data_type='string')
        self.add_met_config(name='ugrid_max_distance_km', data_type='int')
        self.add_met_config(name='ugrid_coordinates_file', data_type='string')

        self.add_met_config(name='point_weight_flag', data_type='string',
                            extra_args={'constant': True})
        self.add_met_config(name='kde_ref_angle', data_type='float')
        self.add_met_config(name='write_weights', data_type='bool')

        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error('Must set FCST_POINT_STAT_INPUT_TEMPLATE '
                           'in config file')

        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error('Must set OBS_POINT_STAT_INPUT_TEMPLATE '
                           'in config file')

        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set POINT_STAT_OUTPUT_DIR in config file')
        return c_dict

    def populate_var_options(self):
        var_options = super().populate_var_options()

        # add options that are supported for obs fields
        obs_options = {
            'duplicate_flag': {'data_type': 'constant'},
            'obs_summary': {'data_type': 'constant'},
            'obs_perc_value': {'data_type': 'int'},
        }
        for key, value in obs_options.items():
            var_options['obs'][key] = value

        self.handle_land_mask_var_options(var_options)
        self.handle_topo_mask_var_options(var_options)
        self.handle_lapse_rate_correction_var_options(var_options)
        self.handle_msl_agl_conversion_var_options(var_options)

        return var_options

    def set_command_line_arguments(self, time_info):
        """!Set command line arguments in self.args to add to command to run.
        This function is overwritten from CompareGridded wrapper.

        @param time_info dictionary with time information
        """
        # call CompareGridded function
        super().set_command_line_arguments(time_info)

        # set optional obs_valid_beg and obs_valid_end arguments
        for ext in ['BEG', 'END']:
            if self.c_dict[f'OBS_VALID_{ext}']:
                obs_valid = do_string_sub(self.c_dict[f'OBS_VALID_{ext}'],
                                          **time_info)
                self.args.append(f"-obs_valid_{ext.lower()} {obs_valid}")

    def find_input_files(self, time_info):
        # get model from first var to compare
        model_path = self.find_model(time_info,
                                     mandatory=True,
                                     return_list=True)
        if not model_path:
            return None

        # if there is more than 1 file, create file list file
        if len(model_path) > 1:
            self.logger.warning('Multiple forecast files found.'
                                'Using the first one')

        self.infiles.append(model_path[0])

        # get observation to from first var compare
        obs_path, time_info = self.find_obs_offset(time_info,
                                                   mandatory=True,
                                                   return_list=True)
        if obs_path is None:
            return None

        # add observation files found individually to use -point_obs argument
        self.infiles.extend(obs_path)

        return time_info

    def get_command(self):
        """! Builds the command to run point_stat
           @rtype string
           @return Returns a point_stat command with arguments that you can run
        """
        fcst_file, *obs_files = self.infiles
        obs_file = obs_files[0]
        cmd = (f"{self.app_path} -v {self.c_dict['VERBOSITY']} "
               f"{fcst_file} {obs_file} {self.param}")

        if len(obs_files) > 1:
            cmd += ' -point_obs ' + ' -point_obs '.join(obs_files[1:])

        for arg in self.args:
            cmd += f' {arg}'

        cmd += f' -outdir {self.outdir}'
        return cmd
