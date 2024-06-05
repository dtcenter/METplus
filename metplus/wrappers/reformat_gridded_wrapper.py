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

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # check if FCST or OBS should be run
        app = self.app_name.upper()
        for fcst_or_obs in ('FCST', 'OBS'):
            c_dict[f'{fcst_or_obs}_RUN'] = (
                self.config.getbool('config', f'{fcst_or_obs}_{app}_RUN', False)
            )

        if not c_dict['FCST_RUN'] and not c_dict['OBS_RUN']:
            self.log_error(f'Must set FCST_{app}_RUN or OBS_{app}_RUN')
            return c_dict

        return c_dict

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. Processing forecast
             or observation data is determined by conf variables.
             This function loops over the list of forecast leads and runs
             the application for each.

            @param input_dict dictionary containing init or valid time info
        """
        run_list = []
        if self.c_dict['FCST_RUN']:
            run_list.append("FCST")
        if self.c_dict['OBS_RUN']:
            run_list.append("OBS")

        for to_run in run_list:
            self.logger.info("Processing {} data".format(to_run))
            self.c_dict['VAR_LIST'] = self.c_dict.get(f'VAR_LIST_{to_run}')
            self.c_dict['DATA_SRC'] = to_run
            super().run_at_time(input_dict)
