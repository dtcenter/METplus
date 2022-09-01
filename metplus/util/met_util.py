import os
import shutil
import sys
import datetime
import re
import gzip
import bz2
import zipfile
import struct
from dateutil.relativedelta import relativedelta
from pathlib import Path
from importlib import import_module

from .string_manip import getlist, getlistint
from .string_template_substitution import do_string_sub
from .string_template_substitution import parse_template
from . import time_util as time_util
from .time_looping import time_generator
from .. import get_metplus_version

"""!@namespace met_util
 @brief Provides  Utility functions for METplus.
"""

from .constants import *

# missing data value used to check if integer values are not set
# we often check for None if a variable is not set, but 0 and None
# have the same result in a test. 0 may be a valid integer value
MISSING_DATA_VALUE = -9999

def pre_run_setup(config_inputs):
    from . import config_metplus
    version_number = get_metplus_version()
    print(f'Starting METplus v{version_number}')

    # Read config inputs and return a config instance
    config = config_metplus.setup(config_inputs)

    logger = config.logger

    user_info = get_user_info()
    user_string = f' as user {user_info} ' if user_info else ' '
    config.set('config', 'METPLUS_VERSION', version_number)
    logger.info('Running METplus v%s%swith command: %s',
                version_number, user_string, ' '.join(sys.argv))

    logger.info(f"Log file: {config.getstr('config', 'LOG_METPLUS')}")
    logger.info(f"METplus Base: {config.getdir('METPLUS_BASE')}")
    logger.info(f"Final Conf: {config.getstr('config', 'METPLUS_CONF')}")
    config_list = config.getstr('config', 'CONFIG_INPUT').split(',')
    for config_item in config_list:
        logger.info(f"Config Input: {config_item}")

    # validate configuration variables
    isOK_A, isOK_B, isOK_C, isOK_D, all_sed_cmds = config_metplus.validate_configuration_variables(config)
    if not (isOK_A and isOK_B and isOK_C and isOK_D):
        # if any sed commands were generated, write them to the sed file
        if all_sed_cmds:
            sed_file = os.path.join(config.getdir('OUTPUT_BASE'), 'sed_commands.txt')
            # remove if sed file exists
            if os.path.exists(sed_file):
                os.remove(sed_file)

            write_list_to_file(sed_file, all_sed_cmds)
            config.logger.error(f"Find/Replace commands have been generated in {sed_file}")

        logger.error("Correct configuration variables and rerun. Exiting.")
        sys.exit(1)

    if not config.getdir('MET_INSTALL_DIR', must_exist=True):
        logger.error('MET_INSTALL_DIR must be set correctly to run METplus')
        sys.exit(1)

    # set staging dir to OUTPUT_BASE/stage if not set
    if not config.has_option('config', 'STAGING_DIR'):
        config.set('config', 'STAGING_DIR',
                   os.path.join(config.getdir('OUTPUT_BASE'), "stage"))

    # handle dir to write temporary files
    handle_tmp_dir(config)

    # handle OMP_NUM_THREADS environment variable
    handle_env_var_config(config,
                          env_var_name='OMP_NUM_THREADS',
                          config_name='OMP_NUM_THREADS')

    config.env = os.environ.copy()

    return config

def run_metplus(config, process_list):
    total_errors = 0

    try:
        processes = []
        for process, instance in process_list:
            try:
                logname = f"{process}.{instance}" if instance else process
                logger = config.log(logname)
                package_name = ('metplus.wrappers.'
                                f'{camel_to_underscore(process)}_wrapper')
                module = import_module(package_name)
                command_builder = (
                    getattr(module, f"{process}Wrapper")(config,
                                                         instance=instance)
                )

                # if Usage specified in PROCESS_LIST, print usage and exit
                if process == 'Usage':
                    command_builder.run_all_times()
                    return 0
            except AttributeError:
                logger.error("There was a problem loading "
                             f"{process} wrapper.")
                return 1
            except ModuleNotFoundError:
                logger.error(f"Could not load {process} wrapper. "
                             "Wrapper may have been disabled.")
                return 1

            processes.append(command_builder)

        # check if all processes initialized correctly
        allOK = True
        for process in processes:
            if not process.isOK:
                allOK = False
                class_name = process.__class__.__name__.replace('Wrapper', '')
                logger.error("{} was not initialized properly".format(class_name))

        # exit if any wrappers did not initialized properly
        if not allOK:
            logger.info("Refer to ERROR messages above to resolve issues.")
            return 1

        loop_order = config.getstr('config', 'LOOP_ORDER', '').lower()

        if loop_order == "processes":
            all_commands = []
            for process in processes:
                new_commands = process.run_all_times()
                if new_commands:
                    all_commands.extend(new_commands)

        elif loop_order == "times":
            all_commands = loop_over_times_and_call(config, processes)
        else:
            logger.error("Invalid LOOP_ORDER defined. "
                         "Options are processes, times")
            return 1

        # if process list contains any wrapper that should run commands
        if any([item[0] not in NO_COMMAND_WRAPPERS for item in process_list]):
            # write out all commands and environment variables to file
            if not write_all_commands(all_commands, config):
                # report an error if no commands were generated
                total_errors += 1

        # compute total number of errors that occurred and output results
        for process in processes:
            if process.errors != 0:
                process_name = process.__class__.__name__.replace('Wrapper', '')
                error_msg = '{} had {} error'.format(process_name, process.errors)
                if process.errors > 1:
                    error_msg += 's'
                error_msg += '.'
                logger.error(error_msg)
                total_errors += process.errors

        return total_errors
    except:
        logger.exception("Fatal error occurred")
        logger.info(f"Check the log file for more information: {config.getstr('config', 'LOG_METPLUS')}")
        return 1

def post_run_cleanup(config, app_name, total_errors):
    logger = config.logger
    # scrub staging directory if requested
    if config.getbool('config', 'SCRUB_STAGING_DIR', False) and\
       os.path.exists(config.getdir('STAGING_DIR')):
        staging_dir = config.getdir('STAGING_DIR')
        logger.info("Scrubbing staging dir: %s", staging_dir)
        shutil.rmtree(staging_dir)

    # save log file path and clock time before writing final conf file
    log_message = (f"Check the log file for more information: "
                   f"{config.getstr('config', 'LOG_METPLUS')}")

    start_clock_time = datetime.datetime.strptime(config.getstr('config',
                                                                'CLOCK_TIME'),
                                                  '%Y%m%d%H%M%S')

    # rewrite final conf so it contains all of the default values used
    write_final_conf(config)

    # compute time it took to run
    end_clock_time = datetime.datetime.now()
    total_run_time = end_clock_time - start_clock_time
    logger.debug(f"{app_name} took {total_run_time} to run.")

    user_info = get_user_info()
    user_string = f' as user {user_info}' if user_info else ''
    if not total_errors:
        logger.info(log_message)
        logger.info('%s has successfully finished running%s.',
                    app_name, user_string)
        return

    error_msg = (f'{app_name} has finished running{user_string} '
                 f'but had {total_errors} error')
    if total_errors > 1:
        error_msg += 's'
    error_msg += '.'
    logger.error(error_msg)
    logger.info(log_message)
    sys.exit(1)

def get_user_info():
    """! Get user information from OS. Note that some OS cannot obtain user ID
    and some cannot obtain username.

    @returns username(uid) if both username and user ID can be read,
     username if only username can be read, uid if only user ID can be read,
     or an empty string if neither can be read.
    """
    try:
        username = os.getlogin()
    except FileNotFoundError:
        username = None

    try:
        uid = os.getuid()
    except AttributeError:
        uid = None

    if username and uid:
        return f'{username}({uid})'

    if username:
        return username

    if uid:
        return uid

    return ''

def write_all_commands(all_commands, config):
    """! Write all commands that were run to a file in the log
     directory. This includes the environment variables that
     were set before each command.

    @param all_commands list of tuples with command run and
     list of environment variables that were set
    @param config METplusConfig object used to write log output
     and get the log timestamp to name the output file
    @returns False if no commands were provided, True otherwise
    """
    if not all_commands:
        config.logger.error("No commands were run. "
                            "Skip writing all_commands file")
        return False

    log_timestamp = config.getstr('config', 'LOG_TIMESTAMP')
    filename = os.path.join(config.getdir('LOG_DIR'),
                            f'.all_commands.{log_timestamp}')
    config.logger.debug(f"Writing all commands and environment to {filename}")
    with open(filename, 'w') as file_handle:
        for command, envs in all_commands:
            for env in envs:
                file_handle.write(f"{env}\n")

            file_handle.write("COMMAND:\n")
            file_handle.write(f"{command}\n\n")

    return True

def handle_tmp_dir(config):
    """! if env var MET_TMP_DIR is set, override config TMP_DIR with value
     if it differs from what is set
     get config temp dir using getdir_nocheck to bypass check for /path/to
     this is done so the user can set env MET_TMP_DIR instead of config TMP_DIR
     and config TMP_DIR will be set automatically"""
    handle_env_var_config(config, 'MET_TMP_DIR', 'TMP_DIR')

    # create temp dir if it doesn't exist already
    # this will fail if TMP_DIR is not set correctly and
    # env MET_TMP_DIR was not set
    mkdir_p(config.getdir('TMP_DIR'))

def handle_env_var_config(config, env_var_name, config_name):
    """! If environment variable is set, use that value
     for the config variable and warn if the previous config value differs

     @param config METplusConfig object to read
     @param env_var_name name of environment variable to read
     @param config_name name of METplus config variable to check
    """
    env_var_value = os.environ.get(env_var_name, '')
    config_value = config.getdir_nocheck(config_name, '')

    # do nothing if environment variable is not set
    if not env_var_value:
        return

    # override config config variable to environment variable value
    config.set('config', config_name, env_var_value)

    # if config config value differed from environment variable value, warn
    if config_value != env_var_value:
        config.logger.warning(f'Config variable {config_name} ({config_value}) '
                              'will be overridden by the environment variable '
                              f'{env_var_name} ({env_var_value})')

def get_skip_times(config, wrapper_name=None):
    """! Read SKIP_TIMES config variable and populate dictionary of times that should be skipped.
         SKIP_TIMES should be in the format: "%m:begin_end_incr(3,11,1)", "%d:30,31", "%Y%m%d:20201031"
         where each item inside quotes is a datetime format, colon, then a list of times in that format
         to skip.
         Args:
             @param config configuration object to pull SKIP_TIMES
             @param wrapper_name name of wrapper if supporting
               skipping times only for certain wrappers, i.e. grid_stat
             @returns dictionary containing times to skip
    """
    skip_times_dict = {}
    skip_times_string = None

    # if wrapper name is set, look for wrapper-specific _SKIP_TIMES variable
    if wrapper_name:
        skip_times_string = config.getstr('config',
                                          f'{wrapper_name.upper()}_SKIP_TIMES', '')

    # if skip times string has not been found, check for generic SKIP_TIMES
    if not skip_times_string:
        skip_times_string = config.getstr('config', 'SKIP_TIMES', '')

        # if no generic SKIP_TIMES, return empty dictionary
        if not skip_times_string:
            return {}

    # get list of skip items, but don't expand begin_end_incr yet
    skip_list = getlist(skip_times_string, expand_begin_end_incr=False)

    for skip_item in skip_list:
        try:
            time_format, skip_times = skip_item.split(':')

            # get list of skip times for the time format, expanding begin_end_incr
            skip_times_list = getlist(skip_times)

            # if time format is already in skip times dictionary, extend list
            if time_format in skip_times_dict:
                skip_times_dict[time_format].extend(skip_times_list)
            else:
                skip_times_dict[time_format] = skip_times_list

        except ValueError:
            config.logger.error(f"SKIP_TIMES item does not match format: {skip_item}")
            return None

    return skip_times_dict

def skip_time(time_info, skip_times):
    """!Used to check the valid time of the current run time against list of times to skip.
        Args:
            @param time_info dictionary with time information to check
            @param skip_times dictionary of times to skip, i.e. {'%d': [31]} means skip 31st day
            @returns True if run time should be skipped, False if not
    """
    if not skip_times:
        return False

    for time_format, skip_time_list in skip_times.items():
        # extract time information from valid time based on skip time format
        run_time_value = time_info.get('valid')
        if not run_time_value:
            return False

        run_time_value = run_time_value.strftime(time_format)

        # loop over times to skip for this format and check if it matches
        for skip_time in skip_time_list:
            if int(run_time_value) == int(skip_time):
                return True

    # if skip time never matches, return False
    return False

def write_final_conf(config):
    """! Write final conf file including default values that were set during
     run. Move variables that are specific to the user's run to the [runtime]
     section to avoid issues such as overwriting existing log files.

        @param config METplusConfig object to write to file
     """
    # write out os environment to file for debugging
    env_file = os.path.join(config.getdir('LOG_DIR'), '.metplus_user_env')
    with open(env_file, 'w') as env_file:
        for key, value in os.environ.items():
            env_file.write('{}={}\n'.format(key, value))

    final_conf = config.getstr('config', 'METPLUS_CONF')

    # remove variables that start with CURRENT
    config.remove_current_vars()

    # move runtime variables to [runtime] section
    config.move_runtime_configs()

    config.logger.info('Overwrite final conf here: %s' % (final_conf,))
    with open(final_conf, 'wt') as conf_file:
        config.write(conf_file)

def is_loop_by_init(config):
    """!Check config variables to determine if looping by valid or init time"""
    if config.has_option('config', 'LOOP_BY'):
        loop_by = config.getstr('config', 'LOOP_BY').lower()
        if loop_by in ['init', 'retro']:
            return True
        elif loop_by in ['valid', 'realtime']:
            return False

    if config.has_option('config', 'LOOP_BY_INIT'):
        return config.getbool('config', 'LOOP_BY_INIT')

    msg = 'MUST SET LOOP_BY to VALID, INIT, RETRO, or REALTIME'
    if config.logger is None:
        print(msg)
    else:
        config.logger.error(msg)

    return None

def loop_over_times_and_call(config, processes, custom=None):
    """! Loop over all run times and call wrappers listed in config

    @param config METplusConfig object
    @param processes list of CommandBuilder subclass objects (Wrappers) to call
    @param custom (optional) custom loop string value
    @returns list of tuples with all commands run and the environment variables
    that were set for each
    """
    # keep track of commands that were run
    all_commands = []
    for time_input in time_generator(config):
        if not isinstance(processes, list):
            processes = [processes]

        for process in processes:
            # if time could not be read, increment errors for each process
            if time_input is None:
                process.errors += 1
                continue

            log_runtime_banner(config, time_input, process)
            add_to_time_input(time_input,
                              instance=process.instance,
                              custom=custom)

            process.clear()
            process.run_at_time(time_input)
            if process.all_commands:
                all_commands.extend(process.all_commands)
            process.all_commands.clear()

    return all_commands

def log_runtime_banner(config, time_input, process):
    loop_by = time_input['loop_by']
    run_time = time_input[loop_by].strftime("%Y-%m-%d %H:%M")

    process_name = process.__class__.__name__
    if process.instance:
        process_name = f"{process_name}({process.instance})"

    config.logger.info("****************************************")
    config.logger.info(f"* Running METplus {process_name}")
    config.logger.info(f"*  at {loop_by} time: {run_time}")
    config.logger.info("****************************************")

def add_to_time_input(time_input, clock_time=None, instance=None, custom=None):
    if clock_time:
        clock_dt = datetime.datetime.strptime(clock_time, '%Y%m%d%H%M%S')
        time_input['now'] = clock_dt

    # if instance is set, use that value, otherwise use empty string
    time_input['instance'] = instance if instance else ''

    # if custom is specified, set it
    # otherwise leave it unset so it can be set within the wrapper
    if custom:
        time_input['custom'] = custom

def get_lead_sequence(config, input_dict=None, wildcard_if_empty=False):
    """!Get forecast lead list from LEAD_SEQ or compute it from INIT_SEQ.
        Restrict list by LEAD_SEQ_[MIN/MAX] if set. Now returns list of relativedelta objects
        Args:
            @param config METplusConfig object to query config variable values
            @param input_dict time dictionary needed to handle using INIT_SEQ. Must contain
               valid key if processing INIT_SEQ
            @param wildcard_if_empty if no lead sequence was set, return a
             list with '*' if this is True, otherwise return a list with 0
            @returns list of relativedelta objects or a list containing 0 if none are found
    """

    out_leads = []
    lead_min, lead_max, no_max = get_lead_min_max(config)

    # check if LEAD_SEQ, INIT_SEQ, or LEAD_SEQ_<n> are set
    # if more than one is set, report an error and exit
    lead_seq = getlist(config.getstr('config', 'LEAD_SEQ', ''))
    init_seq = getlistint(config.getstr('config', 'INIT_SEQ', ''))
    lead_groups = get_lead_sequence_groups(config)

    if not are_lead_configs_ok(lead_seq,
                               init_seq,
                               lead_groups,
                               config,
                               input_dict,
                               no_max):
        return None

    if lead_seq:
        # return lead sequence if wildcard characters are used
        if lead_seq == ['*']:
            return lead_seq

        out_leads = handle_lead_seq(config,
                                    lead_seq,
                                    lead_min,
                                    lead_max)

    # use INIT_SEQ to build lead list based on the valid time
    elif init_seq:
        out_leads = handle_init_seq(init_seq,
                                    input_dict,
                                    lead_min,
                                    lead_max)
    elif lead_groups:
        out_leads = handle_lead_groups(lead_groups)

    if not out_leads:
        if wildcard_if_empty:
            return ['*']

        return [0]

    return out_leads

def are_lead_configs_ok(lead_seq, init_seq, lead_groups,
                        config, input_dict, no_max):
    if lead_groups is None:
        return False

    error_message = ('are both listed in the configuration. '
                     'Only one may be used at a time.')
    if lead_seq:
        if init_seq:
            config.logger.error(f'LEAD_SEQ and INIT_SEQ {error_message}')
            return False

        if lead_groups:
            config.logger.error(f'LEAD_SEQ and LEAD_SEQ_<n> {error_message}')
            return False

    if init_seq and lead_groups:
        config.logger.error(f'INIT_SEQ and LEAD_SEQ_<n> {error_message}')
        return False

    if init_seq:
        # if input dictionary not passed in,
        # cannot compute lead sequence from it, so exit
        if input_dict is None:
            config.logger.error('Cannot run using INIT_SEQ for this wrapper')
            return False

        # if looping by init, fail and exit
        if 'valid' not in input_dict.keys():
            log_msg = ('INIT_SEQ specified while looping by init time.'
                       ' Use LEAD_SEQ or change to loop by valid time')
            config.logger.error(log_msg)
            return False

        # maximum lead must be specified to run with INIT_SEQ
        if no_max:
            config.logger.error('LEAD_SEQ_MAX must be set to use INIT_SEQ')
            return False

    return True

def get_lead_min_max(config):
    # remove any items that are outside of the range specified
    #  by LEAD_SEQ_MIN and LEAD_SEQ_MAX
    # convert min and max to relativedelta objects, then use current time
    # to compare them to each forecast lead
    # this is an approximation because relative time offsets depend on
    # each runtime
    huge_max = '4000Y'
    lead_min_str = config.getstr_nocheck('config', 'LEAD_SEQ_MIN', '0')
    lead_max_str = config.getstr_nocheck('config', 'LEAD_SEQ_MAX', huge_max)
    no_max = lead_max_str == huge_max
    lead_min = time_util.get_relativedelta(lead_min_str, 'H')
    lead_max = time_util.get_relativedelta(lead_max_str, 'H')
    return lead_min, lead_max, no_max

def handle_lead_seq(config, lead_strings, lead_min=None, lead_max=None):
    out_leads = []
    leads = []
    for lead in lead_strings:
        relative_delta = time_util.get_relativedelta(lead, 'H')
        if relative_delta is not None:
            leads.append(relative_delta)
        else:
            config.logger.error(f'Invalid item {lead} in LEAD_SEQ. Exiting.')
            return None

    if lead_min is None and lead_max is None:
        return leads

    now_time = datetime.datetime.now()
    lead_min_approx = now_time + lead_min
    lead_max_approx = now_time + lead_max
    for lead in leads:
        lead_approx = now_time + lead
        if lead_approx >= lead_min_approx and lead_approx <= lead_max_approx:
            out_leads.append(lead)

    return out_leads

def handle_init_seq(init_seq, input_dict, lead_min, lead_max):
    out_leads = []
    lead_min_hours = time_util.ti_get_hours_from_relativedelta(lead_min)
    lead_max_hours = time_util.ti_get_hours_from_relativedelta(lead_max)

    valid_hr = int(input_dict['valid'].strftime('%H'))
    for init in init_seq:
        if valid_hr >= init:
            current_lead = valid_hr - init
        else:
            current_lead = valid_hr + (24 - init)

        while current_lead <= lead_max_hours:
            if current_lead >= lead_min_hours:
                out_leads.append(relativedelta(hours=current_lead))
            current_lead += 24

    out_leads = sorted(out_leads, key=lambda
        rd: time_util.ti_get_seconds_from_relativedelta(rd,
                                                        input_dict['valid']))
    return out_leads

def handle_lead_groups(lead_groups):
    """! Read groups of forecast leads and create a list with all unique items

         @param lead_group dictionary where the values are lists of forecast
         leads stored as relativedelta objects
         @returns list of forecast leads stored as relativedelta objects
    """
    out_leads = []
    for _, lead_seq in lead_groups.items():
        for lead in lead_seq:
            if lead not in out_leads:
                out_leads.append(lead)

    return out_leads

def get_lead_sequence_groups(config):
    # output will be a dictionary where the key will be the
    #  label specified and the value will be the list of forecast leads
    lead_seq_dict = {}
    # used in plotting
    all_conf = config.keys('config')
    indices = []
    regex = re.compile(r"LEAD_SEQ_(\d+)")
    for conf in all_conf:
        result = regex.match(conf)
        if result is not None:
            indices.append(result.group(1))

    # loop over all possible variables and add them to list
    for index in indices:
        if config.has_option('config', f"LEAD_SEQ_{index}_LABEL"):
            label = config.getstr('config', f"LEAD_SEQ_{index}_LABEL")
        else:
            log_msg = (f'Need to set LEAD_SEQ_{index}_LABEL to describe '
                       f'LEAD_SEQ_{index}')
            config.logger.error(log_msg)
            return None

        # get forecast list for n
        lead_string_list = getlist(config.getstr('config', f'LEAD_SEQ_{index}'))
        lead_seq = handle_lead_seq(config,
                                   lead_string_list,
                                   lead_min=None,
                                   lead_max=None)
        # add to output dictionary
        lead_seq_dict[label] = lead_seq

    return lead_seq_dict

def round_0p5(val):
    """! Round to the nearest point five (ie 3.3 rounds to 3.5, 3.1
       rounds to 3.0) Take the input value, multiply by two, round to integer
       (no decimal places) then divide by two.  Expect any input value of n.0,
       n.1, or n.2 to round down to n.0, and any input value of n.5, n.6 or
       n.7 to round to n.5. Finally, any input value of n.8 or n.9 will
       round to (n+1).0
       Args:
          @param val :  The number to be rounded to the nearest .5
       Returns:
          pt_five:  The n.0, n.5, or (n+1).0 value as
                            a result of rounding the input value, val.
    """

    return round(val * 2) / 2

def mkdir_p(path):
    """!
       From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any
       required intermediate directories).
       Args:
           @param path : The full directory path to be created
       Returns
           None: Creates the full directory path if it doesn't exist,
                 does nothing otherwise.
    """
    Path(path).mkdir(parents=True, exist_ok=True)

def get_storms(filter_filename, id_only=False, sort_column='STORM_ID'):
    """! Get each storm as identified by a column in the input file.
         Create dictionary storm ID as the key and a list of lines for that
         storm as the value.

         @param filter_filename name of tcst file to read and extract storm id
         @param sort_column column to use to sort and group storms. Default
          value is STORM_ID
         @returns 2 item tuple - 1)dictionary where key is storm ID and value
          is list of relevant lines from tcst file, 2) header line from tcst
           file. Item with key 'header' contains the header of the tcst file
    """
    # Initialize a set because we want unique storm ids.
    storm_id_list = set()

    try:
        with open(filter_filename, "r") as file_handle:
            header, *lines = file_handle.readlines()

        storm_id_column = header.split().index(sort_column)
        for line in lines:
            storm_id_list.add(line.split()[storm_id_column])
    except (ValueError, FileNotFoundError):
        if id_only:
            return []
        return {}

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)
    if id_only:
        return sorted_storms

    if not sorted_storms:
        return {}

    storm_dict = {'header': header}
    # for each storm, get all lines for that storm
    for storm in sorted_storms:
        storm_dict[storm] = [line for line in lines if storm in line]

    return storm_dict

def get_files(filedir, filename_regex, logger=None):
    """! Get all the files (with a particular
        naming format) by walking
        through the directories.
        Args:
          @param filedir:  The topmost directory from which the
                           search begins.
          @param filename_regex:  The regular expression that
                                  defines the naming format
                                  of the files of interest.
       Returns:
          file_paths (string): a list of filenames (with full filepath)
    """
    file_paths = []

    # Walk the tree
    for root, _, files in os.walk(filedir):
        for filename in files:
            # add it to the list only if it is a match
            # to the specified format
            match = re.match(filename_regex, filename)
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
            else:
                continue
    return sorted(file_paths)

def prune_empty(output_dir, logger):
    """! Start from the output_dir, and recursively check
        all directories and files.  If there are any empty
        files or directories, delete/remove them so they
        don't cause performance degradation or errors
        when performing subsequent tasks.
        Input:
            @param output_dir:  The directory from which searching
                                should begin.
            @param logger: The logger to which all logging is
                           directed.
    """

    # Check for empty files.
    for root, dirs, files in os.walk(output_dir):
        # Create a full file path by joining the path
        # and filename.
        for a_file in files:
            a_file = os.path.join(root, a_file)
            if os.stat(a_file).st_size == 0:
                logger.debug("Empty file: " + a_file +
                             "...removing")
                os.remove(a_file)

    # Now check for any empty directories, some
    # may have been created when removing
    # empty files.
    for root, dirs, files in os.walk(output_dir):
        for direc in dirs:
            full_dir = os.path.join(root, direc)
            if not os.listdir(full_dir):
                logger.debug("Empty directory: " + full_dir +
                             "...removing")
                os.rmdir(full_dir)

def camel_to_underscore(camel):
    """! Change camel case notation to underscore notation, i.e. GridStatWrapper to grid_stat_wrapper
         Multiple capital letters are excluded, i.e. PCPCombineWrapper to pcp_combine_wrapper
         Numerals are also skipped, i.e. ASCII2NCWrapper to ascii2nc_wrapper
         Args:
             @param camel string to convert
             @returns string in underscore notation
    """
    s1 = re.sub(r'([^\d])([A-Z][a-z]+)', r'\1_\2', camel)
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', s1).lower()

def shift_time_seconds(time_str, shift):
    """ Adjust time by shift seconds. Format is %Y%m%d%H%M%S
        Args:
            @param time_str: Start time in %Y%m%d%H%M%S
            @param shift: Amount to adjust time in seconds
        Returns:
            New time in format %Y%m%d%H%M%S
    """
    return (datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S") +
            datetime.timedelta(seconds=shift)).strftime("%Y%m%d%H%M%S")

def get_threshold_via_regex(thresh_string):
    """!Ensure thresh values start with >,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le and then a number
        Optionally can have multiple comparison/number pairs separated with && or ||.
        Args:
            @param thresh_string: String to examine, i.e. <=3.4
        Returns:
            None if string does not match any valid comparison operators or does
              not contain a number afterwards
            regex match object with comparison operator in group 1 and
            number in group 2 if valid
    """

    comparison_number_list = []
    # split thresh string by || or &&
    thresh_split = re.split(r'\|\||&&', thresh_string)
    # check each threshold for validity
    for thresh in thresh_split:
        found_match = False
        for comp in list(VALID_COMPARISONS)+list(VALID_COMPARISONS.values()):
            # if valid, add to list of tuples
            # must be one of the valid comparison operators followed by
            # at least 1 digit or NA
            if thresh == 'NA':
                comparison_number_list.append((thresh, ''))
                found_match = True
                break

            match = re.match(r'^('+comp+r')(.*\d.*)$', thresh)
            if match:
                comparison = match.group(1)
                number = match.group(2)
                # try to convert to float if it can, but allow string
                try:
                    number = float(number)
                except ValueError:
                    pass

                comparison_number_list.append((comparison, number))
                found_match = True
                break

        # if no match was found for the item, return None
        if not found_match:
            return None

    if not comparison_number_list:
        return None

    return comparison_number_list

def comparison_to_letter_format(expression):
    """! Convert comparison operator to the letter version if it is not already
         @args expression string starting with comparison operator to
          convert, i.e. gt3 or <=5.4
         @returns letter comparison operator, i.e. gt3 or le5.4 or None if invalid
    """
    for symbol_comp, letter_comp in VALID_COMPARISONS.items():
        if letter_comp in expression or symbol_comp in expression:
            return expression.replace(symbol_comp, letter_comp)

    return None

def validate_thresholds(thresh_list):
    """ Checks list of thresholds to ensure all of them have the correct format
        Should be a comparison operator with number pair combined with || or &&
        i.e. gt4 or >3&&<5 or gt3||lt1
        Args:
            @param thresh_list list of strings to check
        Returns:
            True if all items in the list are valid format, False if not
    """
    valid = True
    for thresh in thresh_list:
        match = get_threshold_via_regex(thresh)
        if match is None:
            valid = False

    if valid is False:
        print("ERROR: Threshold values must use >,>=,==,!=,<,<=,gt,ge,eq,ne,lt, or le with a number, "
              "optionally combined with && or ||")
        return False
    return True

def write_list_to_file(filename, output_list):
    with open(filename, 'w+') as f:
        for line in output_list:
            f.write(f"{line}\n")

def format_var_items(field_configs, time_info=None):
    """! Substitute time information into field information and format values.

        @param field_configs dictionary with config variable names to read
        @param time_info dictionary containing time info for current run
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
        search_name = do_string_sub(search_name,
                                    skip_missing_tags=True,
                                    **time_info)
    var_items['name'] = search_name

    # get levels, performing string substitution on each item of list
    for level in getlist(field_configs.get('levels')):
        if time_info:
            level = do_string_sub(level,
                                  **time_info)
        var_items['levels'].append(level)

    # if no levels are found, add an empty string
    if not var_items['levels']:
        var_items['levels'].append('')

    # get threshold list if it is set
    # return error string if any thresholds not formatted properly
    search_thresh = field_configs.get('thresh')
    if search_thresh:
        thresh = getlist(search_thresh)
        if not validate_thresholds(thresh):
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

def sub_var_info(var_info, time_info):
    if not var_info:
        return {}

    out_var_info = {}
    for key, value in var_info.items():
        if isinstance(value, list):
            out_value = []
            for item in value:
                out_value.append(do_string_sub(item,
                                               skip_missing_tags=True,
                                               **time_info))
        else:
            out_value = do_string_sub(value,
                                      skip_missing_tags=True,
                                      **time_info)

        out_var_info[key] = out_value

    return out_var_info

def sub_var_list(var_list, time_info):
    """! Perform string substitution on var list values with time info

        @param var_list list of field info to substitute values into
        @param time_info dictionary containing time information
        @returns var_list with values substituted
    """
    if not var_list:
        return []

    out_var_list = []
    for var_info in var_list:
        out_var_info = sub_var_info(var_info, time_info)
        out_var_list.append(out_var_info)

    return out_var_list

def split_level(level):
    """! If level value starts with a letter, then separate that letter from
     the rest of the string. i.e. 'A03' will be returned as 'A', '03'. If no
     level type letter is found and the level value consists of alpha-numeric
     characters, return an empty string as the level type and the full level
     string as the level value

     @param level input string to parse/split
     @returns tuple of level type and level value
    """
    if not level:
        return '', ''

    match = re.match(r'^([a-zA-Z])(\w+)$', level)
    if match:
        level_type = match.group(1)
        level = match.group(2)
        return level_type, level

    match = re.match(r'^[\w]+$', level)
    if match:
        return '', level

    return '', ''

def get_filetype(filepath, logger=None):
    """!This function determines if the filepath is a NETCDF or GRIB file
       based on the first eight bytes of the file.
       It returns the string GRIB, NETCDF, or a None object.

       Note: If it is NOT determined to ba a NETCDF file,
       it returns GRIB, regardless.
       Unless there is an IOError exception, such as filepath refers
       to a non-existent file or filepath is only a directory, than
       None is returned, without a system exit.

       Args:
           @param filepath:  path/to/filename
           @param logger the logger, optional
       Returns:
           @returns The string GRIB, NETCDF or a None object
    """
    # Developer Note
    # Since we have the impending code-freeze, keeping the behavior the same,
    # just changing the implementation.
    # The previous logic did not test for GRIB it would just return 'GRIB'
    # if you couldn't run ncdump on the file.
    # Also note:
    # As John indicated ... there is the case when a grib file
    # may not start with GRIB ... and if you pass the MET command filtetype=GRIB
    # MET will handle it ok ...

    # Notes on file format and determining type.
    # https://www.wmo.int/pages/prog/www/WDM/Guides/Guide-binary-2.html
    # https://www.unidata.ucar.edu/software/netcdf/docs/faq.html
    # http: // www.hdfgroup.org / HDF5 / doc / H5.format.html

    # Interpreting single byte by byte - so ok to ignore endianess
    # od command:
    #   od -An -c -N8 foo.nc
    #   od -tx1 -N8 foo.nc
    # GRIB
    # Octet no.  IS Content
    # 1-4        'GRIB' (Coded CCITT-ITA No. 5) (ASCII);
    # 5-7        Total length, in octets, of GRIB message(including Sections 0 & 5);
    # 8          Edition number - currently 1
    # NETCDF .. ie. od -An -c -N4 foo.nc which will output
    # C   D   F 001
    # C   D   F 002
    # 211   H   D   F
    # HDF5
    # Magic numbers   Hex: 89 48 44 46 0d 0a 1a 0a
    # ASCII: \211 HDF \r \n \032 \n

    # Below is a reference that may be used in the future to
    # determine grib version.
    # import struct
    # with open ("foo.grb2","rb")as binary_file:
    #     binary_file.seek(7)
    #     one_byte = binary_file.read(1)
    #
    # This would return an integer with value 1 or 2,
    # B option is an unsigned char.
    #  struct.unpack('B',one_byte)[0]

    # if filepath is set to None, return None to avoid crash
    if filepath == None:
        return None

    try:
        # read will return up to 8 bytes, if file is 0 bytes in length,
        # than first_eight_bytes will be the empty string ''.
        # Don't test the file length, just adds more time overhead.
        with open(filepath, "rb") as binary_file:
            binary_file.seek(0)
            first_eight_bytes = binary_file.read(8)

        # From the first eight bytes of the file, unpack the bytes
        # of the known identifier byte locations, in to a string.
        # Example, if this was a netcdf file than ONLY name_cdf would
        # equal 'CDF' the other variables, name_hdf would be 'DF '
        # name_grid 'CDF '
        name_cdf, name_hdf, name_grib = [None] * 3
        if len(first_eight_bytes) == 8:
            name_cdf = struct.unpack('3s', first_eight_bytes[:3])[0]
            name_hdf = struct.unpack('3s', first_eight_bytes[1:4])[0]
            name_grib = struct.unpack('4s', first_eight_bytes[:4])[0]

        # Why not just use a else, instead of elif else if we are going to
        # return GRIB ? It allows for expansion, ie. Maybe we pass in a
        # logger and log the cases we can't determine the type.
        if name_cdf == 'CDF' or name_hdf == 'HDF':
            return "NETCDF"
        elif name_grib == 'GRIB':
            return "GRIB"
        else:
            # This mimicks previous behavoir, were we at least will always return GRIB.
            # It also handles the case where GRIB was not in the first 4 bytes
            # of a legitimate grib file, see John.
            # logger.info('Can't determine type, returning GRIB
            # as default %s'%filepath)
            return "GRIB"

    except IOError:
        # Skip the IOError, and keep processing data.
        # ie. filepath references a file that does not exist
        # or filepath is a directory.
        return None

    # Previous Logic
    # ncdump_exe = config.getexe('NCDUMP')
    #try:
    #    result = subprocess.check_output([ncdump_exe, filepath])

    #except subprocess.CalledProcessError:
    #    return "GRIB"

    #regex = re.search("netcdf", result)
    #if regex is not None:
    #    return "NETCDF"
    #else:
    #    return None

def preprocess_file(filename, data_type, config, allow_dir=False):
    """ Decompress gzip, bzip, or zip files or convert Gempak files to NetCDF
        Args:
            @param filename: Path to file without zip extensions
            @param config: Config object
        Returns:
            Path to staged unzipped file or original file if already unzipped
    """
    if not filename:
        return None

    if allow_dir and os.path.isdir(filename):
        return filename

    # if using python embedding for input, return the keyword
    if os.path.basename(filename) in PYTHON_EMBEDDING_TYPES:
        return os.path.basename(filename)

    # if filename starts with a python embedding type, return the full value
    for py_embed_type in PYTHON_EMBEDDING_TYPES:
        if filename.startswith(py_embed_type):
            return filename

    # if _INPUT_DATATYPE value contains PYTHON, return the full value
    if data_type is not None and 'PYTHON' in data_type:
        return filename

    stage_dir = config.getdir('STAGING_DIR')

    if os.path.isfile(filename):
        # if filename provided ends with a valid compression extension,
        # remove the extension and call function again so the
        # file will be uncompressed properly. This is done so that
        # the function will handle files passed to it with an
        # extension the same way as files passed
        # without an extension but the compressed equivalent exists
        for ext in COMPRESSION_EXTENSIONS:
            if filename.endswith(ext):
                return preprocess_file(filename[:-len(ext)], data_type, config)
        # if extension is grd (Gempak), then look in staging dir for nc file
        if filename.endswith('.grd') or data_type == "GEMPAK":
            if filename.endswith('.grd'):
                stagefile = stage_dir + filename[:-3]+"nc"
            else:
                stagefile = stage_dir + filename+".nc"
            if os.path.isfile(stagefile):
                return stagefile
            # if it does not exist, run GempakToCF and return staged nc file
            # Create staging area if it does not exist
            mkdir_p(os.path.dirname(stagefile))

            # only import GempakToCF if needed
            from ..wrappers import GempakToCFWrapper

            run_g2c = GempakToCFWrapper(config)
            run_g2c.infiles.append(filename)
            run_g2c.set_output_path(stagefile)
            cmd = run_g2c.get_command()
            if cmd is None:
                config.logger.error("GempakToCF could not generate command")
                return None
            if config.logger:
                config.logger.debug("Converting Gempak file into {}".format(stagefile))
            run_g2c.build()
            return stagefile

        return filename

    # nc file requested and the Gempak equivalent exists
    if os.path.isfile(filename[:-2]+'grd'):
        return preprocess_file(filename[:-2]+'grd', data_type, config)

    # if file exists in the staging area, return that path
    outpath = stage_dir + filename
    if os.path.isfile(outpath):
        return outpath

    # Create staging area directory only if file has compression extension
    if any([os.path.isfile(f'{filename}{ext}')
            for ext in COMPRESSION_EXTENSIONS]):
        mkdir_p(os.path.dirname(outpath))

    # uncompress gz, bz2, or zip file
    if os.path.isfile(filename+".gz"):
        if config.logger:
            config.logger.debug("Uncompressing gz file to {}".format(outpath))
        with gzip.open(filename+".gz", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(infile.read())
                infile.close()
                outfile.close()
                return outpath
    elif os.path.isfile(filename+".bz2"):
        if config.logger:
            config.logger.debug("Uncompressing bz2 file to {}".format(outpath))
        with open(filename+".bz2", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(bz2.decompress(infile.read()))
                infile.close()
                outfile.close()
                return outpath
    elif os.path.isfile(filename+".zip"):
        if config.logger:
            config.logger.debug("Uncompressing zip file to {}".format(outpath))
        with zipfile.ZipFile(filename+".zip") as z:
            with open(outpath, 'wb') as f:
                f.write(z.read(os.path.basename(filename)))
                return outpath

    # if input doesn't need to exist, return filename
    if not config.getbool('config', 'INPUT_MUST_EXIST', True):
        return filename

    return None

def template_to_regex(template, time_info):
    in_template = re.sub(r'\.', '\\.', template)
    in_template = re.sub(r'{lead.*?}', '.*', in_template)
    return do_string_sub(in_template,
                         **time_info)

def is_python_script(name):
    """ Check if field name is a python script by checking if any of the words
     in the string end with .py

     @param name string to check
     @returns True if the name is determined to be a python script command
     """
    if not name:
        return False

    all_items = name.split(' ')
    if any(item.endswith('.py') for item in all_items):
        return True

    return False

def expand_int_string_to_list(int_string):
    """! Expand string into a list of integer values. Items are separated by
    commas. Items that are formatted X-Y will be expanded into each number
    from X to Y inclusive. If the string ends with +, then add a str '+'
    to the end of the list. Used in .github/jobs/get_use_case_commands.py

    @param int_string String containing a comma-separated list of integers
    @returns List of integers and potentially '+' as the last item
    """
    subset_list = []

    # if string ends with +, remove it and add it back at the end
    if int_string.strip().endswith('+'):
        int_string = int_string.strip(' +')
        hasPlus = True
    else:
        hasPlus = False

    # separate into list by comma
    comma_list = int_string.split(',')
    for comma_item in comma_list:
        dash_list = comma_item.split('-')
        # if item contains X-Y, expand it
        if len(dash_list) == 2:
            for i in range(int(dash_list[0].strip()),
                           int(dash_list[1].strip())+1,
                           1):
                subset_list.append(i)
        else:
            subset_list.append(int(comma_item.strip()))

    if hasPlus:
        subset_list.append('+')

    return subset_list

def subset_list(full_list, subset_definition):
    """! Extract subset of items from full_list based on subset_definition
    Used in internal_tests/use_cases/metplus_use_case_suite.py

    @param full_list List of all use cases that were requested
    @param subset_definition Defines how to subset the full list. If None,
    no subsetting occurs. If an integer value, select that index only.
    If a slice object, i.e. slice(2,4,1), pass slice object into list.
    If list, subset full list by integer index values in list. If
    last item in list is '+' then subset list up to 2nd last index, then
    get all items from 2nd last item and above
    """
    if subset_definition is not None:
        subset_list = []

        # if case slice is a list, use only the indices in the list
        if isinstance(subset_definition, list):
            # if last slice value is a plus sign, get rest of items
            # after 2nd last slice value
            if subset_definition[-1] == '+':
                plus_value = subset_definition[-2]
                # add all values before last index before plus
                subset_list.extend([full_list[i]
                                    for i in subset_definition[:-2]])
                # add last index listed + all items above
                subset_list.extend(full_list[plus_value:])
            else:
                # list of integers, so get items based on indices
                subset_list = [full_list[i] for i in subset_definition]
        else:
            subset_list = full_list[subset_definition]
    else:
        subset_list = full_list

    # if only 1 item is left, make it a list before returning
    if not isinstance(subset_list, list):
        subset_list = [subset_list]

    return subset_list

def is_met_netcdf(file_path):
    """! Check if a file is a MET-generated NetCDF file.
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file
         Args:
             @param file_path full path to file to check
             @returns True if file is a MET-generated NetCDF file and False if
              it is not or it can't be determined.
    """
    try:
        from netCDF4 import Dataset
        nc_file = Dataset(file_path, 'r')
        getattr(nc_file, 'MET_version')
    except (AttributeError, OSError, ImportError):
        return False

    return True

def netcdf_has_var(file_path, name, level):
    """! Check if name is a variable in the NetCDF file. If not, check if
         {name}_{level} (with level prefix letter removed, i.e. 06 from A06)
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file
         Args:
             @param file_path full path to file to check
             @returns True if file is a MET-generated NetCDF file and False if
              it is not or it can't be determined.
    """
    try:
        from netCDF4 import Dataset

        nc_file = Dataset(file_path, 'r')
        variables = nc_file.variables.keys()

        # if name is a variable, return that name
        if name in variables:
            return name


        # if name_level is a variable, return that
        name_underscore_level = f"{name}_{split_level(level)[1]}"
        if name_underscore_level in variables:
            return name_underscore_level

        # requested variable name is not found in file
        return None

    except (AttributeError, OSError, ImportError):
        return False

def generate_tmp_filename():
    import random
    import string
    random_string = ''.join(random.choice(string.ascii_letters)
                            for i in range(10))
    return f"metplus_tmp_{random_string}"

def format_level(level):
    """! Format level string to prevent NetCDF level values from creating
         filenames and field names with bad characters. Replaces '*' with 'all'
         and ',' with '_'

        @param level string of level to format
        @returns formatted string
    """
    return level.replace('*', 'all').replace(',', '_')
