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

from ..util import do_string_sub, ti_calculate, get_lead_sequence
from ..util import skip_time
from . import LoopTimesWrapper


class ExampleWrapper(LoopTimesWrapper):
    """!Wrapper can be used as a base to develop a new wrapper"""
    def __init__(self, config, instance=None):
        self.app_name = 'example'
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('config',
                                                      'EXAMPLE_INPUT_TEMPLATE')
        c_dict['INPUT_DIR'] = self.config.getdir('EXAMPLE_INPUT_DIR', '')

        if not c_dict['INPUT_TEMPLATE']:
            self.logger.warning('EXAMPLE_INPUT_TEMPLATE was not set. '
                                'You should set this variable to see how the '
                                'runtime is substituted. '
                                'For example: {valid?fmt=%Y%m%d%H}.ext')

        if not c_dict['INPUT_DIR']:
            self.logger.debug('EXAMPLE_INPUT_DIR was not set')

        full_path = os.path.join(c_dict['INPUT_DIR'], c_dict['INPUT_TEMPLATE'])
        self.logger.info(f"Input directory is {c_dict['INPUT_DIR']}")
        self.logger.info(f"Input template is {c_dict['INPUT_TEMPLATE']}")
        self.logger.info(f"Full input template path is {full_path}")

        return c_dict

    def run_at_time_once(self, time_info):
        """! Do some processing for the current run time (init or valid)

            @param time_info dictionary with time information of current run
        """
        # read input directory and template from config dictionary
        full_template = os.path.join(self.c_dict['INPUT_DIR'],
                                     self.c_dict['INPUT_TEMPLATE'])

        # perform string substitution to find filename based on
        # template and current run time
        filename = do_string_sub(full_template, **time_info)
        self.logger.info(f'Looking for file: {filename}')
        if os.path.exists(filename):
            self.logger.info(f'FOUND FILE: {filename}')

        return True
