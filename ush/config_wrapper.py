#!/usr/bin/env python

from __future__ import (print_function, division)

import os

# TODO: Inherit from ProdConfig and call super method for produtil calls
class ConfigWrapper:
    def __init__(self, p, logger):
        self.p = p
        self.logger = logger


    def has_option(self, sec, opt):
        return self.p.has_option(sec, opt)


    def has_section(self, sec):
        return self.p.has_option(sec)


    def set(self, sec, key, value):
        self.p.set(sec, key, value)

    def keys(self, sec):
        return self.p.keys(sec)


    def sections(self):
        return self.p.sections()


    def add_section(self, name):
        return self.p.add_section(name)


    def log(self, sublog):
        return self.p.log(sublog)


    def getraw(self, sec, opt, default='', count=0):
        """ parse parameter and replace any existing parameters
            referenced with the value (looking in same section, then
            config, dir, and os environment)
            returns raw string, preserving {valid?fmt=%Y} blocks
            Args:
                @param p: Conf object
                @param sec: Section in the conf file to look for variable
                @param opt: Variable to interpret
            Returns:
                Raw string
        """
        count = count + 1
        if count >= 10:
            return ''

        in_template = self.p.getraw(sec, opt, default)
        out_template = ""
        in_brackets = False
        for i, c in enumerate(in_template):
            if c == "{":
                in_brackets = True
                start_idx = i
            elif c == "}":
                var_name = in_template[start_idx+1:i]
                var = None
                if self.p.has_option(sec,var_name):
                    var = self.getraw(sec, var_name, default, count)
                elif self.p.has_option('config',var_name):
                    var = self.getraw('config', var_name, default, count)
                elif self.p.has_option('dir',var_name):
                    var = self.getraw('dir', var_name, default, count)
                elif var_name[0:3] == "ENV":
                    var = os.environ.get(var_name[4:-1])

                if var is None:
                    out_template += in_template[start_idx:i+1]
                else:
                    out_template += var
                in_brackets = False
            elif not in_brackets:
                out_template += c

        return out_template


    # report error and exit if default is not set
    # helper function for get methods
    def check_default(self, sec, name, default):
        if default == None:
            msg = 'Requested conf [{}] {} was not set in config file'.format(sec, name)
            if self.logger:
                self.logger.error(msg)
            else:
                print(msg)
            exit(1)

        # print debug message saying default value was used
        msg = "Setting [{}] {} to default value: {}.".format(sec, name,
                                                             default)
        if self.logger:
            self.logger.debug(msg)
        else:
            print(msg)

        # set conf with default value so all defaults can be added to
        #  the final conf and warning only appears once per conf item
        #  using a default value
        self.p.set(sec, name, default)

    # temporary function to get full path of exe.
    # replace with shutil.which() when using python3
    def which(self, exe_name):
        fpath, fname = os.path.split(exe_name)
        if fpath:
            if os.path.isfile(exe_name) and os.access(exe_name, os.X_OK):
                return exe_name
        else:
            for path in os.environ['PATH'].split(os.pathsep):
                exe_file = os.path.join(path, exe_name)
                if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                    return exe_file

        return None


    # wrap produtil exe with checks to see if option is set and if exe actually exists
    def getexe(self, exe_name):

        if not self.p.has_option('exe', exe_name):
            msg = 'Requested [exe] {} was not set in config file'.format(exe_name)
            if self.logger:
                self.logger.error(msg)
            else:
                print(msg)
            exit(1)

        exe_path = self.p.getexe(exe_name)

        full_exe_path = self.which(exe_path)
        if full_exe_path == None:            
            msg = 'Executable {} does not exist at {}'.format(exe_name, exe_path)
            if self.logger:
                self.logger.error(msg)
            else:
                print(msg)
            exit(1)

        # set config item to full path to exe and return full path
        self.p.set('exe', exe_name, full_exe_path)
        return full_exe_path


    def getdir(self, dir_name, default_val=None):
        if not self.p.has_option('dir', dir_name):
            self.check_default('dir', dir_name, default_val)
            dir_path = default_val
        else:
            dir_path = self.p.getdir(dir_name)

        if dir_path == '/path/to' or dir_path.startswith('/path/to'):
            msg = 'Directory {} is set to or contains /path/to. Please set this to a valid location'.format(dir_name)
            if self.logger:
                self.logger.error(msg)
            else:
                print(msg)
            exit(1)

        return dir_path


    def getstr(self, sec, name, default_val=None):
        if self.p.has_option(sec, name):
            return self.p.getstr(sec, name)
        # config item was not found

        self.check_default(sec, name, default_val)
        return default_val


    def getbool(self, sec, name, default_val=None):
        if self.p.has_option(sec, name):
            return self.p.getbool(sec, name)
        # config item was not found

        self.check_default(sec, name, default_val)
        return default_val


    def getint(self, sec, name, default_val=None):
        if self.p.has_option(sec, name):
            return self.p.getint(sec, name)
        # config item was not found

        self.check_default(sec, name, default_val)
        return default_val


    def getfloat(self, sec, name, default_val=None):
        if self.p.has_option(sec, name):
            return self.p.getfloat(sec, name)
        # config item was not found

        self.check_default(sec, name, default_val)
        return default_val
