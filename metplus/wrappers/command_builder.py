"""
Program Name: command_builder.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
"""

import os
import sys
import glob
from datetime import datetime
from abc import ABCMeta
from inspect import getframeinfo, stack
import re

from .command_runner import CommandRunner
from ..util import getlist
from ..util import met_util as util
from ..util import do_string_sub, ti_calculate, get_seconds_from_string
from ..util import get_time_from_file
from ..util import config_metplus
from ..util import METConfig
from ..util import MISSING_DATA_VALUE
from ..util import get_custom_string_list
from ..util import get_wrapped_met_config_file, add_met_config_item, format_met_config
from ..util import remove_quotes
from ..util.met_config import add_met_config_dict

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

    # types of climatology values that should be checked and set
    climo_types = ['MEAN', 'STDEV']

    # name of variable to hold any MET config overrides
    MET_OVERRIDES_KEY = 'METPLUS_MET_CONFIG_OVERRIDES'

    def __init__(self, config, instance=None):
        self.isOK = True
        self.errors = 0
        self.config = config
        self.logger = config.logger
        self.env_list = set()
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""
        self.all_commands = []

        # store values to set in environment variables for each command
        self.env_var_dict = {}

        # list of environment variables to set before running command
        self.env_var_keys = [
            'MET_TMP_DIR',
            'OMP_NUM_THREADS',
        ]
        if hasattr(self, 'WRAPPER_ENV_VAR_KEYS'):
            self.env_var_keys.extend(self.WRAPPER_ENV_VAR_KEYS)

        if hasattr(self, 'DEPRECATED_WRAPPER_ENV_VAR_KEYS'):
            self.env_var_keys.extend(self.DEPRECATED_WRAPPER_ENV_VAR_KEYS)

        # if instance is set, check for a section with the same name in the
        # METplusConfig object. If found, copy all values into the config
        if instance:
            self.config = (
                config_metplus.replace_config_from_section(self.config,
                                                           instance,
                                                           required=False)
            )

        self.instance = instance

        self.env = os.environ.copy()
        if hasattr(config, 'env'):
            self.env = config.env

        # populate c_dict dictionary
        self.c_dict = self.create_c_dict()

        # if wrapper has a config file, read MET config overrides variable
        if 'CONFIG_FILE' in self.c_dict:
            config_name = self.MET_OVERRIDES_KEY.replace('METPLUS',
                                                         self.app_name.upper())
            self.env_var_dict[self.MET_OVERRIDES_KEY] = (
                self.config.getraw('config', config_name)
            )

            # add key to list of env vars to set
            self.env_var_keys.append(self.MET_OVERRIDES_KEY)

            # warn if any environment variables set by the wrapper are not
            # being utilized in the user's config file
            self.check_for_unused_env_vars()

        # set MET_TMP_DIR environment variable that controls
        # where the MET tools write temporary files
        self.env_var_dict['MET_TMP_DIR'] = self.config.getdir('TMP_DIR')

        # set OMP_NUM_THREADS environment variable
        self.env_var_dict['OMP_NUM_THREADS'] = (
            self.config.getstr('config', 'OMP_NUM_THREADS')
        )

        self.check_for_externals()

        self.cmdrunner = CommandRunner(
            self.config, logger=self.logger,
            verbose=self.c_dict['VERBOSITY'],
            skip_run=self.c_dict.get('DO_NOT_RUN_EXE', False),
        )

        # set log name to app name by default
        # any wrappers with a name different than the primary app that is run
        # should override this value in their init function after the call
        # to the parent init function
        self.log_name = self.app_name if hasattr(self, 'app_name') else ''

        self.clear()

    def check_for_unused_env_vars(self):
        config_file = self.c_dict.get('CONFIG_FILE')
        if not config_file:
            return

        if not hasattr(self, 'WRAPPER_ENV_VAR_KEYS'):
            return

        if not os.path.exists(config_file):
            if self.c_dict.get('INPUT_MUST_EXIST', True):
                self.log_error(f'Config file does not exist: {config_file}')
            return

        # read config file content
        with open(config_file, 'r') as file_handle:
            content = file_handle.read()

        # report a warning if any env var in the list is not being used
        for env_var_key in self.WRAPPER_ENV_VAR_KEYS:
            env_var_string = f"${{{env_var_key}}}"
            if env_var_string not in content:
                self.logger.warning(f"Environment variable {env_var_string} "
                                    "is not utilized in MET config file: "
                                    f"{config_file}")

    def create_c_dict(self):
        c_dict = dict()
        # set skip if output exists to False for all wrappers
        # wrappers that support this functionality can override this value
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_MET_VERBOSITY',
                                                 '2')
        c_dict['ALLOW_MULTIPLE_FILES'] = False

        app_name = ''
        if hasattr(self, 'app_name'):
            app_name = self.app_name

        c_dict['CUSTOM_LOOP_LIST'] = get_custom_string_list(self.config,
                                                            app_name)

        c_dict['SKIP_TIMES'] = util.get_skip_times(self.config,
                                                   app_name)

        c_dict['MANDATORY'] = (
            self.config.getbool('config',
                                f'{app_name.upper()}_MANDATORY',
                                True)
        )
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = (
            self.config.getbool('config',
                                f'{app_name.upper()}_SKIP_IF_OUTPUT_EXISTS',
                                False)
        )

        # option to bypass check for the existence of input files
        # to make testing easier
        c_dict['INPUT_MUST_EXIST'] = self.config.getbool('config',
                                                         'INPUT_MUST_EXIST',
                                                         True)

        c_dict['USER_SHELL'] = self.config.getstr('config',
                                                  'USER_SHELL',
                                                  'bash')

        c_dict['DO_NOT_RUN_EXE'] = self.config.getbool('config',
                                                       'DO_NOT_RUN_EXE',
                                                       False)

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
        self.env_list.clear()

    def set_environment_variables(self, time_info=None):
        """!Set environment variables that will be read set when running this tool.
            This tool does not have a config file, but environment variables may still
            need to be set, such as MET_TMP_DIR and MET_PYTHON_EXE.
            Reformat as needed. Print list of variables that were set and their values.
            Args:
              @param time_info dictionary containing timing info from current run"""
        if time_info is None:
            clock_time_fmt = (
                datetime.strptime(self.config.getstr('config', 'CLOCK_TIME'),
                                  '%Y%m%d%H%M%S')
            )
            time_info = {'now': clock_time_fmt}

        # loop over list of environment variables that need to be set for the
        # wrapper, apply time info substitution if available, and
        # set environment variable setting empty string if key is not set in
        # the env_var_dict dictionary
        for key in self.env_var_keys:
            value = self.env_var_dict.get(key, '')
            if time_info:
                value = do_string_sub(value,
                                      skip_missing_tags=True,
                                      **time_info)

            self.add_env_var(key, value)

        # set user defined environment variables
        self.set_user_environment(time_info)

        # send environment variables to logger
        for msg in self.print_all_envs(print_each_item=True,
                                       print_copyable=False):
            self.logger.info(msg)

        # log environment variables that can be copied into terminal
        # to rerun application if debug logging is turned on
        for msg in self.print_all_envs(print_each_item=False,
                                       print_copyable=True):
            self.logger.debug(msg)

    def log_error(self, error_string):
        caller = getframeinfo(stack()[1][0])
        self.logger.error(f"({os.path.basename(caller.filename)}:{caller.lineno}) {error_string}")
        self.errors += 1
        self.isOK = False

    def set_user_environment(self, time_info):
        """!Set environment variables defined in [user_env_vars] section of config
        """
        if 'user_env_vars' not in self.config.sections():
            self.config.add_section('user_env_vars')

        for env_var in self.config.keys('user_env_vars'):
            # perform string substitution on each variable
            raw_env_var_value = self.config.getraw('user_env_vars', env_var)
            env_var_value = do_string_sub(raw_env_var_value,
                                          **time_info)
            self.add_env_var(env_var, env_var_value)

    def print_all_envs(self, print_copyable=True, print_each_item=True):
        """! Create list of log messages that output all environment variables
        that were set by this wrapper.

        @param print_copyable if True, also output a list of shell commands
        that can be easily copied and pasted into a browser to recreate the
        environment that was set when the command was run
        @param print_each_item if True, print each environment variable and
        value on a single line (default is True)
        @returns list of log messages
        """
        msg = []
        if print_each_item:
            msg.append("ENVIRONMENT FOR NEXT COMMAND: ")
            for env_item in sorted(self.env_list):
                msg.append(self.print_env_item(env_item))

        if print_copyable:
            msg.append("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
            msg.append(self.get_env_copy())

        return msg

    def _handle_window_once(self, input_list, default_val=0):
        """! Check and set window dictionary variables like
              OBS_WINDOW_BEG or FCST_FILE_WINDOW_END

             @param input_list list of config keys to check for value
             @param default_val value to use if none of the input keys found
        """
        for input_key in input_list:
            if self.config.has_option('config', input_key):
                return self.config.getseconds('config', input_key)

        return default_val

    def handle_obs_window_legacy(self, c_dict):
        """! Handle obs window config variables like
        OBS_<app_name>_WINDOW_[BEGIN/END]. Set c_dict values for begin and end
        to handle old method of setting env vars in MET config files, i.e.
        OBS_WINDOW_[BEGIN/END]. Set env_var_dict value if any of the values
        are set

             @param c_dict dictionary to read items from
        """
        edges = [('BEGIN', -5400),
                 ('END', 5400)]
        app = self.app_name.upper()

        # check {app}_WINDOW_{edge} to support PB2NC_WINDOW_[BEGIN/END]
        for edge, default_val in edges:
            input_list = [f'OBS_{app}_WINDOW_{edge}',
                          f'{app}_OBS_WINDOW_{edge}',
                          f'{app}_WINDOW_{edge}',
                          f'OBS_WINDOW_{edge}',
                         ]
            output_key = f'OBS_WINDOW_{edge}'
            value = self._handle_window_once(input_list, default_val)
            c_dict[output_key] = value

    def handle_file_window_variables(self, c_dict, data_types=None):
        """! Handle all window config variables like
              [FCST/OBS]_<app_name>_WINDOW_[BEGIN/END] and
              [FCST/OBS]_<app_name>_FILE_WINDOW_[BEGIN/END]

                @param c_dict dictionary to set items in
                @param data_types tuple of data types to check, i.e. FCST, OBS
        """
        edges = ['BEGIN', 'END']
        app = self.app_name.upper()

        if not data_types:
            data_types = ['FCST', 'OBS']

        for data_type in data_types:
            for edge in edges:
                input_list = [
                    f'{data_type}_{app}_FILE_WINDOW_{edge}',
                    f'{app}_FILE_WINDOW_{edge}',
                    f'{data_type}_FILE_WINDOW_{edge}',
                    f'FILE_WINDOW_{edge}',
                ]
                output_key = f'{data_type}_FILE_WINDOW_{edge}'
                value = self._handle_window_once(input_list, 0)
                c_dict[output_key] = value

    def set_met_config_obs_window(self, c_dict):
        for edge in ['BEGIN', 'END']:
            obs_window = c_dict.get(f'OBS_WINDOW_{edge}', '')
            if obs_window:
                obs_window_fmt = f"{edge.lower()} = {obs_window};"
            else:
                obs_window_fmt = ''

            self.env_var_dict[f'METPLUS_OBS_WINDOW_{edge}'] = obs_window_fmt

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
        self.env[key] = str(name)
        self.env_list.add(key)

    def get_env_copy(self, var_list=None):
        """!Print list of environment variables that can be easily
        copied into terminal
        """
        out = ""
        if not var_list:
            var_list = self.env_list

        if 'user_env_vars' in self.config.sections():
            for user_var in self.config.keys('user_env_vars'):
                # skip unset user env vars if not needed
                if self.env.get(user_var) is None:
                    continue
                var_list.add(user_var)

        shell = self.c_dict.get('USER_SHELL', '').lower()
        for var in sorted(var_list):
            if shell == 'csh':
                # TODO: Complex environment variables that have special characters
                # like { or } will not be copyable in csh until modifications are
                # made to the formatting of the setenv calls
                clean_env = self.env[var].replace('"', '"\\""')
                line = 'setenv ' + var + ' "' + clean_env + '"'
            else:
                # insert escape characters to allow export command to be copyable
                clean_env = self.env[var].replace('"', r'\"').replace(r'\\"', r'\\\"')
                line = 'export ' + var + '="' + clean_env + '"'
            line = line.replace('\n', '')
            out += line + '; '

        return out

    def print_env_item(self, item):
        """!Print single environment variable in the log file
        """
        return f"{item}={self.env[item]}"

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
            self.log_error('Cannot use {} without {}'.format(fcst_name, obs_name))
            return None, None

        if has_obs and not has_fcst:
            self.log_error('Cannot use {} without {}'.format(obs_name, fcst_name))
            return None, None

        # if generic conf is set, use for both
        if has_gen:
            gen_conf = self.config.getstr(sec, gen_name)
            return gen_conf, gen_conf

        # if none of the options are set, use default value for both if specified
        if default is None:
            msg = 'Must set both {} and {} in the config files'.format(fcst_name,
                                                                       obs_name)
            msg += ' or set {} instead'.format(gen_name)
            self.log_error(msg)

            return None, None

        self.logger.warning('Using default values for {}'.format(gen_name))
        return default, default

    def find_model(self, time_info, var_info=None, mandatory=True,
                   return_list=False):
        """! Finds the model file to compare
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param mandatory if True, report error if not found, warning
                 if not, default is True
                @rtype string
                @return Returns the path to an model file
        """
        return self.find_data(time_info,
                              var_info=var_info,
                              data_type="FCST",
                              mandatory=mandatory,
                              return_list=return_list)

    def find_obs(self, time_info, var_info=None, mandatory=True,
                 return_list=False):
        """! Finds the observation file to compare
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param mandatory if True, report error if not found, warning
                 if not, default is True
                @rtype string
                @return Returns the path to an observation file
        """
        return self.find_data(time_info,
                              var_info=var_info,
                              data_type="OBS",
                              mandatory=mandatory,
                              return_list=return_list)

    def find_obs_offset(self, time_info, var_info=None, mandatory=True,
                        return_list=False):
        """! Finds the observation file to compare, looping through offset
            list until a file is found

             @param time_info dictionary containing timing information
             @param var_info object containing variable information
             @param mandatory if True, report error if not found, warning
              if not, default is True
             @rtype string
             @return Returns tuple of the path to an observation file and
              the time_info object
              used to find the data so the value of offset can be preserved
        """
        offsets = self.c_dict.get('OFFSETS', [0])
        # if no offsets are specified, use argument to determine if file is
        # mandatory if offsets are specified, set mandatory to False to avoid
        # errors when searching through offset list
        is_mandatory = mandatory if offsets == [0] else False

        for offset in offsets:
            time_info['offset_hours'] = offset
            time_info = ti_calculate(time_info)
            obs_path = self.find_obs(time_info,
                                     var_info=var_info,
                                     mandatory=is_mandatory,
                                     return_list=return_list)

            if obs_path is not None:
                return obs_path, time_info

        # if no files are found return None
        # if offsets are specified, log error with list offsets used
        log_message = "Could not find observation file"
        if offsets != [0]:
            log_message = (f"{log_message} using offsets "
                           f"{','.join([str(offset) for offset in offsets])}")

        # if mandatory, report error, otherwise report warning
        if mandatory:
            self.log_error(log_message)
        else:
            self.logger.warning(log_message)

        return None, time_info

    def find_data(self, time_info, var_info=None, data_type='', mandatory=True,
                  return_list=False, allow_dir=False):
        """! Finds the data file to compare
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param data_type type of data to find (i.e. FCST_ or OBS_)
                @param mandatory if True, report error if not found, warning
                 if not. default is True
                @rtype string
                @return Returns the path to an observation file
        """

        data_type_fmt = data_type
        # add underscore at end of data_type if not found unless empty string
        if data_type and not data_type.endswith('_'):
            data_type_fmt += '_'

        if var_info is not None:
            # set level based on input data type
            if data_type_fmt.startswith("OBS"):
                v_level = var_info['obs_level']
            else:
                v_level = var_info['fcst_level']

            # separate character from beginning of numeric
            # level value if applicable
            level = util.split_level(v_level)[1]

            # set level to 0 character if it is not a number
            if not level.isdigit():
                level = '0'
        else:
            level = '0'

        # if level is a range, use the first value, i.e. if 250-500 use 250
        level = level.split('-')[0]

        # if level is in hours, convert to seconds
        level = get_seconds_from_string(level, 'H')

        # arguments for find helper functions
        arg_dict = {'level': level,
                    'data_type': data_type_fmt,
                    'mandatory': mandatory,
                    'time_info': time_info,
                    'return_list': return_list}

        # if looking for a file with an exact time match:
        if (self.c_dict.get(data_type_fmt + 'FILE_WINDOW_BEGIN', 0) == 0 and
                self.c_dict.get(data_type_fmt + 'FILE_WINDOW_END', 0) == 0):

            return self.find_exact_file(**arg_dict, allow_dir=allow_dir)

        # if looking for a file within a time window:
        return self.find_file_in_window(**arg_dict)

    def find_exact_file(self, level, data_type, time_info, mandatory=True,
                        return_list=False, allow_dir=False):
        input_template = self.c_dict.get(f'{data_type}INPUT_TEMPLATE', '')
        data_dir = self.c_dict.get(f'{data_type}INPUT_DIR', '')

        if not input_template:
            self.log_error(f"Could not find any {data_type}INPUT files "
                           "because no template was specified")
            return None

        check_file_list = []
        found_file_list = []

        # check if there is a list of files provided in the template
        # process each template in the list (or single template)
        template_list = getlist(input_template)

        # return None if a list is provided for a wrapper that doesn't allow
        # multiple files to be processed
        if (len(template_list) > 1 and
                not self.c_dict.get('ALLOW_MULTIPLE_FILES', False)):
            self.log_error("List of templates specified for a wrapper that "
                           "does not allow multiple files to be provided.")
            return None

        # pop level from time_info to avoid conflict with explicit level
        # then add it back after the string sub call
        saved_level = time_info.pop('level', None)

        input_must_exist = self.c_dict.get('INPUT_MUST_EXIST', True)

        for template in template_list:
            # perform string substitution
            filename = do_string_sub(template,
                                     level=level,
                                     **time_info)

            # build full path with data directory and filename
            full_path = os.path.join(data_dir, filename)

            if os.path.sep not in full_path:
                self.logger.debug(f"{full_path} is not a file path. "
                                  "Returning that string.")
                check_file_list.append(full_path)
                input_must_exist = False
                continue

            self.logger.debug(f"Looking for {data_type}INPUT file {full_path}")

            # if wildcard expression, get all files that match
            if '?' in full_path or '*' in full_path:

                wildcard_files = sorted(glob.glob(full_path))
                self.logger.debug(f'Wildcard file pattern: {full_path}')
                self.logger.debug(f'{str(len(wildcard_files))} files '
                                  'match pattern')

                # add files to list of files
                for wildcard_file in wildcard_files:
                    check_file_list.append(wildcard_file)
            else:
                # add single file to list
                check_file_list.append(full_path)

        # if it was set, add level back to time_info
        if saved_level:
            time_info['level'] = saved_level

        # if multiple files are not supported by the wrapper and multiple
        # files are found, error and exit
        # this will allow a wildcard to be used to find a single file.
        # Previously a wildcard would produce
        # an error if only 1 file is allowed.
        if (not self.c_dict.get('ALLOW_MULTIPLE_FILES', False) and
                len(check_file_list) > 1):
            self.log_error("Multiple files found when wrapper does not "
                           "support multiple files.")
            return None

        # return None if no files were found
        if not check_file_list:
            msg = f"Could not find any {data_type}INPUT files"
            if not mandatory or not self.c_dict.get('MANDATORY', True):
                self.logger.warning(msg)
            else:
                self.log_error(msg)

            return None

        for file_path in check_file_list:
            # if file doesn't need to exist, skip check
            if not input_must_exist:
                found_file_list.append(file_path)
                continue

            # check if file exists
            input_data_type = self.c_dict.get(data_type + 'INPUT_DATATYPE', '')
            processed_path = util.preprocess_file(file_path,
                                                  input_data_type,
                                                  self.config,
                                                  allow_dir=allow_dir)

            # report error if file path could not be found
            if not processed_path:
                msg = (f"Could not find {data_type}INPUT file {file_path} "
                       f"using template {template}")
                if not mandatory or not self.c_dict.get('MANDATORY', True):
                    self.logger.warning(msg)
                    if self.c_dict.get(f'{data_type}FILL_MISSING'):
                        found_file_list.append(f'MISSING{file_path}')
                        continue
                else:
                    self.log_error(msg)

                return None

            if os.path.isdir(processed_path):
                self.logger.debug(f"Found directory: {processed_path}")
            else:
                self.logger.debug(f"Found file: {processed_path}")
            found_file_list.append(processed_path)

        # if only one item found and return_list is False, return single item
        if len(found_file_list) == 1 and not return_list:
            return found_file_list[0]

        return found_file_list

    def find_file_in_window(self, level, data_type, time_info, mandatory=True,
                            return_list=False):
        template = self.c_dict[f'{data_type}INPUT_TEMPLATE']
        data_dir = self.c_dict[f'{data_type}INPUT_DIR']

        # convert valid_time to unix time
        valid_time = time_info['valid_fmt']
        valid_seconds = int(datetime.strptime(valid_time, "%Y%m%d%H%M%S").strftime("%s"))
        # get time of each file, compare to valid time, save best within range
        closest_files = []
        closest_time = 9999999

        # get range of times that will be considered
        valid_range_lower = self.c_dict.get(data_type + 'FILE_WINDOW_BEGIN', 0)
        valid_range_upper = self.c_dict.get(data_type + 'FILE_WINDOW_END', 0)
        lower_limit = int(datetime.strptime(util.shift_time_seconds(valid_time, valid_range_lower),
                                            "%Y%m%d%H%M%S").strftime("%s"))
        upper_limit = int(datetime.strptime(util.shift_time_seconds(valid_time, valid_range_upper),
                                            "%Y%m%d%H%M%S").strftime("%s"))

        msg = f"Looking for {data_type}INPUT files under {data_dir} within range " +\
              f"[{valid_range_lower},{valid_range_upper}] using template {template}"
        self.logger.debug(msg)

        if not data_dir:
            self.log_error('Must set INPUT_DIR if looking for files within a time window')
            return None

        # step through all files under input directory in sorted order
        for dirpath, _, all_files in os.walk(data_dir):
            for filename in sorted(all_files):
                fullpath = os.path.join(dirpath, filename)

                # remove input data directory to get relative path
                rel_path = fullpath.replace(f'{data_dir}/', "")
                # extract time information from relative path using template
                file_time_info = get_time_from_file(rel_path, template, self.logger)
                if file_time_info is None:
                    continue

                # get valid time and check if it is within the time range
                file_valid_time = file_time_info['valid'].strftime("%Y%m%d%H%M%S")
                # skip if could not extract valid time
                if not file_valid_time:
                    continue
                file_valid_dt = datetime.strptime(file_valid_time, "%Y%m%d%H%M%S")
                file_valid_seconds = int(file_valid_dt.strftime("%s"))
                # skip if outside time range
                if file_valid_seconds < lower_limit or file_valid_seconds > upper_limit:
                    continue

                # if only 1 file is allowed, check if file is
                # closer to desired valid time than previous match
                if not self.c_dict.get('ALLOW_MULTIPLE_FILES', False):
                    diff = abs(valid_seconds - file_valid_seconds)
                    if diff < closest_time:
                        closest_time = diff
                        del closest_files[:]
                        closest_files.append(fullpath)
                # if multiple files are allowed, get all files within range
                else:
                    closest_files.append(fullpath)

        if not closest_files:
            msg = f"Could not find {data_type}INPUT files under {data_dir} within range " +\
                  f"[{valid_range_lower},{valid_range_upper}] using template {template}"
            if not mandatory:
                self.logger.warning(msg)
            else:
                self.log_error(msg)

            return None

        # check if file(s) needs to be preprocessed before returning the path
        # if one file was found and return_list if False, return single file
        if len(closest_files) == 1 and not return_list:
            return util.preprocess_file(closest_files[0],
                                        self.c_dict.get(data_type + 'INPUT_DATATYPE', ''),
                                        self.config)

        # return list if multiple files are found
        out = []
        for close_file in closest_files:
            outfile = util.preprocess_file(close_file,
                                           self.c_dict.get(data_type + 'INPUT_DATATYPE', ''),
                                           self.config)
            out.append(outfile)

        return out

    def find_input_files_ensemble(self, time_info, fill_missing=True):
        """! Get a list of all input files and optional control file.
        Warn and remove control file if found in ensemble list. Ensure that
        if defined, the number of ensemble members (N_MEMBERS) corresponds to
        the file list that was found.

            @param time_info dictionary containing timing information
            @param fill_missing If True, fill list of files with MISSING so
            that number of files matches number of expected members. Defaults
            to True.
            @returns True on success
        """

        # get control file if requested
        if self.c_dict.get('CTRL_INPUT_TEMPLATE'):
            ctrl_file = self.find_data(time_info, data_type='CTRL')

            # return if requested control file was not found
            if not ctrl_file:
                return False

            self.args.append(f'-ctrl {ctrl_file}')

        # if explicit file list file is specified, use it and
        # bypass logic to error check model files
        if self.c_dict.get('FCST_INPUT_FILE_LIST'):
            file_list_path = do_string_sub(self.c_dict['FCST_INPUT_FILE_LIST'],
                                           **time_info)
            self.logger.debug(f"Explicit file list file: {file_list_path}")
            if not os.path.exists(file_list_path):
                self.log_error("Could not find file list file")
                return False

            self.infiles.append(file_list_path)
            return True

        # get list of ensemble files to process
        input_files = self.find_model(time_info, return_list=True)
        if not input_files:
            self.log_error("Could not find any input files")
            return False

        # if control file is requested, remove it from input list
        if self.c_dict.get('CTRL_INPUT_TEMPLATE'):

            # check if control file is found in ensemble list
            if ctrl_file in input_files:
                # warn and remove control file if found
                self.logger.warning(f"Control file found in ensemble list: "
                                    f"{ctrl_file}. Removing from list.")
                input_files.remove(ctrl_file)

        # compare number of files found to expected number of members
        if not fill_missing:
            self.logger.debug('Skipping logic to fill file list with MISSING')
        elif not self._check_expected_ensembles(input_files):
            return False

        # write file that contains list of ensemble files
        list_filename = (f"{time_info['init_fmt']}_"
                         f"{time_info['lead_hours']}_{self.app_name}.txt")
        list_file = self.write_list_file(list_filename, input_files)
        if not list_file:
            self.log_error("Could not write filelist file")
            return False

        self.infiles.append(list_file)

        return True

    def _check_expected_ensembles(self, input_files):
        """! Helper function for find_input_files_ensemble().
        If number of expected ensemble members was defined in the config,
        then ensure that the number of files found correspond to the expected
        number. If more files were found, error and return False. If fewer
        files were found, fill in input_files list with MISSING to allow valid
        threshold check inside MET tool to work properly.
        """
        num_expected = self.c_dict['N_MEMBERS']

        # if expected members count is unset, skip check
        if num_expected == MISSING_DATA_VALUE:
            return True

        num_found = len(input_files)

        # error and return if more than expected number was found
        if num_found > num_expected:
            self.log_error(
                "Found more files than expected! "
                f"Found {num_found} expected {num_expected}. "
                "Adjust wildcard expression in template or adjust "
                "number of expected members (N_MEMBERS). "
                f"Files found: {input_files}"
            )
            return False

        # if fewer files found than expected, warn and add fake files
        if num_found < num_expected:
            self.logger.warning(
                f"Found fewer files than expected. "
                f"Found {num_found} expected {num_expected}"
            )
            # add fake files to list for ens_thresh checking
            diff = num_expected - num_found
            self.logger.warning(f'Adding {diff} fake files to '
                                'ensure ens_thresh check is accurate')
            for _ in range(0, diff, 1):
                input_files.append('MISSING')

        return True

    def write_list_file(self, filename, file_list, output_dir=None):
        """! Writes a file containing a list of filenames to the staging dir

            @param filename name of ascii file to write
            @param file_list list of files to write to ascii file
            @param output_dir (Optional) directory to write files. If None,
             ascii files are written to {STAGING_DIR}/file_lists
            @returns path to output file
        """
        if output_dir is None:
            list_dir = os.path.join(self.config.getdir('STAGING_DIR'),
                                    'file_lists')
        else:
            list_dir = output_dir

        list_path = os.path.join(list_dir, filename)

        if not os.path.exists(list_dir):
            os.makedirs(list_dir, mode=0o0775)

        self.logger.debug("Writing list of filenames...")
        with open(list_path, 'w') as file_handle:
            file_handle.write('file_list\n')
            for f_path in file_list:
                self.logger.debug(f"Adding file to list: {f_path}")
                file_handle.write(f_path + '\n')

        self.logger.debug(f"Wrote list of filenames to {list_path}")
        return list_path

    def find_and_check_output_file(self, time_info=None,
                                   is_directory=False,
                                   output_path_template=None,
                                   check_extension=None):
        """!Build full path for expected output file and check if it exists.
            If output file doesn't exist or it does exists and we are not
            skipping it then return True to run the tool.
            Otherwise return False to not run the tool

            @param time_info time dictionary to use to fill out output file
             template
            @param is_directory If True, check in output directory for
             any files that match the pattern
             {app_name}_{output_prefix}*YYYYMMDD_HHMMSSV*
            @param output_path_template optional filename template to use
             If None, build output path template from c_dict's OUTPUT_DIR
              and OUTPUT_TEMPLATE. Default is None
            @param check_extension optional extension to look for output files
             Used if output path specified in command differs from actual
             filenames that are written (i.e. tc_pairs added .tcst extension
             to output file path specified)
            @returns True if the app should be run or False if it should not
        """
        output_path = output_path_template

        # if output path template not specified, get it from
        # c_dict keys OUTPUT_DIR and OUTPUT_TEMPLATE
        if not output_path:
            output_dir = self.c_dict.get('OUTPUT_DIR', '')
            output_template = self.c_dict.get('OUTPUT_TEMPLATE', '')

            # remove trailing path separator if necessary (directories)
            output_template = output_template.rstrip(os.path.sep)
            output_path = os.path.join(output_dir, output_template)

        # substitute time info if provided
        if time_info:
            output_path = do_string_sub(output_path,
                                        **time_info)

        # replace wildcard character * with all
        output_path = output_path.replace('*', 'all')

        skip_if_output_exists = self.c_dict.get('SKIP_IF_OUTPUT_EXISTS', False)

        # get directory that the output file will exist
        if is_directory:
            parent_dir = output_path
            if time_info and time_info['valid'] != '*':
                valid_format = time_info['valid'].strftime('%Y%m%d_%H%M%S')
            else:
                valid_format = ''

            prefix = self.get_output_prefix(time_info, set_env_vars=False)
            search_string = f"{self.app_name}_{prefix}*{valid_format}V*"
            search_path = os.path.join(output_path,
                                       search_string)
            if skip_if_output_exists:
                self.logger.debug("Looking for existing data that matches: "
                                  f"{search_path}")
            self.outdir = output_path
            output_path = search_path
        else:
            parent_dir = os.path.dirname(output_path)
            # search for {output_path}* for TCGen output
            search_path = f'{output_path}*'
            if check_extension:
                search_path = f'{search_path}{check_extension}'
            self.set_output_path(output_path)

        output_exists = bool(glob.glob(search_path))

        if not parent_dir:
            self.log_error('Must specify path to output file')
            return False

        # create full output dir if it doesn't already exist
        if (not os.path.exists(parent_dir) and
                not self.c_dict.get('DO_NOT_RUN_EXE', False)):
            self.logger.debug(f"Creating output directory: {parent_dir}")
            os.makedirs(parent_dir)

        if not output_exists or not skip_if_output_exists:
            return True

        # if the output file exists and we are supposed to skip, don't run tool
        self.logger.debug(f'Skip writing output {output_path} because it already '
                          'exists. Remove file or change '
                          f'{self.app_name.upper()}_SKIP_IF_OUTPUT_EXISTS to False '
                          'to process')
        return False

    def check_for_externals(self):
        self.check_for_gempak()

    def check_for_gempak(self):
        # check if we are processing Gempak data
        processingGempak = False

        # if any *_DATATYPE keys in c_dict have a value of GEMPAK, we are using Gempak data
        data_types = [value for key,value in self.c_dict.items() if key.endswith('DATATYPE')]
        if 'GEMPAK' in data_types:
            processingGempak = True

        # if any filename templates end with .grd, we are using Gempak data
        template_list = [value for key,value in self.c_dict.items() if key.endswith('TEMPLATE')]

        # handle when template is a list of templates, which happens in EnsembleStat
        templates = []
        for value in template_list:
            if type(value) is list:
                 for subval in value:
                     templates.append(subval)
            else:
                templates.append(value)

        if [value for value in templates if value and value.endswith('.grd')]:
            processingGempak = True

        # If processing Gempak, make sure GempakToCF is found
        if processingGempak:
            gempaktocf_jar = self.config.getstr('exe', 'GEMPAKTOCF_JAR', '')
            self.check_gempaktocf(gempaktocf_jar)

    def check_gempaktocf(self, gempaktocf_jar):
        if not gempaktocf_jar:
            self.log_error("[exe] GEMPAKTOCF_JAR was not set if configuration file. "
                           "This is required to process Gempak data.")
            self.logger.info("Refer to the GempakToCF use case documentation for information "
                             "on how to obtain the tool: parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.py")
            self.isOK = False
        elif not os.path.exists(gempaktocf_jar):
            self.log_error(f"GempakToCF Jar file does not exist at {gempaktocf_jar}. " +
                           "This is required to process Gempak data.")
            self.logger.info("Refer to the GempakToCF use case documentation for information "
                             "on how to obtain the tool: parm/use_cases/met_tool_wrapper/GempakToCF/GempakToCF.py")
            self.isOK = False

    def add_field_info_to_time_info(self, time_info, field_info):
        """!Add name and level values from field info to time info dict to be used in string substitution
            Args:
                @param time_info time dictionary to add items to
                @param field_info field dictionary to get values from
        """
        field_items = ['fcst_name', 'fcst_level', 'obs_name', 'obs_level']
        for field_item in field_items:
            time_info[field_item] = field_info[field_item] if field_item in field_info else ''

    def set_current_field_config(self, field_info=None):
        """! Sets config variables for current fcst/obs name/level that can be
         referenced by other config variables such as OUTPUT_PREFIX.
         Only sets then if CURRENT_VAR_INFO is set in c_dict.

         @param field_info optional dictionary containing field information.
          If not provided, use [config] CURRENT_VAR_INFO
        """
        if not field_info:
            field_info = self.c_dict.get('CURRENT_VAR_INFO', None)

        if field_info is None:
            return

        for fcst_or_obs in ['FCST', 'OBS']:
            for name_or_level in ['NAME', 'LEVEL']:
                current_var = f'CURRENT_{fcst_or_obs}_{name_or_level}'
                name = f'{fcst_or_obs.lower()}_{name_or_level.lower()}'
                self.config.set('config', current_var,
                                field_info[name] if name in field_info else '')

    def check_for_python_embedding(self, input_type, var_info):
        """!Check if field name of given input type is a python script. If it is not, return the field name.
            If it is, check if the input datatype is a valid Python Embedding string, set the c_dict item
            that sets the file_type in the MET config file accordingly, and set the output string to 'python_embedding.
            Used to set up Python Embedding input for MET tools that support multiple input files, such as MTD, EnsembleStat,
            and SeriesAnalysis.
            Args:
              @param input_type type of field input, i.e. FCST, OBS, ENS, POINT_OBS, GRID_OBS, or BOTH
              @param var_info dictionary item containing field information for the current *_VAR<n>_* configs being handled
              @returns field name if not a python script, 'python_embedding' if it is, and None if configuration is invalid"""
        var_input_type = input_type.lower() if input_type != 'BOTH' else 'fcst'
        # reset file type to empty string to handle if python embedding is used for one field but not for the next
        self.c_dict[f'{input_type}_FILE_TYPE'] = ''

        if not util.is_python_script(var_info[f"{var_input_type}_name"]):
            # if not a python script, return var name
            return var_info[f"{var_input_type}_name"]

        # if it is a python script, set file extension to show that and make sure *_INPUT_DATATYPE is a valid PYTHON_* string
        file_ext = 'python_embedding'
        data_type = self.c_dict.get(f'{input_type}_INPUT_DATATYPE', '')
        if data_type not in util.PYTHON_EMBEDDING_TYPES:
            self.log_error(f"{input_type}_{self.app_name.upper()}_INPUT_DATATYPE ({data_type}) must be set to a valid Python Embedding type "
                           f"if supplying a Python script as the {input_type}_VAR<n>_NAME. Valid options: "
                           f"{','.join(util.PYTHON_EMBEDDING_TYPES)}")
            return None

        # set file type string to be set in MET config file to specify Python Embedding is being used for this dataset
        file_type = f"file_type = {data_type};"
        self.c_dict[f'{input_type}_FILE_TYPE'] = file_type
        self.env_var_dict[f'METPLUS_{input_type}_FILE_TYPE'] = file_type
        return file_ext

    def get_field_info(self, d_type='', v_name='', v_level='', v_thresh=None,
                       v_extra='', add_curly_braces=True):
        """! Format field information into format expected by MET config file
              Args:
                @param v_level level of data to extract
                @param v_thresh threshold value to use in comparison
                @param v_name name of field to process
                @param v_extra additional field information to add if available
                @param d_type type of data to find i.e. FCST or OBS
                @param add_curly_braces if True, add curly braces around each
                 field info string. If False, add single quotes around each
                 field info string (defaults to True)
                @rtype string
                @return Returns formatted field information
        """
        # if thresholds are set
        if v_thresh:
            # if neither fcst or obs are probabilistic,
            # pass in all thresholds as a comma-separated list for 1 field info
            if (not self.c_dict.get('FCST_IS_PROB', False) and
                    not self.c_dict.get('OBS_IS_PROB', False)):
                thresholds = [','.join(v_thresh)]
            else:
                thresholds = v_thresh
        # if no thresholds are specified, fail if prob field is in grib PDS
        elif (self.c_dict.get(d_type + '_IS_PROB', False) and
              self.c_dict.get(d_type + '_PROB_IN_GRIB_PDS', False) and
              not util.is_python_script(v_name)):
            self.log_error('No threshold was specified for probabilistic '
                           'forecast GRIB data')
            return None
        else:
            thresholds = [None]

        # list to hold field information
        fields = []

        for thresh in thresholds:
            if (self.c_dict.get(d_type + '_PROB_IN_GRIB_PDS', False) and
                    not util.is_python_script(v_name)):
                field = self._handle_grib_pds_field_info(v_name, v_level,
                                                         thresh)
            else:
                # add field name
                field = f'name="{v_name}";'

                if v_level:
                    field += f' level="{remove_quotes(v_level)}";'

                if self.c_dict.get(d_type + '_IS_PROB', False):
                    field += " prob=TRUE;"

            # handle cat_thresh
            if self.c_dict.get(d_type + '_IS_PROB', False):
                # add probabilistic cat thresh if different from default ==0.1
                cat_thresh = self.c_dict.get(d_type + '_PROB_THRESH')
            else:
                cat_thresh = thresh

            if cat_thresh:
                field += f" cat_thresh=[ {cat_thresh} ];"

            # handle extra options if set
            if v_extra:
                extra = v_extra.strip()
                # if trailing semi-colon is not found, add it
                if not extra.endswith(';'):
                    extra = f"{extra};"
                field += f' {extra}'

            # add curly braces around field info
            if add_curly_braces:
                field = f'{{ {field} }}'
            # otherwise add single quotes around field info
            else:
                field = f"'{field}'"

            # add field info string to list of fields
            fields.append(field)

        # return list of field dictionary items
        return fields

    def _handle_grib_pds_field_info(self, v_name, v_level, thresh):

        field = f'name="PROB"; level="{v_level}"; prob={{ name="{v_name}";'

        if thresh:
            thresh_tuple_list = util.get_threshold_via_regex(thresh)
            for comparison, number in thresh_tuple_list:
                # skip adding thresh_lo or thresh_hi if comparison is NA
                if comparison == 'NA':
                    continue

                if comparison in ["gt", "ge", ">", ">=", "==", "eq"]:
                    field = f"{field} thresh_lo={number};"
                if comparison in ["lt", "le", "<", "<=", "==", "eq"]:
                    field = f"{field} thresh_hi={number};"

        # add closing curly brace for prob=
        return f'{field} }}'

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.log_error('No app path specified. '
                              'You must use a subclass')
            return None

        cmd = '{} -v {}'.format(self.app_path, self.c_dict['VERBOSITY'])

        for arg in self.args:
            cmd += " " + arg

        if not self.infiles:
            self.log_error("No input filenames specified")
            return None

        for infile in self.infiles:
            cmd += " " + infile

        if not self.outfile:
            self.log_error("No output filename specified")
            return None

        out_path = os.path.join(self.outdir, self.outfile)

        # create outdir (including subdir in outfile) if it doesn't exist
        parent_dir = os.path.dirname(out_path)
        if not parent_dir:
            self.log_error('Must specify path to output file')
            return None

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        cmd += " " + out_path

        if self.param:
            cmd += ' ' + self.param

        return cmd

    # Placed running of command in its own class, command_runner run_cmd().
    # This will allow the ability to still call build() as is currently done
    # in subclassed CommandBuilder wrappers and also allow wrappers
    # such as tc_pairs that are not heavily designed around command builder
    # to call cmdrunner.run_cmd().
    # Make sure they have SET THE self.app_name in the subclasses constructor.
    # see regrid_data_plane_wrapper.py as an example of how to set.
    def build(self):
        """!Build and run command"""
        cmd = self.get_command()
        if cmd is None:
            self.log_error("Could not generate command")
            return False

        return self.run_command(cmd)

    def run_command(self, cmd, cmd_name=None):
        """! Run a command with the appropriate environment. Add command to
        list of all commands run.

        @param cmd command to run
        @returns True on success, False otherwise
        """
        # add command to list of all commands run
        self.all_commands.append((cmd,
                                  self.print_all_envs(print_copyable=True)))

        log_name = cmd_name if cmd_name else self.log_name

        if self.instance:
            log_name = f"{log_name}.{self.instance}"

        ret, out_cmd = self.cmdrunner.run_cmd(cmd,
                                              env=self.env,
                                              log_name=log_name,
                                              copyable_env=self.get_env_copy())
        if ret:
            logfile_path = self.config.getstr('config', 'LOG_METPLUS')
            # if MET output is written to its own logfile, get that filename
            if not self.config.getbool('config', 'LOG_MET_OUTPUT_TO_METPLUS'):
                logfile_path = logfile_path.replace('run_metplus',
                                                    log_name)

            self.log_error("MET command returned a non-zero return code:"
                           f"{cmd}")
            self.logger.info("Check the logfile for more information on why "
                             f"it failed: {logfile_path}")
            return False

        return True

    # argument needed to match call
    # pylint:disable=unused-argument
    def run_at_time(self, input_dict):
        """! Used to output error and exit if wrapper is attempted to be run
         with LOOP_ORDER = times and the run_at_time method is not implemented
        """
        self.log_error(f'run_at_time not implemented for {self.log_name} '
                       'wrapper. Cannot run with LOOP_ORDER = times')
        return None

    def run_all_times(self, custom=None):
        """! Loop over time range specified in conf file and
        call METplus wrapper for each time

        @param custom (optional) custom loop string value
        """
        return util.loop_over_times_and_call(self.config, self, custom=custom)

    @staticmethod
    def format_met_config_dict(c_dict, name, keys=None):
        """! Return formatted dictionary named <name> with any <items> if they
        are set to a value. If none of the items are set, return empty string

        @param c_dict config dictionary to read values from
        @param name name of dictionary to create
        @param keys list of c_dict keys to use if they are set. If unset (None)
         then read all keys from c_dict
        @returns MET config formatted dictionary if any items are set, or empty
         string if not
        """
        return format_met_config('dict', c_dict=c_dict, name=name, keys=keys)

    def handle_regrid(self, c_dict, set_to_grid=True):
        dict_items = {}
        if set_to_grid:
            dict_items['to_grid'] = ('string', 'to_grid')

            # handle legacy format of to_grid
            self.add_met_config(
                name='',
                data_type='string',
                env_var_name='REGRID_TO_GRID',
                metplus_configs=[f'{self.app_name.upper()}_REGRID_TO_GRID'],
                extra_args={'to_grid': True},
                output_dict=c_dict,
            )

            # set REGRID_TO_GRID to NONE if unset
            regrid_value = c_dict.get('METPLUS_REGRID_TO_GRID', '')
            if not regrid_value:
                regrid_value = 'NONE'
            c_dict['REGRID_TO_GRID'] = regrid_value
            if 'METPLUS_REGRID_TO_GRID' in c_dict:
                del c_dict['METPLUS_REGRID_TO_GRID']

        dict_items['method'] = ('string', 'uppercase,remove_quotes')
        dict_items['width'] = 'int'
        dict_items['vld_thresh'] = 'float'
        dict_items['shape'] = ('string', 'uppercase,remove_quotes')
        self.add_met_config_dict('regrid', dict_items)

    def handle_description(self):
        """! Get description from config. If <app_name>_DESC is set, use
         that value. If not, check for DESC and use that if it is set.
         If set, set the METPLUS_DESC env_var_dict key to "desc = <value>;"

        """
        # check if <app_name>_DESC is set
        app_name_upper = self.app_name.upper()
        conf_value = self.config.getstr('config',
                                        f'{app_name_upper}_DESC',
                                        '')

        # if not, check if DESC is set
        if not conf_value:
            conf_value = self.config.getstr('config',
                                            'DESC',
                                            '')

        # if the value is set, set the DESC c_dict
        if conf_value:
            self.env_var_dict['METPLUS_DESC'] = (
                f'desc = "{remove_quotes(conf_value)}";'
            )

    def get_output_prefix(self, time_info=None, set_env_vars=True):
        """! Read {APP_NAME}_OUTPUT_PREFIX from config. If time_info is set
         substitute values into filename template tags.

             @param time_info (Optional) dictionary containing time info
             @param set_env_vars (Optional) if True, set env vars with
             values computed from this function
             @returns output prefix with values substituted if requested
        """
        output_prefix = (
            self.config.getraw('config',
                               f'{self.app_name.upper()}_OUTPUT_PREFIX')
        )
        if time_info is None:
            return output_prefix

        output_prefix = do_string_sub(output_prefix,
                                      **time_info)

        if set_env_vars:
            # set METPLUS_OUTPUT_PREFIX in env_var_dict if it is set
            if output_prefix:
                output_prefix_fmt = f'output_prefix = "{output_prefix}";'
                self.env_var_dict['METPLUS_OUTPUT_PREFIX'] = output_prefix_fmt

            # set old method of setting OUTPUT_PREFIX
            self.add_env_var('OUTPUT_PREFIX', output_prefix)

        return output_prefix

    def handle_climo_dict(self):
        """! Read climo mean/stdev variables with and set env_var_dict
         appropriately. Handle previous environment variables that are used
         by wrapped MET configs pre 4.0 (CLIMO_MEAN_FILE and CLIMO_STDEV_FILE)

        """
        items = {
            'file_name': 'list',
            'field': ('list', 'remove_quotes'),
            'regrid': ('dict', '', {
                'method': ('string', 'uppercase,remove_quotes'),
                'width': 'int',
                'vld_thresh': 'float',
                'shape': ('string', 'uppercase,remove_quotes'),
            }),
            'time_interp_method': ('string', 'remove_quotes,uppercase'),
            'match_month': ('bool', 'uppercase'),
            'day_interval': 'int',
            'hour_interval': 'int',
            'file_type': ('string', 'remove_quotes'),
        }
        for climo_type in self.climo_types:
            dict_name = f'climo_{climo_type.lower()}'

            # make sure _FILE_NAME is set from INPUT_TEMPLATE/DIR if used
            self.read_climo_file_name(climo_type)

            self.add_met_config_dict(dict_name, items)

            # handle use_fcst or use_obs options for setting field list
            self.climo_use_fcst_or_obs_fields(dict_name)

            # handle deprecated env vars CLIMO_MEAN_FILE and CLIMO_STDEV_FILE
            # that are used by pre v4.0.0 wrapped MET config files
            env_var_name = f'METPLUS_{dict_name.upper()}_DICT'
            dict_value = self.env_var_dict.get(env_var_name, '')
            match = re.match(r'.*file_name = \[([^\[\]]*)\];.*', dict_value)
            if match:
                file_name = match.group(1)
                self.env_var_dict[f'{dict_name.upper()}_FILE'] = file_name

    def read_climo_file_name(self, climo_type):
        """! Check values for {APP}_CLIMO_{climo_type}_ variables FILE_NAME,
        INPUT_TEMPLATE, and INPUT_DIR. If FILE_NAME is set, use it and warn
        if the INPUT_TEMPLATE/DIR variables are also set. If FILE_NAME is not
        set, read template and dir variables and format the values to set
        FILE_NAME, i.e. the variables:
          GRID_STAT_CLIMO_MEAN_INPUT_TEMPLATE = a, b
          GRID_STAT_CLIMO_MEAN_INPUT_DIR = /some/dir
        will set:
          GRID_STAT_CLIMO_MEAN_FILE_NAME = /some/dir/a, some/dir/b
        Used to support pre v4.0 variables.

            @param climo_type type of climo field (mean or stdev)
        """
        # prefix i.e. GRID_STAT_CLIMO_MEAN_
        prefix = f'{self.app_name.upper()}_CLIMO_{climo_type.upper()}_'

        input_dir = self.config.getdir_nocheck(f'{prefix}INPUT_DIR', '')
        input_template = self.config.getraw('config',
                                            f'{prefix}INPUT_TEMPLATE', '')
        file_name = self.config.getraw('config',
                                       f'{prefix}FILE_NAME', '')

        # if input template is not set, nothing to do
        if not input_template:
            return

        # if input template is set and file name is also set,
        # warn and use file name values
        if file_name:
            self.logger.warning(f'Both {prefix}INPUT_TEMPLATE and '
                                f'{prefix}FILE_NAME are set. Using '
                                f'value set in {prefix}FILE_NAME '
                                f'({file_name})')
            return

        template_list_string = input_template
        # if file name is not set but template is, set file name from template
        # if dir is set and not python embedding,
        # prepend it to each template in list
        if input_dir and input_template not in util.PYTHON_EMBEDDING_TYPES:
            template_list = getlist(input_template)
            for index, template in enumerate(template_list):
                template_list[index] = os.path.join(input_dir, template)

            # change formatted list back to string
            template_list_string = ','.join(template_list)

        self.config.set('config', f'{prefix}FILE_NAME', template_list_string)

    def climo_use_fcst_or_obs_fields(self, dict_name):
        """! If climo field is not explicitly set, check if config is set
         to use forecast or observation fields.

         @param dict_name name of climo to check: climo_mean or climo_stdev
        """
        # if {APP}_CLIMO_[MEAN/STDEV]_FIELD is set, do nothing
        field_conf = f'{self.app_name}_{dict_name}_FIELD'.upper()
        if self.config.has_option('config', field_conf):
            return

        use_fcst_conf = f'{self.app_name}_{dict_name}_USE_FCST'.upper()
        use_obs_conf = f'{self.app_name}_{dict_name}_USE_OBS'.upper()

        use_fcst = self.config.getbool('config', use_fcst_conf, False)
        use_obs = self.config.getbool('config', use_obs_conf, False)

        # if both are set, report an error
        if use_fcst and use_obs:
            self.log_error(f'Cannot set both {use_fcst_conf} and '
                           f'{use_obs_conf} in config.')
            return

        # if neither are set, do nothing
        if not use_fcst and not use_obs:
            return

        env_var_name = f'METPLUS_{dict_name.upper()}_DICT'
        rvalue = 'fcst' if use_fcst else 'obs'

        self.env_var_dict[env_var_name] += f'{dict_name} = {rvalue};'

    def get_wrapper_or_generic_config(self, generic_config_name):
        """! Check for config variable with <APP_NAME>_ prepended first. If set
        use that value. If not, check for config without prefix.

        @param generic_config_name name of variable to read from config
        @returns value if set or empty string if not
        """
        wrapper_config_name = f'{self.app_name.upper()}_{generic_config_name}'
        value = self.config.getstr_nocheck('config',
                                           wrapper_config_name,
                                           '')

        # if wrapper specific variable not set, check for generic
        if not value:
            value = self.config.getstr_nocheck('config',
                                               generic_config_name,
                                               '')

        return value

    def format_field(self, data_type, field_string, is_list=True):
        """! Set {data_type}_FIELD c_dict value to the formatted field string
        Also set {data_type_FIELD_OLD value to support old format until it is
        deprecated.

        @param data_type type of data to set, i.e. FCST, OBS
        @param field_string field information formatted to be read by MET config
        @param is_list if True, add square brackets around field info
        """
        field_formatted = field_string
        if is_list:
            field_formatted = f'[{field_formatted}]'

        self.env_var_dict[f'METPLUS_{data_type}_FIELD'] = (
            f"field = {field_formatted};"
        )
        self.c_dict[f'{data_type}_FIELD'] = field_string

    def handle_flags(self, flag_type):
        """! Handle reading and setting of flag dictionary values to set in
        a MET config file. Sets METPLUS_{flag_type}_FLAG_DICT in the
        env_var_dict.

            @param flag_type type of flag to read, i.e. OUTPUT or ENSEMBLE
        """
        # create variables for upper and lower flag type so that either option
        # can be used as input to the function
        flag_type_upper = flag_type.upper()
        flag_type_lower = flag_type.lower()
        if not hasattr(self, f'{flag_type_upper}_FLAGS'):
            return

        flag_info_dict = {}
        for flag in getattr(self, f'{flag_type_upper}_FLAGS'):
            flag_info_dict[flag] = ('string', 'remove_quotes,uppercase')

        self.add_met_config_dict(f'{flag_type_lower}_flag', flag_info_dict)

    def handle_censor_val_and_thresh(self):
        """! Read {APP_NAME}_CENSOR_[VAL/THRESH] and set
         METPLUS_CENSOR_[VAL/THRESH] in self.env_var_dict so it can be
         referenced in a MET config file
        """
        self.add_met_config(name='censor_thresh',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='censor_val',
                            data_type='list',
                            extra_args={'remove_quotes': True})

    def get_env_var_value(self, env_var_name, read_dict=None, item_type=None):
        """! Read env var value, get text after the equals sign and remove the
        trailing semi-colon.

            @param env_var_name key to obtain
            @param read_dict (Optional) directory to read from. If unset (None)
             then read from self.env_var_dict
            @param item_type if set to list, return [] if variable is unset
            @returns extracted value
        """
        if read_dict is None:
            read_dict = self.env_var_dict

        mask_value = read_dict.get(env_var_name, '')
        if not mask_value:
            if not item_type:
                return ''

            if item_type == 'list':
                return '[]'

        return mask_value.split('=', 1)[1].rstrip(';').strip()

    def handle_time_summary_dict(self):
        """! Read METplusConfig variables for the MET config time_summary
         dictionary and format values into an environment variable
         METPLUS_TIME_SUMMARY_DICT that is referenced in the wrapped MET
         config files.
        """
        app_upper = self.app_name.upper()
        self.add_met_config_dict('time_summary', {
            'flag': 'bool',
            'raw_data': 'bool',
            'beg': 'string',
            'end': 'string',
            'step': 'int',
            'width': ('string', 'remove_quotes'),
            'grib_code': ('list', 'remove_quotes,allow_empty', None,
                          [f'{app_upper}_TIME_SUMMARY_GRIB_CODES']),
            'obs_var': ('list', 'allow_empty', None,
                        [f'{app_upper}_TIME_SUMMARY_VAR_NAMES']),
            'type': ('list', 'allow_empty', None,
                     [f'{app_upper}_TIME_SUMMARY_TYPES']),
            'vld_freq': ('int', None, None,
                         [f'{app_upper}_TIME_SUMMARY_VALID_FREQ']),
            'vld_thresh': ('float', None, None,
                           [f'{app_upper}_TIME_SUMMARY_VALID_THRESH']),
        })

    def handle_mask(self, single_value=False, get_flags=False):
        """! Read mask dictionary values and set them into env_var_list

            @param single_value if True, only a single value for grid and poly
            are allowed. If False, they should be treated as as list
            @param get_flags if True, read grid_flag and poly_flag values
        """
        data_type = 'string' if single_value else 'list'
        app_upper = self.app_name.upper()
        items = {
            'grid': (data_type, 'allow_empty', None,
                     [f'{app_upper}_GRID']),
            'poly': (data_type, 'allow_empty', None,
                     [f'{app_upper}_VERIFICATION_MASK_TEMPLATE',
                      f'{app_upper}_POLY']),
        }

        if get_flags:
            items['grid_flag'] = ('string', 'remove_quotes,uppercase')
            items['poly_flag'] = ('string', 'remove_quotes,uppercase')

        self.add_met_config_dict('mask', items)

    def add_met_config_dict(self, dict_name, items):
        """! Read config variables for MET config dictionary and set
         env_var_dict with formatted values

        @params dict_name name of MET dictionary variable
        @params items dictionary where the key is name of variable inside MET
         dictionary and the value is info about the item (see parse_item_info
         function for more information)
        """
        return_code = add_met_config_dict(config=self.config,
                                          app_name=self.app_name,
                                          output_dict=self.env_var_dict,
                                          dict_name=dict_name,
                                          items=items)
        if not return_code:
            self.isOK = False

        return return_code

    def add_met_config_window(self, dict_name):
        """! Handle a MET config window dictionary. It is assumed that
        the dictionary only contains 'beg' and 'end' entries that are integers.

        @param dict_name name of MET dictionary
        """
        self.add_met_config_dict(dict_name, {
            'beg': 'int',
            'end': 'int',
        })

    def add_met_config(self, **kwargs):
        """! Create METConfig object from arguments and process
             @param kwargs key arguments that should match METConfig
              arguments, which includes the following:
             @param name MET config variable name to set
             @param data_type type of variable to set, i.e. string, list, bool
             @param env_var_name environment variable name to set (uses
              name if not set) with or without METPLUS_ prefix
             @param metplus_configs variables from METplus config that should
              be read to get the value. This can be a list of variable names
              in order of precedence (first variable is used if it is set,
              otherwise 2nd variable is used if set, etc.)
        """
        # if metplus_configs is not provided, use <APP_NAME>_<MET_CONFIG_NAME>
        if not kwargs.get('metplus_configs'):
            kwargs['metplus_configs'] = [
                f"{self.app_name}_{kwargs.get('name')}".upper()
            ]
        item = METConfig(**kwargs)
        output_dict = kwargs.get('output_dict', self.env_var_dict)
        if not add_met_config_item(self.config, item, output_dict):
            self.isOK = False

    def get_config_file(self, default_config_file=None):
        """! Get the MET config file path for the wrapper from the
        METplusConfig object. If unset, use the default value if provided.

        @param default_config_file (optional) filename of wrapped MET config
         file found in parm/met_config to use if config file is not set
        @returns path to wrapped config file or None if no default is provided
        """
        return get_wrapped_met_config_file(self.config,
                                           self.app_name,
                                           default_config_file)

    def handle_climo_cdf_dict(self, write_bins=True):
        items = {
            'cdf_bins': ('float', None, None,
                         [f'{self.app_name.upper()}_CLIMO_CDF_BINS']),
            'center_bins': 'bool',
        }

        # add write_bins unless it should be excluded
        if write_bins:
            items['write_bins'] = 'bool'

        items['direct_prob'] = 'bool'
        self.add_met_config_dict('climo_cdf', items)
