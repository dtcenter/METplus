"""
Program Name: py_embed_ingest_wrapper.py
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

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from . import RegridDataPlaneWrapper
from ..util import do_string_sub

VALID_PYTHON_EMBED_TYPES = ['NUMPY', 'XARRAY', 'PANDAS']

class PyEmbedIngestWrapper(CommandBuilder):
    """!Wrapper to utilize Python Embedding in the MET tools to read in
    data using a python script"""
    def __init__(self, config, logger):
        self.app_name = 'py_embed_ingest'
        super().__init__(config, logger)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper

        c_dict['INGESTERS'] = []

        # find all PY_EMBED_INGEST_<n>_TEMPLATE keys in the conf files
        all_conf = self.config.keys('config')
        indices = []
        regex = re.compile(r"PY_EMBED_INGEST_(\d+)_SCRIPT")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                indices.append(result.group(1))

        for index in indices:
            ingest_script = self.config.getraw('config', 'PY_EMBED_INGEST_{}_SCRIPT'.format(index))
            input_type = self.config.getstr('config', 'PY_EMBED_INGEST_{}_TYPE'.format(index))
            input_type = input_type.upper()
            if input_type not in VALID_PYTHON_EMBED_TYPES:
                self.log_error(f'PY_EMBED_INGEST_{index}_TYPE ({input_type}) not valid. '
                               f"Valid types are {', '.join(VALID_PYTHON_EMBED_TYPES)}")
                self.isOK = False

            # If input type is PANDAS, call ascii2nc? instead of RegridDataPlane
            if input_type == 'PANDAS':
                self.log_error('Running PyEmbedIngester on pandas data not yet implemented')
                self.isOK = False

            output_dir = self.config.getdir('PY_EMBED_INGEST_{}_OUTPUT_DIR'.format(index), '')
            output_template = self.config.getraw('filename_templates',
                                                 'PY_EMBED_INGEST_{}_OUTPUT_TEMPLATE'.format(index))
            output_grid = self.config.getraw('config', 'PY_EMBED_INGEST_{}_OUTPUT_GRID'.format(index), '')
            if output_grid == '':
                self.log_error(f'Must set PY_EMBED_INGEST_{index}_OUTPUT_GRID')
                self.isOK = False

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

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing loop string: {custom_string}")

                time_info['custom'] = custom_string

                if self.run_at_time_lead(time_info) is None:
                    return False

        return True

    def run_at_time_lead(self, time_info):
        rdp = self.c_dict['regrid_data_plane']

        # run each ingester specified
        for ingester in self.c_dict['INGESTERS']:
            index = ingester['index']

            # get grid information to project output data
            output_grid = do_string_sub(ingester['output_grid'],
                                        **time_info)

            # get call to python script
            script = do_string_sub(ingester['script'],
                                   **time_info)

            # get output file path
            output_file = do_string_sub(ingester['output_template'],
                                        **time_info)
            output_path = os.path.join(ingester['output_dir'], output_file)

            rdp.clear()
            rdp.infiles.append(f"PYTHON_{ingester['input_type']}")
            rdp.infiles.append(f'-field \'name="{script}\";\'')
            rdp.infiles.append(output_grid)
            rdp.outfile = output_path
            cmd = rdp.get_command()
            if cmd is None:
                self.log_error("Could not generate command")
                return
            self.logger.info(f'Running PyEmbed Ingester {index}')

            # run command and add to errors if it failed
            if not rdp.build():
                self.errors += 1
