#!/usr/bin/env python

'''
Program Name: CG_GempakToCF.py
Contact(s): George McCabe
Abstract: Runs GempakToCF
History Log:  Initial version 
Usage: CG_GempakToCF.py
Parameters: None
Input Files: 
Output Files: 
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division )

import constants_pdef as P
import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
from CommandGen import CommandGen

class CG_GempakToCF(CommandGen):
  
  def __init__(self, p, logger):
    super(CG_GempakToCF, self).__init__(p, logger)
    self.app_path = self.p.getstr('exe','GEMPAKTOCF')
    self.app_name = os.path.basename(self.app_path)
    self.class_path = self.p.getstr('exe','GEMPAKTOCF_CLASSPATH')

    
  def get_command(self):
    cmd = "java -classpath " + self.class_path + " " + self.app_path + " "

    if len(self.infiles) != 1:
      (self.logger).error(self.app_name+": Only 1 input file can be selected")
      return None

    for f in self.infiles:
      cmd += f + " "
      
    if self.outfile == "":
      (self.logger).error(self.app_name+": No output file specified")
      return None

    cmd += self.outfile
    return cmd
