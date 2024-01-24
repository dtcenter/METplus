# @namespace UsageWrapper
# @brief Provides a default process for run_metplus.py.  Indicates what
# processes are currently available.
# @endcode#

from . import CommandBuilder
from ..util import LOWER_TO_WRAPPER_NAME


class UsageWrapper(CommandBuilder):
    """! A default process, prints out usage when nothing is defined in
         the PROCESS_LIST
    """
    def __init__(self, config, instance=None):
        self.app_name = 'Usage'
        super().__init__(config, instance=instance)
        # get unique list of processes
        self.available_processes = list(set(val for val in LOWER_TO_WRAPPER_NAME.values()))
        self.available_processes.sort()

    def run_all_times(self):
        print("USAGE: This text is displayed when [config] PROCESS_LIST = Usage.\n"
              "Pass in a configuration file (with -c or --config) that overrides [config] PROCESS_LIST "
              "to run other processes. For example:\n\n"
              "run_metplus.py -c parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf\n\nor\n\n"
              "run_metplus.py --config parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf\n\n"
              "Possible processes: ")
        for process in self.available_processes:
            print("  - {}".format(process))
