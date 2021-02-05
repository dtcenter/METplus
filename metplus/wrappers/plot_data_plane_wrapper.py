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

from ..util import met_util as util
from ..util import time_util
from . import CommandBuilder
from ..util import do_string_sub

'''!@namespace PlotDataPlaneWrapper
@brief Wraps the PlotDataPlane tool to plot data
@endcode
'''


class PlotDataPlaneWrapper(CommandBuilder):
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "plot_data_plane"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

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

        return c_dict

    def get_command(self):
        cmd = f"{self.app_path} {self.infiles[0]} {self.get_output_path()}"

        # add arguments
        cmd += ''.join(self.args)

        # add verbosity
        cmd += f" -v {self.c_dict['VERBOSITY']}"
        return cmd

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
              loops over the list of forecast leads and runs the application for
              each.
              Args:
                @param input_dict dictionary containing timing information
        """
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            self.clear()
            input_dict['lead'] = lead

            time_info = time_util.ti_calculate(input_dict)

            if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                self.logger.debug('Skipping run time')
                continue

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info("Processing custom string: "
                                     f"{custom_string}")

                time_info['custom'] = custom_string

                self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ascii2nc
             Args:
                @param time_info dictionary containing timing information
        """
        self.clear()

        # get input files
        if not self.find_input_files(time_info):
            return False

        # get output path
        if not self.find_and_check_output_file(time_info):
            return False

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        if not self.build():
            return False

        if self.c_dict['CONVERT_TO_IMAGE']:
            return self.convert_to_png(self.get_output_path())

        return True

    def find_input_files(self, time_info):
        # if using python embedding input, don't check if file exists,
        # just pass value to input file list
        if 'PYTHON' in self.c_dict['INPUT_TEMPLATE']:
            self.infiles.append(self.c_dict['INPUT_TEMPLATE'])
            return self.infiles

        file_path = self.find_data(time_info,
                                   var_info=None,
                                   return_list=False)
        if not file_path:
            return None

        self.infiles.append(file_path)
        return self.infiles

    def set_command_line_arguments(self, time_info):
        field_name = do_string_sub(self.c_dict['FIELD_NAME'],
                                   **time_info)
        field_info = f" 'name=\"{field_name}\";"
        if self.c_dict['FIELD_LEVEL']:
            field_level = util.remove_quotes(self.c_dict['FIELD_LEVEL'])
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
