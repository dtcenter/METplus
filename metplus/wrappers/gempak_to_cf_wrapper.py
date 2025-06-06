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

import os

from ..util import do_string_sub
from . import LoopTimesWrapper

'''!@namespace GempakToCFWrapper
@brief Wraps the GempakToCF tool to reformat Gempak format to NetCDF Format
@endcode
'''


class GempakToCFWrapper(LoopTimesWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    def __init__(self, config, instance=None):
        self.app_name = "GempakToCF"
        self.app_path = config.getstr('exe', 'GEMPAKTOCF_JAR', '')
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """!Create dictionary from config items to be used in the wrapper
            Allows developer to reference config items without having to know
            the type and consolidates config get calls so it is easier to see
            which config variables are used in the wrapper"""
        c_dict = super().create_c_dict()

        # set this for check if we are using Gempak data to ensure GempakToCF is found
        c_dict['INPUT_DATATYPE'] = 'GEMPAK'
        c_dict['INPUT_DIR'] = self.config.getdir('GEMPAKTOCF_INPUT_DIR', '')
        c_dict['INPUT_TEMPLATE'] = (
            self.config.getraw('config', 'GEMPAKTOCF_INPUT_TEMPLATE')
        )
        c_dict['OUTPUT_DIR'] = self.config.getdir('GEMPAKTOCF_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'GEMPAKTOCF_OUTPUT_TEMPLATE')
        )
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

    def get_command(self):
        cmd = "java -jar " + self.app_path

        if len(self.infiles) != 1:
            self.log_error("Only 1 input file can be selected")
            return None

        for infile in self.infiles:
            cmd += " " + infile

        if self.outfile == "":
            self.log_error("No output file specified")
            return None

        cmd += " " + self.get_output_path()
        return cmd

    def run_at_time_once(self, time_info):
        """! Runs the MET application for a given time and forecast lead combination

            @param time_info dictionary containing timing information
        """
        infile = do_string_sub(self.c_dict['INPUT_TEMPLATE'], **time_info)
        infile = os.path.join(self.c_dict.get('INPUT_DIR', ''), infile)
        self.infiles.append(infile)

        self.set_environment_variables(time_info)

        if not self.find_and_check_output_file(time_info):
            return

        self.build()
