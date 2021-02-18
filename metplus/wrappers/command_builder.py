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

import os
import sys
import glob
from datetime import datetime
from abc import ABCMeta
from inspect import getframeinfo, stack

from .command_runner import CommandRunner
from ..util import met_util as util
from ..util import do_string_sub, ti_calculate, get_seconds_from_string
from ..util import config_metplus

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

    def __init__(self, config, instance=None, config_overrides={}):
        self.isOK = True
        self.errors = 0
        self.config = config
        self.logger = config.logger
        self.env_list = set()
        self.debug = False
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
        ]
        if hasattr(self, 'WRAPPER_ENV_VAR_KEYS'):
            self.env_var_keys.extend(self.WRAPPER_ENV_VAR_KEYS)

        # if instance is set, check for a section with the same name in the
        # METplusConfig object. If found, copy all values into the config
        if instance:
            self.config = (
                config_metplus.replace_config_from_section(self.config,
                                                           instance,
                                                           required=False)
            )

        self.instance = instance

        # override config if any were supplied
        self.override_config(config_overrides)

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

        self.check_for_externals()

        self.cmdrunner = CommandRunner(self.config, logger=self.logger,
                                       verbose=self.c_dict['VERBOSITY'])

        # set log name to app name by default
        # any wrappers with a name different than the primary app that is run
        # should override this value in their init function after the call
        # to the parent init function
        self.log_name = self.app_name if hasattr(self, 'app_name') else ''

        self.clear()

    def override_config(self, config_overrides):
        if not config_overrides:
            return

        self.logger.debug("Overriding config with explicit values:")
        for key, value in config_overrides.items():
            self.logger.debug(f"Setting [config] {key} = {value}")
            self.config.set('config', key, value)

    def check_for_unused_env_vars(self):
        config_file = self.c_dict.get('CONFIG_FILE')
        if not config_file:
            return

        if not hasattr(self, 'WRAPPER_ENV_VAR_KEYS'):
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

        c_dict['CUSTOM_LOOP_LIST'] = util.get_custom_string_list(self.config,
                                                                 app_name)

        c_dict['SKIP_TIMES'] = util.get_skip_times(self.config,
                                                   app_name)

        c_dict['USE_EXPLICIT_NAME_AND_LEVEL'] = (
            self.config.getbool('config',
                                'USE_EXPLICIT_NAME_AND_LEVEL',
                                False)
            )

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
        for msg in self.print_all_envs():
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

    @staticmethod
    def format_regrid_to_grid(to_grid):
        to_grid = to_grid.strip('"')
        if not to_grid:
            to_grid = 'NONE'

        # if not surrounded by quotes and not NONE, FCST or OBS, add quotes
        if to_grid not in ['NONE', 'FCST', 'OBS']:
            to_grid = f'"{to_grid}"'

        return to_grid

    def print_all_envs(self, print_copyable=True):
        """! Create list of log messages that output all environment variables
        that were set by this wrapper.

        @param print_copyable if True, also output a list of shell commands
        that can be easily copied and pasted into a browser to recreate the
        environment that was set when the command was run
        @returns list of log messages
        """
        msg = ["ENVIRONMENT FOR NEXT COMMAND: "]
        for env_item in sorted(self.env_list):
            msg.append(self.print_env_item(env_item))

        if print_copyable:
            msg.append("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
            msg.append(self.get_env_copy())

        return msg

    def handle_window_once(self, input_list, default_val=0):
        """! Check and set window dictionary variables like
              OBS_WINDOW_BEG or FCST_FILE_WINDW_END

             @param input_list list of config keys to check for value
             @param default_val value to use if none of the input keys found
        """
        for input_key in input_list:
            if self.config.has_option('config', input_key):
                return self.config.getseconds('config', input_key)

        return default_val

    def handle_obs_window_variables(self, c_dict):
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

        keys = []
        tmp_dict = {}
        for edge, default_val in edges:
            input_list = [f'OBS_{app}_WINDOW_{edge}',
                          f'OBS_WINDOW_{edge}',
                         ]
            output_key = f'OBS_WINDOW_{edge}'
            value = self.handle_window_once(input_list, default_val)
            c_dict[output_key] = value
            if edge == 'BEGIN':
                edge = 'BEG'
            tmp_dict[output_key] = f'{edge.lower()} = {value};'
            # if something other than the default is used, add output key
            # to the list of items to add to the env_var_dict value
            if value != default_val:
                keys.append(output_key)

        window_str = self.format_met_config_dict(tmp_dict, 'obs_window', keys)
        self.env_var_dict['METPLUS_OBS_WINDOW_DICT'] = window_str

    def handle_file_window_variables(self, c_dict, dtypes=['FCST', 'OBS']):
        """! Handle all window config variables like
              [FCST/OBS]_<app_name>_WINDOW_[BEGIN/END] and
              [FCST/OBS]_<app_name>_FILE_WINDOW_[BEGIN/END]
              Args:
                @param c_dict dictionary to set items in
        """
        edges = ['BEGIN', 'END']
        app = self.app_name.upper()

        for dtype in dtypes:
            for edge in edges:
                input_list = [f'{dtype}_{app}_FILE_WINDOW_{edge}',
                               f'{dtype}_FILE_WINDOW_{edge}',
                               f'FILE_WINDOW_{edge}',
                               ]
                output_key = f'{dtype}_FILE_WINDOW_{edge}'
                value = self.handle_window_once(input_list, 0)
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

        shell = self.config.getstr('config', 'USER_SHELL', 'bash').lower()
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
        template_list = util.getlist(input_template)

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
                return full_path

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
            if not self.c_dict.get('INPUT_MUST_EXIST', True):
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
                file_time_info = util.get_time_from_file(rel_path, template, self.logger)
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

        self.logger.debug(f"Writing list of filenames to {list_path}")
        with open(list_path, 'w') as file_handle:
            file_handle.write('file_list\n')
            for f_path in file_list:
                self.logger.debug(f"Adding file to list: {f_path}")
                file_handle.write(f_path + '\n')

        return list_path

    def find_and_check_output_file(self, time_info=None,
                                   is_directory=False,
                                   output_path_template=None):
        """!Build full path for expected output file and check if it exists.
            If output file doesn't exist or it does exists and we are not skipping it
            then return True to run the tool. Otherwise return False to not run the tool
            Args:
                @param time_info time dictionary to use to fill out output file template
                @param is_directory If True, check in output directory for
                 any files that match the pattern
                 {app_name}_{output_prefix}*YYYYMMDD_HHMMSSV*
                 @param output_path_template optional filename template to use
                  If None, build output path template from c_dict's OUTPUT_DIR
                  and OUTPUT_TEMPLATE. Default is None
                @returns True if the app should be run or False if it should not
        """
        if not output_path_template:
            output_path_template = (
                os.path.join(self.c_dict.get('OUTPUT_DIR',
                                             ''),
                            self.c_dict.get('OUTPUT_TEMPLATE',
                                            '')).rstrip('/')
        )

        if time_info:
            output_path = do_string_sub(output_path_template,
                                        **time_info)
        else:
            output_path = output_path_template

        skip_if_output_exists = self.c_dict.get('SKIP_IF_OUTPUT_EXISTS', False)

        # get directory that the output file will exist
        if is_directory:
            parent_dir = output_path
            if time_info:
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
            self.set_output_path(output_path)

        output_exists = bool(glob.glob(search_path))

        if not parent_dir:
            self.log_error('Must specify path to output file')
            return False

        # create full output dir if it doesn't already exist
        if not os.path.exists(parent_dir):
            self.logger.debug(f"Creating output directory: {parent_dir}")
            os.makedirs(parent_dir)

        if (not output_exists or not skip_if_output_exists):
            return True

        # if the output file exists and we are supposed to skip, don't run tool
        self.logger.debug(f'Skip writing output {output_path} because it already '
                          'exists. Remove file or change '
                          f'{self.app_name.upper()}_SKIP_IF_OUTPUT_EXISTS to False '
                          'to process')
        return False

    def format_list_string(self, list_string):
        """!Add quotation marks around each comma separated item in the string"""
        strings = []
        for string in list_string.split(','):
            string = string.strip().replace('\'', '\"')
            if not string:
                continue
            if string[0] != '"' and string[-1] != '"':
                string = f'"{string}"'
            strings.append(string)

        return ','.join(strings)

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
        """!Sets config variables for current fcst/obs name/level that can be referenced
            by other config variables such as OUTPUT_PREFIX. Only sets then if CURRENT_VAR_INFO
            is set in c_dict.
            Args:
                @param field_info optional dictionary containing field information. If not provided, use
                [config] CURRENT_VAR_INFO
        """
        if not field_info:
            field_info = self.c_dict.get('CURRENT_VAR_INFO', None)

        if field_info is not None:

            self.config.set('config', 'CURRENT_FCST_NAME',
                            field_info['fcst_name'] if 'fcst_name' in field_info else '')
            self.config.set('config', 'CURRENT_OBS_NAME',
                            field_info['obs_name'] if 'obs_name' in field_info else '')
            self.config.set('config', 'CURRENT_FCST_LEVEL',
                            field_info['fcst_level'] if 'fcst_level' in field_info else '')
            self.config.set('config', 'CURRENT_OBS_LEVEL',
                            field_info['obs_level'] if 'obs_level' in field_info else '')

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

    def get_field_info(self, d_type, v_name, v_level='', v_thresh=[], v_extra=''):
        """! Format field information into format expected by MET config file
              Args:
                @param v_level level of data to extract
                @param v_thresh threshold value to use in comparison
                @param v_name name of field to process
                @param v_extra additional field information to add if available
                @param d_type type of data to find i.e. FCST or OBS
                @rtype string
                @return Returns formatted field information
        """
        # separate character from beginning of numeric level value if applicable
        _, level = util.split_level(v_level)

        # list to hold field information
        fields = []

        # get cat thresholds if available
        cat_thresh = ""
        threshs = [None]
        if len(v_thresh) != 0:
            threshs = v_thresh
            cat_thresh = "cat_thresh=[ " + ','.join(threshs) + " ];"

        # if neither input is probabilistic, add all cat thresholds to same field info item
        if not self.c_dict.get('FCST_IS_PROB', False) and not self.c_dict.get('OBS_IS_PROB', False):
            field_name = v_name

            field = "{ name=\"" + field_name + "\";"

            # add level if it is set
            if v_level:
                field += " level=\"" + util.remove_quotes(v_level) + "\";"

            # add threshold if it is set
            if cat_thresh:
                field += ' ' + cat_thresh

            # add extra info if it is set
            if v_extra:
                field += ' ' + v_extra

            field += ' }'
            fields.append(field)

        # if either input is probabilistic, create separate item for each threshold
        else:

            # if input currently being processed if probabilistic, format accordingly
            if self.c_dict.get(d_type + '_IS_PROB', False):
                # if probabilistic data for either fcst or obs, thresholds are required
                # to be specified or no field items will be created. Create a field dict
                # item for each threshold value
                for thresh in threshs:
                    # if utilizing python embedding for prob input, just set the
                    # field name to the call to the script
                    if util.is_python_script(v_name):
                        field = "{ name=\"" + v_name + "\"; prob=TRUE;"
                    elif self.c_dict[d_type + '_INPUT_DATATYPE'] == 'NETCDF' or \
                      not self.c_dict[d_type + '_PROB_IN_GRIB_PDS']:
                        field = "{ name=\"" + v_name + "\";"
                        if v_level:
                            field += " level=\"" + util.remove_quotes(v_level) + "\";"
                        field += " prob=TRUE;"
                    else:
                        # a threshold value is required for GRIB prob DICT data
                        if thresh is None:
                            self.log_error('No threshold was specified for probabilistic '
                                           'forecast GRIB data')
                            return None

                        thresh_str = ""
                        thresh_tuple_list = util.get_threshold_via_regex(thresh)
                        for comparison, number in thresh_tuple_list:
                            # skip adding thresh_lo or thresh_hi if comparison is NA
                            if comparison == 'NA':
                                continue

                            if comparison in ["gt", "ge", ">", ">=", "==", "eq"]:
                                thresh_str += "thresh_lo=" + str(number) + "; "
                            if comparison in ["lt", "le", "<", "<=", "==", "eq"]:
                                thresh_str += "thresh_hi=" + str(number) + "; "

                        field = "{ name=\"PROB\"; level=\"" + v_level + \
                                "\"; prob={ name=\"" + v_name + \
                                "\"; " + thresh_str + "}"

                    # add probabilistic cat thresh if different from default ==0.1
                    prob_cat_thresh = self.c_dict[d_type + '_PROB_THRESH']
                    if prob_cat_thresh is not None:
                        field += " cat_thresh=[" + prob_cat_thresh + "];"

                    if v_extra:
                        field += ' ' + v_extra

                    field += ' }'
                    fields.append(field)
            else:
                field_name = v_name

                for thresh in threshs:
                    field = "{ name=\"" + field_name + "\";"

                    if v_level:
                        field += " level=\"" + util.remove_quotes(v_level) + "\";"

                    if thresh is not None:
                        field += " cat_thresh=[ " + str(thresh) + " ];"

                    if v_extra:
                        field += ' ' + v_extra

                    field += ' }'
                    fields.append(field)

        # return list of field dictionary items
        return fields

    def read_mask_poly(self):
        """! Read old or new config variables used to set mask.poly in MET
             config files

            @returns value from config or empty string if neither variable
             is set
        """
        app = self.app_name.upper()
        conf_value = self.config.getraw('config', f'{app}_MASK_POLY', '')
        if not conf_value:
            conf_value = (
                self.config.getraw('config',
                                   f'{app}_VERIFICATION_MASK_TEMPLATE',
                                   '')
        )
        return conf_value

    def get_verification_mask(self, time_info):
        """!If verification mask template is set in the config file,
            use it to find the verification mask filename"""
        template = self.c_dict.get('MASK_POLY_TEMPLATE')
        if not template:
            return

        filenames = do_string_sub(template,
                                  **time_info)
        mask_list_string = self.format_list_string(filenames)
        self.c_dict['VERIFICATION_MASK'] = mask_list_string
        mask_fmt = f"poly = [{mask_list_string}];"
        self.c_dict['MASK_POLY'] = mask_fmt
        self.env_var_dict['METPLUS_MASK_POLY'] = mask_fmt

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

    def run_command(self, cmd):
        """! Run a command with the appropriate environment. Add command to
        list of all commands run.

        @param cmd command to run
        @returns True on success, False otherwise
        """
        # add command to list of all commands run
        self.all_commands.append((cmd,
                                  self.print_all_envs(print_copyable=False)))

        if self.instance:
            log_name = f"{self.log_name}.{self.instance}"
        else:
            log_name = self.log_name

        ismetcmd = self.c_dict.get('IS_MET_CMD', True)
        run_inshell = self.c_dict.get('RUN_IN_SHELL', False)
        log_theoutput = self.c_dict.get('LOG_THE_OUTPUT', False)

        ret, out_cmd = self.cmdrunner.run_cmd(cmd,
                                              env=self.env,
                                              ismetcmd=ismetcmd,
                                              log_name=log_name,
                                              run_inshell=run_inshell,
                                              log_theoutput=log_theoutput,
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
        """!Used to output error and exit if wrapper is attemped to be run with
            LOOP_ORDER = times and the run_at_time method is not implemented"""
        self.log_error('run_at_time not implemented for {} wrapper. '
                          'Cannot run with LOOP_ORDER = times'.format(self.log_name))
        return None

    def run_all_times(self):
        """!Loop over time range specified in conf file and
        call METplus wrapper for each time"""
        return util.loop_over_times_and_call(self.config, self)

    def set_time_dict_for_single_runtime(self, c_dict):
        # get clock time from start of execution for input time dictionary
        clock_time_obj = datetime.strptime(self.config.getstr('config', 'CLOCK_TIME'),
                                           '%Y%m%d%H%M%S')

        # get start run time and set INPUT_TIME_DICT
        c_dict['INPUT_TIME_DICT'] = {'now': clock_time_obj}
        start_time, _, _ = util.get_start_end_interval_times(self.config)
        if start_time:
            # set init or valid based on LOOP_BY
            use_init = util.is_loop_by_init(self.config)
            if use_init is None:
                self.isOK = False
            elif use_init:
                c_dict['INPUT_TIME_DICT']['init'] = start_time
            else:
                c_dict['INPUT_TIME_DICT']['valid'] = start_time
        else:
            self.config.logger.error("Could not get [INIT/VALID] time information from configuration file")
            self.isOK = False

    def set_met_config_list(self, c_dict, mp_config, met_config_name,
                            c_dict_key=None, remove_quotes=False,
                            allow_empty=False):
        """! Get list from METplus configuration file and format it to be passed
              into a MET configuration file. Set c_dict item with formatted string.
             Args:
                 @param c_dict configuration dictionary to set
                 @param mp_config_name METplus configuration variable name. Assumed to be
                  in the [config] section. Value can be a comma-separated list of items.
                 @param met_config name of MET configuration variable to set. Also used
                  to determine the key in c_dict to set (upper-case)
                 @param c_dict_key optional argument to specify c_dict key to store result. If
                  set to None (default) then use upper-case of met_config_name
                 @param allow_empty if True, if METplus config variable is set
                  but is an empty string, then set the c_dict value to an empty
                  list. If False, behavior is the same as when the variable is
                  not set at all, which is to not set anything for the c_dict
                  value
        """
        mp_config_name = self.get_mp_config_name(mp_config)
        if mp_config_name is None:
            return

        conf_value = util.getlist(self.config.getraw('config',
                                                     mp_config_name,
                                                     ''))
        if conf_value or allow_empty:
            conf_value = str(conf_value).replace("'", '"')

            if remove_quotes:
                conf_value = conf_value.replace('"', '')

            if not c_dict_key:
                c_key = met_config_name.upper()
            else:
                c_key = c_dict_key

            c_dict[c_key] = f'{met_config_name} = {conf_value};'

    def set_met_config_string(self, c_dict, mp_config, met_config_name,
                              c_dict_key=None, remove_quotes=False):
        """! Get string from METplus configuration file and format it to be passed
              into a MET configuration file. Set c_dict item with formatted string.
             Args:
                 @param c_dict configuration dictionary to set
                 @param mp_config METplus configuration variable name. Assumed to be
                  in the [config] section. Value can be a comma-separated list of items.
                 @param met_config_name name of MET configuration variable to set. Also used
                  to determine the key in c_dict to set (upper-case)
                 @param c_dict_key optional argument to specify c_dict key to store result. If
                  set to None (default) then use upper-case of met_config_name
        """
        mp_config_name = self.get_mp_config_name(mp_config)
        if mp_config_name is None:
            return

        conf_value = self.config.getraw('config', mp_config_name, '')
        if conf_value:
            if not c_dict_key:
                c_key = met_config_name.upper()
            else:
                c_key = c_dict_key

            conf_value = util.remove_quotes(conf_value)
            # add quotes back if remote quotes is False
            if not remove_quotes:
                conf_value = f'"{conf_value}"'

            c_dict[c_key] = f'{met_config_name} = {conf_value};'

    def set_met_config_number(self, c_dict, num_type, mp_config, met_config_name, c_dict_key=None):
        """! Get integer from METplus configuration file and format it to be passed
              into a MET configuration file. Set c_dict item with formatted string.
             Args:
                 @param c_dict configuration dictionary to set
                 @param num_type type of number to get from config. If set to 'int', call
                   getint function. If not, call getfloat function.
                 @param mp_config METplus configuration variable name. Assumed to be
                  in the [config] section. Value can be a comma-separated list of items.
                 @param met_config_name name of MET configuration variable to set. Also used
                  to determine the key in c_dict to set (upper-case) if c_dict_key is None
                 @param c_dict_key optional argument to specify c_dict key to store result. If
                  set to None (default) then use upper-case of met_config_name
        """
        mp_config_name = self.get_mp_config_name(mp_config)
        if mp_config_name is None:
            return

        if num_type == 'int':
            conf_value = self.config.getint('config', mp_config_name)
        else:
            conf_value = self.config.getfloat('config', mp_config_name)

        if conf_value is None:
            self.isOK = False
        elif conf_value != util.MISSING_DATA_VALUE:
            if not c_dict_key:
                c_key = met_config_name.upper()
            else:
                c_key = c_dict_key

            c_dict[c_key] = f"{met_config_name} = {str(conf_value)};"

    def set_met_config_int(self, c_dict, mp_config_name, met_config_name, c_dict_key=None):
        self.set_met_config_number(c_dict, 'int', mp_config_name, met_config_name, c_dict_key=c_dict_key)

    def set_met_config_float(self, c_dict, mp_config_name, met_config_name, c_dict_key=None):
        self.set_met_config_number(c_dict, 'float', mp_config_name, met_config_name, c_dict_key=c_dict_key)

    def set_met_config_thresh(self, c_dict, mp_config, met_config_name,
                              c_dict_key=None):
        mp_config_name = self.get_mp_config_name(mp_config)
        if mp_config_name is None:
            return

        conf_value = self.config.getstr('config', mp_config_name, '')
        if conf_value:
            if util.get_threshold_via_regex(conf_value) is None:
                self.log_error(f"Incorrectly formatted threshold: {mp_config_name}")
                return

            if not c_dict_key:
                c_key = met_config_name.upper()
            else:
                c_key = c_dict_key

            c_dict[c_key] = f"{met_config_name} = {str(conf_value)};"

    def set_met_config_bool(self, c_dict, mp_config, met_config_name,
                            c_dict_key=None, uppercase=True):
        """! Get boolean from METplus configuration file and format it to be
             passed into a MET configuration file. Set c_dict item with boolean
             value expressed as a string.
             Args:
                 @param c_dict configuration dictionary to set
                 @param mp_config METplus configuration variable name.
                  Assumed to be in the [config] section.
                 @param met_config_name name of MET configuration variable to
                  set. Also used to determine the key in c_dict to set
                  (upper-case)
                 @param c_dict_key optional argument to specify c_dict key to
                  store result. If set to None (default) then use upper-case of
                  met_config_name
                 @param uppercase If true, set value to TRUE or FALSE
        """
        mp_config_name = self.get_mp_config_name(mp_config)
        if mp_config_name is None:
            return
        conf_value = self.config.getbool('config', mp_config_name, '')
        if conf_value is None:
            self.log_error(f'Invalid boolean value set for {mp_config_name}')
            return

        # if not invalid but unset, return without setting c_dict with no error
        if conf_value == '':
            return

        conf_value = str(conf_value)
        if uppercase:
            conf_value = conf_value.upper()

        if not c_dict_key:
            c_key = met_config_name.upper()
        else:
            c_key = c_dict_key

        c_dict[c_key] = (f'{met_config_name} = '
                         f'{util.remove_quotes(conf_value)};')

    def get_mp_config_name(self, mp_config):
        """! Get first name of METplus config variable that is set.

        @param mp_config list of METplus config keys to check. Can also be a
        single item
        @returns Name of first METplus config name in list that is set in the
        METplusConfig object. None if none keys in the list are set.
        """
        if not isinstance(mp_config, list):
            mp_configs = [mp_config]
        else:
            mp_configs = mp_config

        for mp_config_name in mp_configs:
            if self.config.has_option('config', mp_config_name):
                return mp_config_name

        return None

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
        values = []
        if keys is None:
            keys = c_dict.keys()

        for key in keys:
            value = c_dict.get(key)
            if value:
                values.append(str(value))

        # if none of the keys are set to a value in dict, return empty string
        if not values:
            return ''

        return f"{name} = {{{''.join(values)}}}"

    def handle_regrid(self, c_dict, set_to_grid=True):
        app_name_upper = self.app_name.upper()

        # dictionary to hold regrid values as they are read
        tmp_dict = {}

        if set_to_grid:
            conf_value = (
                self.config.getstr('config',
                                   f'{app_name_upper}_REGRID_TO_GRID', '')
            )

            # set to_grid without formatting for backwards compatibility
            formatted_to_grid = self.format_regrid_to_grid(conf_value)
            c_dict['REGRID_TO_GRID'] = formatted_to_grid

            if conf_value:
                tmp_dict['REGRID_TO_GRID'] = (
                    f"to_grid = {formatted_to_grid};"
                )

        self.set_met_config_string(tmp_dict,
                                   f'{app_name_upper}_REGRID_METHOD',
                                   'method',
                                   'REGRID_METHOD',
                                   remove_quotes=True)

        self.set_met_config_int(tmp_dict,
                                f'{app_name_upper}_REGRID_WIDTH',
                                'width',
                                'REGRID_WIDTH')

        self.set_met_config_float(tmp_dict,
                                  f'{app_name_upper}_REGRID_VLD_THRESH',
                                  'vld_thresh',
                                  'REGRID_VLD_THRESH')
        self.set_met_config_string(tmp_dict,
                                   f'{app_name_upper}_REGRID_SHAPE',
                                   'shape',
                                   'REGRID_SHAPE',
                                   remove_quotes=True)

        regrid_string = self.format_met_config_dict(tmp_dict,
                                                    'regrid',
                                                    ['REGRID_TO_GRID',
                                                     'REGRID_METHOD',
                                                     'REGRID_WIDTH',
                                                     'REGRID_VLD_THRESH',
                                                     'REGRID_SHAPE',
                                                     ])
        self.env_var_dict['METPLUS_REGRID_DICT'] = regrid_string

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
                f'desc = "{util.remove_quotes(conf_value)}";'
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

    def set_climo_env_vars(self):
        """!Set all climatology environment variables from CLIMO_<item>_FILE
            c_dict values if they are not set to None"""
        for climo_item in self.climo_types:

            # climo file is set to None if not found, so set to empty string if None
            climo_file = (
                util.remove_quotes(self.c_dict.get(f'CLIMO_{climo_item}_FILE'))
            )

            climo_string = ''
            # remove then add double quotes for file path unless empty string
            if climo_file:
                climo_file = f'"{util.remove_quotes(climo_file)}"'
                climo_string = f"file_name = [{climo_file}];"

                if climo_item == 'STDEV':
                    climo_string = f'climo_stdev = {{{climo_string}}}'

            # set environment variable
            self.add_env_var(f'METPLUS_CLIMO_{climo_item}_FILE', climo_string)
            # set old method
            self.add_env_var(f'CLIMO_{climo_item}_FILE', climo_file)

    def read_climo_wrapper_specific(self, met_tool, c_dict):
        """!Read climatology directory and template values for specific MET
         tool specified and set the values in c_dict"""
        for climo_item in self.climo_types:
            c_dict[f'CLIMO_{climo_item}_INPUT_DIR'] = (
                self.config.getdir(f'{met_tool}_CLIMO_{climo_item}_INPUT_DIR',
                                   '')
            )
            c_dict[f'CLIMO_{climo_item}_INPUT_TEMPLATE'] = (
                self.config.getraw('filename_templates',
                                   f'{met_tool}_CLIMO_{climo_item}_INPUT_TEMPLATE',
                                   '')
            )

    def handle_climo(self, time_info):
        """!Substitute time information into all climatology template values"""
        for climo_item in self.climo_types:
             self.handle_climo_file_item(time_info, climo_item)

    def handle_climo_file_item(self, time_info, climo_item):
        """!Handle a single climatology value by substituting time information,
            prepending input directory if provided, and
            preprocessing file if necessary. All information is read from
            c_dict. CLIMO_<item>_FILE in c_dict is set."""

        # don't process if template is not set
        if not self.c_dict.get(f'CLIMO_{climo_item}_INPUT_TEMPLATE'):
            return

        template = self.c_dict.get(f'CLIMO_{climo_item}_INPUT_TEMPLATE', '')
        climo_file = do_string_sub(template,
                                   **time_info)
        climo_path = (
            os.path.join(self.c_dict.get(f'CLIMO_{climo_item}_INPUT_DIR',
                                         ''),
                         climo_file)
        )

        if not self.c_dict.get('INPUT_MUST_EXIST'):
            output_path = climo_path
        else:
            self.logger.debug(f"Looking for climatology {climo_item.lower()} "
                              f"file {climo_path}")
            output_path = util.preprocess_file(climo_path,
                                               '',
                                               self.config)

        self.c_dict[f'CLIMO_{climo_item}_FILE'] = output_path
        output_fmt = f'file_name = ["{output_path}"];'
        if climo_item == 'STDEV':
            output_fmt = f'climo_stdev = {{ {output_fmt} }}'
        self.env_var_dict[f'METPLUS_CLIMO_{climo_item}_FILE'] = output_fmt

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

    def format_field(self, data_type, field_formatted):
        """! Set {data_type}_FIELD c_dict value to the formatted field string
        Also set {data_type_FIELD_OLD value to support old format until it is
        deprecated.

        @param field_formatted field string
        @param data_type type of data to set, i.e. FCST, OBS
        """
        self.env_var_dict[f'METPLUS_{data_type}_FIELD'] = (
            f"field = [{field_formatted}];"
        )
        self.c_dict[f'{data_type}_FIELD'] = field_formatted

    def handle_flags(self, flag_type):
        """! Handle reading and setting of flag dictionary values to set in
        a MET config file. Sets METPLUS_{flag_type}_FLAG_DICT in the
        env_var_dict.

            @param flag_type type of flag to read, i.e. OUTPUT or ENSEMBLE
        """
        if not hasattr(self, f'{flag_type}_FLAGS'):
            return

        tmp_dict = {}
        flag_list = []
        for flag in getattr(self, f'{flag_type}_FLAGS'):
            flag_name = f'{flag_type}_FLAG_{flag.upper()}'
            flag_list.append(flag_name)
            self.set_met_config_string(tmp_dict,
                                       f'{self.app_name.upper()}_{flag_name}',
                                       flag,
                                       f'{flag_name}',
                                       remove_quotes=True)

        flag_fmt = (
            self.format_met_config_dict(tmp_dict,
                                        f'{flag_type.lower()}_flag',
                                        flag_list)
        )
        self.env_var_dict[f'METPLUS_{flag_type}_FLAG_DICT'] = flag_fmt

    def handle_censor_val_and_thresh(self):
        """! Read {APP_NAME}_CENSOR_[VAL/THRESH] and set
         METPLUS_CENSOR_[VAL/THRESH] in self.env_var_dict so it can be
         referenced in a MET config file
        """
        self.set_met_config_list(self.env_var_dict,
                                 f'{self.app_name.upper()}_CENSOR_THRESH',
                                 'censor_thresh',
                                 'METPLUS_CENSOR_THRESH',
                                 remove_quotes=True)

        self.set_met_config_list(self.env_var_dict,
                                 f'{self.app_name.upper()}_CENSOR_VAL',
                                 'censor_val',
                                 'METPLUS_CENSOR_VAL',
                                 remove_quotes=True)

    def get_env_var_value(self, env_var_name, read_dict=None):
        """! Read env var value, get text after the equals sign and remove the
        trailing semi-colon.

            @param env_var_name key to obtain
            @param read_dict (Optional) directory to read from. If unset (None)
             then read from self.env_var_dict
            @returns extracted value
        """
        if read_dict is None:
            read_dict = self.env_var_dict

        mask_value = read_dict.get(env_var_name, '')
        if not mask_value:
            return ''

        return mask_value.split('=', 1)[1].rstrip(';').strip()

    def handle_time_summary_dict(self, c_dict, remove_bracket_list=None):
        tmp_dict = {}
        app = self.app_name.upper()
        self.set_met_config_bool(tmp_dict,
                                 f'{app}_TIME_SUMMARY_FLAG',
                                 'flag',
                                 'TIME_SUMMARY_FLAG')

        self.set_met_config_bool(tmp_dict,
                                 f'{app}_TIME_SUMMARY_RAW_DATA',
                                 'raw_data',
                                 'TIME_SUMMARY_RAW_DATA')

        self.set_met_config_string(tmp_dict,
                                   f'{app}_TIME_SUMMARY_BEG',
                                   'beg',
                                   'TIME_SUMMARY_BEG')

        self.set_met_config_string(tmp_dict,
                                   f'{app}_TIME_SUMMARY_END',
                                   'end',
                                   'TIME_SUMMARY_END')

        self.set_met_config_int(tmp_dict,
                                f'{app}_TIME_SUMMARY_STEP',
                                'step',
                                'TIME_SUMMARY_STEP')

        self.set_met_config_int(tmp_dict,
                                f'{app}_TIME_SUMMARY_WIDTH',
                                'width',
                                'TIME_SUMMARY_WIDTH')

        self.set_met_config_list(tmp_dict,
                                 [f'{app}_TIME_SUMMARY_GRIB_CODES',
                                  f'{app}_TIME_SUMMARY_GRIB_CODE'],
                                 'grib_code',
                                 'TIME_SUMMARY_GRIB_CODES',
                                 remove_quotes=True,
                                 allow_empty=True)

        self.set_met_config_list(tmp_dict,
                                 [f'{app}_TIME_SUMMARY_OBS_VAR',
                                  f'{app}_TIME_SUMMARY_VAR_NAMES'],
                                 'obs_var',
                                 'TIME_SUMMARY_VAR_NAMES',
                                 allow_empty=True)

        self.set_met_config_list(tmp_dict,
                                 [f'{app}_TIME_SUMMARY_TYPE',
                                  f'{app}_TIME_SUMMARY_TYPES'],
                                 'type',
                                 'TIME_SUMMARY_TYPES')

        self.set_met_config_int(tmp_dict,
                                [f'{app}_TIME_SUMMARY_VLD_FREQ',
                                 f'{app}_TIME_SUMMARY_VALID_FREQ'],
                                'vld_freq',
                                'TIME_SUMMARY_VALID_FREQ')

        self.set_met_config_float(tmp_dict,
                                  [f'{app}_TIME_SUMMARY_VLD_THRESH',
                                   f'{app}_TIME_SUMMARY_VALID_THRESH'],
                                  'vld_thresh',
                                  'TIME_SUMMARY_VALID_THRESH')

        time_summary = self.format_met_config_dict(tmp_dict,
                                                   'time_summary',
                                                    keys=None)
        self.env_var_dict['METPLUS_TIME_SUMMARY_DICT'] = time_summary

        # set c_dict values to support old method of setting env vars
        for key, value in tmp_dict.items():
            c_dict[key] = self.get_env_var_value(key, read_dict=tmp_dict)

        # remove brackets [] from lists
        if not remove_bracket_list:
            return

        for list_values in remove_bracket_list:
            c_dict[list_values] = c_dict[list_values].strip('[]')

    def handle_mask(self, single_value=False):
        """! Read mask dictionary values and set them into env_var_list

            @param single_value if True, only a single value for grid and poly
            are allowed. If False, they should be treated as as list
        """
        app = self.app_name.upper()
        tmp_dict = {}
        if single_value:
            function_call = self.set_met_config_string
        else:
            function_call = self.set_met_config_list

        function_call(tmp_dict,
                      [f'{app}_MASK_GRID',
                       f'{app}_GRID'],
                      'grid',
                      'MASK_GRID')
        function_call(tmp_dict,
                      [f'{app}_MASK_POLY',
                       f'{app}_VERIFICATION_MASK_TEMPLATE',
                       f'{app}_POLY'],
                      'poly',
                      'MASK_POLY')

        mask_dict_string = self.format_met_config_dict(tmp_dict,
                                                       'mask',
                                                       ['MASK_GRID',
                                                        'MASK_POLY'])
        self.env_var_dict['METPLUS_MASK_DICT'] = mask_dict_string
