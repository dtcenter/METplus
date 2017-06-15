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
    self.inaddons = []
    
  def add_input_file(self, filename, addon):
#    self.infiles.append(filename+" "+str(addon))
    self.infiles.append(filename)
    self.inaddons.append(str(addon))    

  # NOTE: Assumes YYYYMMDD sub dir 
  def get_lowest_forecast_at_valid(self, valid_time, dtype):
    out_file = ""
    day_before = self.shift_time(valid_time, -24)

    # TODO: do we need to make sure to check if dir exists first
    #   , or will glob handle?
    # get all files in yesterday directory, get valid time from init/fcst
    # NOTE: This will only apply to forecasts up to 48  hours
    #  If more is needed, will need to add parameter to specify number of
    #  days to look back
    files = sorted(glob.glob("{:s}/{:s}/*".format(self.input_dir,str(day_before)[0:8])))
    for fpath in files:
      f = os.path.join(str(day_before)[0:8],os.path.basename(fpath))
      native_template = self.p.getstr('filename_templates', dtype+'_NATIVE_TEMPLATE')
      # TODO: hack until we switch over to Julie's string parser
#      fcst = self.pull_forecast(f, native_template)
      fcst = int(os.path.basename(fpath)[21:23])
      if fcst is None:
        print("ERROR: Could not pull forecast leas from f")
        exit
      init = self.pull_template(os.path.basename(native_template[0:-8]), os.path.basename(f[0:-7]), "%Y%m%d%H")
      v = self.shift_time(init,fcst)
      if v == valid_time:
        out_file = fpath

    files = sorted(glob.glob("{:s}/{:s}/*".format(self.input_dir,str(valid_time)[0:8])))
    for fpath in files:
      print("foun:"+fpath)
      # hack until we switch over to Julie's string parser
#      fcst = self.pull_forecast(f, native_template)
      fcst = os.path.basename(fpath)[20:23]
      print("fcst is:" + fcst)
      if fcst is None:
        print("ERROR: Could not pull forecast leas from f")
        exit
      init = self.pull_template(os.path.basename(native_template), os.path.basename(f), "%Y%m%d%H")
      v = self.shift_time(fcst, init)
      print(v+" vs. " +valid_time)
      if v == valid_time:
        out_file = fpath        
    return out_file


  
  def find_closest_before(self, dir, time, template):
    out_file = ""
    day_before = self.shift_time(time, -24)
    files = sorted(glob.glob("{:s}/*{:s}*".format(dir,str(day_before)[0:8])))
    for f in files:
      ftime = self.pull_template(template,os.path.basename(f),"%Y%m%d%H")
      if ftime < time:
        out_file = f

    files = sorted(glob.glob("{:s}/*{:s}*".format(dir,str(time)[0:8])))
    for f in files:
      ftime = self.pull_template(template,os.path.basename(f),"%Y%m%d%H")
      if ftime < time:
        out_file = f        
    return out_file

  def get_accumulation(self, valid_time, accum, ob_type, is_forecast=False):
    file_template = self.p.getstr('filename_templates',ob_type+"_NATIVE_TEMPLATE")
    
    if self.input_dir == "":
      (self.logger).error(self.app_name+": Must set data dir to run get_accumulation")
      exit
    self.add_arg("-add")

    if self.p.getbool('config',ob_type+'_IS_DAILY_FILE') == True:
      # start at valid_time
      search_time = valid_time
      # loop accum times
      data_interval = self.p.getint('config',ob_type+'_DATA_INTERVAL')*3600
      for i in range(0, accum, data_interval):
        search_time = self.shift_time(valid_time, -i)
        # find closest file before time
        f = self.find_closest_before(self.input_dir, search_time, file_template)
        if f == "":
          continue
        # build level info string
        file_time = datetime.datetime.strptime(os.path.basename(f),file_template )
        v_time = datetime.datetime.strptime(search_time, "%Y%m%d%H")
        diff = v_time - file_time
        lead = int((diff.days*24) / (data_interval/3600))
        lead += int( (v_time - file_time).seconds/data_interval) - 1
        addon = "'name=\""+self.p.getstr('config',ob_type+'_'+str(accum)+'_FIELD_NAME')+"\"; level=\"("+str(lead)+",*,*)\";'"
        if os.path.splitext(f)[1] == '.grd':
          f = os.path.splitext(f)[0]+'.nc'
        self.add_input_file(f,addon)
    else: # not a daily file
      # if field that corresponds to search accumulation exists in the files,
      #  check the file with valid time before moving backwards in time
      if self.p.has_option('config', ob_type+'_'+str(accum)+'_FIELD_NAME'):
        search_file = os.path.join(self.input_dir,self.fill_template(file_template, valid_time, accum))
        if os.path.exists(search_file):
          data_type = self.p.getstr('config',ob_type+'_NATIVE_DATA_TYPE')  
          if data_type == "GRIB":
            addon = accum
          elif data_type == "NETCDF":          
            addon = "'name=\""+self.p.getstr('config',ob_type+'_'+str(accum)+'_FIELD_NAME') +"\"; level=\"(0,*,*)\";'"
          if os.path.splitext(search_file)[1] == '.grd':            
            search_file = os.path.splitext(search_file)[0]+'.nc'            
          self.add_input_file(search_file,addon)
          self.set_output_dir(self.outdir)
          return
      
      start_time = valid_time
      last_time = self.shift_time(valid_time, -(accum-1) )
      total_accum = accum
      search_accum = total_accum
      # loop backwards in time until you have a full set of accumulation
      while last_time <= start_time:
        if is_forecast:
          f = self.get_lowest_forecast_at_valid(start_time,ob_type)
          if f == "":
            break
          # TODO: assumes 1hr accum in these files for now
          addon = "'name=\""+self.p.getstr('config',ob_type+'_'+str(1)+'_FIELD_NAME') +"\"; level=\"(0,*,*)\";'"
          if os.path.splitext(f)[1] == '.grd':
            f = os.path.splitext(f)[0]+'.nc'
          self.add_input_file(f,addon)
          start_time = self.shift_time(start_time, -1)
          search_accum -= 1
        else: # not looking for forecast files
          # get all files of valid_time (all accums)
#          print("Searching: "+"{:s}/{:s}/*{:s}*".format(self.input_dir,start_time[0:8],start_time))
          files = sorted(glob.glob("{:s}/{:s}/*{:s}*".format(self.input_dir,start_time[0:8],start_time)))
          (self.logger).debug(self.app_name+": Found " + str(len(files)) + " files")
          for f in files:
            (self.logger).debug(self.app_name+": File: " + f)
          # look for biggest accum that fits search
          while search_accum > 0:
            search_file = os.path.join(self.input_dir,self.fill_template(file_template, start_time, search_accum))
            f = None
            for file in files:
              if file == search_file:
                f = file
                break
            # if found a file, add it to input list with info
            if not f is None:
              addon = ""
              data_type = self.p.getstr('config',ob_type+'_NATIVE_DATA_TYPE')
              if data_type == "GRIB":
                addon = search_accum
              elif data_type == "NETCDF":
                addon = "'name=\""+self.p.getstr('config',ob_type+'_'+str(search_accum)+'_FIELD_NAME') +"\"; level=\"(0,*,*)\";'"
                # TODO: assumes non Gempak NC data has .nc extension
                if os.path.splitext(f)[1] == '.grd':                
                  f = os.path.splitext(f)[0]+'.nc'
              self.add_input_file(f,addon)
              start_time = self.shift_time(start_time, -search_accum)
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
    # TODO: Don't require 'h' character after accum
    # do we even need this?
    outname = re.sub("[0-9]{2}h", str(accum).zfill(2)+"h", f.rstrip())
    (self.logger).debug(outname)
    self.set_output_dir(self.outdir)


  def get_command(self):
    if self.app_path is None:
      (self.logger).error("No app path specified. You must use a subclass")
      return None

    cmd = self.app_path + " "
    for a in self.args:
      cmd += a + " "

    if len(self.infiles) == 0:
      (self.logger).error("No input filenames specified")
      return None

    for idx,f in enumerate(self.infiles):
      cmd += f + " " + self.inaddons[idx] + " "

    if self.param != "":
      cmd += self.param + " "
      
    if self.outfile == "":
      (self.logger).error("No output filename specified")
      return None

    if self.outdir == "":
      (self.logger).error("No output directory specified")
      return None

    cmd += os.path.join(self.outdir,self.outfile)
    return cmd

