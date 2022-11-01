import re
from datetime import datetime, timedelta

from .string_manip import getlist, getlistint
from .time_util import get_relativedelta, add_to_time_input
from .time_util import ti_get_hours_from_relativedelta
from .time_util import ti_get_seconds_from_relativedelta
from .string_template_substitution import do_string_sub
from .config_metplus import log_runtime_banner

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
    lead_min, lead_max, no_max = _get_lead_min_max(config)

    # check if LEAD_SEQ, INIT_SEQ, or LEAD_SEQ_<n> are set
    # if more than one is set, report an error and exit
    lead_seq = getlist(config.getstr('config', 'LEAD_SEQ', ''))
    init_seq = getlistint(config.getstr('config', 'INIT_SEQ', ''))
    lead_groups = get_lead_sequence_groups(config)

    if not _are_lead_configs_ok(lead_seq,
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

        out_leads = _handle_lead_seq(config,
                                    lead_seq,
                                    lead_min,
                                    lead_max)

    # use INIT_SEQ to build lead list based on the valid time
    elif init_seq:
        out_leads = _handle_init_seq(init_seq,
                                    input_dict,
                                    lead_min,
                                    lead_max)
    elif lead_groups:
        out_leads = _handle_lead_groups(lead_groups)

    if not out_leads:
        if wildcard_if_empty:
            return ['*']

        return [0]

    return out_leads

def _are_lead_configs_ok(lead_seq, init_seq, lead_groups,
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

def _get_lead_min_max(config):
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
    lead_min = get_relativedelta(lead_min_str, 'H')
    lead_max = get_relativedelta(lead_max_str, 'H')
    return lead_min, lead_max, no_max

def _handle_lead_seq(config, lead_strings, lead_min=None, lead_max=None):
    out_leads = []
    leads = []
    for lead in lead_strings:
        relative_delta = get_relativedelta(lead, 'H')
        if relative_delta is not None:
            leads.append(relative_delta)
        else:
            config.logger.error(f'Invalid item {lead} in LEAD_SEQ. Exiting.')
            return None

    if lead_min is None and lead_max is None:
        return leads

    # add current time to leads to approximate month and year length
    now_time = datetime.now()
    lead_min_approx = now_time + lead_min
    lead_max_approx = now_time + lead_max
    for lead in leads:
        lead_approx = now_time + lead
        if lead_approx >= lead_min_approx and lead_approx <= lead_max_approx:
            out_leads.append(lead)

    return out_leads

def _handle_init_seq(init_seq, input_dict, lead_min, lead_max):
    out_leads = []
    lead_min_hours = ti_get_hours_from_relativedelta(lead_min)
    lead_max_hours = ti_get_hours_from_relativedelta(lead_max)

    valid_hr = int(input_dict['valid'].strftime('%H'))
    for init in init_seq:
        if valid_hr >= init:
            current_lead = valid_hr - init
        else:
            current_lead = valid_hr + (24 - init)

        while current_lead <= lead_max_hours:
            if current_lead >= lead_min_hours:
                out_leads.append(get_relativedelta(current_lead, default_unit='H'))
            current_lead += 24

    out_leads = sorted(out_leads, key=lambda
        rd: ti_get_seconds_from_relativedelta(rd, input_dict['valid']))
    return out_leads

def _handle_lead_groups(lead_groups):
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
        lead_seq = _handle_lead_seq(config,
                                    lead_string_list,
                                    lead_min=None,
                                    lead_max=None)
        # add to output dictionary
        lead_seq_dict[label] = lead_seq

    return lead_seq_dict
