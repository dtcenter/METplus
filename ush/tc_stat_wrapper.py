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

from __future__ import (print_function, division)

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
                    dictionary of the key-value representation
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
        if not self.p.getdir('MET_INSTALL_DIR'):
            self.logger.error(
                cur_filename + '|' + cur_function + ': MET install ' +
                'directory not found in config file. Exiting.')
            sys.exit(1)
        tc_stat_dict['APP_PATH'] = os.path.join(
            self.p.getdir('MET_INSTALL_DIR'), 'bin/tc_stat')

        tc_stat_dict['APP_NAME'] = os.path.basename(tc_stat_dict['APP_PATH'])

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

        tc_stat_dict['INIT_HOUR'] = self.config.getstr('config',
                                                       'TC_STAT_INIT_HOUR')

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
            util.getlist(self.config.getstr('config', 'TC_STAT_COLUMN_STR_VAL'))

        tc_stat_dict['INIT_THRESH_NAME'] = util.getlist(
            self.config.getstr('config', 'TC_STAT_INIT_THRESH_NAME'))

        tc_stat_dict['INIT_THRESH_VAL'] = util.getlist(
            self.config.getstr('config', 'TC_STAT_INIT_THRESH_VAL'))

        tc_stat_dict['INIT_STR_NAME'] = \
            util.getlist(self.config.getstr('config', 'TC_STAT_INIT_STR_NAME'))

        tc_stat_dict['INIT_STR_VAL'] = \
            util.getlist(self.config.getstr('config', 'TC_STAT_INIT_STR_VAL'))

        tc_stat_dict['WATER_ONLY'] = self.config.getstr('config',
                                                        'TC_STAT_WATER_ONLY')

        tc_stat_dict['LANDFALL'] = self.config.getstr('config',
                                                      'TC_STAT_LANDFALL')

        tc_stat_dict['MATCH_POINTS'] = self.p.getstr('config',
                                                     'TC_STAT_MATCH_POINTS')

        tc_stat_dict['OUTPUT_BASE'] = self.p.getdir('OUTPUT_BASE')

        tc_stat_dict['PROJ_DIR'] = self.p.getdir('PROJ_DIR')

        tc_stat_dict['TMP_DIR'] = self.p.getdir('TMP_DIR')

        tc_stat_dict['METPLUS_BASE'] = self.p.getdir('METPLUS_BASE')

        tc_stat_dict['MET_INSTALL_DIR'] = self.p.getdir('MET_INSTALL_DIR')

        tc_stat_dict['INPUT_DIR'] = self.p.getdir('TC_STAT_INPUT_DIR')

        tc_stat_dict['OUTPUT_DIR'] = self.p.getdir('TC_STAT_OUTPUT_DIR')

        tc_stat_dict['JOB_TYPE'] = \
            self.p.getstr('config', 'TC_STAT_JOB_TYPE').lower()

        tc_stat_dict['PARM_BASE'] = self.p.getdir('PARM_BASE')

        return tc_stat_dict

    def run_all_times(self):
        """! Builds the call to the MET tool TC-STAT for all requested
             initialization times (init or valid).  Called from master_metplus

             Args:

             Returns:

        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Useful for logging
        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.info('Starting tc_stat_wrapper...')
        self.set_envs()
        if not self.config_lists_ok():
            self.logger.error('There is at least one <>_VAL/<>_NAME pair'
                              'requested in the MET tc-stat config file where'
                              'the size of the lists is not equal.  Please'
                              'check your MET tc-stat config file.')
            sys.exit(1)

        # Don't forget to create the output directory, as MET tc_stat will
        # not do this.
        util.mkdir_p(self.tc_stat_dict['OUTPUT_DIR'])

        # Since this is different from the other MET tools, we will build
        # the commands rather than use command builder's methods.
        match_points = str(self.tc_stat_dict['MATCH_POINTS'])

        # Create the name of the filtered file based on the job type
        job_type = self.tc_stat_dict['JOB_TYPE'].lower()
        filtered_filename = 'tc_' + job_type + '_job.tcst'

        filtered_output_file = os.path.join(self.tc_stat_dict['OUTPUT_DIR'],
                                            filtered_filename)
        if job_type == 'filter':
            tc_cmd_list = [self.tc_exe, " -job ", self.tc_stat_dict['JOB_TYPE'],
                           " -lookin ", self.tc_stat_dict['INPUT_DIR'],
                           " -dump_row ", filtered_output_file,
                           " -match_points ",
                           match_points.lower()
                           ]
        elif job_type == 'summary':
            tc_cmd_list = [self.tc_exe, " -job ", self.tc_stat_dict['JOB_TYPE'],
                           " -by ",
                           " -lookin ", self.tc_stat_dict['INPUT_DIR'],
                           " -dump_row ", filtered_output_file,
                           " -match_points ",
                           match_points.lower()
                           ]

        tc_cmd_str = ''.join(tc_cmd_list)

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

    def set_envs(self):
        """! Set the env variables based on settings in the METplus config
             files.

             Args:

             Returns:
                 none - sets environment variables


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
        if self.tc_stat_dict['AMODEL']:
            self.add_env_var('AMODEL', self.tc_stat_dict['AMODEL'])
        else:
            self.add_env_var('AMODEL', '[]')

        if self.tc_stat_dict['BMODEL']:
            self.add_env_var('BMODEL', self.tc_stat_dict['BMODEL'])
        else:
            self.add_env_var('BMODEL', '[]')

        if self.tc_stat_dict['DESC']:
            self.add_env_var('DESC', self.tc_stat_dict['DESC'])
        else:
            self.add_env_var('DESC', '[]')

        if self.tc_stat_dict['STORM_ID']:
            self.add_env_var('STORM_ID', self.tc_stat_dict['STORM_ID'])
        else:
            self.add_env_var('STORM_ID', '[]')

        if self.tc_stat_dict['BASIN']:
            self.add_env_var('BASIN', self.tc_stat_dict['BASIN'])
        else:
            self.add_env_var('BASIN', '[]')

        if self.tc_stat_dict['CYCLONE']:
            self.add_env_var('CYCLONE', self.tc_stat_dict['CYCLONE'])
        else:
            self.add_env_var('CYCLONE', '[]')

        if self.tc_stat_dict['STORM_NAME']:
            self.add_env_var('STORM_NAME', self.tc_stat_dict['STORM_NAME'])
        else:
            self.add_env_var('STORM_NAME', '[]')

        if self.tc_stat_dict['INIT_BEG']:
            self.add_env_var('INIT_BEG', self.tc_stat_dict['INIT_BEG'])
        else:
            self.add_env_var('INIT_BEG', '')

        if self.tc_stat_dict['INIT_END']:
            self.add_env_var('INIT_END', self.tc_stat_dict['INIT_END'])
        else:
            self.add_env_var('INIT_END', '')

        if self.tc_stat_dict['INIT_INCLUDE']:
            self.add_env_var('INIT_INCLUDE', self.tc_stat_dict['INIT_INCLUDE'])
        else:
            self.add_env_var('INIT_INCLUDE', '[]')

        if self.tc_stat_dict['INIT_EXCLUDE']:
            self.add_env_var('INIT_EXCLUDE', self.tc_stat_dict['INIT_EXCLUDE'])
        else:
            self.add_env_var('INIT_EXCLUDE', '[]')

        if self.tc_stat_dict['INIT_HOUR']:
            self.add_env_var('INIT_HOUR', self.tc_stat_dict['INIT_HOUR'])
        else:
            self.add_env_var('INIT_HOUR', '[]')

        if self.tc_stat_dict['VALID_BEG']:
            self.add_env_var('VALID_BEG', self.tc_stat_dict['VALID_BEG'])
        else:
            self.add_env_var('VALID_BEG', '')

        if self.tc_stat_dict['VALID_END']:
            self.add_env_var('VALID_END', self.tc_stat_dict['VALID_END'])
        else:
            self.add_env_var('VALID_END', '')

        if self.tc_stat_dict['VALID_INCLUDE']:
            self.add_env_var('VALID_INCLUDE',
                             self.tc_stat_dict['VALID_INCLUDE'])
        else:
            self.add_env_var('VALID_INCLUDE', '[]')

        if self.tc_stat_dict['VALID_EXCLUDE']:
            self.add_env_var('VALID_EXCLUDE',
                             self.tc_stat_dict['VALID_EXCLUDE'])
        else:
            self.add_env_var('VALID_EXCLUDE', '[]')

        if self.tc_stat_dict['VALID_HOUR']:
            self.add_env_var('VALID_HOUR', self.tc_stat_dict['VALID_HOUR'])
        else:
            self.add_env_var('VALID_HOUR', '[]')

        if self.tc_stat_dict['LEAD_REQ']:
            self.add_env_var('LEAD_REQ', self.tc_stat_dict['LEAD_REQ'])
        else:
            self.add_env_var('LEAD_REQ', '[]')

        if self.tc_stat_dict['LEAD']:
            self.add_env_var('LEAD', self.tc_stat_dict['LEAD'])
        else:
            self.add_env_var('LEAD', '[]')

        if self.tc_stat_dict['INIT_MASK']:
            self.add_env_var('INIT_MASK', self.tc_stat_dict['INIT_MASK'])
        else:
            self.add_env_var('INIT_MASK', '[]')

        if self.tc_stat_dict['TRACK_WATCH_WARN']:
            self.add_env_var('TRACK_WATCH_WARN',
                             self.tc_stat_dict['TRACK_WATCH_WARN'])
        else:
            self.add_env_var('TRACK_WATCH_WARN', '[]')

        if self.tc_stat_dict['COLUMN_THRESH_NAME']:
            self.add_env_var('COLUMN_THRESH_NAME',
                             self.tc_stat_dict['COLUMN_THRESH_NAME'])
        else:
            self.add_env_var('COLUMN_THRESH_NAME', '[]')

        if self.tc_stat_dict['COLUMN_THRESH_VAL']:
            self.add_env_var('COLUMN_THRESH_VAL',
                             self.tc_stat_dict['COLUMN_THRESH_VAL'])
        else:
            self.add_env_var('COLUMN_THRESH_VAL', '[]')

        if self.tc_stat_dict['COLUMN_STR_NAME']:
            self.add_env_var('COLUMN_STR_NAME',
                             self.tc_stat_dict['COLUMN_STR_NAME'])
        else:
            self.add_env_var('COLUMN_STR_NAME', '[]')

        if self.tc_stat_dict['COLUMN_STR_VAL']:
            self.add_env_var('COLUMN_STR_VAL',
                             self.tc_stat_dict['COLUMN_STR_VAL'])
        else:
            self.add_env_var('COLUMN_STR_VAL', '[]')

        if self.tc_stat_dict['INIT_THRESH_NAME']:
            self.add_env_var('INIT_THRESH_NAME',
                             self.tc_stat_dict['INIT_THRESH_NAME'])
        else:
            self.add_env_var('INIT_THRESH_NAME', '[]')

        if self.tc_stat_dict['INIT_THRESH_VAL']:
            self.add_env_var('INIT_THRESH_VAL',
                             self.tc_stat_dict['INIT_THRESH_VAL'])
        else:
            self.add_env_var('INIT_THRESH_VAL', '[]')

        if self.tc_stat_dict['INIT_STR_NAME']:
            self.add_env_var('INIT_STR_NAME',
                             self.tc_stat_dict['INIT_STR_NAME'])
        else:
            self.add_env_var('INIT_STR_NAME', '[]')

        if self.tc_stat_dict['INIT_STR_VAL']:
            self.add_env_var('INIT_STR_VAL', self.tc_stat_dict['INIT_STR_VAL'])
        else:
            self.add_env_var('INIT_STR_VAL', '[]')

        if self.tc_stat_dict['WATER_ONLY']:
            self.add_env_var('WATER_ONLY', self.tc_stat_dict['WATER_ONLY'])
        else:
            # Set to FALSE if not defined
            self.add_env_var('WATER_ONLY', 'FALSE')

        if self.tc_stat_dict['MATCH_POINTS']:
            self.add_env_var('MATCH_POINTS',
                             self.tc_stat_dict['MATCH_POINTS'])
        else:
            # Set to FALSE if not defined
            self.add_env_var('MATCH_POINTS', 'FALSE')

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

    def build_tc_stat(self, tc_stat_output_dir, cur_init, tile_dir,
                      filter_opts):
        """! Creates the call to MET tool TC-STAT to subset tc-pairs output
            based on the criteria specified in the feature relative
            use case parameter/config file.

            Args:
            @param tc_stat_output_dir:  The output directory where filtered
                                       results are saved.
            @param cur_init:  The initialization time
            @param tile_dir:  The input data directory (tc pair data to be
                              filtered)
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

        tc_cmd_list = [self.tc_exe, " -job filter ",
                       " -lookin ", tile_dir,
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

    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_stat',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_stat')
        produtil.log.postmsg('run_tc_stat is starting')

        # Read in the configuration object
        ###import config_launcher
        ###if len(sys.argv) == 3:
        ###    CONFIG = config_launcher.load_baseconfs(sys.argv[2])
        ###else:
        ###    CONFIG = config_launcher.load_baseconfs()

        CONFIG = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG.getdir('MET_BASE')

        TCS = TcStatWrapper(CONFIG, logger=None)
        # TCS.<call_some_method>

        #        util.gen_init_list(TCS.init_date_beg, TCS.init_date_end,
        #                           TCS.init_hour_inc, CONFIG.getstr('config',
        #                                                            'INIT_HOUR_END'))

        produtil.log.postmsg('run_tc_stat completed')

    except Exception as exception:
        produtil.log.jlogger.critical(
            'run_tc_stat failed: %s' % (str(exception),), exc_info=True)
        sys.exit(2)
