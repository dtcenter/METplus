#!/usr/bin/env python

"""
Program Name: custom_ingester_wrapper.py
Contact(s): George McCabe
Abstract: 
History Log:  Initial version
Usage: 
Parameters: None
Input Files: None
Output Files: None
Condition codes: 0 for success, 1 for failure
"""


import os
import re

import util.met_util as util
import util.time_util
from command_builder import CommandBuilder
#from metplus_wrappers import RegridDataPlaneWrapper
import metplus_wrappers as mw
#from regrid_data_plane_wrapper import RegridDataPlaneWrapper
from string_template_substitution import StringSub

VALID_PYTHON_EMBED_TYPES = ['NUMPY', 'XARRAY', 'PANDAS']

class CustomIngestWrapper(CommandBuilder):
    """!Wrapper to utilize Python Embedding in the MET tools to read in
    data using a python script"""
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_name = 'regrid_data_plane'
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper

        c_dict['INGESTERS'] = []

        # find all CUSTOM_INGEST_<n>_TEMPLATE keys in the conf files
        all_conf = self.config.keys('config')
        indices = []
        regex = re.compile(r"CUSTOM_INGEST_(\d+)_SCRIPT")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                indices.append(result.group(1))

        for index in indices:
            ingest_script = self.config.getraw('config', f'CUSTOM_INGEST_{index}_SCRIPT')
            input_type = self.config.getstr('config', f'CUSTOM_INGEST_{index}_TYPE')
            output_dir = self.config.getdir(f'CUSTOM_INGEST_{index}_OUTPUT_DIR', '')
            output_template = self.config.getraw('filename_templates',
                                                 f'CUSTOM_INGEST_{index}_OUTPUT_TEMPLATE')
            output_grid = self.config.getraw('config', f'CUSTOM_INGEST_{index}_OUTPUT_GRID', '')
            ingester_dict = {'output_dir': output_dir,
                             'output_template': output_template,
                             'script': ingest_script,
                             'input_type': input_type,
                             'output_grid': output_grid,
                             'index': index,
                            }

            c_dict['INGESTERS'].append(ingester_dict)

        c_dict['regrid_data_plane'] = RegridDataPlaneWrapper(self.config, self.logger)
        return c_dict

    def run_at_time(self, input_dict):
        """! Do some processing for the current run time (init or valid)
              Args:
                @param input_dict dictionary containing time information of current run
                        generally contains 'now' (current) time and 'init' or 'valid' time
        """
        # get forecast leads to loop over
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            input_dict['lead'] = lead

            # recalculate time info items
            time_info = time_util.ti_calculate(input_dict)

            if self.run_at_time_lead(time_info) is None:
                return False

        return True

    def run_at_time_lead(self, time_info):
        rdp = self.c_dict['regrid_data_plane']

        # run each ingester specified
        for ingester in self.c_dict['INGESTERS']:
            index = ingester['index']
            input_type = ingester['input_type']
            if input_type not in VALID_PYTHON_EMBED_TYPES:
                self.logger.error(f'CUSTOM_INGEST_{index}_TYPE ({input_type}) not valid. '
                                  f'Valid types are {VALID_PYTHON_EMBED_TYPES}')
                return

            # If input type is PANDAS, call ascii2nc? instead of RegridDataPlane
            if input_type == 'PANDAS':
                self.logger.error('Running CustomIngester on pandas data not yet implemented')
                return

            # get grid information to project output data
            output_grid = StringSub(self.logger,
                                    ingester['output_grid'],
                                    **time_info).do_string_sub()
            if output_grid == '':
                self.logger.error(f'Must set CUSTOM_INGEST_{index}_OUTPUT_GRID')
                return

            # get call to python script
            script = StringSub(self.logger,
                               ingester['script'],
                               **time_info).do_string_sub()

            # get output file path
            output_file = StringSub(self.logger,
                                    ingester['output_template'],
                                    **time_info).do_string_sub()
            output_path = os.path.join(ingester['output_dir'], output_file)

            rdp.clear()
            rdp.infiles.append(f'PYTHON_{input_type}')
            rdp.infiles.append(f'-field \'name="{script}\";\'')
            rdp.infiles.append(output_grid)
            rdp.outfile = output_path
            cmd = rdp.get_command()
            if cmd is None:
                self.logger.error("Could not generate command")
                return
            self.logger.info(f'Running Custom Ingester {index}')
            rdp.build()

if __name__ == "__main__":
        util.run_stand_alone("custom_ingest_wrapper", "CustomIngest")
