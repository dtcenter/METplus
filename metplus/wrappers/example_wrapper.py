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
from . import CommandBuilder

class ExampleWrapper(CommandBuilder):
    """!Wrapper can be used as a base to develop a new wrapper"""
    def __init__(self, config, instance=None):
        self.app_name = 'example'
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'EXAMPLE_INPUT_TEMPLATE')
        c_dict['INPUT_DIR'] = self.config.getdir('EXAMPLE_INPUT_DIR', '')

        if not c_dict['INPUT_TEMPLATE']:
            self.logger.warning('EXAMPLE_INPUT_TEMPLATE was not set. '
                                'You should set this variable to see how the '
                                'runtime is substituted. '
                                'For example: {valid?fmt=%Y%m%d%H}.ext')

        if not c_dict['INPUT_DIR']:
            self.logger.debug('EXAMPLE_INPUT_DIR was not set')

        return c_dict

    def run_at_time(self, input_dict):
        """! Do some processing for the current run time (init or valid)

            @param input_dict dictionary with time information of current run
        """
        # fill in time info dictionary
        time_info = ti_calculate(input_dict)

        # check if looping by valid or init and log time for run
        loop_by = time_info['loop_by']
        current_time = time_info[loop_by + '_fmt']
        self.logger.info('Running ExampleWrapper at '
                         f'{loop_by} time {current_time}')

        # read input directory and template from config dictionary
        input_dir = self.c_dict['INPUT_DIR']
        input_template = self.c_dict['INPUT_TEMPLATE']
        self.logger.info(f'Input directory is {input_dir}')
        self.logger.info(f'Input template is {input_template}')

        # get forecast leads to loop over
        lead_seq = get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            time_info['lead'] = lead

            # recalculate time info items
            time_info = ti_calculate(time_info)

            if skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(
                        f"Processing custom string: {custom_string}"
                    )

                time_info['custom'] = custom_string

                # log init/valid/forecast lead times for current loop iteration
                self.logger.info(
                    'Processing forecast lead '
                    f'{time_info["lead_string"]} initialized at '
                    f'{time_info["init"].strftime("%Y-%m-%d %HZ")} '
                    'and valid at '
                    f'{time_info["valid"].strftime("%Y-%m-%d %HZ")}'
                )

                # perform string substitution to find filename based on
                # template and current run time
                filename = do_string_sub(input_template,
                                         **time_info)
                self.logger.info('Looking in input directory '
                                 f'for file: {filename}')

        return True
