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
import pandas

from ..util import time_util
from ..util import do_string_sub, get_lead_sequence
from . import LoopTimesWrapper
from . import RegridDataPlaneWrapper

VALID_PYTHON_EMBED_TYPES = ['NUMPY', 'XARRAY', 'PANDAS']


class PyEmbedIngestWrapper(LoopTimesWrapper):
    """!Wrapper to utilize Python Embedding in the MET tools to read in
    data using a python script"""
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    def __init__(self, config, instance=None):
        self.app_name = 'py_embed_ingest'
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper

        c_dict['INGESTERS'] = []

        # find all PY_EMBED_INGEST_<n>_TEMPLATE keys in the conf files
        all_conf = self.config.keys('config')
        indices = set()
        regex = re.compile(r"PY_EMBED_INGEST_(\d+)_SCRIPT")
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                indices.add(result.group(1))

        indices = sorted(indices)
        for index in indices:
            input_type = self.config.getstr('config', 'PY_EMBED_INGEST_{}_TYPE'.format(index))
            input_type = input_type.upper()
            if input_type not in VALID_PYTHON_EMBED_TYPES:
                self.log_error(f'PY_EMBED_INGEST_{index}_TYPE ({input_type}) not valid. '
                               f"Valid types are {', '.join(VALID_PYTHON_EMBED_TYPES)}")

            # If input type is PANDAS, call ascii2nc? instead of RegridDataPlane
            if input_type == 'PANDAS':
                self.log_error('Running PyEmbedIngester on pandas data not yet implemented')

            output_dir = self.config.getdir('PY_EMBED_INGEST_{}_OUTPUT_DIR'.format(index), '')
            output_template = self.config.getraw('filename_templates',
                                                 'PY_EMBED_INGEST_{}_OUTPUT_TEMPLATE'.format(index))
            output_grid = self.config.getraw('config', 'PY_EMBED_INGEST_{}_OUTPUT_GRID'.format(index), '')
            if output_grid == '':
                self.log_error(f'Must set PY_EMBED_INGEST_{index}_OUTPUT_GRID')


            ingest_script_search_text = f'PY_EMBED_INGEST_{index}_SCRIPT'
            regex = re.compile(ingest_script_search_text + r"(.*)")
            ingest_script_addons = []
            for conf in all_conf:
                result = regex.match(conf)
                if result is not None:
                    ingest_script_addons.append(result.group(1))

            # error if none are found
            if not ingest_script_addons:
                self.log_error(f"No ingest scripts specified for PY_EMBED_INGEST_{index}")
                return

            ingest_scripts = self.get_ingest_items('SCRIPT', index, ingest_script_addons)
            output_field_names = self.get_ingest_items('OUTPUT_FIELD_NAME', index, ingest_script_addons)

            # if output_field_names is not empty and the two lists are different sizes, error
            if output_field_names and len(ingest_scripts) != len(output_field_names):
                self.log_error(f"If using PY_EMBED_INGEST_{index}_OUTPUT_FIELD_NAME*, the number "
                               "of output names must match the number of "
                               f"PY_EMBED_INGEST_{index}_SCRIPT* values")
                return

            ingester_dict = {'output_dir': output_dir,
                             'output_template': output_template,
                             'output_field_names': output_field_names,
                             'scripts': ingest_scripts,
                             'input_type': input_type,
                             'output_grid': output_grid,
                             'index': index,
                            }

            c_dict['INGESTERS'].append(ingester_dict)

        # set config values for RegridDataPlane instance
        instance = 'py_embed_ingest_rdp'
        if not self.config.has_section(instance):
            self.config.add_section(instance)
        self.config.set(instance,
                        'REGRID_DATA_PLANE_SKIP_IF_OUTPUT_EXISTS',
                        c_dict['SKIP_IF_OUTPUT_EXISTS'])

        c_dict['regrid_data_plane'] = (
            RegridDataPlaneWrapper(self.config,
                                   instance=instance)
        )
        return c_dict

    def get_ingest_items(self, item_type, index, ingest_script_addons):
        ingest_items = []
        # for each addon, get raw value for ingest_script or output field name
        for addon in ingest_script_addons:
            ingest_item = self.config.getraw('config',
                                             f"PY_EMBED_INGEST_{index}_{item_type}{addon if addon else ''}")

            # add to list of ingest_items
            if ingest_item:
                ingest_items.append(ingest_item)

        return ingest_items

    def run_at_time_once(self, time_info):
        rdp = self.c_dict['regrid_data_plane']

        # run each ingester specified
        for ingester in self.c_dict['INGESTERS']:
            index = ingester['index']

            # get grid information to project output data
            output_grid = do_string_sub(ingester['output_grid'],
                                        **time_info)

            rdp.clear()
            # get output file path
            rdp.c_dict['OUTPUT_DIR'] = ingester['output_dir']
            rdp.c_dict['OUTPUT_TEMPLATE'] = ingester['output_template']
            if not rdp.find_and_check_output_file(time_info):
                continue

            rdp.infiles.append(f"PYTHON_{ingester['input_type']}")

            for script_raw in ingester['scripts']:
                script = do_string_sub(script_raw,
                                       **time_info)

                rdp.infiles.append(f'-field \'name="{script}\";\'')

            if ingester['output_field_names']:
                rdp.infiles.append(f"-name {','.join(ingester['output_field_names'])}")

            rdp.infiles.append(output_grid)

            rdp.set_environment_variables(time_info)

            self.logger.info(f'Running PyEmbed Ingester {index}')

            # run command and add to errors if it failed
            if not rdp.build():
                self.errors += 1

            self.all_commands.extend(rdp.all_commands)
            rdp.all_commands.clear()

        return True
