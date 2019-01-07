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
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/regrid_data_plane')
        self.app_name = os.path.basename(self.app_path)


    def run_at_time_once(self, task_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
        """
        valid_time = task_info.getValidTime()
        if dtype == "FCST":
            compare_var = var_info.fcst_name
            level = var_info.fcst_level
        else:
            compare_var = var_info.obs_name
            level = var_info.obs_level

        level_type, level = util.split_level(level)

#        if level[0].isalpha():
#            level = var_info.obs_level[1:]

        input_dir = self.p.getdir(dtype+'_REGRID_DATA_PLANE_INPUT_DIR')
        input_template = util.getraw_interp(self.p, 'filename_templates',
                                        dtype+'_REGRID_DATA_PLANE_TEMPLATE')
        output_dir = self.p.getdir(dtype+'_REGRID_DATA_PLANE_OUTPUT_DIR')
        output_template = util.getraw_interp(self.p, 'filename_templates',
                                        dtype+'_REGRID_DATA_PLANE_TEMPLATE')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(output_dir, ymd_v)):
            os.makedirs(os.path.join(output_dir, ymd_v))

        if not level.isdigit():
            f_level = '0'
        else:
            f_level = level

        pcpSts = sts.StringSub(self.logger,
                               input_template,
                               valid=valid_time,
                               level=str(f_level).zfill(2))
        infile = os.path.join(input_dir, pcpSts.doStringSub())

        infile = util.preprocess_file(infile,
                                      self.p.getstr('config',
                                                    dtype+'_REGRID_DATA_PLANE_INPUT_DATATYPE', ''),
                                      self.p, self.logger)
        if infile is not None:
            self.add_input_file(infile)
        else:
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
            self.logger.error(self.app_name+" could not generate command")
            return
        self.logger.info("")
        self.build()
        self.clear()


if __name__ == "__main__":
        util.run_stand_alone("regrid_data_plane_wrapper", "RegridDataPlane")
