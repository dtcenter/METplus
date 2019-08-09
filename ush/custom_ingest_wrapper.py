#!/usr/bin/env python

"""
Program Name: example_wrapper.py
Contact(s): George McCabe
Abstract: 
History Log:  Initial version
Usage: 
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
from string_template_substitution import StringSub

class CustomIngestWrapper(CommandBuilder):
    """!Wrapper to utilize Python Embedding in the MET tools to read in
    data using a python script"""
    def __init__(self, config, logger):
        super(CustomIngestWrapper, self).__init__(config, logger)
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        # change to super() for python 3
        # c_dict = super()
        c_dict = super(CustomIngestWrapper, self).create_c_dict()
        # get values from config object and set them to be accessed by wrapper

        c_dict['INGESTERS'] = []
        # find all CUSTOM_INGEST_<n>_TEMPLATE keys in the conf files
        all_conf = config.keys('config')
        indices = []
        regex = re.compile("CUSTOM_INGEST_(\d+)_SCRIPT")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                indices.append(result.group(1))

        for index in indicies:
            ingest_script = self.config.getstr('config', 'CUSTOM_INGEST_{}_SCRIPT'.format(index))
            input_template = self.config.getraw('filename_templates',
                                                'CUSTOM_INGEST_{}_INPUT_TEMPLATE'.format(index))
            input_dir = self.config.getdir('CUSTOM_INGEST_{}_INPUT_DIR'.format(index), '')
            output_template = self.config.getraw('filename_templates',
                                                 'CUSTOM_INGEST_{}_OUTPUT_TEMPLATE'.format(index))
            output_dir = self.config.getdir('CUSTOM_INGEST_{}_OUTPUT_DIR'.format(index), '')
            ingester_dict = { 'input_dir' : input_dir, 'input_template' : input_template,
                              'output_dir' : output_dir, 'output_template' : output_template,
                              'ingest_script' : ingest_script }
            c_dict['INGESTERS'].append(ingester_dict)

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
            time_info['lead_hours'] = lead

            # recalculate time info items
            time_info = time_util.ti_calculate(time_info)

            # log init, valid, and forecast lead times for current loop iteration
            self.logger.info('Processing forecast lead {} initialized at {} and valid at {}'
                             .format(lead, time_info['init'].strftime('%Y-%m-%d %HZ'),
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
