'''
Program Name: ensemble_stat_wrapper.py
Contact(s): metplus-dev
Abstract:  Initial template based on grid_stat_wrapper by George McCabe
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

import os
import glob

from ..util import sub_var_list
from ..util import do_string_sub, parse_var_list, PYTHON_EMBEDDING_TYPES
from . import CompareGriddedWrapper

"""!@namespace EnsembleStatWrapper
@brief Wraps the MET tool ensemble_stat to compare ensemble datasets
@endcode
"""


class EnsembleStatWrapper(CompareGriddedWrapper):
    """!Wraps the MET tool ensemble_stat to compare ensemble datasets
    """

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_OBTYPE',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_ENS_THRESH',
        'METPLUS_VLD_THRESH',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_FCST_FIELD',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_OBS_FIELD',
        'METPLUS_MESSAGE_TYPE',
        'METPLUS_OBS_THRESH',
        'METPLUS_DUPLICATE_FLAG',
        'METPLUS_SKIP_CONST',
        'METPLUS_OBS_ERROR_FLAG',
        'METPLUS_ENS_SSVAR_BIN_SIZE',
        'METPLUS_ENS_PHIST_BIN_SIZE',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_CLIMO_CDF_DICT',
        'METPLUS_OBS_WINDOW_DICT',
        'METPLUS_MASK_GRID',
        'METPLUS_MASK_POLY',
        'METPLUS_CI_ALPHA',
        'METPLUS_INTERP_DICT',
        'METPLUS_OUTPUT_FLAG_DICT',
        'METPLUS_NC_ORANK_FLAG_DICT',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_OBS_QUALITY_INC',
        'METPLUS_OBS_QUALITY_EXC',
        'METPLUS_ENS_MEMBER_IDS',
        'METPLUS_CONTROL_ID',
        'METPLUS_GRID_WEIGHT_FLAG',
        'METPLUS_PROB_CAT_THRESH',
        'METPLUS_PROB_PCT_THRESH',
        'METPLUS_ECLV_POINTS',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'CLIMO_MEAN_FILE',
        'CLIMO_STDEV_FILE',
        'MODEL',
        'OBTYPE',
        'REGRID_TO_GRID',
        'OUTPUT_PREFIX',
    ]

    OUTPUT_FLAGS = [
        'ecnt',
        'rps',
        'rhist',
        'phist',
        'orank',
        'ssvar',
        'relp',
        'pct',
        'pstd',
        'pjc',
        'prc',
        'eclv',
    ]

    NC_ORANK_FLAGS = [
        'latlon',
        'mean',
        'raw',
        'rank',
        'pit',
        'vld_count',
        'weight',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'ensemble_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """!Create a dictionary containing the values set in the config file
           that are required for running ensemble stat.
           This will make it easier for unit testing.

           Returns:
               @returns A dictionary of the ensemble stat values
                        from the config file.
        """
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_ENSEMBLE_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['FCST_INPUT_DATATYPE'] = (
          self.config.getraw('config', 'FCST_ENSEMBLE_STAT_INPUT_DATATYPE')
        )

        c_dict['OBS_POINT_INPUT_DATATYPE'] = (
          self.config.getraw('config',
                             'OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE')
        )

        c_dict['OBS_GRID_INPUT_DATATYPE'] = (
          self.config.getraw('config',
                             'OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE')
        )

        # check if more than 1 obs datatype is set to python embedding,
        # only one can be used
        if (c_dict['OBS_POINT_INPUT_DATATYPE'] in PYTHON_EMBEDDING_TYPES and
            c_dict['OBS_GRID_INPUT_DATATYPE'] in PYTHON_EMBEDDING_TYPES):
            self.log_error("Both OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE and "
                           "OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE"
                           " are set to Python Embedding types. "
                           "Only one can be used at a time")

        # if either are set, set OBS_INPUT_DATATYPE to that value so
        # it can be found by the check_for_python_embedding function
        elif c_dict['OBS_POINT_INPUT_DATATYPE'] in PYTHON_EMBEDDING_TYPES:
            c_dict['OBS_INPUT_DATATYPE'] = c_dict['OBS_POINT_INPUT_DATATYPE']
        elif c_dict['OBS_GRID_INPUT_DATATYPE'] in PYTHON_EMBEDDING_TYPES:
            c_dict['OBS_INPUT_DATATYPE'] = c_dict['OBS_GRID_INPUT_DATATYPE']

        c_dict['N_MEMBERS'] = (
            self.config.getint('config', 'ENSEMBLE_STAT_N_MEMBERS')
        )

        # allow multiple files in CommandBuilder.find_data logic
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # not all input files are mandatory to be found
        c_dict['MANDATORY'] = False

        # fill inputs that are not found with fake path to note it is missing
        c_dict['FCST_FILL_MISSING'] = True

        c_dict['OBS_POINT_INPUT_DIR'] = (
          self.config.getdir('OBS_ENSEMBLE_STAT_POINT_INPUT_DIR', '')
        )

        c_dict['OBS_POINT_INPUT_TEMPLATE'] = (
          self.config.getraw('config',
                             'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE')
        )

        c_dict['OBS_GRID_INPUT_DIR'] = (
          self.config.getdir('OBS_ENSEMBLE_STAT_GRID_INPUT_DIR', '')
        )

        c_dict['OBS_GRID_INPUT_TEMPLATE'] = (
          self.config.getraw('config',
                             'OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE')
        )

        # The ensemble forecast files input directory and filename templates
        c_dict['FCST_INPUT_DIR'] = (
          self.config.getdir('FCST_ENSEMBLE_STAT_INPUT_DIR', '')
        )

        c_dict['FCST_INPUT_TEMPLATE'] = (
            self.config.getraw('config', 'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE')
        )
        c_dict['FCST_INPUT_FILE_LIST'] = (
            self.config.getraw('config', 'FCST_ENSEMBLE_STAT_INPUT_FILE_LIST')
        )
        if (not c_dict['FCST_INPUT_TEMPLATE'] and
                not c_dict['FCST_INPUT_FILE_LIST']):
            self.log_error("Must set FCST_ENSEMBLE_STAT_INPUT_TEMPLATE or "
                           "FCST_ENSEMBLE_STAT_INPUT_FILE_LIST")

        # optional -ens_mean argument path
        c_dict['ENS_MEAN_INPUT_DIR'] = (
          self.config.getdir('ENSEMBLE_STAT_ENS_MEAN_INPUT_DIR', ''))

        c_dict['ENS_MEAN_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'ENSEMBLE_STAT_ENS_MEAN_INPUT_TEMPLATE'))

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('ENSEMBLE_STAT_OUTPUT_DIR', '')
        )
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set ENSEMBLE_STAT_OUTPUT_DIR "
                           "in configuration file")

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'ENSEMBLE_STAT_OUTPUT_TEMPLATE')
        )

        # get ctrl (control) template/dir - optional
        c_dict['CTRL_INPUT_TEMPLATE'] = (
            self.config.getraw('config', 'ENSEMBLE_STAT_CTRL_INPUT_TEMPLATE')
        )
        c_dict['CTRL_INPUT_DIR'] = (
            self.config.getdir('ENSEMBLE_STAT_CTRL_INPUT_DIR', '')
        )

        # get climatology config variables
        self.handle_climo_dict()

        # need to set these so that find_data will succeed
        c_dict['OBS_POINT_FILE_WINDOW_BEGIN'] = c_dict['OBS_FILE_WINDOW_BEGIN']
        c_dict['OBS_POINT_FILE_WINDOW_END'] = c_dict['OBS_FILE_WINDOW_END']
        c_dict['OBS_GRID_FILE_WINDOW_BEGIN'] = c_dict['OBS_FILE_WINDOW_BEGIN']
        c_dict['OBS_GRID_FILE_WINDOW_END'] = c_dict['OBS_FILE_WINDOW_END']

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = (
            self.get_config_file('EnsembleStatConfig_wrapped')
        )

        # read by MET through environment variable, not set in MET config file
        c_dict['MET_OBS_ERR_TABLE'] = (
            self.config.getraw('config', 'ENSEMBLE_STAT_MET_OBS_ERR_TABLE')
        )

        self.add_met_config(name='vld_thresh',
                            data_type='float',
                            metplus_configs=[
                                'ENSEMBLE_STAT_VLD_THRESH',
                                'ENSEMBLE_STAT_VALID_THRESH',
                                'ENSEMBLE_STAT_FCST_VLD_THRESH',
                                'ENSEMBLE_STAT_FCST_VALID_THRESH',
                                'FCST_ENSEMBLE_STAT_VLD_THRESH',
                                'FCST_ENSEMBLE_STAT_VALID_THRESH',
                                'ENSEMBLE_STAT_ENS_VLD_THRESH',
                            ])

        self.add_met_config(name='obs_thresh',
                            data_type='list',
                            metplus_configs=['ENSEMBLE_STAT_OBS_THRESH',
                                             'ENSEMBLE_STAT_ENS_OBS_THRESH'],
                            extra_args={'remove_quotes': True,
                                        'allow_empty': True})

        self.add_met_config(name='ens_ssvar_bin_size', data_type='float')

        self.add_met_config(name='ens_phist_bin_size', data_type='float')

        self.add_met_config(name='ens_thresh',
                            data_type='float',
                            metplus_configs=['ENSEMBLE_STAT_ENS_THRESH',
                                             'ENSEMBLE_STAT_FCST_ENS_THRESH',
                                             'FCST_ENSEMBLE_STAT_ENS_THRESH'])

        self.add_met_config(name='duplicate_flag',
                            data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='skip_const', data_type='bool')

        # set climo_cdf dictionary variables
        self.handle_climo_cdf_dict()

        # interp dictionary values
        self.handle_interp_dict()

        self.handle_flags('OUTPUT')
        self.handle_flags('NC_ORANK')

        self.add_met_config(name='flag',
                            data_type='bool',
                            env_var_name='METPLUS_OBS_ERROR_FLAG',
                            metplus_configs=['ENSEMBLE_STAT_OBS_ERROR_FLAG'])

        self.add_met_config(name='grid',
                            data_type='list',
                            env_var_name='METPLUS_MASK_GRID',
                            metplus_configs=['ENSEMBLE_STAT_MASK_GRID'],
                            extra_args={'allow_empty': True})

        self.add_met_config(name='poly',
                            data_type='list',
                            env_var_name='METPLUS_MASK_POLY',
                            metplus_configs=['ENSEMBLE_STAT_MASK_POLY',
                                             'ENSEMBLE_STAT_POLY',
                                             ('ENSEMBLE_STAT_'
                                              'VERIFICATION_MASK_TEMPLATE')],
                            extra_args={'allow_empty': True})

        self.add_met_config(name='ci_alpha',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='censor_thresh',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='censor_val',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='message_type',
                            data_type='list',
                            extra_args={'allow_empty': True})

        self.add_met_config_window('obs_window')

        self.add_met_config(
            name='obs_quality_inc',
            data_type='list',
            metplus_configs=['ENSEMBLE_STAT_OBS_QUALITY_INC',
                             'ENSEMBLE_STAT_OBS_QUALITY_INCLUDE']
        )
        self.add_met_config(
            name='obs_quality_exc',
            data_type='list',
            metplus_configs=['ENSEMBLE_STAT_OBS_QUALITY_EXC',
                             'ENSEMBLE_STAT_OBS_QUALITY_EXCLUDE']
        )

        self.add_met_config(name='ens_member_ids',
                            data_type='list')

        self.add_met_config(name='control_id',
                            data_type='string')

        self.add_met_config(name='grid_weight_flag',
                            data_type='string',
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='prob_pct_thresh',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='eclv_points',
                            data_type='float')

        self.add_met_config(name='prob_cat_thresh',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        # signifies that the tool can be run without setting
        # field information for fcst and obs
        c_dict['VAR_LIST_OPTIONAL'] = True

        # parse var list for ENS fields
        c_dict['ENS_VAR_LIST_TEMP'] = parse_var_list(
            self.config,
            data_type='ENS',
            met_tool=self.app_name
        )

        # parse optional var list for FCST and/or OBS fields
        c_dict['VAR_LIST_TEMP'] = parse_var_list(
            self.config,
            met_tool=self.app_name
        )

        return c_dict

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" {' '.join(self.infiles)} {self.param}"
                f" {' '.join(self.args)} -outdir {self.outdir}")

    def run_at_time_all_fields(self, time_info):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
        """
        # get ensemble model files
        # do not fill file list with missing if ens_member_ids is used
        fill_missing = not self.env_var_dict.get('METPLUS_ENS_MEMBER_IDS')
        if not self.find_input_files_ensemble(time_info,
                                              fill_missing=fill_missing):
            return

        if not self.set_command_line_arguments(time_info):
            return

        # parse optional var list for FCST and/or OBS fields
        var_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)

        # set field info
        fcst_field = self.get_all_field_info(var_list, 'FCST')
        obs_field = self.get_all_field_info(var_list, 'OBS')

        if not fcst_field and not obs_field:
            self.log_error("Could not build field info for fcst or obs")
            return

        self.format_field('FCST', fcst_field)
        self.format_field('OBS', obs_field)

        self.process_fields(time_info)

    def set_command_line_arguments(self, time_info):
        """! Set all arguments for plot_point_obs command.

        @param time_info dictionary containing timing information
        @returns False if files could not be found, True on success
        """
        # get point observation file if requested
        if self.c_dict['OBS_POINT_INPUT_TEMPLATE']:
            point_obs_files = self.find_data(time_info, data_type='OBS_POINT',
                                             return_list=True)
            if point_obs_files is None:
                return False

            for point_obs_path in point_obs_files:
                self.args.append(f'-point_obs "{point_obs_path}"')

        # get grid observation file if requested
        if self.c_dict['OBS_GRID_INPUT_TEMPLATE']:
            grid_obs_files = self.find_data(time_info, data_type='OBS_GRID',
                                            return_list=True)
            if grid_obs_files is None:
                return False

            for grid_obs_path in grid_obs_files:
                self.args.append(f'-grid_obs "{grid_obs_path}"')

        # get ens_mean file if requested
        if self.c_dict['ENS_MEAN_INPUT_TEMPLATE']:
            ens_mean_path = self.find_data(time_info, data_type='ENS_MEAN',
                                           return_list=True)
            if ens_mean_path is None:
                return False

            self.args.append(f'-ens_mean {ens_mean_path[0]}')

        return True

    def get_all_field_info(self, var_list, data_type):
        """!Get field info based on data type"""

        field_list = []
        for var_info in var_list:
            type_lower = data_type.lower()
            level = var_info[f'{type_lower}_level']
            thresh = var_info[f'{type_lower}_thresh']
            name = var_info[f'{type_lower}_name']
            extra = var_info[f'{type_lower}_extra']

            # check if python embedding is used and set up correctly
            # set env var for file type if it is used
            py_embed_ok = self.check_for_python_embedding(data_type, var_info)
            if not py_embed_ok:
                return ''

            next_field = self.get_field_info(v_level=level,
                                             v_thresh=thresh,
                                             v_name=name,
                                             v_extra=extra,
                                             d_type=data_type)
            if next_field is None:
                return ''

            field_list.extend(next_field)

        return ','.join(field_list)

    def set_environment_variables(self, time_info):
        self.add_env_var("MET_OBS_ERROR_TABLE",
                         self.c_dict.get('MET_OBS_ERR_TABLE', ''))
        super().set_environment_variables(time_info)

    def process_fields(self, time_info):
        """! Set and print environment variables, then build/run MET command

            @param time_info dictionary containing timing information
            @param fcst_field field information formatted for MET config file
            @param obs_field field information formatted for MET config file
        """
        # set config file since command is reset after each run
        self.param = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)

        # set up output dir with time info
        if not self.find_and_check_output_file(time_info, is_directory=True):
            return

        # set environment variables that are passed to the MET config
        self.set_environment_variables(time_info)

        # run the MET command
        self.build()
