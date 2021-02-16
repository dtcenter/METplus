# @namespace UsageWrapper
# @brief Provides a default process for master_metplus.py.  Indicates what
# processes are currently available.
# @endcode#

from . import CommandBuilder
from ..util import met_util

class UsageWrapper(CommandBuilder):
    """! A default process, prints out usage when nothing is defined in
         the PROCESS_LIST of the parm/metplus_config/metplus_runtime.conf
         and no lower level config files are included.
    """
    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'Usage'
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)
        # get unique list of processes from met_util
        self.available_processes = list(set(val for val in met_util.LOWER_TO_WRAPPER_NAME.values()))
        self.available_processes.sort()

    def run_all_times(self):
        print("USAGE: This text is displayed when [config] PROCESS_LIST = Usage.\n"
              "Pass in a configuration file (with -c or --config) that overrides [config] PROCESS_LIST "
              "to run other processes. For example:\n\n"
              "master_metplus.py -c parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf\n\nor\n\n"
              "master_metplus.py --config parm/use_cases/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf\n\n"
              "Possible processes: ")
        for process in self.available_processes:
            print("  - {}".format(process))
