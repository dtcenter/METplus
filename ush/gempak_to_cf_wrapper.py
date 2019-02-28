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
from command_builder import CommandBuilder


'''!@namespace GempakToCFWrapper
@brief Wraps the GempakToCF tool to reformat Gempak format to NetCDF Format
@endcode
'''


class GempakToCFWrapper(CommandBuilder):

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
            self.logger.error("Only 1 input file can be selected")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.outfile == "":
            self.logger.error("No output file specified")
            return None

        cmd += self.get_output_path()
        return cmd

    def run_at_time(self, init_time, valid_time):
        """! Runs the MET application for a given run time. Processing forecast
              or observation data is determined by conf variables. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """        
        app_name_caps = self.app_name.upper()
        class_name = self.__class__.__name__[0: -7]
        task_info = TaskInfo()
        task_info.init_time = init_time
        task_info.valid_time = valid_time
        lead_seq = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))

        for lead in lead_seq:
            task_info.lead = lead
            self.p.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = lead
            self.run_at_time_once(task_info)


    def run_at_time_once(self, task_info):
        """! Runs the MET application for a given time and forecast lead combination
             Args:
                @param task_info task_info object containing timing information
        """
        valid_time = task_info.getValidTime()
        input_dir = self.p.getdir('GEMPAKTOCF_INPUT_DIR')
        input_template = util.getraw_interp(self.p, 'filename_templates',
                                        'GEMPAKTOCF_INPUT_TEMPLATE')
        output_dir = self.p.getdir('GEMPAKTOCF_OUTPUT_DIR')
        output_template = util.getraw_interp(self.p, 'filename_templates',
                                        'GEMPAKTOCF_OUTPUT_TEMPLATE')

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
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        self.build()
        self.clear()
