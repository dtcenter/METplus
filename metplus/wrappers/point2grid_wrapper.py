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

from ..util import do_string_sub
from ..util import remove_quotes
from . import LoopTimesWrapper

'''!@namespace Point2GridWrapper
@brief Wraps the Point2Grid tool to reformat ascii format to NetCDF
@endcode
'''


class Point2GridWrapper(LoopTimesWrapper):
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    def __init__(self, config, instance=None):
        self.app_name = "point2grid"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

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

        c_dict['GRID_TEMPLATE'] = (
            self.config.getraw('config', 'POINT2GRID_REGRID_TO_GRID')
        )
        # grid is required
        if not c_dict['GRID_TEMPLATE']:
            self.log_error('Must specify a grid name')

        # optional arguments
        c_dict['INPUT_FIELD'] = self.config.getraw('config',
                                                   'POINT2GRID_INPUT_FIELD',
                                                   '')
        # input field is required
        if not c_dict['INPUT_FIELD']:
            self.log_error('Must specify a field with POINT2GRID_INPUT_FIELD')

        c_dict['INPUT_LEVEL'] = self.config.getraw('config',
                                                   'POINT2GRID_INPUT_LEVEL',
                                                   '')

        c_dict['QC_FLAGS'] = self.config.getraw('config',
                                                'POINT2GRID_QC_FLAGS')
        c_dict['ADP'] = self.config.getraw('config', 'POINT2GRID_ADP')

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
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
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

        # add grid name
        grid = remove_quotes(self.c_dict['GRID'])
        cmd += f' "{grid}"'

        # add output path
        out_path = self.get_output_path()
        cmd += ' ' + out_path

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def find_input_files(self, time_info):
        """!Find input file and mask file and add them to the list of input files.
            Args:
                @param time_info time dictionary for current run time
                @returns time_info if all files were found, None otherwise
        """
        # get input file
        # calling find_obs because we set OBS_ variables in c_dict for the input data
        input_path = self.find_obs(time_info)
        if input_path is None:
            return None

        self.infiles.append(input_path)

        self.c_dict['GRID'] = do_string_sub(self.c_dict['GRID_TEMPLATE'],
                                            **time_info)

        return time_info

    def set_command_line_arguments(self, time_info):
        """!Set command line arguments from c_dict
            Args:
                @param time_info time dictionary to use for string substitution"""

        #input_field and input_level go hand in hand. If there is a field there needs to be a level
        #even if it is blank
        input_field = do_string_sub(self.c_dict['INPUT_FIELD'], **time_info)
        input_level = ""
        if self.c_dict['INPUT_LEVEL']:
            input_level = do_string_sub(self.c_dict['INPUT_LEVEL'],
                                        **time_info)
            self.logger.info(f"Processing level: {input_level}")
        #Add either the specified level above or the defauilt blank one
        self.args.append(f"-field 'name=\"{input_field}\"; level=\"{input_level}\";'")

        if self.c_dict['QC_FLAGS'] != '':
            self.args.append(f"-qc {self.c_dict['QC_FLAGS']}")

        if self.c_dict['ADP']:
            self.args.append(f"-adp {self.c_dict['ADP']}")

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

        # string sub all args
        for index, value in enumerate(self.args):
            self.args[index] = do_string_sub(value, **time_info)
