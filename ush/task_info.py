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


class TaskInfo:
    __metaclass__ = ABCMeta

    def __init__(self):
        '''Retrieve parameters from corresponding param file'''
        self.init_time = -1
        self.valid_time = -1
        self.lead = -1
        

    def getValidTime(self):
      if self.valid_time is not -1:
          return self.valid_time
      if self.init_time is not -1 and self.lead is not -1:
          return util.shift_time(self.init_time, self.lead)
      print("ERROR: Could not compute valid_time")
      exit()

  
    def getInitTime(self):
      if self.init_time is not -1:
          return self.init_time
      if self.valid_time is not -1 and self.lead is not -1:
          return util.shift_time(self.valid_time, -self.lead)
      return -1

    def getLeadTime(self):
        return self.lead
