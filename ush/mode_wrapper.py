#!/usr/bin/env python

'''
Program Name: mode_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode
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

class ModeWrapper(CompareGriddedWrapper):

    def __init__(self, p, logger):
        super(ModeWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/mode')
        self.app_name = os.path.basename(self.app_path)


if __name__ == "__main__":
    util.run_stand_alone("mode_wrapper", "Mode")
