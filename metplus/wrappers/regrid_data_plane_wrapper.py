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

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import ReformatGriddedWrapper

# pylint:disable=pointless-string-statement
'''!@namespace RegridDataPlaneWrapper
@brief Wraps the MET tool regrid_data_plane to reformat gridded datasets
@endcode
'''
class RegridDataPlaneWrapper(ReformatGriddedWrapper):
    '''!Wraps the MET tool regrid_data_plane to reformat gridded datasets
    '''
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app = 'REGRID_DATA_PLANE'
        c_dict['VERBOSITY'] = self.config.getstr('config', f'LOG_{app}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['ONCE_PER_FIELD'] = self.config.getbool('config',
                                                       f'{app}_ONCE_PER_FIELD',
                                                       True)

        c_dict['FCST_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               f'FCST_{app}_INPUT_TEMPLATE',
                               '')

        if not c_dict['FCST_INPUT_TEMPLATE']:
            c_dict['FCST_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   f'FCST_{app}_TEMPLATE',
                                   '')

        c_dict['OBS_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE',
                               '')

        if not c_dict['OBS_INPUT_TEMPLATE']:
            c_dict['OBS_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_TEMPLATE',
                                   '')

        c_dict['FCST_OUTPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE',
                               '')

        if not c_dict['FCST_OUTPUT_TEMPLATE']:
            c_dict['FCST_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_TEMPLATE',
                                   '')

        c_dict['OBS_OUTPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE',
                               '')

        if not c_dict['OBS_OUTPUT_TEMPLATE']:
            c_dict['OBS_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_TEMPLATE',
                                   '')

        window_types = []
        if self.config.getbool('config', 'FCST_REGRID_DATA_PLANE_RUN', False):
            window_types.append('FCST')
            c_dict['FCST_INPUT_DIR'] = \
                self.config.getdir('FCST_REGRID_DATA_PLANE_INPUT_DIR', '')

            c_dict['FCST_OUTPUT_DIR'] = \
                self.config.getdir('FCST_REGRID_DATA_PLANE_OUTPUT_DIR', '')

            if not c_dict['FCST_INPUT_TEMPLATE']:
                self.log_error("FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE must be set if "
                               "FCST_REGRID_DATA_PLANE_RUN is True")
                self.isOK = False

            if not c_dict['FCST_OUTPUT_TEMPLATE']:
                self.log_error("FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE must be set if "
                               "FCST_REGRID_DATA_PLANE_RUN is True")
                self.isOK = False


        if self.config.getbool('config', 'OBS_REGRID_DATA_PLANE_RUN', False):
            window_types.append('OBS')
            c_dict['OBS_INPUT_DIR'] = \
                self.config.getdir('OBS_REGRID_DATA_PLANE_INPUT_DIR', '')

            c_dict['OBS_OUTPUT_DIR'] = \
                self.config.getdir('OBS_REGRID_DATA_PLANE_OUTPUT_DIR', '')

            if not c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE must be set if "
                               "OBS_REGRID_DATA_PLANE_RUN is True")
                self.isOK = False

            if not c_dict['OBS_OUTPUT_TEMPLATE']:
                self.log_error("OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE must be set if "
                               "OBS_REGRID_DATA_PLANE_RUN is True")
                self.isOK = False

        self.handle_window_variables(c_dict, self.app_name, dtypes=window_types)

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
        if 'RegridDataPlane' in util.get_process_list(self.config):
            if not c_dict['VERIFICATION_GRID']:
                self.log_error("REGRID_DATA_PLANE_VERIF_GRID must be set.")
                self.isOK = False

        return c_dict

    def get_explicit_field_names(self, index, data_type, time_info):
        """! Get output field name from [FCST/OBS]_<APP_NAME>_*
             Use input/output field name if it exists, then use generic
             field name, then return empty string if neither are set
             Args:
               @param index integer n corresponding to [FCST/OBS]_VAR<n>_*
               @param data_type type of data being processed (FCST or OBS)
               @return tuple containing input and output field names to use
        """
        app = self.app_name.upper()
        input_field_name = \
            self.config.getraw('config',
                               f'{data_type}_{app}_VAR{index}_INPUT_FIELD_NAME',
                               '')
        if not input_field_name:
            input_field_name = \
                self.config.getraw('config',
                                   f'{data_type}_{app}_VAR{index}_FIELD_NAME',
                                   '')

        input_field_level = \
            self.config.getraw('config',
                               f'{data_type}_{app}_VAR{index}_INPUT_LEVEL',
                               '')

        output_field_name = \
            self.config.getraw('config',
                               f'{data_type}_{app}_VAR{index}_OUTPUT_FIELD_NAME',
                               '')
        if not output_field_name:
            output_field_name = \
                self.config.getraw('config',
                                   f'{data_type}_{app}_VAR{index}_FIELD_NAME',
                                   '')

        # run through do_string_sub in case the field name contains a template
        input_field_name = do_string_sub(input_field_name,
                                         **time_info)
        input_field_level = do_string_sub(input_field_level,
                                          **time_info)

        output_field_name = do_string_sub(output_field_name,
                                          **time_info)

        return input_field_name, input_field_level, output_field_name

    def get_input_indices(self, data_type):
        """!Find all n in [FCST/OBS]_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME or
           [FCST/OBS]_REGRID_DATA_PLANE_VAR<n>_FIELD_NAME. Used to see if there are
           any fields defined that don't correspond to an item in [FCST/OBS]_VAR<n>_
           variables.
           Args:
               @param data_type type of field to look for (FCST or OBS)
               @returns list of indices that are set
        """
        input_regex = f'({data_type})_{self.app_name.upper()}_'+r'VAR(\d+)_INPUT_FIELD_NAME'
        rdp_input_indices = \
          util.find_indices_in_config_section(input_regex, self.config, 'config').keys()

        # check RDP VAR<n>_FIELD_NAME if INPUT_FIELD is not set
        if not rdp_input_indices:
            input_regex = f'({data_type})_{self.app_name.upper()}_'+r'VAR(\d+)_FIELD_NAME'
            rdp_input_indices = \
              util.find_indices_in_config_section(input_regex, self.config, 'config').keys()

        return rdp_input_indices

    def get_field_info_list(self, var_list, data_type, time_info):
        """!Read field list (var_list) generated from [FCST/OBS]_VAR<n>_ variables replace values
            from [FCST/OBS]_REGRID_DATA_PLANE_VAR<n>_INPUT_ variables if they are set
            Args:
                @param var_list list of field info objects populated from
                [FCST/OBS]_VAR<n>_ variables
                @param data_type type of data to process, i.e. FCST or OBS
                @returns field list values combined with wrapper specific info"""
        # get list of fields to process
        rdp_input_indices = self.get_input_indices(data_type)

        # if no field info or input field configs are set, error and return
        if not var_list and not rdp_input_indices:
            self.log_error('No input fields were specified to RegridDataPlane. You must set either '
                           f'{data_type}_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME or '
                           f'{data_type}_VAR<n>_NAME.')
            return None

        # get list of fields from var_list and rdp_input_indices
        field_info_list = var_list if var_list else []

        var_indices = []
        # if index exists in field info list, replace values if they are set
        for field_info in field_info_list:

            input_name, input_level, output_name = (
                self.get_explicit_field_names(field_info['index'], data_type, time_info)
            )

            if input_name:
                field_info[f'{data_type.lower()}_name'] = input_name
            else:
                input_name = field_info[f'{data_type.lower()}_name']
                # option to supress warnings can be set in wrapper that calls
                # RegridDataPlane to prevent these warnings from showing up
                if self.c_dict.get('SHOW_WARNINGS', True):
                    msg = (f"{data_type}_REGRID_DATA_PLANE_"
                           f"VAR{field_info['index']}_NAME not set. "
                           f"Using name = {input_name} from "
                           f"{data_type}_VAR{field_info['index']}_NAME")
                    self.logger.warning(msg)

            if util.is_python_script(input_name):
                field_info[f'{data_type.lower()}_level'] = ''
            elif input_level:
                field_info[f'{data_type.lower()}_level'] = input_level

            # also add output name
            if output_name:
                field_info[f'{data_type.lower()}_output_name'] = output_name

            var_indices.append(field_info['index'])

        # get list of indices from wrapper-specific that are not in var list
        rdp_only_indices = list(set(rdp_input_indices) - set(var_indices))

        # if index does not exist, add an entry to the list
        for rdp_only_index in rdp_only_indices:
            input_name, input_level, output_name = (
                self.get_explicit_field_names(rdp_only_index, data_type, time_info)
            )

            field_info = {f"{data_type.lower()}_name": input_name,
                          f"{data_type.lower()}_level": input_level,
                          'index': rdp_only_index,
                          }

            if output_name:
                field_info[f"{data_type.lower()}_output_name"] = output_name

            field_info_list.append(field_info)

        return field_info_list

    def get_output_name(self, field_info, data_type, input_name):
        """!Set output name if set in field info or use input name if not
            Args:
               @param field_info field dictionary to read level information
               @param data_type type of data to process, i.e. FCST or OBS
               @param input_name name of input field to be used as output name not explicitly set
               @returns output name
        """
        output_name = field_info.get(f'{data_type.lower()}_output_name', None)
        if not output_name:
            if self.c_dict.get('SHOW_WARNINGS', True):
                msg = (f'{data_type}_REGRID_DATA_PLANE_OUTPUT_NAME not set. '
                       f'Using {input_name} as the output name.')
                self.logger.warning(msg)

            output_name = input_name

        return output_name

    def handle_output_file(self, time_info, field_info, data_type):
        """!Add field level to time_info dict so it can be referenced in
            filename template, then set output file path and check if it should be skipped
            if it exists.
            Args:
                 @param time_info time dictionary used for string substitution
                 @param field_info field dictionary to read level information
                 @param data_type type of data to process, i.e. FCST or OBS
                 @returns True if command should be run, False if it should not be run
        """
        _, level = util.split_level(field_info[f'{data_type.lower()}_level'])
        time_info['level'] = time_util.get_seconds_from_string(level, 'H')
        return self.find_and_check_output_file(time_info)

    def run_once_per_field(self, time_info, field_info_list, data_type):
        """!Loop over fields and run command for each.
            Args:
                @param time_info time dictionary used for string substitution
                @param field_info_list list of field dictionaries to process
                @param data_type type of data to process, i.e. FCST or OBS
        """
        return_status = True
        for field_info in field_info_list:
            self.args.clear()

            self.set_command_line_arguments()

            self.add_field_info_to_time_info(time_info,
                                             field_info)

            input_name = field_info[f'{data_type.lower()}_name']
            input_level = field_info[f'{data_type.lower()}_level']
            field_text_list = self.get_field_info(data_type,
                                                  input_name,
                                                  input_level)

            for field_text in field_text_list:
                self.args.append(f"-field '{field_text.strip('{ }')}'")

            field_name = input_name

            self.args.append("-name " + self.get_output_name(field_info,
                                                             data_type,
                                                             field_name))

            if not self.handle_output_file(time_info,
                                           field_info,
                                           data_type):
                return False

            if not self.build():
                return_status = False

        return return_status

    def run_once_for_all_fields(self, time_info, field_info_list, data_type):
        """!Loop over fields to add each field info, then run command once to
            process all fields.
            Args:
                @param time_info time dictionary used for string substitution
                @param field_info_list list of field dictionaries to process
                @param data_type type of data to process, i.e. FCST or OBS
        """
        self.set_command_line_arguments()
        output_names = []
        for field_info in field_info_list:
            self.add_field_info_to_time_info(time_info,
                                             field_info)

            input_name = field_info[f'{data_type.lower()}_name']
            input_level = field_info[f'{data_type.lower()}_level']
            field_text_list = self.get_field_info(data_type,
                                                  input_name,
                                                  input_level)
            for field_text in field_text_list:
                self.args.append(f"-field '{field_text.strip('{ }')}'")

            field_name = input_name

            # get list of output names
            output_names.append(self.get_output_name(field_info,
                                                     data_type,
                                                     field_name))


        # add list of output names
        self.args.append("-name " + ','.join(output_names))

        if not self.handle_output_file(time_info,
                                       field_info_list[0],
                                       data_type):
            return False

        # build and run commands
        return self.build()

    def run_at_time_once(self, time_info, var_list, data_type):
        """!Build command or commands to run at the given run time
            Args:
                @param time_info time dictionary used for string substitution
                @param var_list list of field dictionaries to process
                @param data_type type of data to process, i.e. FCST or OBS
        """
        self.clear()

        # set output dir and template to current data type's values
        self.c_dict['OUTPUT_DIR'] = self.c_dict[f'{data_type}_OUTPUT_DIR']
        self.c_dict['OUTPUT_TEMPLATE'] = self.c_dict[f'{data_type}_OUTPUT_TEMPLATE']

        field_info_list = self.get_field_info_list(var_list, data_type, time_info)
        if not field_info_list:
            self.log_error("Could not build field info list")
            return False

        if not self.find_input_files(time_info, data_type, field_info_list):
            return False

        # set environment variables
        self.set_environment_variables(time_info)

        # determine if running once for all fields or once per field
        # if running once per field, loop over field list and run once for each
        if self.c_dict['ONCE_PER_FIELD']:
            return self.run_once_per_field(time_info, field_info_list, data_type)

        # if not running once per field, process all fields and run once
        return self.run_once_for_all_fields(time_info, field_info_list, data_type)

    def find_input_files(self, time_info, data_type, field_info_list):
        """!Get input file and verification grid to process. Use the first field in the
            list to substitute level if that is provided in the filename template"""
        input_path = self.find_data(time_info, var_info=field_info_list[0], data_type=data_type)
        if not input_path:
            return None

        self.infiles.append(input_path)

        verif_grid = do_string_sub(self.c_dict['VERIFICATION_GRID'],
                                   **time_info)

        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{verif_grid}"')

        return self.infiles

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
        input_level = util.remove_quotes(field_info[f'{data_type.lower()}_level'])

        field_text = f"-field 'name=\"{field_name}\";"

        if input_level:
            field_text +=f" level=\"{input_level}\";"

        field_text += "'"
        self.args.append(field_text)

        return field_name
