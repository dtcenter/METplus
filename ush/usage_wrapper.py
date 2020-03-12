#!/usr/bin/env python

import metplus_check_python_version

from command_builder import CommandBuilder
from met_util import LOWER_TO_WRAPPER_NAME

# @namespace UsageWrapper
# @brief Provides a default process for master_metplus.py.  Indicates what
# processes are currently available.
# @endcode#


class UsageWrapper(CommandBuilder):
    """! A default process, prints out usage when nothing is defined in
         the PROCESS_LIST of the parm/metplus_config/metplus_runtime.conf
         and no lower level config files are included.
    """
    def __init__(self, p, logger):
        self.app_name = 'Usage'
        super().__init__(p, logger)
        self.logger = logger
        # get unique list of processes from met_util
        self.available_processes = list(set(val for val in LOWER_TO_WRAPPER_NAME.values()))
        self.available_processes.sort()

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
