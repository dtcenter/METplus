import os

from .constants import DEPRECATED_DICT, DEPRECATED_MET_LIST
from .constants import UPGRADE_INSTRUCTIONS_URL
from .string_manip import find_indices_in_config_section, getlist
from .string_manip import is_python_script
from .string_template_substitution import do_string_sub
from .config_util import get_process_list, get_custom_string_list


def validate_config_variables(config):

    all_sed_cmds = []
    # check for deprecated config items and warn user to remove/replace them
    deprecated_is_ok, sed_cmds = check_for_deprecated_config(config)
    all_sed_cmds.extend(sed_cmds)

    # check for deprecated env vars in MET config files and
    # warn user to remove/replace them
    deprecated_met_is_ok, sed_cmds = check_for_deprecated_met_config(config)
    all_sed_cmds.extend(sed_cmds)

    # validate configuration variables
    field_is_ok, sed_cmds = validate_field_info_configs(config)
    all_sed_cmds.extend(sed_cmds)

    # check that OUTPUT_BASE is not set to the exact same value as INPUT_BASE
    inoutbase_is_ok = True
    input_real_path = os.path.realpath(config.getdir_nocheck('INPUT_BASE', ''))
    output_real_path = os.path.realpath(config.getdir('OUTPUT_BASE'))
    if input_real_path == output_real_path:
      config.logger.error("INPUT_BASE AND OUTPUT_BASE are set to the "
                          f"exact same path: {input_real_path}")
      config.logger.error("Please change one of these paths to avoid risk "
                          "of losing input data")
      inoutbase_is_ok = False

    check_user_environment(config)

    is_ok = (deprecated_is_ok and field_is_ok and
             inoutbase_is_ok and deprecated_met_is_ok)

    return is_ok, all_sed_cmds


def check_for_deprecated_config(config):
    """!Checks user configuration files and reports errors or warnings if any
     deprecated variable are found. If an alternate variable name can be
     suggested, add it to the 'alt' section. If the alternate cannot be
     literally substituted for the old name, set copy to False

     @param config METplusConfig object to evaluate
     @returns A tuple containing a boolean if the configuration is suitable to
      run or not and if it is not correct, the 2nd item is a list of sed
       commands that can be run to help fix the incorrect config variables
    """
    logger = config.logger

    # create list of errors and warnings to report for deprecated configs
    e_list = []
    all_sed_cmds = []

    # keep track of upgrade instructions to output after all vars are checked
    upgrade_notes = set()

    for old, depr_info in DEPRECATED_DICT.items():
        if not isinstance(depr_info, dict):
            continue

        # check if <n> is found in old item, use regex to find vars if found
        if '<n>' not in old:
            handle_deprecated(old, depr_info.get('alt', ''),
                              depr_info, config, all_sed_cmds,
                              e_list, upgrade_notes)
            continue

        old_regex = old.replace('<n>', r'(\d+)')
        indices = find_indices_in_config_section(old_regex,
                                                 config,
                                                 index_index=1).keys()
        for index in indices:
            old_with_index = old.replace('<n>', index)
            alt_with_index = depr_info.get('alt', '').replace('<n>', index)

            handle_deprecated(old_with_index, alt_with_index,
                              depr_info, config, all_sed_cmds,
                              e_list, upgrade_notes)

    if 'ensemble' in upgrade_notes:
        short_msg = ('Please navigate to the upgrade instructions: '
                     f'{UPGRADE_INSTRUCTIONS_URL}')
        msg = ('EnsembleStat functionality has been moved to GenEnsProd. '
               'The required changes to the config files depend on '
               'the type of evaluation that is being performed. '
               f'{short_msg}')

        e_list.insert(0, msg)
        e_list.append(short_msg)

    # if any errors exist, report them and exit
    if not e_list:
        return True, []

    logger.error('DEPRECATED CONFIG ITEMS WERE FOUND. PLEASE FOLLOW THE '
                 'INSTRUCTIONS TO UPDATE THE CONFIG FILES')
    for error_msg in e_list:
        logger.error(error_msg)
    return False, all_sed_cmds


def handle_deprecated(old, alt, depr_info, config, all_sed_cmds, e_list,
                      upgrade_notes):
    # if deprecated config item is found
    if not config.has_option('config', old):
        return

    upgrade_note = depr_info.get('upgrade')
    if upgrade_note:
        upgrade_notes.add(upgrade_note)

    # if it is required to remove, add to error list
    if not alt:
        e_list.append("{} should be removed".format(old))
        return

    e_list.append("{} should be replaced with {}".format(old, alt))

    config_files = config.getstr('config', 'CONFIG_INPUT', '').split(',')
    if 'copy' not in depr_info.keys() or depr_info['copy']:
        for config_file in config_files:
            all_sed_cmds.append(f"sed -i 's|^{old}|{alt}|g' {config_file}")
            all_sed_cmds.append(f"sed -i 's|{{{old}}}|{{{alt}}}|g' {config_file}")

    return


def check_for_deprecated_met_config(config):
    sed_cmds = []
    all_good = True

    # check if *_CONFIG_FILE if set in the METplus config file and check for
    # deprecated environment variables in those files
    met_config_keys = [key for key in config.keys('config')
                       if key.endswith('CONFIG_FILE')]

    for met_config_key in met_config_keys:
        met_tool = met_config_key.replace('_CONFIG_FILE', '')

        # get custom loop list to check if multiple config files are used
        # based on the custom string
        custom_list = get_custom_string_list(config, met_tool)

        for custom_string in custom_list:
            met_config = config.getraw('config', met_config_key)
            if not met_config:
                continue

            met_config_file = do_string_sub(met_config, custom=custom_string)

            if not check_for_deprecated_met_config_file(config,
                                                        met_config_file):
                all_good = False

    return all_good, sed_cmds


def check_for_deprecated_met_config_file(config, met_config):

    all_good = True
    if not os.path.exists(met_config):
        config.logger.error(f"Config file does not exist: {met_config}")
        return False

    # skip check if no deprecated variables are set
    if not DEPRECATED_MET_LIST:
        return all_good

    config.logger.debug("Checking for deprecated environment "
                        f"variables in: {met_config}")

    with open(met_config, 'r') as file_handle:
        lines = file_handle.read().splitlines()

    for line in lines:
        for deprecated_item in DEPRECATED_MET_LIST:
            if '${' + deprecated_item + '}' not in line:
                continue
            all_good = False
            config.logger.error("Please remove deprecated environment variable"
                                f" ${{{deprecated_item}}} found in MET config "
                                f"file: {met_config}")

    return all_good


def validate_field_info_configs(config):
    """!Verify that config variables with _VAR<n>_ in them are valid.

    @param config METplusConfig object to validate
    @returns True if all are valid or False if any items are invalid
    """

    variable_extensions = ['NAME', 'LEVELS', 'THRESH', 'OPTIONS']
    all_good = True, []

    if skip_field_info_validation(config):
        return True, []

    # keep track of all sed commands to replace config variable names
    all_sed_cmds = []

    for ext in variable_extensions:
        # find all _VAR<n>_<ext> keys in the conf files
        data_types_and_indices = find_indices_in_config_section(r"(\w+)_VAR(\d+)_"+ext,
                                                                config,
                                                                index_index=2,
                                                                id_index=1)

        # if BOTH_VAR<n>_ is used, set FCST and OBS to the same value
        # if FCST or OBS is used, the other must be present as well
        # if BOTH and either FCST or OBS are set, report an error
        # get other data type
        for index, data_type_list in data_types_and_indices.items():

            is_valid, err_msgs, sed_cmds = is_var_item_valid(data_type_list, index, ext, config)
            if not is_valid:
                for err_msg in err_msgs:
                    config.logger.error(err_msg)
                all_sed_cmds.extend(sed_cmds)
                all_good = False
                continue

            # make sure FCST and OBS have the same number of levels if coming from separate variables
            if ext != 'LEVELS' or not all(item in ['FCST', 'OBS'] for item in data_type_list):
                continue

            fcst_levels = getlist(config.getraw('config', f"FCST_VAR{index}_LEVELS", ''))

            # add empty string if no levels are found because python embedding items do not need
            # to include a level, but the other item may have a level and the numbers need to match
            if not fcst_levels:
                fcst_levels.append('')

            obs_levels = getlist(config.getraw('config', f"OBS_VAR{index}_LEVELS", ''))
            if not obs_levels:
                obs_levels.append('')

            if len(fcst_levels) != len(obs_levels):
                config.logger.error(f"FCST_VAR{index}_LEVELS and OBS_VAR{index}_LEVELS do not have "
                                    "the same number of elements")
                all_good = False

    return all_good, all_sed_cmds


def skip_field_info_validation(config):
    """!Check config to see if having corresponding FCST/OBS variables is necessary. If process list only
        contains reformatter wrappers, don't validate field info. Also, if MTD is in the process list and
        it is configured to only process either FCST or OBS, validation is unnecessary."""

    reformatters = ['PCPCombine', 'RegridDataPlane']
    process_list = [item[0] for item in get_process_list(config)]

    # if running MTD in single mode, you don't need matching FCST/OBS
    if ('MTD' in process_list and
            config.getbool('config', 'MTD_SINGLE_RUN', False)):
        return True

    # if running any app other than the reformatters, you need matching FCST/OBS, so don't skip
    if [item for item in process_list if item not in reformatters]:
        return False

    return True


def check_user_environment(config):
    """!Check if any environment variables set in [user_env_vars] are already set in
    the user's environment. Warn them that it will be overwritten from the conf if it is"""
    if not config.has_section('user_env_vars'):
        return

    for env_var in config.keys('user_env_vars'):
        if env_var in os.environ:
            msg = '{} is already set in the environment. '.format(env_var) +\
                  'Overwriting from conf file'
            config.logger.warning(msg)


def is_var_item_valid(item_list, index, ext, config):
    """!Given a list of data types (FCST, OBS, ENS, or BOTH) check if the
        combination is valid.
        If BOTH is found, FCST and OBS should not be found.
        If FCST or OBS is found, the other must also be found.
        @param item_list list of data types that were found for a given index
        @param index number following _VAR in the variable name
        @param ext extension to check, i.e. NAME, LEVELS, THRESH, or OPTIONS
        @param config METplusConfig instance
        @returns tuple containing boolean if var item is valid, list of error
         messages and list of sed commands to help the user update their old
         configuration files
    """

    full_ext = f"_VAR{index}_{ext}"
    msg = []
    sed_cmds = []
    if 'BOTH' in item_list and ('FCST' in item_list or 'OBS' in item_list):

        msg.append(f"Cannot set FCST{full_ext} or OBS{full_ext} if BOTH{full_ext} is set.")
    elif ext == 'THRESH':
        # allow thresholds unless BOTH and (FCST or OBS) are set
        pass

    elif 'FCST' in item_list and 'OBS' not in item_list:
        # if FCST level has 1 item and OBS name is a python embedding script,
        # don't report error
        _fcst_or_obs_missing('FCST', config, index, ext, sed_cmds, msg)

    elif 'OBS' in item_list and 'FCST' not in item_list:
        # if OBS level has 1 item and FCST name is a python embedding script,
        # don't report error
        _fcst_or_obs_missing('OBS', config, index, ext, sed_cmds, msg)

    return not bool(msg), msg, sed_cmds


def _fcst_or_obs_missing(found_item, config, index, ext, sed_cmds, msg):
    other_item = 'OBS' if found_item == 'FCST' else 'FCST'
    full_ext = f"_VAR{index}_{ext}"
    # if FCST level has 1 item and OBS name is a python embedding script,
    # don't report error
    level_list = getlist(config.getraw('config',
                                       f'{found_item}_VAR{index}_LEVELS',
                                       ''))
    other_name = config.getraw('config', f'{other_item}_VAR{index}_NAME', '')
    skip_error_for_py_embed = (ext == 'LEVELS' and is_python_script(other_name)
                               and len(level_list) == 1)
    # do not report error for OPTIONS since it isn't required to be same length
    if ext in ['OPTIONS'] or skip_error_for_py_embed:
        return

    msg.append(
        f"If {found_item}{full_ext} is set, you must either set {other_item}{full_ext} or "
        f"change {found_item}{full_ext} to BOTH{full_ext}")

    config_files = config.getstr('config', 'CONFIG_INPUT', '').split(',')
    for config_file in config_files:
        sed_cmds.append(
            f"sed -i 's|^{found_item}{full_ext}|BOTH{full_ext}|g' {config_file}")
        sed_cmds.append(
            f"sed -i 's|{{{found_item}{full_ext}}}|{{BOTH{full_ext}}}|g' {config_file}")
