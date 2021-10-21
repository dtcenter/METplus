"""
Program Name: loop_times_wrapper.py
Contact(s): George McCabe
"""

from . import CommandBuilder
from ..util import get_lead_sequence, skip_time, ti_calculate

'''!@namespace LoopTimesWrapper
@brief parent class for any wrapper that will loop over init/valid times
and forecast lead times
@endcode
'''


class LoopTimesWrapper(CommandBuilder):

    def __init__(self, config, instance=None, config_overrides=None):
        # set app_name if not set by child class to allow tests to run
        if not hasattr(self, 'app_name'):
            self.app_name = 'loop_times'

        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
             loops over the list of forecast leads and runs the application for
             each.

                @param input_dict dictionary containing timing information
        """
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string

            for lead in get_lead_sequence(self.config, input_dict):
                self.clear()

                input_dict['lead'] = lead

                time_info = ti_calculate(input_dict)

                if skip_time(time_info, self.c_dict.get('SKIP_TIMES')):
                    continue

                self.run_at_time_once(time_info)

        return True
