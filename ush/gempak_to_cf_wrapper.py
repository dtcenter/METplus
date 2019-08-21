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
import met_util as util
import string_template_substitution as sts
import time_util
from command_builder import CommandBuilder

'''!@namespace GempakToCFWrapper
@brief Wraps the GempakToCF tool to reformat Gempak format to NetCDF Format
@endcode
'''


class GempakToCFWrapper(CommandBuilder):
    def __init__(self, config, logger):
        super(GempakToCFWrapper, self).__init__(config, logger)
        self.app_name = "GempakToCF"
        self.class_path = self.config.getstr('exe', 'GEMPAKTOCF_CLASSPATH')

    def get_command(self):
        cmd = "java -classpath " + self.class_path + " GempakToCF "

        if len(self.infiles) != 1:
            self.logger.error("Only 1 input file can be selected")
            return None

        for infile in self.infiles:
            cmd += infile + " "

        if self.outfile == "":
            self.logger.error("No output file specified")
            return None

        cmd += self.get_output_path()
        return cmd

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. Processing forecast
              or observation data is determined by conf variables. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param input_dict dictionary containing timing information
        """
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            self.clear()
            input_dict['lead_hours'] = lead
            self.config.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)
            time_info = time_util.ti_calculate(input_dict)
            self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Runs the MET application for a given time and forecast lead combination
             Args:
                @param time_info dictionary containing timing information
        """
        valid_time = time_info['valid']
        input_dir = self.config.getdir('GEMPAKTOCF_INPUT_DIR')
        input_template = self.config.getraw('filename_templates',
                                            'GEMPAKTOCF_INPUT_TEMPLATE')
        output_dir = self.config.getdir('GEMPAKTOCF_OUTPUT_DIR')
        output_template = self.config.getraw('filename_templates',
                                             'GEMPAKTOCF_OUTPUT_TEMPLATE')

        gsts = sts.StringSub(self.logger,
                             input_template,
                             valid=valid_time)
        infile = os.path.join(input_dir, gsts.do_string_sub())
        self.infiles.append(infile)

        gsts = sts.StringSub(self.logger,
                             output_template,
                             valid=valid_time)
        outfile = os.path.join(output_dir, gsts.do_string_sub())

        if os.path.exists(outfile) and \
                        self.config.getbool('config', 'GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS', False) is True:
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS to True to process'
                              .format(outfile))
            return

        self.set_output_path(outfile)

        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))

        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        self.build()
