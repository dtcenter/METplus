#!/usr/bin/env python

"""
Program Name: wavelet_stat_wrapper.py
Contact(s): George McCabe
Abstract: Runs wavelet_stat
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import met_util as util
from metplus_wrappers.compare_gridded_wrapper import CompareGriddedWrapper

'''!@namespace WaveletStatWrapper
@brief Wraps the MET tool wavelet_stat to compare gridded datasets
@endcode
'''


class WaveletStatWrapper(CompareGriddedWrapper):
    """"!Wraps the MET tool wavelet_stat to compare gridded datasets
    """
    def __init__(self, p, logger):
        super().__init__(p, logger)
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin/wavelet_stat')
        self.app_name = os.path.basename(self.app_path)


if __name__ == "__main__":
        util.run_stand_alone("wavelet_stat_wrapper", "WaveletStat")
