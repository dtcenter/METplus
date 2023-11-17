import sys
import os
import shutil
from datetime import datetime
from typing import NamedTuple, Union
from logging import Logger
import shlex

from produtil.run import exe, run

from .string_manip import get_logfile_info, log_terminal_includes_info
from .system_util import get_user_info, write_list_to_file
from .config_util import get_process_list, handle_env_var_config
from .config_util import handle_tmp_dir, write_final_conf, write_all_commands
from .config_validate import validate_config_variables
from .. import get_metplus_version
from .config_metplus import setup
from . import get_wrapper_instance


class RunArgs(NamedTuple):
    logger: Union[Logger, None] = None
    log_path: Union[str, None] = None
    skip_run: bool = False
    log_met_to_metplus: bool = True
    env: os._Environ = os.environ
    copyable_env: str = ''


class PrintLogger(object):
    def __init__(self):
        self.info = print
        self.debug = print
        self.error = print
        self.warning = print


def run_cmd(cmd, run_args):
    if not cmd:
        return 0

    # if env not set, use os.environ
    env = os.environ if run_args.env is None else run_args.env
    if run_args.logger is not None:
        logger = run_args.logger
    else:
        logger = PrintLogger()

    logger.info("COMMAND: %s" % cmd)

    # don't run app if DO_NOT_RUN_EXE is set to True
    if run_args.skip_run:
        logger.info("Not running command (DO_NOT_RUN_EXE = True)")
        return 0

    log_path = run_args.log_path

    # determine if command must be run in a shell
    run_in_shell = '*' in cmd or ';' in cmd or '<' in cmd or '>' in cmd

    # Run the executable and pass the arguments as a sequence.
    # Split the command in to a sequence using shell syntax.
    the_exe = shlex.split(cmd)[0]
    the_args = shlex.split(cmd)[1:]
    if log_path:
        logger.debug("Logging command output to: %s" % log_path)
        _log_header_info(log_path, run_args.copyable_env, cmd, run_args.log_met_to_metplus)

        if run_in_shell:
            cmd_exe = exe('sh')['-c', cmd].env(**env).err2out() >> log_path
        else:
            cmd_exe = exe(the_exe)[the_args].env(**env).err2out() >> log_path
    else:
        if run_in_shell:
            cmd_exe = exe('sh')['-c', cmd].env(**env)
        else:
            cmd_exe = exe(the_exe)[the_args].env(**env).err2out()

    # get current time to calculate total time to run command
    start_cmd_time = datetime.now()

    # run command
    try:
        ret = run(cmd_exe)
    except Exception as err:
        logger.error(f'Exception occurred: {err}')
        ret = -1
    else:
        # calculate time to run
        end_cmd_time = datetime.now()
        total_cmd_time = end_cmd_time - start_cmd_time
        logger.info(f'Finished running {the_exe} - took {total_cmd_time}')

    return ret


def _log_header_info(log_path, copyable_env, cmd, log_met_to_metplus):
    with open(log_path, 'a+') as log_file_handle:
        # if logging MET command to its own log file,
        # add command that was run to that log
        if not log_met_to_metplus:
            # if environment variables were set and available,
            # write them to MET tool log
            if copyable_env:
                log_file_handle.write(
                    "\nCOPYABLE ENVIRONMENT FOR NEXT COMMAND:\n")
                log_file_handle.write(f"{copyable_env}\n\n")
            else:
                log_file_handle.write('\n')

            log_file_handle.write(f"COMMAND:\n{cmd}\n\n")

        # write line to designate where MET tool output starts
        log_file_handle.write("OUTPUT:\n")


def pre_run_setup(config_inputs):

    version_number = get_metplus_version()
    print(f'Starting METplus v{version_number}')

    # Read config inputs and return a config instance
    config = setup(config_inputs)

    logger = config.logger

    user_info = get_user_info()
    user_string = f' as user {user_info} ' if user_info else ' '

    config.set('config', 'METPLUS_VERSION', version_number)
    running_log = (f"Running METplus v{version_number}{user_string}with "
                   f"command: {' '.join(sys.argv)}")
    logger.info(running_log)

    # print running message if terminal log does not include INFO
    if not log_terminal_includes_info(config):
        print(running_log)

    # if log file is not set, log message instructing user how to set it
    log_file = get_logfile_info(config)

    logger.info(f"Log file: {log_file}")
    logger.info(f"METplus Base: {config.getdir('METPLUS_BASE')}")
    logger.info(f"Final Conf: {config.getstr('config', 'METPLUS_CONF')}")
    config_list = config.getstr('config', 'CONFIG_INPUT').split(',')
    for config_item in config_list:
        logger.info(f"Config Input: {config_item}")

    # validate configuration variables
    is_ok, all_sed_cmds = validate_config_variables(config)
    if not is_ok:
        # if any sed commands were generated, write them to the sed file
        if all_sed_cmds:
            sed_file = os.path.join(config.getdir('OUTPUT_BASE'),
                                    'sed_commands.txt')
            # remove if sed file exists
            if os.path.exists(sed_file):
                os.remove(sed_file)

            write_list_to_file(sed_file, all_sed_cmds)
            config.logger.error("Find/Replace commands have been "
                                f"generated in {sed_file}")

        logger.error("Correct configuration variables and rerun. Exiting.")
        logger.info(f"Check the log file for more information: {log_file}")
        return None

    if not config.getdir('MET_INSTALL_DIR', must_exist=True):
        logger.error('MET_INSTALL_DIR must be set correctly to run METplus')
        return None

    # handle dir to write temporary files
    handle_tmp_dir(config)

    # handle OMP_NUM_THREADS environment variable
    handle_env_var_config(config,
                          env_var_name='OMP_NUM_THREADS',
                          config_name='OMP_NUM_THREADS')

    config.env = os.environ.copy()

    return config


def run_metplus(config):
    """!Load all wrapper instances, check for initialization errors, run all
    wrappers, write list of commands to file if any were executed, check
    for wrapper runtime errors.

    @param config METplusConfig object to parse process list, pass to wrapper
    constructors, and log any messages.
    @returns integer number of errors that occurred
    """
    # Use config object to get the list of processes to call
    process_list = get_process_list(config)

    try:
        # if Usage is in process list, run it and exit
        if 'Usage' in [p[0] for p in process_list]:
            wrapper = get_wrapper_instance(config, 'Usage')
            wrapper.run_all_times()
            return 0

        # get all wrapper instances
        processes = _load_all_wrappers(config, process_list)
        if not processes:
            return 1

        # check if all processes initialized correctly
        init_errors = _check_wrapper_init_errors(processes, config.logger)
        if init_errors:
            return init_errors

        all_commands = []
        for process in processes:
            new_commands = process.run_all_times()
            if new_commands:
                all_commands.extend(new_commands)

        # write out all commands and environment variables to file
        write_all_commands(all_commands, config)

        # compute total number of errors that occurred and output results
        return _check_wrapper_run_errors(processes, config.logger)
    except Exception:
        config.logger.exception("Fatal error occurred")
        config.logger.info("Check the log file for more information: "
                           f"{get_logfile_info(config)}")
        return 1


def _load_all_wrappers(config, process_list):
    """!Initialize all METplus wrapper instances in process list.

    @param config METplusConfig object to pass to wrapper constructors
    @param process_list list of tuple containing process name and instance
    identifier if specified.
    @returns list of wrapper instances if all were loaded properly, or None
    if something went wrong.
    """
    processes = []
    is_ok = True
    for process, instance in process_list:
        wrapper = get_wrapper_instance(config, process, instance)
        if not wrapper:
            is_ok = False
            continue
        processes.append(wrapper)

    return processes if is_ok else None


def _check_wrapper_init_errors(processes, logger=None):
    """!Check all wrappers for initialization errors.

    @param processes list of wrapper to check
    @param logger (optional) log object to write logs
    @returns integer number of initialization errors from all wrappers
    """
    all_ok = True
    errors = 0
    for process in processes:
        if process.isOK:
            continue
        all_ok = False
        errors += process.errors
        if logger:
            class_name = process.__class__.__name__.replace('Wrapper', '')
            logger.error("{} was not initialized properly".format(class_name))

    # if any wrappers did not initialize properly
    if not all_ok:
        if logger:
            logger.info("Refer to ERROR messages above to resolve issues.")
        # set number of errors to 1 if no errors were set by wrapper
        if not errors:
            errors = 1

    return errors


def _check_wrapper_run_errors(processes, logger=None):
    total_errors = 0
    for process in processes:
        if not process.errors:
            continue
        total_errors += process.errors

        if not logger:
            continue
        process_name = process.__class__.__name__.replace('Wrapper', '')
        error_msg = f'{process_name} had {process.errors} error'
        if process.errors > 1:
            error_msg += 's'
        error_msg += '.'
        logger.error(error_msg)

    return total_errors


def post_run_cleanup(config, app_name, total_errors):
    logger = config.logger
    # scrub staging directory if requested
    if (config.getbool('config', 'SCRUB_STAGING_DIR') and
            os.path.exists(config.getdir('STAGING_DIR'))):
        staging_dir = config.getdir('STAGING_DIR')
        logger.info("Scrubbing staging dir: %s", staging_dir)
        logger.info('Set SCRUB_STAGING_DIR to False to preserve '
                    'intermediate files.')
        shutil.rmtree(staging_dir)

    # save log file path and clock time before writing final conf file
    log_message = (f"Check the log file for more information: "
                   f"{get_logfile_info(config)}")

    start_clock_time = datetime.strptime(config.getstr('config', 'CLOCK_TIME'),
                                         '%Y%m%d%H%M%S')

    # rewrite final conf so it contains all of the default values used
    write_final_conf(config)

    # compute time it took to run
    end_clock_time = datetime.now()
    total_run_time = end_clock_time - start_clock_time
    logger.info(f"{app_name} took {total_run_time} to run.")

    user_info = get_user_info()
    user_string = f' as user {user_info}' if user_info else ''
    if not total_errors:
        logger.info(log_message)
        success_log = (f'{app_name} has successfully '
                       f'finished running{user_string}.')
        logger.info(success_log)

        # print success log message if terminal does not include INFO
        if not log_terminal_includes_info(config):
            print(success_log)
        return True

    error_msg = (f'{app_name} has finished running{user_string} '
                 f'but had {total_errors} error')
    if total_errors > 1:
        error_msg += 's'
    error_msg += '.'
    logger.error(error_msg)
    logger.info(log_message)
    return False
