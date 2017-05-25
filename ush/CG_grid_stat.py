#!/usr/bin/env python

'''
Program Name: CG_grid_stat.py
Contact(s): George McCabe
Abstract: 
History Log:  Initial version 
Usage: CG_grid_stat.py
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
class CG_grid_stat(CommandGen):
  
  def __init__(self, p, logger):
    super(CG_grid_stat, self).__init__(p, logger)
#    self.app_path = self.p.opt['GRID_STAT']
    self.app_path = self.p.getstr('exe','GRID_STAT')
    self.app_name = os.path.basename(self.app_path)

  def set_output_dir(self, outdir):
    self.outdir = "-outdir "+outdir
    
  def get_command(self):
    if self.app_path is None:
      (self.logger).error(self.app_name+": No app path specified. You must use a subclass")
      return None

    cmd = self.app_path + " "
    for a in self.args:
      cmd += a + " "

    if len(self.infiles) == 0:
      (self.logger).error(self.app_name+": No input filenames specified")
      return None

    for f in self.infiles:
      cmd += f + " "

    if self.param != "":
      cmd += self.param + " "
      
    if self.outdir == "":
      (self.logger).error(self.app_name+": No output directory specified")
      return None

    cmd += self.outdir
    return cmd
