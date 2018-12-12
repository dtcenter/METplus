#!/usr/bin/env python

'''
Program Name: task_info.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
'''

from __future__ import (print_function, division)

import os
import sys
import re
import csv
import subprocess
import datetime
import string_template_substitution as sts
import met_util as util

from abc import ABCMeta

'''!@namespace TaskInfo
@brief Utility to handle timing in MET+ wrappers
@code{.sh}
Cannot be called directly. These are helper functions
to be used in other MET+ wrappers
@endcode
'''
class TaskInfo:
    __metaclass__ = ABCMeta
    """!Utility to handle timing in MET+ wrappers
    """
    def __init__(self):
        """!Retrieve parameters from corresponding param file
        """
        self.clear()

    def clear(self):
        """!Clear out all values
        """
        self.init_time = -1
        self.valid_time = -1
        self.lead = -1
        

    def getValidTime(self):
        """! returns valid time or calculates it from init and lead time
           @rtype string
           @return Returns the time in YYYYMMDDHHMM format
        """
        if self.valid_time is not -1:
            return self.valid_time
        if self.init_time is not -1 and self.lead is not -1:
            return util.shift_time(self.init_time, self.lead)
        print("ERROR: Could not compute valid_time")
        exit()

  
    def getInitTime(self):
        """! returns init time or calculates it from valid and lead time
           @rtype string
           @return Returns the time in YYYYMMDDHHMM format
        """
        if self.init_time is not -1:
            return self.init_time
        if self.valid_time is not -1 and self.lead is not -1:
            return util.shift_time(self.valid_time, -self.lead)
        return -1

    def getLeadTime(self):
        """! returns the forecast lead
           @rtype int
           @return Returns the forecast lead time
        """
        return self.lead
