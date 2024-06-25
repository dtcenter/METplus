"""
Program Name: reformat_point_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs MET tools that reformat point obs
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

from ..util import ti_calculate
from . import RuntimeFreqWrapper

'''!@namespace ReformatPointWrapper
@brief Wraps the MET tools that reformat point observation data
@endcode
'''


class ReformatPointWrapper(RuntimeFreqWrapper):
    def create_c_dict(self):
        c_dict = super().create_c_dict()
        app_upper = self.app_name.upper()

        # populate OBS input templates using app name
        self.get_input_templates(c_dict, {
            'OBS': {'prefix': app_upper, 'required': True},
        })

        # set output templates using app name
        c_dict['OUTPUT_DIR'] = self.config.getdir(f'{app_upper}_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', f'{app_upper}_OUTPUT_TEMPLATE')
        )
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error(f'{app_upper}_OUTPUT_TEMPLATE must be set')

        return c_dict

    def get_command(self):
        """!Build command to run

        @returns str command
        """
        return (f"{self.app_path} {' '.join(self.infiles)}"
                f" {self.get_output_path()}"
                f"{' ' + ' '.join(self.args) if self.args else ''}"
                f" -v {self.c_dict['VERBOSITY']}")

    def _get_offset_time_info(self, time_info):
        """!Get offset value that was used to find input data so the output
        time information can include the correct offset value. Copy the time
        information dictionary, then remove the offset variables if they are
        set and replace them with the computed offset from the first set of
        files that were found. This is primarily needed so that PB2NC wrapper
        can write output files that contain the offset.

        @param time_info dictionary containing time information from run
        @returns time info dictionary with input offset value included
        """
        temp_time_info = time_info.copy()
        for key in ('offset', 'offset_hours'):
            if key in temp_time_info:
                del temp_time_info[key]
            val = self.c_dict['ALL_FILES'][0].get('time_info').get(key)
            if val:
                temp_time_info[key] = val

        return ti_calculate(temp_time_info)

    def find_input_files(self, time_info):
        if not self.c_dict.get('ALL_FILES'):
            return None

        input_files = []
        for files in self.c_dict['ALL_FILES']:
            new_files = files.get('OBS', [])
            if not new_files:
                continue
            input_files.extend(new_files)

        if not input_files:
            return None

        self.logger.debug(f"Adding input: {' and '.join(input_files)}")
        self.infiles.extend(input_files)

        return self._get_offset_time_info(time_info)
