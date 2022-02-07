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

from ..util import met_util as util
from . import CompareGriddedWrapper
from ..util import do_string_sub
from ..util import parse_var_list

"""!@namespace EnsembleStatWrapper
@brief Wraps the MET tool ensemble_stat to compare ensemble datasets
@endcode
"""

class EnsembleStatWrapper(CompareGriddedWrapper):
    """!Wraps the MET tool ensemble_stat to compare ensemble datasets
    """

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_OBTYPE',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_ENS_FILE_TYPE',
        'METPLUS_ENS_THRESH',
        'METPLUS_ENS_VLD_THRESH',
        'METPLUS_ENS_OBS_THRESH',
        'METPLUS_ENS_FIELD',
        'METPLUS_NBRHD_PROB_DICT',
        'METPLUS_NMEP_SMOOTH_DICT',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_FCST_FIELD',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_OBS_FIELD',
        'METPLUS_MESSAGE_TYPE',
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
        'METPLUS_ENSEMBLE_FLAG_DICT',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_OBS_QUALITY_INC',
        'METPLUS_OBS_QUALITY_EXC',
        'METPLUS_ENS_MEMBER_IDS',
        'METPLUS_CONTROL_ID',
        'METPLUS_GRID_WEIGHT_FLAG',
    ]

    # handle deprecated env vars used pre v4.0.0
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'CLIMO_MEAN_FILE',
        'CLIMO_STDEV_FILE',
    ]

    OUTPUT_FLAGS = ['ecnt',
                    'rps',
                    'rhist',
                    'phist',
                    'orank',
                    'ssvar',
                    'relp'
                    ]

    ENSEMBLE_FLAGS = ['latlon',
                      'mean',
                      'stdev',
                      'minus',
                      'plus',
                      'min',
                      'max',
                      'range',
                      'vld_count',
                      'frequency',
                      'nep',
                      'nmep',
                      'rank',
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

        c_dict['ENS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'ENS_ENSEMBLE_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DATATYPE'] = \
          self.config.getstr('config',
                             'FCST_ENSEMBLE_STAT_INPUT_DATATYPE',
                             '')

        c_dict['OBS_POINT_INPUT_DATATYPE'] = \
          self.config.getstr('config',
                             'OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE',
                             '')

        c_dict['OBS_GRID_INPUT_DATATYPE'] = \
          self.config.getstr('config',
                             'OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE',
                             '')

        # check if more than 1 obs datatype is set to python embedding,
        # only one can be used
        if (c_dict['OBS_POINT_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES and
            c_dict['OBS_GRID_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES):
            self.log_error("Both OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE and "
                           "OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE"
                           " are set to Python Embedding types. "
                           "Only one can be used at a time")

        # if either are set, set OBS_INPUT_DATATYPE to that value so
        # it can be found by the check_for_python_embedding function
        elif c_dict['OBS_POINT_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES:
            c_dict['OBS_INPUT_DATATYPE'] = c_dict['OBS_POINT_INPUT_DATATYPE']
        elif c_dict['OBS_GRID_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES:
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

        c_dict['OBS_POINT_INPUT_DIR'] = \
          self.config.getdir('OBS_ENSEMBLE_STAT_POINT_INPUT_DIR', '')

        c_dict['OBS_POINT_INPUT_TEMPLATE'] = \
          self.config.getraw('config',
                             'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE')

        c_dict['OBS_GRID_INPUT_DIR'] = \
          self.config.getdir('OBS_ENSEMBLE_STAT_GRID_INPUT_DIR', '')

        c_dict['OBS_GRID_INPUT_TEMPLATE'] = \
          self.config.getraw('config',
                             'OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE')

        # The ensemble forecast files input directory and filename templates
        c_dict['FCST_INPUT_DIR'] = \
          self.config.getdir('FCST_ENSEMBLE_STAT_INPUT_DIR', '')

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

        c_dict['OUTPUT_DIR'] = self.config.getdir('ENSEMBLE_STAT_OUTPUT_DIR',
                                                  '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set ENSEMBLE_STAT_OUTPUT_DIR "
                           "in configuration file")

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'ENSEMBLE_STAT_OUTPUT_TEMPLATE',
                               '')
        )

        # get ctrl (control) template/dir - optional
        c_dict['CTRL_INPUT_TEMPLATE'] = self.config.getraw(
            'config',
            'ENSEMBLE_STAT_CTRL_INPUT_TEMPLATE'
        )
        c_dict['CTRL_INPUT_DIR'] = self.config.getdir(
            'ENSEMBLE_STAT_CTRL_INPUT_DIR',
            ''
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
        c_dict['MET_OBS_ERR_TABLE'] = \
            self.config.getstr('config', 'ENSEMBLE_STAT_MET_OBS_ERR_TABLE', '')

        self.add_met_config(name='vld_thresh',
                            data_type='float',
                            env_var_name='METPLUS_ENS_VLD_THRESH',
                            metplus_configs=['ENSEMBLE_STAT_ENS_VLD_THRESH',
                                             'ENSEMBLE_STAT_VLD_THRESH',
                                             'ENSEMBLE_STAT_ENS_VALID_THRESH',
                                             'ENSEMBLE_STAT_VALID_THRESH',
                                             ])

        self.add_met_config(name='obs_thresh',
                            data_type='list',
                            env_var_name='METPLUS_ENS_OBS_THRESH',
                            metplus_configs=['ENSEMBLE_STAT_ENS_OBS_THRESH',
                                             'ENSEMBLE_STAT_OBS_THRESH'],
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='ens_ssvar_bin_size',
                            data_type='float')

        self.add_met_config(name='ens_phist_bin_size',
                            data_type='float')

        self.handle_nbrhd_prob_dict()

        self.add_met_config(name='ens_thresh',
                            data_type='float')

        self.add_met_config(name='duplicate_flag',
                            data_type='string',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='skip_const',
                            data_type='bool')

        # set climo_cdf dictionary variables
        self.handle_climo_cdf_dict()

        # set nmep_smooth dictionary variables
        self.handle_nmep_smooth_dict()

        # interp dictionary values
        self.handle_interp_dict()

        self.handle_flags('OUTPUT')
        self.handle_flags('ENSEMBLE')

        self.add_met_config(name='flag',
                            data_type='bool',
                            env_var_name='METPLUS_OBS_ERROR_FLAG',
                            metplus_configs=['ENSEMBLE_STAT_OBS_ERROR_FLAG'])

        self.add_met_config(name='grid',
                            data_type='list',
                            env_var_name='METPLUS_MASK_GRID',
                            metplus_configs=['ENSEMBLE_STAT_MASK_GRID'],
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
        self.handle_obs_window_legacy(c_dict)

        c_dict['MASK_POLY_TEMPLATE'] = self.read_mask_poly()

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

        # old method of setting MET config values
        c_dict['ENS_THRESH'] = (
            self.config.getstr('config', 'ENSEMBLE_STAT_ENS_THRESH', '1.0')
        )

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

    def handle_nmep_smooth_dict(self):
        self.add_met_config_dict('nmep_smooth', {
            'vld_thresh': 'float',
            'shape': ('string', 'uppercase,remove_quotes'),
            'gaussian_dx': 'float',
            'gaussian_radius': 'int',
            'type': ('dictlist', '', {'method': ('string',
                                                 'uppercase,remove_quotes'),
                                      'width': 'int',
                                      }
                     )
        })

    def handle_nbrhd_prob_dict(self):
        self.add_met_config_dict('nbrhd_prob', {
            'width': ('list', 'remove_quotes'),
            'shape': ('string', 'uppercase,remove_quotes'),
            'vld_thresh': 'float',
        })

    def run_at_time_all_fields(self, time_info):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
        """
        # get ensemble model files
        if not self.find_input_files_ensemble(time_info):
            return

        # parse var list for ENS fields
        ensemble_var_list = util.sub_var_list(self.c_dict['ENS_VAR_LIST_TEMP'],
                                              time_info)

        # parse optional var list for FCST and/or OBS fields
        var_list = util.sub_var_list(self.c_dict['VAR_LIST_TEMP'],
                                     time_info)

        # if empty var list for FCST/OBS, use None as first var, else use first var in list
        if not var_list:
            first_var_info = None
        else:
            first_var_info = var_list[0]

        # get point observation file if requested
        if self.c_dict['OBS_POINT_INPUT_TEMPLATE']:
            point_obs_path = self.find_data(time_info, first_var_info, 'OBS_POINT')
            if point_obs_path is None:
                return

            self.point_obs_files.append(point_obs_path)

        # get grid observation file if requested
        if self.c_dict['OBS_GRID_INPUT_TEMPLATE']:
            grid_obs_path = self.find_data(time_info, first_var_info, 'OBS_GRID')
            if grid_obs_path is None:
                return

            self.grid_obs_files.append(grid_obs_path)

        # set field info
        fcst_field = self.get_all_field_info(var_list, 'FCST')
        obs_field = self.get_all_field_info(var_list, 'OBS')
        ens_field = self.get_all_field_info(ensemble_var_list, 'ENS')

        if not fcst_field and not obs_field and not ens_field:
            self.log_error("Could not build field info for fcst, obs, or ens")
            return

        self.format_field('FCST', fcst_field)
        self.format_field('OBS', obs_field)
        self.format_field('ENS', ens_field)

        # run
        self.process_fields(time_info)


    def get_all_field_info(self, var_list, data_type):
        """!Get field info based on data type"""

        field_list = []
        for var_info in var_list:
            if data_type == 'FCST':
                level = var_info['fcst_level']
                thresh = var_info['fcst_thresh']
                name = var_info['fcst_name']
                extra = var_info['fcst_extra']
            elif data_type == 'OBS':
                level = var_info['obs_level']
                thresh = var_info['obs_thresh']
                name = var_info['obs_name']
                extra = var_info['obs_extra']
            elif data_type == 'ENS':
                level = var_info['ens_level']
                thresh = var_info['ens_thresh']
                name = var_info['ens_name']
                extra = var_info['ens_extra']
            else:
                return ''

            # check if python embedding is used and set up correctly
            # set env var for file type if it is used
            pyEmbedIsOK = self.check_for_python_embedding(data_type, var_info)
            if not pyEmbedIsOK:
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

        fcst_field = self.c_dict.get('FCST_FIELD', '')
        self.add_env_var("FCST_FIELD",
                         fcst_field)
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))

        ens_field = self.c_dict.get('ENS_FIELD', '')
        # if ens field is not set, use fcst field
        if not ens_field:
            ens_field = fcst_field

        self.add_env_var("ENS_FIELD", ens_field)

        self.add_env_var("OBS_WINDOW_BEGIN",
                         str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var("OBS_WINDOW_END",
                         str(self.c_dict['OBS_WINDOW_END']))

        # read output prefix at this step to ensure that
        # CURRENT_[FCST/OBS]_[NAME/LEVEL] is substituted correctly
        self.add_env_var('VERIF_MASK',
                         self.c_dict.get('VERIFICATION_MASK', ''))

        # support old method of setting variables in MET config files
        self.add_env_var('ENS_THRESH',
                         self.c_dict.get('ENS_THRESH'))
        met_config_list_old = [
            'OBTYPE',
            'INPUT_BASE',
            'ENS_FILE_TYPE',
            'FCST_FILE_TYPE',
            'OBS_FILE_TYPE',
        ]
        for item in met_config_list_old:
            self.add_env_var(item, self.c_dict.get(item, ''))

        # call parent function to set common vars, user env vars,
        # and print list of variables that are set
        super().set_environment_variables(time_info)

    def process_fields(self, time_info):
        """! Set and print environment variables, then build/run MET command
              Args:
                @param time_info dictionary containing timing information
                @param fcst_field field information formatted for MET config file
                @param obs_field field information formatted for MET config file
        """
        # set config file since command is reset after each run
        self.param = do_string_sub(self.c_dict['CONFIG_FILE'],
                                   **time_info)

        # set up output dir with time info
        if not self.find_and_check_output_file(time_info,
                                               is_directory=True):
            return

        # set environment variables that are passed to the MET config
        self.set_environment_variables(time_info)

        # check if METplus can generate the command successfully
        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return

        # run the MET command
        self.build()


    def clear(self):
        """!Unset class variables to prepare for next run time
        """
        super().clear()
        self.point_obs_files = []
        self.grid_obs_files = []


    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.log_error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for args in self.args:
            cmd += args + " "

        if len(self.infiles) == 0:
            self.log_error(self.app_name+": No input filenames specified")
            return None

        for infile in self.infiles:
            cmd += infile + " "

        if self.param != "":
            cmd += self.param + " "

        for obs_file in self.point_obs_files:
            cmd += "-point_obs " + obs_file + " "

        for obs_file in self.grid_obs_files:
            cmd += "-grid_obs " + obs_file + " "

        if self.outdir == "":
            self.log_error(self.app_name+": No output directory specified")
            return None

        cmd += '-outdir {}'.format(self.outdir)
        return cmd
