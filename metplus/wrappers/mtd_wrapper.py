'''
Program Name: mtd_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode time domain
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

import os

from ..util import get_lead_sequence, sub_var_list
from ..util import ti_calculate, getlist
from ..util import do_string_sub, skip_time
from ..util import parse_var_list, add_field_info_to_time_info
from . import CompareGriddedWrapper


class MTDWrapper(CompareGriddedWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_PER_INIT_OR_VALID'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_OBTYPE',
        'METPLUS_REGRID_DICT',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_FCST_FIELD',
        'METPLUS_FCST_CONV_RADIUS',
        'METPLUS_FCST_CONV_THRESH',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_OBS_FIELD',
        'METPLUS_OBS_CONV_RADIUS',
        'METPLUS_OBS_CONV_THRESH',
        'METPLUS_MIN_VOLUME',
        'METPLUS_OUTPUT_PREFIX',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'mtd'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)
        self.fcst_file = None
        self.obs_file = None

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_MTD_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # set to prevent find_obs from getting multiple files within
        #  a time window. Does not refer to time series of files
        c_dict['ALLOW_MULTIPLE_FILES'] = False
        c_dict['ONCE_PER_FIELD'] = True

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('MTD_OUTPUT_DIR',
                               self.config.getdir('OUTPUT_BASE'))
        )
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'MTD_OUTPUT_TEMPLATE')
        )

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('MTDConfig_wrapped')

        # new method of reading/setting MET config values
        self.add_met_config(name='min_volume', data_type='int')

        # old approach to reading/setting MET config values
        c_dict['MIN_VOLUME'] = self.config.getstr('config', 'MTD_MIN_VOLUME', '2000')

        c_dict['SINGLE_RUN'] = (
            self.config.getbool('config', 'MTD_SINGLE_RUN', False)
        )
        if c_dict['SINGLE_RUN']:
            c_dict['SINGLE_DATA_SRC'] = (
                self.config.getstr('config', 'MTD_SINGLE_DATA_SRC', '')
            )
            if not c_dict['SINGLE_DATA_SRC']:
                self.log_error('Must set MTD_SINGLE_DATA_SRC if '
                               'MTD_SINGLE_RUN is True')

        self.get_input_templates(c_dict)

        # if single run for OBS, read OBS values into FCST keys
        read_type = 'FCST'
        if c_dict['SINGLE_RUN'] and c_dict.get('SINGLE_DATA_SRC') == 'OBS':
            read_type = 'OBS'

        self.read_field_values(c_dict, read_type, 'FCST')

        # if not running single mode, also read OBS values
        if not c_dict['SINGLE_RUN']:
            self.read_field_values(c_dict, 'OBS', 'OBS')

        c_dict['VAR_LIST_TEMP'] = (
            parse_var_list(self.config,
                           data_type=c_dict.get('SINGLE_DATA_SRC'),
                           met_tool=self.app_name)
        )
        if not c_dict['VAR_LIST_TEMP']:
            self.log_error('No input fields were specified.'
                           'Must set [FCST/OBS]_VAR<n>_[NAME/LEVELS].')

        return c_dict

    def read_field_values(self, c_dict, read_type, write_type):

        c_dict[f'{write_type}_INPUT_DATATYPE'] = (
            self.config.getstr('config', f'{read_type}_MTD_INPUT_DATATYPE', '')
        )

        self.add_met_config(name='conv_radius',
                            data_type='string',
                            env_var_name=f'METPLUS_{write_type}_CONV_RADIUS',
                            metplus_configs=[f'{read_type}_MTD_CONV_RADIUS',
                                             'MTD_CONV_RADIUS'],
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='conv_thresh',
                            data_type='thresh',
                            env_var_name=f'METPLUS_{write_type}_CONV_THRESH',
                            metplus_configs=[f'{read_type}_MTD_CONV_THRESH',
                                             'MTD_CONV_THRESH'])

        # support old method of setting env vars
        conf_value = (
            self.config.getstr('config', f'{read_type}_MTD_CONV_RADIUS', '')
        )
        if not conf_value:
            conf_value = self.config.getstr('config', 'MTD_CONV_RADIUS', '')
        c_dict[f'{write_type}_CONV_RADIUS'] = conf_value

        # set OBS values if single run to support old method
        if c_dict['SINGLE_RUN']:
            c_dict['OBS_CONV_RADIUS'] = conf_value

        conf_value = (
            self.config.getstr('config', f'{read_type}_MTD_CONV_THRESH', '')
        )
        if not conf_value:
            conf_value = self.config.getstr('config', 'MTD_CONV_THRESH', '')
        c_dict[f'{write_type}_CONV_THRESH'] = conf_value

        # set OBS values if single run to support old method
        if c_dict['SINGLE_RUN']:
            c_dict['OBS_CONV_THRESH'] = conf_value

    def run_at_time_once(self, time_info):
        # calculate valid based on first forecast lead
        lead_seq = get_lead_sequence(self.config, time_info)
        if not lead_seq:
            lead_seq = [0]
        first_lead = lead_seq[0]
        time_info['lead'] = first_lead
        first_valid_time_info = ti_calculate(time_info)

        # get formatted time to use to name file list files
        time_fmt = f"{first_valid_time_info['valid_fmt']}"

        # loop through the files found for each field (var_info)
        for file_dict in self.c_dict['ALL_FILES']:
            var_info = file_dict['var_info']
            inputs = {}
            for data_type in ('FCST', 'OBS'):
                file_list = file_dict.get(data_type)
                if not file_list:
                    continue
                if len(file_list) == 1:
                    if not os.path.exists(file_list[0]):
                        self.log_error(f'{data_type} file does not exist: '
                                       f'{file_list[0]}')
                        continue
                    inputs[data_type] = file_list[0]
                    continue

                file_ext = self.check_for_python_embedding(data_type, var_info)
                if not file_ext:
                    continue

                dt = 'single' if self.c_dict['SINGLE_RUN'] else data_type
                outfile = f"{time_fmt}_mtd_{dt.lower()}_{file_ext}.txt"
                inputs[data_type] = self.write_list_file(outfile, file_list)

            if not inputs:
                self.log_error('Input files not found')
                continue
            if len(inputs) < 2 and not self.c_dict['SINGLE_RUN']:
                self.log_error('Could not find all required inputs files')
                continue
            arg_dict = {
                'obs_path': inputs.get('OBS'),
                'model_path': inputs.get('FCST'),
            }
            self.process_fields_one_thresh(first_valid_time_info, var_info,
                                           **arg_dict)

    def process_fields_one_thresh(self, first_valid_time_info, var_info,
                                  model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param first_valid_time_info dictionary containing timing information
                @param var_info object containing variable information
                @param model_path forecast file list path
                @param obs_path observation file list path
        """
        fcst_field_list = []
        obs_field_list = []

        if model_path:
            fcst_thresh_list = var_info['fcst_thresh']

            # if probabilistic forecast and no thresholds specified,
            # error and skip
            if self.c_dict['FCST_IS_PROB'] and not fcst_thresh_list:
                self.logger.error("Must specify thresholds for "
                                  "probabilistic forecast data")
                return

            # if no thresholds are specified, run once
            if not fcst_thresh_list:
                fcst_thresh_list = [""]

            # loop over thresholds and build field list with one thresh per item
            for fcst_thresh in fcst_thresh_list:
                fcst_field = (
                    self.get_field_info(v_name=var_info['fcst_name'],
                                        v_level=var_info['fcst_level'],
                                        v_extra=var_info['fcst_extra'],
                                        v_thresh=[fcst_thresh],
                                        d_type='FCST')
                )

                if fcst_field is None:
                    self.log_error("No forecast fields found")
                    return

                fcst_field_list.extend(fcst_field)

        if obs_path:
            obs_thresh_list = var_info['obs_thresh']

            if self.c_dict['OBS_IS_PROB'] and not obs_thresh_list:
                self.logger.error("Must specify thresholds for "
                                  "probabilistic obs data")
                return

            # if no thresholds are specified, run once
            if not obs_thresh_list:
                obs_thresh_list = [""]

            # loop over thresholds and build field list w/ one thresh per item
            for obs_thresh in obs_thresh_list:
                obs_field = self.get_field_info(v_name=var_info['obs_name'],
                                                v_level=var_info['obs_level'],
                                                v_extra=var_info['obs_extra'],
                                                v_thresh=[obs_thresh],
                                                d_type='OBS')

                if obs_field is None:
                    self.log_error("No observation fields found")
                    return

                obs_field_list.extend(obs_field)

            # if FCST is not set, set it to the OBS field list so
            # the lists are the same length
            if not fcst_field_list:
                fcst_field_list = obs_field_list

        else:
            # if OBS is not set, set it to the FCST field list so
            # the lists are the same length
            obs_field_list = fcst_field_list

        # loop through fields and call MTD
        for fcst_field, obs_field in zip(fcst_field_list, obs_field_list):
            self.format_field('FCST', fcst_field, is_list=False)
            self.format_field('OBS',  obs_field,  is_list=False)

            self.param = do_string_sub(self.c_dict['CONFIG_FILE'],
                                       **first_valid_time_info)

            self.set_current_field_config(var_info)
            self.set_environment_variables(first_valid_time_info)

            if not self.find_and_check_output_file(first_valid_time_info,
                                                   is_directory=True):
                return

            fcst_file = model_path
            if self.c_dict['SINGLE_RUN']:
                if self.c_dict.get('SINGLE_DATA_SRC') == 'OBS':
                    fcst_file = obs_path
            else:
                self.obs_file = obs_path

            self.fcst_file = fcst_file
            self.build()

    def clear(self):
        super().clear()
        self.fcst_file = None
        self.obs_file = None

    def set_environment_variables(self, time_info):
        # old method of setting MET config variables
        self.add_env_var("FCST_FIELD",
                         self.c_dict.get('FCST_FIELD', ''))
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))
        self.add_env_var("OBS_CONV_RADIUS",
                         self.c_dict.get('OBS_CONV_RADIUS', ''))
        self.add_env_var("FCST_CONV_RADIUS",
                         self.c_dict.get('FCST_CONV_RADIUS', ''))
        self.add_env_var("OBS_CONV_THRESH",
                         self.c_dict.get('OBS_CONV_THRESH', ''))
        self.add_env_var("FCST_CONV_THRESH",
                         self.c_dict.get('FCST_CONV_THRESH', ''))

        self.add_env_var("MIN_VOLUME", self.c_dict["MIN_VOLUME"])

        self.add_env_var("FCST_FILE_TYPE",
                         self.c_dict.get('FCST_FILE_TYPE', ''))
        self.add_env_var("OBS_FILE_TYPE",
                         self.c_dict.get('OBS_FILE_TYPE', ''))

        super().set_environment_variables(time_info)

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']} "

        for a in self.args:
            cmd += a + " "

        if self.c_dict['SINGLE_RUN']:
            cmd += '-single ' + self.fcst_file + ' '
        else:
            cmd += '-fcst ' + self.fcst_file + ' '
            cmd += '-obs ' + self.obs_file + ' '

        cmd += '-config ' + self.param + ' '

        if self.outdir != "":
            cmd += '-outdir {}'.format(self.outdir)

        return cmd

    def get_input_templates(self, c_dict):
        input_types = ['FCST', 'OBS']
        if c_dict.get('SINGLE_RUN', False):
            input_types = [c_dict['SINGLE_DATA_SRC']]

        app = self.app_name.upper()
        template_dict = {}
        for in_type in input_types:
            template_path = (
                self.config.getraw('config',
                                   f'{in_type}_{app}_INPUT_FILE_LIST')
            )
            if template_path:
                c_dict['EXPLICIT_FILE_LIST'] = True
            else:
                in_dir = self.config.getdir(f'{in_type}_{app}_INPUT_DIR', '')
                templates = getlist(
                    self.config.getraw('config',
                                       f'{in_type}_{app}_INPUT_TEMPLATE')
                )
                template_list = [os.path.join(in_dir, template)
                                 for template in templates]
                template_path = ','.join(template_list)

            template_dict[in_type] = template_path

        c_dict['TEMPLATE_DICT'] = template_dict

    def get_files_from_time(self, time_info):
        """! Create dictionary containing time information (key time_info) and
             any relevant files for that runtime. The parent implementation of
             this function creates a dictionary and adds the time_info to it.
             This wrapper gets all files for the current runtime and adds it to
             the dictionary with keys 'FCST' and 'OBS'

             @param time_info dictionary containing time information
             @returns dictionary containing time_info dict and any relevant
             files with a key representing a description of that file
        """
        if self.c_dict.get('ONCE_PER_FIELD', False):
            var_list = sub_var_list(self.c_dict.get('VAR_LIST_TEMP'), time_info)
        else:
            var_list = [None]

        # create a dictionary for each field (var) with time_info and files
        file_dict_list = []
        for var_info in var_list:
            file_dict = {'var_info': var_info}
            if var_info:
                add_field_info_to_time_info(time_info, var_info)

            input_files = self.get_input_files(time_info, fill_missing=True)
            # only add all input files if none are missing
            no_missing = True
            if input_files:
                for key, value in input_files.items():
                    if 'missing' in value:
                        no_missing = False
                    file_dict[key] = value
            if no_missing:
                file_dict_list.append(file_dict)

        return file_dict_list

    def _update_list_with_new_files(self, time_info, list_to_update):
        new_files = self.get_files_from_time(time_info)
        if not new_files:
            return

        # if list to update is empty, copy new items into list
        if not list_to_update:
            for new_file in new_files:
                list_to_update.append(new_file.copy())
            return

        # if list to update is not empty, add new files to each file list,
        # make sure new files correspond to the correct field (var)
        assert len(list_to_update) == len(new_files)
        for new_file, existing_item in zip(new_files, list_to_update):
            assert new_file['var_info'] == existing_item['var_info']
            for key, value in new_file.items():
                if key == 'var_info':
                    continue
                existing_item[key].extend(value)
