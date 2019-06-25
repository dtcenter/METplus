#!/usr/bin/env python

"""
Program Name: example_wrapper.py
Contact(s): George McCabe
Abstract: Template for creating a new wrapper
History Log:  Initial version
Usage: Not meant to be run
Parameters: None
Input Files: None
Output Files: None
Condition codes: 0 for success, 1 for failure
"""

from __future__ import print_function

import os
import met_util as util
import time_util
from command_builder import CommandBuilder

class ExampleWrapper(CommandBuilder):
    """!Wrapper can be used as a base to develop a new wrapper"""
    def __init__(self, config, logger):
        super(ExampleWrapper, self).__init__(config, logger)
        self.app_name = 'example'
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        # change to super() for python 3
        # c_dict = super()
        c_dict = super(ExampleWrapper, self).create_c_dict()
        # get values from config object and set them to be accessed by wrapper
        c_dict['EXAMPLE'] = self.config.getstr('config', 'LOOP_BY')
        return c_dict

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. Processing forecast
              or observation data is determined by conf variables. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """
        # fill in time info dictionary
        time_info = time_util.ti_calculate(input_dict)

        loop_by = time_info['loop_by']
        self.logger.info("Running ExampleWrapper at {} time {}".format(loop_by,
                                                                       time_info[loop_by+'_fmt']))

        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            time_info['lead_hours'] = lead

            time_info = time_util.ti_calculate(time_info)
            self.logger.info("Processing forecast lead {} initialized at {} and valid at {}"
                             .format(lead, time_info['init'].strftime('%Y-%m-%d %HZ'),
                                     time_info['init'].strftime('%Y-%m-%d %HZ')))

        # process data
        return True
