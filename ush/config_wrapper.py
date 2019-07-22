#!/usr/bin/env python

"""
Program Name: config_wrapper.py
Contact(s): George McCabe
Abstract: Wraps produtil config functions to do additional error checking
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes:
"""

from __future__ import (print_function, division)

import os
import re

def which(exe_name):
    """!Temporary function to get full path of exe.
        replace with shutil.which() when using python3"""
    fpath = os.path.split(exe_name)[0]
    if fpath:
        if os.path.isfile(exe_name) and os.access(exe_name, os.X_OK):
            return exe_name
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file = os.path.join(path, exe_name)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                return exe_file

    return None

class ConfigWrapper(object):
    """!Wraps produtil config functions to do additional error checking"""
    def __init__(self, conf, logger):
        self.conf = conf
        self.logger = logger

    def has_option(self, sec, opt):
        """!Calls produtil config has_option"""
        return self.conf.has_option(sec, opt)

    def has_section(self, sec):
        """!Calls produtil config has_section"""
        return self.conf.has_option(sec)

    def set(self, sec, key, value):
        """!Calls produtil config set"""
        self.conf.set(sec, key, value)

    def keys(self, sec):
        """!Calls produtil config keys"""
        return self.conf.keys(sec)

    def sections(self):
        """!Calls produtil config sections"""
        return self.conf.sections()

    def add_section(self, name):
        """!Calls produtil config add_section"""
        return self.conf.add_section(name)

    def log(self, sublog):
        """!Calls produtil config log"""
        return self.conf.log(sublog)

    def getraw(self, sec, opt, default='', count=0):
        """ parse parameter and replace any existing parameters
            referenced with the value (looking in same section, then
            config, dir, and os environment)
            returns raw string, preserving {valid?fmt=%Y} blocks
            Args:
                @param sec: Section in the conf file to look for variable
                @param opt: Variable to interpret
                @param default: Default value to use if config is not set
                @param count: Counter used to stop recursion to prevent infinite
            Returns:
                Raw string
        """
        count = count + 1
        if count >= 10:
            return ''

        in_template = self.conf.getraw(sec, opt, default)
        out_template = ""
        in_brackets = False
        for index, character in enumerate(in_template):
            if character == "{":
                in_brackets = True
                start_idx = index
            elif character == "}":
                var_name = in_template[start_idx+1:index]
                var = None
                if self.conf.has_option(sec, var_name):
                    var = self.getraw(sec, var_name, default, count)
                elif self.conf.has_option('config', var_name):
                    var = self.getraw('config', var_name, default, count)
                elif self.conf.has_option('dir', var_name):
                    var = self.getraw('dir', var_name, default, count)
                elif var_name[0:3] == "ENV":
                    var = os.environ.get(var_name[4:-1])

                if var is None:
                    out_template += in_template[start_idx:index+1]
                else:
                    out_template += var
                in_brackets = False
            elif not in_brackets:
                out_template += character

        return out_template

    def check_default(self, sec, name, default):
        """!helper function for get methods, report error and exit if
            default is not set """
        if default is None:
            msg = 'Requested conf [{}] {} was not set in config file'.format(sec, name)
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))
            exit(1)

        # print debug message saying default value was used
        msg = "Setting [{}] {} to default value: {}.".format(sec, name,
                                                             default)
        if self.logger:
            self.logger.debug(msg)
        else:
            print('DEBUG: {}'.format(msg))

        # set conf with default value so all defaults can be added to
        #  the final conf and warning only appears once per conf item
        #  using a default value
        self.conf.set(sec, name, default)

    def getexe(self, exe_name):
        """!Wraps produtil exe with checks to see if option is set and if
            exe actually exists"""
        if not self.conf.has_option('exe', exe_name):
            msg = 'Requested [exe] {} was not set in config file'.format(exe_name)
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))
            exit(1)

        exe_path = self.conf.getexe(exe_name)

        full_exe_path = which(exe_path)
        if full_exe_path is None:
            msg = 'Executable {} does not exist at {}'.format(exe_name, exe_path)
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))
            exit(1)

        # set config item to full path to exe and return full path
        self.conf.set('exe', exe_name, full_exe_path)
        return full_exe_path

    def getdir(self, dir_name, default_val=None):
        """!Wraps produtil getdir and reports an error if it is set to /path/to"""
        if not self.conf.has_option('dir', dir_name):
            self.check_default('dir', dir_name, default_val)
            dir_path = default_val
        else:
            dir_path = self.conf.getdir(dir_name)

        if '/path/to' in dir_path:
            msg = 'Directory {} is set to or contains /path/to.'.format(dir_name)+\
                  ' Please set this to a valid location'
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))
            exit(1)

        return dir_path

    def getstr(self, sec, name, default_val=None):
        """!Wraps produtil getstr to gracefully report if variable is not set
            and no default value is specified"""
        if self.conf.has_option(sec, name):
            return self.conf.getstr(sec, name)

        # config item was not found
        self.check_default(sec, name, default_val)
        return default_val

    def getbool(self, sec, name, default_val=None):
        """!Wraps produtil getbool to gracefully report if variable is not set
            and no default value is specified"""
        if self.conf.has_option(sec, name):
            return self.conf.getbool(sec, name)

        # config item was not found
        self.check_default(sec, name, default_val)
        return default_val

    def getint(self, sec, name, default_val=None):
        """!Wraps produtil getint to gracefully report if variable is not set
            and no default value is specified"""
        if self.conf.has_option(sec, name):
            return self.conf.getint(sec, name)

        # config item was not found
        self.check_default(sec, name, default_val)
        return default_val

    def getfloat(self, sec, name, default_val=None):
        """!Wraps produtil getfloat to gracefully report if variable is not set
            and no default value is specified"""
        if self.conf.has_option(sec, name):
            return self.conf.getfloat(sec, name)

        # config item was not found
        self.check_default(sec, name, default_val)
        return default_val

    def getseconds(self, sec, name, default_val=None):
        """!Converts time values ending in H, M, or S to seconds"""
        if self.conf.has_option(sec, name):
            # convert value to seconds
            # Valid options match format 3600, 3600S, 60M, or 1H
            value = self.conf.getstr(sec, name)
            regex_and_multiplier = {r'(-*)(\d+)S' : 1,
                                    r'(-*)(\d+)M' : 60,
                                    r'(-*)(\d+)H' : 3600,
                                    r'(-*)(\d+)' : 1}
            for reg, mult in regex_and_multiplier.items():
                match = re.match(reg, value)
                if match:
                    if match.group(1) == '-':
                        mult = mult * -1
                    return int(match.group(2)) * mult

            # if value is not in an expected format, error and exit
            msg = '[{}] {} does not match expected format. '.format(sec, name) +\
              'Valid options match 3600, 3600S, 60M, or 1H'
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))

            exit(1)

        # config item was not found
        self.check_default(sec, name, default_val)
        return default_val
