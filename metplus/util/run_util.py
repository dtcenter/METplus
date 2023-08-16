import sys
import os
import shutil
import logging
from datetime import datetime
from importlib import import_module

from .constants import NO_COMMAND_WRAPPERS
from .string_manip import get_logfile_info, log_terminal_includes_info
from .system_util import get_user_info, write_list_to_file
from .config_util import get_process_list, handle_env_var_config
from .config_util import handle_tmp_dir, write_final_conf, write_all_commands
from .config_validate import validate_config_variables
from .. import get_metplus_version
from .config_metplus import setup
from . import camel_to_underscore


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
        logger.info("Check the log file for more information: "
                    f"{get_logfile_info(config)}")
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
            wrapper = _get_wrapper_instance(config, 'Usage')
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


def _get_wrapper_instance(config, process, instance=None):
    """!Initialize METplus wrapper instance.

    @param config METplusConfig object to pass to wrapper constructor
    @param process name of wrapper in camel case, e.g. GridStat
    @param instance (optional) instance identifier for creating multiple
    instances of a wrapper. Set to None (default) if no instance is specified
    @returns CommandBuilder sub-class object or None if something went wrong
    """
    try:
        package_name = ('metplus.wrappers.'
                        f'{camel_to_underscore(process)}_wrapper')
        module = import_module(package_name)
        metplus_wrapper = (
            getattr(module, f"{process}Wrapper")(config, instance=instance)
        )
    except AttributeError:
        config.logger.error(f"There was a problem loading {process} wrapper.")
        return None
    except ModuleNotFoundError:
        config.logger.error(f"Could not load {process} wrapper. "
                            "Wrapper may have been disabled.")
        return None

    return metplus_wrapper


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
        wrapper = _get_wrapper_instance(config, process, instance)
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
        return

    error_msg = (f'{app_name} has finished running{user_string} '
                 f'but had {total_errors} error')
    if total_errors > 1:
        error_msg += 's'
    error_msg += '.'
    logger.error(error_msg)
    logger.info(log_message)
    sys.exit(1)
