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
