"""!
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row, George McCabe
Abstract: Builds commands to run stat_analysis
"""

import os
import glob
from datetime import datetime
import itertools
from dateutil.relativedelta import relativedelta
import copy

from ..util import getlist, format_thresh
from ..util import do_string_sub, find_indices_in_config_section
from ..util import parse_var_list, remove_quotes, list_to_str
from ..util import get_start_and_end_times, get_time_prefix
from ..util import ti_get_seconds_from_relativedelta
from ..util import get_met_time_list, get_delta_list
from ..util import YMD, YMD_HMS
from . import RuntimeFreqWrapper


class StatAnalysisWrapper(RuntimeFreqWrapper):
    """! Wrapper to the MET tool stat_analysis which is used to filter
         and summarize data from MET's point_stat, grid_stat,
         ensemble_stat, and wavelet_stat
    """

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_OBTYPE',
        'METPLUS_DESC',
        'METPLUS_FCST_LEAD',
        'METPLUS_OBS_LEAD',
        'METPLUS_FCST_VALID_BEG',
        'METPLUS_FCST_VALID_END',
        'METPLUS_FCST_VALID_HOUR',
        'METPLUS_OBS_VALID_BEG',
        'METPLUS_OBS_VALID_END',
        'METPLUS_OBS_VALID_HOUR',
        'METPLUS_FCST_INIT_BEG',
        'METPLUS_FCST_INIT_END',
        'METPLUS_FCST_INIT_HOUR',
        'METPLUS_OBS_INIT_BEG',
        'METPLUS_OBS_INIT_END',
        'METPLUS_OBS_INIT_HOUR',
        'METPLUS_FCST_VAR',
        'METPLUS_OBS_VAR',
        'METPLUS_FCST_UNITS',
        'METPLUS_OBS_UNITS',
        'METPLUS_FCST_LEVEL',
        'METPLUS_OBS_LEVEL',
        'METPLUS_VX_MASK',
        'METPLUS_INTERP_MTHD',
        'METPLUS_INTERP_PNTS',
        'METPLUS_FCST_THRESH',
        'METPLUS_OBS_THRESH',
        'METPLUS_COV_THRESH',
        'METPLUS_ALPHA',
        'METPLUS_LINE_TYPE',
        'METPLUS_JOBS',
        'METPLUS_HSS_EC_VALUE',
    ]

    FIELD_LISTS = [
        'FCST_VAR_LIST',
        'OBS_VAR_LIST',
        'FCST_UNITS_LIST',
        'OBS_UNITS_LIST',
        'FCST_THRESH_LIST',
        'OBS_THRESH_LIST',
        'FCST_LEVEL_LIST',
        'OBS_LEVEL_LIST',
    ]

    FORMAT_LISTS = [
        'FCST_VALID_HOUR_LIST',
        'FCST_INIT_HOUR_LIST',
        'OBS_VALID_HOUR_LIST',
        'OBS_INIT_HOUR_LIST',
        'FCST_LEAD_LIST',
        'OBS_LEAD_LIST',
    ]

    EXPECTED_CONFIG_LISTS = [
        'MODEL_LIST',
        'DESC_LIST',
        'VX_MASK_LIST',
        'INTERP_MTHD_LIST',
        'INTERP_PNTS_LIST',
        'COV_THRESH_LIST',
        'ALPHA_LIST',
        'LINE_TYPE_LIST',
    ] + FORMAT_LISTS + FIELD_LISTS

    LIST_CATEGORIES = ['GROUP_LIST_ITEMS', 'LOOP_LIST_ITEMS']

    STRING_SUB_SPECIAL_KEYS = [
        'fcst_valid_hour_beg', 'fcst_valid_hour_end',
        'fcst_init_hour_beg', 'fcst_init_hour_end',
        'obs_valid_hour_beg', 'obs_valid_hour_end',
        'obs_init_hour_beg', 'obs_init_hour_end',
        'valid_hour', 'valid_hour_beg', 'valid_hour_end',
        'init_hour', 'init_hour_beg', 'init_hour_end',
        'fcst_valid', 'fcst_valid_beg', 'fcst_valid_end',
        'fcst_init', 'fcst_init_beg', 'fcst_init_end',
        'obs_valid', 'obs_valid_beg', 'obs_valid_end',
        'obs_init', 'obs_init_beg', 'obs_init_end',
        'valid', 'valid_beg', 'valid_end',
        'init', 'init_beg', 'init_end',
        'fcst_lead_hour', 'fcst_lead_min',
        'fcst_lead_sec', 'fcst_lead_totalsec',
        'obs_lead_hour', 'obs_lead_min',
        'obs_lead_sec', 'obs_lead_totalsec',
        'lead', 'lead_hour', 'lead_min', 'lead_sec', 'lead_totalsec'
    ]

    def __init__(self, config, instance=None):
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     'stat_analysis')
        self.app_name = os.path.basename(self.app_path)
        super().__init__(config, instance=instance)

    def get_command(self):
        """! Build command to run. It is assumed that any errors preventing a
        successfully run will have preventing this function from being called.

        @returns string with command to run
        """
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" -lookin {self.c_dict['LOOKIN_DIR']}"
                f" {' '.join(self.args)}").rstrip()

    def create_c_dict(self):
        """! Create a data structure (dictionary) that contains all the
             values set in the configuration files that are common for
             stat_analysis_wrapper.py.

        @returns dictionary containing the settings in the configuration files
         unique to the wrapper
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config', 'LOG_STAT_ANALYSIS_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        # skip RuntimeFreq wrapper logic to find files
        c_dict['FIND_FILES'] = False

        # STATAnalysis config file is optional, so
        # don't provide wrapped config file name as default value
        c_dict['CONFIG_FILE'] = self.get_config_file()

        c_dict['OUTPUT_DIR'] = self.config.getdir('STAT_ANALYSIS_OUTPUT_DIR',
                                                  '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set STAT_ANALYSIS_OUTPUT_DIR")

        # read optional template to set -out command line argument
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'STAT_ANALYSIS_OUTPUT_TEMPLATE', '')
        )

        # set date type, which is controlled by LOOP_BY
        c_dict['DATE_TYPE'] = get_time_prefix(self.config)
        if not c_dict['DATE_TYPE']:
            self.isOK = False

        start_dt, end_dt = get_start_and_end_times(self.config)
        if not start_dt:
            self.log_error('Could not get start and end times. '
                           'VALID_BEG/END or INIT_BEG/END must be set.')
        else:
            c_dict['DATE_BEG'] = start_dt
            c_dict['DATE_END'] = end_dt

        if not c_dict['RUNTIME_FREQ']:
            # if start and end times are not equal and
            # LOOP_ORDER = times (legacy), set frequency to once per init/valid
            if (start_dt != end_dt and
                    self.config.has_option('config', 'LOOP_ORDER') and
                    self.config.getraw('config', 'LOOP_ORDER') == 'times'):
                self.logger.warning(
                    'LOOP_ORDER has been deprecated. Please set '
                    'STAT_ANALYSIS_RUNTIME_FREQ = RUN_ONCE_PER_INIT_OR_VALID '
                    'instead.'
                )
                c_dict['RUNTIME_FREQ'] = 'RUN_ONCE_PER_INIT_OR_VALID'
            else:
                self.logger.debug('Setting RUNTIME_FREQ to RUN_ONCE. Set '
                                  'STAT_ANALYSIS_RUNTIME_FREQ to override.')
                c_dict['RUNTIME_FREQ'] = 'RUN_ONCE'

        # read jobs from STAT_ANALYSIS_JOB<n> or legacy JOB_NAME/ARGS if unset
        c_dict['JOBS'] = self._read_jobs_from_config()

        # read all lists and check if field lists are all empty
        all_field_lists_empty = self._read_lists_from_config(c_dict)

        # read any [FCST/OBS]_VAR<n>_* variables if they are set
        c_dict['VAR_LIST'] = parse_var_list(self.config)
        c_dict['MODEL_INFO_LIST'] = self._parse_model_info()

        # if MODEL_LIST was not set, populate it from the model info list
        if not c_dict['MODEL_LIST'] and c_dict['MODEL_INFO_LIST']:
            self.logger.warning("MODEL_LIST was left blank, "
                                + "creating with MODELn information.")
            for model_info in c_dict['MODEL_INFO_LIST']:
                c_dict['MODEL_LIST'].append(model_info['name'])

        c_dict = self._set_lists_loop_or_group(c_dict)

        # read MET config settings that will apply to every run
        self.add_met_config(name='hss_ec_value',
                            data_type='float',
                            metplus_configs=['STAT_ANALYSIS_HSS_EC_VALUE'])

        return self._c_dict_error_check(c_dict, all_field_lists_empty)

    def run_at_time_once(self, time_input):
        """! Function called when processing all times.

         @param time_input currently only used to set custom, now and today
         since only RUN_ONCE runtime frequency is supported
         @returns list of tuples containing all commands that were run and the
         environment variables that were set for each
        """
        # if init or valid time is set in the time input, set DATE_BEG and
        # DATE_END to that time to set fcst/obs_init/valid_beg/end values
        # if both init and valid are set, valid is used
        for init_or_valid in ['init', 'valid']:
            if time_input.get(init_or_valid, '*') != '*':
                self.c_dict['DATE_BEG'] = time_input[init_or_valid]
                self.c_dict['DATE_END'] = time_input[init_or_valid]

        self._run_stat_analysis(time_input)
        return self.all_commands

    def _run_stat_analysis(self, time_input):
        """! This runs stat_analysis over a period of valid
             or initialization dates for a job defined by
             the user.
        """
        runtime_settings_dict_list = self._get_all_runtime_settings(time_input)
        if not runtime_settings_dict_list:
            self.log_error('Could not get runtime settings dict list')
            return False

        for runtime_settings in runtime_settings_dict_list:
            self._run_stat_analysis_job(runtime_settings)

        return True

    def _get_all_runtime_settings(self, time_input):
        """! Get all settings for each run of stat_analysis.

        @returns list of dictionaries containing settings for each run
        """
        runtime_settings_dict_list = []
        c_dict_list = self._get_c_dict_list()
        for c_dict in c_dict_list:
            runtime_settings = self._get_runtime_settings(c_dict)
            runtime_settings_dict_list.extend(runtime_settings)

        # Loop over run settings.
        formatted_runtime_settings_dict_list = []
        for runtime_settings in runtime_settings_dict_list:
            # add time input values to runtime settings
            runtime_settings.update(time_input)
            stringsub_dict = self._build_stringsub_dict(runtime_settings)

            # Set up stat_analysis -lookin argument, model and obs information
            # and stat_analysis job.
            model_info = self._get_model_obtype_and_lookindir(runtime_settings)
            if model_info is None:
                return None

            # add obtype to string sub dict since it was added in
            # the call to _get_model_obtype_and_lookindir
            stringsub_dict['obtype'] = runtime_settings['OBTYPE'].strip('" ')
            jobs = self._get_job_info(model_info, runtime_settings,
                                      stringsub_dict)

            # get -out argument if set
            output_file = None
            if self.c_dict['OUTPUT_TEMPLATE']:
                output_filename = (
                    self._get_output_filename('output',
                                              self.c_dict['OUTPUT_TEMPLATE'],
                                              stringsub_dict)
                )
                output_file = os.path.join(self.c_dict['OUTPUT_DIR'],
                                           output_filename)

            # Set up forecast and observation valid and init time information
            runtime_settings_fmt = self._format_valid_init(runtime_settings,
                                                           stringsub_dict)

            # add jobs and output file path to formatted runtime_settings
            runtime_settings_fmt['JOBS'] = jobs
            runtime_settings_fmt['OUTPUT_FILENAME'] = output_file

            # save string sub dictionary to sub any other env vars for each run
            runtime_settings_fmt['string_sub'] = stringsub_dict

            formatted_runtime_settings_dict_list.append(runtime_settings_fmt)

        return formatted_runtime_settings_dict_list

    def _run_stat_analysis_job(self, runtime_settings):
        """!Set environment variables to run StatAnalysis job and call it.

        @param runtime_settings_dict_list list of dictionaries
         containing information needed to run a StatAnalysis job
        """
        self.clear()
        if not self._create_output_directories(runtime_settings):
            return

        # set METPLUS_ env vars for MET config file to be consistent
        # with other wrappers
        for key in self.WRAPPER_ENV_VAR_KEYS:
            item = key.replace('METPLUS_', '')
            if not runtime_settings.get(item, ''):
                continue
            value = runtime_settings.get(item, '')
            if key.endswith('_JOBS'):
                value = '["' + '","'.join(value) + '"]'
            elif key.endswith('_BEG') or key.endswith('_END'):
                value = f'"{value}"'
            else:
                value = f'[{value}]'
            item = item.lower().replace('_level', '_lev')
            value = f'{item} = {value};'
            self.env_var_dict[key] = value

        # send environment variables to logger
        self.set_environment_variables(runtime_settings['string_sub'])

        # set lookin dir to add to command
        self.logger.debug("Setting -lookin dir to "
                          f"{runtime_settings['LOOKIN_DIR']}")
        self.c_dict['LOOKIN_DIR'] = runtime_settings['LOOKIN_DIR']

        # set any command line arguments
        if self.c_dict.get('CONFIG_FILE'):
            self.args.append(f"-config {self.c_dict['CONFIG_FILE']}")
        else:
            self.args.append(runtime_settings['JOBS'][0])

        # set -out file path if requested, value will be set to None if not
        output_filename = runtime_settings.get('OUTPUT_FILENAME')
        if output_filename:
            self.args.append(f"-out {output_filename}")

        self.build()

    def _read_jobs_from_config(self):
        """! Parse the jobs from the METplusConfig object

        @returns list of strings containing each job specifications
        """
        jobs = []
        job_indices = list(
            find_indices_in_config_section(r'STAT_ANALYSIS_JOB(\d+)$',
                                           self.config,
                                           index_index=1).keys()
        )

        if job_indices:
            for j_id in job_indices:
                job = self.config.getraw('config', f'STAT_ANALYSIS_JOB{j_id}')
                if job:
                    jobs.append(job)

        # if not jobs found, check for old _JOB_NAME and _JOB_ARGS variables
        if not jobs:
            job_name = self.config.getraw('config', 'STAT_ANALYSIS_JOB_NAME')
            job_args = self.config.getraw('config', 'STAT_ANALYSIS_JOB_ARGS')
            if job_name and job_args:
                jobs.append(f'-job {job_name} {job_args}')

        return jobs

    def _c_dict_error_check(self, c_dict, all_field_lists_empty):
        """! Check values read into c_dict from METplusConfig and report errors
        if anything is misconfigured.

        @param c_dict dictionary containing config values to check
        @param all_field_lists_empty True if no field lists were parsed
        """
        if not c_dict.get('CONFIG_FILE'):
            if len(c_dict['JOBS']) > 1:
                self.log_error(
                    'Only 1 job can be set with STAT_ANALYSIS_JOB<n> if '
                    'STAT_ANALYSIS_CONFIG_FILE is not set.'
                )
            else:
                self.logger.info("STAT_ANALYSIS_CONFIG_FILE not set. Passing "
                                 "job arguments to stat_analysis directly on "
                                 "the command line. This will bypass "
                                 "any filtering done unless you add the "
                                 "arguments to STAT_ANALYSIS_JOBS<n>")

        if not c_dict['JOBS']:
            self.log_error(
                "Must set at least one job with STAT_ANALYSIS_JOB<n>"
            )
        else:
            # check if [dump_row_file] or [out_stat_file] are in any job
            for job in c_dict['JOBS']:
                for check in ('dump_row_file', 'out_stat_file'):
                    if f'[{check}]' not in job:
                        continue
                    for model in c_dict['MODEL_INFO_LIST']:
                        if model[f'{check}name_template']:
                            continue
                        conf = check.replace('_file', '').upper()
                        conf = f"STAT_ANALYSIS_{conf}_TEMPLATE"
                        self.log_error(f'Must set {conf} if [{check}] is used'
                                       ' in a job')

        # if var list is set and field lists are not all empty, error
        if c_dict['VAR_LIST'] and not all_field_lists_empty:
            self.log_error("Field information defined in both "
                           "[FCST/OBS]_VAR_LIST and "
                           "[FCST/OBS]_VAR<n>_[NAME/LEVELS]. Use "
                           "one or the other formats to run")

        # if model list and info list were not set, report and error
        if not c_dict['MODEL_LIST'] and not c_dict['MODEL_INFO_LIST']:
            self.log_error("No model information was found.")

        return c_dict

    def _read_lists_from_config(self, c_dict):
        """! Get list configuration variables and add to dictionary

         @param c_dict dictionary to hold output values
         @returns True if all field lists are empty or False if any are set
        """
        all_empty = True

        all_lists_to_read = self.EXPECTED_CONFIG_LISTS + self.LIST_CATEGORIES
        for conf_list in all_lists_to_read:
            if 'LEVEL_LIST' in conf_list:
                c_dict[conf_list] = (
                    self._get_level_list(conf_list.split('_')[0])
                )
            else:
                c_dict[conf_list] = self._format_conf_list(conf_list)

            # keep track if any field list is not empty
            if conf_list in self.FIELD_LISTS and c_dict[conf_list]:
                all_empty = False

        return all_empty

    def _get_level_list(self, data_type):
        """!Read forecast or observation level list from config.
            Format list items to match the format expected by
            StatAnalysis by removing parenthesis and any quotes,
            then adding back single quotes

              @param data_type type of list to get, FCST or OBS
              @returns list containing the formatted level list
        """
        level_list = []

        level_input = getlist(
            self.config.getraw('config', f'{data_type}_LEVEL_LIST', '')
        )

        for level in level_input:
            level = level.strip('(').strip(')')
            level = f'{remove_quotes(level)}'
            level_list.append(level)

        return [f'"{item}"' for item in level_list]

    def _format_conf_list(self, conf_list):
        """! Process config list. If list name (e.g. FCST_LEAD_LIST) is not
        set, then check if numbered config variable (e.g. FCST_LEAD_LIST<n>)
        is set. Format thresholds lists as thresholds. Add quotation marks
        around any list not found in the self.FORMAT_LISTS. Format lists will
        be formatted later based on the loop/group conditions.

         @param conf_list name of METplus config variable to process
         @returns list of items parsed from configuration
        """
        items = getlist(
            self.config.getraw('config', conf_list, '')
        )

        # if list is empty or unset, check for {LIST_NAME}<n>
        if not items:
            indices = list(
                find_indices_in_config_section(fr'{conf_list}(\d+)$',
                                               self.config,
                                               index_index=1).keys()
            )
            if indices:
                items = []
                for index in indices:
                    sub_items = getlist(
                        self.config.getraw('config', f'{conf_list}{index}')
                    )
                    if not sub_items:
                        continue

                    items.append(','.join(sub_items))

        # do not add quotes and format thresholds if threshold list
        if 'THRESH' in conf_list:
            return [format_thresh(item) for item in items]

        if conf_list in self.LIST_CATEGORIES:
            return items

        formatted_items = []
        for item in items:
            # do not format items in format list now
            if conf_list not in self.FORMAT_LISTS:
                sub_items = item.split(',')
                sub_item_str = '", "'.join(sub_items)
                formatted_items.append(f'"{sub_item_str}"')
            else:
                formatted_items.append(item)

        return formatted_items

    def _set_lists_loop_or_group(self, c_dict):
        """! Determine whether the lists from the METplus config file
             should treat the items in that list as a group or items
             to be looped over based on user settings, the values
             in the list, and process being run.

             @param c_dict dictionary containing the configuration information

             @returns tuple containing lists_to_group_items ( list of
              all the list names whose items are being grouped
              together) and lists_to_loop_items (list of all
              the list names whose items are being looped over)
        """
        # get list of list variables not found in group or loop lists
        missing_config_list = [conf for conf in self.EXPECTED_CONFIG_LISTS
                               if conf not in c_dict['GROUP_LIST_ITEMS']
                               and conf not in c_dict['LOOP_LIST_ITEMS']]

        # add missing lists to group_lists
        for missing_config in missing_config_list:
            c_dict['GROUP_LIST_ITEMS'].append(missing_config)

        # move empty lists in loop lists to group lists
        for list_name in c_dict['LOOP_LIST_ITEMS']:
            # skip if list has values
            if c_dict[list_name]:
                continue

            self.logger.warning(f'{list_name} was found in LOOP_LIST_ITEMS'
                                ' but is empty. Moving to group list')
            c_dict['GROUP_LIST_ITEMS'].append(list_name)
            c_dict['LOOP_LIST_ITEMS'].remove(list_name)

        # log summary of group and loop lists
        self.logger.debug("Items in these lists will be grouped together: "
                          + ', '.join(c_dict['GROUP_LIST_ITEMS']))
        self.logger.debug("Items in these lists will be looped over: "
                          + ', '.join(c_dict['LOOP_LIST_ITEMS']))

        return c_dict

    def _build_stringsub_dict(self, config_dict):
        """! Build a dictionary with list names, dates, and commonly
             used identifiers to pass to string_template_substitution.

        @param config_dict dictionary containing the configuration information
        @returns dictionary with the formatted info to pass to do_string_sub
        """
        date_type = self.c_dict['DATE_TYPE']

        stringsub_dict = {}

        # add all loop list and group list items to string sub keys list
        for list_item in self.EXPECTED_CONFIG_LISTS:
            list_name = list_item.replace('_LIST', '').lower()
            stringsub_dict[list_name] = ''

        # create a dictionary of empty string values from the special keys
        for special_key in self.STRING_SUB_SPECIAL_KEYS:
            stringsub_dict[special_key] = ''

        # set time info from current runtime
        for item in ['now', 'today', 'custom', 'init', 'valid', 'lead']:
            stringsub_dict[item] = config_dict.get(item, '')
            if stringsub_dict[item] == '*':
                stringsub_dict[item] = 'ALL'

        # Set string sub info from fcst/obs hour lists
        self._set_stringsub_hours(stringsub_dict,
                                  config_dict.get(f'FCST_{date_type}_HOUR'),
                                  config_dict.get(f'OBS_{date_type}_HOUR'))

        # handle opposite of date_type VALID if INIT and vice versa
        self._set_strinsub_other(stringsub_dict, date_type.lower(),
                                 config_dict.get('FCST_LEAD'),
                                 config_dict.get('OBS_LEAD'))

        # Set loop information
        for loop_or_group_list in self.EXPECTED_CONFIG_LISTS:
            list_name = loop_or_group_list.replace('_LIST', '')
            sub_name = list_name.lower()
            list_name_value = self._get_list_name_value(list_name, config_dict)

            if 'HOUR' not in list_name and 'LEAD' not in list_name:
                stringsub_dict[sub_name] = list_name_value

                # if list is MODEL, also set obtype
                if list_name == 'MODEL':
                    stringsub_dict['obtype'] = (
                        config_dict.get('OBTYPE', '').replace('"', '')
                        .replace(' ', '')
                    )

                continue

            if 'HOUR' in list_name:
                self._build_stringsub_hours(list_name, config_dict,
                                            stringsub_dict)
            elif 'LEAD' in list_name:
                self._build_stringsub_leads(list_name, config_dict,
                                            stringsub_dict)

        # Some lines for debugging if needed in future
        # for key, value in stringsub_dict.items():
        #    self.logger.debug("{} ({})".format(key, value))
        return stringsub_dict

    def _build_stringsub_hours(self, list_name, config_dict, stringsub_dict):
        """! Handle logic specific to setting lists named with HOUR

        @param list_name name of list to process
        @param config_dict dictionary to read values from
        @param stringsub_dict dictionary to set values
        """
        sub_name = list_name.lower()
        delta_list = get_delta_list(config_dict[list_name])
        if not delta_list:
            list_name_value = self._get_list_name_value(list_name, config_dict)
            stringsub_dict[sub_name] = list_name_value
            stringsub_dict[sub_name + '_beg'] = relativedelta()
            stringsub_dict[sub_name + '_end'] = (
                relativedelta(hours=+23, minutes=+59, seconds=+59)
            )
            return

        if len(delta_list) == 1:
            stringsub_dict[sub_name] = delta_list[0]
        else:
            stringsub_dict[sub_name] = (
                '_'.join(get_met_time_list(config_dict[list_name]))
            )

        stringsub_dict[sub_name + '_beg'] = delta_list[0]
        stringsub_dict[sub_name + '_end'] = delta_list[-1]

        check_list = self._get_check_list(list_name, config_dict)
        # if opposite fcst is not set or the same,
        # set init/valid hour beg/end to fcst, same for obs
        if not check_list or config_dict[list_name] == check_list:
            # sub name e.g. fcst_valid_hour
            # generic list e.g. valid_hour
            generic_list = (
                sub_name.replace('fcst_', '').replace('obs_', '')
            )
            stringsub_dict[f'{generic_list}_beg'] = (
                stringsub_dict[f'{sub_name}_beg']
            )
            stringsub_dict[f'{generic_list}_end'] = (
                stringsub_dict[f'{sub_name}_end']
            )

            if (stringsub_dict[f'{generic_list}_beg'] ==
                    stringsub_dict[f'{generic_list}_end']):
                stringsub_dict[generic_list] = (
                    stringsub_dict[f'{sub_name}_end']
                )

    @staticmethod
    def _get_list_name_value(list_name, config_dict):
        value = config_dict.get(list_name, '')
        value = value.replace('"', '').replace(' ', '').replace(',', '_')
        value = value.replace('*', 'ALL')
        return value

    def _build_stringsub_leads(self, list_name, config_dict, stringsub_dict):
        """! Handle logic specific to setting lists named with LEAD

        @param list_name name of list to process
        @param config_dict dictionary to read values from
        @param stringsub_dict dictionary to set values
        """
        sub_name = list_name.lower()
        lead_list = get_met_time_list(config_dict.get(list_name))

        if not lead_list:
            return

        # if multiple leads are specified, format lead info
        # using met time notation separated by underscore
        if len(lead_list) > 1:
            stringsub_dict[sub_name] = '_'.join(lead_list)
            return

        stringsub_dict[sub_name] = lead_list[0]

        lead_rd = get_delta_list(config_dict[list_name])[0]
        total_sec = ti_get_seconds_from_relativedelta(lead_rd)
        stringsub_dict[sub_name + '_totalsec'] = str(total_sec)

        stringsub_dict[f'{sub_name}_hour'] = lead_list[0][:-4]
        stringsub_dict[f'{sub_name}_min'] = lead_list[0][-4:-2]
        stringsub_dict[f'{sub_name}_sec'] = lead_list[0][-2:]

        check_list = self._get_check_list(list_name, config_dict)
        if not check_list or config_dict[list_name] == check_list:
            stringsub_dict['lead'] = stringsub_dict[sub_name]
            stringsub_dict['lead_hour'] = (
                stringsub_dict[sub_name + '_hour']
            )
            stringsub_dict['lead_min'] = (
                stringsub_dict[sub_name + '_min']
            )
            stringsub_dict['lead_sec'] = (
                stringsub_dict[sub_name + '_sec']
            )
            stringsub_dict['lead_totalsec'] = (
                stringsub_dict[sub_name + '_totalsec']
            )

    @staticmethod
    def _get_check_list(list_name, config_dict):
        """! Helper function for getting opposite list from config dict.

        @param list_name either FCST or OBS
        @param config_dict dictionary to query
        @returns equivalent OBS item if list_name is FCST,
         equivalent FCST item if list_name is OBS, or
         None if list_name is not FCST or OBS
        """
        if 'FCST' in list_name:
            return config_dict[list_name.replace('FCST', 'OBS')]
        if 'OBS' in list_name:
            return config_dict[list_name.replace('OBS', 'FCST')]
        return None

    def _set_stringsub_hours(self, sub_dict, fcst_hour_str, obs_hour_str):
        """! Set string sub dictionary _beg and _end values for fcst and obs
        hour lists.
        Set other values depending on values set in fcst and obs hour lists.
        Values that are set depend on what it set in c_dict DATE_TYPE, which
        is either INIT or VALID. If neither fcst or obs hr list are set,
        {date_type}_beg/end and {date_type} are not set at all (empty string).

        @param sub_dict dictionary to set string sub values
        @param fcst_hour_str string with list of forecast hours to process
        @param obs_hour_str string with list of observation hours to process
        """
        if fcst_hour_str:
            fcst_hour_list = get_delta_list(fcst_hour_str)
        else:
            fcst_hour_list = None

        if obs_hour_str:
            obs_hour_list = get_delta_list(obs_hour_str)
        else:
            obs_hour_list = None

        self._set_stringsub_hours_item(sub_dict, 'fcst', fcst_hour_list)
        self._set_stringsub_hours_item(sub_dict, 'obs', obs_hour_list)

        self._set_stringsub_generic(sub_dict, fcst_hour_list, obs_hour_list,
                                    self.c_dict['DATE_TYPE'].lower())

    def _set_stringsub_hours_item(self, sub_dict, fcst_or_obs, hour_list):
        """! Set either fcst or obs values in string sub dictionary, e.g.
        [fcst/obs]_[init/valid]_[beg/end].
        Values that are set depend on what it set in c_dict DATE_TYPE, which
        is either INIT or VALID. If the beg and end values are the same, then
        also set the same variable without the _beg/end extension, e.g. if
        fcst_valid_beg is equal to fcst_valid_end, also set fcst_valid.

        @param sub_dict dictionary to set string sub values
        @param fcst_or_obs string to note processing either fcst or obs
        @param hour_list list of fcst or obs hours
        """
        date_beg = self.c_dict['DATE_BEG']
        date_end = self.c_dict['DATE_END']
        prefix = f"{fcst_or_obs}_{self.c_dict['DATE_TYPE'].lower()}"

        # get YYYYMMDD of begin and end time
        beg_ymd = datetime.strptime(date_beg.strftime(YMD), YMD)
        end_ymd = datetime.strptime(date_end.strftime(YMD), YMD)

        # if hour list is provided, truncate begin and end time to YYYYMMDD
        # and add first hour offset to begin time and last hour to end time
        if hour_list:
            sub_dict[f'{prefix}_beg'] = beg_ymd + hour_list[0]
            sub_dict[f'{prefix}_end'] = end_ymd + hour_list[-1]
            if sub_dict[f'{prefix}_beg'] == sub_dict[f'{prefix}_end']:
                sub_dict[prefix] = sub_dict[f'{prefix}_beg']

            return

        sub_dict[f'{prefix}_beg'] = date_beg

        # if end time is only YYYYMMDD, set HHMMSS to 23:59:59
        # otherwise use HHMMSS from end time
        if date_end == end_ymd:
            sub_dict[f'{prefix}_end'] = end_ymd + relativedelta(hours=+23,
                                                                minutes=+59,
                                                                seconds=+59)
        else:
            sub_dict[f'{prefix}_end'] = date_end

    @staticmethod
    def _set_stringsub_generic(sub_dict, fcst_hour_list, obs_hour_list,
                               date_type):
        """! Set [init/valid]_[beg/end] values based on the hour lists that
        are provided.
        Set {date_type}_[beg/end] to fcst_{date_type}_[beg/end] if
        fcst and obs lists are the same or if fcst list is set and obs is not.
        Set {date_type}_[beg/end] to obs_{date_type}_[beg/end] if obs list is
        set and fcst is not.
        Also sets {date_type} if {date_type}_beg and {date_type}_end are equal.

        @param sub_dict dictionary to set string sub values
        @param fcst_hour_list list of forecast hours or leads
        @param obs_hour_list list of observation hours or leads
        @param date_type type of date to process: valid or init
        """
        # if fcst and obs hour lists the same or if fcst is set but not obs,
        # set {date_type}_beg/end to fcst_{date_type}_beg/end
        if (fcst_hour_list == obs_hour_list or
                (fcst_hour_list and not obs_hour_list)):
            sub_dict[f'{date_type}_beg'] = sub_dict[f'fcst_{date_type}_beg']
            sub_dict[f'{date_type}_end'] = sub_dict[f'fcst_{date_type}_end']

        # if fcst hr list is set but obs hr list is not,
        # set {date_type}_beg/end to obs_{date_type}_beg/end
        elif not fcst_hour_list and obs_hour_list:
            sub_dict[f'{date_type}_beg'] = sub_dict[f'obs_{date_type}_beg']
            sub_dict[f'{date_type}_end'] = sub_dict[f'obs_{date_type}_end']

        # if {date_type} beg and end are the same, set {date_type}
        if sub_dict[f'{date_type}_beg'] == sub_dict[f'{date_type}_end']:
            sub_dict[date_type] = sub_dict[f'{date_type}_beg']

    def _set_strinsub_other(self, sub_dict, date_type, fcst_lead_str,
                            obs_lead_str):
        """! Compute beg and end values for opposite of date_type (e.g. valid
        if init and vice versa) using min/max forecast leads.

        @param sub_dict dictionary to set string sub values
        @param date_type type of date to process: valid or init
        @param fcst_lead_str string to parse list of forecast leads
        @param obs_lead_str string to parse list of observation leads
        """
        if fcst_lead_str:
            fcst_lead_list = get_delta_list(fcst_lead_str)
        else:
            fcst_lead_list = None

        if obs_lead_str:
            obs_lead_list = get_delta_list(obs_lead_str)
        else:
            obs_lead_list = None

        other_type = 'valid' if date_type == 'init' else 'init'
        self._set_strinsub_other_item(sub_dict, date_type, 'fcst',
                                      fcst_lead_list)
        self._set_strinsub_other_item(sub_dict, date_type, 'obs',
                                      obs_lead_list)
        self._set_stringsub_generic(sub_dict, fcst_lead_list, obs_lead_list,
                                    other_type)

    @staticmethod
    def _set_strinsub_other_item(sub_dict, date_type, fcst_or_obs, hour_list):
        """! Compute other type's begin and end values using the beg/end and
        min/max forecast leads.
        If date_type is init,
         compute valid_beg by adding init_beg and min lead,
         compute valid_end by adding init_end and max lead.
        If date_type is valid,
         compute init_beg by subtracting max lead from valid_beg,
         compute init_end by subtracting min lead from valid_end.

        @param sub_dict dictionary to set string sub values
        @param date_type type of date to process: valid or init
        @param fcst_or_obs string to use to process either fcst or obs
        @param hour_list list of forecast leads to use to calculate times
        """
        other_type = 'valid' if date_type == 'init' else 'init'
        date_prefix = f'{fcst_or_obs}_{date_type}'
        other_prefix = f'{fcst_or_obs}_{other_type}'
        if not hour_list:
            sub_dict[f'{other_prefix}_beg'] = sub_dict[f'{date_prefix}_beg']
            sub_dict[f'{other_prefix}_end'] = sub_dict[f'{date_prefix}_end']
            return

        min_lead = hour_list[0]
        max_lead = hour_list[-1]

        if date_type == 'init':
            sub_dict[f'{other_prefix}_beg'] = (
                    sub_dict[f'{date_prefix}_beg'] + min_lead
            )
            sub_dict[f'{other_prefix}_end'] = (
                    sub_dict[f'{date_prefix}_end'] + max_lead
            )
        else:
            sub_dict[f'{other_prefix}_beg'] = (
                    sub_dict[f'{date_prefix}_beg'] - max_lead
            )
            sub_dict[f'{other_prefix}_end'] = (
                    sub_dict[f'{date_prefix}_end'] - min_lead
            )

    def _get_output_filename(self, output_type, filename_template,
                             stringsub_dict):
        """! Create a file name for stat_analysis output.

        @param output_type string for the type of stat_analysis output, either
        dump_row, out_stat, or output.
        @param filename_template string of the template to create the file
         name.
        @param stringsub_dict dictionary with info to substitute into filename
        templates
        @returns string of the filled file name template
        """
        self.logger.debug(f"Building {output_type} filename from "
                          f"template: {filename_template}")

        output_filename = do_string_sub(filename_template,
                                        **stringsub_dict)
        return output_filename

    def _get_lookin_dir(self, dir_path, config_dict):
        """!Fill in necessary information to get the path to the lookin
         directory to pass to stat_analysis. Expand any wildcards.

        @param dir_path string of the user provided directory path
        @param config_dict dictionary containing the configuration information
        @returns string of the filled directory from dir_path
        """
        stringsub_dict = self._build_stringsub_dict(config_dict)
        dir_path_filled = do_string_sub(dir_path,
                                        **stringsub_dict)

        all_paths = []
        for one_path in dir_path_filled.split(','):
            if '*' not in one_path:
                all_paths.append(one_path.strip())
                continue

            self.logger.debug(f"Expanding wildcard path: {one_path}")
            expand_path = glob.glob(one_path.strip())
            if not expand_path:
                self.logger.warning("Wildcard expansion found no matches")
                continue
            all_paths.extend(sorted(expand_path))

        return ' '.join(all_paths)

    def _format_valid_init(self, config_dict, stringsub_dict):
        """! Format the valid and initialization dates and
             hours for the MET stat_analysis config file.

        @param config_dict dictionary containing the configuration information
        @param stringsub_dict dictionary with info to substitute into filename
        templates
        @returns dictionary containing the edited configuration information
         for valid and initialization dates and hours
        """
        output_dict = copy.deepcopy(config_dict)
        # set all of the HOUR and LEAD lists to include the MET time format
        for list_name in self.FORMAT_LISTS:
            list_name = list_name.replace('_LIST', '')
            values = get_met_time_list(config_dict.get(list_name, ''))
            values = [f'"{item}"' for item in values]
            output_dict[list_name] = ', '.join(values)

        for fcst_or_obs in ['FCST', 'OBS']:
            for init_or_valid in ['INIT', 'VALID']:
                self._format_valid_init_item(output_dict,
                                             stringsub_dict,
                                             fcst_or_obs,
                                             init_or_valid)

        return output_dict

    def _format_valid_init_item(self, output_dict, stringsub_dict, fcst_or_obs,
                                init_or_valid):
        """! Check if variables are set in the METplusConfig to explicitly
        set the begin and end values in the wrapped MET config file.

        @param output_dict dictionary to set values to set in MET config
        @param fcst_or_obs string either FCST or OBS
        @param init_or_valid string either INIT or VALID
        """
        prefix = f'{fcst_or_obs}_{init_or_valid}'

        # check if explicit value is set for _BEG or _END
        # e.g. STAT_ANALYSIS_FCST_INIT_BEG
        app = self.app_name.upper()
        for beg_or_end in ('BEG', 'END'):
            var_prefix = f'{app}_{prefix}_{beg_or_end}'
            generic_prefix = f'{app}_{init_or_valid}_{beg_or_end}'
            value = None
            if self.config.has_option('config', var_prefix):
                value = self.config.getraw('config', var_prefix)
            elif self.config.has_option('config', generic_prefix):
                value = self.config.getraw('config', generic_prefix)

            if value:
                formatted_value = do_string_sub(value, **stringsub_dict)
                output_dict[f'{prefix}_{beg_or_end}'] = formatted_value

    def _parse_model_info(self):
        """! Parse for model information.

        @returns list of dictionaries containing model information
        """
        model_info_list = []
        model_indices = list(
            find_indices_in_config_section(r'MODEL(\d+)$',
                                           self.config,
                                           index_index=1).keys()
        )
        for m in model_indices:
            model_name = self.config.getraw('config', f'MODEL{m}')

            # add quotes to model name if a value is set
            model_name = f'"{model_name}"' if model_name else ''

            model_dir = (
                self.config.getraw('config',
                                   f'MODEL{m}_STAT_ANALYSIS_LOOKIN_DIR')
            )
            if not model_dir:
                self.log_error(f"MODEL{m}_STAT_ANALYSIS_LOOKIN_DIR must be "
                               f"set if MODEL{m} is set.")
                return None, None

            model_obtype = self.config.getraw('config', f'MODEL{m}_OBTYPE')
            model_obtype = f'"{model_obtype}"' if model_obtype else ''

            model_dump_row_filename_template = None
            model_out_stat_filename_template = None
            for output_type in ['DUMP_ROW', 'OUT_STAT']:
                var_name = f'STAT_ANALYSIS_{output_type}_TEMPLATE'
                # use MODEL<n>_STAT_ANALYSIS_<output_type>_TEMPLATE if set
                model_filename_template = (
                    self.config.getraw('config', f'MODEL{m}_{var_name}')
                )

                # if not set, use STAT_ANALYSIS_<output_type>_TEMPLATE
                if not model_filename_template:
                    model_filename_template = (
                        self.config.getraw('config', var_name)
                    )

                if output_type == 'DUMP_ROW':
                    model_dump_row_filename_template = model_filename_template
                elif output_type == 'OUT_STAT':
                    model_out_stat_filename_template = model_filename_template

            mod = {
                'name': model_name,
                'dir': model_dir,
                'obtype': model_obtype,
                'dump_row_filename_template': model_dump_row_filename_template,
                'out_stat_filename_template': model_out_stat_filename_template,
            }
            model_info_list.append(mod)

        if not model_info_list:
            self.log_error('At least one set of model information must be '
                           'set using MODEL<n>, MODEL<n>_OBTYPE, and '
                           'MODEL<n>_STAT_ANALYSIS_LOOKIN_DIR')

        return model_info_list

    def _process_job_args(self, job_type, job, model_info,
                         runtime_settings_dict, stringsub_dict):
        """! Get dump_row or out_stat file paths and replace [dump_row_file]
        and [out_stat_file] keywords from job arguments with the paths.

        @param job_type type of job, either dump_row or out_stat
        @param job string of job arguments to replace keywords
        @param model_info dictionary containing info for each model processed.
         Used to get filename template to use for substitution
        @param runtime_settings_dict dictionary containing information for the
        run that is being processed. Used to substitute values.
        @param stringsub_dict dictionary with info to substitute into filename
        templates
        @returns job string with values substituted for [dump_row_file] or
         [out_stat_file]
        """
        output_template = (
            model_info[f'{job_type}_filename_template']
        )

        output_filename = (
            self._get_output_filename(job_type,
                                      output_template,
                                      stringsub_dict)
        )
        output_file = os.path.join(self.c_dict['OUTPUT_DIR'],
                                   output_filename)

        # substitute output filename in JOBS line
        job = job.replace(f'[{job_type}_file]', output_file)
        job = job.replace(f'[{job_type}_filename]', output_file)

        # add output file path to runtime_settings_dict
        runtime_settings_dict[f'{job_type.upper()}_FILENAME'] = output_file

        return job

    def _get_c_dict_list(self):
        """! Build list of config dictionaries for each field
        name/level/threshold specified by the [FCST/OBS]_VAR<n>_* config vars.
        If field information was specified in the field lists
        [FCST_OBS]_[VAR/UNITS/THRESH/LEVEL]_LIST instead of these
        variables, then return a list with a single dictionary that contains
        the relevant values from self.c_dict.

        @returns list of dictionaries for each field to process
        """
        # if fields were not specified with [FCST/OBS]_VAR<n>_* variables
        # return and array with only self.c_dict
        if not self.c_dict['VAR_LIST']:
            c_dict = {}
            self._add_other_lists_to_c_dict(c_dict)
            return [c_dict]

        # otherwise, use field information to build lists with single items
        # make individual dictionaries for each threshold
        var_info_list = self.c_dict['VAR_LIST']
        c_dict_list = []
        for var_info in var_info_list:
            fcst_units, obs_units = self._get_field_units(var_info['index'])

            run_fourier = (
                self.config.getbool('config',
                                    f"VAR{var_info['index']}_FOURIER_DECOMP",
                                    False)
            )
            fourier_wave_num_pairs = ['']
            if run_fourier:
                fourier_wave_num_pairs = getlist(
                    self.config.getstr('config',
                                       f"VAR{var_info['index']}_WAVE_NUM_LIST",
                                       '')
                )

            # if no thresholds were specified, use a list
            # containing an empty string to loop one iteration
            fcst_thresholds = var_info['fcst_thresh']
            if not fcst_thresholds:
                fcst_thresholds = ['']

            obs_thresholds = var_info['obs_thresh']
            if not obs_thresholds:
                obs_thresholds = ['']

            for fcst_thresh, obs_thresh in zip(fcst_thresholds, obs_thresholds):
                for pair in fourier_wave_num_pairs:
                    c_dict = {
                        'index': var_info['index'],
                        'FCST_VAR_LIST': [f'"{var_info["fcst_name"]}"'],
                        'OBS_VAR_LIST': [f'"{var_info["obs_name"]}"'],
                        'FCST_LEVEL_LIST': [f'"{var_info["fcst_level"]}"'],
                        'OBS_LEVEL_LIST': [f'"{var_info["obs_level"]}"'],
                        'FCST_THRESH_LIST': [], 'OBS_THRESH_LIST': [],
                        'FCST_UNITS_LIST': [], 'OBS_UNITS_LIST': [],
                        'INTERP_MTHD_LIST': [],
                    }

                    if fcst_thresh:
                        thresh_formatted = format_thresh(fcst_thresh)
                        c_dict['FCST_THRESH_LIST'].append(thresh_formatted)

                    if obs_thresh:
                        thresh_formatted = format_thresh(obs_thresh)
                        c_dict['OBS_THRESH_LIST'].append(thresh_formatted)

                    if fcst_units:
                        c_dict['FCST_UNITS_LIST'].append(f'"{fcst_units}"')
                    if obs_units:
                        c_dict['OBS_UNITS_LIST'].append(f'"{obs_units}"')

                    c_dict['run_fourier'] = run_fourier
                    if pair:
                        c_dict['INTERP_MTHD_LIST'] = ['WV1_' + pair]

                    self._add_other_lists_to_c_dict(c_dict)

                    c_dict_list.append(c_dict)

        return c_dict_list

    @staticmethod
    def _get_runtime_settings(c_dict):
        """! Build list of all combinations of runtime settings that should be
        run. Combine all group lists into a single item separated by comma.
        Compute the cartesian product to get all of the different combinations
        of the loop lists to create the final list of settings to run.

        @param c_dict dictionary containing [GROUP/LOOP]_LIST_ITEMS that
        contain list names to group or loop, as well the actual lists which
        are named the same as the values in the [GROUP/LOOP]_LIST_ITEMS but
        with the _LIST extension removed.
        @returns list of dictionaries that contain all of the settings to use
        for a given run.
        """
        runtime_setup_dict = {}

        # for group items, set the value to a list with a single item that is
        # a string of all items separated by a comma
        for group_list in c_dict['GROUP_LIST_ITEMS']:
            key = group_list.replace('_LIST', '')
            runtime_setup_dict[key] = [', '.join(c_dict[group_list])]

        # for loop items, pass the list directly as the value
        for loop_list in c_dict['LOOP_LIST_ITEMS']:
            key = loop_list.replace('_LIST', '')
            runtime_setup_dict[key] = c_dict[loop_list]

        # Create a dict with all the combinations of settings to be run
        runtime_setup_dict_names = sorted(runtime_setup_dict)

        runtime_settings_dict_list = []

        # find cartesian product (all combos of the lists) of each dict key
        products = itertools.product(
            *(runtime_setup_dict[name] for name in runtime_setup_dict_names)
        )
        for product in products:
            # pair up product values with dict keys and add them to new dict
            next_dict = {}
            for key, value in zip(runtime_setup_dict_names, product):
                next_dict[key] = value
            runtime_settings_dict_list.append(next_dict)

        # NOTE: Logic to create list of runtime settings was previously
        # handled using complex list comprehension that was difficult to
        # read. New logic was intended to be more readable by other developers.
        # Original code is commented below for reference:
        # runtime_settings_dict_list = [
        #     dict(zip(runtime_setup_dict_names, prod)) for prod in
        #     itertools.product(*(runtime_setup_dict[name] for name in
        #                         runtime_setup_dict_names))
        # ]

        return runtime_settings_dict_list

    def _get_field_units(self, index):
        """! Get units of fcst and obs fields if set based on VAR<n> index

         @param index VAR<n> index corresponding to other [FCST/OBS] info
         @returns tuple containing forecast and observation units respectively
        """
        fcst_units = self.config.getraw('config', f'FCST_VAR{index}_UNITS')
        obs_units = self.config.getraw('config', f'OBS_VAR{index}_UNITS')
        if not obs_units and fcst_units:
            obs_units = fcst_units
        elif not fcst_units and obs_units:
            fcst_units = obs_units

        return fcst_units, obs_units

    def _add_other_lists_to_c_dict(self, c_dict):
        """! Using GROUP_LIST_ITEMS and LOOP_LIST_ITEMS, add lists from
             self.c_dict that are not already in c_dict.
             @param c_dict dictionary to add values to
        """
        # add group and loop lists
        for list_category in self.LIST_CATEGORIES:
            list_items = self.c_dict[list_category]
            if list_category not in c_dict:
                c_dict[list_category] = list_items

            for list_item in list_items:
                if list_item not in c_dict:
                    c_dict[list_item] = self.c_dict[list_item]

    def _get_model_obtype_and_lookindir(self, runtime_settings_dict):
        """! Reads through model info dictionaries for given run.
        Sets lookindir command line argument. Sets MODEL and OBTYPE values in
        runtime setting dictionary.

        @param runtime_settings_dict dictionary with all settings used in run
        @returns last model info dictionary is successful, None if not.
        """
        lookin_dirs = []
        model_list = []
        obtype_list = []
        model_info = None

        # get list of models to process
        models_to_run = runtime_settings_dict['MODEL'].split(',')
        for model_info in self.c_dict['MODEL_INFO_LIST']:
            # skip model if not in list of models to process
            if model_info['name'] not in models_to_run:
                self.logger.debug(f"Model {model_info['name']} not found in "
                                  "list of models to run. Skipping.")
                continue

            model_list.append(model_info['name'])
            if model_info['obtype']:
                obtype_list.append(model_info['obtype'])

            # set MODEL and OBTYPE to single item to find lookin dir
            runtime_settings_dict['MODEL'] = model_info["name"]
            runtime_settings_dict['OBTYPE'] = model_info["obtype"]

            lookin_dirs.append(
                self._get_lookin_dir(model_info['dir'], runtime_settings_dict)
            )

        # set lookin dir command line argument
        runtime_settings_dict['LOOKIN_DIR'] = ' '.join(lookin_dirs)

        # error and return None if lookin dir is empty
        if not runtime_settings_dict['LOOKIN_DIR']:
            self.log_error("No value found for lookin dir")
            return None

        if not model_list:
            self.log_error("Could not find model to process")
            return None

        # set values in runtime settings dict for model and obtype
        runtime_settings_dict['MODEL'] = list_to_str(model_list)
        runtime_settings_dict['OBTYPE'] = list_to_str(obtype_list)

        # return last model info dict used
        return model_info

    def _get_job_info(self, model_info, runtime_settings_dict, stringsub_dict):
        """! Get job information and concatenate values into a string

        @param model_info model info to use to determine output file paths
        @param runtime_settings_dict dictionary with all settings for next run
        @param stringsub_dict dictionary with info to substitute into filename
        templates
        @returns list of strings containing job info to pass config file
        """
        jobs = []
        for job in self.c_dict['JOBS']:
            for job_type in ['dump_row', 'out_stat']:
                if f"-{job_type}" not in job:
                    continue

                job = self._process_job_args(job_type, job, model_info,
                                             runtime_settings_dict,
                                             stringsub_dict)

            # substitute filename templates that may be found in rest of job
            job = do_string_sub(job, **stringsub_dict)
            jobs.append(job)

        return jobs

    def _create_output_directories(self, runtime_settings_dict):
        """! Check if output filename is set for dump_row or out_stat. If set,
             Check if the file already exists and if it should be skipped.

             @param runtime_settings_dict dictionary containing filename info
             @returns True if job should be run, False if it should be skipped
        """
        run_job = True
        for job_type in ['DUMP_ROW', 'OUT_STAT', 'OUTPUT']:
            output_path = (
                runtime_settings_dict.get(f'{job_type}_FILENAME')
            )
            if not output_path:
                continue

            if not self.find_and_check_output_file(
                    output_path_template=output_path):
                run_job = False

        return run_job
