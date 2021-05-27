'''
Program Name: tcmpr_plotter_wrapper.py
Contact(s): George McCabe
'''

import os
import shutil

from ..util import met_util as util
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

        # check if R is available, do not attempt to run if it is not
        if shutil.which('Rscript') is None:
            self.log_error('Rscript must be in the path')

        self.met_install_dir = self.config.getdir('MET_INSTALL_DIR')
        self.tcmpr_script = os.path.join(self.met_install_dir,
                                         'share', 'met', 'Rscripts',
                                         'plot_tcmpr.R')

        self.logger.info(f"plot_tcmpr.R script location: {self.tcmpr_script} ")
        if not os.path.exists(self.tcmpr_script):
            self.log_error('plot_tcmpr.R script could be found')

        # The only required argument for plot_tcmpr.R, the name of
        # the tcst file to plot.
        self.input_data = self.config.getdir('TCMPR_PLOTTER_TCMPR_DATA_DIR',
                                             '')
        if not self.input_data:
            self.log_error("TCMPR_PLOTTER_TCMPR_DATA_DIR must be set")

        # Optional arguments
        self.plot_config_file = self.config.getstr('config',
                                                   'TCMPR_PLOTTER_CONFIG_FILE',
                                                   '')
        if not self.plot_config_file:
            self.log_error("TCMPR_PLOTTER_CONFIG_FILE must be set")

        self.output_base_dir = self.config.getdir(
            'TCMPR_PLOTTER_PLOT_OUTPUT_DIR', ''
        )
        if not self.output_base_dir:
            self.log_error("Must set TCMPR_PLOTTER_PLOT_OUTPUT_DIR")

        self.read_args()

    def read_args(self):
        """! Read config variables and add arguments to command """
        prefix = f'{self.app_name.upper()}_'
        for name, data_type in self.ARGUMENTS.items():
            config_name = f'{prefix}{name.upper()}'

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

            # add quotes around value if they are not already there
            if 'quotes' in data_type and value:
                value = f'"{util.remove_quotes(value)}"'

            if value:
                arg_string = f'-{name}'
                # don't add value for boolean
                if data_type != 'bool':
                    arg_string = f'{arg_string} {value}'

                self.args.append(f'{arg_string}')

    def set_environment_variables(self):
        """!Set environment variables that are needed to run """
        self.add_env_var('MET_INSTALL_DIR', self.met_install_dir)
        super().set_environment_variables()

    def run_all_times(self):
        """! Builds the command for invoking tcmpr.R plot script. """

        self.logger.debug(f'Input: {self.input_data}')
        self.logger.debug(f'Config File: {self.plot_config_file}')
        self.logger.debug(f'Output Directory: {self.output_base_dir}')

        self.args.append(f'-lookin {self.get_input_files()}')
        self.args.append(f'-outdir {self.output_base_dir}')

        # Create the TCMPR output directory, where the plots will be written
        if not os.path.exists(self.output_base_dir):
            self.logger.debug(f'Creating directory: {self.output_base_dir}')
            os.makedirs(self.output_base_dir)

        self.set_environment_variables()
        self.build()

        self.logger.info("Plotting complete")
        return self.all_commands

    def get_input_files(self):
        """! Get input file paths. If input is a directory, find all .tcst
        files inside the directory.

            @returns string with file paths separated by a space
        """
        # If input data is a file, create a single command and invoke R script.
        if os.path.isfile(self.input_data):
            self.logger.debug(f'Plotting file: {self.input_data}')
            return self.input_data

        # input is directory, so find all tcst files to process
        self.logger.debug(f'Plotting all files in: {self.input_data}')
        tcst_files = util.get_files(self.input_data, ".*.tcst")
        self.logger.debug(f"Number of files: {len(tcst_files)}")
        return ' '.join(tcst_files)

    def get_command(self):
        """! Over-ride CommandBuilder's get_command because unlike
             other MET tools, tcmpr_plotter_wrapper handles input
             files differently because it wraps an R-script, plot_tcmpr.R
             rather than a typical MET tool. Build command to run from
             arguments"""
        cmd = f"Rscript {self.tcmpr_script} {' '.join(self.args)}"
        return cmd
