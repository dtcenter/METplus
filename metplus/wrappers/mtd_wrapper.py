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

from ..util import get_lead_sequence, ti_calculate, do_string_sub, parse_var_list
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

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'MODEL',
        'OBTYPE',
        'REGRID_TO_GRID',
        'FCST_FIELD',
        'OBS_FIELD',
        'FCST_CONV_RADIUS',
        'OBS_CONV_RADIUS',
        'FCST_CONV_THRESH',
        'OBS_CONV_THRESH',
        'MIN_VOLUME',
        'FCST_FILE_TYPE',
        'OBS_FILE_TYPE',
        'OUTPUT_PREFIX',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'mtd'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

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

        input_info = {
            'FCST': {'prefix': 'FCST_MTD', 'required': True},
            'OBS': {'prefix': 'OBS_MTD', 'required': True},
        }

        c_dict['SINGLE_RUN'] = (
            self.config.getbool('config', 'MTD_SINGLE_RUN', False)
        )
        if c_dict['SINGLE_RUN']:
            single_src = self.config.getraw('config', 'MTD_SINGLE_DATA_SRC')
            c_dict['SINGLE_DATA_SRC'] = single_src
            if not single_src:
                self.log_error('Must set MTD_SINGLE_DATA_SRC if '
                               'MTD_SINGLE_RUN is True')
            elif single_src not in ('FCST', 'OBS'):
                self.log_error('MTD_SINGLE_DATA_SRC must be FCST or OBS.'
                               f' It is set to {single_src}')

            # do not read input templates for other data source if single mode
            if single_src == 'FCST':
                del input_info['OBS']
            else:
                del input_info['FCST']

        self.get_input_templates(c_dict, input_info)

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

            if not inputs or (len(inputs) < 2 and not self.c_dict['SINGLE_RUN']):
                self.missing_input_count += 1
                msg = 'Could not find all required inputs files'
                if self.c_dict['ALLOW_MISSING_INPUTS']:
                    self.logger.warning(msg)
                else:
                    self.log_error(msg)
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

            if self.c_dict['SINGLE_RUN']:
                if self.c_dict.get('SINGLE_DATA_SRC') == 'OBS':
                    self.infiles.append(obs_path)
                else:
                    self.infiles.append(model_path)
            else:
                self.infiles.extend([model_path, obs_path])

            self.build()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']} "

        for a in self.args:
            cmd += a + " "

        if self.c_dict['SINGLE_RUN']:
            cmd += f'-single {self.infiles[0]} '
        else:
            cmd += f'-fcst {self.infiles[0]} -obs {self.infiles[1]} '

        cmd += '-config ' + self.param + ' '

        if self.outdir != "":
            cmd += '-outdir {}'.format(self.outdir)

        return cmd
