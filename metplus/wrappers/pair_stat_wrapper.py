"""
Program Name: pair_stat_wrapper.py
Contact(s): George McCabe
Abstract: Wrapper to MET pair_stat
History Log:  Initial version
Usage: pair_stat_wrapper.py
Parameters: None
Input Files: netCDF data files
Output Files: ascii files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub
from . import CompareGriddedWrapper


class PairStatWrapper(CompareGriddedWrapper):
    """! Wrapper to the MET tool, Pair-Stat."""
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_FCST_FIELD',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_FCST_CLIMO_MEAN_DICT',
        'METPLUS_FCST_CLIMO_STDEV_DICT',
        'METPLUS_OBS_FIELD',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_OBS_CLIMO_MEAN_DICT',
        'METPLUS_OBS_CLIMO_STDEV_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_CAT_THRESH',
        'METPLUS_CNT_THRESH',
        'METPLUS_CNT_LOGIC',
        'METPLUS_WIND_THRESH',
        'METPLUS_WIND_LOGIC',
        'METPLUS_MPR_COLUMN',
        'METPLUS_MPR_THRESH',
        'METPLUS_MPR_STR_INC',
        'METPLUS_MPR_STR_EXC',
        'METPLUS_MPR_SUMMARY',
        'METPLUS_ECLV_POINTS',
        'METPLUS_HSS_EC_VALUE',
        'METPLUS_RANK_CORR_FLAG',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_CLIMO_CDF_DICT',
        'METPLUS_LAND_MASK_DICT',
        'METPLUS_TOPO_MASK_DICT',
        'METPLUS_OBS_WINDOW_DICT',
        'METPLUS_MASK_DICT',
        'METPLUS_CI_ALPHA',
        'METPLUS_BOOT_DICT',
        'METPLUS_SEEPS_P1_THRESH',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_POINT_WEIGHT_FLAG',
        'METPLUS_OUTPUT_PREFIX',
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
        'mpr',
        'seeps',
        'seeps_mpr',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'pair_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """!Create a dictionary that holds all the values set in the
             METplus config file for the PairStat wrapper.

             Returns:
                 c_dict   - A dictionary containing the key-value pairs set
                             in the METplus configuration file.
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config', 'LOG_PAIR_STAT_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        self.get_input_templates(c_dict, {
            'PAIRS': {'prefix': 'PAIR_STAT_PAIRS', 'required': True},
        })

        c_dict['PAIRS_INPUT_DATATYPE'] = (
            self.config.getstr('config', 'PAIR_STAT_PAIRS_INPUT_DATATYPE', '')
        )

        c_dict['OUTPUT_DIR'] = self.config.getdir('PAIR_STAT_OUTPUT_DIR', '')

        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('config', 'PAIR_STAT_OUTPUT_TEMPLATE')

        c_dict['FORMAT'] = self.config.getraw('config', 'PAIR_STAT_FORMAT')

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('PairStatConfig_wrapped')

        self.add_met_config(name='censor_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='censor_val', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='cat_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='cnt_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='cnt_logic', data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='wind_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='wind_logic', data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='mpr_column', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='mpr_thresh', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='mpr_str_inc', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='mpr_str_exc', data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='mpr_summary', data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='eclv_points', data_type='float')
        self.add_met_config(name='hss_ec_value', data_type='float')
        self.add_met_config(name='rank_corr_flag', data_type='bool')

        self.handle_climo_dict()
        self.handle_climo_cdf_dict()
        self.add_met_config(name='message_type_group_map', data_type='list',
                            extra_args={'remove_quotes': True})

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

        self.add_met_config_window('obs_window')
        self.handle_mask(get_point=True)

        self.add_met_config(name='ci_alpha',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config_dict('boot', {
            'interval': ('string', 'remove_quotes'),
            'rep_prop': 'float',
            'nrep': 'int',
            'rng': 'string',
            'seed': 'string',
        })

        self.add_met_config(name='seeps_p1_thresh', data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='FCST_FILE_TYPE',
                            metplus_configs=['PAIR_STAT_FCST_FILE_TYPE',
                                             'FCST_PAIR_STAT_FILE_TYPE',
                                             'PAIR_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='OBS_FILE_TYPE',
                            metplus_configs=['PAIR_STAT_OBS_FILE_TYPE',
                                             'OBS_PAIR_STAT_FILE_TYPE',
                                             'PAIR_STAT_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        c_dict['OBS_VALID_BEG'] = (
            self.config.getraw('config', 'PAIR_STAT_OBS_VALID_BEG', '')
        )
        c_dict['OBS_VALID_END'] = (
            self.config.getraw('config', 'PAIR_STAT_OBS_VALID_END', '')
        )

        c_dict['FCST_PROB_THRESH'] = (
            self.config.getstr('config', 'FCST_PAIR_STAT_PROB_THRESH', '==0.1')
        )
        c_dict['OBS_PROB_THRESH'] = (
            self.config.getstr('config', 'OBS_PAIR_STAT_PROB_THRESH', '==0.1')
        )

        c_dict['ONCE_PER_FIELD'] = (
            self.config.getbool('config', 'PAIR_STAT_ONCE_PER_FIELD', False)
        )

        self.handle_flags('output')

        self.handle_interp_dict()

        self.add_met_config(name='point_weight_flag',
                            data_type='string',
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set PAIR_STAT_OUTPUT_DIR in config file')

        # skip RuntimeFreq input file logic - remove once integrated
        #c_dict['FIND_FILES'] = False
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
        pairs_files = self.c_dict['ALL_FILES'][0].get('PAIRS')
        # pairs_files = self.find_data(time_info, data_type='PAIRS',
        #                              mandatory=True,
        #                              return_list=True)
        if not pairs_files:
            return None

        pairs_path = pairs_files[0]

        # if there is more than 1 file, create file list file
        if len(pairs_files) > 1:
            list_filename = (f"{time_info['init_fmt']}_"
                             f"{time_info['lead_hours']}_"
                             f"{self.app_name}_pairs.txt")
            pairs_path = self.write_list_file(list_filename, pairs_files)

        self.infiles.append(pairs_path)
        return time_info

    def get_command(self):
        """!Builds the command to run pair_stat
           @rtype string
           @return Returns a pair_stat command with arguments that you can run
        """
        return (f"{self.app_path} -pairs {' '.join(self.infiles)}"
                f" -format {self.c_dict['FORMAT']} -config {self.param}"
                f" -outdir {self.outdir} -v {self.c_dict['VERBOSITY']}")
