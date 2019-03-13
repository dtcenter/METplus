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

import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
import string_template_substitution as sts
from task_info import TaskInfo
from reformat_gridded_wrapper import ReformatGriddedWrapper

'''!@namespace RegridDataPlaneWrapper
@brief Wraps the MET tool regrid_data_plane to reformat gridded datasets
@endcode
'''
class RegridDataPlaneWrapper(ReformatGriddedWrapper):
    '''!Wraps the MET tool regrid_data_plane to reformat gridded datasets
    '''
    def __init__(self, p, logger):
        super(RegridDataPlaneWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(util.getdir(self.p, 'MET_INSTALL_DIR', None, logger),
                                     'bin/regrid_data_plane')
        self.app_name = os.path.basename(self.app_path)
        self.create_c_dict()


    def create_c_dict(self):
        self.c_dict = dict()
        if self.p.has_option('filename_templates', 'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE'):
            self.c_dict['FCST_INPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                   'FCST_REGRID_DATA_PLANE_INPUT_TEMPLATE')
        elif self.p.has_option('filename_templates', 'FCST_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['FCST_INPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                   'FCST_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['FCST_INPUT_TEMPLATE'] = None

        if self.p.has_option('filename_templates', 'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE'):
            self.c_dict['OBS_INPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                  'OBS_REGRID_DATA_PLANE_INPUT_TEMPLATE')
        elif self.p.has_option('filename_templates', 'OBS_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['OBS_INPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                  'OBS_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['OBS_INPUT_TEMPLATE'] = None

        if self.p.has_option('filename_templates', 'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'):
            self.c_dict['FCST_OUTPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                   'FCST_REGRID_DATA_PLANE_OUTPUT_TEMPLATE')
        elif self.p.has_option('filename_templates', 'FCST_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['FCST_OUTPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                   'FCST_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['FCST_OUTPUT_TEMPLATE'] = None

        if self.p.has_option('filename_templates', 'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE'):
            self.c_dict['OBS_OUTPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                  'OBS_REGRID_DATA_PLANE_OUTPUT_TEMPLATE')
        elif self.p.has_option('filename_templates', 'OBS_REGRID_DATA_PLANE_TEMPLATE'):
            self.c_dict['OBS_OUTPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates',
                                                  'OBS_REGRID_DATA_PLANE_TEMPLATE')
        else:
            self.c_dict['OBS_OUTPUT_TEMPLATE'] = None

        self.c_dict['FCST_INPUT_DIR'] = util.getdir(self.p, 'FCST_REGRID_DATA_PLANE_INPUT_DIR', '', self.logger)
        self.c_dict['OBS_INPUT_DIR'] = util.getdir(self.p, 'OBS_REGRID_DATA_PLANE_INPUT_DIR', '', self.logger)
        self.c_dict['FCST_OUTPUT_DIR'] = util.getdir(self.p, 'FCST_REGRID_DATA_PLANE_OUTPUT_DIR', '', self.logger)
        self.c_dict['OBS_OUTPUT_DIR'] = util.getdir(self.p, 'OBS_REGRID_DATA_PLANE_OUTPUT_DIR', '', self.logger)

    def run_at_time_once(self, task_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
        """
        init_time = task_info.getInitTime()
        valid_time = task_info.getValidTime()
        lead = task_info.getLeadTime()

        if dtype == "FCST":
            compare_var = var_info.fcst_name
            level = var_info.fcst_level
        else:
            compare_var = var_info.obs_name
            level = var_info.obs_level

        level_type, level = util.split_level(level)

        if self.c_dict[dtype+'_INPUT_DIR'] is '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_INPUT_DIR in config file'.format(dtype))
            exit(1)

        if self.c_dict[dtype+'_INPUT_TEMPLATE'] is None:
            self.logger.error('Must set {}_REGRID_DATA_PLANE_INPUT_TEMPLATE in config file'.format(dtype))
            exit(1)

        if self.c_dict[dtype+'_OUTPUT_DIR'] is '':
            self.logger.error('Must set {}_REGRID_DATA_PLANE_OUTPUT_DIR in config file'.format(dtype))
            exit(1)

        if self.c_dict[dtype+'_OUTPUT_TEMPLATE'] is None:
            self.logger.error('Must set {}_REGRID_DATA_PLANE_OUTPUT_TEMPLATE in config file'.format(dtype))
            exit(1)

        input_dir = self.c_dict[dtype+'_INPUT_DIR']
        input_template = self.c_dict[dtype+'_INPUT_TEMPLATE']
        output_dir = self.c_dict[dtype+'_OUTPUT_DIR']
        output_template = self.c_dict[dtype+'_OUTPUT_TEMPLATE']

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(output_dir, ymd_v)):
            os.makedirs(os.path.join(output_dir, ymd_v))

        if not level.isdigit():
            f_level = '0'
        else:
            f_level = level

        pcpSts = sts.StringSub(self.logger,
                               input_template,
                               init=init_time,
                               valid=valid_time,
                               lead=str(lead),
                               level=str(f_level).zfill(2))
        infile = os.path.join(input_dir, pcpSts.doStringSub())

        infile = util.preprocess_file(infile,
                                      self.p.getstr('config',
                                                    dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE', ''),
                                      self.p, self.logger)
        if infile is not None:
            self.add_input_file(infile)
        else:
            self.logger.error('Could not find input file in {} matching template {}'
                              .format(input_dir, input_template))
            return False
        self.add_input_file(self.p.getstr('config', 'VERIFICATION_GRID'))
        regridSts = sts.StringSub(self.logger,
                                  output_template,
                                  valid=valid_time,
                                  level=str(f_level).zfill(2))
        outfile = regridSts.doStringSub()
        self.set_output_path(os.path.join(output_dir, outfile))

        if self.p.getstr('config', dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE', 'GRIB') == 'GRIB':
            field_name = "{:s}_{:s}".format(compare_var, str(level).zfill(2))
            self.add_arg("-field 'name=\"{:s}\"; level=\"(*,*)\";'".format(field_name))
        else:
            field_name = "{:s}".format(compare_var)
            self.add_arg("-field 'name=\"{:s}\"; level=\"{:s}\";'".format(field_name, level))

        self.add_arg("-method BUDGET")
        self.add_arg("-width 2")
        self.add_arg("-name " + field_name)
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return
        self.build()
        self.clear()


if __name__ == "__main__":
        util.run_stand_alone("regrid_data_plane_wrapper", "RegridDataPlane")
