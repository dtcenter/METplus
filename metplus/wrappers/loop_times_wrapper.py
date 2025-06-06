"""
Program Name: loop_times_wrapper.py
Contact(s): George McCabe
"""

from . import RuntimeFreqWrapper

'''!@namespace LoopTimesWrapper
@brief parent class for any wrapper that will loop over init/valid times
and forecast lead times
@endcode
'''


class LoopTimesWrapper(RuntimeFreqWrapper):

    def __init__(self, config, instance=None):
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # set default runtime frequency to run once for each runtime
        if not c_dict.get('RUNTIME_FREQ'):
            c_dict['RUNTIME_FREQ'] = 'RUN_ONCE_FOR_EACH'

        return c_dict
