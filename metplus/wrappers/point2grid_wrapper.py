"""
Program Name: point2grid_wrapper.py
Contact(s): Hank Fisher 
Abstract: Builds command for and runs point2grid
History Log:  Initial version
Usage:
Parameters: None
Input Files: nc files
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import CommandBuilder

'''!@namespace Point2GridWrapper
@brief Wraps the Point2Grid tool to reformat ascii format to NetCDF
@endcode
'''


class Point2GridWrapper(CommandBuilder):

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = "point2grid"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_POINT2GRID_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['ALLOW_MULTIPLE_FILES'] = False

        # input and output files
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('POINT2GRID_INPUT_DIR',
                                                     '')

        c_dict['OBS_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                          'POINT2GRID_INPUT_TEMPLATE')

        if not c_dict['OBS_INPUT_TEMPLATE']:
            self.log_error("POINT2GRID_INPUT_TEMPLATE required to run")

        c_dict['OUTPUT_DIR'] = self.config.getdir('POINT2GRID_OUTPUT_DIR',
                                                  '')

        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'POINT2GRID_OUTPUT_TEMPLATE')

        # handle window variables [POINT2GRID_]FILE_WINDOW_[BEGIN/END]
        c_dict['OBS_FILE_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'POINT2GRID_FILE_WINDOW_BEGIN',
                                 self.config.getseconds('config',
                                                        'OBS_FILE_WINDOW_BEGIN', 0))

        c_dict['OBS_FILE_WINDOW_END'] = \
          self.config.getseconds('config', 'POINT2GRID_FILE_WINDOW_END',
                                 self.config.getseconds('config',
                                                        'OBS_FILE_WINDOW_END', 0))

        c_dict['GRID'] = self.config.getstr('config',
                                            'POINT2GRID_REGRID_TO_GRID',
                                            '')

        # optional arguments
        c_dict['INPUT_FIELD'] = self.config.getraw('config',
                                                   'POINT2GRID_INPUT_FIELD',
                                                   '')

        c_dict['INPUT_LEVEL'] = self.config.getraw('config',
                                                   'POINT2GRID_INPUT_LEVEL',
                                                   '')

        c_dict['QC_FLAGS'] = self.config.getbool('config',
                                                        'POINT2GRID_QC_FLAGS',
                                                        '')
        c_dict['ADP'] = self.config.getstr('config',
                                                        'POINT2GRID_ADP',
                                                        '')

        c_dict['REGRID_METHOD'] = self.config.getstr('config',
                                                   'POINT2GRID_REGRID_METHOD',
                                                   '')

        c_dict['GAUSSIAN_DX'] = self.config.getstr('config',
                                                          'POINT2GRID_GAUSSIAN_DX',
                                                          '')

        c_dict['GAUSSIAN_RADIUS'] = self.config.getstr('config',
                                                     'POINT2GRID_GAUSSIAN_RADIUS',
                                                     '')

        c_dict['PROB_CAT_THRESH'] = self.config.getstr('config',
                                              'POINT2GRID_PROB_CAT_THRESH',
                                              '')

        c_dict['VLD_THRESH'] = self.config.getstr('config',
                                              'POINT2GRID_VLD_THRESH',
                                              '')

        return c_dict

    def get_command(self):
        cmd = self.app_path

        # don't run if no input or output files were found
        if not self.infiles:
            self.log_error("No input files were found")
            return

        if not self.outfile:
            self.log_error("No output file specified")
            return

        # add input files
        for infile in self.infiles:
            cmd += ' ' + infile

        # add grid name. point2grid requires a grid name between the input and output files
        if not self.c_dict['GRID']:
            self.log_error('Must specify a grid name')
            return None
        cmd += ' ' + self.c_dict['GRID'] 

        # add output path
        out_path = self.get_output_path()
        cmd += ' ' + out_path

        parent_dir = os.path.dirname(out_path)
        if parent_dir == '':
            self.log_error('Must specify path to output file')
            return None

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
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
            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                time_info['custom'] = custom_string

                self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run point2grid
             Args:
                @param time_info dictionary containing timing information
        """
        # get input files
        if self.find_input_files(time_info) is None:
            return

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return

        self.build()

    def find_input_files(self, time_info):
        """!Find input file and mask file and add them to the list of input files.
            Args:
                @param time_info time dictionary for current run time
                @returns List of input files found or None if either file was not found
        """
        # get input file
        # calling find_obs because we set OBS_ variables in c_dict for the input data
        input_path = self.find_obs(time_info,
                                   var_info=None)
        if input_path is None:
            return None

        self.infiles.append(input_path)

        return self.infiles

    def set_command_line_arguments(self, time_info):
        """!Set command line arguments from c_dict
            Args:
                @param time_info time dictionary to use for string substitution"""

        #input_field and input_level go hand in hand. If there is a field there needs to be a level
        #even if it is blank
        input_level = ""
        if self.c_dict['INPUT_FIELD']:
            input_field = do_string_sub(self.c_dict['INPUT_FIELD'],
                                        **time_info)
            if self.c_dict['INPUT_LEVEL']:
                input_level = do_string_sub(self.c_dict['INPUT_LEVEL'],
                                            **time_info)
                self.logger.info(f"Processing level: {input_level}")
            #Add either the specified level above or the defauilt blank one
            self.args.append(f"-field 'name=\"{input_field}\"; level=\"{input_level}\";'")

        if self.c_dict['QC_FLAGS']:
            self.args.append("-qc")

        if self.c_dict['ADP']:
            self.args.append("-adp")

        if self.c_dict['REGRID_METHOD']:
            self.args.append(f"-method {self.c_dict['REGRID_METHOD']}")

        if self.c_dict['GAUSSIAN_DX']:
            self.args.append(f"-gaussian_dx {self.c_dict['GAUSSIAN_DX']}")

        if self.c_dict['GAUSSIAN_RADIUS']:
            self.args.append(f"-gaussian_radius {self.c_dict['GAUSSIAN_RADIUS']}")

        if self. c_dict['PROB_CAT_THRESH']:
            self.args.append(f"-prob_cat_thresh {self.c_dict['PROB_CAT_THRESH']}")

        if self. c_dict['VLD_THRESH']:
            self.args.append(f"-vld_thresh {self.c_dict['VLD_THRESH']}")
