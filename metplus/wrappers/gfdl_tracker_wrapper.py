"""
Program Name: gfdl_tracker_wrapper.py
Contact(s): George McCabe
Abstract: Builds commands to run GFDL Tracker
History Log:  Initial version
Usage: Not meant to be run
Parameters: None
Input Files: None
Output Files: None
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub, ti_calculate, get_lead_sequence
from . import CommandBuilder

class GFDLTrackerWrapper(CommandBuilder):
    """!Wrapper can be used as a base to develop a new wrapper"""
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'gfdl_tracker'
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # get values from config object and set them to be accessed by wrapper
        gfdl_tracker_base = self.config.getdir('GFDL_TRACKER_BASE', '')
        if not gfdl_tracker_base:
            self.log_error('GFDL_TRACKER_BASE must be set.')
            return c_dict

        c_dict['INPUT_GRIB_VERSION'] = self.config.getint('config',
                                                          'GFDL_TRACKER_GRIB_VERSION',
                                                          '')

        if c_dict['INPUT_GRIB_VERSION'] == 1:
            index_script_name = 'grbindex.exe'
        elif c_dict['INPUT_GRIB_VERSION'] == 2:
            index_script_name = 'grb2index.exe'
        else:
            self.log_error("GFDL_TRACKER_GRIB_VERSION "
                           f"({c_dict['INPUT_GRIB_VERSION']}) "
                           "must be 1 or 2")
            return c_dict

        c_dict['INDEX_SCRIPT'] = os.path.join(gfdl_tracker_base,
                                              'trk_exec',
                                              index_script_name)

        if not os.path.exists(c_dict['INDEX_SCRIPT']):
            self.log_error("GRIB index script does not exist: "
                           f"{c_dict['INDEX_SCRIPT']}")

        c_dict['INPUT_TEMPLATE'] = self.config.getraw('config',
                                                      'GFDL_TRACKER_INPUT_TEMPLATE', '')
        c_dict['INPUT_DIR'] = self.config.getdir('GFDL_TRACKER_INPUT_DIR', '')

        if not c_dict['INPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_INPUT_TEMPLATE must be set. ')

        return c_dict

    def run_at_time(self, input_dict):
        """! Do some processing for the current run time (init or valid)
              Args:
                @param input_dict dictionary containing time information of current run
                        generally contains 'now' (current) time and 'init' or 'valid' time
        """
        # create index files for each input file

        # replace values in input.nml

        # run tracker passing in input.nml configuration file

        # get forecast leads to loop over
        lead_seq = get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            input_dict['lead'] = lead

            # recalculate time info items
            time_info = ti_calculate(input_dict)

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                time_info['custom'] = custom_string
                input_files = self.find_data(time_info=time_info,
                                             return_list=True)
                self.logger.debug(f'Found files: {input_files}')

        return True
