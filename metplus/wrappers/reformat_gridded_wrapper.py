'''
Program Name: reformat_gridded_wrapper.py
Contact(s): George McCabe
Abstract: Parent class of all apps designed to reformat gridded data
History Log:  Initial version
Usage:
Parameters: None
Input Files: nc files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
'''

import os

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder

# pylint:disable=pointless-string-statement
'''!@namespace ReformatGriddedWrapper
@brief Common functionality to wrap similar MET applications
that reformat gridded data
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''

class ReformatGriddedWrapper(CommandBuilder):
    """!Common functionality to wrap similar MET applications
that reformat gridded data
    """
    def __init__(self, config, instance=None, config_overrides={}):
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    # this class should not be called directly
    # pylint:disable=unused-argument
    def run_at_time_once(self, time_info, var_list, data_type):
        """!To be implemented by child class"""
        self.log_error('ReformatGridded wrapper cannot be called directly.'+\
                          ' Please use child wrapper')
        return

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. Processing forecast
              or observation data is determined by conf variables. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """
        app_name_caps = self.app_name.upper()
        class_name = self.__class__.__name__[0: -7]
        lead_seq = util.get_lead_sequence(self.config, input_dict)

        run_list = []
        if self.config.getbool('config', 'FCST_'+app_name_caps+'_RUN', False):
            run_list.append("FCST")
        if self.config.getbool('config', 'OBS_'+app_name_caps+'_RUN', False):
            run_list.append("OBS")

        if not run_list:
            self.log_error(class_name+" specified in process_list, but "+\
                              "FCST_"+app_name_caps+"_RUN and OBS_"+app_name_caps+"_RUN "+\
                              " are both False. Set one or both to true or "+\
                              "remove "+class_name+" from the process_list")
            return

        for to_run in run_list:
            self.logger.info("Processing {} data".format(to_run))
            for lead in lead_seq:
                input_dict['lead'] = lead

                time_info = time_util.ti_calculate(input_dict)

                self.logger.info("Processing forecast lead {}".format(time_info['lead_string']))


                if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                    self.logger.debug('Skipping run time')
                    continue

                # loop over custom string list and set custom in the time_info dictionary
                for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                    if custom_string:
                        self.logger.info(f"Processing custom string: {custom_string}")

                    time_info['custom'] = custom_string
                    self.c_dict['CUSTOM_STRING'] = custom_string

                    var_list = util.parse_var_list(self.config, time_info, data_type=to_run)
                    if not var_list:
                        var_list = None

                    self.run_at_time_once(time_info, var_list, to_run)
