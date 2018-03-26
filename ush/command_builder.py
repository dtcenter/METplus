#!/usr/bin/env python

'''
Program Name: CommandBuilder.py
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
import time
import subprocess
import datetime
import calendar
import string_template_substitution as sts
import met_util as util

from produtil.run import batchexe
from produtil.run import checkrun

from abc import ABCMeta


class CommandBuilder:
    __metaclass__ = ABCMeta

    def __init__(self, p, logger):
        '''Retrieve parameters from corresponding param file'''
        self.p = p
        self.logger = logger
        self.debug = False
        self.app_name = None
        self.app_path = None
        self.env = os.environ.copy()        
        self.clear()

    def clear(self):
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""


    def set_debug(self, debug):
        self.debug = debug

    def add_arg(self, arg):
        self.args.append(arg)

    def add_input_file(self, filename):
        self.infiles.append(filename)

    def get_input_files(self):
        return self.infiles

    def set_input_dir(self, d):
        self.input_dir = d

    def set_output_path(self, outpath):
        '''Split path into directory and filename then save both'''
        self.outfile = os.path.basename(outpath)
        self.outdir = os.path.dirname(outpath)

    def get_output_path(self):
        '''Combine output directory and filename then return result'''
        return os.path.join(self.outdir, self.outfile)

    def set_output_filename(self, outfile):
        self.outfile = outfile

    def set_output_dir(self, outdir):
        self.outdir = outdir

    def set_param_file(self, param):
        self.param = param

    def add_env_var(self, key,  name):
        self.env[key] = name

    def get_env(self):
        return self.env

    def print_env(self):
        '''Print all environment variables set for this application'''        
        for x in self.env:
            self.logger.debug(x, "=", self.env[x])

    def print_env_copy(self, vars):
        '''Print list of environment variables that can be easily \
        copied into terminal'''
        out = ""
        for v in vars:
            if self.env[v].find('"') != -1:
                next = 'export '+v+'="'+self.env[v].replace('"', '\\"')+'"'
            else:
                next = 'export '+v+'='+self.env[v]
            out += next+'; '
        self.logger.debug(out)

    def print_env_item(self, item):
        # TODO: Fix logger call here
        (self.logger).debug(item+"="+self.env[item])
        #    print(item,":",self.env[item])

    def get_command(self):
        '''Build command to run from arguments'''
        if self.app_path is None:
            (self.logger).error("No app path specified. "\
                                "You must use a subclass")
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

        cmd += os.path.join(self.outdir, self.outfile)
        return cmd

    def build(self):
        '''Build and run command'''
        cmd = self.get_command()
        if cmd is None:
            return
        (self.logger).info("RUNNING: " + cmd)
        process = subprocess.Popen(cmd, env=self.env, shell=True)
        process.wait()


    def run_all_times(self):
        use_init = p.getbool('config', 'LOOP_BY_INIT')
        if use_init:
            time_format = p.getstr('config', 'INIT_TIME_FMT')
            start_t = p.getstr('config', 'INIT_BEG')
            end_t = p.getstr('config', 'INIT_END')
            time_interval = p.getint('config', 'INIT_INC')
        else:
            time_format = p.getstr('config', 'VALID_TIME_FMT')
            start_t = p.getstr('config', 'VALID_BEG')
            end_t = p.getstr('config', 'VALID_END')
            time_interval = p.getint('config', 'VALID_INC')
        
        if time_interval < 60:
            print("ERROR: time_interval parameter must be greater than 60 seconds")
            exit(1)
        
        loop_time = calendar.timegm(time.strptime(start_t, time_format))
        end_time = calendar.timegm(time.strptime(end_t, time_format))

        while loop_time <= end_time:
            run_time = time.strftime("%Y%m%d%H%M", time.gmtime(loop_time))
            # Set valid time to -1 if using init and vice versa            
            if use_init:
                self.run_at_time(run_time, -1)
            else:
                self.run_at_time(-1, run_time)
            loop_time += time_interval
