import re
from datetime import datetime, timedelta

from .string_manip import getlist, getlistint, split_dir_and_template
from .system_util import traverse_dir
from .time_util import get_relativedelta
from .time_util import ti_get_hours_from_relativedelta
from .time_util import ti_get_seconds_from_relativedelta
from .time_util import ti_get_lead_string
from .string_template_substitution import do_string_sub, get_time_from_file


def time_generator(config):
    """!Generator used to read METplusConfig variables for time looping

    @param config METplusConfig object to read
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

    # use TIME_GENERATOR_INPUT_DIR/TEMPLATE to find times if set
    if _is_time_generator_dir_or_template_set(config):
        config.logger.debug(f"Using TIME_GENERATOR_INPUT_DIR/TEMPLATE to find {prefix} times")
        # Get unique datetime values that appear in ALL directory / template combinations.
        unique_dts = _get_intersected_unique_times(config, time_type=prefix, sort_by=prefix)
        config.logger.debug(f"Found {len(unique_dts)} {prefix.lower()} times that match all search criteria")
        for file_dt in unique_dts:
            file_time_info = _create_time_input_dict(prefix, file_dt, clock_dt)
            yield file_time_info

        return

    time_format = config.getraw('config', f'{prefix}_TIME_FMT', '')
    if not time_format:
        config.logger.error(f'Must set {prefix}_TIME_FMT if LOOP_BY={prefix}')
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

    time_interval = _get_time_interval(config, prefix)

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

def _is_time_generator_dir_or_template_set(config):
    """!Check if any of the time generator input configs are set."""
    return (config.has_option('config', 'TIME_GENERATOR_INPUT_DIR') or
            config.has_option('config', 'TIME_GENERATOR_INPUT_TEMPLATE'))

def _get_dir_template_pairs(config):
    """!Get directory/template pairs from config variables.

    @returns List of (input_dir, input_template) tuples, or empty list on error
    """
    input_dirs = getlist(config.getdir('TIME_GENERATOR_INPUT_DIR'))
    input_templates = getlist(config.getraw('config', 'TIME_GENERATOR_INPUT_TEMPLATE'))

    # read input dirs and templates, substituting custom/instance/now/today
    clock_dt = datetime.strptime(
        config.getstr('config', 'CLOCK_TIME'),
        '%Y%m%d%H%M%S'
    )
    replace_args = {
        'custom': config.getraw('config', 'CURRENT_CUSTOM', ''),
        'instance': config.getraw('config', 'CURRENT_INSTANCE', ''),
        'now': clock_dt,
        'today': clock_dt.strftime('%Y%m%d'),
    }
    input_dirs = [do_string_sub(item, **replace_args, skip_missing_tags=True)
                  for item in input_dirs]
    input_templates = [do_string_sub(item, **replace_args, skip_missing_tags=True)
                       for item in input_templates]

    # Handle pairing logic
    if len(input_dirs) < 2:
        # Use the single directory for each template, applying smart splitting
        dir_template_pairs = []
        # handle if input directory was not provided and entire path is in template
        input_dir = '' if not input_dirs else input_dirs[0]
        for template in input_templates:
            clean_dir, clean_template = split_dir_and_template(input_dir, template)
            if clean_template:  # Only add pairs that have a valid template
                dir_template_pairs.append((clean_dir, clean_template))
        return dir_template_pairs

    else:
        # Lists must be the same length for pairing
        if len(input_dirs) != len(input_templates):
            config.logger.error(f"TIME_GENERATOR_INPUT_DIR list length ({len(input_dirs)}) "
                                f"must match TIME_GENERATOR_INPUT_TEMPLATE list length ({len(input_templates)}) "
                                f"or TIME_GENERATOR_INPUT_DIR must contain exactly one item")
            return []

        # Pair up directories and templates using zip, applying smart splitting
        dir_template_pairs = []
        for input_dir, input_template in zip(input_dirs, input_templates):
            clean_dir, clean_template = split_dir_and_template(input_dir, input_template)
            if clean_template:  # Only add pairs that have a valid template
                dir_template_pairs.append((clean_dir, clean_template))

        return dir_template_pairs


def _template_is_forecast(input_dir, input_template):
    """!Determine if a template contains forecast lead time information.
    This is done by checking if the template contains a lead tag or both
    init and valid tags.

    @param input_dir Input directory path
    @param input_template Input template path
    @returns True if template is a forecast, False otherwise
    """
    # Use existing logic to properly combine dir and template
    _, combined_template = split_dir_and_template(input_dir, input_template)

    return ('{lead' in combined_template or
            '{init' in combined_template and '{valid' in combined_template)


def _get_intersected_unique_times(config, time_type, sort_by=None, input_dict=None):
    """!Get unique times that appear in ALL directory/template combinations.
    Enhanced to handle mixed template types (forecast vs analysis).

    @param config METplusConfig object
    @param time_type Type of time to extract ('init', 'valid', 'lead')
    @param sort_by Optional sort parameter for get_files_and_time_info
    @param input_dict Optional filtering dictionary for filtering leads by template

    @returns Sorted list of unique times that appear in all combinations
    """
    dir_template_pairs = _get_dir_template_pairs(config)
    if not dir_template_pairs:
        return []

    # Separate templates into forecast (has lead times) and analysis (valid only)
    forecast_templates = []
    analysis_templates = []

    for input_dir, input_template in dir_template_pairs:
        # Check if this template has lead time information
        is_forecast = _template_is_forecast(input_dir, input_template)

        config.logger.debug(f"Searching for files in {input_dir} using template {input_template}")
        files_and_time_info = get_files_and_time_info(input_dir, input_template,
                                                      sort_by=sort_by,
                                                      logger=config.logger)
        config.logger.debug(f"Found {len(files_and_time_info)} file{'s' if len(files_and_time_info) >1 else ''}")

        # If input_dict is provided, apply filtering
        # only filter analysis files if input_dict contains valid time
        # to avoid filtering out init times incorrectly when init == valid
        if input_dict is not None and (is_forecast or 'valid' in input_dict):
            files_and_time_info = _filter_files_by_input_dict(files_and_time_info,
                                                              input_dict, config)
            if files_and_time_info is None:
                return []

        if is_forecast:
            forecast_templates.append((input_dir, input_template, files_and_time_info))
        else:
            analysis_templates.append((input_dir, input_template, files_and_time_info))

    return _get_enhanced_times(time_type, forecast_templates, analysis_templates)


def _get_enhanced_times(time_type, forecast_templates, analysis_templates):
    """!Call the appropriate _get_enhanced_*_times function depending on the time type.

    @param time_type Type of time to extract ('init', 'valid', 'lead')
    @param forecast_templates List of (dir, template, files_and_time_info) for forecast data
    @param analysis_templates List of (dir, template, files_and_time_info) for analysis data
    @returns Sorted list of unique times or empty list if invalid time_type provided
    """
    # Handle the case based on what time_type is requested
    if time_type.lower() == 'lead':
        return _get_enhanced_lead_times(forecast_templates, analysis_templates)
    elif time_type.lower() == 'valid':
        return _get_enhanced_valid_times(forecast_templates, analysis_templates)
    elif time_type.lower() == 'init':
        return _get_enhanced_init_times(forecast_templates, analysis_templates)

    return []

def _get_enhanced_lead_times(forecast_templates, analysis_templates):
    """!Get forecast lead times, considering analysis templates for valid time constraints.

    @param forecast_templates List of (dir, template, files_and_time_info) for forecast data
    @param analysis_templates List of (dir, template, files_and_time_info) for analysis data
    @returns Sorted list of unique lead times
    """
    if not forecast_templates:
        # No forecast templates, use 0 forecast lead
        return [0]

    skip_analysis_filter = bool(not analysis_templates)

    # Get all valid times from analysis templates (if any)
    analysis_valid_times = set()
    for _, _, files_and_time_info in analysis_templates:
        valid_times = get_unique_times(files_and_time_info, time_type='valid')
        analysis_valid_times.update(valid_times)

    # Get lead times from forecast templates
    all_lead_sets = []
    for _, _, files_and_time_info in forecast_templates:
        if analysis_valid_times:
            # Filter forecast files to only include those with valid times matching analysis
            filtered_files = []
            for filepath, time_info in files_and_time_info:
                if time_info.get('valid') in analysis_valid_times:
                    filtered_files.append((filepath, time_info))
            unique_leads = get_unique_times(filtered_files, time_type='lead')
        elif skip_analysis_filter:
            # use all times if no analysis templates were specified
            unique_leads = get_unique_times(files_and_time_info, time_type='lead')
        else:
            # No analysis times match, so filter out all times
            continue

        all_lead_sets.append(set(unique_leads))

    # Take intersection of lead times across forecast templates
    if not all_lead_sets:
        return []

    return _get_intersection_times(all_lead_sets)


def _get_enhanced_valid_times(forecast_templates, analysis_templates):
    """!Get valid times from both forecast and analysis templates.

    @param forecast_templates List of (dir, template, files_and_time_info) for forecast data
    @param analysis_templates List of (dir, template, files_and_time_info) for analysis data
    @returns Sorted list of unique valid times that appear in all template types
    """
    all_valid_sets = []

    # Get valid times from forecast templates
    for _, _, files_and_time_info in forecast_templates:
        valid_times = get_unique_times(files_and_time_info, time_type='valid')
        all_valid_sets.append(set(valid_times))

    # Get valid times from analysis templates
    for _, _, files_and_time_info in analysis_templates:
        valid_times = get_unique_times(files_and_time_info, time_type='valid')
        all_valid_sets.append(set(valid_times))

    if not all_valid_sets:
        return []

    # Take intersection of all valid time sets
    return _get_intersection_times(all_valid_sets)


def _get_enhanced_init_times(forecast_templates, analysis_templates):
    """!Get init times, primarily from forecast templates.

    @param forecast_templates List of (dir, template, files_and_time_info) for forecast data
    @param analysis_templates List of (dir, template, files_and_time_info) for analysis data
    @returns Sorted list of unique init times
    """
    all_init_sets = []

    # Get init times from forecast templates (these are meaningful)
    for _, _, files_and_time_info in forecast_templates:
        init_times = get_unique_times(files_and_time_info, time_type='init')
        all_init_sets.append(set(init_times))

    # For analysis templates, init == valid, but we may not want to include these
    # in the intersection since they would filter out all init times except init == valid
    # Only include if there are no forecast templates
    if not forecast_templates:
        for _, _, files_and_time_info in analysis_templates:
            init_times = get_unique_times(files_and_time_info, time_type='init')
            all_init_sets.append(set(init_times))

    if not all_init_sets:
        return []

    # Take intersection
    return _get_intersection_times(all_init_sets)


def _get_intersection_times(all_sets):
    intersected_times = all_sets[0]
    for lead_set in all_sets[1:]:
        intersected_times = intersected_times.intersection(lead_set)

    return sorted(list(intersected_times))


def _filter_files_by_input_dict(files_and_time_info, input_dict, config):
    """!Filter files_and_time_info based on input_dict constraints.

    @param files_and_time_info List of (filepath, time_info_dict) tuples
    @param input_dict Dictionary with 'init' and/or 'valid' keys
    @param config METplusConfig object for logging

    @returns Filtered list of (filepath, time_info_dict) tuples, or None on error
    """
    # Validate that input_dict contains either 'init' or 'valid' but not both
    # (or if both are present, one should be '*')
    has_init = 'init' in input_dict and input_dict['init'] != '*'
    has_valid = 'valid' in input_dict and input_dict['valid'] != '*'

    if has_init and has_valid and input_dict['init'] != input_dict['valid']:
        config.logger.error("input_dict contains both 'init' and 'valid' keys "
                            "without one being set to '*'. This is not supported.")
        return None

    if has_init or has_valid:
        # Determine which time type to filter by
        filter_time_type = 'init' if has_init else 'valid'
        filter_time_value = input_dict[filter_time_type]

        # Filter files to only include those matching the specified time
        filtered_files_and_time_info = []
        for filepath, file_time_info in files_and_time_info:
            if file_time_info.get(filter_time_type) == filter_time_value:
                filtered_files_and_time_info.append((filepath, file_time_info))

        config.logger.debug(f"Filtered input files to {len(filtered_files_and_time_info)} "
                            f"file{'s' if len(filtered_files_and_time_info) > 1 else ''} "
                            f"matching {filter_time_type}={filter_time_value}")
        return filtered_files_and_time_info

    return files_and_time_info


def _get_time_interval(config, prefix):
    time_interval = config.getstr('config', f'{prefix}_INCREMENT', '60')
    # if [INIT/VALID]_INCREMENT is an empty string, set it to prevent crash
    if not time_interval:
        time_interval = '60'
    return get_relativedelta(time_interval)


def get_files_and_time_info(data_dir, template, sort_by=None, logger=None):
    files_and_time_info = []
    for fullpath in traverse_dir(data_dir):
        # remove input data directory to get relative path
        rel_path = fullpath.replace(f"{data_dir}/", "")
        # extract time information from relative path using template
        file_time_info = get_time_from_file(rel_path, template, logger)
        if file_time_info is None:
            continue

        files_and_time_info.append((fullpath, file_time_info))

    if sort_by:
        # Sort by the sort_by, e.g. init or valid, datetime in the time info dictionary
        files_and_time_info.sort(key=lambda x: x[1].get(sort_by.lower(), datetime.min))

    return files_and_time_info


def get_unique_times(files_and_time_info, time_type):
    """!Extract unique time info dictionaries from files and time info list.

    @param files_and_time_info: List of tuples (filepath, time_info_dict)
    @param time_type: String of the type of time to extract, e.g. "init" or "valid"
    @returns: List of unique datetimes
    """
    seen = set()
    unique_times = []

    for filepath, time_info in files_and_time_info:
        time_value = time_info.get(time_type.lower())
        if not time_value: continue

        if time_value not in seen:
            seen.add(time_value)
            unique_times.append(time_value)

    return unique_times


def get_start_and_end_times(config):
    times = list(time_generator(config))
    if not times or times[0] is None:
        return None, None

    start_dt = times[0][times[0]['loop_by']]
    end_dt = times[-1][times[-1]['loop_by']]
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
    """!Read the METplusConfig object and determine the prefix for the time
    looping variables.

    @param config METplusConfig object to read
    @returns string 'INIT' if looping by init time, 'VALID' if looping by
     valid time, or None if not enough information was found in the config
    """
    loop_by = config.getstr('config', 'LOOP_BY', '').upper()

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
    """!Use time format to get datetime object from time string, substituting
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


def get_skip_times(config, skip_or_inc, init_or_valid, wrapper):
    """!Read skip or include times config variable and populate dictionary
     of times that should be skipped. Config values should be in the format:
     "%m:begin_end_incr(3,11,1)", "%d:30,31", "%Y%m%d:20201031"
     where each item inside quotes is a datetime format, colon, then a list
     of times in that format to skip or include.

     @param config configuration object to read values
     @param skip_or_inc string with either 'SKIP' or 'INCLUDE'
     @param init_or_valid string with either 'INIT' or 'VALID'
     @param wrapper name of wrapper if supporting
       skipping times only for certain wrappers, i.e. grid_stat
     @returns dictionary containing times to skip
    """
    times_dict = {}

    # get possible config variable names. If reading VALID, also check
    # deprecated generic variable that doesn't include VALID
    config_names = []
    if wrapper:
        config_names.append(
            f'{wrapper.upper()}_{skip_or_inc}_{init_or_valid}_TIMES'
        )

        # handle old naming that doesn't specify VALID
        if init_or_valid == 'VALID':
            config_names.append(f'{wrapper.upper()}_{skip_or_inc}_TIMES')

    config_names.append(f'{skip_or_inc}_{init_or_valid}_TIMES')

    # handle old naming that doesn't specify VALID
    if init_or_valid == 'VALID':
        config_names.append(f'{skip_or_inc}_TIMES')

    # find first config variable name that is set
    config_name = config.get_mp_config_name(config_names)

    # return empty dictionary if none of the config variables are set
    if not config_name:
        return {}

    # warn if deprecated name without _VALID is used
    if init_or_valid == 'VALID' and 'VALID' not in config_name:
        config.logger.warning(
            f"{config_name} is deprecated. "
            f"Please use {config_name.replace('_TIMES', '_VALID_TIMES')}"
        )

    times_string = config.getstr('config', config_name, '')
    if not times_string:
        return {}

    # get list of skip items, but don't expand begin_end_incr yet
    item_list = getlist(times_string, expand_begin_end_incr=False)
    for item in item_list:
        try:
            time_format, times = item.split(':')

            # get list of times for the time format, expand begin_end_incr
            times_list = getlist(times)

            # if time format is already in times dictionary, extend list
            if time_format in times_dict:
                times_dict[time_format].extend(times_list)
            else:
                times_dict[time_format] = times_list

        except ValueError:
            config.logger.error(f"{skip_or_inc}_{init_or_valid}_TIMES item "
                                f"does not match format: {item}")
            return None

    return times_dict


def skip_time(time_info, c_dict):
    """!Used to check the valid and init time of the current run time against
     a list of times to skip.

    @param time_info dictionary with time information to check
    @param c_dict dictionary to read [SKIP/INC]_[VALID/INIT]_TIMES which
    contain a dictionary of times to skip: {'%d': [31]} means skip 31st day
    @returns True if run time should be skipped, False if not
    """
    for init_valid in ('init', 'valid'):
        skip_list = c_dict.get(f'SKIP_{init_valid.upper()}_TIMES')
        inc_list = c_dict.get(f'INC_{init_valid.upper()}_TIMES')

        # if no skip or include times were set, continue to not skip
        if not skip_list and not inc_list:
            continue

        # if any include times are listed, skip if the time doesn't match
        if inc_list and not _found_time_match(time_info, inc_list, init_valid):
            return True

        # skip if the time matches a skip time
        if skip_list and _found_time_match(time_info, skip_list, init_valid):
            return True

    # if time never matches, return False, meaning run for the given time
    return False


def _found_time_match(time_info, time_dict, init_or_valid):
    run_time_dt = time_info.get(init_or_valid)
    if not run_time_dt or run_time_dt == '*':
        return False

    for time_format, time_list in time_dict.items():
        # extract time information from valid time based on skip time format
        run_time_value = run_time_dt.strftime(time_format)

        # loop over times to skip for this format and check if it matches
        for time_item in time_list:
            try:
                if int(run_time_value) == int(time_item):
                    return True
            except ValueError:
                if str(run_time_value) == str(time_item):
                    return True

    return False


def get_lead_sequence(config, input_dict=None, wildcard_if_empty=False):
    """!Get forecast lead list from LEAD_SEQ or compute it from INIT_SEQ.
        Restrict list by LEAD_SEQ_[MIN/MAX] if set. Now returns list of relativedelta objects

        @param config METplusConfig object to query config variable values
        @param input_dict time dictionary needed to handle using INIT_SEQ. Must contain
          valid key if processing INIT_SEQ
        @param wildcard_if_empty if no lead sequence was set, return a
         list with '*' if this is True, otherwise return a list with 0
        @returns list of relativedelta objects or a list containing 0 if none are found
    """

    out_leads = []

    # use TIME_GENERATOR_INPUT_DIR/TEMPLATE to find forecast leads if set
    if _is_time_generator_dir_or_template_set(config):
        config.logger.debug("Using TIME_GENERATOR_INPUT_DIR/TEMPLATE to find lead times")
        unique_leads = _get_intersected_unique_times(config, time_type='lead', sort_by='lead',
                                                     input_dict=input_dict)
        lead_seq = _handle_lead_seq(config, unique_leads, default_unit='S')
        if lead_seq:
            leads_fmt = [ti_get_lead_string(lead, plural=False) for lead in lead_seq]
            config.logger.debug(f"Found {len(lead_seq)} lead times that match "
                                f"all search criteria: {', '.join(leads_fmt)}")
        else:
            config.logger.debug("No lead times found that match all search criteria")
        return lead_seq

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

        # init sequence should return an empty list if no matches were found
        if init_seq:
            return []

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

    if not init_seq:
        return True

    # if input dictionary not passed in,
    # cannot compute lead sequence from it, so exit
    if input_dict is None:
        config.logger.error('Cannot run using INIT_SEQ for this wrapper')
        return False

    # if looping by init, fail and exit
    if 'valid' not in input_dict.keys() or input_dict['valid'] == '*':
        config.logger.error('INIT_SEQ specified while looping by init time.'
                            ' Use LEAD_SEQ or change to loop by valid time')
        return False

    # maximum lead must be specified to run with INIT_SEQ
    if no_max:
        config.logger.error('LEAD_SEQ_MAX must be set to use INIT_SEQ')
        return False

    return True


def _get_lead_min_max(config):
    # remove any items that are outside the range specified
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


def _handle_lead_seq(config, lead_strings, lead_min=None, lead_max=None, default_unit='H'):
    out_leads = []
    leads = []
    for lead in lead_strings:
        relative_delta = get_relativedelta(lead, default_unit)
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
        if lead_min_approx <= lead_approx <= lead_max_approx:
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

    out_leads = sorted(out_leads, key=lambda rd: ti_get_seconds_from_relativedelta(rd, input_dict['valid']))
    return out_leads


def _handle_lead_groups(lead_groups):
    """! Read groups of forecast leads and create a list with all unique items

         @param lead_groups dictionary where the values are lists of forecast
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
    lead_seq_dict = _get_lead_groups_from_indices(config)
    if lead_seq_dict is not None:
        return lead_seq_dict

    # if no indices were found, check if divisions are requested
    return _get_lead_groups_from_divisions(config)


def _get_lead_groups_from_indices(config):
    all_conf = config.keys('config')
    indices = []
    regex = re.compile(r"LEAD_SEQ_(\d+)$")
    for conf in all_conf:
        result = regex.match(conf)
        if result is not None:
            indices.append(result.group(1))

    if not indices:
        return None

    lead_seq_dict = {}
    # loop over all possible variables and add them to list
    for index in indices:
        label = _get_label_from_index(config, index)
        # get forecast list for n
        lead_string_list = getlist(config.getstr('config', f'LEAD_SEQ_{index}'))
        lead_seq = _handle_lead_seq(config, lead_string_list,
                                    lead_min=None, lead_max=None)
        # add to output dictionary
        lead_seq_dict[label] = lead_seq

    return lead_seq_dict


def _get_lead_groups_from_divisions(config):
    if not config.has_option('config', 'LEAD_SEQ_GROUP_SIZE'):
        return {}

    lead_list = getlist(config.getstr('config', 'LEAD_SEQ', ''))
    divisions = config.getstr('config', 'LEAD_SEQ_GROUP_SIZE')
    divisions = get_relativedelta(divisions, default_unit='H')
    lead_min = get_relativedelta('0')
    lead_max = divisions - get_relativedelta('1S')
    index = 1
    now = datetime.now()
    # maximum 1000 divisions can be created to prevent infinite loop
    num_leads = 0
    lead_groups = {}
    while now + lead_max < now + (divisions * 1000):
        lead_seq = _handle_lead_seq(config, lead_list,
                                    lead_min=lead_min, lead_max=lead_max)
        if lead_seq:
            label = _get_label_from_index(config, index)
            lead_groups[label] = lead_seq
            num_leads += len(lead_seq)

        # if all forecast leads have been handled, break out of while loop
        if num_leads >= len(lead_list):
            break

        index += 1
        lead_min += divisions
        lead_max += divisions

    if num_leads < len(lead_list):
        config.logger.warning('Could not split LEAD_SEQ using LEAD_SEQ_GROUP_SIZE')
        return None

    return lead_groups


def _get_label_from_index(config, index):
    if config.has_option('config', f"LEAD_SEQ_{index}_LABEL"):
        return config.getstr('config', f"LEAD_SEQ_{index}_LABEL")
    if config.has_option('config', "LEAD_SEQ_GROUP_LABEL"):
        return f"{config.getstr('config', 'LEAD_SEQ_GROUP_LABEL')}{index}"
    return f"Group{index}"
