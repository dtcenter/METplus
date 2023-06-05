"""
Program Name: config_metplus.py
Contact(s): George McCabe, Julie Prestopnik, Jim Frimel, Minna Win
Abstract:
History Log:  Initial version
Usage: Used to read the configuration files to setup the METplus wrappers
Parameters: None
Input Files: N/A
Output Files: N/A
"""

import os
import re
import sys
import logging
from datetime import datetime, timezone
import time
import shutil
from configparser import ConfigParser, NoOptionError
from pathlib import Path
import uuid

from produtil.config import ProdConfig

from .constants import RUNTIME_CONFS, MISSING_DATA_VALUE
from .string_template_substitution import do_string_sub
from .string_manip import getlist, remove_quotes
from .string_manip import validate_thresholds, find_indices_in_config_section
from .system_util import mkdir_p
from .config_util import is_loop_by_init
from .config_validate import validate_field_info_configs

"""!Creates the initial METplus directory structure,
loads information into each job.

This module is used to create the initial METplus conf file in the
first METplus job via the metplus.config_metplus.launch().
The launch() function does more than just create the conf file though.
It creates several initial files and  directories

The METplusConfig class is used in place of a produtil.config.ProdConfig
throughout the METplus system.  It can be used as a drop-in replacement
for a produtil.config.ProdConfig, but has additional features needed to
support initial creation of the METplus system.
"""

'''!@var __all__
All symbols exported by "from metplus.util.config_metplus import *"
'''
__all__ = [
    'setup',
    'parse_var_list',
    'replace_config_from_section',
]

'''!@var METPLUS_BASE
The METplus installation directory
'''
METPLUS_BASE = os.path.realpath(str(Path(__file__).parents[2]))

# name of directory under METPLUS_BASE that contains config files
PARM_DIR = 'parm'

# set parm base to METPLUS_BASE/parm unless METPLUS_PARM_BASE env var is set
PARM_BASE = os.environ.get('METPLUS_PARM_BASE',
                           os.path.join(METPLUS_BASE, PARM_DIR))

# name of directory under PARM_DIR that contains defaults
METPLUS_CONFIG_DIR = 'metplus_config'

# default METplus configuration files that are sourced first
BASE_CONFS = [
    'defaults.conf',
]

# support previous location of default config files
OLD_BASE_CONFS = [
    'metplus_system.conf',
    'metplus_data.conf',
    'metplus_runtime.conf',
    'metplus_logging.conf'
]

# set all loggers to use UTC
logging.Formatter.converter = time.gmtime


def setup(args, base_confs=None):
    """!Setup the METplusConfig by reading in default configurations and any
    arguments from the command line.

    @param args list of configuration files or configuration
     variable overrides. Reads all configuration inputs and returns
     a configuration object
    @param base_confs optional config files to read first
    @returns METplusConfig object
    """
    if base_confs is None:
        base_confs = _get_default_config_list()

    override_list = _parse_launch_args(args)

    # add default config files to override list
    override_list = base_confs + override_list
    config = launch(override_list)

    return config


def _get_default_config_list(parm_base=None):
    """! Get list of default METplus config files. Look through BASE_CONFS list
    and check if each file exists under the parm base. Add each to a list
    if they do exist.

        @param parm_base directory to search for METplus config files. Uses
         real path of PARM_BASE if it is not set (None)
        @returns list of full paths to default METplus config files
    """
    default_config_list = []
    if parm_base is None:
        parm_base = PARM_BASE

    conf_dir = os.path.join(parm_base,
                            METPLUS_CONFIG_DIR)

    # if both are found, set old base confs first so the new takes precedence
    for base_conf in OLD_BASE_CONFS + BASE_CONFS:
        conf_path = os.path.join(conf_dir,
                                 base_conf)
        if os.path.exists(conf_path):
            default_config_list.append(conf_path)

    if not default_config_list:
        print(f"FATAL: No default config files found in {conf_dir}")
        sys.exit(1)

    return default_config_list


def _parse_launch_args(args):
    """! Parsed arguments to scripts that launch the METplus wrappers.

    Options:
    * section.variable=value --- set this value in this section
    * /path/to/file.conf --- read this conf file after the default conf files

    @param args the script arguments, after script-specific ones are removed
    @returns tuple containing path to parm directory, list of config files and
     collections.defaultdict of explicit config overrides
    """
    if not args:
        return []

    if isinstance(args, str):
        args = [args]

    override_list = []

    # Now look for any option and conf file arguments:
    bad = False
    for arg in args:
        m = re.match(r'''(?x)
          (?P<section>[a-zA-Z][a-zA-Z0-9_]*)
           \.(?P<option>[^=]+)
           =(?P<value>.*)$''', arg)
        # check if argument is a explicit variable override
        if m:
            section = m.group('section')
            key = m.group('option')
            value = m.group('value')
            override_list.append((section, key, value))
            continue

        filepath = arg
        # check if argument is a path to a file that exists
        if not os.path.exists(filepath):
            print(f'ERROR: Invalid argument: {filepath}')
            bad = True
            continue

        # expand file path to full path
        filepath = os.path.realpath(filepath)

        # path exists but is not a file
        if not os.path.isfile(filepath):
            print(f'ERROR: Conf is not a file: {filepath}')
            bad = True
            continue

        # warn and skip if file is empty
        if os.stat(filepath).st_size == 0:
            print(f'WARNING: Conf file is empty: {filepath}. Skipping')
            continue

        # add file path to override list
        override_list.append(filepath)

    # exit if anything went wrong reading config arguments
    if bad:
        sys.exit(2)

    return override_list


def launch(config_list):
    """! Process configuration files and explicit configuration variables
     overrides. Subsequent configuration files override values in previously
     read files. Explicit configuration variables are read after all config
     files are processed.

    @param config_list list of configuration files to process
    """
    config = METplusConfig()

    # set config variable for current time
    config.set('config', 'CLOCK_TIME',
               datetime.now().strftime('%Y%m%d%H%M%S'))

    config_format_list = []
    # Read in and parse all the conf files and overrides
    for config_item in config_list:
        if isinstance(config_item, str):
            print(f"Parsing config file: {config_item}")
            config.read(config_item)
            config_format_list.append(config_item)
        else:
            # set explicit config override
            section, key, value = config_item
            if not config.has_section(section):
                config.add_section(section)

            print(f"Parsing override: [{section}] {key} = {value}")
            config.set(section, key, value)
            config_format_list.append(f'{section}.{key}={value}')

        # move all config variables from old sections into the [config] section
        config._move_all_to_config_section()

    # save list of user configuration files in a variable
    config.set('config', 'CONFIG_INPUT', ','.join(config_format_list))

    # save unique identifier for the METplus run
    config.set('config', 'RUN_ID', str(uuid.uuid4())[0:8])

    # get OUTPUT_BASE to make sure it is set correctly so the first error
    # that is logged relates to OUTPUT_BASE, not LOG_DIR, which is likely
    # only set incorrectly because OUTPUT_BASE is set incorrectly
    # Initialize the output directories
    mkdir_p(config.getdir('OUTPUT_BASE'))

    # set and log variables to the config object
    get_logger(config)

    final_conf = config.getstr('config', 'METPLUS_CONF')

    # create final conf directory if it doesn't already exist
    final_conf_dir = os.path.dirname(final_conf)
    mkdir_p(final_conf_dir)

    # set METPLUS_BASE/PARM_BASE conf so they can be referenced in other confs
    config.set('config', 'METPLUS_BASE', METPLUS_BASE)
    config.set('config', 'PARM_BASE', PARM_BASE)

    with open(final_conf, 'wt') as file_handle:
        config.write(file_handle)

    return config


def _set_logvars(config):
    """!Sets and adds the LOG_METPLUS and LOG_TIMESTAMP
       to the config object. If LOG_METPLUS was already defined by the
       user in their conf file. It expands and rewrites it in the conf
       object and the final file.
       conf file.

           @param config:   the config instance
    """
    log_timestamp_template = config.getstr('config', 'LOG_TIMESTAMP_TEMPLATE',
                                           '')
    if config.getbool('config', 'LOG_TIMESTAMP_USE_DATATIME', False):
        loop_by = 'INIT' if is_loop_by_init(config) else 'VALID'
        time_str = config.getraw('config', f'{loop_by}_BEG')
        time_fmt = config.getraw('config', f'{loop_by}_TIME_FMT')
        date_t = datetime.strptime(time_str, time_fmt)
    else:
        date_t = datetime.now(timezone.utc)

    log_filenametimestamp = date_t.strftime(log_timestamp_template)

    # add LOG_TIMESTAMP to the final configuration file
    config.set('config', 'LOG_TIMESTAMP', log_filenametimestamp)

    metplus_log = config.strinterp(
        'config',
        '{LOG_METPLUS}',
        LOG_TIMESTAMP_TEMPLATE=log_filenametimestamp
    )

    # add log directory to log file path if only filename was provided
    if metplus_log:
        if os.path.basename(metplus_log) == metplus_log:
            metplus_log = os.path.join(config.getdir('LOG_DIR'), metplus_log)
        print('Logging to %s' % metplus_log)
    else:
        print('Logging to terminal only')

    # set LOG_METPLUS with timestamp substituted
    config.set('config', 'LOG_METPLUS', metplus_log)


def get_logger(config):
    """!This function will return a logger with a formatted file handler
    for writing to the LOG_METPLUS and it sets the LOG_LEVEL. If LOG_METPLUS is
    not defined, a logger is still returned without adding a file handler,
    but still setting the LOG_LEVEL.

       @param config:   the config instance
       @returns logger
    """
    _set_logvars(config)

    # Retrieve all logging related parameters from the param file
    log_level = config.getstr('config', 'LOG_LEVEL')
    log_level_terminal = config.getstr('config', 'LOG_LEVEL_TERMINAL')

    # Create the log directory if it does not exist
    mkdir_p(config.getdir('LOG_DIR'))

    logger = config.log()

    try:
        log_level_val = logging.getLevelName(log_level)
    except ValueError:
        print(f'ERROR: Invalid value set for LOG_LEVEL: {log_level}')
        sys.exit(1)

    try:
        log_level_terminal_val = logging.getLevelName(log_level_terminal)
    except ValueError:
        print('ERROR: Invalid value set for LOG_LEVEL_TERMINAL:'
              f' {log_level_terminal}')
        sys.exit(1)

    metpluslog = config.getstr('config', 'LOG_METPLUS', '')
    if not metpluslog:
        logger.setLevel(log_level_terminal_val)
    else:
        # set logger level to the minimum of the two log levels because
        # setting level for each handler will not work otherwise
        logger.setLevel(min(log_level_val, log_level_terminal_val))

        # create log directory if it does not already exist
        dir_name = os.path.dirname(metpluslog)
        if not os.path.exists(dir_name):
            mkdir_p(dir_name)

        # do not send logs up to root logger handlers
        logger.propagate = False

        # create log formatter from config settings
        formatter = METplusLogFormatter(config)

        # set up the file logging
        file_handler = logging.FileHandler(metpluslog, mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level_val)
        logger.addHandler(file_handler)

        # set up console logging
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level_terminal_val)
        logger.addHandler(stream_handler)

    # set add the logger to the config
    config.logger = logger
    return logger


def replace_config_from_section(config, section, required=True):
    """! Check if config has a section named [section] If it does, create a
    new METplusConfig object, set each value from the input config, then
    set each value from [section], overriding any values that are found in both

    @param config input METplusConfig object
    @param section name of section in config object to look for
    @param required (optional) True/False to determine if an error should occur
    if the section does not exist. Default value is True
    @returns If required and section does not exist, error and return None.
    If not required and section does not exist, return input config. If section
    does exist, return new METplusConfig object with config values replaced by
    all values in [section]
    """
    if not config.has_section(section):
        # if section is required to be found, report error and return None
        if required:
            error_message = f'Section {section} does not exist.'
            if config.logger:
                config.logger.error(error_message)
            else:
                print(f"ERROR: {error_message}")

            return None
        # if not required, return input config object
        return config

    new_config = METplusConfig()

    # copy over all key/values from sections
    for section_to_copy in ['config', 'user_env_vars']:
        all_configs = config.keys(section_to_copy)
        for key in all_configs:
            new_config.set(section_to_copy,
                           key,
                           config.getraw(section_to_copy, key, sub_vars=False))

    # override values in [config] with values from {section}
    all_configs = config.keys(section)
    for key in all_configs:
        new_config.set('config',
                       key,
                       config.getraw(section, key, sub_vars=False))

    return new_config


class METplusConfig(ProdConfig):
    """! Configuration class to store configuration values read from
    METplus config files.
    """

    # items that are found in these sections
    # will be moved into the [config] section
    OLD_SECTIONS = (
        'dir',
        'exe',
        'filename_templates',
        'regex_pattern',
    )

    def __init__(self, conf=None):
        """!Creates a new METplusConfig
        @param conf The configuration file
        """
        # set interpolation to None so you can supply filename template
        # that contain % to config.set
        conf = ConfigParser(strict=False,
                            inline_comment_prefixes=(';',),
                            interpolation=None) if (conf is None) else conf
        super().__init__(conf)
        self._cycle = None
        self._logger = logging.getLogger('metplus')
        # config.logger is called in wrappers, so set this name
        # so the code doesn't break
        self.logger = self._logger

        # get the OS environment and store it
        self.env = os.environ.copy()

        # add section to hold environment variables defined by the user
        self.add_section('user_env_vars')

    def log(self, sublog=None):
        """! Overrides method in ProdConfig
        If the sublog argument is
        provided, then the logger will be under that subdomain of the
        "metplus" logging domain.  Otherwise, this METplusConfig's logger
        (usually the "metplus" domain) is returned.
        @param sublog the logging subdomain, or None
        @returns a logging.Logger object"""
        if sublog is not None:
            with self:
                return logging.getLogger('metplus.'+sublog)
        return self._logger

    def _move_all_to_config_section(self):
        """! Move all configuration variables that are found in the
             previously supported sections into the config section.
        """
        for section in self.OLD_SECTIONS:
            if not self.has_section(section):
                continue

            all_configs = self.keys(section)
            for key in all_configs:
                self.set('config',
                         key,
                         super().getraw(section, key))

            self._conf.remove_section(section)

    def move_runtime_configs(self):
        """! Move all config variables that are specific to the current runtime
        environment to the [runtime] section so that they do not cause issues
        if a user reads in the final conf from a run to run_metplus to rerun
        """
        from_section = 'config'
        to_section = 'runtime'
        more_run_confs = [item for item in self.keys(from_section)
                          if item.startswith('LOG') or item.endswith('BASE')]

        # create destination section if it does not exist
        if not self.has_section(to_section):
            self._conf.add_section(to_section)

        for key in RUNTIME_CONFS + more_run_confs:
            if not self.has_option(from_section, key):
                continue

            # add conf to [runtime] section
            self.set(to_section, key, super().getraw(from_section, key))

            # remove conf from [config] section
            self._conf.remove_option(from_section, key)

    def remove_current_vars(self):
        """! Remove variables from [config] section that start with CURRENT
        """
        current_vars = [item for item in self.keys('config')
                        if item.startswith('CURRENT')]
        for current_var in current_vars:
            if self.has_option('config', current_var):
                self._conf.remove_option('config', current_var)

    # override get methods to perform additional error checking
    def getraw(self, sec, opt, default='', count=0, sub_vars=True):
        """ parse parameter and replace any existing parameters
            referenced with the value (looking in same section, then
            config, dir, and os environment)
            returns raw string, preserving {valid?fmt=%Y} blocks

            @param sec Section in the conf file to look for variable
            @param opt Variable to interpret
            @param default Default value to use if config is not set
            @param count Counter used to stop recursion to prevent infinite
            @param sub_vars If False, skip string template substitution,
             defaults to True
            @returns Raw string or empty string if function calls itself too
             many times
        """
        if count >= 10:
            self.logger.error("Could not resolve getraw - check for circular "
                              "references in METplus configuration variables")
            return ''

        # if requested section is in the list of sections that are no longer
        # used, look in the [config] section for the variable
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        in_template = super().getraw(sec, opt, '')
        # if default is set but variable was not, set variable to default value
        if not in_template and default:
            self.check_default(sec, opt, default)
            return default

        # if not substituting values of other variables return value
        if not sub_vars:
            return in_template

        # get inner-most tags that could potentially be other variables
        match_list = re.findall(r'\{([^}{]*)\}', in_template)
        for var_name in match_list:
            # check if each tag is an existing METplus config variable
            if self.has_option(sec, var_name):
                value = self.getraw(sec, var_name, default, count+1)
            elif self.has_option('config', var_name):
                value = self.getraw('config', var_name, default, count+1)
            elif var_name.startswith('ENV'):
                # if environment variable, ENV[nameofvar], get nameofvar
                value = os.environ.get(var_name[4:-1])
            else:
                value = None

            if value is None:
                continue
            in_template = in_template.replace(f"{{{var_name}}}", value)

        # Replace double slash with single slash because MET config files fail
        # when they encounter double slash. This is a GitHub issue MET #1277
        # This fix will prevent using URLs with https:// so the MET issue must
        # be resolved before we can remove the replace call
        return in_template.replace('//', '/')

    def check_default(self, sec, name, default):
        """! helper function for get methods, report error and raise
         NoOptionError if default is not set.
         If default is set, set the config variable to the
         default value so that the value is stored in the final conf

         @param sec section of config
         @param name name of config variable
         @param default value to use - if set to None, error/raise exception
        """
        if default is None:
            raise

        # print debug message saying default value was used
        if default == '':
            default_text = 'empty string'
        else:
            default_text = default

        msg = "Setting [{}] {} to default value ({})".format(sec,
                                                             name,
                                                             default_text)
        if self.logger:
            self.logger.debug(msg)
        else:
            print('DEBUG: {}'.format(msg))

        # set conf with default value so all defaults can be added to
        #  the final conf and warning only appears once per conf item
        #  using a default value
        self.set(sec, name, default)

    def getexe(self, exe_name):
        """! Wraps produtil exe with checks to see if option is set and if
            exe actually exists. Returns None if not found instead of exiting
        """
        try:
            exe_path = super().getstr('config', exe_name)
        except NoOptionError as e:
            if self.logger:
                self.logger.error(e)
            else:
                print(e)

            return None

        full_exe_path = shutil.which(exe_path)
        if full_exe_path is None:
            msg = f'Executable {exe_name} does not exist at {exe_path}'
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))
            return None

        # set config item to full path to exe and return full path
        self.set('config', exe_name, full_exe_path)
        return full_exe_path

    def getdir(self, dir_name, default=None, must_exist=False):
        """! Wraps produtil getdir and reports an error if
         it is set to /path/to
         """
        dir_path = self.getraw('config', dir_name, default=default)

        if '/path/to' in dir_path:
            raise ValueError(f"{dir_name} cannot be set to "
                             "or contain '/path/to'")

        if '\n' in dir_path:
            raise ValueError(f"Invalid value for [config] {dir_name} "
                             f"({dir_path}). Hint: Check that next variable "
                             "in the config file does not start with a space")

        if must_exist and not os.path.exists(dir_path):
            self.logger.error(f"Path must exist: {dir_path}")
            return None

        return dir_path.replace('//', '/')

    def getdir_nocheck(self, dir_name, default=None):
        return super().getstr('config', dir_name,
                              default=default).replace('//', '/')

    def getstr_nocheck(self, sec, name, default=None):
        # if requested section is in the list of sections that are
        # no longer used look in the [config] section for the variable
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        return super().getstr(sec, name, default=default).replace('//', '/')

    def getstr(self, sec, name, default=None, badtypeok=False, morevars=None,
               taskvars=None):
        """! Wraps produtil getstr. Config variable is checked with a default
         value of None because if the config is not set and a default is
          specified, it will just return that value.
          We want to log that a default was used and set it in the config so
          it will show up in the final conf that is generated at the end of
          execution. If no default was specified in the call,
          the NoOptionError is raised again. Replace double forward slash
          with single to prevent error that occurs if that is found inside
          a MET config file because it considers // the start of a comment
        """
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        try:
            return super().getstr(sec, name, default=None,
                                  badtypeok=badtypeok, morevars=morevars,
                                  taskvars=taskvars).replace('//', '/')
        except NoOptionError:
            # if config variable is not set
            self.check_default(sec, name, default)
            return default.replace('//', '/')

    def getbool(self, sec, name, default=None, badtypeok=False, morevars=None,
                taskvars=None):
        """! Wraps produtil getbool. Config variable is checked with a
         default value of None because if the config is not set and a
         default is specified, it will just return that value.
         We want to log that a default was used and set it in the config so
         it will show up in the final conf that is generated at the end of
         execution. If no default was specified in the call,
         the NoOptionError is raised again.
         @returns None if value is not a boolean (or yes/no), value if set,
          default if not set
         """
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        try:
            return super().getbool(sec, name, default=None,
                                   badtypeok=badtypeok, morevars=morevars,
                                   taskvars=taskvars)
        except NoOptionError:
            # config item was not set
            self.check_default(sec, name, default)
            return default
        except ValueError:
            # check if it was an empty string and return default or False if so
            value_string = super().getstr(sec, name)
            if not value_string:
                if default:
                    return default

                return False

            # check if value is y/Y/n/N and return True/False if so
            value_string = remove_quotes(value_string)
            if value_string.lower() == 'y':
                return True
            if value_string.lower() == 'n':
                return False

            # if value is not correct type, log error and return None
            self.logger.error(f"[{sec}] {name} must be an boolean.")
            return None

    def getint(self, sec, name, default=None, badtypeok=False, morevars=None,
               taskvars=None):
        """!Wraps produtil getint to gracefully report if variable is not set
            and no default value is specified
            @returns Value if set, default of missing value if not set,
             None if value is an incorrect type"""
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        try:
            # call ProdConfig function with no default set so
            # we can log and set the default
            return super().getint(sec, name, default=None,
                                  badtypeok=badtypeok, morevars=morevars,
                                  taskvars=taskvars)

        # if config variable is not set
        except NoOptionError:
            if default is None:
                default = MISSING_DATA_VALUE

            self.check_default(sec, name, default)
            return default

        # if invalid value
        except ValueError:
            # check if it was an empty string and return MISSING_DATA_VALUE
            if super().getstr(sec, name) == '':
                return MISSING_DATA_VALUE

            # if value is not correct type, log error and return None
            self.logger.error(f"[{sec}] {name} must be an integer.")
            return None

    def getfloat(self, sec, name, default=None, badtypeok=False, morevars=None,
                 taskvars=None):
        """!Wraps produtil getint to gracefully report if variable is not set
            and no default value is specified
            @returns Value if set, default of missing value if not set,
             None if value is an incorrect type"""
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        try:
            # call ProdConfig function with no default set so
            # we can log and set the default
            return super().getfloat(sec, name, default=None,
                                    badtypeok=badtypeok, morevars=morevars,
                                    taskvars=taskvars)

        # if config variable is not set
        except NoOptionError:
            if default is None:
                default = float(MISSING_DATA_VALUE)

            self.check_default(sec, name, default)
            return default

        # if invalid value
        except ValueError:
            # check if it was an empty string and return MISSING_DATA_VALUE
            if super().getstr(sec, name) == '':
                return MISSING_DATA_VALUE

            # if value is not correct type, log error and return None
            self.logger.error(f"[{sec}] {name} must be a float.")
            return None

    def getseconds(self, sec, name, default=None, badtypeok=False,
                   morevars=None, taskvars=None):
        """!Converts time values ending in H, M, or S to seconds"""
        if sec in self.OLD_SECTIONS:
            sec = 'config'

        try:
            # convert value to seconds
            # Valid options match format 3600, 3600S, 60M, or 1H
            value = super().getstr(sec, name, default=None,
                                   badtypeok=badtypeok, morevars=morevars,
                                   taskvars=taskvars)
            regex_and_multiplier = {r'(-*)(\d+)S': 1,
                                    r'(-*)(\d+)M': 60,
                                    r'(-*)(\d+)H': 3600,
                                    r'(-*)(\d+)D': 86400,
                                    r'(-*)(\d+)': 1}
            for reg, mult in regex_and_multiplier.items():
                match = re.match(reg, value)
                if match:
                    if match.group(1) == '-':
                        mult = mult * -1
                    return int(match.group(2)) * mult

            # if value is not in an expected format, error and exit
            msg = (f'[{sec}] {name} does not match expected format. '
                   'Valid options match 3600, 3600S, 60M, or 1H')
            if self.logger:
                self.logger.error(msg)
            else:
                print('ERROR: {}'.format(msg))

            return None

        except NoOptionError:
            # config item was not found
            self.check_default(sec, name, default)
            return default

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
            if self.has_option('config', mp_config_name):
                return mp_config_name

        return None


class METplusLogFormatter(logging.Formatter):
    def __init__(self, config):
        self.default_fmt = config.getraw('config', 'LOG_LINE_FORMAT')
        self.info_fmt = config.getraw('config', 'LOG_INFO_LINE_FORMAT',
                                      self.default_fmt)
        self.debug_fmt = config.getraw('config', 'LOG_DEBUG_LINE_FORMAT',
                                       self.default_fmt)
        self.error_fmt = config.getraw('config', 'LOG_ERR_LINE_FORMAT',
                                       self.default_fmt)
        super().__init__(fmt=self.default_fmt,
                         datefmt=config.getraw('config',
                                               'LOG_LINE_DATE_FORMAT'),
                         style='%')

    def format(self, record):
        if record.levelno == logging.ERROR:
            self._style._fmt = self.error_fmt
        elif record.levelno == logging.DEBUG:
            self._style._fmt = self.debug_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt

        output = logging.Formatter.format(self, record)

        # restore default format
        self._style._fmt = self.default_fmt

        return output


def parse_var_list(config, time_info=None, data_type=None, met_tool=None,
                   levels_as_list=False):
    """ read conf items and populate list of dictionaries containing
    information about each variable to be compared

            @param config: METplusConfig object
            @param time_info: time object for string sub, optional
            @param data_type: data type to find. Can be FCST, OBS, or ENS.
             If not set, get FCST/OBS/BOTH
            @param met_tool: optional name of MET tool to look for wrapper
             specific var items
            @param levels_as_list If true, store levels and output names as
             a list instead of creating a field info dict for each name/level
        @returns list of dictionaries with variable information
    """

    # validate configs again in case wrapper is not running from run_metplus
    # this does not need to be done if parsing a specific data type,
    # i.e. ENS or FCST
    if data_type is None:
        if not validate_field_info_configs(config)[0]:
            return []
    elif data_type == 'BOTH':
        config.logger.error("Cannot request BOTH explicitly in parse_var_list")
        return []

    # var_list is a list containing an list of dictionaries
    var_list = []

    # if specific data type is requested, only get that type
    if data_type:
        data_types = [data_type]
    # otherwise get both FCST and OBS
    else:
        data_types = ['FCST', 'OBS']

    # get indices of VAR<n> items for data type and/or met tool
    indices = []
    if met_tool:
        indices = _find_var_name_indices(config, data_types, met_tool)
    if not indices:
        indices = _find_var_name_indices(config, data_types)

    # get config name prefixes for each data type to find
    dt_search_prefixes = {}
    for current_type in data_types:
        # get list of variable prefixes to search
        prefixes = get_field_search_prefixes(current_type, met_tool)
        dt_search_prefixes[current_type] = prefixes

    # loop over all possible variables and add them to list
    for index in indices:
        field_info_list = []
        for current_type in data_types:
            # get dictionary of existing config variables to use
            search_prefixes = dt_search_prefixes[current_type]
            field_configs = get_field_config_variables(config,
                                                       index,
                                                       search_prefixes)

            field_info = _format_var_items(field_configs, time_info,
                                           config.logger)
            if not isinstance(field_info, dict):
                config.logger.error(f'Could not process {current_type}_'
                                    f'VAR{index} variables: {field_info}')
                continue

            field_info['data_type'] = current_type.lower()
            field_info_list.append(field_info)

        # check that all fields types were found
        if not field_info_list or len(data_types) != len(field_info_list):
            continue

        # check if number of levels for each field type matches
        n_levels = len(field_info_list[0]['levels'])
        if len(data_types) > 1:
            if n_levels != len(field_info_list[1]['levels']):
                continue

        # if requested, put all field levels in a single item
        if levels_as_list:
            var_dict = {}
            for field_info in field_info_list:
                current_type = field_info.get('data_type')
                var_dict[f"{current_type}_name"] = field_info.get('name')
                var_dict[f"{current_type}_level"] = field_info.get('levels')
                var_dict[f"{current_type}_thresh"] = field_info.get('thresh')
                var_dict[f"{current_type}_extra"] = field_info.get('extra')
                var_dict[f"{current_type}_output_name"] = field_info.get('output_names')

            var_dict['index'] = index
            var_list.append(var_dict)
            continue

        # loop over levels and add all values to output dictionary
        for level_index in range(n_levels):
            var_dict = {}

            # get level values to use for string substitution in name
            # used for python embedding calls that read the level value
            sub_info = {}
            for field_info in field_info_list:
                dt_level = f"{field_info.get('data_type')}_level"
                sub_info[dt_level] = field_info.get('levels')[level_index]

            for field_info in field_info_list:
                current_type = field_info.get('data_type')
                name = field_info.get('name')
                level = field_info.get('levels')[level_index]
                thresh = field_info.get('thresh')
                extra = field_info.get('extra')
                output_name = field_info.get('output_names')[level_index]

                # substitute level in name if filename template is specified
                subbed_name = do_string_sub(name,
                                            skip_missing_tags=True,
                                            **sub_info)

                var_dict[f"{current_type}_name"] = subbed_name
                var_dict[f"{current_type}_level"] = level
                var_dict[f"{current_type}_thresh"] = thresh
                var_dict[f"{current_type}_extra"] = extra
                var_dict[f"{current_type}_output_name"] = output_name

            var_dict['index'] = index
            var_list.append(var_dict)

    # extra debugging information used for developer debugging only
    '''
    for v in var_list:
        config.logger.debug(f"VAR{v['index']}:")
        if 'fcst_name' in v.keys():
            config.logger.debug(" fcst_name:"+v['fcst_name'])
            config.logger.debug(" fcst_level:"+v['fcst_level'])
        if 'fcst_thresh' in v.keys():
            config.logger.debug(" fcst_thresh:"+str(v['fcst_thresh']))
        if 'fcst_extra' in v.keys():
            config.logger.debug(" fcst_extra:"+v['fcst_extra'])
        if 'fcst_output_name' in v.keys():
            config.logger.debug(" fcst_output_name:"+v['fcst_output_name'])
        if 'obs_name' in v.keys():
            config.logger.debug(" obs_name:"+v['obs_name'])
            config.logger.debug(" obs_level:"+v['obs_level'])
        if 'obs_thresh' in v.keys():
            config.logger.debug(" obs_thresh:"+str(v['obs_thresh']))
        if 'obs_extra' in v.keys():
            config.logger.debug(" obs_extra:"+v['obs_extra'])
        if 'obs_output_name' in v.keys():
            config.logger.debug(" obs_output_name:"+v['obs_output_name'])
        if 'ens_name' in v.keys():
            config.logger.debug(" ens_name:"+v['ens_name'])
            config.logger.debug(" ens_level:"+v['ens_level'])
        if 'ens_thresh' in v.keys():
            config.logger.debug(" ens_thresh:"+str(v['ens_thresh']))
        if 'ens_extra' in v.keys():
            config.logger.debug(" ens_extra:"+v['ens_extra'])
        if 'ens_output_name' in v.keys():
            config.logger.debug(" ens_output_name:"+v['ens_output_name'])
    '''
    return sorted(var_list, key=lambda x: x['index'])


def _find_var_name_indices(config, data_types, met_tool=None):
    """!Get list of indices used in _VAR<n>_ config variables. Data type
    determines prefix of variable name to find. If FCST or OBS is included
    in data type list, then BOTH keyword is also searched. If specified,
    wrapper-specific variables are searched, e.g. FCST_GRID_STAT_VAR<n>_*.
    Variables that end with NAME, INPUT_FIELD_NAME, or FIELD_NAME are used to
    gather indices.

    @param config METplusConfig object to read
    @param data_types list of prefixes of config variables that describe the
     type of data e.g. FCST or OBS.
    @param met_tool (optional) name of wrapper to search for wrapper-specific
    variables, e.g. *_GRID_STAT_VAR<n>_*.
    @returns list of integers for all matching config variables
    """
    data_type_regex = f"{'|'.join(data_types)}"

    # if data_types includes FCST or OBS, also search for BOTH
    if any([item for item in ['FCST', 'OBS'] if item in data_types]):
        data_type_regex += '|BOTH'

    regex_string = f"({data_type_regex})"

    # if MET tool is specified, get tool specific items
    if met_tool:
        regex_string += f"_{met_tool.upper()}"

    regex_string += r"_VAR(\d+)_(NAME|INPUT_FIELD_NAME|FIELD_NAME)"

    # find all <data_type>_VAR<n>_NAME keys in the conf files
    indices = find_indices_in_config_section(regex_string,
                                             config,
                                             index_index=2,
                                             id_index=1).keys()
    return [int(index) for index in indices]


def _format_var_items(field_configs, time_info=None, logger=None):
    """! Substitute time information into field information and format values.

        @param field_configs dictionary with config variable names to read
        @param time_info dictionary containing time info for current run
        @param logger (optional) logging object
        @returns dictionary containing name, levels, and output_names, as
         well as thresholds and extra options if found. If not enough
         information was set in the METplusConfig object, an empty
         dictionary is returned.
    """
    # dictionary to hold field (var) item info
    var_items = {}

    # set defaults for optional items
    var_items['levels'] = []
    var_items['thresh'] = []
    var_items['extra'] = ''
    var_items['output_names'] = []

    # get name, return error string if not found
    search_name = field_configs.get('name')
    if not search_name:
        return 'Name not found'

    # perform string substitution on name
    if time_info:
        search_name = do_string_sub(search_name, **time_info,
                                    skip_missing_tags=True)
    var_items['name'] = search_name

    # get levels, performing string substitution on each item of list
    for level in getlist(field_configs.get('levels')):
        if time_info:
            level = do_string_sub(level, **time_info)
        var_items['levels'].append(level)

    # if no levels are found, add an empty string
    if not var_items['levels']:
        var_items['levels'].append('')

    # get threshold list if it is set
    # return error string if any thresholds not formatted properly
    search_thresh = field_configs.get('thresh')
    if search_thresh:
        thresh = getlist(search_thresh)
        if not validate_thresholds(thresh, logger):
            return 'Invalid threshold supplied'

        var_items['thresh'] = thresh

    # get extra options if it is set, format with semi-colons between items
    search_extra = field_configs.get('options')
    if search_extra:
        if time_info:
            search_extra = do_string_sub(search_extra,
                                         **time_info)

        # strip off empty space around each value
        extra_list = [item.strip() for item in search_extra.split(';')]

        # split up each item by semicolon, then add a semicolon to the end
        # use list(filter(None to remove empty strings from list
        extra_list = list(filter(None, extra_list))
        var_items['extra'] = f"{'; '.join(extra_list)};"

    # get output names if they are set
    out_name_str = field_configs.get('output_names')

    # use input name for each level if not set
    if not out_name_str:
        for _ in var_items['levels']:
            var_items['output_names'].append(var_items['name'])
    else:
        for out_name in getlist(out_name_str):
            if time_info:
                out_name = do_string_sub(out_name,
                                         **time_info)
            var_items['output_names'].append(out_name)

    if len(var_items['levels']) != len(var_items['output_names']):
        return 'Number of levels does not match number of output names'

    return var_items


def get_field_search_prefixes(data_type, met_tool=None):
    """! Get list of prefixes to search for field variables.

        @param data_type type of field to search for, i.e. FCST, OBS, ENS, etc.
         Check for BOTH_ variables first only if data type is FCST or OBS
        @param met_tool name of tool to search for variable or None if looking
         for generic field info
        @returns list of prefixes to search, i.e. [BOTH_, FCST_] or
         [ENS_] or [BOTH_GRID_STAT_, OBS_GRID_STAT_]
    """
    search_prefixes = []
    var_strings = []

    # if met tool name is set, prioritize
    # wrapper-specific configs before generic configs
    if met_tool:
        var_strings.append(f'{met_tool.upper()}_')

    var_strings.append('')

    for var_string in var_strings:
        search_prefixes.append(f"{data_type}_{var_string}")

        # if looking for FCST or OBS, also check for BOTH prefix
        if data_type in ['FCST', 'OBS']:
            search_prefixes.append(f"BOTH_{var_string}")

    return search_prefixes


def get_field_config_variables(config, index, search_prefixes):
    """! Search for variables that are set in the config that correspond to
     the fields requested. Some field info items have
     synonyms that can be used if the typical name is not set. This is used
     in RegridDataPlane wrapper.

        @param config METplusConfig object to search
        @param index integer <n> of field (VAR<n>) to find
        @param search_prefixes list of valid prefixes to search for variables
         in the config, i.e. FCST_VAR1_ or OBS_GRID_STAT_VAR2_
        @returns dictionary containing a config variable name to be used for
         each field info value. If a valid config variable was not set for a
         field info value, the value for that key will be set to None.
    """
    # list of field info variables to find from config
    # used as keys for dictionaries
    field_info_items = ['name',
                        'levels',
                        'thresh',
                        'options',
                        'output_names',
                       ]

    field_configs = {}
    search_suffixes = {}

    # initialize field configs dictionary values to None
    # initialize dictionary of valid suffixes to search for with
    # the capitalized version of field info name
    for field_info_item in field_info_items:
        field_configs[field_info_item] = None
        search_suffixes[field_info_item] = [field_info_item.upper()]

    # add alternate suffixes for config variable names to attempt
    search_suffixes['name'].append('INPUT_FIELD_NAME')
    search_suffixes['name'].append('FIELD_NAME')
    search_suffixes['levels'].append('INPUT_LEVEL')
    search_suffixes['levels'].append('FIELD_LEVEL')
    search_suffixes['output_names'].append('OUTPUT_FIELD_NAME')
    search_suffixes['output_names'].append('FIELD_NAME')

    # look through field config keys and obtain highest priority
    # variable name for each field config
    for search_var, suffixes in search_suffixes.items():
        for prefix in search_prefixes:

            found = False
            for suffix in suffixes:
                var_name = f"{prefix}VAR{index}_{suffix}"
                # if variable is found in config,
                # get the value and break out of suffix loop
                if config.has_option('config', var_name):
                    field_configs[search_var] = config.getraw('config',
                                                              var_name)
                    found = True
                    break

            # if config variable was found, break out of prefix loop
            if found:
                break

    return field_configs
