"""
Program Name: PB2NC_Wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET tool PB2NC
History Log:  Initial version
Usage: pb2nc_wrapper.py
Parameters: None
Input Files: prepBUFR data files
Output Files: netCDF files
Condition codes: 0 for success, 1 for failure
"""

import os
import re

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import CommandBuilder

class PB2NCWrapper(CommandBuilder):
    """! Wrapper to the MET tool pb2nc which converts prepbufr files
         to NetCDF for MET's point_stat tool can recognize.
    """

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'pb2nc'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        """! Create a data structure (dictionary) that contains all the
        values set in the configuration files

             Args:

             Returns:
                c_dict  - a dictionary containing the settings in the
                configuration files (that aren't in the
                           metplus_data, metplus_system, and metplus_runtime
                           config files.
        """
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getint('config', 'LOG_PB2NC_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['OFFSETS'] = util.getlistint(self.config.getstr('config', 'PB2NC_OFFSETS', '0'))

        # Directories
        # these are optional because users can specify full file path in template instead
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('PB2NC_INPUT_DIR', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('PB2NC_OUTPUT_DIR', '')

        # filename templates, exit if not set
        c_dict['OBS_INPUT_TEMPLATE'] = self.config.getraw('filename_templates', 'PB2NC_INPUT_TEMPLATE')
        if c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.log_error('Must set PB2NC_INPUT_TEMPLATE in config file')
            exit(1)

        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates', 'PB2NC_OUTPUT_TEMPLATE')
        if c_dict['OUTPUT_TEMPLATE'] == '':
            self.log_error('Must set PB2NC_OUTPUT_TEMPLATE in config file')
            exit(1)

        c_dict['OBS_INPUT_DATATYPE'] = self.config.getstr('config', 'PB2NC_INPUT_DATATYPE', '')

        # Configuration
        c_dict['CONFIG_FILE'] = self.config.getraw('config',
                                                   'PB2NC_CONFIG_FILE',
                                                   '')
        if c_dict['CONFIG_FILE'] == '':
            self.log_error('PB2NC_CONFIG_FILE is required')
            self.isOK = False

        c_dict['MESSAGE_TYPE'] = util.getlist(
            self.config.getstr('config', 'PB2NC_MESSAGE_TYPE', '[]'))

        tmp_message_type = str(c_dict['MESSAGE_TYPE']).replace("\'", "\"")
        c_dict['MESSAGE_TYPE'] = ''.join(tmp_message_type)

        c_dict['STATION_ID'] = util.getlist(
            self.config.getstr('config', 'PB2NC_STATION_ID', '[]'))
        tmp_message_type = str(c_dict['STATION_ID']).replace("\'", "\"")
        c_dict['STATION_ID'] = ''.join(tmp_message_type.split())

        grid_id = self.config.getstr('config', 'PB2NC_GRID')
        c_dict['GRID'] = self.reformat_grid_id(grid_id)
        if c_dict['GRID'] is None:
            self.log_error('PB2NC_GRID value was formatted incorrectly')
            self.isOK = False

        c_dict['POLY'] = self.config.getstr('config', 'PB2NC_POLY')

        c_dict['BUFR_VAR_LIST'] = util.getlist(
            self.config.getstr('config', 'PB2NC_OBS_BUFR_VAR_LIST', '[]'))

        c_dict['TIME_SUMMARY_FLAG'] = \
          'TRUE' if self.config.getbool('config', 'PB2NC_TIME_SUMMARY_FLAG') \
          else 'FALSE'
        c_dict['TIME_SUMMARY_BEG'] = \
          f"\"{self.config.getstr('config', 'PB2NC_TIME_SUMMARY_BEG')}\""
        c_dict['TIME_SUMMARY_END'] = \
          f"\"{self.config.getstr('config', 'PB2NC_TIME_SUMMARY_END')}\""

        var_names = str(util.getlist(self.config.getstr('config',
                                                        'PB2NC_TIME_SUMMARY_VAR_NAMES')))
        c_dict['TIME_SUMMARY_VAR_NAMES'] = var_names.replace("\'", "\"")

        time_types = str(util.getlist(self.config.getstr('config',
                                                         'PB2NC_TIME_SUMMARY_TYPES')))
        c_dict['TIME_SUMMARY_TYPES'] = time_types.replace("\'", "\"")

        c_dict['OBS_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'PB2NC_WINDOW_BEGIN',
                             self.config.getseconds('config',
                                                'OBS_WINDOW_BEGIN', 0))
        c_dict['OBS_WINDOW_END'] = \
          self.config.getseconds('config', 'PB2NC_WINDOW_END',
                             self.config.getseconds('config',
                                                'OBS_WINDOW_END', 0))

        c_dict['OBS_FILE_WINDOW_BEGIN'] = \
          self.config.getseconds('config', 'PB2NC_FILE_WINDOW_BEGIN',
                             self.config.getseconds('config',
                                                'OBS_FILE_WINDOW_BEGIN', 0))
        c_dict['OBS_FILE_WINDOW_END'] = \
          self.config.getseconds('config', 'PB2NC_FILE_WINDOW_END',
                             self.config.getseconds('config',
                                                'OBS_FILE_WINDOW_END', 0))

        c_dict['VALID_BEGIN_TEMPLATE'] = \
          self.config.getraw('config', 'PB2NC_VALID_BEGIN', '')

        c_dict['VALID_END_TEMPLATE'] = \
          self.config.getraw('config', 'PB2NC_VALID_END', '')

        c_dict['VALID_WINDOW_BEGIN'] = ''
        c_dict['VALID_WINDOW_END'] = ''

        c_dict['ALLOW_MULTIPLE_FILES'] = True

        return c_dict


    def reformat_grid_id(self, grid_id):
        """!Reformat the grid id (MASK_GRID value in the configuration
            file) if it starts with G. Looks for G<n> where n is a 
            digit 0-999 and zero pads the value. i.e. G7 becomes G007,
            G13 becomes G013, etc.
            Args:
                @param grid_id identifier of grid
            Returns:
                @return reformatted grid id if valid, None if not
        """
        # If grid ID does not start with G, return it
        if not grid_id.startswith('G'):
            return grid_id

        # look for G<n> where n is a digit 0-999
        match = re.match(r'G([0-9]{1,3})$', grid_id)

        # pad with zeros if found
        if match:
            number = match.group(1)
            return 'G' + number.zfill(3)

        # Unexpected format
        self.log_error('Grid id in unexpected format of Gn or ' +
                          'Gnn, please check again. Exiting...')
        return None

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""
        # set environment variables needed for MET application
        self.add_env_var("PB2NC_MESSAGE_TYPE", self.c_dict['MESSAGE_TYPE'])
        self.add_env_var("PB2NC_STATION_ID", self.c_dict['STATION_ID'])
        self.add_env_var("OBS_WINDOW_BEGIN", str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var("OBS_WINDOW_END", str(self.c_dict['OBS_WINDOW_END']))
        self.add_env_var("PB2NC_GRID", self.c_dict['GRID'])
        self.add_env_var("PB2NC_POLY", self.c_dict['POLY'])

        tmp_message_type = str(self.c_dict['BUFR_VAR_LIST']).replace("\'", "\"")
        bufr_var_list = ''.join(tmp_message_type.split())
        self.add_env_var("OBS_BUFR_VAR_LIST", bufr_var_list)

        self.add_env_var('TIME_SUMMARY_FLAG',
                         self.c_dict['TIME_SUMMARY_FLAG'])
        self.add_env_var('TIME_SUMMARY_BEG',
                         self.c_dict['TIME_SUMMARY_BEG'])
        self.add_env_var('TIME_SUMMARY_END',
                         self.c_dict['TIME_SUMMARY_END'])
        self.add_env_var('TIME_SUMMARY_VAR_NAMES',
                         self.c_dict['TIME_SUMMARY_VAR_NAMES'])
        self.add_env_var('TIME_SUMMARY_TYPES',
                         self.c_dict['TIME_SUMMARY_TYPES'])

        super().set_environment_variables(time_info)

    def find_input_files(self, input_dict):
        """!Find prepbufr data to convert. If file(s) are found, return timing information
            dictionary containing offset information of input file. Return None otherwise"""

        infiles, time_info = self.find_obs_offset(input_dict,
                                                  None,
                                                  mandatory=True,
                                                  return_list=True)

        # if file is found, return timing info dict so output template can use offset value
        if infiles is None:
            return None

        self.logger.debug(f"Adding input: {' and '.join(infiles)}")
        self.infiles.extend(infiles)
        return time_info

    def set_valid_window_variables(self, time_info):
        begin_template = self.c_dict['VALID_BEGIN_TEMPLATE']
        end_template = self.c_dict['VALID_END_TEMPLATE']

        if begin_template:
            self.c_dict['VALID_WINDOW_BEGIN'] = \
                do_string_sub(begin_template,
                              **time_info)

        if end_template:
            self.c_dict['VALID_WINDOW_END'] = \
                do_string_sub(end_template,
                              **time_info)


    def run_at_time(self, input_dict):
        """! Loop over each forecast lead and build pb2nc command """
         # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            lead_string = time_util.ti_calculate(input_dict)['lead_string']
            self.logger.info("Processing forecast lead {}".format(lead_string))

            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                input_dict['custom'] = custom_string

                # Run for given init/valid time and forecast lead combination
                self.run_at_time_once(input_dict)


    def run_at_time_once(self, input_dict):
        """!Find files needed to run pb2nc and run if found"""
        # clear out information set from previous run
        self.clear()

        # look for input files to process
        time_info = self.find_input_files(input_dict)

        # if no files were found, don't run pb2nc
        if time_info is None:
            return

        if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
            self.logger.debug('Skipping run time')
            return

        # look for output file path and skip running pb2nc if necessary
        if not self.find_and_check_output_file(time_info):
            return

        # set environment variables to be passed to MET config file
        self.set_environment_variables(time_info)

        self.set_valid_window_variables(time_info)

        # handle config file substitution
        self.c_dict['CONFIG_FILE'] = do_string_sub(self.c_dict['CONFIG_FILE'],
                                                   **time_info)

        # build command and run if successful
        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return
        self.build()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.log_error('No app path specified. You must use a subclass')
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            self.log_error("No input filenames specified")
            return None

        # if multiple input files, add first now, then add rest with
        # -pbfile argument
        cmd += self.infiles[0] + " "

        if self.outfile == "":
            self.log_error("No output filename specified")
            return None

        if self.outdir == "":
            self.log_error("No output directory specified")
            return None

        out_path = os.path.join(self.outdir, self.outfile)

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        cmd += out_path + ' '

        cmd += self.c_dict['CONFIG_FILE'] + ' '

        if len(self.infiles) > 1:
            for f in self.infiles[1:]:
                cmd += '-pbfile ' + f + ' '

        if self.c_dict['VALID_WINDOW_BEGIN']:
            cmd += f"-valid_beg {self.c_dict['VALID_WINDOW_BEGIN']} "

        if self.c_dict['VALID_WINDOW_END']:
            cmd += f"-valid_end {self.c_dict['VALID_WINDOW_END']} "

        return cmd.strip()
