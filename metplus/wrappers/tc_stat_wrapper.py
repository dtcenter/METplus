"""!
Program Name: TCStatWrapper.py
Contact(s):  Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Stratify tropical cyclone data by any combination of time, column,
          statistics
History log: Initial version
Usage: TCStatWrapper.py
Parameters: None
Input Files: tc_pairs data
Output Files: subset of tc_pairs data
Condition codes: 0 for success, 1 for failure

"""

import os
import sys

from produtil.run import ExitStatusException

from ..util import metplus_check_python_version, run_stand_alone, getlist, mkdir_p
from . import CommandBuilder

## @namespace TCStatWrapper
#  @brief Wrapper to the MET tool tc_stat, which is used for filtering tropical
#  cyclone pair data.

# pylint:disable=too-few-public-methods
# This class is just a wrapper to the MET tool tc_stat.  The attribute data
# is used to create the tc_stat commands and not necessarily operate on that
# attribute data.


class TCStatWrapper(CommandBuilder):
    """! Wrapper for the MET tool, tc_stat, which is used to filter tropical
         cyclone pair data.
    """

    def __init__(self, config, logger):
        self.app_name = 'tc_stat'

        # Check whether we are running MET tc_stat from the command line
        # or with the MET config file.
        run_method = config.getstr('config', 'TC_STAT_RUN_VIA')
        self.by_config = bool(run_method == 'CONFIG')

        super().__init__(config, logger)
        self.tc_exe = self.c_dict['APP_PATH']
        self.logger.info("Initialized TCStatWrapper")

    def create_c_dict(self):
        """!  Read in and store all the values from the config file.  This
              will make it easier to reassign values while unit testing and
              make it easier when retrieving these values, especially when
              they are needed multiple times by different methods.

              Args:

              Returns:
                    tc_stat_dict - a dictionary of the key-value representation
                                   of options set in the config file.
        """
        self.logger.info('Creating tc-stat dictionary...')

        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_TC_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Check for the MET_INSTALL_DIR, if it is missing, then
        # we cannot invoke the MET tool.
        if not self.config.getdir('MET_INSTALL_DIR'):
            self.log_error(
                cur_filename + '|' + cur_function + ': MET install ' +
                'directory not found in config file. Exiting.')
            sys.exit(1)
        c_dict['APP_PATH'] = os.path.join(
            self.config.getdir('MET_BIN_DIR', ''), 'tc_stat')

        c_dict['APP_NAME'] = os.path.basename(c_dict['APP_PATH'])

        if self.by_config:
            c_dict['AMODEL'] = \
                getlist(self.config.getstr('config', 'TC_STAT_AMODEL'))

            c_dict['BMODEL'] = \
                getlist(self.config.getstr('config', 'TC_STAT_BMODEL'))

            c_dict['DESC'] = \
                getlist(self.config.getstr('config', 'TC_STAT_DESC'))

            c_dict['STORM_ID'] = \
                getlist(self.config.getstr('config', 'TC_STAT_STORM_ID'))

            c_dict['BASIN'] = getlist(
                self.config.getstr('config', 'TC_STAT_BASIN'))

            c_dict['CYCLONE'] = getlist(
                self.config.getstr('config', 'TC_STAT_CYCLONE'))

            c_dict['STORM_NAME'] = getlist(
                self.config.getstr('config', 'TC_STAT_STORM_NAME'))

            c_dict['INIT_BEG'] = self.config.getstr('config',
                                                          'TC_STAT_INIT_BEG')

            c_dict['INIT_END'] = self.config.getstr('config',
                                                          'TC_STAT_INIT_END')

            c_dict['INIT_INCLUDE'] = getlist(
                self.config.getstr('config', 'TC_STAT_INIT_INCLUDE'))

            c_dict['INIT_EXCLUDE'] = getlist(
                self.config.getstr('config', 'TC_STAT_INIT_EXCLUDE'))

            c_dict['INIT_HOUR'] = getlist(
                self.config.getstr('config', 'TC_STAT_INIT_HOUR'))

            c_dict['VALID_BEG'] = self.config.getstr('config',
                                                           'TC_STAT_INIT_BEG')

            c_dict['VALID_END'] = self.config.getstr('config',
                                                           'TC_STAT_INIT_END')

            c_dict['VALID_INCLUDE'] = getlist(
                self.config.getstr('config', 'TC_STAT_VALID_INCLUDE'))

            c_dict['VALID_EXCLUDE'] = getlist(
                self.config.getstr('config', 'TC_STAT_VALID_EXCLUDE'))

            c_dict['LEAD_REQ'] = \
                getlist(self.config.getstr('config', 'TC_STAT_LEAD_REQ'))

            c_dict['INIT_MASK'] = \
                getlist(self.config.getstr('config', 'TC_STAT_INIT_MASK'))

            c_dict['VALID_MASK'] = \
                getlist(self.config.getstr('config', 'TC_STAT_VALID_MASK'))

            c_dict['VALID_HOUR'] = \
                getlist(self.config.getstr('config', 'TC_STAT_VALID_HOUR'))

            c_dict['LEAD'] = \
                getlist(self.config.getstr('config', 'TC_STAT_LEAD'))

            c_dict['TRACK_WATCH_WARN'] = \
                getlist(
                    self.config.getstr('config', 'TC_STAT_TRACK_WATCH_WARN'))

            c_dict['COLUMN_THRESH_NAME'] = \
                getlist(
                    self.config.getstr('config', 'TC_STAT_COLUMN_THRESH_NAME'))

            c_dict['COLUMN_THRESH_VAL'] = getlist(
                self.config.getstr('config', 'TC_STAT_COLUMN_THRESH_VAL'))

            c_dict['COLUMN_STR_NAME'] = \
                getlist(
                    self.config.getstr('config', 'TC_STAT_COLUMN_STR_NAME'))

            c_dict['COLUMN_STR_VAL'] = \
                getlist(
                    self.config.getstr('config', 'TC_STAT_COLUMN_STR_VAL'))

            c_dict['INIT_THRESH_NAME'] = getlist(
                self.config.getstr('config', 'TC_STAT_INIT_THRESH_NAME'))

            c_dict['INIT_THRESH_VAL'] = getlist(
                self.config.getstr('config', 'TC_STAT_INIT_THRESH_VAL'))

            c_dict['INIT_STR_NAME'] = \
                getlist(
                    self.config.getstr('config', 'TC_STAT_INIT_STR_NAME'))

            c_dict['INIT_STR_VAL'] = \
                getlist(
                    self.config.getstr('config', 'TC_STAT_INIT_STR_VAL'))

            try:
                c_dict['WATER_ONLY'] = \
                    self.config.getbool('config', 'TC_STAT_WATER_ONLY')
            except ValueError:
                # WATER_ONLY not defined in any configuration files,
                # set to False and proceed.
                self.logger.warn(
                    cur_filename + '|' + cur_function +
                    ': WATER_ONLY undefined in config file.  Setting to False.')
                c_dict['WATER_ONLY'] = False
                pass

            try:
                c_dict['LANDFALL'] = \
                    self.config.getbool('config', 'TC_STAT_LANDFALL')
            except ValueError:
                # Not set by user in MET tc_stat config file or METplus config
                # file.  Set to False and continue ingesting config file values.
                self.logger.warn(
                    cur_filename + '|' + cur_function + ': LANDFALL' +
                    ' undefined in config file.  Setting to False...')
                c_dict['LANDFALL'] = False
                pass

            c_dict['LANDFALL_BEG'] = \
                self.config.getstr('config', 'TC_STAT_LANDFALL_BEG')

            c_dict['LANDFALL_END'] = \
                self.config.getstr('config', 'TC_STAT_LANDFALL_END')

            c_dict['JOBS_LIST'] = \
                self.config.getstr('config', 'TC_STAT_JOBS_LIST')
        else:
            # via command line, only one job requested
            c_dict['CMD_LINE_JOB'] = self.config.getstr(
                'config', 'TC_STAT_CMD_LINE_JOB')

        c_dict['MATCH_POINTS'] = \
            self.config.getstr('config', 'TC_STAT_MATCH_POINTS').upper()
        c_dict['OUTPUT_BASE'] = self.config.getdir('OUTPUT_BASE')

        c_dict['TMP_DIR'] = self.config.getdir('TMP_DIR')

        c_dict['METPLUS_BASE'] = self.config.getdir('METPLUS_BASE')

        c_dict['MET_INSTALL_DIR'] = self.config.getdir('MET_INSTALL_DIR')

        c_dict['INPUT_DIR'] = self.config.getdir('TC_STAT_INPUT_DIR','')

        if not c_dict['INPUT_DIR']:
            self.log_error["TC_STAT_INPUT_DIR can not be empty"]

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_STAT_OUTPUT_DIR')

        c_dict['PARM_BASE'] = self.config.getdir('PARM_BASE')

        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'TC_STAT_CONFIG_FILE')

        return c_dict

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
                self.log_error('There is at least one <>_VAL/<>_NAME pair'
                                  'requested in the MET tc-stat config '
                                  'file where the size of the lists '
                                  'is not equal.  Please '
                                  'check your MET tc-stat config file.')
                sys.exit(1)

        # Don't forget to create the output directory, as MET tc_stat will
        # not do this.
        mkdir_p(self.c_dict['OUTPUT_DIR'])

        # Since this is different from the other MET tools, we will build
        # the commands rather than use command builder's methods.
        match_points = str(self.c_dict['MATCH_POINTS'])
        if self.by_config:
            # Running with config file

            tc_cmd_list = [self.tc_exe,
                           " -lookin", self.c_dict['INPUT_DIR'],
                           " -config ", self.c_dict['CONFIG_FILE'],
                           self.c_dict['JOBS_LIST']]
        else:
            # Run single job from command line
            tc_cmd_list = [self.tc_exe,
                           " -lookin", self.c_dict['INPUT_DIR'],
                           self.c_dict['CMD_LINE_JOB'],
                           "-match_points", match_points]

        tc_cmd_str = ' '.join(tc_cmd_list)

        # Since this wrapper is not using the CommandBuilder to build the cmd,
        # we need to add the met verbosity level to the MET cmd created before
        # we run the command.
        tc_cmd_str = self.cmdrunner.insert_metverbosity_opt(tc_cmd_str)

        # Run tc_stat
        try:
            (ret, cmd) = \
                self.cmdrunner.run_cmd(tc_cmd_str, self.env, app_name=self.app_name)
            if not ret == 0:
                raise ExitStatusException(
                    '%s: non-zero exit status' % (repr(cmd),), ret)
        except ExitStatusException as ese:
            self.log_error(ese)

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

        tmp_amodel = self.c_dict['AMODEL']
        if tmp_amodel:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_amodel_str = str(tmp_amodel).replace("\'", "\"")
            tmp_amodel = ''.join(tmp_amodel_str.split())
            self.add_env_var('AMODEL', tmp_amodel)
        else:
            self.add_env_var('AMODEL', "[]")

        tmp_bmodel = self.c_dict['BMODEL']
        if tmp_bmodel:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_bmodel_str = str(tmp_bmodel).replace("\'", "\"")
            tmp_bmodel = ''.join(tmp_bmodel_str.split())
            self.add_env_var('BMODEL', tmp_bmodel)
        else:
            self.add_env_var('BMODEL', "[]")

        tmp_desc = self.c_dict['DESC']
        if tmp_desc:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_desc_str = str(tmp_desc).replace("\'", "\"")
            tmp_desc = ''.join(tmp_desc_str.split())
            self.add_env_var('DESC', tmp_desc)
        else:
            self.add_env_var('DESC', "[]")

        tmp_storm_id = self.c_dict['STORM_ID']
        if tmp_storm_id:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_storm_id_str = str(tmp_storm_id).replace("\'", "\"")
            tmp_storm_id = ''.join(tmp_storm_id_str.split())
            self.add_env_var('STORM_ID', tmp_storm_id)
        else:
            self.add_env_var('STORM_ID', "[]")

        tmp_basin = self.c_dict['BASIN']
        if tmp_basin:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_basin_str = str(tmp_basin).replace("\'", "\"")
            tmp_basin = ''.join(tmp_basin_str.split())
            self.add_env_var('BASIN', tmp_basin)
        else:
            self.add_env_var('BASIN', "[]")

        tmp_cyclone = self.c_dict['CYCLONE']
        if tmp_cyclone:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_cyclone_str = str(tmp_cyclone).replace("\'", "\"")
            tmp_cyclone = ''.join(tmp_cyclone_str.strip())
            self.add_env_var('CYCLONE', tmp_cyclone)
        else:
            self.add_env_var('CYCLONE', "[]")

        tmp_storm_name = self.c_dict['STORM_NAME']
        if tmp_storm_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_storm_name_str = str(tmp_storm_name).replace("\'", "\"")
            tmp_storm_name = ''.join(tmp_storm_name_str.strip())
            self.add_env_var('STORM_NAME', tmp_storm_name)
        else:
            self.add_env_var('STORM_NAME', "[]")

        if self.c_dict['INIT_BEG']:
            self.add_env_var('INIT_BEG', self.c_dict['INIT_BEG'])
        else:
            self.add_env_var('INIT_BEG', "")

        if self.c_dict['INIT_END']:
            self.add_env_var('INIT_END', self.c_dict['INIT_END'])
        else:
            self.add_env_var('INIT_END', "")

        tmp_init_include = self.c_dict['INIT_INCLUDE']
        if tmp_init_include:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_include_str = str(tmp_init_include).replace("\'", "\"")
            tmp_init_include = ''.join(tmp_init_include_str.strip())
            self.add_env_var('INIT_INCLUDE', tmp_init_include)
        else:
            self.add_env_var('INIT_INCLUDE', "[]")

        tmp_init_exclude = self.c_dict['INIT_EXCLUDE']
        if tmp_init_exclude:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_exclude_str = str(tmp_init_exclude).replace("\'", "\"")
            tmp_init_exclude = ''.join(tmp_init_exclude_str.strip())
            self.add_env_var('INIT_EXCLUDE', tmp_init_exclude)
        else:
            self.add_env_var('INIT_EXCLUDE', "[]")

        tmp_init_hour = self.c_dict['INIT_HOUR']
        if tmp_init_hour:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_hour_str = str(tmp_init_hour).replace("\'", "\"")
            tmp_init_hour = ''.join(tmp_init_hour_str.split())
            self.add_env_var('INIT_HOUR', tmp_init_hour)
        else:
            self.add_env_var('INIT_HOUR', "[]")

        tmp_valid_begin = self.c_dict['VALID_BEG']
        if tmp_valid_begin:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_begin_str = str(tmp_valid_begin).replace("\'", "\"")
            tmp_valid_begin = ''.join(tmp_valid_begin_str.strip())
            self.add_env_var('VALID_BEG', tmp_valid_begin)
        else:
            self.add_env_var('VALID_BEG', '')

        tmp_valid_end = self.c_dict['VALID_END']
        if tmp_valid_end:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_end_str = str(tmp_valid_end).replace("\'", "\"")
            tmp_valid_end = ''.join(tmp_valid_end_str.strip())
            self.add_env_var('VALID_END', tmp_valid_end)
        else:
            self.add_env_var('VALID_END', "")

        tmp_valid_include = self.c_dict['VALID_INCLUDE']
        if tmp_valid_include:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_include_str = str(tmp_valid_include).replace("\'", "\"")
            tmp_valid_include = ''.join(tmp_valid_include_str.strip())
            self.add_env_var('VALID_INCLUDE', tmp_valid_include)
        else:
            self.add_env_var('VALID_INCLUDE', "[]")

        tmp_valid_exclude = self.c_dict['VALID_EXCLUDE']
        if tmp_valid_exclude:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_exclude_str = str(tmp_valid_exclude).replace("\'", "\"")
            tmp_valid_exclude = ''.join(tmp_valid_exclude_str.strip())
            self.add_env_var('VALID_EXCLUDE', tmp_valid_exclude)
        else:
            self.add_env_var('VALID_EXCLUDE', "[]")

        tmp_valid_hour = self.c_dict['VALID_HOUR']
        if tmp_valid_hour:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_hour_str = str(tmp_valid_hour).replace("\'", "\"")
            tmp_valid_hour = ''.join(tmp_valid_hour_str.strip())
            self.add_env_var('VALID_HOUR', tmp_valid_hour)
        else:
            self.add_env_var('VALID_HOUR', "[]")

        tmp_lead_req = self.c_dict['LEAD_REQ']
        if tmp_lead_req:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_lead_req_str = str(tmp_lead_req).replace("\'", "\"")
            tmp_lead_req = ''.join(tmp_lead_req_str.strip())
            self.add_env_var('LEAD_REQ', tmp_lead_req)
        else:
            self.add_env_var('LEAD_REQ', "[]")

        tmp_lead = self.c_dict['LEAD']
        if tmp_lead:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_lead_str = str(tmp_lead).replace("\'", "\"")
            tmp_lead = ''.join(tmp_lead_str.strip())
            self.add_env_var('LEAD', tmp_lead)
        else:
            self.add_env_var('LEAD', "[]")

        tmp_init_mask = self.c_dict['INIT_MASK']
        if tmp_init_mask:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_mask_str = str(tmp_init_mask).replace("\'", "\"")
            tmp_init_mask = ''.join(tmp_init_mask_str.strip())
            self.add_env_var('INIT_MASK', tmp_init_mask)
        else:
            self.add_env_var('INIT_MASK', "[]")

        tmp_valid_mask = self.c_dict['VALID_MASK']
        if tmp_valid_mask:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_valid_mask_str = str(tmp_valid_mask).replace("\'", "\"")
            tmp_valid_mask = ''.join(tmp_valid_mask_str.strip())
            self.add_env_var('VALID_MASK', tmp_valid_mask)
        else:
            self.add_env_var('VALID_MASK', "[]")

        tmp_track_watch_warn = self.c_dict['TRACK_WATCH_WARN']
        if tmp_track_watch_warn:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_track_watch_warn_str = str(tmp_track_watch_warn).replace("\'",
                                                                         "\"")
            tmp_track_watch_warn = ''.join(tmp_track_watch_warn_str.strip())
            self.add_env_var('TRACK_WATCH_WARN', tmp_track_watch_warn)
        else:
            self.add_env_var('TRACK_WATCH_WARN', "[]")

        tmp_column_thresh_name = self.c_dict['COLUMN_THRESH_NAME']
        if tmp_column_thresh_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_thresh_name_str = str(tmp_column_thresh_name).replace(
                "\'", "\"")
            tmp_column_thresh_name = ''.join(tmp_column_thresh_name_str.strip())
            self.add_env_var('COLUMN_THRESH_NAME', tmp_column_thresh_name)
        else:
            self.add_env_var('COLUMN_THRESH_NAME', "[]")

        tmp_column_thresh_val = self.c_dict['COLUMN_THRESH_VAL']
        if tmp_column_thresh_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_thresh_val_str = str(tmp_column_thresh_val).replace("\'",
                                                                           "\"")
            tmp_column_thresh_val = ''.join(tmp_column_thresh_val_str.strip())
            self.add_env_var('COLUMN_THRESH_VAL', tmp_column_thresh_val)
        else:
            self.add_env_var('COLUMN_THRESH_VAL', "[]")

        tmp_column_str_name = self.c_dict['COLUMN_STR_NAME']
        if tmp_column_str_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_str_name = str(tmp_column_str_name).replace("\'",
                                                                   "\"")
            tmp_column_str_name = ''.join(tmp_column_str_name.strip())
            self.add_env_var('COLUMN_STR_NAME', tmp_column_str_name)
        else:
            self.add_env_var('COLUMN_STR_NAME', "[]")

        tmp_column_str_val = self.c_dict['COLUMN_STR_VAL']
        if tmp_column_str_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_column_str_val_str = str(tmp_column_str_val).replace("\'", "\"")
            tmp_column_str_val = ''.join(tmp_column_str_val_str.strip())
            self.add_env_var('COLUMN_STR_VAL', tmp_column_str_val)
        else:
            self.add_env_var('COLUMN_STR_VAL', "[]")

        tmp_init_thresh_name = self.c_dict['INIT_THRESH_NAME']
        if tmp_init_thresh_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_thresh_name_str = str(tmp_init_thresh_name).replace("\'",
                                                                         "\"")
            tmp_init_thresh_name = ''.join(tmp_init_thresh_name_str.strip())

            self.add_env_var('INIT_THRESH_NAME', tmp_init_thresh_name)

        else:
            self.add_env_var('INIT_THRESH_NAME', "[]")

        tmp_init_thresh_val = self.c_dict['INIT_THRESH_VAL']
        if tmp_init_thresh_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_thresh_val_str = str(tmp_init_thresh_val).replace("\'",
                                                                       "\"")
            tmp_init_thresh_val = ''.join(tmp_init_thresh_val_str.strip())
            self.add_env_var('INIT_THRESH_VAL', tmp_init_thresh_val)
        else:
            self.add_env_var('INIT_THRESH_VAL', "[]")

        tmp_init_str_name = self.c_dict['INIT_STR_NAME']
        if tmp_init_str_name:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_str_name_str = str(tmp_init_str_name).replace("\'", "\"")
            tmp_init_str_name = ''.join(tmp_init_str_name_str.strip())
            self.add_env_var('INIT_STR_NAME', tmp_init_str_name)
        else:
            self.add_env_var('INIT_STR_NAME', "[]")

        tmp_init_str_val = self.c_dict['INIT_STR_VAL']
        if tmp_init_str_val:
            # Replace any single quotes with double quotes and remove any
            # whitespace
            tmp_init_str_val_str = str(tmp_init_str_val).replace("\'", "\"")
            tmp_init_str_val = ''.join(tmp_init_str_val_str.strip())
            self.add_env_var('INIT_STR_VAL', tmp_init_str_val)
        else:
            self.add_env_var('INIT_STR_VAL', "[]")

        # boolean values for WATER_ONLY
        if self.c_dict['WATER_ONLY']:
            flag = "TRUE"
        else:
            flag = "FALSE"
        self.add_env_var('WATER_ONLY', flag)

        # boolean value for LANDFALL
        if self.c_dict['LANDFALL']:
            flag = "TRUE"
        else:
            flag = "FALSE"
        self.add_env_var('LANDFALL', flag)

        if self.c_dict['LANDFALL_BEG']:
            self.add_env_var('LANDFALL_BEG',
                             self.c_dict['LANDFALL_BEG'])
        else:
            # Set to default
            self.add_env_var('LANDFALL_BEG', '-24')

        if self.c_dict['LANDFALL_END']:
            self.add_env_var('LANDFALL_END',
                             self.c_dict['LANDFALL_END'])
        else:
            # Set to default
            self.add_env_var('LANDFALL_END', '00')

        # boolean value for MATCH_POINTS
        if self.c_dict['MATCH_POINTS'] == 'true':
            flag = "TRUE"
        else:
            flag = "FALSE"
        self.add_env_var('MATCH_POINTS', flag)

        if self.c_dict['CONFIG_FILE']:
            self.add_env_var('CONFIG_FILE',
                             self.c_dict['CONFIG_FILE'])
        else:
            self.log_error(
                cur_filename + '|' + cur_function +
                ': no MET TC-Stat config file found. Exiting')
            sys.exit(1)

        jobs_list_tmp = self.c_dict['JOBS_LIST']
        if jobs_list_tmp:
            # MET is expecting a string
            jobs_list_str = '"' + jobs_list_tmp + '"'
            self.add_env_var('JOBS', jobs_list_str)
        else:
            self.log_error('No jobs list defined. Please check your METplus'
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
        if len(self.c_dict['COLUMN_THRESH_NAME']) != \
                len(self.c_dict['COLUMN_THRESH_VAL']):
            self.log_error(
                cur_filename + '|' + cur_function +
                ': COLUMN_THRESH_NAME does not have the same ' +
                'number of items as COLUMN_THRESH_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # Check COLUMN_STR_NAME and COLUMN_STR_VAL
        if len(self.c_dict['COLUMN_STR_NAME']) != \
                len(self.c_dict['COLUMN_STR_VAL']):
            self.log_error(
                cur_filename + '|' + cur_function +
                ': COLUMN_STR_NAME does not have the same ' +
                'number of items as COLUMN_STR_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # Check INIT_THRESH_NAME and INIT_THRESH_VAL
        if len(self.c_dict['INIT_THRESH_NAME']) != \
                len(self.c_dict['INIT_THRESH_VAL']):
            self.log_error(
                cur_filename + '|' + cur_function +
                ': INIT_THRESH_NAME does not have the same ' +
                'number of items as INIT_THRESH_VAL. Please' +
                ' check your MET tc_stat config file')
            return False

        # Check INIT_STR_NAME and INIT_STR_VAL
        if len(self.c_dict['INIT_STR_NAME']) != \
                len(self.c_dict['INIT_STR_VAL']):
            self.log_error(
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

        mkdir_p(tc_stat_output_dir)

        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(tc_stat_output_dir, cur_init,
                                   filter_filename)
        filter_path = os.path.join(tc_stat_output_dir, cur_init)
        mkdir_p(filter_path)

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
                self.cmdrunner.run_cmd(tc_cmd_str, self.env, app_name=self.app_name)
            if not ret == 0:
                raise ExitStatusException(
                    '%s: non-zero exit status' % (repr(cmd),), ret)
        except ExitStatusException as ese:
            self.log_error(ese)
