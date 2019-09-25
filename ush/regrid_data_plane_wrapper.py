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

from __future__ import (print_function, division)

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
        super(RegridDataPlaneWrapper, self).__init__(config, logger)
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super(RegridDataPlaneWrapper, self).create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_REGRID_DATA_PLANE_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        app = 'REGRID_DATA_PLANE'
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

        if self.config.has_option('config',
                                  'FCST_REGRID_DATA_PLANE_FIELD_NAME'):
            c_dict['FCST_OUTPUT_FIELD_NAME'] = \
                self.config.getstr('config',
                                   'FCST_REGRID_DATA_PLANE_OUTPUT_FIELD_NAME')
        elif self.config.has_option('config',
                                    'FCST_REGRID_DATA_PLANE_FIELD_NAME'):
            c_dict['FCST_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_TEMPLATE')
        else:
            c_dict['FCST_OUTPUT_TEMPLATE'] = None

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
            self.config.getstr('config',
                               f'{d_type}_{app}_VAR{index}_INPUT_FIELD_NAME',
                               '')

        if input_field_name == '':
            input_field_name = \
                self.config.getstr('config',
                                   f'{d_type}_{app}_VAR{index}_FIELD_NAME',
                                   '')

        output_field_name = \
            self.config.getstr('config',
                               f'{d_type}_{app}_VAR{index}_OUTPUT_FIELD_NAME',
                               '')

        if output_field_name == '':
            output_field_name = \
                self.config.getstr('config',
                                   f'{d_type}_{app}_VAR{index}_FIELD_NAME',
                                   '')

        return input_field_name, output_field_name

    def run_at_time_once(self, time_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti time_info object containing timing information
                @param v var_info object containing variable information
        """
        self.clear()

        if var_info is None:
            self.logger.error('No fields were specified using [FCST/OBS]_VAR<n>_NAME.')
            return

        if dtype == "FCST":
            field_name = var_info['fcst_name']
            v_level = var_info['fcst_level']
        else:
            field_name = var_info['obs_name']
            v_level = var_info['obs_level']

        # run through StringSub in case the field name contains a template
        field_name = sts.StringSub(self.logger, field_name, **time_info).do_string_sub()

        _, level = util.split_level(v_level)

        if self.c_dict[dtype+'_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_INPUT_TEMPLATE'.format(dtype) +\
                              ' in config file')
            exit(1)

        if self.c_dict[dtype+'_OUTPUT_TEMPLATE'] == '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'.format(dtype) +\
                              ' in config file')
            exit(1)

        input_dir = self.c_dict[dtype+'_INPUT_DIR']
        input_template = self.c_dict[dtype+'_INPUT_TEMPLATE']
        output_dir = self.c_dict[dtype+'_OUTPUT_DIR']
        output_template = self.c_dict[dtype+'_OUTPUT_TEMPLATE']

        if not level.isdigit():
            f_level = '0'
        else:
            f_level = level

        string_sub = sts.StringSub(self.logger,
                                   input_template,
                                   level=(int(f_level)*3600),
                                   **time_info)
        infile = os.path.join(input_dir, string_sub.do_string_sub())

        infile = util.preprocess_file(infile,
                                      self.config.getstr('config',
                                                         dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE',
                                                         ''),
                                      self.config)
        if infile is not None:
            self.infiles.append(infile)
        else:
            self.logger.error('Could not find input file in {} matching template {}'
                              .format(input_dir, input_template))
            return False

        verif_grid = self.c_dict['VERIFICATION_GRID']
        if verif_grid == '':
            self.logger.error('No verification grid specified! ' + \
                              'Set REGRID_DATA_PLANE_VERIF_GRID')
            return False

        # put quotes around verification grid in case it is a grid description
        self.infiles.append(f'"{verif_grid}"')
        string_sub = sts.StringSub(self.logger,
                                   output_template,
                                   level=(int(f_level)*3600),
                                   **time_info)
        outfile = string_sub.do_string_sub()
        self.set_output_path(os.path.join(output_dir, outfile))

        outpath = self.get_output_path()
        if os.path.exists(outpath) and \
          self.c_dict['SKIP_IF_OUTPUT_EXISTS'] is True:
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS to True to process'
                              .format(outpath))
            return True

        # if using python script to supply input data, just set field name
        # if PcpCombine has been run on this data, set field name = name_level
        # and level=(*,*), otherwise set name=name and level=level
        if util.is_python_script(field_name):
            self.args.append("-field 'name=\"{:s}\";'".format(field_name))
        elif self.config.getbool('config', dtype + '_PCP_COMBINE_RUN', False):
            name = "{:s}_{:s}".format(field_name, str(level))
            self.args.append("-field 'name=\"{:s}\"; level=\"(*,*)\";'".format(name))
        else:
            name = "{:s}".format(field_name)
            self.args.append("-field 'name=\"{:s}\"; level=\"{:s}\";'".format(name, v_level))

        # set regrid method is explicitly set
        if self.c_dict['METHOD'] != '':
            self.args.append("-method {}".format(self.c_dict['METHOD']))

        # set width argument
        self.args.append("-width {}".format(self.c_dict['WIDTH']))

        # set output name
        # if [FCST/OBS]_REGRID_DATA_PLANE_OUTPUT_FIELD_NAME is not explicitly set,
        # use the input field name. If input comes from a python script, report error
        index = var_info['index']
        _, output_name = self.get_explicit_field_names(index, dtype)
        if not output_name:
            if util.is_python_script(field_name):
                self.logger.error('Must explicitly set '
                                  f'{dtype}_REGRID_DATA_PLANE_VAR{index}_'
                                  'OUTPUT_FIELD_NAME '
                                  'if input field comes from a python script.')
                return

            output_name = name

        self.args.append("-name " + output_name)
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return
        self.build()

if __name__ == "__main__":
    util.run_stand_alone("regrid_data_plane_wrapper", "RegridDataPlane")
