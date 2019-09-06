#!/usr/bin/env python

from __future__ import print_function, unicode_literals
import sys
import os
import re
import met_util as util
import time_util
from command_builder import CommandBuilder
from string_template_substitution import StringSub

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


class PB2NCWrapper(CommandBuilder):
    """! Wrapper to the MET tool pb2nc which converts prepbufr files
         to NetCDF for MET's point_stat tool can recognize.
    """

    def __init__(self, config, logger):
        super(PB2NCWrapper, self).__init__(config, logger)
        self.app_name = 'pb2nc'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

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
        c_dict = super(PB2NCWrapper, self).create_c_dict()
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = self.config.getbool('config', 'PB2NC_SKIP_IF_OUTPUT_EXISTS', False)
        c_dict['OFFSETS'] = util.getlistint(self.config.getstr('config', 'PB2NC_OFFSETS', '0'))

        # Directories
        # these are optional because users can specify full file path in template instead
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('PB2NC_INPUT_DIR', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('PB2NC_OUTPUT_DIR', '')

        # filename templates, exit if not set
        c_dict['OBS_INPUT_TEMPLATE'] = self.config.getraw('filename_templates', 'PB2NC_INPUT_TEMPLATE')
        if c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set PB2NC_INPUT_TEMPLATE in config file')
            exit(1)

        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates', 'PB2NC_OUTPUT_TEMPLATE')
        if c_dict['OUTPUT_TEMPLATE'] == '':
            self.logger.error('Must set PB2NC_OUTPUT_TEMPLATE in config file')
            exit(1)

        c_dict['OBS_INPUT_DATATYPE'] = self.config.getstr('config', 'PB2NC_INPUT_DATATYPE', '')

        # Configuration
        c_dict['CONFIG_FILE'] = self.config.getstr('config',
                                                   'PB2NC_CONFIG_FILE')
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

        c_dict['POLY'] = self.config.getstr('config', 'PB2NC_POLY')

        c_dict['BUFR_VAR_LIST'] = util.getlist(
            self.config.getstr('config', 'PB2NC_OBS_BUFR_VAR_LIST', '[]'))

        c_dict['TIME_SUMMARY_FLAG'] = self.config.getbool('config',
                                                      'PB2NC_TIME_SUMMARY_FLAG')
        c_dict['TIME_SUMMARY_BEG'] = self.config.getstr('config',
                                                    'PB2NC_TIME_SUMMARY_BEG')
        c_dict['TIME_SUMMARY_END'] = self.config.getstr('config',
                                                    'PB2NC_TIME_SUMMARY_END')
        c_dict['TIME_SUMMARY_VAR_NAMES'] = util.getlist(
            self.config.getstr('config', 'PB2NC_TIME_SUMMARY_VAR_NAMES'))
        c_dict['TIME_SUMMARY_TYPES'] = util.getlist(
            self.config.getstr('config', 'PB2NC_TIME_SUMMARY_TYPES'))

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
        self.logger.error('Grid id in unexpected format of Gn or ' +
                          'Gnn, please check again. Exiting...')

    def set_environment_variables(self, time_info):
        """!Set environment variables that will be read by the MET config file.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""
        # list of fields to print to log
        print_list = ["PB2NC_MESSAGE_TYPE", "PB2NC_STATION_ID",
                      "OBS_WINDOW_BEGIN", "OBS_WINDOW_END",
                      "PB2NC_GRID", "PB2NC_POLY", "OBS_BUFR_VAR_LIST",
                      "TIME_SUMMARY_FLAG", "TIME_SUMMARY_BEG",
                      "TIME_SUMMARY_END", "TIME_SUMMARY_VAR_NAMES",
                      "TIME_SUMMARY_TYPES" ]

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
                         str(self.c_dict['TIME_SUMMARY_FLAG']))
        self.add_env_var('TIME_SUMMARY_BEG',
                         self.c_dict['TIME_SUMMARY_BEG'])
        self.add_env_var('TIME_SUMMARY_END',
                         self.c_dict['TIME_SUMMARY_END'])
        self.add_env_var('TIME_SUMMARY_VAR_NAMES',
                         str(self.c_dict['TIME_SUMMARY_VAR_NAMES']))
        self.add_env_var('TIME_SUMMARY_TYPES',
                         str(self.c_dict['TIME_SUMMARY_TYPES']))

        # set user environment variables
        self.set_user_environment(time_info)

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

    def find_input_files(self, input_dict):
        """!Find prepbufr data to convert. If file(s) are found, return timing information
            dictionary containing offset information of input file. Return None otherwise"""
        infile = None

        # loop over offset list and find first file that matches
        for offset in self.c_dict['OFFSETS']:
            input_dict['offset_hours'] = offset
            time_info = time_util.ti_calculate(input_dict)
            infile = self.find_obs(time_info, None, False)

            if infile is not None:
                if isinstance(infile, list):
                    self.infiles.extend(f)
                else:
                    self.infiles.append(infile)
                self.logger.debug('Adding input file {}'.format(infile))
                break

        # if file is found, return timing info dict so output template can use offset value
        if infile is not None:
            return time_info

        self.logger.error('Could not find input file in {} matching template {} using offsets {}'
                          .format(self.c_dict['OBS_INPUT_DIR'],
                                  self.c_dict['OBS_INPUT_TEMPLATE'],
                                  self.c_dict['OFFSETS']))

    def find_and_check_output_file(self, time_info):
        """!Look for expected output file. If it exists and configured to skip if it does, then return False"""
        outfile = StringSub(self.logger,
                            self.c_dict['OUTPUT_TEMPLATE'],
                            **time_info).do_string_sub()
        outpath = os.path.join(self.c_dict['OUTPUT_DIR'], outfile)
        self.set_output_path(outpath)

        if not os.path.exists(outpath) or not self.c_dict['SKIP_IF_OUTPUT_EXISTS']:
            return True

        # if the output file exists and we are supposed to skip, don't run pb2nc
        self.logger.debug('Skip writing output file {} because it already '
                          'exists. Remove file or change '
                          'PB2NC_SKIP_IF_OUTPUT_EXISTS to False to process'
                          .format(outpath))
        
    def run_at_time(self, input_dict):
        """! Loop over each forecast lead and build pb2nc command """
        if self.c_dict['GRID'] is None:
            self.logger.error('PB2NC_GRID value was formatted incorrectly')
            return

        # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            lead_string = time_util.ti_calculate(input_dict)['lead_string']
            self.logger.info("Processing forecast lead {}".format(lead_string))

            # set current lead time config and environment variables
            self.config.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)

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

        # look for output file path and skip running pb2nc if necessary
        if not self.find_and_check_output_file(time_info):
            return

        # set environment variables to be passed to MET config file
        self.set_environment_variables(time_info)

        # build command and run if successful
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return
        self.build()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.logger.error('No app path specified. You must use a subclass')
            return None

        cmd = '{} -v {} '.format(self.app_path, self.verbose)

        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            self.logger.error("No input filenames specified")
            return None

        # if multiple input files, add first now, then add rest with
        # -pbfile argument
        cmd += self.infiles[0] + " "

        if self.outfile == "":
            self.logger.error("No output filename specified")
            return None

        if self.outdir == "":
            self.logger.error("No output directory specified")
            return None

        out_path = os.path.join(self.outdir, self.outfile)

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        cmd += " " + out_path

        if self.c_dict['CONFIG_FILE'] != "":
            cmd += ' ' + self.c_dict['CONFIG_FILE']

        if len(self.infiles) > 1:
            for f in self.infiles[1:]:
                cmd += ' -pbfile' + f

        return cmd

if __name__ == "__main__":
        util.run_stand_alone("pb2nc_wrapper", "PB2NC")
