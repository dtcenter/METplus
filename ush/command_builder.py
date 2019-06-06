#!/usr/bin/env python

"""
Program Name: CommandBuilder.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
"""

from __future__ import (print_function, division)

import os
from datetime import datetime
from command_runner import CommandRunner
import met_util as util
from config_wrapper import ConfigWrapper
import string_template_substitution as sts
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

    def __init__(self, config, logger):
        self.logger = logger
        self.config = ConfigWrapper(config, logger)
        self.debug = False
        self.verbose = 2
        self.app_name = None
        self.app_path = None
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""
        self.env = os.environ.copy()
        self.verbose = self.config.getstr('config', 'LOG_MET_VERBOSITY', '2')
        self.cmdrunner = CommandRunner(self.config, logger=self.logger)
        self.set_user_environment()
        self.c_dict = {}
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
        if 'user_env_vars' not in self.config.sections():
            self.config.add_section('user_env_vars')

        for env_var in self.config.keys('user_env_vars'):
            #            if env_var in self.env:
            #                self.logger.warning("{} is already set in the environment. Overwriting from conf file"
            #                                    .format(env_var))
            self.add_env_var(env_var, self.config.getstr('user_env_vars', env_var))

        # set MET_TMP_DIR to conf TMP_DIR
        self.add_env_var('MET_TMP_DIR', self.config.getdir('TMP_DIR'))

    def set_debug(self, debug):
        self.debug = debug

    def add_arg(self, arg):
        """!Add generic argument to MET application command line
        """
        self.args.append(arg)

    def add_input_file(self, filename, addon=None):
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

    def add_env_var(self, key, name):
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
            self.logger.debug(x + '="' + self.env[x] + '"')

    def print_env_copy(self, var_list):
        """!Print list of environment variables that can be easily
        copied into terminal
        """
        out = ""
        all_vars = var_list + self.config.keys('user_env_vars')
        for v in all_vars:
            line = 'export ' + v + '="' + self.env[v].replace('"', '\\"') + '"'
            out += line + '; '
        self.logger.debug(out)

    def print_env_item(self, item):
        """!Print single environment variable in the log file
        """
        self.logger.debug(item + "=" + self.env[item])

    def print_user_env_items(self):
        for k in self.config.keys('user_env_vars'):
            self.print_env_item(k)

    def handle_fcst_and_obs_field(self, gen_name, fcst_name, obs_name, default=None, sec='config'):
        has_gen = self.config.has_option(sec, gen_name)
        has_fcst = self.config.has_option(sec, fcst_name)
        has_obs = self.config.has_option(sec, obs_name)

        # use fcst and obs if both are set
        if has_fcst and has_obs:
            fcst_conf = self.config.getstr(sec, fcst_name)
            obs_conf = self.config.getstr(sec, obs_name)
            if has_gen:
                self.logger.warning('Ignoring conf {} and using {} and {}'
                                    .format(gen_name, fcst_name, obs_name))
            return fcst_conf, obs_conf

        # if one but not the other is set, error and exit
        if has_fcst and not has_obs:
            self.logger.error('Cannot use {} without {}'.format(fcst_name, obs_name))
            exit(1)

        if has_obs and not has_fcst:
            self.logger.error('Cannot use {} without {}'.format(obs_name, fcst_name))
            exit(1)

        # if generic conf is set, use for both
        if has_gen:
            gen_conf = self.config.getstr(sec, gen_name)
            return gen_conf, gen_conf

        # if none of the options are set, use default value for both if specified
        if default == None:
            self.logger.error('{0} Or set {1}'.format('Must set both {} and {} in the config files.'
                                                      .format(fcst_name, obs_name), '{} instead'.format(gen_name)))
            exit(1)
        self.logger.warning('Using default values for {}'.format(gen_name))
        return default, default

    def find_model(self, time_info, v):
        """! Finds the model file to compare
              Args:
                @param time_info dictionary containing timing information
                @param v var_info object containing variable information
                @rtype string
                @return Returns the path to an model file
        """
        return self.find_data(time_info, v, "FCST")

    def find_obs(self, time_info, v):
        """! Finds the observation file to compare
              Args:
                @param time_info dictionary containing timing information
                @param v var_info object containing variable information
                @rtype string
                @return Returns the path to an observation file
        """
        return self.find_data(time_info, v, "OBS")

    def find_data(self, time_info, v, data_type):
        """! Finds the data file to compare
              Args:
                @param time_info dictionary containing timing information
                @param v var_info object containing variable information
                @param data_type type of data to find (FCST or OBS)
                @rtype string
                @return Returns the path to an observation file
        """
        # get time info
        valid_time = time_info['valid_fmt']

        if v != None:
            # set level based on input data type
            if data_type.startswith("OBS"):
                v_level = v.obs_level
            else:
                v_level = v.fcst_level

            # separate character from beginning of numeric level value if applicable
            level_type, level = util.split_level(v_level)

            # set level to 0 character if it is not a number
            if not level.isdigit():
                level = '0'
        else:
            level = '0'

        template = self.c_dict[data_type + '_INPUT_TEMPLATE']
        data_dir = self.c_dict[data_type + '_INPUT_DIR']

        # if looking for a file with an exact time match:
        if self.c_dict[data_type + '_FILE_WINDOW_BEGIN'] == 0 and \
                        self.c_dict[data_type + '_FILE_WINDOW_END'] == 0:
            # perform string substitution
            dsts = sts.StringSub(self.logger,
                                 template,
                                 level=(int(level.split('-')[0]) * 3600),
                                 **time_info)
            filename = dsts.doStringSub()

            # build full path with data directory and filename
            path = os.path.join(data_dir, filename)

            # check if desired data file exists and if it needs to be preprocessed
            path = util.preprocess_file(path,
                                        self.c_dict[data_type + '_INPUT_DATATYPE'],
                                        self.config)
            return path

        # if looking for a file within a time window:
        # convert valid_time to unix time
        valid_seconds = int(datetime.strptime(valid_time, "%Y%m%d%H%M").strftime("%s"))
        # get time of each file, compare to valid time, save best within range
        closest_files = []
        closest_time = 9999999

        # get range of times that will be considered
        valid_range_lower = self.c_dict[data_type + '_FILE_WINDOW_BEGIN']
        valid_range_upper = self.c_dict[data_type + '_FILE_WINDOW_END']
        lower_limit = int(datetime.strptime(util.shift_time_seconds(valid_time, valid_range_lower),
                                            "%Y%m%d%H%M").strftime("%s"))
        upper_limit = int(datetime.strptime(util.shift_time_seconds(valid_time, valid_range_upper),
                                            "%Y%m%d%H%M").strftime("%s"))

        # step through all files under input directory in sorted order
        for dirpath, dirnames, all_files in os.walk(data_dir):
            for filename in sorted(all_files):
                fullpath = os.path.join(dirpath, filename)

                # remove input data directory to get relative path
                f = fullpath.replace(data_dir + "/", "")
                # extract time information from relative path using template
                se = util.get_time_from_file(self.logger, f, template)
                if se is not None:
                    # get valid time and check if it is within the time range
                    file_valid_time = se['valid'].strftime("%Y%m%d%H%M")
                    # skip if could not extract valid time
                    if file_valid_time == '':
                        continue
                    file_valid_dt = datetime.strptime(file_valid_time, "%Y%m%d%H%M")
                    file_valid_seconds = int(file_valid_dt.strftime("%s"))
                    # skip if outside time range
                    if file_valid_seconds < lower_limit or file_valid_seconds > upper_limit:
                        continue

                    # if only 1 file is allowed, check if file is
                    # closer to desired valid time than previous match
                    if not self.c_dict['ALLOW_MULTIPLE_FILES']:
                        diff = abs(valid_seconds - file_valid_seconds)
                        if diff < closest_time:
                            closest_time = diff
                            del closest_files[:]
                            closest_files.append(fullpath)
                    # if multiple files are allowed, get all files within range
                    else:
                        closest_files.append(fullpath)

        if not closest_files:
            return None

        # check if file(s) needs to be preprocessed before returning the path
        # return single file path if 1 file was found
        if len(closest_files) == 1:
            return util.preprocess_file(closest_files[0],
                                        self.c_dict[data_type + '_INPUT_DATATYPE'],
                                        self.config)

        # return list if multiple files are found
        out = []
        for f in closest_files:
            outfile = util.preprocess_file(f,
                                           self.c_dict[data_type + '_INPUT_DATATYPE'],
                                           self.config)
            out.append(outfile)

        return out

    def write_list_file(self, filename, file_list):
        list_dir = os.path.join(self.config.getdir('STAGING_DIR'), 'file_lists')
        list_path = os.path.join(list_dir, filename)

        if not os.path.exists(list_dir):
            os.makedirs(list_dir, mode=0o0775)

        with open(list_path, 'w') as file_handle:
            for f_path in file_list:
                file_handle.write(f_path + '\n')
        return list_path

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.logger.error('No app path specified. '
                              'You must use a subclass')
            return None

        cmd = self.app_path + " "

        if self.verbose != -1:
            cmd += "-v " + str(self.verbose) + " "

        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            self.logger.error("No input filenames specified")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.outfile == "":
            self.logger.error("No output filename specified")
            return None

        if self.outdir == "":
            self.logger.error("No output directory specified")
            return None

        out_path = os.path.join(self.outdir, self.outfile)

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        cmd += " " + out_path

        if self.param != "":
            cmd += ' ' + self.param

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

    def run_at_time(self, input_dict):
        self.logger.error('run_at_time not implemented for {} wrapper. '
                          'Cannot run with LOOP_ORDER = times'.format(self.app_name))
        exit(1)

    def run_all_times(self):
        """!Loop over time range specified in conf file and
        call METplus wrapper for each time"""
        util.loop_over_times_and_call(self.config, self)
