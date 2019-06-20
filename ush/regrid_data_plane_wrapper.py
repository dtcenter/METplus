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
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin/regrid_data_plane')
        self.app_name = os.path.basename(self.app_path)
        self.create_c_dict()


    def create_c_dict(self):
        self.c_dict = dict()
        self.c_dict['SKIP_IF_OUTPUT_EXISTS'] = \
          self.config.getbool('config', 'REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS',
                              False)
        if self.config.has_option('filename_templates',
                                  'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE'):
            self.c_dict['FCST_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'FCST_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['FCST_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['FCST_INPUT_TEMPLATE'] = None

        if self.config.has_option('filename_templates',
                                  'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE'):
            self.c_dict['OBS_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'OBS_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['OBS_INPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['OBS_INPUT_TEMPLATE'] = None

        if self.config.has_option('filename_templates',
                                  'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'):
            self.c_dict['FCST_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'FCST_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['FCST_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'FCST_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['FCST_OUTPUT_TEMPLATE'] = None

        if self.config.has_option('filename_templates',
                                  'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'):
            self.c_dict['OBS_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE')
        elif self.config.has_option('filename_templates',
                                    'OBS_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['OBS_OUTPUT_TEMPLATE'] = \
                self.config.getraw('filename_templates',
                                   'OBS_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['OBS_OUTPUT_TEMPLATE'] = None

        if self.config.getbool('config', 'FCST_REGRID_DATA_PLANE_RUN', False):
            self.c_dict['FCST_INPUT_DIR'] = \
                self.config.getdir('FCST_REGRID_DATA_PLANE_INPUT_DIR', '')
            self.c_dict['FCST_OUTPUT_DIR'] = \
                self.config.getdir('FCST_REGRID_DATA_PLANE_OUTPUT_DIR', '')

        if self.config.getbool('config', 'OBS_REGRID_DATA_PLANE_RUN', False):
            self.c_dict['OBS_INPUT_DIR'] = \
                self.config.getdir('OBS_REGRID_DATA_PLANE_INPUT_DIR', '')

            self.c_dict['OBS_OUTPUT_DIR'] = \
                self.config.getdir('OBS_REGRID_DATA_PLANE_OUTPUT_DIR', '')

        self.c_dict['VERIFICATION_GRID'] = \
            self.config.getstr('config', 'REGRID_DATA_PLANE_VERIF_GRID', '')

        self.c_dict['METHOD'] = \
          self.config.getstr('config', 'REGRID_DATA_PLANE_METHOD', '')

        self.c_dict['WIDTH'] = \
         self.config.getint('config', 'REGRID_DATA_PLANE_WIDTH', 1)

    def run_at_time_once(self, time_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti time_info object containing timing information
                @param v var_info object containing variable information
        """
        self.clear()

        if dtype == "FCST":
            compare_var = var_info['fcst_name']
            level = var_info['fcst_level']
        else:
            compare_var = var_info['obs_name']
            level = var_info['obs_level']

        level = util.split_level(level)[1]

        if self.c_dict[dtype+'_INPUT_DIR'] == '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_INPUT_DIR'.format(dtype) +\
                              ' in config file')
            exit(1)

        if self.c_dict[dtype+'_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_INPUT_TEMPLATE'.format(dtype) +\
                              ' in config file')
            exit(1)

        if self.c_dict[dtype+'_OUTPUT_DIR'] == '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_OUTPUT_DIR'.format(dtype) +\
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

        self.infiles.append(verif_grid)
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

        if self.config.getstr('config',
                              dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE',
                              '') in ['', 'NETCDF']:
            field_name = "{:s}_{:s}".format(compare_var, str(level).zfill(2))
            self.args.append("-field 'name=\"{:s}\"; level=\"(*,*)\";'".format(field_name))
        else:
            field_name = "{:s}".format(compare_var)
            self.args.append("-field 'name=\"{:s}\"; level=\"{:s}\";'".format(field_name, level))

        if self.c_dict['METHOD'] != '':
            self.args.append("-method {}".format(self.c_dict['METHOD']))

        self.args.append("-width {}".format(self.c_dict['WIDTH']))

        self.args.append("-name " + field_name)
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return
        self.build()

if __name__ == "__main__":
    util.run_stand_alone("regrid_data_plane_wrapper", "RegridDataPlane")
