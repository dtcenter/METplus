#!/usr/bin/env python

"""!
Program Name: TcStatWrapper.py
Contact(s):  Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Stratify tropical cyclone data by any combination of time, column,
          statistics
History log: Initial version
Usage: TcStatWrapper.py
Parameters: None
Input Files: tc_pairs data
Output Files: subset of tc_pairs data
Condition codes: 0 for success, 1 for failure

"""

from __future__ import (print_function, division, unicode_literals)

import os
import sys
import produtil.setup
from produtil.run import ExitStatusException
import met_util as util
from command_builder import CommandBuilder
import config_metplus


## @namespace TcStatWrapper
#  @brief Wrapper to the MET tool tc_stat, which is used for filtering tropical
#  cyclone pair data.

# pylint:disable=too-few-public-methods
# This class is just a wrapper to the MET tool tc_stat.  The attribute data
# is used to create the tc_stat commands and not necessarily operate on that
# attribute data.


class TcStatWrapper(CommandBuilder):
    """! Wrapper for the MET tool, tc_stat, which is used to filter tropical
         cyclone pair data.
    """

    def __init__(self, p, logger):
        super(TcStatWrapper, self).__init__(p, logger)
        self.app_name = 'tc_stat'
        self.config = self.p
        self.logger = logger

        # Check whether we are running MET tc_stat from the command line
        # or with the MET config file.
        run_method = self.p.getstr('config', 'TC_STAT_RUN_VIA')
        self.by_config = bool(run_method == 'CONFIG')

        if self.logger is None:
            self.logger = util.get_logger(self.p, sublog='TcStat')
        self.tc_stat_dict = self.create_tc_stat_dictionary()
        self.tc_exe = self.tc_stat_dict['APP_PATH']
        self.logger.info("Initialized TcStatWrapper")

    def create_tc_stat_dictionary(self):
        """!  Read in and store all the values from the config file.  This
              will make it easier to reassign values while unit testing and
              make it easier when retrieving these values, especially when
              they are needed multiple times by different methods.

              Args:

              Returns:
                    tc_stat_dict - a dictionary of the key-value representation
                                   of options set in the config file.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info('Creating tc-stat dictionary...')

        tc_stat_dict = dict()

        # Check for the MET_INSTALL_DIR, if it is missing, then
        # we cannot invoke the MET tool.
        if not util.getdir(self.p, 'MET_INSTALL_DIR'):
            self.logger.error(
                cur_filename + '|' + cur_function + ': MET install ' +
                'directory not found in config file. Exiting.')
            sys.exit(1)
        tc_stat_dict['APP_PATH'] = os.path.join(
            util.getdir(self.p, 'MET_INSTALL_DIR'), 'bin/tc_stat')

        tc_stat_dict['APP_NAME'] = os.path.basename(tc_stat_dict['APP_PATH'])

        if self.by_config:
            tc_stat_dict['AMODEL'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_AMODEL'))

            tc_stat_dict['BMODEL'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_BMODEL'))

            tc_stat_dict['DESC'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_DESC'))

            tc_stat_dict['STORM_ID'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_STORM_ID'))

            tc_stat_dict['BASIN'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_BASIN'))

            tc_stat_dict['CYCLONE'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_CYCLONE'))

            tc_stat_dict['STORM_NAME'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_STORM_NAME'))

            tc_stat_dict['INIT_BEG'] = self.config.getstr('config',
                                                          'TC_STAT_INIT_BEG')

            tc_stat_dict['INIT_END'] = self.config.getstr('config',
                                                          'TC_STAT_INIT_END')

            tc_stat_dict['INIT_INCLUDE'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_INIT_INCLUDE'))

            tc_stat_dict['INIT_EXCLUDE'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_INIT_EXCLUDE'))

            tc_stat_dict['INIT_HOUR'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_INIT_HOUR'))

            tc_stat_dict['VALID_BEG'] = self.config.getstr('config',
                                                           'TC_STAT_INIT_BEG')

            tc_stat_dict['VALID_END'] = self.config.getstr('config',
                                                           'TC_STAT_INIT_END')

            tc_stat_dict['VALID_INCLUDE'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_VALID_INCLUDE'))

            tc_stat_dict['VALID_EXCLUDE'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_VALID_EXCLUDE'))

            tc_stat_dict['LEAD_REQ'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_LEAD_REQ'))

            tc_stat_dict['INIT_MASK'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_INIT_MASK'))

            tc_stat_dict['VALID_MASK'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_VALID_MASK'))

            tc_stat_dict['VALID_HOUR'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_VALID_HOUR'))

            tc_stat_dict['LEAD'] = \
                util.getlist(self.config.getstr('config', 'TC_STAT_LEAD'))

            tc_stat_dict['TRACK_WATCH_WARN'] = \
                util.getlist(
                    self.config.getstr('config', 'TC_STAT_TRACK_WATCH_WARN'))

            tc_stat_dict['COLUMN_THRESH_NAME'] = \
                util.getlist(
                    self.config.getstr('config', 'TC_STAT_COLUMN_THRESH_NAME'))

            tc_stat_dict['COLUMN_THRESH_VAL'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_COLUMN_THRESH_VAL'))

            tc_stat_dict['COLUMN_STR_NAME'] = \
                util.getlist(
                    self.config.getstr('config', 'TC_STAT_COLUMN_STR_NAME'))

            tc_stat_dict['COLUMN_STR_VAL'] = \
                util.getlist(
                    self.config.getstr('config', 'TC_STAT_COLUMN_STR_VAL'))

            tc_stat_dict['INIT_THRESH_NAME'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_INIT_THRESH_NAME'))

            tc_stat_dict['INIT_THRESH_VAL'] = util.getlist(
                self.config.getstr('config', 'TC_STAT_INIT_THRESH_VAL'))

            tc_stat_dict['INIT_STR_NAME'] = \
                util.getlist(
                    self.config.getstr('config', 'TC_STAT_INIT_STR_NAME'))

            tc_stat_dict['INIT_STR_VAL'] = \
                util.getlist(
                    self.config.getstr('config', 'TC_STAT_INIT_STR_VAL'))

            try:
                tc_stat_dict['WATER_ONLY'] = \
                    self.config.getbool('config', 'TC_STAT_WATER_ONLY')
            except ValueError:
                # WATER_ONLY not defined in any configuration files,
                # set to False and proceed.
                self.logger.warn(
                    cur_filename + '|' + cur_function +
                    ': WATER_ONLY undefined in config file.  Setting to False.')
                tc_stat_dict['WATER_ONLY'] = False
                pass

            try:
                tc_stat_dict['LANDFALL'] = \
                    self.config.getbool('config', 'TC_STAT_LANDFALL')
            except ValueError:
                # Not set by user in MET tc_stat config file or METplus config
                # file.  Set to False and continue ingesting config file values.
                self.logger.warn(
                    cur_filename + '|' + cur_function + ': LANDFALL' +
                    ' undefined in config file.  Setting to False...')
                tc_stat_dict['LANDFALL'] = False
                pass

            tc_stat_dict['LANDFALL_BEG'] = \
                self.config.getstr('config', 'TC_STAT_LANDFALL_BEG')

            tc_stat_dict['LANDFALL_END'] = \
                self.config.getstr('config', 'TC_STAT_LANDFALL_END')

            tc_stat_dict['JOBS_LIST'] = \
                self.p.getstr('config', 'TC_STAT_JOBS_LIST')
        else:
            # via command line, only one job requested
            tc_stat_dict['CMD_LINE_JOB'] = self.config.getstr(
                'config', 'TC_STAT_CMD_LINE_JOB')

        tc_stat_dict['MATCH_POINTS'] = \
            self.p.getstr('config', 'TC_STAT_MATCH_POINTS').upper()
        tc_stat_dict['OUTPUT_BASE'] = util.getdir(self.p, 'OUTPUT_BASE')

        tc_stat_dict['TMP_DIR'] = util.getdir(self.p, 'TMP_DIR')

        tc_stat_dict['METPLUS_BASE'] = util.getdir(self.p, 'METPLUS_BASE')

        tc_stat_dict['MET_INSTALL_DIR'] = util.getdir(self.p, 'MET_INSTALL_DIR')

        tc_stat_dict['INPUT_DIR'] = util.getdir(self.p, 'TC_STAT_INPUT_DIR')

        tc_stat_dict['OUTPUT_DIR'] = util.getdir(self.p, 'TC_STAT_OUTPUT_DIR')

        tc_stat_dict['PARM_BASE'] = util.getdir(self.p, 'PARM_BASE')

        tc_stat_dict['CONFIG_FILE'] = self.p.getstr('config', 'TC_STAT_CONFIG_FILE')

        return tc_stat_dict

    def run_all_times(self):
        """! Builds the call to the MET tool TC-STAT for all requested
             initialization times (init or valid).  Called from master_metplus

             Args:

             Returns:
                0 if successfully runs MET tc_stat tool.
                1 otherwise
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.info(cur_filename  + '|' + cur_filename +
                         ':   Starting tc_stat_wrapper...')
        if self.by_config:
            self.set_envs()
            if not self.config_lists_ok():
                self.logger.error('There is at least one <>_VAL/<>_NAME pair'
                                  'requested in the MET tc-stat config '
                                  'file where the size of the lists '
                                  'is not equal.  Please '
                                  'check your MET tc-stat config file.')
                sys.exit(1)

        # Don't forget to create the output directory, as MET tc_stat will
        # not do this.
        util.mkdir_p(self.tc_stat_dict['OUTPUT_DIR'])

        # Since this is different from the other MET tools, we will build
        # the commands rather than use command builder's methods.
        match_points = str(self.tc_stat_dict['MATCH_POINTS'])
        if self.by_config:
            # Running with config file

            tc_cmd_list = [self.tc_exe,
                           " -lookin", self.tc_stat_dict['INPUT_DIR'],
                           " -config ", self.tc_stat_dict['CONFIG_FILE'],
                           self.tc_stat_dict['JOBS_LIST']]
        else:
            # Run single job from command line
            tc_cmd_list = [self.tc_exe,
                           " -lookin", self.tc_stat_dict['INPUT_DIR'],
                           self.tc_stat_dict['CMD_LINE_JOB'],
                           "-match_points", match_points]

        tc_cmd_str = ' '.join(tc_cmd_list)

        # Since this wrapper is not using the CommandBuilder to build the cmd,
        # we need to add the met verbosity level to the MET cmd created before
        # we run the command.
        tc_cmd_str = self.cmdrunner.insert_metverbosity_opt(tc_cmd_str)

        # Run tc_stat
        try:
            (ret, cmd) = \
                self.cmdrunner.run_cmd(tc_cmd_str, app_name=self.app_name)
            if not ret == 0:
                raise ExitStatusException(
                    '%s: non-zero exit status' % (repr(cmd),), ret)
        except ExitStatusException as ese:
            self.logger.error(ese)

        return 0

    def set_envs(self):
        """! Set the env variables based on settings in the METplus config
             files.  This is only necessary when running MET tc_stat via
             the config file.

             Args:

             Returns:
                 0 - if successfully sets env variable


        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.info('Setting env variables from config file...')
        # Set all the environment variables that are needed by the
        # MET config file.

        tmp_amodel = self.tc_stat_dict['AMODEL']
        if tmp_amodel:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_amodel_str = str(tmp_amodel).replace("\'", "\"")
            tmp_amodel = ''.join(tmp_amodel_str.split())
            self.add_env_var('AMODEL', tmp_amodel)
        else:
            self.add_env_var('AMODEL', "[]")

        tmp_bmodel = self.tc_stat_dict['BMODEL']
        if tmp_bmodel:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_bmodel_str = str(tmp_bmodel).replace("\'", "\"")
            tmp_bmodel = ''.join(tmp_bmodel_str.split())
            self.add_env_var('BMODEL', tmp_bmodel)
        else:
            self.add_env_var('BMODEL', "[]")

        tmp_desc = self.tc_stat_dict['DESC']
        if tmp_desc:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_desc_str = str(tmp_desc).replace("\'", "\"")
            tmp_desc = ''.join(tmp_desc_str.split())
            self.add_env_var('DESC', tmp_desc)
        else:
            self.add_env_var('DESC', "[]")

        tmp_storm_id = self.tc_stat_dict['STORM_ID']
        if tmp_storm_id:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_storm_id_str = str(tmp_storm_id).replace("\'", "\"")
            tmp_storm_id = ''.join(tmp_storm_id_str.split())
            self.add_env_var('STORM_ID', tmp_storm_id)
        else:
            self.add_env_var('STORM_ID', "[]")

        tmp_basin = self.tc_stat_dict['BASIN']
        if tmp_basin:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_basin_str = str(tmp_basin).replace("\'", "\"")
            tmp_basin = ''.join(tmp_basin_str.split())
            self.add_env_var('BASIN', tmp_basin)
        else:
            self.add_env_var('BASIN', "[]")

        tmp_cyclone = self.tc_stat_dict['CYCLONE']
        if tmp_cyclone:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_cyclone_str = str(tmp_cyclone).replace("\'", "\"")
            tmp_cyclone = ''.join(tmp_cyclone_str.strip())
            self.add_env_var('CYCLONE', tmp_cyclone)
        else:
            self.add_env_var('CYCLONE', "[]")

        tmp_storm_name = self.tc_stat_dict['STORM_NAME']
        if tmp_storm_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_storm_name_str = str(tmp_storm_name).replace("\'", "\"")
            tmp_storm_name = ''.join(tmp_storm_name_str.strip())
            self.add_env_var('STORM_NAME', tmp_storm_name)
        else:
            self.add_env_var('STORM_NAME', "[]")

        if self.tc_stat_dict['INIT_BEG']:
            self.add_env_var(b'INIT_BEG', self.tc_stat_dict['INIT_BEG'])
        else:
            self.add_env_var(b'INIT_BEG', "")

        if self.tc_stat_dict['INIT_END']:
            self.add_env_var('INIT_END', self.tc_stat_dict['INIT_END'])
        else:
            self.add_env_var(b'INIT_END', "")

        tmp_init_include = self.tc_stat_dict['INIT_INCLUDE']
        if tmp_init_include:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_include_str = str(tmp_init_include).replace("\'", "\"")
            tmp_init_include = ''.join(tmp_init_include_str.strip())
            self.add_env_var('INIT_INCLUDE', tmp_init_include)
        else:
            self.add_env_var('INIT_INCLUDE', "[]")

        tmp_init_exclude = self.tc_stat_dict['INIT_EXCLUDE']
        if tmp_init_exclude:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_exclude_str = str(tmp_init_exclude).replace("\'", "\"")
            tmp_init_exclude = ''.join(tmp_init_exclude_str.strip())
            self.add_env_var('INIT_EXCLUDE', tmp_init_exclude)
        else:
            self.add_env_var('INIT_EXCLUDE', "[]")

        tmp_init_hour = self.tc_stat_dict['INIT_HOUR']
        if tmp_init_hour:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_hour_str = str(tmp_init_hour).replace("\'", "\"")
            tmp_init_hour = ''.join(tmp_init_hour_str.split())
            self.add_env_var('INIT_HOUR', tmp_init_hour)
        else:
            self.add_env_var('INIT_HOUR', "[]")

        tmp_valid_begin = self.tc_stat_dict['VALID_BEG']
        if tmp_valid_begin:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_begin_str = str(tmp_valid_begin).replace("\'", "\"")
            tmp_valid_begin = ''.join(tmp_valid_begin_str.strip())
            self.add_env_var(b'VALID_BEG', tmp_valid_begin)
        else:
            self.add_env_var(b'VALID_BEG', '')

        tmp_valid_end = self.tc_stat_dict['VALID_END']
        if tmp_valid_end:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_end_str = str(tmp_valid_end).replace("\'", "\"")
            tmp_valid_end = ''.join(tmp_valid_end_str.strip())
            self.add_env_var(b'VALID_END', tmp_valid_end)
        else:
            self.add_env_var(b'VALID_END', "")

        tmp_valid_include = self.tc_stat_dict['VALID_INCLUDE']
        if tmp_valid_include:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_include_str = str(tmp_valid_include).replace("\'", "\"")
            tmp_valid_include = ''.join(tmp_valid_include_str.strip())
            self.add_env_var('VALID_INCLUDE', tmp_valid_include)
        else:
            self.add_env_var('VALID_INCLUDE', "[]")

        tmp_valid_exclude = self.tc_stat_dict['VALID_EXCLUDE']
        if tmp_valid_exclude:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_exclude_str = str(tmp_valid_exclude).replace("\'", "\"")
            tmp_valid_exclude = ''.join(tmp_valid_exclude_str.strip())
            self.add_env_var('VALID_EXCLUDE', tmp_valid_exclude)
        else:
            self.add_env_var('VALID_EXCLUDE', "[]")

        tmp_valid_hour = self.tc_stat_dict['VALID_HOUR']
        if tmp_valid_hour:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_hour_str = str(tmp_valid_hour).replace("\'", "\"")
            tmp_valid_hour = ''.join(tmp_valid_hour_str.strip())
            self.add_env_var('VALID_HOUR', tmp_valid_hour)
        else:
            self.add_env_var('VALID_HOUR', "[]")

        tmp_lead_req = self.tc_stat_dict['LEAD_REQ']
        if tmp_lead_req:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_lead_req_str = str(tmp_lead_req).replace("\'", "\"")
            tmp_lead_req = ''.join(tmp_lead_req_str.strip())
            self.add_env_var('LEAD_REQ', tmp_lead_req)
        else:
            self.add_env_var('LEAD_REQ', "[]")

        tmp_lead = self.tc_stat_dict['LEAD']
        if tmp_lead:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_lead_str = str(tmp_lead).replace("\'", "\"")
            tmp_lead = ''.join(tmp_lead_str.strip())
            self.add_env_var('LEAD', tmp_lead)
        else:
            self.add_env_var('LEAD', "[]")

        tmp_init_mask = self.tc_stat_dict['INIT_MASK']
        if tmp_init_mask:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_mask_str = str(tmp_init_mask).replace("\'", "\"")
            tmp_init_mask = ''.join(tmp_init_mask_str.strip())
            self.add_env_var('INIT_MASK', tmp_init_mask)
        else:
            self.add_env_var('INIT_MASK', "[]")

        tmp_valid_mask = self.tc_stat_dict['VALID_MASK']
        if tmp_valid_mask:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_mask_str = str(tmp_valid_mask).replace("\'", "\"")
            tmp_valid_mask = ''.join(tmp_valid_mask_str.strip())
            self.add_env_var('VALID_MASK', tmp_valid_mask)
        else:
            self.add_env_var('VALID_MASK', "[]")

        tmp_track_watch_warn = self.tc_stat_dict['TRACK_WATCH_WARN']
        if tmp_track_watch_warn:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_track_watch_warn_str = str(tmp_track_watch_warn).replace("\'",
                                                                         "\"")
            tmp_track_watch_warn = ''.join(tmp_track_watch_warn_str.strip())
            self.add_env_var('TRACK_WATCH_WARN', tmp_track_watch_warn)
        else:
            self.add_env_var('TRACK_WATCH_WARN', "[]")

        tmp_column_thresh_name = self.tc_stat_dict['COLUMN_THRESH_NAME']
        if tmp_column_thresh_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_thresh_name_str = str(tmp_column_thresh_name).replace(
                "\'", "\"")
            tmp_column_thresh_name = ''.join(tmp_column_thresh_name_str.strip())
            self.add_env_var('COLUMN_THRESH_NAME', tmp_column_thresh_name)
        else:
            self.add_env_var('COLUMN_THRESH_NAME', "[]")

        tmp_column_thresh_val = self.tc_stat_dict['COLUMN_THRESH_VAL']
        if tmp_column_thresh_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_thresh_val_str = str(tmp_column_thresh_val).replace("\'",
                                                                           "\"")
            tmp_column_thresh_val = ''.join(tmp_column_thresh_val_str.strip())
            self.add_env_var('COLUMN_THRESH_VAL', tmp_column_thresh_val)
        else:
            self.add_env_var('COLUMN_THRESH_VAL', "[]")

        tmp_column_str_name = self.tc_stat_dict['COLUMN_STR_NAME']
        if tmp_column_str_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_thresh_val_str = str(tmp_column_thresh_val).replace("\'",
                                                                           "\"")
            tmp_column_thresh_val = ''.join(tmp_column_thresh_val_str.strip())
            self.add_env_var('COLUMN_STR_NAME', tmp_column_thresh_val)
        else:
            self.add_env_var('COLUMN_STR_NAME', "[]")

        tmp_column_str_val = self.tc_stat_dict['COLUMN_STR_VAL']
        if tmp_column_str_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_str_val_str = str(tmp_column_str_val).replace("\'", "\"")
            tmp_column_str_val = ''.join(tmp_column_str_val_str.strip())
            self.add_env_var('COLUMN_STR_VAL', tmp_column_str_val)
        else:
            self.add_env_var('COLUMN_STR_VAL', "[]")

        tmp_init_thresh_name = self.tc_stat_dict['INIT_THRESH_NAME']
        if tmp_init_thresh_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_thresh_name_str = str(tmp_init_thresh_name).replace("\'",
                                                                         "\"")
            tmp_init_thresh_name = ''.join(tmp_init_thresh_name_str.strip())

            self.add_env_var('INIT_THRESH_NAME', tmp_init_thresh_name)

        else:
            self.add_env_var('INIT_THRESH_NAME', "[]")

        tmp_init_thresh_val = self.tc_stat_dict['INIT_THRESH_VAL']
        if tmp_init_thresh_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_thresh_val_str = str(tmp_init_thresh_val).replace("\'",
                                                                       "\"")
            tmp_init_thresh_val = ''.join(tmp_init_thresh_val_str.strip())
            self.add_env_var('INIT_THRESH_VAL', tmp_init_thresh_val)
        else:
            self.add_env_var('INIT_THRESH_VAL', "[]")

        tmp_init_str_name = self.tc_stat_dict['INIT_STR_NAME']
        if tmp_init_str_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_str_name_str = str(tmp_init_str_name).replace("\'", "\"")
            tmp_init_str_name = ''.join(tmp_init_str_name_str.strip())
            self.add_env_var('INIT_STR_NAME', tmp_init_str_name)
        else:
            self.add_env_var('INIT_STR_NAME', "[]")

        tmp_init_str_val = self.tc_stat_dict['INIT_STR_VAL']
        if tmp_init_str_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_str_val_str = str(tmp_init_str_val).replace("\'", "\"")
            tmp_init_str_val = ''.join(tmp_init_str_val_str.strip())
            self.add_env_var('INIT_STR_VAL', tmp_init_str_val)
        else:
            self.add_env_var('INIT_STR_VAL', "[]")

        # boolean values for WATER_ONLY
        if self.tc_stat_dict['WATER_ONLY']:
            flag = "TRUE"
        else:
            flag = "FALSE"
        self.add_env_var('WATER_ONLY', flag)

        # boolean value for LANDFALL
        if self.tc_stat_dict['LANDFALL']:
            flag = "TRUE"
        else:
            flag = "FALSE"
        self.add_env_var('LANDFALL', flag)

        if self.tc_stat_dict['LANDFALL_BEG']:
            self.add_env_var('LANDFALL_BEG',
                             self.tc_stat_dict['LANDFALL_BEG'])
        else:
            # Set to default
            self.add_env_var('LANDFALL_BEG', '-24')

        if self.tc_stat_dict['LANDFALL_END']:
            self.add_env_var('LANDFALL_END',
                             self.tc_stat_dict['LANDFALL_END'])
        else:
            # Set to default
            self.add_env_var('LANDFALL_END', '00')

        # boolean value for MATCH_POINTS
        if self.tc_stat_dict['MATCH_POINTS'] == 'true':
            flag = "TRUE"
        else:
            flag = "FALSE"
        self.add_env_var('MATCH_POINTS', flag)

        if self.tc_stat_dict['CONFIG_FILE']:
            self.add_env_var(b'CONFIG_FILE',
                             self.tc_stat_dict['CONFIG_FILE'])
        else:
            self.logger.error(
                cur_filename + '|' + cur_function +
                ': no MET TC-Stat config file found. Exiting')
            sys.exit(1)

        jobs_list_tmp = self.tc_stat_dict['JOBS_LIST']
        if jobs_list_tmp:
            # MET is expecting a string
            jobs_list_str = '"' + jobs_list_tmp + '"'
            self.add_env_var('JOBS', jobs_list_str)
        else:
            self.logger.error('No jobs list defined. Please check your METplus'
                              'config file.  Exiting...')
            sys.exit(1)
        return 0

    def config_lists_ok(self):
        """! Verify that the length of the name and val lists
             in the MET tc-stat config file are of equal length, if
             not, log an error message and exit.  As soon as a length mismatch
             is encountered, return False.

             Args:

             Returns:
                 True: if all corresponding <>_NAME and <>_VAL lists
                       have the same length
                 False: if any name/val list length mismatch is encountered
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info('Checking if name-val lists in config file have'
                         'the same length...')
        is_ok = True

        # Check COLUMN_THRESH_NAME and COLUMN_THRESH_VAL
        if len(self.tc_stat_dict['COLUMN_THRESH_NAME']) != \
                len(self.tc_stat_dict['COLUMN_THRESH_VAL']):
            self.logger.error(
                cur_filename + '|' + cur_function +
                ': COLUMN_THRESH_NAME does not have the same ' +
                'number of items as COLUMN_THRESH_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # Check COLUMN_STR_NAME and COLUMN_STR_VAL
        if len(self.tc_stat_dict['COLUMN_STR_NAME']) != \
                len(self.tc_stat_dict['COLUMN_STR_VAL']):
            self.logger.error(
                cur_filename + '|' + cur_function +
                ': COLUMN_STR_NAME does not have the same ' +
                'number of items as COLUMN_STR_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # Check INIT_THRESH_NAME and INIT_THRESH_VAL
        if len(self.tc_stat_dict['INIT_THRESH_NAME']) != \
                len(self.tc_stat_dict['INIT_THRESH_VAL']):
            self.logger.error(
                cur_filename + '|' + cur_function +
                ': INIT_THRESH_NAME does not have the same ' +
                'number of items as INIT_THRESH_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # Check INIT_STR_NAME and INIT_STR_VAL
        if len(self.tc_stat_dict['INIT_STR_NAME']) != \
                len(self.tc_stat_dict['INIT_STR_VAL']):
            self.logger.error(
                cur_filename + '|' + cur_function +
                ': INIT_STR_NAME does not have the same ' +
                'number of items as INIT_STR_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # If we got here, all corresponding lists have the same length
        return is_ok

    def build_tc_stat(self, tc_stat_output_dir, cur_init, tc_input_list,
                      filter_opts):
        """!This is called from extract_tiles_wrapper and from any other
            wrapper to provide additional filtering WITHOUT the need for
            a tc_stat MET config file.

            Creates the call to MET tool TC-STAT to subset tc-pairs output
            based on the criteria specified in the feature relative
            use case parameter/config file.

            Args:
            @param tc_stat_output_dir:  The output directory where filtered
                                       results are saved.
            @param cur_init:  The initialization time
            @param tc_input_list:  The "list" of input data (the files containing
                                   the tc pair data to be filtered) in a
                                   string
            @param filter_opts:  The list of filter options to apply

            Returns:
                None: if no error, then invoke MET tool TC-STAT and
                    subsets tc-pairs data, creating a filter.tcst file.

                Raises CalledProcessError
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        util.mkdir_p(tc_stat_output_dir)

        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(tc_stat_output_dir, cur_init,
                                   filter_filename)
        filter_path = os.path.join(tc_stat_output_dir, cur_init)
        util.mkdir_p(filter_path)

        # This is for extract_tiles to call without a config file
        tc_cmd_list = [self.tc_exe, " -job filter ",
                       " -lookin ", tc_input_list,
                       " -match_points true ",
                       " -init_inc ", cur_init,
                       " -dump_row ", filter_name,
                       " ", filter_opts]

        tc_cmd_str = ''.join(tc_cmd_list)

        # Since this wrapper is not using the CommandBuilder to build the cmd,
        # we need to add the met verbosity level to the MET cmd created before
        # we run the command.
        tc_cmd_str = self.cmdrunner.insert_metverbosity_opt(tc_cmd_str)

        # Run tc_stat
        try:
            # tc_cmd = batchexe('sh')['-c', tc_cmd_str].err2out()
            # checkrun(tc_cmd)
            (ret, cmd) = \
                self.cmdrunner.run_cmd(tc_cmd_str, app_name=self.app_name)
            if not ret == 0:
                raise ExitStatusException(
                    '%s: non-zero exit status' % (repr(cmd),), ret)
        except ExitStatusException as ese:
            self.logger.error(ese)


if __name__ == "__main__":
    util.run_stand_alone("tc_stat_wrapper", "TcStat")
