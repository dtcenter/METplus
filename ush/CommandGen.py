#!/usr/bin/env python

'''
Program Name: CommandGen.py
Contact(s): George McCabe
Abstract: 
History Log:  Initial version 
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
'''

from __future__ import (print_function, division )

import os
import sys
import re
import csv
import subprocess
import datetime

from abc import ABCMeta

class CommandGen:
  __metaclass__ = ABCMeta
  
  def __init__(self, p, logger):
    # Retrieve parameters from corresponding param file
    self.p = p
    self.logger = logger
    self.debug = False
    self.app_name = None
    self.app_path = None    
    self.args = []
    self.input_dir = ""
    self.infiles = []
    self.outdir = ""
    self.outfile = ""
    self.param = ""
    self.env = os.environ.copy()

  def set_debug(self, debug):
    self.debug = debug

  def add_arg(self, arg):
    self.args.append(arg)
    
  def add_input_file(self, filename):
    self.infiles.append(filename)

  def set_input_dir(self, d):
    self.input_dir = d
    
  def set_output_path(self, outpath):
    self.outfile = os.path.basename(outpath)
    self.outdir = os.path.dirname(outpath)

  def get_output_path(self):
    return os.path.join(self.outdir,self.outfile)
            
  def set_output_filename(self, outfile):
    self.outfile = outfile

  def set_output_dir(self, outdir):
    self.outdir = outdir
    
  def set_param_file(self, param):
    self.param = param

  def clear_command(self):
    self.args = []
    self.infiles = []
    self.outfile = ""
    self.param = ""

  def add_env_var(self, key,  name):
    self.env[key] = name
    
  def get_env(self):
    return self.env

  def print_env(self):
    for x in self.env:
      (self.logger).debug(x,":",self.env[x])

  def print_env_item(self, item):
      # TODO: Fix logger call here
   (self.logger).debug(item+":"+self.env[item])
#    print(item,":",self.env[item]) 

  def fill_template(self, template, d, lead):
    out = template
    out = out.replace("%FFF", str(lead).zfill(3))
    out = out.replace("%FF", str(lead).zfill(2))
    t = datetime.datetime.strptime(d, "%Y%m%d%H")
    out = t.strftime(out)
    return out

  def pull_template(self, template, str, new_template):
    t = datetime.datetime.strptime(str, template)
    return t.strftime(new_template)

  def shift_time(self, time, shift):
    return (datetime.datetime.strptime(time, "%Y%m%d%H") + datetime.timedelta(hours=shift)).strftime("%Y%m%d%H")
                   
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

    for f in self.infiles:
      cmd += f + " "

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


  def run(self):
    cmd = self.get_command()
    if cmd is None:
      return
    (self.logger).info("RUNNING: " + cmd)
    process = subprocess.Popen(cmd, env=self.env, shell=True)
    process.wait()
#    os.system(cmd)
