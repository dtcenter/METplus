#!/usr/bin/env python

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

#pylint:disable=unused-import
import metplus_check_python_version

import met_util as util
import time_util
from string_template_substitution import StringSub
from reformat_gridded_wrapper import ReformatGriddedWrapper

# pylint:disable=pointless-string-statement
'''!@namespace RegridDataPlaneWrapper
@brief Wraps the MET tool regrid_data_plane to reformat gridded datasets
@endcode
'''
class RegridDataPlaneWrapper(ReformatGriddedWrapper):
    '''!Wraps the MET tool regrid_data_plane to reformat gridded datasets
    '''
    def __init__(self, config, logger):
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)
        super().__init__(config, logger)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app = 'REGRID_DATA_PLANE'
        c_dict['VERBOSITY'] = self.config.getstr('config', f'LOG_{app}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['SKIP_IF_OUTPUT_EXISTS'] = \
          self.config.getbool('config', f'{app}_SKIP_IF_OUTPUT_EXISTS',
                              False)

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

        # run through StringSub in case the field name contains a template
        input_field_name = StringSub(self.logger,
                                     input_field_name,
                                     **time_info).do_string_sub()
        input_field_level = StringSub(self.logger,
                                      input_field_level,
                                      **time_info).do_string_sub()

        output_field_name = StringSub(self.logger,
                                      output_field_name,
                                      **time_info).do_string_sub()

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

            if input_level:
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

    def run_at_time_once(self, time_info, var_list, data_type):
        self.clear()

        # set output dir and template to current data type's values
        self.c_dict['OUTPUT_DIR'] = self.c_dict[f'{data_type}_OUTPUT_DIR']
        self.c_dict['OUTPUT_TEMPLATE'] = self.c_dict[f'{data_type}_OUTPUT_TEMPLATE']

        field_info_list = self.get_field_info_list(var_list, data_type, time_info)
        if not field_info_list:
            self.log_error("Could not build field info list")
            return

        if not self.find_input_files(time_info, data_type, field_info_list):
            return

        # set environment variables
        self.set_environment_variables(time_info)

        # determine if running once for all fields or once per field
        # if running once per field, loop over field list and run once for each
        if self.c_dict['ONCE_PER_FIELD']:
            # set command line arguments that apply to each run

            for field_info in field_info_list:
                self.args.clear()
                self.add_field_info_to_time_info(time_info, field_info)
                self.set_command_line_arguments()
                self.set_field_command_line_arguments(field_info, data_type)

                # set output name if set in field info or use input name if not
                output_name = field_info.get(f'{data_type}_output_name', None)
                if not output_name:
                    output_name = field_info[f'{data_type.lower()}_name']
                self.args.append("-name " + output_name)

                # add first field level to time_info dict so it can be referenced in filename template
                level = field_info[f'{data_type.lower()}_level']
                time_info['level'] = time_util.get_seconds_from_string(level, 'H')
                if not self.find_and_check_output_file(time_info):
                    return

                self.build_and_run_command()

            return

        # if not running once per field, process all fields and run once
        self.set_command_line_arguments()
        output_names = []
        for field_info in field_info_list:
            self.add_field_info_to_time_info(time_info, field_info)
            # get list of output names
            output_name = field_info.get(f'{data_type}_output_name', None)
            if not output_name:
                output_name = field_info[f'{data_type.lower()}_name']
            output_names.append(output_name)

            self.set_field_command_line_arguments(field_info, data_type)

        # add list of output names
        self.args.append("-name " + ','.join(output_names))

        # add first field level to time_info dict so it can be referenced in filename template
        level = field_info[f'{data_type.lower()}_level']
        time_info['level'] = time_util.get_seconds_from_string(level, 'H')
        if not self.find_and_check_output_file(time_info):
            return

        # build and run commands
        self.build_and_run_command()

    def find_input_files(self, time_info, data_type, field_info_list):
        """!Get input file and verification grid to process. Use the first field in the
            list to substitute level if that is provided in the filename template"""
        input_path = self.find_data(time_info, var_info=field_info_list[0], data_type=data_type)
        if not input_path:
            return None

        self.infiles.append(input_path)

        verif_grid = StringSub(self.logger,
                               self.c_dict['VERIFICATION_GRID'],
                               **time_info).do_string_sub()

        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{verif_grid}"')

        return self.infiles

    def set_command_line_arguments(self):
        """!Returns False if command should not be run"""

        # set regrid method is explicitly set
        if self.c_dict['METHOD'] != '':
            self.args.append("-method {}".format(self.c_dict['METHOD']))

        # set width argument
        self.args.append("-width {}".format(self.c_dict['WIDTH']))

        if self.c_dict['GAUSSIAN_DX']:
            self.args.append(f"-gaussian_dx {self.c_dict['GAUSSIAN_DX']}")

        if self.c_dict['GAUSSIAN_RADIUS']:
            self.args.append(f"-gaussian_radius {self.c_dict['GAUSSIAN_RADIUS']}")

        return True

    def set_field_command_line_arguments(self, field_info, data_type):
        """!Returns False if command should not be run"""

        field_name = field_info[f'{data_type.lower()}_name']
        # strip off quotes around input_level if found
        input_level = util.remove_quotes(field_info[f'{data_type.lower()}_level'])

        _, level = util.split_level(input_level)

        # if using python script to supply input data, just set field name
        # if PcpCombine has been run on this data, set field name = name_level
        # and level=(*,*), otherwise set name=name and level=level
        if util.is_python_script(field_name):
            self.args.append(f"-field 'name=\"{field_name}\";'")
        elif self.config.getbool('config', data_type + '_PCP_COMBINE_RUN', False):
            if len(str(level)) > 0:
                name = "{:s}_{:s}".format(field_name, str(level))
            else:
                name = "{:s}".format(field_name)
            self.args.append(f"-field 'name=\"{name}\"; level=\"(*,*)\";'")
        else:
            name = "{:s}".format(field_name)
            self.args.append(f"-field 'name=\"{name}\"; level=\"{input_level}\";'")

if __name__ == "__main__":
    util.run_stand_alone(__file__, "RegridDataPlane")
