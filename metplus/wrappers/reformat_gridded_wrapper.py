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

from ..util import get_lead_sequence
from ..util import time_util, skip_time
from . import LoopTimesWrapper

# pylint:disable=pointless-string-statement
'''!@namespace ReformatGriddedWrapper
@brief Common functionality to wrap similar MET applications
that reformat gridded data
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''


class ReformatGriddedWrapper(LoopTimesWrapper):
    """! Common functionality to wrap similar MET applications
         that reformat gridded data
    """
    def __init__(self, config, instance=None):
        super().__init__(config, instance=instance)

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. Processing forecast
             or observation data is determined by conf variables.
             This function loops over the list of forecast leads and runs
             the application for each.

            @param input_dict dictionary containing init or valid time info
        """
        app_name_caps = self.app_name.upper()
        run_list = []
        if self.config.getbool('config', 'FCST_'+app_name_caps+'_RUN', False):
            run_list.append("FCST")
        if self.config.getbool('config', 'OBS_'+app_name_caps+'_RUN', False):
            run_list.append("OBS")

        if not run_list:
            class_name = self.__class__.__name__[0: -7]
            self.log_error(f"{class_name} specified in process_list, but "
                           f"FCST_{app_name_caps}_RUN and "
                           f"OBS_{app_name_caps}_RUN  are both False. "
                           f"Set one or both to true or remove {class_name} "
                           "from the process_list")
            return

        for to_run in run_list:
            self.logger.info("Processing {} data".format(to_run))
            self.c_dict['VAR_LIST'] = self.c_dict.get(f'VAR_LIST_{to_run}')
            self.c_dict['DATA_SRC'] = to_run
            super().run_at_time(input_dict)
