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

import os
import met_util as util
import time_util
from command_builder import CommandBuilder
from string_template_substitution import StringSub

class ExampleWrapper(CommandBuilder):
    """!Wrapper can be used as a base to develop a new wrapper"""
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_name = 'example'
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'EXAMPLE_INPUT_TEMPLATE', '')
        c_dict['INPUT_DIR'] = self.config.getdir('EXAMPLE_INPUT_DIR', '')

        if c_dict['INPUT_TEMPLATE'] == '':
            self.logger.info('[filename_templates] EXAMPLE_INPUT_TEMPLATE was not set. '
                             'You should set this variable to see how the runtime is '
                             'substituted. For example: {valid?fmt=%Y%m%d%H}.ext')

        if c_dict['INPUT_DIR'] == '':
            self.logger.debug('EXAMPLE_INPUT_DIR was not set')

        return c_dict

    def run_at_time(self, input_dict):
        """! Do some processing for the current run time (init or valid)
              Args:
                @param input_dict dictionary containing time information of current run
                        generally contains 'now' (current) time and 'init' or 'valid' time
        """
        # fill in time info dictionary
        time_info = time_util.ti_calculate(input_dict)

        # check if looping by valid or init and log time for run
        loop_by = time_info['loop_by']
        self.logger.info('Running ExampleWrapper at {} time {}'.format(loop_by,
                                                                       time_info[loop_by+'_fmt']))

        # read input directory and template from config dictionary
        input_dir = self.c_dict['INPUT_DIR']
        input_template = self.c_dict['INPUT_TEMPLATE']
        self.logger.info('Input directory is {}'.format(input_dir))
        self.logger.info('Input template is {}'.format(input_template))

        # get forecast leads to loop over
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            time_info['lead'] = lead

            # recalculate time info items
            time_info = time_util.ti_calculate(time_info)

            # log init, valid, and forecast lead times for current loop iteration
            self.logger.info('Processing forecast lead {} initialized at {} and valid at {}'
                             .format(time_info['lead_string'], time_info['init'].strftime('%Y-%m-%d %HZ'),
                                     time_info['valid'].strftime('%Y-%m-%d %HZ')))

            # perform string substitution to find filename based on template and current run time
            # pass in logger, then template, then any items to use to fill in template
            # pass time info with ** in front to expand each dictionary item to a variable
            #  i.e. time_info['init'] becomes init=init_value
            filename = StringSub(self.logger,
                                 input_template,
                                 **time_info).do_string_sub()
            self.logger.info('Looking in input directory for file: {}'.format(filename))

        return True

if __name__ == "__main__":
        util.run_stand_alone("example_wrapper", "Example")
