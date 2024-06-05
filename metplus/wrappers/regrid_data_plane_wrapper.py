'''
Program Name: regrid_data_plane.py
Contact(s): George McCabe
Abstract: Runs regrid_data_plane
History Log:  Initial version
Usage:
Parameters: None
Input Files: nc files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
'''

import os

from ..util import get_seconds_from_string, do_string_sub
from ..util import parse_var_list, get_process_list
from ..util import add_field_info_to_time_info, sub_var_list
from ..util import remove_quotes, split_level, format_level
from . import ReformatGriddedWrapper

# pylint:disable=pointless-string-statement
'''!@namespace RegridDataPlaneWrapper
@brief Wraps the MET tool regrid_data_plane to reformat gridded datasets
@endcode
'''


class RegridDataPlaneWrapper(ReformatGriddedWrapper):
    """! Wraps the MET tool regrid_data_plane to reformat gridded datasets"""
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    def __init__(self, config, instance=None):
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app = 'REGRID_DATA_PLANE'
        c_dict['VERBOSITY'] = self.config.getstr('config', f'LOG_{app}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['ONCE_PER_FIELD'] = self.config.getbool('config',
                                                       f'{app}_ONCE_PER_FIELD',
                                                       True)

        window_types = []
        for fcst_or_obs in ('FCST', 'OBS'):
            if not c_dict[f'{fcst_or_obs}_RUN']:
                continue

            window_types.append(fcst_or_obs)

            for in_or_out in ('INPUT', 'OUTPUT'):
                # read FCST/OBS_INPUT/OUTPUT_DIR
                c_dict[f'{fcst_or_obs}_{in_or_out}_DIR'] = (
                    self.config.getdir(f'{fcst_or_obs}_{app}_{in_or_out}_DIR')
                )

                # read FCST/OBS_INPUT/OUTPUT_TEMPLATE
                name = self.config.get_mp_config_name(
                    [f'{fcst_or_obs}_{app}_{in_or_out}_TEMPLATE',
                     f'{fcst_or_obs}_{app}_TEMPLATE']
                )
                if not name:
                    self.log_error(f"{fcst_or_obs}_{app}_{in_or_out}_TEMPLATE "
                                   f"must be set if {fcst_or_obs}_{app}_RUN")
                    continue

                c_dict[f'{fcst_or_obs}_{in_or_out}_TEMPLATE'] = (
                    self.config.getraw('config', name)
                )

                # set list of variables (fields)
                c_dict[f'VAR_LIST_{fcst_or_obs}'] = parse_var_list(
                    self.config,
                    data_type=fcst_or_obs,
                    met_tool=self.app_name
                )

        self.handle_file_window_variables(c_dict, data_types=window_types)

        c_dict['VERIFICATION_GRID'] = \
            self.config.getraw('config', 'REGRID_DATA_PLANE_VERIF_GRID', '')

        c_dict['METHOD'] = \
          self.config.getstr('config', 'REGRID_DATA_PLANE_METHOD', '')

        c_dict['WIDTH'] = \
         self.config.getint('config', 'REGRID_DATA_PLANE_WIDTH', 1)

        c_dict['GAUSSIAN_DX'] = \
         self.config.getstr('config', 'REGRID_DATA_PLANE_GAUSSIAN_DX', '')

        c_dict['GAUSSIAN_RADIUS'] = \
         self.config.getstr('config', 'REGRID_DATA_PLANE_GAUSSIAN_RADIUS', '')

        # only check if VERIFICATION_GRID is set if running the tool from the process list
        # RegridDataPlane can be called from other tools like CustomIngest, which sets the
        # verification grid itself
        if 'RegridDataPlane' in get_process_list(self.config):
            if not c_dict['VERIFICATION_GRID']:
                self.log_error("REGRID_DATA_PLANE_VERIF_GRID must be set.")
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

    def handle_output_file(self, time_info, field_info, data_type):
        """! Add field level to time_info dict so it can be referenced in
            filename template, then set output file path and check if it
             should be skipped if it exists.

             @param time_info time dictionary used for string substitution
             @param field_info field dictionary to read level information
             @param data_type type of data to process, i.e. FCST or OBS
             @returns True if command should be run, False if it should
              not be run
        """
        _, level = split_level(field_info[f'{data_type.lower()}_level'])
        time_info['level'] = get_seconds_from_string(level, 'H')
        return self.find_and_check_output_file(time_info)

    def run_once_per_field(self, time_info, var_list, data_type):
        """! Loop over fields and run command for each.

            @param time_info time dictionary used for string substitution
            @param var_list list of field dictionaries to process
            @param data_type type of data to process, i.e. FCST or OBS
        """
        return_status = True
        for field_info in var_list:
            self.args.clear()

            self.set_command_line_arguments()

            add_field_info_to_time_info(time_info, field_info)

            input_name = field_info[f'{data_type.lower()}_name']
            input_level = field_info[f'{data_type.lower()}_level']
            input_extra = field_info.get(f'{data_type.lower()}_extra', '')
            field_text_list = self.get_field_info(data_type,
                                                  input_name,
                                                  v_level=input_level,
                                                  v_extra=input_extra)

            for field_text in field_text_list:
                self.args.append(f"-field '{field_text.strip('{ }')}'")

            output_name = field_info.get(f'{data_type.lower()}_output_name')
            if output_name is None:
                output_name = input_name

            self.args.append("-name " + output_name)

            if not self.handle_output_file(time_info,
                                           field_info,
                                           data_type):
                return False

            if not self.build():
                return_status = False

        return return_status

    def get_output_names(self, var_list, data_type):
        """! Get list of output names from var_list. If there are any
         duplicate output names, create new output names
         using input name and level. This is done to prevent the app
         from crashing when trying to write 2 fields with the same name.
         Rename NetCDF level names to avoid using
         a field name with * or , in the name.

            @param var_list list of field info dictionaries
            @param data_type type of data to process, i.e. FCST or OBS
            @returns list of output names
        """
        output_names = []

        # get list of output names using {DATA_TYPE}_output_name or input name
        for field_info in var_list:
            # get list of output names
            output_name = field_info.get(f'{data_type.lower()}_output_name')

            # use input name if output name is not set
            if output_name is None:
                output_name = field_info[f'{data_type.lower()}_name']

            output_names.append(output_name)

        # if there are any duplicates, clear list and build names using
        # input name and input level
        if len(output_names) != len(set(output_names)):
            self.logger.warning("Duplicate output names found. "
                                "Replacing output names to use "
                                "{input_name}_{input_level} instead.")
            output_names.clear()
            for field_info in var_list:
                input_name = field_info[f'{data_type.lower()}_name']
                input_level = field_info[f'{data_type.lower()}_level']
                input_level = format_level(input_level)
                output_name = f"{input_name}_{input_level}"
                output_names.append(output_name)

        return output_names

    def run_once_for_all_fields(self, time_info, var_list, data_type):
        """!Loop over fields to add each field info, then run command once to
            process all fields.
            Args:
                @param time_info time dictionary used for string substitution
                @param var_list list of field dictionaries to process
                @param data_type type of data to process, i.e. FCST or OBS
        """
        self.set_command_line_arguments()

        for field_info in var_list:
            add_field_info_to_time_info(time_info, field_info)

            input_name = field_info[f'{data_type.lower()}_name']
            input_level = field_info[f'{data_type.lower()}_level']
            input_extra = field_info.get(f'{data_type.lower()}_extra', '')
            field_text_list = self.get_field_info(data_type,
                                                  input_name,
                                                  v_level=input_level,
                                                  v_extra=input_extra)
            for field_text in field_text_list:
                self.args.append(f"-field '{field_text.strip('{ }')}'")

        output_names = self.get_output_names(var_list, data_type)

        # add list of output names
        self.args.append("-name " + ','.join(output_names))

        if not self.handle_output_file(time_info, var_list[0], data_type):
            return False

        # build and run commands
        return self.build()

    def run_at_time_once(self, time_info):
        """!Build command or commands to run at the given run time

            @param time_info time dictionary used for string substitution
        """
        self.clear()
        var_list = sub_var_list(self.c_dict['VAR_LIST'], time_info)
        data_type = self.c_dict['DATA_SRC']

        # set output dir and template to current data type's values
        self.c_dict['OUTPUT_DIR'] = self.c_dict.get(f'{data_type}_OUTPUT_DIR')
        self.c_dict['OUTPUT_TEMPLATE'] = (
            self.c_dict.get(f'{data_type}_OUTPUT_TEMPLATE')
        )

        # if no field info or input field configs are set, error and return
        if not var_list:
            self.log_error('No input fields were specified to '
                           'RegridDataPlane. You must set '
                           f'{data_type}_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_'
                           f'NAME or {data_type}_VAR<n>_NAME.')
            return False

        add_field_info_to_time_info(time_info, var_list[0])
        self.run_count += 1
        if not self.find_input_files(time_info, data_type):
            self.missing_input_count += 1
            return False

        # set environment variables
        self.set_environment_variables(time_info)

        # determine if running once for all fields or once per field
        # if running once per field, loop over field list and run once for each
        if self.c_dict['ONCE_PER_FIELD']:
            return self.run_once_per_field(time_info, var_list, data_type)

        # if not running once per field, process all fields and run once
        return self.run_once_for_all_fields(time_info, var_list, data_type)

    def find_input_files(self, time_info, data_type):
        """!Get input file and verification grid to process. Use the first
         field in the list to substitute level if that is provided in the
         filename template

         @param time_info time dictionary used for string substitution
         @param data_type type of data to process, i.e. FCST or OBS
         @returns list of input files if files were found, None if not
         """
        input_path = self.find_data(time_info, data_type=data_type)
        if not input_path:
            return None

        self.infiles.append(input_path)

        grid = do_string_sub(self.c_dict['VERIFICATION_GRID'], **time_info)

        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{grid}"')

        return time_info

    def set_command_line_arguments(self):
        """!Returns False if command should not be run"""

        # set regrid method is explicitly set
        if self.c_dict['METHOD']:
            self.args.append("-method {}".format(self.c_dict['METHOD']))

        # set width argument
        self.args.append("-width {}".format(self.c_dict['WIDTH']))

        if self.c_dict['GAUSSIAN_DX']:
            self.args.append(f"-gaussian_dx {self.c_dict['GAUSSIAN_DX']}")

        if self.c_dict['GAUSSIAN_RADIUS']:
            self.args.append(f"-gaussian_radius {self.c_dict['GAUSSIAN_RADIUS']}")

        return True

    def set_field_command_line_arguments(self, field_info, data_type):
        """!Sets command line arguments for an input field.
            Args:
                @param field_info field dictionary to read level information
                @param data_type type of data to process, i.e. FCST or OBS
                @returns input name to be used as output name if not explicitly set
        """

        field_name = field_info[f'{data_type.lower()}_name']
        # strip off quotes around input_level if found
        input_level = remove_quotes(field_info[f'{data_type.lower()}_level'])

        field_text = f"-field 'name=\"{field_name}\";"

        if input_level:
            field_text +=f" level=\"{input_level}\";"

        field_text += "'"
        self.args.append(field_text)

        return field_name
