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
from command_runner import CommandRunner
from abc import ABCMeta

'''!@namespace CommandBuilder
@brief Common functionality to wrap all MET applications
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''
class CommandBuilder:
    __metaclass__ = ABCMeta

    """!Common functionality to wrap all MET applications
    """
    def __init__(self, p, logger):
        self.p = p
        self.logger = logger
        self.debug = False
        self.app_name = None
        self.app_path = None
        self.env = os.environ.copy()
        self.set_verbose(self.p.getstr('config', 'LOG_MET_VERBOSITY', '2'))
        self.cmdrunner = CommandRunner(self.p, logger=self.logger)
        self.set_user_environment()
        self.clear()

    def clear(self):
        """!Unset class variables to prepare for next run time
        """
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""


    def set_user_environment(self):
        if 'user_env_vars' not in self.p.sections():
            self.p.add_section('user_env_vars')
        for env_var in self.p.keys('user_env_vars'):
#            if env_var in self.env:
#                self.logger.warning("{} is already set in the environment. Overwriting from conf file"
#                                    .format(env_var))
            self.add_env_var(env_var, self.p.getstr('user_env_vars', env_var))


    def set_debug(self, debug):
        self.debug = debug

    def set_verbose(self, v):
        self.verbose = v

    def add_arg(self, arg):
        """!Add generic argument to MET application command line
        """
        self.args.append(arg)

    def add_input_file(self, filename):
        """!Add input filename to MET application command line
        """
        self.infiles.append(filename)

    def get_input_files(self):
        """!Returns list of input files passed to MET application
        """
        return self.infiles

    def set_input_dir(self, d):
        """!Set directory to look for input files
        """
        self.input_dir = d

    def set_output_path(self, outpath):
        """!Split path into directory and filename then save both
        """
        self.outfile = os.path.basename(outpath)
        self.outdir = os.path.dirname(outpath)

    def get_output_path(self):
        """!Combine output directory and filename then return result
        """
        return os.path.join(self.outdir, self.outfile)

    def set_output_filename(self, outfile):
        self.outfile = outfile

    def set_output_dir(self, outdir):
        self.outdir = outdir

    def set_param_file(self, param):
        self.param = param

    def add_env_var(self, key,  name):
        """!Sets an environment variable so that the MET application
        can reference it in the parameter file or the application itself
        """
        self.env[key] = name
        # Note: Modify os.environ directly since it is automatically
        # copied to the produtil runner environment. If needed,
        # we could also pass self.env to the command runner,
        # My preference would be to only copy the env vars
        # required, not the whole environment, since that is already
        # being done.
        os.environ[key] = name

    def get_env(self):
        return self.env

    def print_env(self):
        """!Print all environment variables set for this application
        """
        for x in self.env:
            self.logger.debug(x+"="+self.env[x])

    def print_env_copy(self, vars):
        """!Print list of environment variables that can be easily
        copied into terminal
        """
        out = ""
        all_vars = vars + self.p.keys('user_env_vars')
        for v in all_vars:
            if self.env[v].find('"') != -1:
                next = 'export '+v+'="'+self.env[v].replace('"', '\\"')+'"'
            else:
                next = 'export '+v+'='+self.env[v]
            out += next+'; '
        self.logger.debug(out)

    def print_env_item(self, item):
        """!Print single environment variable in the log file
        """
        self.logger.debug(item+"="+self.env[item])


    def print_user_env_items(self):
        for k in self.p.keys('user_env_vars'):
            self.print_env_item(k)


    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            (self.logger).error("No app path specified. "\
                                "You must use a subclass")
            return None

        cmd = self.app_path + " "

        if self.verbose != -1:
            cmd += "-v "+str(self.verbose) + " "

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

        cmd += " " + os.path.join(self.outdir, self.outfile)

        return cmd

    # Placed running of command in its own class, command_runner run_cmd().
    # This will allow the ability to still call build() as is currenly done
    # in subclassed CommandBuilder wrappers and also allow wrappers
    # such as tc_pairs that are not heavily designed around command builder
    # to call cmdrunner.run_cmd().
    # Make sure they have SET THE self.app_name in the subclasses constructor.
    # see regrid_data_plane_wrapper.py as an example of how to set.
    def build(self):
        """!Build and run command"""
        cmd = self.get_command()
        if cmd is None:
            return
        self.cmdrunner.run_cmd(cmd, app_name=self.app_name)


    def run_all_times(self):
        """!Loop over time range specified in conf file and
        call MET+ wrapper for each time"""
        use_init = self.p.getbool('config', 'LOOP_BY_INIT', True)
        if use_init:
            time_format = self.p.getstr('config', 'INIT_TIME_FMT')
            start_t = self.p.getstr('config', 'INIT_BEG')
            end_t = self.p.getstr('config', 'INIT_END')
            time_interval = self.p.getint('config', 'INIT_INCREMENT')
        else:
            time_format = self.p.getstr('config', 'VALID_TIME_FMT')
            start_t = self.p.getstr('config', 'VALID_BEG')
            end_t = self.p.getstr('config', 'VALID_END')
            time_interval = self.p.getint('config', 'VALID_INCREMENT')
        
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



#if __name__ == "__main__":
#  main()
