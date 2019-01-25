#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import produtil.setup
from command_builder import CommandBuilder
import config_metplus


## @namespace UsageWrapper
# @brief Provides a default process for master_metplus.py.  Indicates what
# processes are currently available.
# Call as follows:
# @code{.sh}
# usage_wrapper.py [-c /path/to/user.template.conf]
# @endcode#

class UsageWrapper(CommandBuilder):
    """! A default process, prints out usage when nothing is defined in
         the PROCESS_LIST of the parm/metplus_config/metplus_runtime.conf
         and no lower level config files are included.
    """
    def __init__(self, p, logger):
        super(UsageWrapper, self).__init__(p, logger)
        self.logger = logger
        self.available_processes = ['TcPairs', 'ExtractTiles', 'SeriesByInit',
                                    'SeriesByLead', 'PcpCombine',
                                    'RegridDataPlane', 'GridStat',
                                    'Mode', 'MTD', 'RegridDataPlane',
                                    'CyclonePlotter', 'TCMPRPlotter',
                                    'PB2NC', 'PointStat']

    def run_all_times(self):
        print("USAGE:\n  This is a default process, please indicate more " +
              " specific processes in the PROCESS_LIST variable in one " +
              "or more of the following configuration files:\n " +
              "-parm/metplus_config/metplus_runtime.conf\n " +
              "-parm/metplus_use_cases/<usecase_name>/<usecase_name>.conf\n " +
              "-parm/metplus_use_cases/<usecase_name>/" +
              "examples/<example_name>.conf \n")
        print("Currently available processes are: ")
        for process in self.available_processes:
            print("  - {}".format(process))


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='SeriesByLeadWrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='SeriesByLeadWrapper')
        produtil.log.postmsg('SeriesByLeadWrapper is starting')

        # Read in the configuration object CONFIG
        CONFIG = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG.getdir('MET_BASE')

        UW = UsageWrapper(CONFIG, logger=None)
        UW.run_all_times()

        produtil.log.postmsg('series analysis by lead time completed')
    except Exception as exc:
        produtil.log.jlogger.critical(
            'SeriesByLeadWrapper failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)
