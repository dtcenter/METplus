from datetime import datetime, timedelta

from .string_manip import getlist
from .time_util import get_relativedelta
from .string_template_substitution import do_string_sub

def time_generator(config):
    """! Generator used to read METplusConfig variables for time looping

    @param METplusConfig object to read
    @returns None if not enough information is available on config.
     Yields the next run time dictionary or None if something went wrong
    """
    # determine INIT or VALID prefix
    prefix = get_time_prefix(config)
    if not prefix:
        yield None
        return

    # get clock time of when the run started
    clock_dt = datetime.strptime(
        config.getstr('config', 'CLOCK_TIME'),
        '%Y%m%d%H%M%S'
    )

    time_format = config.getraw('config', f'{prefix}_TIME_FMT', '')
    if not time_format:
        config.logger.error(f'Could not read {prefix}_TIME_FMT')
        yield None
        return

    # check for [INIT/VALID]_LIST and use that list if set
    if config.has_option('config', f'{prefix}_LIST'):
        time_list = getlist(config.getraw('config', f'{prefix}_LIST'))
        if not time_list:
            config.logger.error(f"Could not read {prefix}_LIST")
            yield None
            return

        for time_string in time_list:
            current_dt = _get_current_dt(time_string,
                                         time_format,
                                         clock_dt,
                                         config.logger)
            if not current_dt:
                yield None

            time_info = _create_time_input_dict(prefix, current_dt, clock_dt)
            yield time_info

        return

    # if list is not provided, use _BEG, _END, and _INCREMENT
    start_string = config.getraw('config', f'{prefix}_BEG')
    end_string = config.getraw('config', f'{prefix}_END', start_string)
    time_interval = get_relativedelta(
        config.getstr('config', f'{prefix}_INCREMENT', '60')
    )

    start_dt = _get_current_dt(start_string,
                               time_format,
                               clock_dt,
                               config.logger)

    end_dt = _get_current_dt(end_string,
                             time_format,
                             clock_dt,
                             config.logger)

    if not _validate_time_values(start_dt,
                                 end_dt,
                                 time_interval,
                                 prefix,
                                 config.logger):
        yield None
        return

    current_dt = start_dt
    while current_dt <= end_dt:
        time_info = _create_time_input_dict(prefix, current_dt, clock_dt)
        yield time_info

        current_dt += time_interval

def get_start_and_end_times(config):
    prefix = get_time_prefix(config)
    if not prefix:
        return None, None

    # get clock time of when the run started
    clock_dt = datetime.strptime(
        config.getstr('config', 'CLOCK_TIME'),
        '%Y%m%d%H%M%S'
    )

    time_format = config.getraw('config', f'{prefix}_TIME_FMT', '')
    if not time_format:
        config.logger.error(f'Could not read {prefix}_TIME_FMT')
        return None, None

    start_string = config.getraw('config', f'{prefix}_BEG')
    end_string = config.getraw('config', f'{prefix}_END', start_string)

    start_dt = _get_current_dt(start_string,
                               time_format,
                               clock_dt,
                               config.logger)

    end_dt = _get_current_dt(end_string,
                             time_format,
                             clock_dt,
                             config.logger)

    if not _validate_time_values(start_dt,
                                 end_dt,
                                 get_relativedelta('60'),
                                 prefix,
                                 config.logger):
        return None, None

    return start_dt, end_dt

def _validate_time_values(start_dt, end_dt, time_interval, prefix, logger):
    if not start_dt:
        logger.error(f"Could not read {prefix}_BEG")
        return False

    if not end_dt:
        logger.error(f"Could not read {prefix}_END")
        return False

    # check that time increment is at least 60 seconds
    if (start_dt + time_interval <
            start_dt + timedelta(seconds=60)):
        logger.error(f'{prefix}_INCREMENT must be greater than or '
                     'equal to 60 seconds')
        return False

    if start_dt > end_dt:
        logger.error(f"{prefix}_BEG must come after {prefix}_END ")
        return False

    return True

def _create_time_input_dict(prefix, current_dt, clock_dt):
    return {
        'loop_by': prefix.lower(),
        prefix.lower(): current_dt,
        'now': clock_dt,
        'today': clock_dt.strftime('%Y%m%d'),
    }

def get_time_prefix(config):
    """! Read the METplusConfig object and determine the prefix for the time
    looping variables.

    @param config METplusConfig object to read
    @returns string 'INIT' if looping by init time, 'VALID' if looping by
     valid time, or None if not enough information was found in the config
    """
    loop_by = config.getstr('config', 'LOOP_BY', '').upper()
    if not loop_by:
        return None

    if loop_by in ['INIT', 'RETRO']:
        return 'INIT'

    if loop_by in ['VALID', 'REALTIME']:
        return 'VALID'

    # check for legacy variable LOOP_BY_INIT if LOOP_BY is not set properly
    if config.has_option('config', 'LOOP_BY_INIT'):
        if config.getbool('config', 'LOOP_BY_INIT'):
            return 'INIT'

        return 'VALID'

    # report an error if time prefix could not be determined
    config.logger.error('MUST SET LOOP_BY to VALID, INIT, RETRO, or REALTIME')
    return None

def _get_current_dt(time_string, time_format, clock_dt, logger):
    """! Use time format to get datetime object from time string, substituting
     values for today or now template tags if specified.

    @param time_string string value read from the config that
     may include now or today tags
    @param time_format format of time_string, i.e. %Y%m%d
    @param clock_dt datetime object for time when execution started
    @returns datetime object if successful, None if not
    """
    subbed_time_string = do_string_sub(
        time_string,
        now=clock_dt,
        today=clock_dt.strftime('%Y%m%d')
    )
    try:
        current_dt = datetime.strptime(subbed_time_string, time_format)
    except ValueError:
        logger.error(
            f'Could not format time string ({time_string}) using '
            f'time format ({time_format})'
        )
        return None

    return current_dt
