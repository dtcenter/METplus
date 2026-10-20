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

from . import RuntimeFreqWrapper


class ExampleWrapper(RuntimeFreqWrapper):
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    """!Wrapper can be used as a base to develop a new wrapper"""
    def __init__(self, config, instance=None):
        self.app_name = 'example'
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['INPUT_MUST_EXIST'] = False

        self.get_input_templates(c_dict, {
            '': {'prefix': 'EXAMPLE', 'required': False},
        })

        if not c_dict['INPUT_DIR']:
            self.logger.debug('EXAMPLE_INPUT_DIR was not set')

        if not c_dict['INPUT_TEMPLATE']:
            self.logger.warning(
                'EXAMPLE_INPUT_TEMPLATE was not set. '
                'You should set this variable to see how the '
                'runtime is substituted. For example: {valid?fmt=%Y%m%d%H}.ext'
            )

        full_path = os.path.join(c_dict['INPUT_DIR'], c_dict['INPUT_TEMPLATE'])
        self.logger.info(f"Input directory is {c_dict['INPUT_DIR']}")
        self.logger.info(f"Input template is {c_dict['INPUT_TEMPLATE']}")
        self.logger.info(f"Full input template path is {full_path}")

        c_dict['ALLOW_MULTIPLE_FILES'] = True

        return c_dict

    def run_at_time_once(self, time_info):
        """!Log files that were requested and log if a file was found on disk.

        @param time_info dictionary with time information of the current run
        """
        for file_dict in self.c_dict['ALL_FILES']:
            files = file_dict.get('')
            if not files: continue
            for filename in files:
                self.logger.info(f'Looking for file: {filename}')
                if os.path.exists(filename):
                    self.logger.info(f'FOUND FILE: {filename}')

        return True
