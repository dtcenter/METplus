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

"""!@namespace EnsembleStatWrapper
@brief Wraps the MET tool ensemble_stat to compare ensemble datasets
@endcode
"""

class EnsembleStatWrapper(CompareGriddedWrapper):
    """!Wraps the MET tool ensemble_stat to compare ensemble datasets
    """
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'ensemble_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        """!Create a dictionary containing the values set in the config file
           that are required for running ensemble stat.
           This will make it easier for unit testing.

           Returns:
               @returns A dictionary of the ensemble stat values
                        from the config file.
        """
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_ENSEMBLE_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['ENS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'ENS_ENSEMBLE_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'FCST_ENSEMBLE_STAT_INPUT_DATATYPE', '')

        c_dict['OBS_POINT_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE', '')

        c_dict['OBS_GRID_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE', '')

        # check if more than 1 obs datatype is set to python embedding, only one can be used
        if (c_dict['OBS_POINT_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES and
            c_dict['OBS_GRID_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES):
            self.log_error("Both OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE and "
                           "OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE"
                           " are set to Python Embedding types. Only one can be used at a time")

        # if either are set, set OBS_INPUT_DATATYPE to that value so it can be found by
        # the check_for_python_embedding function
        elif c_dict['OBS_POINT_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES:
            c_dict['OBS_INPUT_DATATYPE'] = c_dict['OBS_POINT_INPUT_DATATYPE']
        elif c_dict['OBS_GRID_INPUT_DATATYPE'] in util.PYTHON_EMBEDDING_TYPES:
            c_dict['OBS_INPUT_DATATYPE'] = c_dict['OBS_GRID_INPUT_DATATYPE']

        c_dict['CONFIG_FILE'] = \
            self.config.getraw('config', 'ENSEMBLE_STAT_CONFIG_FILE', '')

        if not c_dict['CONFIG_FILE']:
            self.log_error("Must set ENSEMBLE_STAT_CONFIG_FILE.")

        c_dict['ENS_THRESH'] = \
          self.config.getstr('config', 'ENSEMBLE_STAT_ENS_THRESH', '1.0')

        # met_obs_error_table is not required, if it is not defined
        # set it to the empty string '', that way the MET default is used.
        c_dict['MET_OBS_ERR_TABLE'] = \
            self.config.getstr('config', 'ENSEMBLE_STAT_MET_OBS_ERR_TABLE', '')

        # No Default being set this is REQUIRED TO BE DEFINED in conf file.
        c_dict['N_MEMBERS'] = \
            self.config.getint('config', 'ENSEMBLE_STAT_N_MEMBERS', -1)

        if c_dict['N_MEMBERS'] < 0:
            self.log_error("Must set ENSEMBLE_STAT_N_MEMBERS to a integer > 0")

        c_dict['OBS_POINT_INPUT_DIR'] = \
          self.config.getdir('OBS_ENSEMBLE_STAT_POINT_INPUT_DIR', '')

        c_dict['OBS_POINT_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE')

        c_dict['OBS_GRID_INPUT_DIR'] = \
          self.config.getdir('OBS_ENSEMBLE_STAT_GRID_INPUT_DIR', '')

        c_dict['OBS_GRID_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                             'OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE')

        # The ensemble forecast files input directory and filename templates
        c_dict['FCST_INPUT_DIR'] = \
          self.config.getdir('FCST_ENSEMBLE_STAT_INPUT_DIR', '')

        # This is a raw string and will be interpreted to generate the
        # ensemble member filenames. This may be a list of 1 or n members.
        c_dict['FCST_INPUT_TEMPLATE'] = \
          util.getlist(self.config.getraw('filename_templates',
                                          'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE'))
        if not c_dict['FCST_INPUT_TEMPLATE']:
            self.log_error("Must set FCST_ENSEMBLE_STAT_INPUT_TEMPLATE")

        c_dict['OUTPUT_DIR'] = self.config.getdir('ENSEMBLE_STAT_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set ENSEMBLE_STAT_OUTPUT_DIR in configuration file")

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'ENSEMBLE_STAT_OUTPUT_TEMPLATE',
                               '')
        )

        # get climatology config variables
        self.read_climo_wrapper_specific('ENSEMBLE_STAT', c_dict)

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'ensemble_stat')

        # need to set these so that find_data will succeed
        c_dict['OBS_POINT_WINDOW_BEGIN'] = c_dict['OBS_WINDOW_BEGIN']
        c_dict['OBS_POINT_WINDOW_END'] = c_dict['OBS_WINDOW_END']
        c_dict['OBS_GRID_WINDOW_BEGIN'] = c_dict['OBS_WINDOW_BEGIN']
        c_dict['OBS_GRID_WINDOW_END'] = c_dict['OBS_WINDOW_END']

        c_dict['OBS_POINT_FILE_WINDOW_BEGIN'] = c_dict['OBS_FILE_WINDOW_BEGIN']
        c_dict['OBS_POINT_FILE_WINDOW_END'] = c_dict['OBS_FILE_WINDOW_END']
        c_dict['OBS_GRID_FILE_WINDOW_BEGIN'] = c_dict['OBS_FILE_WINDOW_BEGIN']
        c_dict['OBS_GRID_FILE_WINDOW_END'] = c_dict['OBS_FILE_WINDOW_END']

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'ENSEMBLE_STAT_REGRID_TO_GRID', '')

        self.set_c_dict_float(c_dict,
                              'ENSEMBLE_STAT_ENS_VLD_THRESH',
                              'vld_thresh',
                              'ENS_VLD_THRESH')

        # used to override the file type for fcst/obs if using python embedding for input
        c_dict['ENS_FILE_TYPE'] = ''
        c_dict['FCST_FILE_TYPE'] = ''
        c_dict['OBS_FILE_TYPE'] = ''
        c_dict['VAR_LIST_OPTIONAL'] = True

        return c_dict

    def run_at_time_all_fields(self, time_info):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
        """
        # get ensemble model files
        fcst_file_list = self.find_model_members(time_info)
        if not fcst_file_list:
            return

        self.infiles.append(fcst_file_list)

        # parse var list for ENS fields
        ensemble_var_list = util.parse_var_list(self.config, time_info, data_type='ENS')

        # parse optional var list for FCST and/or OBS fields
        var_list = util.parse_var_list(self.config, time_info, met_tool=self.app_name)

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

        # run
        self.process_fields(time_info, fcst_field, obs_field, ens_field)


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


    def find_model_members(self, time_info):
        """! Finds the model member files to compare
              Args:
                @param time_info dictionary containing timing information
                @rtype string
                @return Returns a list of the paths to the ensemble model files
        """
        model_dir = self.c_dict['FCST_INPUT_DIR']
        # used for filling in missing files to ensure ens_thresh check is accurate
        fake_dir = '/ensemble/member/is/missing'

        # model_template is a list of 1 or more.
        ens_members_path = []

        # get all files that exist
        for ens_member_template in self.c_dict['FCST_INPUT_TEMPLATE']:
            member_file = do_string_sub(ens_member_template,
                                        **time_info)
            expected_path = os.path.join(model_dir, member_file)

            # if wildcard expression, get all files that match
            if '?' in expected_path or '*' in expected_path:
                wildcard_files = sorted(glob.glob(expected_path))
                self.logger.debug('Ensemble members file pattern: {}'
                                  .format(expected_path))
                self.logger.debug('{} members match file pattern'
                                  .format(str(len(wildcard_files))))

                # add files to list of ensemble members
                for wildcard_file in wildcard_files:
                    ens_members_path.append(wildcard_file)
            else:
                # otherwise check if file exists
                expected_path = util.preprocess_file(expected_path,
                                                     self.c_dict['FCST_INPUT_DATATYPE'],
                                                     self.config)

                # if the file exists, add it to the list
                if expected_path:
                    ens_members_path.append(expected_path)
                else:
                    # add relative path to fake dir and add to list
                    ens_members_path.append(os.path.join(fake_dir, member_file))
                    self.logger.warning('Expected ensemble file {} not found'
                                        .format(member_file))

        # if more files found than expected, error and exit
        if len(ens_members_path) > self.c_dict['N_MEMBERS']:
            msg = 'Found more files than expected! ' +\
                  'Found {} expected {}. '.format(len(ens_members_path),
                                                  self.c_dict['N_MEMBERS']) +\
                  'Adjust wildcard expression in [filename_templates] '+\
                  'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE or adjust [config] '+\
                  'ENSEMBLE_STAT_N_MEMBERS. Files found: {}'.format(ens_members_path)
            self.log_error(msg)
            self.logger.error("Could not file files in {} for init {} f{} "
                              .format(model_dir, time_info['init_fmt'],
                                      str(time_info['lead_hours'])))
            return False
        # if fewer files found than expected, warn and add fake files
        elif len(ens_members_path) < self.c_dict['N_MEMBERS']:
            msg = 'Found fewer files than expected. '+\
              'Found {} expected {}.'.format(len(ens_members_path),
                                             self.c_dict['N_MEMBERS'])
            self.logger.warning(msg)
            # add fake files to list to get correct number of files for ens_thresh
            diff = self.c_dict['N_MEMBERS'] - len(ens_members_path)
            self.logger.warning('Adding {} fake files to '.format(str(diff))+\
                                'ensure ens_thresh check is accurate')
            for _ in range(0, diff, 1):
                ens_members_path.append(fake_dir)

        # write file that contains list of ensemble files
        list_filename = time_info['init_fmt'] + '_' + \
          str(time_info['lead_hours']) + '_ensemble.txt'
        return self.write_list_file(list_filename, ens_members_path)

    def set_environment_variables(self, fcst_field, obs_field, ens_field, time_info):
        self.add_env_var("MET_OBS_ERROR_TABLE",
                         self.c_dict["MET_OBS_ERR_TABLE"])

        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        if ens_field != '':
            self.add_env_var("ENS_FIELD", ens_field)
        else:
            self.add_env_var("ENS_FIELD", fcst_field)

        self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
        self.add_env_var("INPUT_BASE", self.c_dict['INPUT_BASE'])
        self.add_env_var("FCST_LEAD", str(time_info['lead_hours']).zfill(3))
        self.add_env_var("OBS_WINDOW_BEGIN", str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var("OBS_WINDOW_END", str(self.c_dict['OBS_WINDOW_END']))
        self.add_env_var("ENS_THRESH", self.c_dict['ENS_THRESH'])
        self.add_env_var('ENS_VLD_THRESH',
                         self.c_dict.get('ENS_VLD_THRESH', ''))

        self.add_env_var('OUTPUT_PREFIX', self.get_output_prefix(time_info))

        self.add_env_var("ENS_FILE_TYPE", self.c_dict['ENS_FILE_TYPE'])
        self.add_env_var("FCST_FILE_TYPE", self.c_dict['FCST_FILE_TYPE'])
        self.add_env_var("OBS_FILE_TYPE", self.c_dict['OBS_FILE_TYPE'])

        # set climatology environment variables
        self.set_climo_env_vars()

        super().set_environment_variables(time_info)

    def process_fields(self, time_info, fcst_field, obs_field, ens_field=None):
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
        self.set_environment_variables(fcst_field, obs_field, ens_field, time_info)

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
