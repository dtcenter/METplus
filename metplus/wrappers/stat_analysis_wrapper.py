'''
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row, George McCabe
Abstract: Runs stat_analysis
History Log: Fourth version
Usage: stat_analysis_wrapper.py
Parameters: None
Input Files: MET STAT files
Output Files: MET STAT files
Condition codes: 0 for success, 1 for failure
'''

import logging
import os
import copy
import re
import glob
import datetime
import itertools
from dateutil.relativedelta import relativedelta

from ..util import getlist
from ..util import met_util as util
from ..util import do_string_sub, find_indices_in_config_section
from ..util import parse_var_list, remove_quotes
from ..util import get_start_and_end_times
from ..util import time_string_to_met_time, get_relativedelta
from ..util import ti_get_seconds_from_relativedelta
from . import CommandBuilder

class StatAnalysisWrapper(CommandBuilder):
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

        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
        if self.args:
            cmd += ' ' + ' '.join(self.args)

        if not self.lookindir:
            self.log_error("No lookin directory specified")
            return None
        
        cmd += ' -lookin ' + self.lookindir

        if self.c_dict.get('CONFIG_FILE'):
            cmd += f" -config {self.c_dict['CONFIG_FILE']}"
        else:
            cmd += f' {self.job_args}'

        if self.c_dict.get('OUTPUT_FILENAME'):
            cmd += f" -out {self.c_dict['OUTPUT_FILENAME']}"

        return cmd

    def create_c_dict(self):
        """! Create a data structure (dictionary) that contains all the
             values set in the configuration files that are common for 
             stat_analysis_wrapper.py.
        
             Args:
 
             Returns:
                 c_dict  - a dictionary containing the settings in the
                           configuration files unique to the wrapper
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config', 'LOG_STAT_ANALYSIS_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        # STATAnalysis config file is optional, so
        # don't provide wrapped config file name as default value
        c_dict['CONFIG_FILE'] = self.get_config_file()

        c_dict['OUTPUT_DIR'] = self.config.getdir('STAT_ANALYSIS_OUTPUT_DIR',
                                                  '')

        # read optional template to set -out command line argument
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'STAT_ANALYSIS_OUTPUT_TEMPLATE', '')
        )

        # set date type, which is typically controlled by LOOP_BY
        c_dict['DATE_TYPE'] = self.config.getstr('config',
                                                 'DATE_TYPE',
                                                 self.config.getstr('config',
                                                                    'LOOP_BY',
                                                                    ''))

        start_dt, end_dt = get_start_and_end_times(self.config)
        if not start_dt:
            self.log_error('Could not get start and end times. '
                           'VALID_BEG/END or INIT_BEG/END must be set.')
        else:
            c_dict['DATE_BEG'] = start_dt.strftime('%Y%m%d')
            c_dict['DATE_END'] = end_dt.strftime('%Y%m%d')

        # read jobs from STAT_ANALYSIS_JOB<n> or legacy JOB_NAME/ARGS if unset
        c_dict['JOBS'] = self._read_jobs_from_config()

        # read all lists and check if field lists are all empty
        all_field_lists_empty = self.read_lists_from_config(c_dict)

        # read any [FCST/OBS]_VAR<n>_* variables if they are set
        c_dict['VAR_LIST'] = parse_var_list(self.config)

        c_dict['MODEL_INFO_LIST'] = self.parse_model_info()

        # if MODEL_LIST was not set, populate it from the model info list
        if not c_dict['MODEL_LIST'] and c_dict['MODEL_INFO_LIST']:
            self.logger.warning("MODEL_LIST was left blank, "
                                + "creating with MODELn information.")
            for model_info in c_dict['MODEL_INFO_LIST']:
                c_dict['MODEL_LIST'].append(model_info['name'])

        c_dict = self.set_lists_loop_or_group(c_dict)

        # read MET config settings that will apply to every run
        self.add_met_config(name='hss_ec_value',
                            data_type='float',
                            metplus_configs=['STAT_ANALYSIS_HSS_EC_VALUE'])

        return self.c_dict_error_check(c_dict, all_field_lists_empty)

    def _read_jobs_from_config(self):
        jobs = []
        job_indices = list(
            find_indices_in_config_section(r'STAT_ANALYSIS_JOB(\d+)$',
                                           self.config,
                                           index_index=1).keys()
        )

        if job_indices:
            for j_id in job_indices:
                job = self.config.getraw('config', f'STAT_ANALYSIS_JOB{j_id}')
                jobs.append(job)
        else:
            job_name = self.config.getraw('config', 'STAT_ANALYSIS_JOB_NAME')
            job_args = self.config.getraw('config', 'STAT_ANALYSIS_JOB_ARGS')
            jobs.append(f'-job {job_name} {job_args}')

        return jobs

    def c_dict_error_check(self, c_dict, all_field_lists_empty):

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

        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set STAT_ANALYSIS_OUTPUT_DIR")

        if not c_dict['JOBS']:
            self.log_error(
                "Must set at least one job with STAT_ANALYSIS_JOB<n>"
            )

        for conf_list in self.LIST_CATEGORIES:
            if not c_dict[conf_list]:
                self.log_error(f"Must set {conf_list} to run StatAnalysis")

        if not c_dict['DATE_TYPE']:
            self.log_error("DATE_TYPE or LOOP_BY must be set to run "
                           "StatAnalysis wrapper")

        if c_dict['DATE_TYPE'] not in ['VALID', 'INIT']:
            self.log_error("DATE_TYPE must be VALID or INIT")

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

    def read_lists_from_config(self, c_dict):
        """! Get list configuration variables and add to dictionary

         @param c_dict dictionary to hold output values
         @returns True if all field lists are empty or False if any are set
        """
        all_empty = True

        all_lists_to_read = self.EXPECTED_CONFIG_LISTS + self.LIST_CATEGORIES
        for conf_list in all_lists_to_read:
            if 'LEVEL_LIST' in conf_list:
                c_dict[conf_list] = (
                    self.get_level_list(conf_list.split('_')[0])
                )
            else:
                c_dict[conf_list] = self._format_conf_list(conf_list)

            # keep track if any field list is not empty
            if conf_list in self.FIELD_LISTS and c_dict[conf_list]:
                all_empty = False

        return all_empty

    def _format_conf_list(self, conf_list):
        items = getlist(
            self.config.getraw('config', conf_list, '')
        )

        # if list if empty or unset, check for {LIST_NAME}<n>
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
            return [self.format_thresh(item) for item in items]

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

    @staticmethod
    def list_to_str(list_of_values, add_quotes=True):
        """! Turn a list of values into a single string so it can be 
             set to an environment variable and read by the MET 
             stat_analysis config file.
                 
             Args:
                 @param list_of_values - list of values, i.e. ['value1', 'value2']
                 @param add_quotes if True, add quotation marks around values
                  default is True
  
             @returns string created from list_of_values with the values separated
               by commas, i.e. '"value1", "value2"'  or 1, 3 if add_quotes is False
        """
        # return empty string if list is empty
        if not list_of_values:
            return ''

        if add_quotes:
            return '"' + '", "'.join(list_of_values) + '"'

        return ', '.join(list_of_values)

    @staticmethod
    def _format_time_list(string_value, get_met_format, sort_list=True):
        out_list = []
        if not string_value:
            return []
        for time_string in string_value.split(','):
            time_string = time_string.strip()
            if get_met_format:
                value = time_string_to_met_time(time_string, default_unit='H',
                                                force_hms=True)
                out_list.append(value)
            else:
                delta_obj = get_relativedelta(time_string, default_unit='H')
                out_list.append(delta_obj)

        if sort_list:
            if get_met_format:
                out_list.sort(key=int)
            else:
                out_list.sort(key=ti_get_seconds_from_relativedelta)

        return out_list

    @staticmethod
    def _get_met_time_list(string_value, sort_list=True):
        return StatAnalysisWrapper._format_time_list(string_value,
                                                     get_met_format=True,
                                                     sort_list=sort_list)

    @staticmethod
    def _get_delta_list(string_value, sort_list=True):
        return StatAnalysisWrapper._format_time_list(string_value,
                                                     get_met_format=False,
                                                     sort_list=sort_list)

    def set_lists_loop_or_group(self, c_dict):
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

    @staticmethod
    def format_thresh(thresh_str):
        """! Format thresholds for file naming

        @param thresh_str string of the thresholds.
         Can be a comma-separated list, i.e. gt3,<=5.5, ==7

        @returns string of comma-separated list of the threshold(s) with
         letter format, i.e. gt3,le5.5,eq7
        """
        formatted_thresh_list = []
        # separate thresholds by comma and strip off whitespace around values
        thresh_list = [thresh.strip() for thresh in thresh_str.split(',')]
        for thresh in thresh_list:
            if not thresh:
                continue

            thresh_letter = util.comparison_to_letter_format(thresh)
            if thresh_letter:
                formatted_thresh_list.append(thresh_letter)

        return ','.join(formatted_thresh_list)

    def build_stringsub_dict(self, config_dict):
        """! Build a dictionary with list names, dates, and commonly
             used identifiers to pass to string_template_substitution.
            
        @param lists_to_loop list of all the list names whose items
         are being grouped together
        @param lists_to_group list of all the list names whose items
         are being looped over
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

        # Set string sub info from fcst/obs hour lists
        self._set_stringsub_hours(stringsub_dict,
                                  config_dict[f'FCST_{date_type}_HOUR'],
                                  config_dict[f'OBS_{date_type}_HOUR'])

        # handle opposite of date_type VALID if INIT and vice versa
        self._set_strinsub_other(stringsub_dict, date_type.lower(),
                                 config_dict['FCST_LEAD'],
                                 config_dict['OBS_LEAD'])

        # Set loop information
        for loop_or_group_list in self.EXPECTED_CONFIG_LISTS:
            list_name = loop_or_group_list.replace('_LIST', '')
            sub_name = list_name.lower()
            list_name_value = (
                config_dict[list_name].replace('"', '').replace(' ', '')
                                      .replace(',', '_').replace('*', 'ALL')
            )

            if list_name == 'MODEL':
                stringsub_dict[sub_name] = list_name_value
                stringsub_dict['obtype'] = (
                    config_dict['OBTYPE'].replace('"', '').replace(' ', '')
                )

            elif 'HOUR' in list_name:
                delta_list = self._get_delta_list(config_dict[list_name])
                if not delta_list:
                    stringsub_dict[sub_name] = list_name_value
                    # TODO: should this be set to 0:0:0 to 23:59:59?
                    stringsub_dict[sub_name + '_beg'] = relativedelta()
                    stringsub_dict[sub_name + '_end'] = (
                        relativedelta(hours=+23, minutes=+59, seconds=+59)
                    )
                    continue
                if len(delta_list) == 1:
                    stringsub_dict[sub_name] = delta_list[0]
                else:
                    stringsub_dict[sub_name] = (
                        '_'.join(self._get_met_time_list(config_dict[list_name]))
                    )

                stringsub_dict[sub_name + '_beg'] = delta_list[0]
                stringsub_dict[sub_name + '_end'] = delta_list[-1]

                if 'FCST' in list_name:
                    check_list = config_dict[list_name.replace('FCST',
                                                               'OBS')]
                elif 'OBS' in list_name:
                    check_list = config_dict[list_name.replace('OBS',
                                                               'FCST')]
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

            elif 'LEAD' in list_name:
                lead_list = self._get_met_time_list(config_dict[list_name])

                if not lead_list:
                    continue

                # if multiple leads are specified, format lead info
                # using met time notation separated by underscore
                if len(lead_list) > 1:
                    stringsub_dict[sub_name] = (
                        '_'.join(lead_list)
                    )
                    continue

                stringsub_dict[sub_name] = lead_list[0]

                lead_rd = self._get_delta_list(config_dict[list_name])[0]
                total_sec = ti_get_seconds_from_relativedelta(lead_rd)
                stringsub_dict[sub_name+'_totalsec'] = str(total_sec)

                stringsub_dict[f'{sub_name}_hour'] = lead_list[0][:-4]
                stringsub_dict[f'{sub_name}_min'] = lead_list[0][-4:-2]
                stringsub_dict[f'{sub_name}_sec'] = lead_list[0][-2:]

                if 'FCST' in list_name:
                    check_list = config_dict[list_name.replace('FCST', 'OBS')]
                elif 'OBS' in list_name:
                    check_list = config_dict[list_name.replace('OBS', 'FCST')]
                if not check_list or config_dict[list_name] == check_list:
                    stringsub_dict['lead'] = stringsub_dict[sub_name]
                    stringsub_dict['lead_hour'] = (
                        stringsub_dict[sub_name+'_hour']
                    )
                    stringsub_dict['lead_min'] = (
                        stringsub_dict[sub_name+'_min']
                    )
                    stringsub_dict['lead_sec'] = (
                        stringsub_dict[sub_name+'_sec']
                    )
                    stringsub_dict['lead_totalsec'] = (
                        stringsub_dict[sub_name+'_totalsec']
                    )
            else:
                stringsub_dict[sub_name] = list_name_value

        # Some lines for debugging if needed in future
        #for key, value in stringsub_dict.items():
        #    self.logger.debug("{} ({})".format(key, value))
        return stringsub_dict

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
            fcst_hour_list = self._get_delta_list(fcst_hour_str)
        else:
            fcst_hour_list = None

        if obs_hour_str:
            obs_hour_list = self._get_delta_list(obs_hour_str)
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

        if hour_list:
            sub_dict[f'{prefix}_beg'] = (
                datetime.datetime.strptime(date_beg, '%Y%m%d') + hour_list[0]
            )
            sub_dict[f'{prefix}_end'] = (
                datetime.datetime.strptime(date_end, '%Y%m%d') + hour_list[-1]
            )
            if sub_dict[f'{prefix}_beg'] == sub_dict[f'{prefix}_end']:
                sub_dict[prefix] = sub_dict[f'{prefix}_beg']

            return

        # if fcst hour list is not set, use date beg 000000-235959 as
        # fcst_{date_type}_beg/end
        sub_dict[f'{prefix}_beg'] = (
            datetime.datetime.strptime(
                date_beg + '000000', '%Y%m%d%H%M%S'
            )
        )
        sub_dict[f'{prefix}_end'] = (
            datetime.datetime.strptime(
                date_end + '235959', '%Y%m%d%H%M%S'
            )
        )

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
            fcst_lead_list = self._get_delta_list(fcst_lead_str)
        else:
            fcst_lead_list = None

        if obs_lead_str:
            obs_lead_list = self._get_delta_list(obs_lead_str)
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

    def get_output_filename(self, output_type, filename_template,
                            filename_type,
                            lists_to_loop,config_dict):
        """! Create a file name for stat_analysis output.
             
             Args:
                 output_type       - string for the type of
                                     stat_analysis output, either 
                                     dump_row or out_stat
                 filename_template - string of the template to be used 
                                     to create the file name
                 filename_type     - string of the source of the
                                     template being used, either 
                                     default or user
                 lists_to_loop     - list of all the list names whose
                                     items are being grouped together
                 config_dict       - dictionary containing the
                                     configuration information

             Returns:
                 output_filename   - string of the filled file name
                                     template
        """
        date_beg = self.c_dict['DATE_BEG']
        date_end = self.c_dict['DATE_END']
        date_type = self.c_dict['DATE_TYPE']

        stringsub_dict = self.build_stringsub_dict(config_dict)

        if filename_type == 'default':

            if date_beg == date_end:
                filename_template = (
                    filename_template+date_type.lower()+date_beg
                )
            else:
                filename_template = (
                    filename_template+date_type.lower()+
                    date_beg+'to'+date_end
                )
            for loop_list in lists_to_loop:
                if loop_list != 'MODEL_LIST':
                    list_name = loop_list.replace('_LIST', '')
                    if 'HOUR' in list_name:
                        value = self._get_met_time_list(config_dict[list_name])[0]
                        filename_template = (
                            filename_template+'_'
                            +list_name.replace('_', '').lower()
                            +value+'Z'
                        )
                    else:
                        filename_template = (
                            filename_template+'_'
                            +list_name.replace('_', '').lower()
                            +config_dict[list_name].replace('"', '')
                        )
            filename_template += '_' + output_type + '.stat'

        self.logger.debug("Building "+output_type+" filename from "
                          +filename_type+" template: "+filename_template)

        output_filename = do_string_sub(filename_template,
                                        **stringsub_dict)
        return output_filename

    def get_lookin_dir(self, dir_path, config_dict):
        """!Fill in necessary information to get the path to
            the lookin directory to pass to stat_analysis.
             
             Args:
                 dir_path          - string of the user provided
                                     directory path
                 lists_to_loop     - list of all the list names whose
                                     items are being grouped together
                 lists_to group    - list of all the list names whose
                                     items are being looped over
                 config_dict       - dictionary containing the
                                     configuration information

             Returns:
                 lookin_dir        - string of the filled directory
                                     from dir_path
        """
        stringsub_dict = self.build_stringsub_dict(config_dict)
        dir_path_filled = do_string_sub(dir_path,
                                        **stringsub_dict)

        all_paths = []
        for one_path in dir_path_filled.split(','):
            if '*' in one_path:
                self.logger.debug(f"Expanding wildcard path: {one_path}")
                expand_path = glob.glob(one_path.strip())
                if not expand_path:
                    self.logger.warning(f"Wildcard expansion found no matches")
                    continue
                all_paths.extend(sorted(expand_path))
            else:
               all_paths.append(one_path.strip())
        return ' '.join(all_paths)

    def format_valid_init(self, config_dict):
        """! Format the valid and initialization dates and
             hours for the MET stat_analysis config file.

             Args:
                 config_dict - dictionary containing the
                               configuration information

             Returns:
                 config_dict - dictionary containing the
                               edited configuration information
                               for valid and initialization dates
                               and hours 
        """
        date_beg = self.c_dict['DATE_BEG']
        date_end = self.c_dict['DATE_END']
        date_type = self.c_dict['DATE_TYPE']

        for list_name in self.FORMAT_LISTS:
            list_name = list_name.replace('_LIST', '')
            values = self._get_met_time_list(config_dict.get(list_name, ''))
            values = [f'"{item}"' for item in values]
            config_dict[list_name] = ', '.join(values)

        fcst_valid_hour_list = config_dict['FCST_VALID_HOUR'].split(', ')
        fcst_init_hour_list = config_dict['FCST_INIT_HOUR'].split(', ')
        obs_valid_hour_list = config_dict['OBS_VALID_HOUR'].split(', ')
        obs_init_hour_list = config_dict['OBS_INIT_HOUR'].split(', ')
        nfcst_valid_hour = len(fcst_valid_hour_list)
        nfcst_init_hour = len(fcst_init_hour_list)
        nobs_valid_hour = len(obs_valid_hour_list)
        nobs_init_hour = len(obs_init_hour_list)
        if nfcst_valid_hour > 1:
            if date_type == 'VALID':
                fcst_valid_hour_beg = fcst_valid_hour_list[0].replace('"','')
                fcst_valid_hour_end = fcst_valid_hour_list[-1].replace('"','')
                config_dict['FCST_VALID_BEG'] = (
                    str(date_beg)+'_'+fcst_valid_hour_beg
                )
                config_dict['FCST_VALID_END'] = (
                    str(date_end)+'_'+fcst_valid_hour_end
                )
            elif date_type == 'INIT':
                config_dict['FCST_VALID_BEG'] = ''
                config_dict['FCST_VALID_END'] = ''
        elif nfcst_valid_hour == 1 and fcst_valid_hour_list != ['']:
            fcst_valid_hour_now = fcst_valid_hour_list[0].replace('"','')
            config_dict['FCST_VALID_HOUR'] = '"'+fcst_valid_hour_now+'"'
            if date_type == 'VALID':
                config_dict['FCST_VALID_BEG'] = (
                    str(date_beg)+'_'+fcst_valid_hour_now
                )
                config_dict['FCST_VALID_END'] = (
                    str(date_end)+'_'+fcst_valid_hour_now
                )
            elif date_type == 'INIT':
                config_dict['FCST_VALID_BEG'] = ''
                config_dict['FCST_VALID_END'] = ''
        else:
            config_dict['FCST_VALID_BEG'] = ''
            config_dict['FCST_VALID_END'] = ''
            config_dict['FCST_VALID_HOUR'] = ''
        if nfcst_init_hour > 1:
            if date_type == 'VALID':
                config_dict['FCST_INIT_BEG'] = ''
                config_dict['FCST_INIT_END'] = ''
            elif date_type == 'INIT':
                fcst_init_hour_beg = fcst_init_hour_list[0].replace('"','')
                fcst_init_hour_end = fcst_init_hour_list[-1].replace('"','')
                config_dict['FCST_INIT_BEG'] = (
                    str(date_beg)+'_'+fcst_init_hour_beg
                )
                config_dict['FCST_INIT_END'] = (
                    str(date_end)+'_'+fcst_init_hour_end
                )
        elif nfcst_init_hour == 1 and fcst_init_hour_list != ['']:
            fcst_init_hour_now = fcst_init_hour_list[0].replace('"','')
            config_dict['FCST_INIT_HOUR'] = '"'+fcst_init_hour_now+'"'
            if date_type == 'VALID':
                config_dict['FCST_INIT_BEG'] = ''
                config_dict['FCST_INIT_END'] = ''
            elif date_type == 'INIT':
                config_dict['FCST_INIT_BEG'] = (
                    str(date_beg)+'_'+fcst_init_hour_now
                )
                config_dict['FCST_INIT_END'] = (
                    str(date_end)+'_'+fcst_init_hour_now
                )
        else:
            config_dict['FCST_INIT_BEG'] = ''
            config_dict['FCST_INIT_END'] = ''
            config_dict['FCST_INIT_HOUR'] = ''
        if nobs_valid_hour > 1:
            if date_type == 'VALID':
                obs_valid_hour_beg = obs_valid_hour_list[0].replace('"','')
                obs_valid_hour_end = obs_valid_hour_list[-1].replace('"','')
                config_dict['OBS_VALID_BEG'] = (
                    str(date_beg)+'_'+obs_valid_hour_beg
                )
                config_dict['OBS_VALID_END'] = (
                    str(date_end)+'_'+obs_valid_hour_end
                )
            elif date_type == 'INIT':
                config_dict['OBS_VALID_BEG'] = ''
                config_dict['OBS_VALID_END'] = ''
        elif nobs_valid_hour == 1 and obs_valid_hour_list != ['']:
            obs_valid_hour_now = obs_valid_hour_list[0].replace('"','')
            config_dict['OBS_VALID_HOUR'] = '"'+obs_valid_hour_now+'"'
            if date_type == 'VALID':
                config_dict['OBS_VALID_BEG'] = (
                     str(date_beg)+'_'+obs_valid_hour_now
                )
                config_dict['OBS_VALID_END'] = (
                     str(date_end)+'_'+obs_valid_hour_now
                )
            elif date_type == 'INIT':
                config_dict['OBS_VALID_BEG'] = ''
                config_dict['OBS_VALID_END'] = ''
        else:
            config_dict['OBS_VALID_BEG'] = ''
            config_dict['OBS_VALID_END'] = ''
            config_dict['OBS_VALID_HOUR'] = ''
        if nobs_init_hour > 1:
            if date_type == 'VALID':
                config_dict['OBS_INIT_BEG'] = ''
                config_dict['OBS_INIT_END'] = ''
            elif date_type == 'INIT':
                obs_init_hour_beg = obs_init_hour_list[0].replace('"','')
                obs_init_hour_end = obs_init_hour_list[-1].replace('"','')
                config_dict['OBS_INIT_BEG'] = (
                    str(date_beg)+'_'+obs_init_hour_beg
                )
                config_dict['OBS_INIT_END'] = (
                    str(date_end)+'_'+obs_init_hour_end
                )
        elif nobs_init_hour == 1 and obs_init_hour_list != ['']:
            obs_init_hour_now = obs_init_hour_list[0].replace('"','')
            config_dict['OBS_INIT_HOUR'] = '"'+obs_init_hour_now+'"'
            if date_type == 'VALID':
                config_dict['OBS_INIT_BEG'] = ''
                config_dict['OBS_INIT_END'] = ''
            elif date_type == 'INIT':
                config_dict['OBS_INIT_BEG'] = (
                    str(date_beg)+'_'+obs_init_hour_now
                )
                config_dict['OBS_INIT_END'] = (
                    str(date_end)+'_'+obs_init_hour_now
                )
        else:
            config_dict['OBS_INIT_BEG'] = ''
            config_dict['OBS_INIT_END'] = ''
            config_dict['OBS_INIT_HOUR'] = ''
        return config_dict

    def parse_model_info(self):
        """! Parse for model information.
             
             Args:
                
             Returns:
                 model_list - list of dictionaries containing
                              model information
        """
        model_info_list = []
        model_indices = list(
            find_indices_in_config_section(r'MODEL(\d+)$',
                                           self.config,
                                           index_index=1).keys()
        )
        for m in model_indices:
            model_name = self.config.getstr('config', f'MODEL{m}')
            model_reference_name = self.config.getstr('config',
                                                      f'MODEL{m}_REFERENCE_NAME',
                                                      model_name)
            model_dir = self.config.getraw('dir',
                                           f'MODEL{m}_STAT_ANALYSIS_LOOKIN_DIR')
            if not model_dir:
                self.log_error(f"MODEL{m}_STAT_ANALYSIS_LOOKIN_DIR must be set "
                               f"if MODEL{m} is set.")
                return None, None

            model_obtype = self.config.getstr('config', f'MODEL{m}_OBTYPE', '')
            if not model_obtype:
                self.log_error(f"MODEL{m}_OBTYPE must be set "
                               f"if MODEL{m} is set.")
                return None, None

            for output_type in ['DUMP_ROW', 'OUT_STAT']:
                # if MODEL<n>_STAT_ANALYSIS_<output_type>_TEMPLATE is set, use that
                model_filename_template = (
                    self.config.getraw('filename_templates',
                                       'MODEL'+m+'_STAT_ANALYSIS_'
                                       +output_type+'_TEMPLATE')
                )

                # if not set, use STAT_ANALYSIS_<output_type>_TEMPLATE
                if not model_filename_template:
                    model_filename_template = (
                        self.config.getraw('filename_templates',
                                           'STAT_ANALYSIS_'
                                           + output_type + '_TEMPLATE')
                    )

                if not model_filename_template:
                     model_filename_template = '{model?fmt=%s}_{obtype?fmt=%s}_'
                     model_filename_type = 'default'
                else:
                     model_filename_type = 'user'

                if output_type == 'DUMP_ROW':
                     model_dump_row_filename_template = (
                         model_filename_template
                     )
                     model_dump_row_filename_type = model_filename_type
                elif output_type == 'OUT_STAT':
                    model_out_stat_filename_template = (
                        model_filename_template
                    )
                    model_out_stat_filename_type = model_filename_type

            mod = {}
            mod['name'] = model_name
            mod['reference_name'] = model_reference_name
            mod['dir'] = model_dir
            mod['obtype'] = model_obtype
            mod['dump_row_filename_template'] = (
                model_dump_row_filename_template
            )
            mod['dump_row_filename_type'] = model_dump_row_filename_type
            mod['out_stat_filename_template'] = (
                model_out_stat_filename_template
            )
            mod['out_stat_filename_type'] = model_out_stat_filename_type
            model_info_list.append(mod)

        return model_info_list

    def get_level_list(self, data_type):
        """!Read forecast or observation level list from config.
            Format list items to match the format expected by
            StatAnalysis by removing parenthesis and any quotes,
            then adding back single quotes
            Args:
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

    def process_job_args(self, job_type, job, model_info,
                         lists_to_loop_items, runtime_settings_dict):

        output_template = (
            model_info[f'{job_type}_filename_template']
        )
        filename_type = (
            model_info[f'{job_type}_filename_type']
        )

        output_filename = (
            self.get_output_filename(job_type,
                                     output_template,
                                     filename_type,
                                     lists_to_loop_items,
                                     runtime_settings_dict)
        )
        output_file = os.path.join(self.c_dict['OUTPUT_DIR'],
                                   output_filename)

        # substitute output filename in JOBS line
        job = job.replace(f'[{job_type}_file]', output_file)
        job = job.replace(f'[{job_type}_filename]', output_file)

        # add output file path to runtime_settings_dict
        runtime_settings_dict[f'{job_type.upper()}_FILENAME'] = output_file

        return job

    def get_all_runtime_settings(self):
        runtime_settings_dict_list = []
        c_dict_list = self.get_c_dict_list()
        for c_dict in c_dict_list:
            runtime_settings = self.get_runtime_settings(c_dict)
            runtime_settings_dict_list.extend(runtime_settings)

        # Loop over run settings.
        formatted_runtime_settings_dict_list = []
        for runtime_settings_dict in runtime_settings_dict_list:
            loop_lists = c_dict['LOOP_LIST_ITEMS']

            # Set up stat_analysis -lookin argument, model and obs information
            # and stat_analysis job.
            model_info = self.get_model_obtype_and_lookindir(runtime_settings_dict)
            if model_info is None:
                return None

            runtime_settings_dict['JOBS'] = (
                self.get_job_info(model_info, runtime_settings_dict,
                                  loop_lists)
            )

            # get -out argument if set
            if self.c_dict['OUTPUT_TEMPLATE']:
                output_filename = (
                    self.get_output_filename('output',
                                             self.c_dict['OUTPUT_TEMPLATE'],
                                             'user',
                                             loop_lists,
                                             runtime_settings_dict)
                )
                output_file = os.path.join(self.c_dict['OUTPUT_DIR'],
                                           output_filename)

                # add output file path to runtime_settings_dict
                runtime_settings_dict['OUTPUT_FILENAME'] = output_file

            # Set up forecast and observation valid
            # and initialization time information.
            runtime_settings_dict = (
                self.format_valid_init(runtime_settings_dict)
            )
            formatted_runtime_settings_dict_list.append(runtime_settings_dict)

        return formatted_runtime_settings_dict_list

    def get_runtime_settings(self, c_dict):
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

    def get_c_dict_list(self):
        """! Build list of config dictionaries for each field
        name/level/threshold specified by the [FCST/OBS]_VAR<n>_* config vars.
        If field information was specified in the field lists
        [FCST_OBS]_[VAR/UNITS/THRESH/LEVEL]_LIST instead of these
        variables, then return a list with a single item that is a deep copy
        of the self.c_dict.

        @returns list of dictionaries for each field to process
        """
        # if fields were not specified with [FCST/OBS]_VAR<n>_* variables
        # return and array with only self.c_dict
        if not self.c_dict['VAR_LIST']:
            c_dict = {}
            self.add_other_lists_to_c_dict(c_dict)
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
            if run_fourier:
                fourier_wave_num_pairs = getlist(
                    self.config.getstr('config',
                                       f"VAR{var_info['index']}_WAVE_NUM_LIST",
                                       '')
                )
            else:
                fourier_wave_num_pairs = ['']

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
                        thresh_formatted = self.format_thresh(fcst_thresh)
                        c_dict['FCST_THRESH_LIST'].append(thresh_formatted)

                    if obs_thresh:
                        thresh_formatted = self.format_thresh(obs_thresh)
                        c_dict['OBS_THRESH_LIST'].append(thresh_formatted)

                    if fcst_units:
                        c_dict['FCST_UNITS_LIST'].append(f'"{fcst_units}"')
                    if obs_units:
                        c_dict['OBS_UNITS_LIST'].append(f'"{obs_units}"')

                    c_dict['run_fourier'] = run_fourier
                    if pair:
                        c_dict['INTERP_MTHD_LIST'] = ['WV1_' + pair]

                    self.add_other_lists_to_c_dict(c_dict)

                    c_dict_list.append(c_dict)

        return c_dict_list

    def _get_field_units(self, index):
        """! Get units of fcst and obs fields if set based on VAR<n> index

         @param index VAR<n> index corresponding to other [FCST/OBS] info
         @returns tuple containing forecast and observation units respectively
        """
        fcst_units = self.config.getstr('config',
                                        f'FCST_VAR{index}_UNITS',
                                        '')
        obs_units = self.config.getstr('config',
                                       f'OBS_VAR{index}_UNITS',
                                       '')
        if not obs_units and fcst_units:
            obs_units = fcst_units
        if not fcst_units and obs_units:
            fcst_units = obs_units

        return fcst_units, obs_units

    def add_other_lists_to_c_dict(self, c_dict):
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

    def get_model_obtype_and_lookindir(self, runtime_settings_dict):
        """! Reads through model info dictionaries for given run.
        Sets lookindir command line argument. Sets MODEL and OBTYPE values in
        runtime setting dictionary.

        @param runtime_settings_dict dictionary with all settings used in run
        @returns last model info dictionary is successful, None if not.
        """
        lookin_dirs = []
        model_list = []
        reference_list = []
        obtype_list = []
        dump_row_filename_list = []
        # get list of models to process
        models_to_run = [
            model.strip().replace('"', '')
            for model in runtime_settings_dict['MODEL'].split(',')
        ]
        for model_info in self.c_dict['MODEL_INFO_LIST']:
            # skip model if not in list of models to process
            if model_info['name'] not in models_to_run:
                continue

            model_list.append(model_info['name'])
            reference_list.append(model_info['reference_name'])
            obtype_list.append(model_info['obtype'])
            dump_row_filename_list.append(
                model_info['dump_row_filename_template']
            )
            # set MODEL and OBTYPE to single item to find lookin dir
            runtime_settings_dict['MODEL'] = f'"{model_info["name"]}"'
            runtime_settings_dict['OBTYPE'] = f'"{model_info["obtype"]}"'

            lookin_dirs.append(
                self.get_lookin_dir(model_info['dir'], runtime_settings_dict)
            )

        # set lookin dir command line argument
        runtime_settings_dict['LOOKIN_DIR'] = ' '.join(lookin_dirs)

        # error and return None if lookin dir is empty
        if not runtime_settings_dict['LOOKIN_DIR']:
            self.log_error("No value found for lookin dir")
            return None

        if not model_list or not obtype_list:
            self.log_error("Could not find model or obtype to process")
            return None

        # set values in runtime settings dict for model and obtype
        runtime_settings_dict['MODEL'] = self.list_to_str(model_list)
        runtime_settings_dict['MODEL_REFERENCE_NAME'] = (
            self.list_to_str(reference_list)
        )
        runtime_settings_dict['OBTYPE'] = self.list_to_str(obtype_list)

        # return last model info dict used
        return model_info

    def get_job_info(self, model_info, runtime_settings_dict, loop_lists):
        """! Get job information and concatenate values into a string
             @params model_info model information to use to determine output file paths
             @params runtime_settings_dict dictionary containing all settings used in next run
             @returns string containing job information to pass to StatAnalysis config file
        """
        jobs = []
        for job in self.c_dict['JOBS']:
            for job_type in ['dump_row', 'out_stat']:
                if f"-{job_type}" in job:
                    job = self.process_job_args(job_type,
                                                job,
                                                model_info,
                                                loop_lists,
                                                runtime_settings_dict,
                                                )

            jobs.append(job)

        return jobs

    def run_stat_analysis(self):
        """! This runs stat_analysis over a period of valid
             or initialization dates for a job defined by
             the user.
        """
        runtime_settings_dict_list = self.get_all_runtime_settings()
        if not runtime_settings_dict_list:
            self.log_error('Could not get runtime settings dict list')
            return False

        self.run_stat_analysis_job(runtime_settings_dict_list)

        return True

    def run_stat_analysis_job(self, runtime_settings_dict_list):
        """! Sets environment variables need to run StatAnalysis jobs
             and calls the tool for each job.

             Args:
                 @param runtime_settings_dict_list list of dictionaries
                  containing information needed to run a StatAnalysis job
        """
        for runtime_settings_dict in runtime_settings_dict_list:
            if not self.create_output_directories(runtime_settings_dict):
                continue

            # Set environment variables and run stat_analysis.
            for name, value in runtime_settings_dict.items():
                self.add_env_var(name, value)

            self.job_args = None
            # set METPLUS_ env vars for MET config file to be consistent
            # with other wrappers
            mp_lists = ['MODEL',
                        'DESC',
                        'FCST_LEAD',
                        'OBS_LEAD',
                        'FCST_VALID_HOUR',
                        'OBS_VALID_HOUR',
                        'FCST_INIT_HOUR',
                        'OBS_INIT_HOUR',
                        'FCST_VAR',
                        'OBS_VAR',
                        'FCST_UNITS',
                        'OBS_UNITS',
                        'FCST_LEVEL',
                        'OBS_LEVEL',
                        'OBTYPE',
                        'VX_MASK',
                        'INTERP_MTHD',
                        'INTERP_PNTS',
                        'FCST_THRESH',
                        'OBS_THRESH',
                        'COV_THRESH',
                        'ALPHA',
                        'LINE_TYPE'
                        ]
            for mp_list in mp_lists:
                if not runtime_settings_dict.get(mp_list, ''):
                    continue
                value = (f"{mp_list.lower()} = "
                         f"[{runtime_settings_dict.get(mp_list, '')}];")
                self.env_var_dict[f'METPLUS_{mp_list}'] = value

            mp_items = ['FCST_VALID_BEG',
                        'FCST_VALID_END',
                        'OBS_VALID_BEG',
                        'OBS_VALID_END',
                        'FCST_INIT_BEG',
                        'FCST_INIT_END',
                        'OBS_INIT_BEG',
                        'OBS_INIT_END',
                        ]
            for mp_item in mp_items:
                if not runtime_settings_dict.get(mp_item, ''):
                    continue
                value = remove_quotes(runtime_settings_dict.get(mp_item,
                                                                     ''))
                value = (f"{mp_item.lower()} = \"{value}\";")
                self.env_var_dict[f'METPLUS_{mp_item}'] = value

            value = f'jobs = ["'
            value += '","'.join(runtime_settings_dict['JOBS'])
            value += '"];'
            self.env_var_dict[f'METPLUS_JOBS'] = value

            # send environment variables to logger
            self.set_environment_variables()

            # set lookin dir
            self.logger.debug(f"Setting -lookin dir to {runtime_settings_dict['LOOKIN_DIR']}")
            self.lookindir = runtime_settings_dict['LOOKIN_DIR']
            self.job_args = runtime_settings_dict['JOBS'][0]

            # set -out file path if requested, value will be set to None if not
            self.c_dict['OUTPUT_FILENAME'] = (
                runtime_settings_dict.get('OUTPUT_FILENAME')
            )

            self.build()

            self.clear()

    def create_output_directories(self, runtime_settings_dict):
        """! Check if output filename is set for dump_row or out_stat. If set,
             Check if the file already exists and if it should be skipped.

             @param runtime_settings_dict dictionary containing filename info
             @returns True if job should be run, False if it should be skipped
        """
        run_job = True
        for job_type in ['dump_row', 'out_stat', 'output']:
            output_path = (
                runtime_settings_dict.get(f'{job_type.upper()}_FILENAME')
            )
            if output_path:
                if not self.find_and_check_output_file(
                        output_path_template=output_path):
                    run_job = False

        return run_job

    def run_all_times(self):
        self.run_stat_analysis()
        return self.all_commands

    def run_at_time(self, input_dict):
        loop_by = self.c_dict['DATE_TYPE']
        run_date = input_dict[loop_by.lower()].strftime('%Y%m%d')
        self.c_dict['DATE_BEG'] = run_date
        self.c_dict['DATE_END'] = run_date
        self.run_stat_analysis()
