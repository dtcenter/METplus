import os
import re

from .string_manip import getlist, get_wrapper_name
from .string_template_substitution import do_string_sub
from .system_util import mkdir_p


def get_process_list(config):
    """!Read process list, Extract instance string if specified inside
     parenthesis. Remove dashes/underscores and change to lower case,
     then map the name to the correct wrapper name

     @param config METplusConfig object to read PROCESS_LIST value
     @returns list of tuple containing process name and instance identifier
     (None if no instance was set)
    """
    # get list of processes
    process_list = getlist(config.getstr('config', 'PROCESS_LIST'))

    out_process_list = []
    # for each item remove dashes, underscores, and cast to lower-case
    for process in process_list:
        # if instance is specified, extract the text inside parenthesis
        match = re.match(r'(.*)\((.*)\)', process)
        if match:
            instance = match.group(2)
            process_name = match.group(1)
        else:
            instance = None
            process_name = process

        wrapper_name = get_wrapper_name(process_name)
        if wrapper_name is None:
            config.logger.warning(f"PROCESS_LIST item {process_name} "
                                  "may be invalid.")
            wrapper_name = process_name

        out_process_list.append((wrapper_name, instance))

    return out_process_list


def get_custom_string_list(config, met_tool):
    var_name = 'CUSTOM_LOOP_LIST'
    custom_loop_list = config.getstr_nocheck('config',
                                             f'{met_tool.upper()}_{var_name}',
                                             config.getstr_nocheck('config',
                                                                   var_name,
                                                                   ''))
    custom_loop_list = getlist(custom_loop_list)
    if not custom_loop_list:
        custom_loop_list.append('')

    return custom_loop_list


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
    if config_value == env_var_value:
        return

    config.logger.warning(f'Config variable {config_name} ({config_value}) '
                          'will be overridden by the environment variable '
                          f'{env_var_name} ({env_var_value})')


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


def write_final_conf(config):
    """! Write final conf file including default values that were set during
     run. Move variables that are specific to the user's run to the [runtime]
     section to avoid issues such as overwriting existing log files.

        @param config METplusConfig object to write to file
     """
    final_conf = config.getstr('config', 'METPLUS_CONF')

    # remove variables that start with CURRENT
    config.remove_current_vars()

    # move runtime variables to [runtime] section
    config.move_runtime_configs()

    config.logger.info('Overwrite final conf here: %s' % (final_conf,))
    with open(final_conf, 'wt') as conf_file:
        config.write(conf_file)


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
        config.logger.info("No commands were run. "
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
        out_var_info = _sub_var_info(var_info, time_info)
        out_var_list.append(out_var_info)

    return out_var_list


def _sub_var_info(var_info, time_info):
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
