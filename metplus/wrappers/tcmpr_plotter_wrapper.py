'''
Program Name: tcmpr_plotter_wrapper.py
Contact(s): George McCabe
'''

import os
import shutil

from ..util import getlist
from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from ..util import time_generator
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
        'prefix': 'string/quotes',
        'title': 'string/quotes',
        'subtitle': 'string/quotes',
        'xlab': 'string/quotes',
        'ylab': 'string/quotes',
        'xlim': 'string',
        'ylim': 'string',
        'filter': 'string/quotes',
        'tcst': 'string',
        'dep': 'list/loop',
        'scatter_x': 'string',
        'scatter_y': 'string',
        'skill_ref': 'string',
        'series': 'string',
        'series_ci': 'string',
        'legend': 'string/quotes',
        'lead': 'string',
        'plot': 'list/loop',
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

    def __init__(self, config, instance=None):
        self.app_name = 'tcmpr_plotter'

        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # check if R is available, do not attempt to run if it is not
        if shutil.which('Rscript') is None:
            self.logger.error('Rscript must be in the path')

            # if running script, set isOK to False
            # this allows tests to run without needing Rscript
            if not c_dict.get('DO_NOT_RUN_EXE', False):
                self.isOK = False

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
        input_dict = next(time_generator(self.config))
        if not input_dict:
            self.isOK = False
        c_dict['TIME_INFO'] = time_util.ti_calculate(input_dict)

        # read all optional command line arguments
        c_dict['COMMAND_ARGS'] = self.read_optional_args()
        c_dict['LOOP_INFO'] = self.read_loop_info()
        c_dict['LOOP_ARGS'] = {}

        # get option to pass input directory instead of finding .tcst files
        c_dict['READ_ALL_FILES'] = (
            self.config.getbool('config', 'TCMPR_PLOTTER_READ_ALL_FILES', False)
        )

        return c_dict

    def read_optional_args(self):
        """! Read config variables and add arguments to command """
        prefix = f'{self.app_name.upper()}_'
        command_args = {}

        for name, data_type in self.ARGUMENTS.items():
            config_name = f'{prefix}{name.upper()}'

            # skip required arguments because they are handled elsewhere
            if name == 'config' or name == 'lookin' or name == 'outdir':
                continue

            # skip list arguments that will be looped over
            if name == 'plot' or name == 'dep':
                continue

            # handle config name exceptions that differ from argument name
            if name == 'tcst':
                config_name = f'{prefix}FILTERED_TCST_DATA_FILE'
            elif name == 'plot_config':
                config_name = f'{config_name}_OPTS'

            if 'string' in data_type:
                value = self.config.getraw('config', config_name, '')
            elif 'bool' in data_type:
                value = self.config.getbool('config', config_name, '')
            elif 'list' in data_type:
                value = getlist(self.config.getraw('config', config_name))
            else:
                self.log_error(f"Invalid type for {name}: {data_type}")

            if value:
                # add quotes around value if they are not already there
                if 'quotes' in data_type:
                    value = f'"{util.remove_quotes(value)}"'

                # don't add value for boolean
                if data_type == 'bool':
                    value = ''

                self.logger.debug(f"Adding argument: -{name} {value}")
                command_args[name] = value

        return command_args

    def read_loop_info(self):
        prefix = f'{self.app_name.upper()}_'
        loop_args = {}

        loop_keys = [key for key, value in self.ARGUMENTS.items()
                     if 'loop' in value]

        for name in loop_keys:
            config_name = f'{prefix}{name.upper()}'
            label_config_name = f'{config_name}_LABELS'
            if name == 'plot':
                config_name = f'{config_name}_TYPES'
            elif name == 'dep':
                config_name = f'{config_name}_VARS'

            values = getlist(self.config.getraw('config', config_name))
            labels = getlist(self.config.getraw('config', label_config_name))

            # if labels are not set, use values as labels
            if not labels:
                labels = values

            if len(values) != len(labels):
                self.log_error("Lists must have the same length: "
                               f"{config_name} ({values}) and "
                               f"{label_config_name} ({labels})")
                return None

            loop_args[name] = []
            for arg_value, label_value in zip(values, labels):
                loop_args[name].append((arg_value, label_value))

            # if no values were added to list, add a tuple of 2 empty strings
            if not loop_args[name]:
                loop_args[name].append(('', ''))

        return loop_args

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

        # loop over each loop argument (dep and plot) and run command for each
        self.loop_over_args_and_run()

        self.logger.info("Plotting complete")
        return self.all_commands

    def loop_over_args_and_run(self):
        for dep, dep_label in self.c_dict['LOOP_INFO']['dep']:
            # set values in dictionary for string substitution
            self.c_dict['TIME_INFO']['dep'] = dep
            self.c_dict['TIME_INFO']['dep_label'] = dep_label

            for plot, plot_label in self.c_dict['LOOP_INFO']['plot']:
                self.c_dict['TIME_INFO']['plot'] = plot
                self.c_dict['TIME_INFO']['plot_label'] = plot_label

                # clear loop args and add arguments if they are set
                self.c_dict['LOOP_ARGS'].clear()
                if dep:
                    self.c_dict['LOOP_ARGS']['dep'] = dep

                if plot:
                    self.c_dict['LOOP_ARGS']['plot'] = plot

                # build and run the command
                self.build()

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
        if self.c_dict['READ_ALL_FILES']:
            self.logger.debug('Passing in directory to R script')
            return [input_data]

        input_files = util.get_files(input_data, ".*.tcst")
        self.logger.debug(f"Number of files: {len(input_files)}")
        return input_files

    def format_arg_string(self):
        arg_list = []

        arg_dict = self.c_dict['COMMAND_ARGS']
        loop_dict = self.c_dict['LOOP_ARGS']

        # handle all optional args - use ARGUMENTS to preserve order
        for name in self.ARGUMENTS:
            if name in arg_dict:
                # add dash before argument name
                next_arg = f'-{name}'
                # add value of argument if set (not set for boolean)
                value = arg_dict[name]
                if value:
                    # perform string substitution to get value for items
                    # that should change spaces to underscores
                    value = do_string_sub(value, **self.c_dict['TIME_INFO'])

                    # if prefix, change spaces to underscore for filename
                    if name == 'prefix':
                        value = value.replace(' ', '_')

                    next_arg = f'{next_arg} {value}'

                arg_list.append(next_arg)

        # handle loop args (dep and plot)
        for name, value in loop_dict.items():
            next_arg = f'-{name} {value}'
            arg_list.append(next_arg)

        # return empty string if no args were set to
        # prevent adding extra space between args before and after
        if not arg_list:
            return ''

        # return list separated by space with an extra space at the beginning
        return f" {' '.join(arg_list)}"

    def get_command(self):
        """! Builds the command to run the R script
           @rtype string
           @return Returns a command with arguments that can be run
        """
        # get arguments
        arg_string = self.format_arg_string()

        cmd = (f"Rscript {self.c_dict['TCMPR_SCRIPT']}"
               f" -config {self.c_dict['CONFIG_FILE']}"
               f"{arg_string}"
               f" -lookin {' '.join(self.infiles)}"
               f" -outdir {self.c_dict['OUTPUT_DIR']}")

        # run entire command through string substitution
        cmd = do_string_sub(cmd, **self.c_dict['TIME_INFO'])
        return cmd
