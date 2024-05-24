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
from ..util import time_util
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
        'METPLUS_OBS_FIELD',
        'METPLUS_MESSAGE_TYPE',
        'METPLUS_LAND_MASK_DICT',
        'METPLUS_TOPO_MASK_DICT',
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
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_SEEPS_P1_THRESH',
        'METPLUS_UGRID_DATASET',
        'METPLUS_UGRID_MAX_DISTANCE_KM',
        'METPLUS_UGRID_COORDINATES_FILE',
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
        c_dict['OFFSETS'] = getlistint(
            self.config.getstr('config', 'POINT_STAT_OFFSETS', '0')
        )
        self.get_input_templates(c_dict, {
            'FCST': {'prefix': 'FCST_POINT_STAT', 'required': True},
            'OBS': {'prefix': 'OBS_POINT_STAT', 'required': True},
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

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='FCST_FILE_TYPE',
                            metplus_configs=['POINT_STAT_FCST_FILE_TYPE',
                                             'FCST_POINT_STAT_FILE_TYPE',
                                             'POINT_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='OBS_FILE_TYPE',
                            metplus_configs=['POINT_STAT_OBS_FILE_TYPE',
                                             'OBS_POINT_STAT_FILE_TYPE',
                                             'POINT_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.handle_climo_cdf_dict()

        self.add_met_config_dict('land_mask', {
            'flag': 'bool',
            'file_name': 'list',
            'field': ('dict', None, {
                'name': 'string',
                'level': 'string',
            }),
            'regrid': ('dict', None, {
                'method': ('string', 'remove_quotes'),
                'width': 'int',
            }),
            'thresh': 'thresh',
        })

        self.add_met_config_dict('topo_mask', {
            'flag': 'bool',
            'file_name': 'list',
            'field': ('dict', None, {
                'name': 'string',
                'level': 'string',
            }),
            'regrid': ('dict', None, {
                'method': ('string', 'remove_quotes'),
                'width': 'int',
            }),
            'use_obs_thresh': 'thresh',
            'interp_fcst_thresh': 'thresh',
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
                            extra_args={'remove_quotes': True, 'uppercase': True})
        self.add_met_config(name='obs_summary', data_type='string',
                            extra_args={'remove_quotes': True, 'uppercase': True})

        self.add_met_config(name='obs_perc_value', data_type='int')

        self.handle_flags('output')

        self.handle_interp_dict()

        self.add_met_config(
            name='time_interp_method', data_type='string',
            env_var_name='CLIMO_MEAN_TIME_INTERP_METHOD',
            metplus_configs=['POINT_STAT_CLIMO_MEAN_TIME_INTERP_METHOD'],
            extra_args={'remove_quotes': True, 'uppercase': True},
        )
        self.add_met_config(
            name='time_interp_method', data_type='string',
            env_var_name='CLIMO_STDEV_TIME_INTERP_METHOD',
            metplus_configs=['POINT_STAT_CLIMO_STDEV_TIME_INTERP_METHOD'],
            extra_args={'remove_quotes': True, 'uppercase': True},
        )

        self.add_met_config(name='hss_ec_value', data_type='float',
                            metplus_configs=['POINT_STAT_HSS_EC_VALUE'])

        self.add_met_config_dict('hira', {
            'flag': 'bool',
            'width': ('list', 'remove_quotes'),
            'vld_thresh': 'float',
            'cov_thresh': ('list', 'remove_quotes'),
            'shape': ('string', 'remove_quotes, uppercase'),
            'prob_cat_thresh': ('list', 'remove_quotes'),
        })

        self.add_met_config(name='message_type_group_map', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='seeps_p1_thresh', data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='ugrid_dataset', data_type='string')
        self.add_met_config(name='ugrid_max_distance_km', data_type='int')
        self.add_met_config(name='ugrid_coordinates_file', data_type='string')

        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error('Must set FCST_POINT_STAT_INPUT_TEMPLATE '
                           'in config file')

        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error('Must set OBS_POINT_STAT_INPUT_TEMPLATE '
                           'in config file')

        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set POINT_STAT_OUTPUT_DIR in config file')
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

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
            return False

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
            return False

        # add observation files found individually to use -point_obs argument
        self.infiles.extend(obs_path)

        return True

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
