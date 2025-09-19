"""
Program Name: mtd_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode time domain
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

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
        """!Create a configuration dictionary for the current execution.

        This function consolidates and prepares configuration settings based
        on the inputs and other context.

            @returns dict: The created configuration dictionary for the current run.
        """
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
            'FCST': {'prefix': 'FCST_MTD', 'required': False},
            'OBS': {'prefix': 'OBS_MTD', 'required': False},
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
                           met_tool=self.app_name,
                           var_options=self.var_options)
        )
        if not c_dict['VAR_LIST_TEMP']:
            self.log_error('No input fields were specified.'
                           'Must set [FCST/OBS]_VAR<n>_[NAME/LEVELS].')

        return c_dict

    def read_field_values(self, c_dict, read_type, write_type):
        """!Read FCST or OBS read type field values and sets FCST or OBS write
        type variables used in the wrapped MET config file.

        If single input mode is specified, the FCST and OBS values are set using
        values from that single input type. This function handles this situation.

        @param c_dict (dict) dictionary to set values from the METplusConfig
        @param read_type (str) input type to read values from, e.g. FCST or OBS
        @param write_type (str) input type to write values to, e.g. FCST or OBS
        @returns None
        """
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
        """!Process data for a single time step.

        This method calculates the valid time for the given time information,
        prepares input files (forecast and observation) for the current step,
        and processes fields for all thresholds. If input files are missing,
        it handles them as per configuration settings.

            @param time_info (dict) Information about the current time being processed.
        """
        # calculate valid based on first forecast lead
        lead_seq = get_lead_sequence(self.config, time_info)
        if not lead_seq:
            lead_seq = [0]
        first_lead = lead_seq[0]
        time_info['lead'] = first_lead
        first_valid_time_info = ti_calculate(time_info)

        # get formatted time to use to name file list files
        time_fmt = f"{first_valid_time_info['valid_fmt']}"

        for file_dict in self.c_dict['ALL_FILES']:
            var_info, inputs = self._prepare_inputs(file_dict, time_fmt)

            if not self._validate_inputs(inputs):
                continue

            arg_dict = {
                'obs_path': inputs.get('OBS'),
                'model_path': inputs.get('FCST'),
            }
            self.process_fields_one_thresh(first_valid_time_info, var_info,
                                           **arg_dict)

    def _prepare_inputs(self, file_dict, time_fmt):
        """!Prepare input files for observation and forecast.

        @param file_dict (dict): Dictionary with file information.
        @param time_fmt (str): Formatted time string.
        @returns tuple: A tuple containing var_info and inputs dictionary.
        """
        var_info = file_dict['var_list'][0]
        inputs = {}

        for data_type in ('FCST', 'OBS'):
            file_list = file_dict.get(data_type)
            if not file_list:
                continue

            if len(file_list) == 1:
                if not os.path.exists(file_list[0]):
                    self.log_error(f'{data_type} file does not exist: {file_list[0]}')
                    continue
                inputs[data_type] = file_list[0]
                continue

            file_ext = self.check_for_python_embedding(data_type, var_info)
            if not file_ext:
                continue

            dt = 'single' if self.c_dict['SINGLE_RUN'] else data_type
            outfile = f"{time_fmt}_mtd_{dt.lower()}_{file_ext}.txt"
            inputs[data_type] = self.write_list_file(outfile, file_list)

        return var_info, inputs

    def _validate_inputs(self, inputs):
        """!Validate if sufficient input files are available.

        @param inputs (dict): Dictionary with input file paths.
        @returns bool: True if inputs are valid, False otherwise.
        """
        if not inputs or (len(inputs) < 2 and not self.c_dict['SINGLE_RUN']):
            self.missing_input_count += 1
            msg = 'Could not find all required input files'
            if self.c_dict['ALLOW_MISSING_INPUTS']:
                self.logger.warning(msg)
            else:
                self.log_error(msg)
            return False

        return True

    def process_fields_one_thresh(self, first_valid_time_info, var_info,
                                  model_path, obs_path):
        """!Process fields for a specific threshold.

        This function performs processing tasks for fields at the given
        threshold level. It leverages forecast and observation data
        and applies the required transformations and operations.

            @param first_valid_time_info (dict) The valid time details for the current threshold.
            @param var_info (str) Information about the variable being processed.
            @param model_path (str) The path to the forecast file.
            @param obs_path (str) The path to the observation file.
        """
        fcst_field_list = self._process_field_list(
            var_info, 'FCST', model_path, self.c_dict.get('FCST_IS_PROB')
        )
        obs_field_list = self._process_field_list(
            var_info, 'OBS', obs_path, self.c_dict.get('OBS_IS_PROB')
        )

        fcst_field_list, obs_field_list = self._sync_field_lengths(
            fcst_field_list, obs_field_list
        )

        self._run_once_per_field(
            fcst_field_list, obs_field_list, first_valid_time_info, var_info,
            model_path, obs_path
        )

    def _process_field_list(self, var_info, data_type, path, is_probabilistic):
        """!Process the field information for each threshold.

        This function takes variable information, a data type, a path, and a flag indicating
        if the variable is probabilistic. It loops over each threshold in the field
        information and builds a formatted list of field info strings for each threshold.

            @param var_info (dict) Information about the variable being processed.
            @param data_type (str) The type of data (e.g., 'FCST' or 'OBS').
            @param path (str or None) The path to the field file, or None if not applicable.
            @param is_probabilistic (bool) Whether the field represents probabilistic data.
            @returns list: A list of formatted field info strings for each threshold.
        """
        if not path:
            return []

        field_list = []
        thresh_list = var_info[f'{data_type.lower()}_thresh']
        if is_probabilistic and not thresh_list:
            self.logger.error(f"Must specify thresholds for probabilistic {data_type} data")
            return []
        if not thresh_list:
            thresh_list = [""]
        for thresh in thresh_list:
            field = self.get_field_info(
                v_name=var_info[f'{data_type.lower()}_name'],
                v_level=var_info[f'{data_type.lower()}_level'],
                v_extra=var_info[f'{data_type.lower()}_extra'],
                v_thresh=[thresh],
                d_type=data_type
            )
            if not field:
                self.log_error(f"No {data_type.lower()} fields found")
                return []
            field_list.extend(field)
        return field_list

    def get_command(self):
        """!Builds the command to run the mtd application
           @rtype string
           @return string containing mtd command with arguments
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

    def get_files_from_time(self, time_info):
        """!Retrieve input files based on the provided time.

        This method overrides the `RuntimeFreqWrapper` class's method.
        It implements logic specific to fetching required input files within
        a defined time window and filters files based on input requirements.

        @param time_info (dict) Dictionary containing time-related metadata.
        @returns list: A list of input files applicable for the given time.
        """
        file_dict_list = super().get_files_from_time(time_info)
        if not self.c_dict['SINGLE_RUN']:
            for file_dict in file_dict_list:
                if file_dict.get('OBS') is None or file_dict.get('FCST') is None:
                    file_dict['OBS'] = None
                    file_dict['FCST'] = None
        return file_dict_list

    def _run_once_per_field(self, fcst_field_list, obs_field_list, time_info, var_info, model_path, obs_path):
        """!Loop over forecast and observation field lists. Build and run
        mtd command for each. The same input files are used for each run.

        @param fcst_field_list (list): List of forecast field strings.
        @param obs_field_list (list): List of observation field strings.
        @param time_info (dict): Dictionary containing time information.
        @param var_info (str): Dictionary containing field information.
        @param model_path (str): Path to forecast file.
        @param obs_path (str): Path to observation file.
        """
        for fcst_field, obs_field in zip(fcst_field_list, obs_field_list):
            self.format_field('FCST', fcst_field, is_list=False)
            self.format_field('OBS', obs_field, is_list=False)
            self.param = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
            self.set_current_field_config(var_info)
            self.set_environment_variables(time_info)
            if not self.find_and_check_output_file(time_info, is_directory=True):
                return
            if self.c_dict['SINGLE_RUN']:
                if self.c_dict.get('SINGLE_DATA_SRC') == 'OBS':
                    self.infiles.append(obs_path)
                else:
                    self.infiles.append(model_path)
            else:
                self.infiles.extend([model_path, obs_path])
            self.build()

    @staticmethod
    def _sync_field_lengths(fcst_field_list, obs_field_list):
        """!Synchronizes the lengths of two field lists by ensuring that if one
           list is empty, it is replaced with the contents of the other. This
           operation is performed in-place on the input lists.

           @param fcst_field_list (list): The forecast field list to synchronize.
           @param obs_field_list (list): The observation field list to synchronize.
           @returns tuple: A tuple containing the synchronized forecast and
            observation field lists.
        """
        if not fcst_field_list:
            fcst_field_list = obs_field_list
        elif not obs_field_list:
            obs_field_list = fcst_field_list
        return fcst_field_list, obs_field_list
