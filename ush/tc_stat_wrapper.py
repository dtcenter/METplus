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
from produtil.run import batchexe
from produtil.run import checkrun
import met_util as util

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


class TcStatWrapper(object):
    """! Wrapper for the MET tool, tc_stat, which is used to filter tropical
         cyclone pair data.
    """
    def __init__(self, p):
        met_build_base = p.getdir('MET_BUILD_BASE')
        # self.tc_exe = p.getexe('TC_STAT')
        self.tc_exe = os.path.join(met_build_base, 'bin/tc_stat')
#        self.init_date_beg = p.getstr('config', 'INIT_DATE_BEG')
#        self.init_date_end = p.getstr('config', 'INIT_DATE_END')
#        self.init_hour_inc = p.getint('config', 'INIT_HOUR_INC')
        self.logger = util.get_logger(p)
        self.config = p

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

        # Make call to tc_stat, capturing any stderr and stdout to the MET
        #  Plus log.
        try:
            tc_cmd = batchexe('sh')['-c', tc_cmd_str].err2out()
            checkrun(tc_cmd)
        except produtil.run.ExitStatusException as ese:
            msg = ("ERROR| " + cur_filename + ":" + cur_function +
                   " from calling MET TC-STAT with command:" +
                   tc_cmd.to_shell())
            self.logger.error(msg)
            self.logger.error(ese)


if __name__ == "__main__":

    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_stat',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_stat')
        produtil.log.postmsg('run_tc_stat is starting')

        # Read in the configuration object p
        import config_launcher
        if len(sys.argv) == 3:
            CONFIG = config_launcher.load_baseconfs(sys.argv[2])
        else:
            CONFIG = config_launcher.load_baseconfs()

        TCS = TcStatWrapper(CONFIG)

        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG.getdir('MET_BASE')

#        util.gen_init_list(TCS.init_date_beg, TCS.init_date_end,
#                           TCS.init_hour_inc, CONFIG.getstr('config',
#                                                            'INIT_HOUR_END'))

        produtil.log.postmsg('run_tc_stat completed')

    except Exception as exception:
        produtil.log.jlogger.critical(
            'run_tc_stat failed: %s' % (str(exception),), exc_info=True)
        sys.exit(2)
