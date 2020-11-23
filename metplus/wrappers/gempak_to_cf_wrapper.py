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

from ..util import met_util as util
from ..util import do_string_sub
from ..util import time_util
from . import CommandBuilder

'''!@namespace GempakToCFWrapper
@brief Wraps the GempakToCF tool to reformat Gempak format to NetCDF Format
@endcode
'''


class GempakToCFWrapper(CommandBuilder):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "GempakToCF"
        self.app_path = config.getstr('exe', 'GEMPAKTOCF_JAR', '')
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        """!Create dictionary from config items to be used in the wrapper
            Allows developer to reference config items without having to know
            the type and consolidates config get calls so it is easier to see
            which config variables are used in the wrapper"""
        c_dict = super().create_c_dict()

        # set this for check if we are using Gempak data to ensure GempakToCF is found
        c_dict['INPUT_DATATYPE'] = 'GEMPAK'
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

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. Processing forecast
              or observation data is determined by conf variables. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param input_dict dictionary containing timing information
        """
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            self.clear()
            input_dict['lead'] = lead
            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                input_dict['custom'] = custom_string

                time_info = time_util.ti_calculate(input_dict)

                if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                    self.logger.debug('Skipping run time')
                    continue

                self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Runs the MET application for a given time and forecast lead combination
             Args:
                @param time_info dictionary containing timing information
        """
        valid_time = time_info['valid']
        input_dir = self.config.getdir('GEMPAKTOCF_INPUT_DIR')
        input_template = self.config.getraw('filename_templates',
                                            'GEMPAKTOCF_INPUT_TEMPLATE')
        output_dir = self.config.getdir('GEMPAKTOCF_OUTPUT_DIR')
        output_template = self.config.getraw('filename_templates',
                                             'GEMPAKTOCF_OUTPUT_TEMPLATE')

        infile = do_string_sub(input_template,
                               valid=valid_time)
        infile = os.path.join(input_dir, infile)
        self.infiles.append(infile)

        outfile = do_string_sub(output_template,
                                valid=valid_time)
        outfile = os.path.join(output_dir, outfile)

        if os.path.exists(outfile) and \
                        self.config.getbool('config', 'GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS', False) is True:
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'GEMPAKTOCF_SKIP_IF_OUTPUT_EXISTS to True to process'
                              .format(outfile))
            return

        self.set_output_path(outfile)

        if not os.path.exists(os.path.dirname(outfile)):
            os.makedirs(os.path.dirname(outfile))

        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return

        self.build()
