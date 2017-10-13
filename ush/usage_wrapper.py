#!/usr/bin/env python
from __future__ import print_function


## @namespace UsageWrapper
# @brief Provides a default process for master_metplus.py.  Indicates what
# processes are currently available.
# Call as follows:
# @code{.sh}
# usage_wrapper.py [-c /path/to/user.template.conf]
# @endcode#

class UsageWrapper(object):
    """! A default process, prints out usage when nothing is defined in
         the PROCESS_LIST of the parm/metplus_config/metplus_runtime.conf
         and no lower level config files are included.
    """
    def __init__(self):
        self.available_processes = ['TcPairs', 'ExtractTiles', 'SeriesByInit',
                                    'SeriesByLead', 'PcpCombine',
                                    'RegridDataPlane',
                                    'GridStat', 'Mode', 'RegridDataPlane']

    def main(self):
        print("This is a default process, please indicate more specific " +
              "processes in the PROCESS_LIST variable in one of the " +
              "following configuration files:\n " +
              "-parm/metplus_config/metplus_runtime.conf\n " +
              "-parm/metplus_use_cases/<usecase_name>/<usecase_name>.conf\n " +
              "-parm/metplus_use_cases/<usecase_name>/" +
              "examples/<example_name>.conf \n")
        print("Currently available processes are: ")
        for process in self.available_processes:
            print("  - {}".format(process))


if __name__ == "__main__":
    uw = UsageWrapper()
    uw.main()
