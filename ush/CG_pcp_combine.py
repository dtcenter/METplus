#!/usr/bin/env python

'''
Program Name: CG_pcp_combine.py
Contact(s): George McCabe
Abstract: Runs pcp_combine to merge multiple forecast files
History Log:  Initial version 
Usage: CG_pcp_combine.py
Parameters: None
Input Files: grib2 files
Output Files: pcp_combine files
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division )

import produtil.setup
from produtil.run import batchexe, run, checkrun
import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
import glob
import datetime

from CommandGen import CommandGen

class CG_pcp_combine(CommandGen):
  
  def __init__(self, p, logger):
    super(CG_pcp_combine, self).__init__(p, logger)
    self.app_path = self.p.getstr('exe','PCP_COMBINE')
    self.app_name = os.path.basename(self.app_path)

  def add_input_file(self, filename, interval):
    self.infiles.append(filename+" "+str(interval))
    
  def search_for_accumulation(self, files, accum):
    for f in files:
      if int(f[-3:-1]) == accum:
        return f
    return None

  # TODO: needs more testing!
  def find_closest_before(self, dir, time, template):
    out_file = ""
    day_before = self.shift_time(time, 24)
    files = glob.glob("{:s}/*{:s}*".format(dir,str(day_before)[0:8],str(day_before)[0:8]))
    for f in files:
      ftime = self.pull_template(template,os.path.basename(f),"%Y%m%d%H")
      if ftime < time:
        out_file = f

    files = glob.glob("{:s}/*{:s}*".format(dir,str(time)[0:8],str(time)[0:8]))
    for f in files:
      ftime = self.pull_template(template,os.path.basename(f),"%Y%m%d%H")
      if ftime < time:
        out_file = f        
    return out_file

  def get_accumulation(self, valid_time, accum, ob_type):
    if self.input_dir == "":
      (self.logger).error(self.app_name+": Must set data dir to run get_accumulation")
      exit
    self.add_arg("-add")
    (self.logger).debug(self.app_name+": Valid time: " + valid_time + " accum: " + str(accum) + " ob_type: " + ob_type)

    # TODO: HOW DO I DESCRIBE THE DIFFERENCE OF THESE SETUPS WITHOUT REFERRING TO OB_TYPE
    if ob_type == "WPCSNOW":
      # start at valid_time
      search_time = valid_time
      # loop accum times
      for i in range(0, accum, 1):
        search_time = self.shift_time(valid_time, -i)
        # find closest file before time
        (self.logger).debug(self.app_name+": SEARCH TIME: " + search_time)
        f = self.find_closest_before(self.input_dir, search_time, self.p.getstr('config','WPCSNOW_NATIVE_TEMPLATE'))
        if f == "":
          continue
        (self.logger).debug("FILE: " + f)
        # build level info string
        file_time = datetime.datetime.strptime(os.path.basename(f),self.p.getstr('config','WPCSNOW_NATIVE_TEMPLATE') )
        v_time = datetime.datetime.strptime(search_time, "%Y%m%d%H")
        lead = int(((v_time - file_time).seconds/3600) - 1)
        addon = "'name=\"W01I_NONE\"; level=\"("+str(lead)+",*,*)\";'"
        (self.logger).debug("ADDING: " + f + " " + addon)
        self.add_input_file(f,addon)
    else:
      start_time = self.shift_time(valid_time, -(accum-1) )
      total_accum = accum
      search_accum = total_accum
      while start_time <= valid_time:
        files = glob.glob("{:s}/{:s}/*{:s}*".format(self.input_dir,start_time[0:8],start_time))
        (self.logger).debug(self.app_name+": Found " + str(len(files)) + " files")
        for f in files:
          (self.logger).debug(self.app_name+": File: " + f)

        while search_accum > 0:
          f = self.search_for_accumulation(files,search_accum)
          if not f is None:
            self.add_input_file(f,search_accum)
            start_time = self.shift_time(start_time, search_accum)
            total_accum -= search_accum
            search_accum = total_accum
            break
          search_accum -= 1
             
        if total_accum == 0:
          break
             
        if search_accum == 0:
          (self.logger).warning(self.app_name+": Could not find files to compute accumulation")
          return None
    (self.logger).debug("FILE: " + f)
    outname = re.sub("[0-9]{2}h", str(accum).zfill(2)+"h", f.rstrip())
    (self.logger).debug(outname)
    self.set_output_dir(self.outdir)

  
