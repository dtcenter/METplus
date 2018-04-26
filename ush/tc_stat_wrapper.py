#!/usr/bin/env python

"""!
Program Name: TcStatWrapper.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Subset tc_pairs data using MET tool TC-STAT for use in
          ExtractTiles.py or series analysis
          (via SeriesByLead.py or series_by_init.py)
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
#
#
#
#

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
        self.logger=logger
        if self.logger is None:
            self.logger = util.get_logger(self.p,sublog='TcStat')

        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/tc_stat')
        self.app_name = os.path.basename(self.app_path)
        self.tc_exe = self.app_path

        # TODO after testing, remove lines below that have ###
        ###met_install_dir = self.p.getdir('MET_INSTALL_DIR')
        ###self.tc_exe = os.path.join(met_install_dir, 'bin/tc_stat')
#        self.init_date_beg = p.getstr('config', 'INIT_DATE_BEG')
#        self.init_date_end = p.getstr('config', 'INIT_DATE_END')
#        self.init_hour_inc = p.getint('config', 'INIT_HOUR_INC')
        ###self.logger = util.get_logger(p)
        ###self.config = p

        self.logger.info("Initialized TcStatWrapper")

    def build_tc_stat(self, series_output_dir, cur_init, tile_dir,
                      filter_opts):
        """! Create the call to MET tool TC-STAT to subset tc-pairs output
            based on the criteria specified in the parameter/config file.
            Args:
            @param series_output_dir:  The output directory where filtered
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

        util.mkdir_p(series_output_dir)
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(series_output_dir, cur_init,
                                   filter_filename)
        filter_path = os.path.join(series_output_dir, cur_init)
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
            #tc_cmd = batchexe('sh')['-c', tc_cmd_str].err2out()
            #checkrun(tc_cmd)
            (ret, cmd) = self.cmdrunner.run_cmd(tc_cmd_str,app_name=self.app_name)
            if not ret == 0:
                raise ExitStatusException('%s: non-zero exit status'%(repr(cmd),),ret)
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
        #TCS.<call_some_method>

#        util.gen_init_list(TCS.init_date_beg, TCS.init_date_end,
#                           TCS.init_hour_inc, CONFIG.getstr('config',
#                                                            'INIT_HOUR_END'))

        produtil.log.postmsg('run_tc_stat completed')

    except Exception as exception:
        produtil.log.jlogger.critical(
            'run_tc_stat failed: %s' % (str(exception),), exc_info=True)
        sys.exit(2)
