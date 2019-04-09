#!/usr/bin/env python

from __future__ import print_function
import os
import calendar
import time
import re
import sys
from collections import namedtuple
from collections import OrderedDict
import itertools
import copy
import pdb
import datetime

import config_metplus
import met_util as util
import time_util
import grid_to_obs_util as g2o_util
import produtil.setup
from compare_gridded_wrapper import CompareGriddedWrapper
from string_template_substitution import StringSub


"""
Program Name: point_stat_wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET point_stat
History Log:  Initial version
Usage: point_stat_wrapper.py
Parameters: None
Input Files: netCDF data files
Output Files: ascii files
Condition codes: 0 for success, 1 for failure

"""


class PointStatWrapper(CompareGriddedWrapper):
    """! Wrapper to the MET tool, Point-Stat."""

    def __init__(self, p, logger):
        super(PointStatWrapper, self).__init__(p, logger)
        met_install_dir = util.getdir(p, 'MET_INSTALL_DIR', None, logger)
        self.app_path = os.path.join(met_install_dir, 'bin/point_stat')
        self.app_name = os.path.basename(self.app_path)

        self.c_dict = self.create_point_stat_dict()


    def create_point_stat_dict(self):
        """! Create a dictionary that holds all the values set in the
             METplus config file for the point-stat wrapper.

             Args:
                 None
             Returns:
                 c_dict   - A dictionary containing the key-value pairs set
                             in the METplus configuration file.
        """
        c_dict = super(PointStatWrapper, self).create_c_dict()
        # TODO: These are all required by CompareGridded, put into function?
        # pass in all caps MET app name, i.e. POINT_STAT or PB2NC
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['OFFSETS'] = util.getlistint(self.p.getstr('config', 'POINT_STAT_OFFSETS', '0'))
        c_dict['FCST_INPUT_TEMPLATE'] = \
            util.getraw_interp(self.p, 'filename_templates',
                               'FCST_POINT_STAT_INPUT_TEMPLATE')
        c_dict['OBS_INPUT_TEMPLATE'] = \
            util.getraw_interp(self.p, 'filename_templates',
                               'OBS_POINT_STAT_INPUT_TEMPLATE')

        c_dict['FCST_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'FCST_POINT_STAT_INPUT_DATATYPE', '')
        c_dict['OBS_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'OBS_POINT_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DIR'] = util.getdir(self.p, 'FCST_POINT_STAT_INPUT_DIR')
        c_dict['OBS_INPUT_DIR'] = util.getdir(self.p, 'OBS_POINT_STAT_INPUT_DIR')
        c_dict['OUTPUT_DIR'] = \
            util.getdir(self.p, 'POINT_STAT_OUTPUT_DIR')

        # Configuration
        c_dict['CONFIG_FILE'] = \
            self.p.getstr('config', 'POINT_STAT_CONFIG_FILE')

        c_dict['MODEL_NAME'] = self.p.getstr('config', 'MODEL_NAME')
        c_dict['POINT_STAT_CONFIG_FILE'] = \
            self.p.getstr('config', 'POINT_STAT_CONFIG_FILE')
        c_dict['REGRID_TO_GRID'] = self.p.getstr('config', 'POINT_STAT_REGRID_TO_GRID')
        c_dict['POINT_STAT_GRID'] = self.p.getstr('config', 'POINT_STAT_GRID')

        c_dict['POINT_STAT_POLY'] = util.getlist(
            self.p.getstr('config', 'POINT_STAT_POLY', ''))
        c_dict['POINT_STAT_STATION_ID'] = util.getlist(
            self.p.getstr('config', 'POINT_STAT_STATION_ID', ''))
        c_dict['POINT_STAT_MESSAGE_TYPE'] = util.getlist(
            self.p.getstr('config', 'POINT_STAT_MESSAGE_TYPE', ''))

        c_dict['OBS_WINDOW_BEGIN'] = \
          self.p.getstr('config', 'OBS_POINT_STAT_WINDOW_BEGIN', 0)
        c_dict['OBS_WINDOW_END'] = \
          self.p.getstr('config', 'OBS_POINT_STAT_WINDOW_END', 0)

        c_dict['NEIGHBORHOOD_WIDTH'] = self.p.getstr('config', 'POINT_STAT_NEIGHBORHOOD_WIDTH', '')
        c_dict['NEIGHBORHOOD_SHAPE'] = self.p.getstr('config', 'POINT_STAT_NEIGHBORHOOD_SHAPE', '')
        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            util.getraw_interp(self.p, 'filename_templates',
                               'POINT_STAT_VERIFICATION_MASK_TEMPLATE')
        c_dict['VERIFICATION_MASK'] = ''

        return c_dict


    def run_at_time(self, input_dict):
        """! Stub, not yet implemented """

        # get field variables to compare
        var_list = util.parse_var_list(self.p)

        # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.p, self.logger, input_dict)
        for lead in lead_seq:
            input_dict['lead_hours'] = lead

            self.logger.info("Processing forecast lead {}".format(lead))

            # set current lead time config and environment variables
            self.p.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(input_dict, var_list)


    def run_at_time_once(self, input_dict, var_list):
        if self.c_dict['FCST_INPUT_DIR'] == '':
            self.logger.error('Must set FCST_POINT_STAT_INPUT_DIR in config file')
            exit(1)

        if self.c_dict['FCST_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set FCST_POINT_STAT_INPUT_TEMPLATE in config file')
            exit(1)

        if self.c_dict['OBS_INPUT_DIR'] == '':
            self.logger.error('Must set OBS_POINT_STAT_INPUT_DIR in config file')
            exit(1)

        if self.c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set OBS_POINT_STAT_INPUT_TEMPLATE in config file')
            exit(1)

        if self.c_dict['OUTPUT_DIR'] == '':
            self.logger.error('Must set POINT_STAT_OUTPUT_DIR in config file')
            exit(1)

        # clear any settings leftover from previous run
        self.clear()

        # get model to compare
        time_info = time_util.ti_calculate(input_dict)
        model_path = self.find_model(time_info, var_list[0])
        if model_path == None:
            self.logger.error('Could not find file in {} matching template {}'
                              .format(self.c_dict['FCST_INPUT_DIR'],
                                      self.c_dict['FCST_INPUT_TEMPLATE']))
            self.logger.error("Could not find file in " + self.c_dict['FCST_INPUT_DIR'] +\
                              " for init time " + time_info['init_fmt'] + " f" + str(time_info['lead_hours']))
            return False

        # get observation to compare
        obs_path = None
        # loop over offset list and find first file that matches
        for offset in self.c_dict['OFFSETS']:
            input_dict['offset'] = offset
            time_info = time_util.ti_calculate(input_dict)
            obs_path = self.find_obs(time_info, var_list[0])

            if obs_path is not None:
                break

        if obs_path is None:
            self.logger.error('Could not find observation file in {} '
                              'matching template {}'
                              .format(self.c_dict['OBS_INPUT_DIR'],
                                      self.c_dict['OBS_INPUT_TEMPLATE']))
            return False

        # found both fcst and obs
        self.add_input_file(model_path)
        if type(obs_path) is list:
            for obs in obs_path:
                self.add_input_file(obs)
        else:
            self.add_input_file(obs_path)

        # get field information
        fcst_field_list = []
        obs_field_list = []
        for v in var_list:
            next_fcst = self.get_one_field_info(v.fcst_level, v.fcst_thresh, v.fcst_name, v.fcst_extra, 'FCST')
            next_obs = self.get_one_field_info(v.obs_level, v.obs_thresh, v.obs_name, v.obs_extra, 'OBS')
            fcst_field_list.append(next_fcst)
            obs_field_list.append(next_obs)
        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.process_fields(time_info, fcst_field, obs_field)


    def set_environment_variables(self, a=None, b=None, c=None):
        """! Set all the environment variables in the MET config
             file to the corresponding values in the METplus config file.

             Args:

             Returns: None - invokes parent class, CommandBuilder add_env_var
                             to add each environment variable to run the

        """
        # pylint:disable=protected-access
        # list of fields to print to log
        print_list = ["MODEL_NAME", "REGRID_TO_GRID",
                      "FCST_FIELD", "OBS_FIELD",
                      "OBS_WINDOW_BEGIN", "OBS_WINDOW_END",
                      "POINT_STAT_MESSAGE_TYPE", "POINT_STAT_GRID",
                      "POINT_STAT_POLY","POINT_STAT_STATION_ID"]

        # Set the environment variables
        self.add_env_var(b'MODEL_NAME', str(self.c_dict['MODEL_NAME']))

        regrid_to_grid = str(self.c_dict['REGRID_TO_GRID'])
        self.add_env_var(b'REGRID_TO_GRID', regrid_to_grid)
#        os.environ['REGRID_TO_GRID'] = regrid_to_grid

        # MET accepts a list of values for POINT_STAT_POLY, POINT_STAT_GRID,
        # POINT_STAT_STATION_ID, and POINT_STAT_MESSAGE_TYPE. If these
        # values are not set in the METplus config file, assign them to "[]" so
        # MET recognizes that these are empty lists, resulting in the
        # expected behavior.
        poly_str = str(self.c_dict['POINT_STAT_POLY'])
        if not poly_str:
            self.add_env_var(b'POINT_STAT_POLY', "[]")
        else:
            poly = poly_str.replace("\'", "\"")
            self.add_env_var(b'POINT_STAT_POLY', poly)

        grid_str = str(self.c_dict['POINT_STAT_GRID'])
        if not grid_str:
            self.add_env_var(b'POINT_STAT_GRID', "[]")
        else:
            # grid = grid_str.replace("\'", "\"")
            grid = '"' + grid_str + '"'
            self.add_env_var(b'POINT_STAT_GRID', grid)

        sid_str = str(self.c_dict['POINT_STAT_STATION_ID'])
        if not sid_str:
            self.add_env_var(b'POINT_STAT_STATION_ID', "[]")
        else:
            sid = sid_str.replace("\'", "\"")
            self.add_env_var(b'POINT_STAT_STATION_ID', sid)

        tmp_message_type = str(self.c_dict['POINT_STAT_MESSAGE_TYPE'])
        # Check for "empty" POINT_STAT_MESSAGE_TYPE in METplus config file and
        # set the POINT_STAT_MESSAGE_TYPE environment variable appropriately.
        if not tmp_message_type:
            self.add_env_var('POINT_STAT_MESSAGE_TYPE', "[]")
        else:
            # Not empty, set the POINT_STAT_MESSAGE_TYPE environment
            #  variable to the
            # message types specified in the METplus config file.
            tmp_message_type = str(tmp_message_type).replace("\'", "\"")
            # Remove all whitespace
            tmp_message_type = ''.join(tmp_message_type.split())
            self.add_env_var(b'POINT_STAT_MESSAGE_TYPE', tmp_message_type)

        # Retrieve all the fcst and obs field values (name, level, options)
        # from the METplus config file, passed into the MET config file via
        # the FCST_FIELD and OBS_FIELD environment variables.
        all_vars_list = util.parse_var_list(self.p)
        met_fields = util.reformat_fields_for_met(all_vars_list, self.logger)

        self.add_env_var(b'FCST_FIELD', met_fields.fcst_field)
        self.add_env_var(b'OBS_FIELD', met_fields.obs_field)

        # Set the environment variables corresponding to the obs_window
        # dictionary.
        self.add_env_var(b'OBS_WINDOW_BEGIN',
                         str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var(b'OBS_WINDOW_END', str(self.c_dict['OBS_WINDOW_END']))
        
        # add additional env vars if they are specified
        if self.c_dict['VERIFICATION_MASK'] != '':
            self.add_env_var('VERIF_MASK',
                             self.c_dict['VERIFICATION_MASK'])
            print_list.append('VERIF_MASK')

        # add additional env vars if they are specified
        if self.c_dict['NEIGHBORHOOD_WIDTH'] != '':
            self.add_env_var('NEIGHBORHOOD_WIDTH',
                             self.c_dict['NEIGHBORHOOD_WIDTH'])
            print_list.append('NEIGHBORHOOD_WIDTH')

        if self.c_dict['NEIGHBORHOOD_SHAPE'] != '':
            self.add_env_var('NEIGHBORHOOD_SHAPE',
                             self.c_dict['NEIGHBORHOOD_SHAPE'])
            print_list.append('NEIGHBORHOOD_SHAPE')

        if self.c_dict['VERIFICATION_MASK'] != '':
            self.add_env_var('VERIF_MASK',
                             self.c_dict['VERIFICATION_MASK'])
            print_list.append('VERIF_MASK')

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)


if __name__ == "__main__":
        util.run_stand_alone("point_stat_wrapper", "PointStat")
