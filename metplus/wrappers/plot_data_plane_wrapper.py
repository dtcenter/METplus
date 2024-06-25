"""
Program Name: plot_data_plane_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs plot_data_plane
History Log:  Initial version
Usage:
Parameters: None
Input Files: valid MET input files
Output Files: ps files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import time_util
from ..util import do_string_sub, remove_quotes, skip_time, get_lead_sequence
from . import LoopTimesWrapper

'''!@namespace PlotDataPlaneWrapper
@brief Wraps the PlotDataPlane tool to plot data
@endcode
'''


class PlotDataPlaneWrapper(LoopTimesWrapper):
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    def __init__(self, config, instance=None):
        self.app_name = "plot_data_plane"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               'LOG_PLOT_DATA_PLANE_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        c_dict['INPUT_DIR'] = self.config.getdir('PLOT_DATA_PLANE_INPUT_DIR',
                                                 '')
        c_dict['INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                                'PLOT_DATA_PLANE_INPUT_TEMPLATE')
        )
        if not c_dict['INPUT_TEMPLATE']:
            self.log_error("Must set PLOT_DATA_PLANE_INPUT_TEMPLATE")

        c_dict['OUTPUT_DIR'] = self.config.getdir('PLOT_DATA_PLANE_OUTPUT_DIR',
                                                  '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'PLOT_DATA_PLANE_OUTPUT_TEMPLATE')
        )
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error("Must set PLOT_DATA_PLANE_OUTPUT_TEMPLATE")

        c_dict['FIELD_NAME'] = (
            self.config.getraw('config',
                               'PLOT_DATA_PLANE_FIELD_NAME')
        )
        if not c_dict['FIELD_NAME']:
            self.log_error("Must set PLOT_DATA_PLANE_FIELD_NAME")

        c_dict['FIELD_LEVEL'] = (
            self.config.getraw('config',
                               'PLOT_DATA_PLANE_FIELD_LEVEL')
        )
        c_dict['FIELD_EXTRA'] = (
            self.config.getraw('config',
                               'PLOT_DATA_PLANE_FIELD_EXTRA')
        )

        c_dict['TITLE'] = (
            self.config.getraw('config',
                               'PLOT_DATA_PLANE_TITLE', '')
        )
        c_dict['COLOR_TABLE'] = (
            self.config.getraw('config',
                               'PLOT_DATA_PLANE_COLOR_TABLE', '')
        )
        c_dict['RANGE_MIN_MAX'] = (
            self.config.getraw('config',
                               'PLOT_DATA_PLANE_RANGE_MIN_MAX', '')
        )

        c_dict['CONVERT_TO_IMAGE'] = (
            self.config.getbool('config',
                                'PLOT_DATA_PLANE_CONVERT_TO_IMAGE',
                                False)
        )

        c_dict['CONVERT_EXE'] = self.config.getexe('CONVERT')
        if c_dict['CONVERT_TO_IMAGE'] and not c_dict['CONVERT_EXE']:
            self.log_error("[exe] CONVERT must be set correctly if "
                           "PLOT_DATA_PLANE_CONVERT_TO_IMAGE is True")
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

    def get_command(self):
        cmd = f"{self.app_path} {self.infiles[0]} {self.get_output_path()}"

        # add arguments
        cmd += ''.join(self.args)

        # add verbosity
        cmd += f" -v {self.c_dict['VERBOSITY']}"
        return cmd

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run plot_data_plane.
        Calls parent run_at_time_once (RuntimeFreq) then optionally converts
        PS output to PNG if requested.

        @param time_info dictionary containing timing information
        """
        self.clear()
        if not super().run_at_time_once(time_info):
            return False

        if self.c_dict['CONVERT_TO_IMAGE']:
            return self.convert_to_png(self.get_output_path())

        return True

    def find_input_files(self, time_info):
        # if using python embedding input, don't check if file exists,
        # just pass value to input file list
        if 'PYTHON' in self.c_dict['INPUT_TEMPLATE']:
            self.infiles.append(self.c_dict['INPUT_TEMPLATE'])
            return time_info

        file_path = self.find_data(time_info, return_list=False)
        if not file_path:
            return None

        self.infiles.append(file_path)
        return time_info

    def set_command_line_arguments(self, time_info):
        field_name = do_string_sub(self.c_dict['FIELD_NAME'],
                                   **time_info)
        field_info = f" 'name=\"{field_name}\";"
        if self.c_dict['FIELD_LEVEL']:
            field_level = remove_quotes(self.c_dict['FIELD_LEVEL'])
            field_info += f" level=\"{field_level}\";"

        if self.c_dict['FIELD_EXTRA']:
            field_info += f" {self.c_dict['FIELD_EXTRA']}"

        field_info += "'"
        self.args.append(field_info)

        if self.c_dict['TITLE']:
            title = do_string_sub(self.c_dict['TITLE'],
                                  **time_info)
            self.args.append(f' -title "{title}"')

        if self.c_dict['COLOR_TABLE']:
            color_table = do_string_sub(self.c_dict['COLOR_TABLE'],
                                        **time_info)
            self.args.append(f" -color_table {color_table}")

        if self.c_dict['RANGE_MIN_MAX']:
            range_min_max = do_string_sub(self.c_dict['RANGE_MIN_MAX'],
                                          **time_info)
            self.args.append(f" -plot_range {range_min_max}")

    def convert_to_png(self, ps_filename):
        """! Convert output postscript file to a rotated png image file

            @param ps_filename ps file generated by plot_data_plane
            @returns True if success, False if error
        """
        convert_exe = self.c_dict.get('CONVERT_EXE')
        if not convert_exe:
            self.log_error("[exe] CONVERT not set correctly. Cannot generate"
                           "image file.")
            return False

        png_filename = f"{os.path.splitext(ps_filename)[0]}.png"
        convert_command = (f"{convert_exe} -rotate 90 "
                           f"-background white -flatten "
                           f"{ps_filename} {png_filename}")

        return self.run_command(convert_command)
