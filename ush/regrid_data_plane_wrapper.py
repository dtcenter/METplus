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
import met_util as util
import string_template_substitution as sts
from reformat_gridded_wrapper import ReformatGriddedWrapper

'''!@namespace RegridDataPlaneWrapper
@brief Wraps the MET tool regrid_data_plane to reformat gridded datasets
@endcode
'''
class RegridDataPlaneWrapper(ReformatGriddedWrapper):
    '''!Wraps the MET tool regrid_data_plane to reformat gridded datasets
    '''
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        app = 'REGRID_DATA_PLANE'
        c_dict['VERBOSITY'] = self.config.getstr('config', f'LOG_{app}_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['SKIP_IF_OUTPUT_EXISTS'] = \
          self.config.getbool('config', f'{app}_SKIP_IF_OUTPUT_EXISTS',
                              False)
        if self.config.has_option('filename_templates',
                                  f'FCST_{app}_INPUT_TEMPLATE'):
            c_dict['FCST_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   f'FCST_{app}_INPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    f'FCST_{app}_TEMPLATE'):
            c_dict['FCST_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   f'FCST_{app}_TEMPLATE')
        else:
            c_dict['FCST_INPUT_TEMPLATE'] = None

        if self.config.has_option('filename_templates',
                                  'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE'):
            c_dict['OBS_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'OBS_REGRID_DATA_PLANE_TEMPLATE'):
            c_dict['OBS_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_TEMPLATE')
        else:
            c_dict['OBS_INPUT_TEMPLATE'] = None

        if self.config.has_option('filename_templates',
                                  'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'):
            c_dict['FCST_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'FCST_REGRID_DATA_PLANE_TEMPLATE'):
            c_dict['FCST_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_TEMPLATE')
        else:
            c_dict['FCST_OUTPUT_TEMPLATE'] = None

        if self.config.has_option('filename_templates',
                                  'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'):
            c_dict['OBS_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'OBS_REGRID_DATA_PLANE_TEMPLATE'):
            c_dict['OBS_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_TEMPLATE')
        else:
            c_dict['OBS_OUTPUT_TEMPLATE'] = None

        if self.config.getbool('config', 'FCST_REGRID_DATA_PLANE_RUN', False):
            c_dict['FCST_INPUT_DIR'] = \
                self.config.getdir('FCST_REGRID_DATA_PLANE_INPUT_DIR', '')
            c_dict['FCST_OUTPUT_DIR'] = \
                self.config.getdir('FCST_REGRID_DATA_PLANE_OUTPUT_DIR', '')

        if self.config.getbool('config', 'OBS_REGRID_DATA_PLANE_RUN', False):
            c_dict['OBS_INPUT_DIR'] = \
                self.config.getdir('OBS_REGRID_DATA_PLANE_INPUT_DIR', '')

            c_dict['OBS_OUTPUT_DIR'] = \
                self.config.getdir('OBS_REGRID_DATA_PLANE_OUTPUT_DIR', '')

        c_dict['VERIFICATION_GRID'] = \
            self.config.getstr('config', 'REGRID_DATA_PLANE_VERIF_GRID', '')

        c_dict['METHOD'] = \
          self.config.getstr('config', 'REGRID_DATA_PLANE_METHOD', '')

        c_dict['WIDTH'] = \
         self.config.getint('config', 'REGRID_DATA_PLANE_WIDTH', 1)

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

    def run_at_time_once(self, time_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti time_info object containing timing information
                @param v var_info object containing variable information
        """
        self.clear()

        # exit if input or output template is not set
        if self.c_dict[dtype+'_INPUT_TEMPLATE'] == '':
            self.log_error('Must set {}_REGRID_DATA_PLANE_INPUT_TEMPLATE'.format(dtype) +\
                              ' in config file')
            exit(1)

        if self.c_dict[dtype+'_OUTPUT_TEMPLATE'] == '':
            self.log_error('Must set {}_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'.format(dtype) +\
                              ' in config file')
            exit(1)

        if self.c_dict['VERIFICATION_GRID'] == '':
            self.log_error('No verification grid specified! ' + \
                              'Set REGRID_DATA_PLANE_VERIF_GRID')
            exit(1)


        # check if any RDP VAR<n>_INPUT_FIELD_* configs are set
        # get a list of the indices that are set
        input_regex = f'{dtype}_{self.app_name.upper()}_'+r'VAR(\d)_INPUT_NAME'
        rdp_input_indices = \
          util.find_regex_in_config_section(input_regex, self.config, 'config')

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
        field_name = sts.StringSub(self.logger,
                                   field_name,
                                   **time_info).do_string_sub()

        input_level = sts.StringSub(self.logger,
                                    input_level,
                                    **time_info).do_string_sub()

        output_name = sts.StringSub(self.logger,
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

        input_file = sts.StringSub(self.logger,
                                   input_template,
                                   level=(int(f_level)*3600),
                                   **time_info).do_string_sub()
        infile = os.path.join(input_dir,  input_file)

        infile = \
          util.preprocess_file(infile,
                               self.config.getstr('config',
                                                  dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE',
                                                  ''),
                               self.config)

        if infile is not None:
            self.infiles.append(infile)
        else:
            self.log_error('Could not find input file in {} matching template {}'
                              .format(input_dir, input_template))
            return False

        verif_grid = self.c_dict['VERIFICATION_GRID']
        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{verif_grid}"')

        # get output path and check if it already exists, skip if necessary
        outfile = sts.StringSub(self.logger,
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
            name = "{:s}_{:s}".format(field_name, str(level))
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

        return True

if __name__ == "__main__":
    util.run_stand_alone("regrid_data_plane_wrapper", "RegridDataPlane")
