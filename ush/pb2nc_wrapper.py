#!/usr/bin/env python

from __future__ import print_function, unicode_literals
import sys
import os
import re
import time
import calendar
from collections import namedtuple
import config_metplus
import met_util as util
import time_util
from command_builder import CommandBuilder
import produtil.setup
import datetime
from string_template_substitution import StringSub
from reformat_gridded_wrapper import ReformatGriddedWrapper

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

    def __init__(self, p, logger):
        super(PB2NCWrapper, self).__init__(p, logger)
        met_install_dir = util.getdir(p, 'MET_INSTALL_DIR', None, logger)
        self.app_path = os.path.join(met_install_dir, 'bin/pb2nc')
        self.app_name = os.path.basename(self.app_path)

        self.c_dict = self.create_c_dict()


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
        c_dict = dict()
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = self.p.getbool('config', 'PB2NC_SKIP_IF_OUTPUT_EXISTS', True)
        c_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))
        c_dict['OFFSETS'] = util.getlistint(self.p.getstr('config', 'PB2NC_OFFSETS', '0'))

        # Directories
        c_dict['APP_PATH'] = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                           'bin/pb2nc')
        c_dict['APP_NAME'] = os.path.basename(c_dict['APP_PATH'])

        c_dict['OBS_INPUT_DIR'] = self.p.getdir('PB2NC_INPUT_DIR')
        c_dict['OUTPUT_DIR'] = self.p.getdir('PB2NC_OUTPUT_DIR')

        c_dict['OBS_INPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates', 'PB2NC_INPUT_TEMPLATE')
        c_dict['OUTPUT_TEMPLATE'] = util.getraw_interp(self.p, 'filename_templates', 'PB2NC_OUTPUT_TEMPLATE')
        c_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config', 'PB2NC_EXACT_VALID_TIME', True)
        c_dict['OBS_INPUT_DATATYPE'] = self.p.getstr('config', 'PB2NC_INPUT_DATATYPE', '')

        # Configuration
        c_dict['CONFIG_FILE'] = self.p.getstr('config',
                                                     'PB2NC_CONFIG_FILE')
        c_dict['MESSAGE_TYPE'] = util.getlist(
            self.p.getstr('config', 'PB2NC_MESSAGE_TYPE', '[]'))

        tmp_message_type = str(c_dict['MESSAGE_TYPE']).replace("\'", "\"")
        c_dict['MESSAGE_TYPE'] = ''.join(tmp_message_type)

        c_dict['STATION_ID'] = util.getlist(
            self.p.getstr('config', 'PB2NC_STATION_ID', '[]'))
        tmp_message_type = str(c_dict['STATION_ID']).replace("\'", "\"")
        c_dict['STATION_ID'] = ''.join(tmp_message_type.split())

        grid_id = self.p.getstr('config', 'PB2NC_GRID')
        if grid_id.startswith('G'):
            # Reformat grid ids that begin with 'G' ( G10, G1, etc.) to format
            # Gnnn
            c_dict['GRID'] = self.reformat_grid_id(grid_id)
        else:
            c_dict['GRID'] = grid_id

        c_dict['POLY'] = self.p.getstr('config', 'PB2NC_POLY')

        c_dict['BUFR_VAR_LIST'] = util.getlist(
            self.p.getstr('config', 'PB2NC_OBS_BUFR_VAR_LIST', '[]'))
        tmp_message_type = str(c_dict['BUFR_VAR_LIST']).replace("\'", "\"")
        c_dict['BUFR_VAR_LIST'] = ''.join(tmp_message_type.split())

        c_dict['TIME_SUMMARY_FLAG'] = self.p.getbool('config',
                                                      'PB2NC_TIME_SUMMARY_FLAG')
        c_dict['TIME_SUMMARY_BEG'] = self.p.getstr('config',
                                                    'PB2NC_TIME_SUMMARY_BEG')
        c_dict['TIME_SUMMARY_END'] = self.p.getstr('config',
                                                    'PB2NC_TIME_SUMMARY_END')
        c_dict['TIME_SUMMARY_VAR_NAMES'] = util.getlist(
            self.p.getstr('conf', 'PB2NC_TIME_SUMMARY_VAR_NAMES'))
        c_dict['TIME_SUMMARY_TYPES'] = util.getlist(
            self.p.getstr('config', 'PB2NC_TIME_SUMMARY_TYPES'))
        c_dict['OBS_WINDOW_BEGIN'] = self.p.getstr('config',
                                                    'OBS_WINDOW_BEGIN')
        c_dict['OBS_WINDOW_END'] = self.p.getstr('config', 'OBS_WINDOW_END')

        c_dict['VERTICAL_LOCATION'] = self.p.getstr('config',
                                                     'PB2NC_VERTICAL_LOCATION')

        return c_dict


    def reformat_grid_id(self, grid_id):
        """!Reformat the grid id (MASK_GRID value in the configuration
            file.)

            Args:
                @param grid_id      - the grid_id of the grid to use in
                                      regridding

            Returns:
                reformatted_id - the grid id reformatted based on
                the numerical
                                value portion of the grid id defined
                                in the
                                configuration file (MASK_GRID)
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and
        # method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Do reformatting
        match = re.match(r'G([0-9]{1,3})', grid_id)
        if match:
            number = match.group(1)
            reformatted_id = 'G' + number.zfill(3)
        else:
            # Unexpected format
            self.logger.error('Grid id in unexpected format of Gn or ' +
                'Gnn, please check again. Exiting...')
            sys.exit(1)

        return reformatted_id

    def run_at_time(self, input_dict):
        """! Stub, not yet implemented """
        # loop of forecast leads and process each
        lead_seq = self.c_dict['LEAD_SEQ']
        for lead in lead_seq:
            input_dict['lead_hours'] = lead

            self.logger.info("Processing forecast lead {}".format(lead))

            # set current lead time config and environment variables
            self.p.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(input_dict)


    def run_at_time_once(self, input_dict):
        self.clear()
        if self.c_dict['OBS_INPUT_DIR'] == '':
            self.logger.error('Must set PB2NC_INPUT_DIR in config file')
            exit(1)

        if self.c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set PB2NC_INPUT_TEMPLATE in config file')
            exit(1)

        if self.c_dict['OUTPUT_DIR'] == '':
            self.logger.error('Must set PB2NC_OUTPUT_DIR in config file')
            exit(1)

        if self.c_dict['OUTPUT_TEMPLATE'] == '':
            self.logger.error('Must set PB2NC_OUTPUT_TEMPLATE in config file')
            exit(1)

        input_dir = self.c_dict['OBS_INPUT_DIR']
        input_template = self.c_dict['OBS_INPUT_TEMPLATE']
        output_dir = self.c_dict['OUTPUT_DIR']
        output_template = self.c_dict['OUTPUT_TEMPLATE']

        infile = None
        # loop over offset list and find first file that matches
        for offset in self.c_dict['OFFSETS']:
            input_dict['offset'] = offset
            time_info = time_util.ti_calculate(input_dict)
            infile = self.find_obs(time_info, None)

            if infile is not None:
                self.add_input_file(infile)
                self.logger.debug('Adding input file {}'.format(infile))
                break

        if infile is None:
            self.logger.error('Could not find input file in {} matching template {}'
                              .format(input_dir, input_template))
            return False

        outSts = StringSub(self.logger,
                           output_template,
                           **time_info)
        outfile = outSts.doStringSub()
        outfile = os.path.join(output_dir, outfile)
        self.set_output_path(outfile)

        # if we don't overwrite and the output file exists, warn and continue
        if os.path.exists(outfile) and \
          (self.c_dict['SKIP_IF_OUTPUT_EXISTS'] is True or
           self.c_dict['OVERWRITE_NC_OUTPUT'] is False):
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'OVERWRITE_NC_OUTPUT to True to process'
                              .format(outfile))
            return True

        # set config file since command is reset after each run
        self.set_param_file(self.c_dict['CONFIG_FILE'])

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
        self.add_env_var("OBS_WINDOW_BEGIN", self.c_dict['OBS_WINDOW_BEGIN'])
        self.add_env_var("OBS_WINDOW_END", self.c_dict['OBS_WINDOW_END'])
        self.add_env_var("PB2NC_GRID", self.c_dict['GRID'])
        self.add_env_var("PB2NC_POLY", self.c_dict['POLY'])
        self.add_env_var("OBS_BUFR_VAR_LIST", self.c_dict['BUFR_VAR_LIST'])
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

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return
        self.build()


if __name__ == "__main__":
        util.run_stand_alone("pb2nc_wrapper", "PB2NC")
