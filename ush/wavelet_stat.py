#!/usr/bin/env python

'''
Program Name: wavelet_stat_wrapper.py
Contact(s): George McCabe
Abstract: Runs wavelet_stat
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import os
from compare_gridded_wrapper import CompareGriddedWrapper

'''!@namespace WaveletStatWrapper
@brief Wraps the MET tool wavelet_stat to compare gridded datasets
@endcode
'''
class WaveletStatWrapper(CompareGriddedWrapper):
    '''!Wraps the MET tool wavelet_stat to compare gridded datasets
    '''
    def __init__(self, p, logger):
        super(WaveletStatWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/wavelet_stat')
        self.app_name = os.path.basename(self.app_path)
