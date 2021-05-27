'''
Program Name: tcmpr_plotter_wrapper.py
Contact(s): George McCabe
'''

import os
import shutil

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import CommandBuilder

class TCMPRPlotterWrapper(CommandBuilder):
    """! A Python class than encapsulates the plot_tcmpr.R plotting script.

    Generates plots for input files with .tcst format and
    creates output subdirectory based on the input tcst file.
    The plot_tcmpr.R plot also supports additional filtering by calling
    MET tool tc_stat. This wrapper extends plot_tcmpr.R by allowing the user
    to specify as input a directory (to support plotting all files in the
    specified directory and its subdirectories). The user can now either
    indicate a file or directory in the (required) -lookin option.
    """

    ARGUMENTS = {
        'config': 'string',
        'lookin': 'string/quotes',
        'outdir': 'string',
        'prefix': 'string',
        'title': 'string/quotes',
        'subtitle': 'string/quotes',
        'xlab': 'string/quotes',
        'ylab': 'string/quotes',
        'xlim': 'string',
        'ylim': 'string',
        'filter': 'string/quotes',
        'tcst': 'string',
        'dep': 'list',
        'scatter_x': 'string',
        'scatter_y': 'string',
        'skill_ref': 'string',
        'series': 'string',
        'series_ci': 'string',
        'legend': 'string/quotes',
        'lead': 'string',
        'plot': 'list',
        'rp_diff': 'string',
        'demo_yr': 'string',
        'hfip_bsln': 'string',
        'plot_config': 'string',
        'save_data': 'string',
        'footnote_flag': 'bool',
        'no_ee': 'bool',
        'no_log': 'bool',
        'save': 'bool',
    }

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'tcmpr_plotter'

        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # check if R is available, do not attempt to run if it is not
        if shutil.which('Rscript') is None:
            self.log_error('Rscript must be in the path')

            # if not running script, reset isOK to True for tests
            if self.c_dict.get('DO_NOT_RUN_EXE', False):
                self.isOK = True

        # save MET_INSTALL_DIR to find R script and set environment variable
        c_dict['MET_INSTALL_DIR'] = self.config.getdir('MET_INSTALL_DIR', '')
        c_dict['TCMPR_SCRIPT'] = os.path.join(c_dict['MET_INSTALL_DIR'],
                                              'share', 'met', 'Rscripts',
                                              'plot_tcmpr.R')

        # check that R script can be found
        if not os.path.exists(c_dict['TCMPR_SCRIPT']):
            self.log_error('plot_tcmpr.R script could not be found')

        # get input data
        c_dict['INPUT_DATA'] = (
            self.config.getraw('config', 'TCMPR_PLOTTER_TCMPR_DATA_DIR', '')
        )
        if not c_dict['INPUT_DATA']:
            self.log_error("TCMPR_PLOTTER_TCMPR_DATA_DIR must be set")

        # get output directory
        c_dict['OUTPUT_DIR'] = self.config.getdir(
            'TCMPR_PLOTTER_PLOT_OUTPUT_DIR', ''
        )
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set TCMPR_PLOTTER_PLOT_OUTPUT_DIR")

        # get config file
        c_dict['CONFIG_FILE'] = self.config.getraw('config',
                                                   'TCMPR_PLOTTER_CONFIG_FILE',
                                                   '')
        if not c_dict['CONFIG_FILE']:
            self.log_error("TCMPR_PLOTTER_CONFIG_FILE must be set")

        # get time information
        input_dict = self.set_time_dict_for_single_runtime()
        if not input_dict:
            self.isOK = False
        c_dict['TIME_INFO'] = time_util.ti_calculate(input_dict)

        # read all optional command line arguments
        c_dict['COMMAND_ARGS'] = self.read_optional_args()

        return c_dict

    def read_optional_args(self):
        """! Read config variables and add arguments to command """
        prefix = f'{self.app_name.upper()}_'
        command_args = []

        for name, data_type in self.ARGUMENTS.items():
            config_name = f'{prefix}{name.upper()}'

            # skip required arguments because they are handled elsewhere
            if name == 'config' or name == 'lookin' or name == 'outdir':
                continue

            # handle config name exceptions that differ from argument name
            if name == 'plot':
                config_name = f'{config_name}_TYPES'
            elif name == 'dep':
                config_name = f'{config_name}_VARS'
            elif name == 'tcst':
                config_name = f'{prefix}FILTERED_TCST_DATA_FILE'
            elif name == 'plot_config':
                config_name = f'{config_name}_OPTS'

            if 'string' in data_type:
                value = self.config.getraw('config', config_name, '')
            elif 'bool' in data_type:
                value = self.config.getbool('config', config_name, '')
            elif 'list' in data_type:
                value = util.getlist(self.config.getraw('config',
                                                        config_name,
                                                        ''))
                value = ','.join(value)
            else:
                self.log_error(f"Invalid type for {name}: {data_type}")

            if value:
                # add quotes around value if they are not already there
                if 'quotes' in data_type:
                    value = f'"{util.remove_quotes(value)}"'

                arg_string = f'-{name}'
                # don't add value for boolean
                if data_type != 'bool':
                    arg_string = f'{arg_string} {value}'

                self.logger.debug(f"Adding argument: {arg_string}")
                command_args.append(f'{arg_string}')

        return command_args

    def set_environment_variables(self):
        """!Set environment variables that are needed to run """
        self.add_env_var('MET_INSTALL_DIR', self.c_dict['MET_INSTALL_DIR'])
        super().set_environment_variables()

    def run_all_times(self):
        """! Builds the command for invoking tcmpr.R plot script. """
        self.logger.debug(f"Script: {self.c_dict['TCMPR_SCRIPT']}")
        self.logger.debug(f"Config File: {self.c_dict['CONFIG_FILE']}")
        self.logger.debug(f"Input: {self.c_dict['INPUT_DATA']}")
        self.logger.debug(f"Output Directory: {self.c_dict['OUTPUT_DIR']}")

        self.infiles = self.get_input_files()

        # Create the TCMPR output directory, where the plots will be written
        if not os.path.exists(self.c_dict['OUTPUT_DIR']):
            self.logger.debug("Creating directory: "
                              f"{self.c_dict['OUTPUT_DIR']}")
            os.makedirs(self.c_dict['OUTPUT_DIR'])

        self.set_environment_variables()
        self.build()

        self.logger.info("Plotting complete")
        return self.all_commands

    def get_input_files(self):
        """! Get input file paths. If input is a directory, find all .tcst
        files inside the directory.

            @returns list of file paths
        """
        input_data = do_string_sub(self.c_dict['INPUT_DATA'],
                                   **self.c_dict['TIME_INFO'])
        # If input data is a file, create a single command and invoke R script.
        if os.path.isfile(input_data):
            self.logger.debug(f"Plotting file: {input_data}")
            return [input_data]

        # input is directory, so find all tcst files to process
        self.logger.debug(f'Plotting all files in: {input_data}')
        input_files = util.get_files(input_data, ".*.tcst")
        self.logger.debug(f"Number of files: {len(input_files)}")
        return sorted(input_files)

    def get_command(self):
        """! Over-ride CommandBuilder's get_command because unlike
             other MET tools, tcmpr_plotter_wrapper handles input
             files differently because it wraps an R-script, plot_tcmpr.R
             rather than a typical MET tool. Build command to run from
             arguments"""
        args = self.c_dict['COMMAND_ARGS']
        arg_string = f" {' '.join(args)}" if args else ''
        cmd = (f"Rscript {self.c_dict['TCMPR_SCRIPT']}"
               f" -config {self.c_dict['CONFIG_FILE']}"
               f"{arg_string}"
               f" -lookin {' '.join(self.infiles)}"
               f" -outdir {self.c_dict['OUTPUT_DIR']}")
        return cmd
