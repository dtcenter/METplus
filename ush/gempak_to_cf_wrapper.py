#!/usr/bin/env python

"""
Program Name: gempak_to_cf.py
Contact(s): Julie Prestopnik
Abstract: Runs GempakToCF
History Log:  Initial version
Usage:
Parameters: None
Input Files: gempak files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

from __future__ import print_function

import os
import logging
import met_util as util
import string_template_substitution as sts
from task_info import TaskInfo
from reformat_gridded_wrapper import ReformatGriddedWrapper


'''!@namespace GempakToCFWrapper
@brief Wraps the GempakToCF tool to reformat Gempak format to NetCDF Format
@endcode
'''


class GempakToCFWrapper(ReformatGriddedWrapper):

    def __init__(self, p, logger):
        super(GempakToCFWrapper, self).__init__(p, logger)
        self.app_name = "GempakToCF"
        self.class_path = self.p.getstr('exe', 'GEMPAKTOCF_CLASSPATH')
        self.logger = logger
        if self.logger is None:
            self.logger = util.get_logger(self.p,sublog='GempakToCF')

                        
    def get_command(self):
        cmd = "java -classpath " + self.class_path + " GempakToCF "

        if len(self.infiles) != 1:
            self.logger.error(self.app_name +
                              ": Only 1 input file can be selected")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.outfile == "":
            self.logger.error(self.app_name + ": No output file specified")
            return None

        cmd += self.get_output_path()
        return cmd

    def run_at_time_once(self, task_info, var_info, dtype):
        """! Runs the MET application for a given time and forecast lead combination
             Args:
                @param task_info task_info object containing timing information
                @param var_info var_info object containing variable information
                @params dtype dtype (FCST or OBS)
        """
        valid_time = task_info.getValidTime()
        input_dir = self.p.getdir(dtype+'_GEMPAKTOCF_INPUT_DIR')
        input_template = util.getraw_interp(self.p, 'filename_templates',
                                        dtype+'_GEMPAKTOCF_INPUT_TEMPLATE')
        output_dir = self.p.getdir(dtype+'_GEMPAKTOCF_OUTPUT_DIR')
        output_template = util.getraw_interp(self.p, 'filename_templates',
                                        dtype+'_GEMPAKTOCF_OUTPUT_TEMPLATE')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(output_dir, ymd_v)):
            self.logger.info("Output directory does not exist, creating.")
            os.makedirs(os.path.join(output_dir, ymd_v))

        gempakSts = sts.StringSub(self.logger,
                               input_template,
                               valid=valid_time)
        infile = os.path.join(input_dir, gempakSts.doStringSub())
        self.add_input_file(infile)

        gempakToCfSts = sts.StringSub(self.logger,
                                  output_template,
                                  valid=valid_time)
        outfile = os.path.join(output_dir, gempakToCfSts.doStringSub())
        self.set_output_path(outfile)

        cmd = self.get_command()
        self.logger.info(cmd)
        if cmd is None:
            self.logger.error(self.app_name+" could not generate command")
            return


        self.logger.info("")
        self.build()
        self.clear()
