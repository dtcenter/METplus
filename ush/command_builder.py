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
from abc import ABCMeta
from command_runner import CommandRunner
import met_util as util
import string_template_substitution as sts

# pylint:disable=pointless-string-statement
'''!@namespace CommandBuilder
@brief Common functionality to wrap all MET applications
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''


class CommandBuilder:
    """!Common functionality to wrap all MET applications
    """
    __metaclass__ = ABCMeta

    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.debug = False
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""
        self.env = os.environ.copy()
        if hasattr(config, 'env'):
            self.env = config.env
        self.c_dict = self.create_c_dict()
        self.cmdrunner = CommandRunner(self.config, logger=self.logger,
                                       verbose=self.c_dict['VERBOSITY'])

        # if env MET_TMP_DIR was not set, set it to config TMP_DIR
        if 'MET_TMP_DIR' not in self.env:
            self.env['MET_TMP_DIR'] = self.config.getdir('TMP_DIR')

        self.clear()

    def create_c_dict(self):
        c_dict = dict()
        # set skip if output exists to False for all wrappers
        # wrappers that support this functionality can override this value
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_MET_VERBOSITY', '2')
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = False
        return c_dict

    def clear(self):
        """!Unset class variables to prepare for next run time
        """
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""

    def set_user_environment(self, time_info=None):
        """!Set environment variables defined in [user_env_vars] section of config
        """
        if time_info is None:
            time_info = { 'now' : datetime.strptime(self.config.getstr('config', 'CLOCK_TIME'),
                                                                       '%Y%m%d%H%M%S') }

        if 'user_env_vars' not in self.config.sections():
            self.config.add_section('user_env_vars')

        for env_var in self.config.keys('user_env_vars'):
            # perform string substitution on each variable
            raw_env_var_value = self.config.getraw('user_env_vars', env_var)
            env_var_value = sts.StringSub(self.logger,
                                          raw_env_var_value,
                                          **time_info).do_string_sub()
            self.add_env_var(env_var, env_var_value)

    def set_output_path(self, outpath):
        """!Split path into directory and filename then save both
        """
        self.outfile = os.path.basename(outpath)
        self.outdir = os.path.dirname(outpath)

    def get_output_path(self):
        """!Combine output directory and filename then return result
        """
        return os.path.join(self.outdir, self.outfile)

    def add_env_var(self, key, name):
        """!Sets an environment variable so that the MET application
        can reference it in the parameter file or the application itself
        """
        self.env[key] = name

    def print_env(self):
        """!Print all environment variables set for this application
        """
        for env_name in self.env:
            self.logger.debug(env_name + '="' + self.env[env_name] + '"')

    def print_env_copy(self, var_list):
        """!Print list of environment variables that can be easily
        copied into terminal
        """
        out = ""
        all_vars = var_list + self.config.keys('user_env_vars') + ['MET_TMP_DIR']
        shell = self.config.getstr('config', 'USER_SHELL', 'bash').lower()
        for var in all_vars:
            if shell == 'csh':
                line = 'setenv ' + var + ' "' + self.env[var].replace('"', '"\\""') + '"'
            else:
                line = 'export ' + var + '="' + self.env[var].replace('"', '\\"') + '"'

            out += line + '; '
        self.logger.debug(out)

    def print_env_item(self, item):
        """!Print single environment variable in the log file
        """
        self.logger.debug(item + "=" + self.env[item])

    def print_user_env_items(self):
        """!Prints user environment variables in the log file
        """
        for k in self.config.keys('user_env_vars') + ['MET_TMP_DIR']:
            self.print_env_item(k)

    def handle_fcst_and_obs_field(self, gen_name, fcst_name, obs_name, default=None, sec='config'):
        """!Handles config variables that have fcst/obs versions or a generic
            variable to handle both, i.e. FCST_NAME, OBS_NAME, and NAME.
            If FCST_NAME and OBS_NAME both exist, they are used. If both are don't
            exist, NAME is used.
        """
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
        if default is None:
            msg = 'Must set both {} and {} in the config files'.format(fcst_name,
                                                                       obs_name)
            msg += ' or set {} instead'.format(gen_name)
            self.logger.error(msg)

            exit(1)
        self.logger.warning('Using default values for {}'.format(gen_name))
        return default, default

    def find_model(self, time_info, var_info, mandatory=True):
        """! Finds the model file to compare
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param mandatory if True, report error if not found, warning if not
                  default is True
                @rtype string
                @return Returns the path to an model file
        """
        return self.find_data(time_info, var_info, "FCST", mandatory)

    def find_obs(self, time_info, var_info, mandatory=True):
        """! Finds the observation file to compare
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param mandatory if True, report error if not found, warning if not
                  default is True
                @rtype string
                @return Returns the path to an observation file
        """
        return self.find_data(time_info, var_info, "OBS", mandatory)

    def find_data(self, time_info, var_info, data_type, mandatory=True):
        """! Finds the data file to compare
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param data_type type of data to find (FCST or OBS)
                @param mandatory if True, report error if not found, warning if not
                  default is True
                @rtype string
                @return Returns the path to an observation file
        """
        # get time info
        valid_time = time_info['valid_fmt']

        if var_info is not None:
            # set level based on input data type
            if data_type.startswith("OBS"):
                v_level = var_info['obs_level']
            else:
                v_level = var_info['fcst_level']

            # separate character from beginning of numeric level value if applicable
            level = util.split_level(v_level)[1]

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
            filename = dsts.do_string_sub()

            # build full path with data directory and filename
            full_path = os.path.join(data_dir, filename)

            # check if desired data file exists and if it needs to be preprocessed
            processed_path = util.preprocess_file(full_path,
                                        self.c_dict[data_type + '_INPUT_DATATYPE'],
                                        self.config)

            # report error if file path could not be found
            if processed_path is None:
                msg = f"Could not find {data_type} file {full_path} using template {template}"
                if mandatory:
                    self.logger.error(msg)
                else:
                    self.logger.warning(msg)

            return processed_path

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
        for dirpath, _, all_files in os.walk(data_dir):
            for filename in sorted(all_files):
                fullpath = os.path.join(dirpath, filename)

                # remove input data directory to get relative path
                rel_path = fullpath.replace(data_dir + "/", "")
                # extract time information from relative path using template
                file_time_info = util.get_time_from_file(self.logger, rel_path, template)
                if file_time_info is not None:
                    # get valid time and check if it is within the time range
                    file_valid_time = file_time_info['valid'].strftime("%Y%m%d%H%M")
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
            msg = f"Could not find {data_type} files under {data_dir} within range " +\
            f"[{valid_range_lower},{valid_range_upper}] using template {template}"
            if mandatory:
                self.logger.error(msg)
            else:
                self.logger.warning(msg)
            return None

        # check if file(s) needs to be preprocessed before returning the path
        # return single file path if 1 file was found
        if len(closest_files) == 1:
            return util.preprocess_file(closest_files[0],
                                        self.c_dict[data_type + '_INPUT_DATATYPE'],
                                        self.config)

        # return list if multiple files are found
        out = []
        for close_file in closest_files:
            outfile = util.preprocess_file(close_file,
                                           self.c_dict[data_type + '_INPUT_DATATYPE'],
                                           self.config)
            out.append(outfile)

        return out

    def write_list_file(self, filename, file_list):
        """! Writes a file containing a list of filenames to the staging dir"""
        list_dir = os.path.join(self.config.getdir('STAGING_DIR'), 'file_lists')
        list_path = os.path.join(list_dir, filename)

        if not os.path.exists(list_dir):
            os.makedirs(list_dir, mode=0o0775)

        with open(list_path, 'w') as file_handle:
            for f_path in file_list:
                file_handle.write(f_path + '\n')
        return list_path

    def find_and_check_output_file(self, time_info):
        """!Look for expected output file. If it exists and configured to skip if it does, then return False"""
        outfile = sts.StringSub(self.logger,
                            self.c_dict['OUTPUT_TEMPLATE'],
                            **time_info).do_string_sub()
        outpath = os.path.join(self.c_dict['OUTPUT_DIR'], outfile)
        self.set_output_path(outpath)

        if not os.path.exists(outpath) or not self.c_dict['SKIP_IF_OUTPUT_EXISTS']:
            return True

        # if the output file exists and we are supposed to skip, don't run pb2nc
        self.logger.debug(f'Skip writing output file {outpath} because it already '
                          'exists. Remove file or change '
                          f'{self.app_name.upper()}_SKIP_IF_OUTPUT_EXISTS to False '
                          'to process')

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.logger.error('No app path specified. '
                              'You must use a subclass')
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for arg in self.args:
            cmd += arg + " "

        if not self.infiles:
            self.logger.error("No input filenames specified")
            return None

        for infile in self.infiles:
            cmd += infile + " "

        if self.outfile == "":
            self.logger.error("No output filename specified")
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

        self.cmdrunner.run_cmd(cmd, self.env, app_name=self.app_name)

    # argument needed to match call
    # pylint:disable=unused-argument
    def run_at_time(self, input_dict):
        """!Used to output error and exit if wrapper is attemped to be run with
            LOOP_ORDER = times and the run_at_time method is not implemented"""
        self.logger.error('run_at_time not implemented for {} wrapper. '
                          'Cannot run with LOOP_ORDER = times'.format(self.app_name))
        exit(1)

    def run_all_times(self):
        """!Loop over time range specified in conf file and
        call METplus wrapper for each time"""
        util.loop_over_times_and_call(self.config, self)
