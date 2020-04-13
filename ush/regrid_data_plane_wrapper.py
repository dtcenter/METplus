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

import metplus_check_python_version

import os
import met_util as util
from string_template_substitution import StringSub
from reformat_gridded_wrapper import ReformatGriddedWrapper

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

        if self.config.getbool('config', 'FCST_REGRID_DATA_PLANE_RUN', False):
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

    def get_explicit_field_names(self, index, d_type):
        """! Get output field name from [FCST/OBS]_<APP_NAME>_*
             Use input/output field name if it exists, then use generic
             field name, then return empty string if neither are set
             Args:
               @param index integer n corresponding to [FCST/OBS]_VAR<n>_*
               @param d_type type of data being processed (FCST or OBS)
               @return tuple containing input and output field names to use
        """
        app = self.app_name.upper()
        input_field_name = \
            self.config.getraw('config',
                               f'{d_type}_{app}_VAR{index}_INPUT_FIELD_NAME',
                               '')
        if not input_field_name:
            input_field_name = \
                self.config.getraw('config',
                                   f'{d_type}_{app}_VAR{index}_FIELD_NAME',
                                   '')

        input_field_level = \
            self.config.getraw('config',
                               f'{d_type}_{app}_VAR{index}_INPUT_LEVEL',
                               '')

        output_field_name = \
            self.config.getraw('config',
                               f'{d_type}_{app}_VAR{index}_OUTPUT_FIELD_NAME',
                               '')
        if not output_field_name:
            output_field_name = \
                self.config.getraw('config',
                                   f'{d_type}_{app}_VAR{index}_FIELD_NAME',
                                   '')

        return input_field_name, input_field_level, output_field_name

    def get_input_indicies(self, data_type):
        # check if any RDP VAR<n>_INPUT_FIELD_* configs are set
        # get a list of the indices that are set
        input_regex = f'({data_type})_{self.app_name.upper()}_'+r'VAR(\d+)_INPUT_FIELD_NAME'
        rdp_input_indices = \
          util.find_indices_in_config_section(input_regex, self.config, 'config').keys()

        # check RDP VAR<n>_FIELD_NAME if INPUT_FIELD is not set
        if not rdp_input_indices:
            input_regex = f'({data_type})_{self.app_name.upper()}_'+r'VAR(\d+)_FIELD_NAME'
            rdp_input_indices = \
              util.find_indices_in_config_section(input_regex, self.config, 'config').keys()

        return rdp_input_indices

    def get_field_info_list(self, var_list, data_type):
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

        # replace values in field info list from RDP explicit values if they are set
        for index in rdp_input_indices:

            input_name, input_level, output_name = (
                self.get_explicit_field_names(index, dtype)
                )

            # if index exists in field info list, replace values if they are set
            found_index = False
            for field_info in field_info_list:
                if field_info['index'] == index:
                    found_index = True
                    if input_name:
                        field_info[f'{data_type}_name'] = input_name

                    if input_level:
                        field_info[f'{data_type}_level'] = input_name

                    # also add output name
                    if output_name:
                        field_info[f'{data_type}_output_name'] = output_name

            # if index does not exist, add an entry to the list
            if not found_index:
                field_info = {f"{data_type}_name": input_name,
                              f"{data_type}_level": input_level,
                              'index': index,
                            }

                if output_name:
                    field_info[f"{data_type}_output_name"] = output_name

                field_info_list.append(field_info)

        return field_info_list

    def run_at_time_all_vars(self, time_info, var_list, data_type):
        self.clear()

        field_info_list = self.get_field_info_list(var_list, data_type)
        if not field_info_list:
            self.log_error("Could not build field info list")
            return

        # add first field level to time_info dict so it can be referenced in filename template
        level = field_info_list[0][f'{data_type}_level']
        time_info['level'] = time_util.get_seconds_from_string(level, 'H')

        if not self.find_input_files(time_info, data_type, field_info_list):
            self.log_error(f"Could not find {dtype} file {full_path} using template {input_template}")
            return

        if not self.find_and_check_output_file(time_info):
            return

        # set environment variables

        # determine if running once for all fields or once per field
        # if running once per field, loop over field list and run once for each
        if self.c_dict.get('ONCE_PER_FIELD', True):

        # if not, process all fields and run once
        else:

        # set command line arguments

        # build and run commands

    def find_input_files(self, time_info, data_type, field_info_list):
        """!Get input file and verification grid to process. Use the first field in the list to substitute
            level if that is provided in the filename template"""
        # get list of files even if only one is found (return_list=True)
#        input_path = self.find_data(time_info, var_info=field_info_list[0], data_type=data_type, return_list=True)
        input_path = self.find_data(time_info, var_info=field_info_list[0], data_type=data_type)
        if not input_path:
            return None

#        self.infiles.extend(input_path)
        self.infiles.append(input_path)

        verif_grid = StringSub(self.logger,
                               self.c_dict['VERIFICATION_GRID'],
                               **time_info).do_string_sub()

        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{verif_grid}"')

        return self.infiles

    def run_at_time_once(self, time_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti time_info object containing timing information
                @param v var_info object containing variable information
        """
        self.clear()

        # check if any RDP VAR<n>_INPUT_FIELD_* configs are set
        # get a list of the indices that are set
        input_regex = f'({dtype})_{self.app_name.upper()}_'+r'VAR(\d+)_INPUT_FIELD_NAME'
        rdp_input_indices = \
          util.find_indices_in_config_section(input_regex, self.config, 'config').keys()

        # check RDP VAR<n>_FIELD_NAME if INPUT_FIELD is not set
        if not rdp_input_indices:
            input_regex = f'({dtype})_{self.app_name.upper()}_'+r'VAR(\d+)_FIELD_NAME'
            rdp_input_indices = \
              util.find_indices_in_config_section(input_regex, self.config, 'config').keys()

        # if no field info or input field configs are set, error and return
        if var_info is None and not rdp_input_indices:
            self.log_error('No input fields were specified to RegridDataPlane. You must set either '
                           f'{dtype}_REGRID_DATA_PLANE_VAR<n>_INPUT_FIELD_NAME or '
                           f'{dtype}_VAR<n>_NAME.')
            return

        # if var info is set, build command using that item's info
        # unless the corresponding index RDP_VAR<index>_INPUT_* info is set

        # set output name
        # if [FCST/OBS]_REGRID_DATA_PLANE_OUTPUT_FIELD_NAME is not explicitly set,
        # use the input field name. If input comes from a python script, report error
        if var_info is not None:
            index = var_info['index']
            input_name, input_level, output_name = \
              self.get_explicit_field_names(index, dtype)

            # get input field name/level from [FCST/OBS]_VAR<n>_* if not set explicitly
            if not input_name:
                input_name = var_info[f'{dtype.lower()}_name']

            if not input_level:
                input_level = var_info[f'{dtype.lower()}_level']

            if not output_name and util.is_python_script(input_name):
                    self.log_error('Must explicitly set '
                                      f'{dtype}_REGRID_DATA_PLANE_VAR{index}_'
                                      'OUTPUT_FIELD_NAME '
                                      'if input field comes from a python script.')
                    return

            field_info = {'input_name': input_name,
                          'input_level': input_level,
                          'output_name': output_name}

            if not self.set_arguments(field_info, time_info, dtype):
                # do not run if error or output should be skipped
                return

            # try to build and run command
            self.build_and_run_command()

        # if var info is not set, build command for each RDP_VAR<n>_INPUT_NAME
        else:
            for index in rdp_input_indices:
                self.clear()
                input_name, input_level, output_name = \
                  self.get_explicit_field_names(index, dtype)

                field_info = {'input_name': input_name,
                              'input_level': input_level,
                              'output_name': output_name}

                if not self.set_arguments(field_info, time_info, dtype):
                    # do not run if error or output should be skipped
                    continue

                # try to build and run command
                self.build_and_run_command()

    def set_arguments(self, field_info, time_info, dtype):
        """!Returns False if command should not be run"""
        field_name = field_info['input_name']
        input_level = field_info['input_level']
        output_name = field_info['output_name']

        # run through StringSub in case the field name contains a template
        field_name = StringSub(self.logger,
                               field_name,
                               **time_info).do_string_sub()

        input_level = StringSub(self.logger,
                                input_level,
                                **time_info).do_string_sub()

        output_name = StringSub(self.logger,
                                output_name,
                                **time_info).do_string_sub()

        # strip off quotes around input_level if found
        input_level = util.remove_quotes(input_level)

        _, level = util.split_level(input_level)

        input_dir = self.c_dict[dtype+'_INPUT_DIR']
        input_template = self.c_dict[dtype+'_INPUT_TEMPLATE']
        output_dir = self.c_dict[dtype+'_OUTPUT_DIR']
        output_template = self.c_dict[dtype+'_OUTPUT_TEMPLATE']

        if not level.isdigit():
            f_level = '0'
        else:
            f_level = level

        input_file = StringSub(self.logger,
                               input_template,
                               level=(int(f_level)*3600),
                               **time_info).do_string_sub()
        full_path = os.path.join(input_dir, input_file)

        infile = \
          util.preprocess_file(full_path,
                               self.config.getstr('config',
                                                  dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE',
                                                  ''),
                               self.config)

        if infile is not None:
            self.infiles.append(infile)
        else:
            self.log_error(f"Could not find {dtype} file {full_path} using template {input_template}")
            return False

        verif_grid = StringSub(self.logger,
                               self.c_dict['VERIFICATION_GRID'],
                               **time_info).do_string_sub()

        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{verif_grid}"')

        # get output path and check if it already exists, skip if necessary
        outfile = StringSub(self.logger,
                            output_template,
                            level=(int(f_level)*3600),
                            **time_info).do_string_sub()
        self.set_output_path(os.path.join(output_dir, outfile))

        outpath = self.get_output_path()
        if os.path.exists(outpath) and \
          self.c_dict['SKIP_IF_OUTPUT_EXISTS'] is True:
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS to True to process'
                              .format(outpath))
            return False

        # if using python script to supply input data, just set field name
        # if PcpCombine has been run on this data, set field name = name_level
        # and level=(*,*), otherwise set name=name and level=level
        if util.is_python_script(field_name):
            self.args.append(f"-field 'name=\"{field_name}\";'")
        elif self.config.getbool('config', dtype + '_PCP_COMBINE_RUN', False):
            if len(str(level)) > 0:
               name = "{:s}_{:s}".format(field_name, str(level))
            else:
               name = "{:s}".format(field_name)
            self.args.append(f"-field 'name=\"{name}\"; level=\"(*,*)\";'")
        else:
            name = "{:s}".format(field_name)
            self.args.append(f"-field 'name=\"{name}\"; level=\"{input_level}\";'")

        if not output_name:
            output_name = name

        # set regrid method is explicitly set
        if self.c_dict['METHOD'] != '':
            self.args.append("-method {}".format(self.c_dict['METHOD']))

        # set width argument
        self.args.append("-width {}".format(self.c_dict['WIDTH']))

        self.args.append("-name " + output_name)

        if self.c_dict['GAUSSIAN_DX']:
            self.args.append(f"-gaussian_dx {self.c_dict['GAUSSIAN_DX']}")

        if self.c_dict['GAUSSIAN_RADIUS']:
            self.args.append(f"-gaussian_radius {self.c_dict['GAUSSIAN_RADIUS']}")

        return True

if __name__ == "__main__":
    util.run_stand_alone(__file__, "RegridDataPlane")
