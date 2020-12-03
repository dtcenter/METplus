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
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace GridDiagWrapper
@brief Wraps the Grid-Diag tool
@endcode
'''


class GridDiagWrapper(CommandBuilder):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "grid_diag"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_GRID_DIAG_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['CONFIG_FILE'] = self.config.getraw('config', 'GRID_DIAG_CONFIG_FILE')
        if not c_dict['CONFIG_FILE']:
            self.log_error('GRID_DIAG_CONFIG_FILE required to run.')

        c_dict['INPUT_DIR'] = self.config.getdir('GRID_DIAG_INPUT_DIR', '')
        c_dict['INPUT_TEMPLATES'] = util.getlist(
            self.config.getraw('filename_templates',
                               'GRID_DIAG_INPUT_TEMPLATE'))

        c_dict['OUTPUT_DIR'] = self.config.getdir('GRID_DIAG_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'GRID_DIAG_OUTPUT_TEMPLATE')

        data_type = self.config.getstr('config', 'GRID_DIAG_INPUT_DATATYPE', '')
        if data_type:
            c_dict['DATA_FILE_TYPE'] = f"file_type = {data_type};"

        # values used in configuration file

        conf_value = self.config.getstr('config', 'GRID_DIAG_REGRID_METHOD', '')
        if conf_value:
            c_dict['REGRID_METHOD'] = f"method = {conf_value};"

        conf_value = self.config.getint('config', 'GRID_DIAG_REGRID_WIDTH')
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['REGRID_WIDTH'] = f"width = {str(conf_value)};"

        conf_value = self.config.getfloat('config', 'GRID_DIAG_REGRID_VLD_THRESH', )
        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            c_dict['REGRID_VLD_THRESH'] = f"vld_thresh = {str(conf_value)};"

        conf_value = self.config.getstr('config', 'GRID_DIAG_REGRID_SHAPE', '')
        if conf_value:
            c_dict['REGRID_SHAPE'] = f"shape = {conf_value};"

        conf_value = self.config.getstr('config', 'GRID_DIAG_REGRID_TO_GRID', '')
        if conf_value:
            c_dict['REGRID_TO_GRID'] = (
                f"to_grid = {self.format_regrid_to_grid(conf_value)};"
            )

        conf_value = self.config.getstr('config', 'GRID_DIAG_DESCRIPTION', '')
        if conf_value:
            c_dict['DESC'] = f'desc = "{util.remove_quotes(conf_value)}";'

        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'GRID_DIAG_VERIFICATION_MASK_TEMPLATE')

        return c_dict

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""

        self.add_env_var('DATA_FILE_TYPE',
                         self.c_dict.get('DATA_FILE_TYPE', ''))

        self.add_env_var('DATA_FIELD',
                         self.c_dict.get('DATA_FIELD', ''))

        regrid_dict_string = ''
        # if any regrid items are set, create the regrid dictionary and add them
        if (self.c_dict.get('REGRID_METHOD', '') or
                self.c_dict.get('REGRID_WIDTH', '') or
                self.c_dict.get('REGRID_VLD_THRESH', '') or
                self.c_dict.get('REGRID_SHAPE', '') or
                self.c_dict.get('REGRID_TO_GRID', '')
        ):
            regrid_dict_string = 'regrid = {'
            regrid_dict_string += f"{self.c_dict.get('REGRID_TO_GRID', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_METHOD', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_WIDTH', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_VLD_THRESH', '')}"
            regrid_dict_string += f"{self.c_dict.get('REGRID_SHAPE', '')}"
            regrid_dict_string += '}'

        self.add_env_var('REGRID_DICT',
                         regrid_dict_string)

        self.add_env_var('DESC',
                         self.c_dict.get('DESC', ''))

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

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param input_dict dictionary containing timing information
        """
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string

            time_info = time_util.ti_calculate(input_dict)

            self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ascii2nc
             Args:
                @param time_info dictionary containing timing information
        """
        self.clear()

        # get input files
        if not self.find_input_files(time_info):
            return

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
            that are formatted to be read by the MET config file. Set DATA_FIELD
            item of c_dict with the formatted list of fields.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns True if field list could be built, False if not.
        """

        field_list = util.parse_var_list(self.config,
                                         time_info,
                                         data_type='FCST',
                                         met_tool=self.app_name)
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

        self.c_dict['DATA_FIELD'] = ','.join(all_fields)

        return True

    def find_input_files(self, time_info):
        """! Loop over list of input templates and find files for each
            Args:
                @param time_info time dictionary to use for string substitution
                @returns Input file list if all files were found, None if not.
        """
        self.infiles = []
        for idx, input_template in enumerate(self.c_dict['INPUT_TEMPLATES']):
            self.c_dict['INPUT_TEMPLATE'] = input_template
            list_file = self.find_input_file_list(time_info, idx)

            if list_file is None:
                return None

            self.infiles.append(list_file)

        return self.infiles

    def find_input_file_list(self, time_info, idx):
        """!Get DECK file and list of input data files and set c_dict items.
            Args:
                @param time_info time dictionary to use for string substitution
                @param idx index to use for file list names
                @returns Input file list if all files were found, None if not.
        """
        all_input_files = []

        lead_seq = util.get_lead_sequence(self.config, time_info)
        for lead in lead_seq:
            time_info['lead'] = lead

            time_info = time_util.ti_calculate(time_info)

            # get a list of the input data files, write to an ascii file if there are more than one
            input_files = self.find_data(time_info, return_list=True)
            if not input_files:
                continue

            all_input_files.extend(input_files)

        if not all_input_files:
            return None

        # create an ascii file with a list of the input files
        list_file = self.write_list_file(f"grid_diag_data_files_idx{idx}_{time_info['valid_fmt']}.txt",
                                         all_input_files)
        return list_file

    def set_command_line_arguments(self, time_info):

        # add config file - passing through do_string_sub to get custom string if set
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
        self.args.append(f"-config {config_file}")
