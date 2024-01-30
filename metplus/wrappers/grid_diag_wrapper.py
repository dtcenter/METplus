"""grid_diag
Program Name: grid_diag_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs grid_diag
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub, parse_var_list, sub_var_list
from . import RuntimeFreqWrapper

'''!@namespace GridDiagWrapper
@brief Wraps the Grid-Diag tool
@endcode
'''


class GridDiagWrapper(RuntimeFreqWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_PER_INIT_OR_VALID'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_DATA_DICT',
        'METPLUS_MASK_DICT',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'DESC',
        'DATA_FIELD',
        'DATA_FILE_TYPE',
        'VERIF_MASK',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "grid_diag"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GRID_DIAG_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('GridDiagConfig_wrapped')

        c_dict['INPUT_DIR'] = self.config.getdir('GRID_DIAG_INPUT_DIR', '')
        self.get_input_templates(c_dict)

        # error if no input templates are set
        if not c_dict['TEMPLATE_DICT']:
            self.log_error('Must set GRID_DIAG_INPUT_TEMPLATE to run')

        c_dict['OUTPUT_DIR'] = self.config.getdir('GRID_DIAG_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'GRID_DIAG_OUTPUT_TEMPLATE')
        )

        data_type = self.config.getstr('config',
                                       'GRID_DIAG_INPUT_DATATYPE',
                                       '')
        if data_type:
            c_dict['DATA_FILE_TYPE'] = f"file_type = {data_type};"

        # values used in configuration file

        # set regrid dictionary values
        self.handle_regrid(c_dict)

        self.handle_description()

        self.handle_mask(single_value=True)

        self.handle_censor_val_and_thresh()

        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config,
                                                 data_type='FCST',
                                                 met_tool=self.app_name)

        # handle setting VERIF_MASK for old wrapped MET config files
        self.add_met_config(name='poly',
                            data_type='list',
                            env_var_name='METPLUS_VERIF_MASK',
                            metplus_configs=['GRID_DIAG_MASK_POLY',
                                             'GRID_DIAG_POLY',
                                             ('GRID_DIAG_'
                                              'VERIFICATION_MASK_TEMPLATE')],
                            extra_args={'allow_empty': True})
        self.env_var_dict['VERIF_MASK'] = (
            self.env_var_dict.get('METPLUS_VERIF_MASK', '')
        )

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
             Reformat as needed. Print list of variables that were set and
              their values.

            @param time_info dictionary containing timing info from current run
        """
        data_dict = self.format_met_config_dict(self.c_dict,
                                                'data',
                                                ['DATA_FILE_TYPE',
                                                 'DATA_FIELD_FMT'])
        self.env_var_dict['METPLUS_DATA_DICT'] = data_dict
        super().set_environment_variables(time_info)

    def get_command(self):
        cmd = self.app_path

        # add input files
        for infile in self.infiles:
            cmd += f" -data {infile}"

        # add other arguments
        cmd += f" {' '.join(self.args)}"

        # add output path
        out_path = self.get_output_path()
        cmd += f' -out {out_path}'

        # add verbosity
        cmd += f" -v {self.c_dict['VERBOSITY']}"
        return cmd

    def run_at_time_once(self, time_info):
        # subset input files as appropriate
        self.run_count += 1
        input_list_dict = self.subset_input_files(time_info)
        if not input_list_dict:
            self.missing_input_count += 1
            return

        for input_list_file in input_list_dict.values():
            self.infiles.append(input_list_file)

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get field information to set in MET config
        if not self.set_data_field(time_info):
            return

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        self.build()

    def set_data_field(self, time_info):
        """!Get list of fields from config to process. Build list of field info
            that are formatted to be read by the MET config file. Set
            DATA_FIELD item of c_dict with the formatted list of fields.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns True if field list could be built, False if not.
        """
        field_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)
        if not field_list:
            self.log_error("Could not get field information from config.")
            return False

        all_fields = []
        for field in field_list:
            field_list = self.get_field_info(d_type='FCST',
                                             v_name=field['fcst_name'],
                                             v_level=field['fcst_level'],
                                             v_extra=field['fcst_extra'])
            if field_list is None:
                return False

            all_fields.extend(field_list)

        data_field = ','.join(all_fields)
        self.c_dict['DATA_FIELD_FMT'] = f"field = [ {data_field} ];"

        # support old method of setting environment variable
        self.c_dict['DATA_FIELD'] = data_field

        return True

    def set_command_line_arguments(self, time_info):
        """! add config file passing through do_string_sub to get custom
         string if set

            @param time_info dictionary containing time information
        """
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")

    def get_files_from_time(self, time_info):
        """! Create dictionary containing time information (key time_info) and
             any relevant files for that runtime. The parent implementation of
             this function creates a dictionary and adds the time_info to it.
             This wrapper gets all files for the current runtime and adds it to
             the dictionary with key 'input'

             @param time_info dictionary containing time information
             @returns dictionary containing time_info dict and any relevant
             files with a key representing a description of that file
        """
        file_dict = super().get_files_from_time(time_info)
        input_files = self.get_input_files(time_info)
        if input_files is None:
            return None

        for key, value in input_files.items():
            file_dict[key] = value

        return file_dict
