#!/usr/bin/env python

'''
Program Name: CG_regrid_data_plane.py
Contact(s): George McCabe
Abstract: Runs regrid_data_plane
History Log:  Initial version 
Usage: CG_regrid_data_plane.py
Parameters: None
Input Files: nc files
Output Files: nc files
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

class CG_regrid_data_plane(CommandGen):
  
  def __init__(self, p, logger):
    super(CG_regrid_data_plane, self).__init__(p, logger)
    self.app_path = self.p.getstr('exe','REGRID_DATA_PLANE_EXE')
    self.app_name = os.path.basename(self.app_path)
