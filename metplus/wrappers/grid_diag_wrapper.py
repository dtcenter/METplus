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

from ..util import met_util as util
from ..util import time_util
from . import RuntimeFreqWrapper
from ..util import do_string_sub
from ..util import parse_var_list

'''!@namespace GridDiagWrapper
@brief Wraps the Grid-Diag tool
@endcode
'''


class GridDiagWrapper(RuntimeFreqWrapper):

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_DATA_DICT',
        'METPLUS_MASK_DICT',
    ]

    def __init__(self, config, instance=None, config_overrides=None):
        self.app_name = "grid_diag"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

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

        c_dict['OUTPUT_DIR'] = self.config.getdir('GRID_DIAG_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
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

        c_dict['MASK_POLY_TEMPLATE'] = self.read_mask_poly()

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

        # support old method of setting MET config variables
        self.add_env_var('DATA_FILE_TYPE',
                         self.c_dict.get('DATA_FILE_TYPE', ''))

        self.add_env_var('DATA_FIELD',
                         self.c_dict.get('DATA_FIELD', ''))

        self.add_env_var('DESC',
                         self.env_var_dict.get('METPLUS_DESC', ''))

        verif_mask = self.c_dict.get('VERIFICATION_MASK', '')
        if verif_mask:
            verif_mask = f'poly = {verif_mask};'

        self.add_env_var('VERIF_MASK',
                         verif_mask)

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
        """! Process runtime and try to build command to run ascii2nc
             Args:
                @param time_info dictionary containing timing information
        """

        # if custom is already set in time info, run for only that item
        # if not, loop over the CUSTOM_LOOP_LIST and process once for each
        if 'custom' in time_info:
            custom_loop_list = [time_info['custom']]
        else:
            custom_loop_list = self.c_dict['CUSTOM_LOOP_LIST']

        for custom_string in custom_loop_list:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            time_info['custom'] = custom_string
            self.run_at_time_custom(time_info)

    def run_at_time_custom(self, time_info):
        self.clear()

        # subset input files as appropriate
        input_list_dict = self.subset_input_files(time_info)
        if not input_list_dict:
            return

        for input_list_file in input_list_dict.values():
            self.infiles.append(input_list_file)

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get field information to set in MET config
        if not self.set_data_field(time_info):
            return

        # get verification mask if available
        self.get_verification_mask(time_info)

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
        field_list = util.sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)
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
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
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
        input_files = self.find_input_files(time_info)
        if input_files is None:
            return None

        for key, value in input_files.items():
            file_dict[key] = value

        return file_dict
