import sys
import os
import shutil
from datetime import datetime
from importlib import import_module

from .constants import NO_COMMAND_WRAPPERS
from .string_manip import get_logfile_info
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
    logger.info('Running METplus v%s%swith command: %s',
                version_number, user_string, ' '.join(sys.argv))

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
    total_errors = 0

    # Use config object to get the list of processes to call
    process_list = get_process_list(config)

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

        all_commands = []
        for process in processes:
            new_commands = process.run_all_times()
            if new_commands:
                all_commands.extend(new_commands)

        # if process list contains any wrapper that should run commands
        if any([item[0] not in NO_COMMAND_WRAPPERS for item in process_list]):
            # write out all commands and environment variables to file
            if not write_all_commands(all_commands, config):
                # report an error if no commands were generated
                total_errors += 1

        # compute total number of errors that occurred and output results
        for process in processes:
            if not process.errors:
                continue
            process_name = process.__class__.__name__.replace('Wrapper', '')
            error_msg = f'{process_name} had {process.errors} error'
            if process.errors > 1:
                error_msg += 's'
            error_msg += '.'
            logger.error(error_msg)
            total_errors += process.errors

        return total_errors
    except:
        logger.exception("Fatal error occurred")
        logger.info("Check the log file for more information: "
                    f"{get_logfile_info(config)}")
        return 1


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
