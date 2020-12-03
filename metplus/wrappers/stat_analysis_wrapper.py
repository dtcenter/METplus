'''
Program Name: stat_analysis_wrapper.py
Contact(s): Mallory Row
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

from ..util import met_util as util
from ..util import do_string_sub
from . import CommandBuilder

class StatAnalysisWrapper(CommandBuilder):
    """! Wrapper to the MET tool stat_analysis which is used to filter 
         and summarize data from MET's point_stat, grid_stat, 
         ensemble_stat, and wavelet_stat
    """

    field_lists = ['FCST_VAR_LIST',
                   'OBS_VAR_LIST',
                   'FCST_UNITS_LIST',
                   'OBS_UNITS_LIST',
                   'FCST_THRESH_LIST',
                   'OBS_THRESH_LIST',
                   'FCST_LEVEL_LIST',
                   'OBS_LEVEL_LIST',
                   ]

    format_lists = ['FCST_VALID_HOUR_LIST',
                    'FCST_INIT_HOUR_LIST',
                    'OBS_VALID_HOUR_LIST',
                    'OBS_INIT_HOUR_LIST',
                    'FCST_LEAD_LIST',
                    'OBS_LEAD_LIST',
                    ]

    expected_config_lists = ['MODEL_LIST',
                             'DESC_LIST',
                             'VX_MASK_LIST',
                             'INTERP_MTHD_LIST',
                             'INTERP_PNTS_LIST',
                             'COV_THRESH_LIST',
                             'ALPHA_LIST',
                             'LINE_TYPE_LIST',
                             ] + format_lists + field_lists

    force_group_for_make_plots_lists = ['MODEL_LIST',
                                        'FCST_LEAD_LIST',
                                        'OBS_LEAD_LIST',
                                        'FCST_LEVEL_LIST',
                                        'OBS_LEVEL_LIST',
                                        'FCST_THRESH_LIST',
                                        'OBS_THRESH_LIST',
                                        'FCST_UNITS_LIST',
                                        'OBS_UNITS_LIST',
                                       ]

    list_categories = ['GROUP_LIST_ITEMS', 'LOOP_LIST_ITEMS']
    list_categories_make_plots = ['GROUP_LIST_ITEMS_MAKE_PLOTS', 'LOOP_LIST_ITEMS_MAKE_PLOTS']
    # what is the used for? these are not formatted later
    format_later_list = [
        'MODEL_LIST', 'FCST_VALID_HOUR_LIST', 'OBS_VALID_HOUR_LIST',
        'FCST_INIT_HOUR_LIST', 'OBS_INIT_HOUR_LIST'
    ]

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     'stat_analysis')
        self.app_name = os.path.basename(self.app_path)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def get_command(self):

        cmd = self.app_path
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
        c_dict['LOOP_ORDER'] = self.config.getstr('config', 'LOOP_ORDER')
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 
                                                   'STAT_ANALYSIS_CONFIG_FILE',
                                                   '')

        c_dict['OUTPUT_DIR'] = self.config.getdir('STAT_ANALYSIS_OUTPUT_DIR',
                                                  '')

        c_dict['DATE_TYPE'] = self.config.getstr('config',
                                                 'DATE_TYPE',
                                                 self.config.getstr('config',
                                                                    'LOOP_BY',
                                                                    ''))

        for time_conf in ['VALID_BEG', 'VALID_END', 'INIT_BEG', 'INIT_END']:
            c_dict[time_conf] = self.config.getstr('config', time_conf, '')

        for job_conf in ['JOB_NAME', 'JOB_ARGS']:
            c_dict[job_conf] = self.config.getstr('config',
                                                   f'STAT_ANALYSIS_{job_conf}',
                                                   '')

        # read in all lists except field lists, which will be read in afterwards and checked
        all_lists_to_read = self.expected_config_lists + self.list_categories
        non_field_lists = [conf_list for
                           conf_list in all_lists_to_read
                           if conf_list not in self.field_lists]
        for conf_list in non_field_lists:
            c_dict[conf_list] = util.getlist(
                self.config.getstr('config', conf_list, '')
            )

            # if list in format lists, zero pad value to be at least 2
            # digits, then add 4 zeros
            if conf_list in self.format_lists:
                c_dict[conf_list] = (
                    [value.zfill(2).ljust(4 + len(value.zfill(2)), '0')
                     for value in c_dict[conf_list]]
                )

        # read all field lists and check if they are all empty
        c_dict['all_field_lists_empty'] = self.read_field_lists_from_config(c_dict)

        # check if MakePlots is in process list and set boolean
        # MakePlots is removed from the list in met_util.get_process_list, so
        # need to read the conf value again
        self.runMakePlots = 'MakePlots' in self.config.getstr('config', 'PROCESS_LIST')
        if self.runMakePlots:
            # only import MakePlots wrappers if it will be used
            from .make_plots_wrapper import MakePlotsWrapper, wrapper_cannot_run
            if wrapper_cannot_run:
                self.log_error("Cannot import MakePlots wrapper! Requires pandas and numpy")
            else:
                self.check_MakePlots_config(c_dict)

                # create MakePlots wrapper instance
                self.MakePlotsWrapper = MakePlotsWrapper(self.config)
                if not self.MakePlotsWrapper.isOK:
                    self.log_error("MakePlotsWrapper was not initialized correctly.")

        c_dict['VAR_LIST'] = util.parse_var_list(self.config)

        c_dict['MODEL_INFO_LIST'] = self.parse_model_info()
        if not c_dict['MODEL_LIST'] and c_dict['MODEL_INFO_LIST']:
                self.logger.warning("MODEL_LIST was left blank, "
                                    + "creating with MODELn information.")
                for model_info in c_dict['MODEL_INFO_LIST']:
                    c_dict['MODEL_LIST'].append(model_info['name'])

        c_dict = self.set_lists_loop_or_group(c_dict)

        return self.c_dict_error_check(c_dict)

    def c_dict_error_check(self, c_dict):

        if not c_dict.get('CONFIG_FILE'):
            self.logger.info("STAT_ANALYSIS_CONFIG_FILE not set. Passing job arguments to "
                             "stat_analysis directly on the command line. This will bypass "
                             "any filtering done unless you add the arguments to "
                             "STAT_ANALYSIS_JOB_ARGS")

        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set STAT_ANALYSIS_OUTPUT_DIR")

        for job_conf in ['JOB_NAME', 'JOB_ARGS']:
            if not c_dict[job_conf]:
                self.log_error(f"Must set STAT_ANALYSIS_{job_conf} to run StatAnalysis")

        for conf_list in self.list_categories:
            if not c_dict[conf_list]:
                self.log_error(f"Must set {conf_list} to run StatAnalysis")

        if not c_dict['DATE_TYPE']:
            self.log_error("DATE_TYPE or LOOP_BY must be set to run "
                           "StatAnalysis wrapper")

        if c_dict['DATE_TYPE'] not in ['VALID', 'INIT']:
            self.log_error("DATE_TYPE must be VALID or INIT")

        # if var list is set and field lists are not all empty, error
        if c_dict['VAR_LIST'] and not c_dict['all_field_lists_empty']:
            self.log_error("Field information defined in both "
                           "[FCST/OBS]_VAR_LIST and "
                           "[FCST/OBS]_VAR<n>_[NAME/LEVELS]. Use "
                           "one or the other formats to run")

        # if no var list is found, other lists must be set to run MakePlots
        elif not c_dict['VAR_LIST'] and c_dict['all_field_lists_empty'] and self.runMakePlots:
            self.log_error("No field information found. Must define fields to "
                           "process with either [FCST/OBS]_VAR_LIST or "
                           "[FCST/OBS]_VAR<n>_[NAME/LEVELS]")

        # if MODEL_LIST was not set in config, populate it from the model info list
        # if model info list is also not set, report and error
        if not c_dict['MODEL_LIST'] and not c_dict['MODEL_INFO_LIST']:
            self.log_error("No model information was found.")

        # if running MakePlots and model list in group list, error and exit
        if self.runMakePlots:
            if 'MODEL_LIST' in c_dict['GROUP_LIST_ITEMS']:
                self.log_error("Cannot group MODELS if running MakePlots. Remove "
                               "MODEL_LIST from LOOP_LIST_ITEMS")

            if len(c_dict['MODEL_LIST']) > 8:
                self.log_error("Number of models for plotting limited to 8.")

#        self.check_dump_row_templates_for_plotting()

        # set forMakePlots to False to begin. When gathering settings to
        # send to MakePlots wrapper, this will be set to True
        self.forMakePlots = False

        return c_dict

    def read_field_lists_from_config(self, field_dict):
        """! Get field list configuration variables and add to dictionary
             @param field_dict dictionary to hold output values
             @returns True if all lists are empty or False if any have a value"""
        all_empty = True
        for field_list in self.field_lists:
            if 'LEVEL_LIST' in field_list:
                field_dict[field_list] = (
                    self.get_level_list(field_list.split('_')[0])
                )
            else:
                field_dict[field_list] = util.getlist(
                    self.config.getstr('config',
                                       field_list,
                                       '')
                )

            # keep track if any list is not empty
            if field_dict[field_list]:
                all_empty = False

        return all_empty

    def check_MakePlots_config(self, c_dict):

        # the following are specific to running MakePlots wrapper
        bad_config_variable_list = [
            'FCST_VAR_LIST', 'FCST_LEVEL_LIST',
            'FCST_THRESH_LIST', 'FCST_UNITS_LIST',
            'OBS_VAR_LIST', 'OBS_LEVEL_LIST',
            'OBS_THRESH_LIST', 'OBS_UNITS_LIST'
        ]
        for bad_config_variable in bad_config_variable_list:
            if c_dict[bad_config_variable]:
                self.log_error("Bad config option for running StatAnalysis "
                               "followed by MakePlots. Please remove "
                               +bad_config_variable+" and set using FCST/OBS_VARn")

        loop_group_accepted_options = [
            'FCST_VALID_HOUR_LIST', 'FCST_INIT_HOUR_LIST',
            'OBS_VALID_HOUR_LIST', 'OBS_INIT_HOUR_LIST'
        ]
        for config_list in c_dict['GROUP_LIST_ITEMS']:
            if config_list not in loop_group_accepted_options:
                self.log_error("Bad config option for running StatAnalysis "
                                  +"followed by MakePlots. Only accepted "
                                  +"values in GROUP_LIST_ITEMS are "
                                  +"FCST_VALID_HOUR_LIST, "
                                  +"FCST_INIT_HOUR_LIST, "
                                  +"OBS_VALID_HOUR_LIST, "
                                  +"OBS_INIT_HOUR_LIST. "
                                  +"Found "+config_list)

        for config_list in c_dict['LOOP_LIST_ITEMS']:
            if config_list not in loop_group_accepted_options:
                self.log_error("Bad config option for running StatAnalysis "
                                  +"followed by MakePlots. Only accepted "
                                  +"values in LOOP_LIST_ITEMS are "
                                  +"FCST_VALID_HOUR_LIST, "
                                  +"FCST_INIT_HOUR_LIST, "
                                  +"OBS_VALID_HOUR_LIST, "
                                  +"OBS_INIT_HOUR_LIST. "
                                  +"Found "+config_list)

        # Do checks for required configuration file options that are
        # defined by user.
        required_config_variable_list = [
            'VX_MASK_LIST', 'FCST_LEAD_LIST', 'LINE_TYPE_LIST'
            ]
        for required_config_variable in required_config_variable_list:
            if len(c_dict[required_config_variable]) == 0:
                self.log_error(required_config_variable+" has no items. "
                                  +"This list must have items to run "
                                  +"StatAnalysis followed by MakePlots.")

        # if MakePlots is run but -dump_row is not found in the job args, error
        if '-dump_row' not in c_dict['JOB_ARGS']:
            self.log_error("Must include -dump_row in STAT_ANALYSIS_JOB_ARGS if running MakePlots")

    def list_to_str(self, list_of_values, add_quotes=True):
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

    def set_lists_loop_or_group(self, c_dict):
        """! Determine whether the lists from the METplus config file
             should treat the items in that list as a group or items 
             to be looped over based on user settings, the values
             in the list, and process being run.
             
             Args:
                 @param group_items list of the METplus config list
                  names to group the list's items set by user
                 @param loop_items list of the METplus config list
                  names to loop over the list's items set by user
                 @param config_dict dictionary containing the
                  configuration information
             
             @returns tuple containing lists_to_group_items ( list of
              all the list names whose items are being grouped
              together) and lists_to_loop_items (list of all
              the list names whose items are being looped over)
        """
        # get list of config variables not found in either GROUP_LIST_ITEMS or LOOP_LIST_ITEMS
        missing_config_list = [conf for conf in self.expected_config_lists if conf not in c_dict['GROUP_LIST_ITEMS']]
        missing_config_list = [conf for conf in missing_config_list if conf not in c_dict['LOOP_LIST_ITEMS']]
        found_config_list = [conf for conf in self.expected_config_lists if conf not in missing_config_list]

        # loop through lists not found in either loop or group lists
        for missing_config in missing_config_list:

            # if running MakePlots
            if (c_dict['LOOP_ORDER'] == 'processes' and self.runMakePlots):

                # if LINE_TYPE_LIST is missing, add it to group list
                if missing_config == 'LINE_TYPE_LIST':
                    c_dict['GROUP_LIST_ITEMS'].append(missing_config)

                # else if list in config_dict is empty, warn and add to group list
                elif not c_dict[missing_config]:
                    self.logger.warning(missing_config + " is empty, "
                                        + "will be treated as group.")
                    c_dict['GROUP_LIST_ITEMS'].append(missing_config)

                # otherwise add to loop list
                else:
                    c_dict['LOOP_LIST_ITEMS'].append(missing_config)

            # if not running MakePlots, just add missing list to group list
            else:
                c_dict['GROUP_LIST_ITEMS'].append(missing_config)

        # loop through lists found in either loop or group lists originally
        for found_config in found_config_list:
            # if list is empty and in loop list, warn and move to group list
            if not c_dict[found_config] and found_config in c_dict['LOOP_LIST_ITEMS']:
                self.logger.warning(found_config + " is empty, "
                                    + "will be treated as group.")
                c_dict['GROUP_LIST_ITEMS'].append(found_config)
                c_dict['LOOP_LIST_ITEMS'].remove(found_config)

        self.logger.debug("Items in these lists will be grouped together: "
                          + ', '.join(c_dict['GROUP_LIST_ITEMS']))
        self.logger.debug("Items in these lists will be looped over: "
                          + ', '.join(c_dict['LOOP_LIST_ITEMS']))

        # if running MakePlots, create new group and loop lists based on
        # the criteria for running that wrapper
        if self.runMakePlots:
            c_dict['GROUP_LIST_ITEMS_MAKE_PLOTS'] = list(c_dict['GROUP_LIST_ITEMS'])
            c_dict['LOOP_LIST_ITEMS_MAKE_PLOTS'] = list(c_dict['LOOP_LIST_ITEMS'])
            for force_group_list in self.force_group_for_make_plots_lists:
                if force_group_list in c_dict['LOOP_LIST_ITEMS_MAKE_PLOTS']:
                    c_dict['LOOP_LIST_ITEMS_MAKE_PLOTS'].remove(force_group_list)
                    c_dict['GROUP_LIST_ITEMS_MAKE_PLOTS'].append(force_group_list)

        return c_dict

    def format_thresh(self, thresh):
        """! Format thresholds for file naming

             Args:
                @param thresh string of the thresholds. Can be a comma-separated list, i.e. gt3,<=5.5, ==7

             @returns string of comma-separated list of the threshold(s) with letter format, i.e. gt3, le5.5, eq7
        """
        formatted_thresh_list = []
        # separate thresholds by comma and strip off whitespace around values
        thresh_list = [thresh.strip() for thresh in thresh.split(',')]
        for thresh in thresh_list:
            if not thresh:
                continue

            thresh_letter = util.comparison_to_letter_format(thresh)
            if thresh_letter:
                formatted_thresh_list.append(thresh_letter)

        return ','.join(formatted_thresh_list)

    def build_stringsub_dict(self, lists_to_loop, lists_to_group, config_dict):
        """! Build a dictionary with list names, dates, and commonly
             used identifiers to pass to string_template_substitution.
            
             Args:
                 lists_to_loop  - list of all the list names whose items
                                  are being grouped together
                 lists_to group - list of all the list names whose items
                                  are being looped over
                 config_dict    - dictionary containing the configuration 
                                  information
            
             Returns:
                 stringsub_dict - dictionary containing the formatted
                                  information to pass to the 
                                  string_template_substitution
        """
        date_beg = self.c_dict['DATE_BEG']
        date_end = self.c_dict['DATE_END']
        date_type = self.c_dict['DATE_TYPE']

        stringsub_dict_keys = []
        for loop_list in lists_to_loop:
            list_name = loop_list.replace('_LIST', '')
            stringsub_dict_keys.append(list_name.lower())
        for group_list in lists_to_group:
            # if setting up MakePlots, skip adding forced
            # group lists so they will remain templates
            # to be filled in by the plotting scripts
            if (self.forMakePlots and
                    group_list in self.force_group_for_make_plots_lists):
                continue

            list_name = group_list.replace('_LIST', '')
            stringsub_dict_keys.append(list_name.lower())

        special_keys = [
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
        # create a dictionary of empty string values from the special keys
        for special_key in special_keys:
            stringsub_dict_keys.append(special_key)
        stringsub_dict = dict.fromkeys(stringsub_dict_keys, '')

        # Set full date information
        fcst_hour_list = config_dict['FCST_'+date_type+'_HOUR']
        obs_hour_list = config_dict['OBS_' + date_type + '_HOUR']
        if fcst_hour_list:
            fcst_hour_list = [fhr.strip() for fhr in fcst_hour_list.replace('"', '').split(',')]
        if obs_hour_list:
            obs_hour_list = [fhr.strip() for fhr in obs_hour_list.replace('"', '').split(',')]

        # if fcst hour list is set, set fcst_{data_type}_beg/end with first and last values
        # TODO: values should be sorted first
        if fcst_hour_list:
            stringsub_dict['fcst_'+date_type.lower()+'_beg'] = (
                datetime.datetime.strptime(
                    date_beg+fcst_hour_list[0], '%Y%m%d%H%M%S'
                )
            )
            stringsub_dict['fcst_'+date_type.lower()+'_end'] = (
                datetime.datetime.strptime(
                    date_end+fcst_hour_list[-1], '%Y%m%d%H%M%S'
                )
            )
            if (stringsub_dict['fcst_'+date_type.lower()+'_beg']
                    == stringsub_dict['fcst_'+date_type.lower()+'_end']):
                stringsub_dict['fcst_'+date_type.lower()] = (
                    stringsub_dict['fcst_'+date_type.lower()+'_beg']
                )
        # if fcst hour list is not set, use date beg 000000-235959 as fcst_{date_type}_beg/end
        #TODO: should be date beg 000000 and date end 235959?
        else:
            stringsub_dict['fcst_'+date_type.lower()+'_beg'] = (
                datetime.datetime.strptime(
                    date_beg+'000000', '%Y%m%d%H%M%S'
                )
            )
            stringsub_dict['fcst_'+date_type.lower()+'_end'] = (
                datetime.datetime.strptime(
                    date_beg+'235959', '%Y%m%d%H%M%S'
                )
            )
        # if obs hour list is set, set obs_{data_type}_beg/end with first and last values
        # TODO: values should be sorted first
        # TODO: this could be made into function to handle fcst and obs
        if obs_hour_list:
            stringsub_dict['obs_'+date_type.lower()+'_beg'] = (
                datetime.datetime.strptime(
                    date_beg+obs_hour_list[0], '%Y%m%d%H%M%S'
                )
            )
            stringsub_dict['obs_'+date_type.lower()+'_end'] = (
                datetime.datetime.strptime(
                    date_end+obs_hour_list[-1], '%Y%m%d%H%M%S'
                )
            )
            if (stringsub_dict['obs_'+date_type.lower()+'_beg']
                    == stringsub_dict['obs_'+date_type.lower()+'_end']):
                stringsub_dict['obs_'+date_type.lower()] = (
                    stringsub_dict['obs_'+date_type.lower()+'_beg']
                )
        # if obs hour list is not set, use date beg 000000-235959 as obs_{date_type}_beg/end
        #TODO: should be date beg 000000 and date end 235959?
        else:
            stringsub_dict['obs_'+date_type.lower()+'_beg'] = (
                datetime.datetime.strptime(
                    date_beg+'000000', '%Y%m%d%H%M%S'
                )
            )
            stringsub_dict['obs_'+date_type.lower()+'_end'] = (
                datetime.datetime.strptime(
                    date_beg+'235959', '%Y%m%d%H%M%S'
                )
            )
        # if fcst and obs hour lists the same, set {date_type}_beg/end to fcst_{date_type}_beg/end
        if fcst_hour_list == obs_hour_list:
            stringsub_dict[date_type.lower()+'_beg'] = (
                 stringsub_dict['fcst_'+date_type.lower()+'_beg']
            )
            stringsub_dict[date_type.lower()+'_end'] = (
                 stringsub_dict['fcst_'+date_type.lower()+'_end']
            )
            # if {date_type} beg and end are the same, set {date_type}
            if (stringsub_dict[date_type.lower()+'_beg']
                    == stringsub_dict[date_type.lower()+'_end']):
                 stringsub_dict[date_type.lower()] = (
                     stringsub_dict['fcst_'+date_type.lower()+'_beg']
                 )
        # if fcst hr list is not set but obs hr list is, set {date_type}_beg/end to fcst_{date_type}_beg/end
        # TODO: should be elif?
        if fcst_hour_list and not obs_hour_list:
            stringsub_dict[date_type.lower()+'_beg'] = (
                stringsub_dict['fcst_'+date_type.lower()+'_beg']
            )
            stringsub_dict[date_type.lower()+'_end'] = (
                stringsub_dict['fcst_'+date_type.lower()+'_end']
            )
            # if {date_type} beg and end are the same, set {date_type} (same as above)
            if (stringsub_dict[date_type.lower()+'_beg']
                    == stringsub_dict[date_type.lower()+'_end']):
                stringsub_dict[date_type.lower()] = (
                    stringsub_dict['fcst_'+date_type.lower()+'_beg']
                )
        # if fcst hr list is set but obs hr list is not, set {date_type}_beg/end to obs_{date_type}_beg/end
        # TODO: should be elif?
        if not fcst_hour_list and obs_hour_list:
            stringsub_dict[date_type.lower()+'_beg'] = (
                stringsub_dict['obs_'+date_type.lower()+'_beg']
            )
            stringsub_dict[date_type.lower()+'_end'] = (
                stringsub_dict['obs_'+date_type.lower()+'_end']
            )
            # if {date_type} beg and end are the same, set {date_type} (same as above twice)
            if (stringsub_dict[date_type.lower()+'_beg']
                    == stringsub_dict[date_type.lower()+'_end']):
                stringsub_dict[date_type.lower()] = (
                    stringsub_dict['obs_'+date_type.lower()+'_beg']
                )
        # if neither fcst or obs hr list are set, {date_type}_beg/end are not set at all (empty string)
        # also {date_type} is not set

        # Set loop information
        for loop_list in lists_to_loop:
            list_name = loop_list.replace('_LIST', '')
            list_name_value = (
                config_dict[list_name].replace('"', '').replace(' ', '')
            )
            # CHANGE: format thresh when it is read instead of here
#            if 'THRESH' in list_name:
#                stringsub_dict[list_name.lower()] = self.format_thresh(
#                        list_name_value
#                )
#            elif list_name == 'MODEL':
            if list_name == 'MODEL':
                stringsub_dict[list_name.lower()] = list_name_value
                stringsub_dict['obtype'] = (
                    config_dict['OBTYPE'].replace('"', '').replace(' ', '')
                )
            elif 'HOUR' in list_name:
                 stringsub_dict[list_name.lower()] = (
                     datetime.datetime.strptime(list_name_value, '%H%M%S')
                 )
                 stringsub_dict[list_name.lower()+'_beg'] = stringsub_dict[
                     list_name.lower()
                 ]
                 stringsub_dict[list_name.lower()+'_end'] = stringsub_dict[
                     list_name.lower()
                 ]
                 check_list1 = config_dict[list_name]
                 if 'FCST' in list_name:
                     check_list2 = config_dict[list_name.replace('FCST',
                                                                 'OBS')]
                 elif 'OBS' in list_name:
                     check_list2 = config_dict[list_name.replace('OBS',
                                                                 'FCST')]
                 if (check_list1 == check_list2
                         or len(check_list2) == 0):
                     list_type = list_name.replace('_HOUR', '').lower()
                     if 'VALID' in list_name:
                        stringsub_dict['valid_hour_beg'] = (
                            stringsub_dict[list_type+'_hour_beg']
                        )
                        stringsub_dict['valid_hour_end'] = (
                           stringsub_dict[list_type+'_hour_end']
                        )
                        if (stringsub_dict['valid_hour_beg']
                                == stringsub_dict['valid_hour_end']):
                            stringsub_dict['valid_hour'] = (
                                stringsub_dict['valid_hour_end']
                            )
                     elif 'INIT' in list_name:
                        stringsub_dict['init_hour_beg'] = (
                            stringsub_dict[list_type+'_hour_beg']
                        )
                        stringsub_dict['init_hour_end'] = (
                            stringsub_dict[list_type+'_hour_end']
                        )
                        if (stringsub_dict['init_hour_beg']
                                == stringsub_dict['init_hour_end']):
                           stringsub_dict['init_hour'] = (
                                stringsub_dict['init_hour_end']
                           )
            elif 'LEAD' in list_name:
                lead_timedelta = datetime.timedelta(
                    hours=int(list_name_value[:-4]),
                    minutes=int(list_name_value[-4:-2]),
                    seconds=int(list_name_value[-2:])
                )
                stringsub_dict[list_name.lower()] = list_name_value
                stringsub_dict[list_name.lower()+'_hour'] = (
                    list_name_value[:-4]
                )
                stringsub_dict[list_name.lower()+'_min'] = (
                    list_name_value[-4:-2]
                )
                stringsub_dict[list_name.lower()+'_sec'] = (
                    list_name_value[-2:]
                )
                stringsub_dict[list_name.lower()+'_totalsec'] = str(int(
                    lead_timedelta.total_seconds()
                ))
                list_type = list_name.replace('_LEAD', '').lower()
                check_list1 = config_dict[list_name]
                if 'FCST' in list_name:
                    check_list2 = config_dict[list_name.replace('FCST', 'OBS')]
                elif 'OBS' in list_name:
                    check_list2 = config_dict[list_name.replace('OBS', 'FCST')]
                if (check_list1 == check_list2
                         or len(check_list2) == 0):
                    stringsub_dict['lead'] = stringsub_dict[list_name.lower()]
                    stringsub_dict['lead_hour'] = (
                        stringsub_dict[list_name.lower()+'_hour']
                    )
                    stringsub_dict['lead_min'] = (
                        stringsub_dict[list_name.lower()+'_min']
                    )
                    stringsub_dict['lead_sec'] = (
                        stringsub_dict[list_name.lower()+'_sec']
                    )
                    stringsub_dict['lead_totalsec'] = (
                        stringsub_dict[list_name.lower()+'_totalsec']
                    )
            else:
                stringsub_dict[list_name.lower()] = list_name_value

        # Set group information
        for group_list in lists_to_group:
            list_name = group_list.replace('_LIST', '')
            list_name_value = (
                config_dict[list_name].replace('"', '').replace(' ', '') \
                .replace(',', '_').replace('*', 'ALL')
            )
            if 'THRESH' in list_name:
                if (self.forMakePlots and
                        group_list in self.force_group_for_make_plots_lists):
                    continue

                thresh_letter = self.format_thresh(
                    config_dict[list_name]
                )

                stringsub_dict[list_name.lower()] = (
                    thresh_letter.replace(',', '_').replace('*', 'ALL')
                )
            elif 'HOUR' in list_name:
                list_name_values_list = (
                    config_dict[list_name].replace('"', '').split(', ')
                )
                stringsub_dict[list_name.lower()] = list_name_value
                if list_name_values_list != ['']:
                    stringsub_dict[list_name.lower()+'_beg'] = (
                        datetime.datetime.strptime(list_name_values_list[0], 
                                                   '%H%M%S')
                    )
                    stringsub_dict[list_name.lower()+'_end'] = (
                        datetime.datetime.strptime(list_name_values_list[-1], 
                                                   '%H%M%S')
                    )
                    if (stringsub_dict[list_name.lower()+'_beg']
                            == stringsub_dict[list_name.lower()+'_end']):
                       stringsub_dict[list_name.lower()] = (
                           stringsub_dict[list_name.lower()+'_end']
                       )
                    check_list1 = config_dict[list_name]
                    if 'FCST' in list_name:
                        check_list2 = config_dict[list_name.replace('FCST',
                                                                    'OBS')]
                    elif 'OBS' in list_name:
                        check_list2 = config_dict[list_name.replace('OBS',
                                                                    'FCST')]
                    if (check_list1 == check_list2
                             or len(check_list2) == 0):
                        list_type = list_name.replace('_HOUR', '').lower()
                        if 'VALID' in list_name:
                            stringsub_dict['valid_hour_beg'] = (
                                stringsub_dict[list_type+'_hour_beg']
                            )
                            stringsub_dict['valid_hour_end'] = (
                               stringsub_dict[list_type+'_hour_end']
                            )
                            if (stringsub_dict['valid_hour_beg']
                                    == stringsub_dict['valid_hour_end']):
                                stringsub_dict['valid_hour'] = (
                                    stringsub_dict['valid_hour_end']
                                )
                        elif 'INIT' in list_name:
                            stringsub_dict['init_hour_beg'] = (
                                stringsub_dict[list_type+'_hour_beg']
                            )
                            stringsub_dict['init_hour_end'] = (
                               stringsub_dict[list_type+'_hour_end']
                            )
                            if (stringsub_dict['init_hour_beg']
                                    == stringsub_dict['init_hour_end']):
                                stringsub_dict['init_hour'] = (
                                    stringsub_dict['init_hour_end']
                                )
                else:
                    stringsub_dict[list_name.lower()+'_beg'] = (
                        datetime.datetime.strptime('000000',
                                                   '%H%M%S')
                    )
                    stringsub_dict[list_name.lower()+'_end'] = (
                        datetime.datetime.strptime('235959',
                                                   '%H%M%S')
                    )
                    check_list1 = config_dict[list_name]
                    if 'FCST' in list_name:
                        check_list2 = config_dict[list_name.replace('FCST',
                                                                    'OBS')]
                    elif 'OBS' in list_name:
                        check_list2 = config_dict[list_name.replace('OBS',
                                                                    'FCST')]
                    if (check_list1 == check_list2
                             or len(check_list2) == 0):
                        list_type = list_name.replace('_HOUR', '').lower()
                        if 'VALID' in list_name:
                            stringsub_dict['valid_hour_beg'] = (
                                stringsub_dict[list_type+'_hour_beg']
                            )
                            stringsub_dict['valid_hour_end'] = (
                               stringsub_dict[list_type+'_hour_end']
                            )
                            if (stringsub_dict['valid_hour_beg']
                                    == stringsub_dict['valid_hour_end']):
                                stringsub_dict['valid_hour'] = (
                                    stringsub_dict['valid_hour_end']
                                )
                        elif 'INIT' in list_name:
                            stringsub_dict['init_hour_beg'] = (
                                stringsub_dict[list_type+'_hour_beg']
                            )
                            stringsub_dict['init_hour_end'] = (
                               stringsub_dict[list_type+'_hour_end']
                            )
                            if (stringsub_dict['init_hour_beg']
                                    == stringsub_dict['init_hour_end']):
                                stringsub_dict['init_hour'] = (
                                    stringsub_dict['init_hour_end']
                                )
            elif not (self.forMakePlots and
                      group_list in self.force_group_for_make_plots_lists):
                # if setting up MakePlots, skip adding forced
                # group lists so they will remain templates
                # to be filled in by the plotting scripts
                stringsub_dict[list_name.lower()] = list_name_value

        nkeys_end = len(stringsub_dict_keys)
        # Some lines for debugging if needed in future
        #self.logger.info(nkeys_start)
        #self.logger.info(nkeys_end)
        #for key, value in stringsub_dict.items():
        #    self.logger.info("{} ({})".format(key, value))
        return stringsub_dict

    def get_output_filename(self, output_type, filename_template,
                            filename_type,
                            lists_to_loop, lists_to_group, config_dict):
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
                 lists_to group    - list of all the list names whose
                                     items are being looped over
                 config_dict       - dictionary containing the
                                     configuration information

             Returns:
                 output_filename   - string of the filled file name
                                     template
        """
        date_beg = self.c_dict['DATE_BEG']
        date_end = self.c_dict['DATE_END']
        date_type = self.c_dict['DATE_TYPE']

        stringsub_dict = self.build_stringsub_dict(lists_to_loop,
                                                   lists_to_group, config_dict)

        if filename_type == 'default':
            if (self.runMakePlots and output_type == 'dump_row'):
                filename_template_prefix = ( 
                    filename_template+date_type.lower()
                    +'{'+date_type.lower()+'_beg?fmt=%Y%m%d}'
                    +'to{'+date_type.lower()+'_end?fmt=%Y%m%d}_'
                )
                if (stringsub_dict['valid_hour_beg'] != ''
                        and stringsub_dict['valid_hour_end'] != ''):
                    filename_template_prefix+=(
                        'valid{valid_hour_beg?fmt=%H%M}to'
                        +'{valid_hour_end?fmt=%H%M}Z_'
                    )
                else:
                    filename_template_prefix+=(
                        'fcst_valid{fcst_valid_hour_beg?fmt=%H%M}to'
                        +'{fcst_valid_hour_end?fmt=%H%M}Z_'
                        'obs_valid{obs_valid_hour_beg?fmt=%H%M}to'
                        +'{obs_valid_hour_end?fmt=%H%M}Z_'
                    )
                if (stringsub_dict['init_hour_beg'] != ''
                        and stringsub_dict['init_hour_end'] != ''):
                    filename_template_prefix+=(
                        'init{init_hour_beg?fmt=%H%M}to'
                        +'{init_hour_end?fmt=%H%M}Z'
                    )
                else:
                    filename_template_prefix+=(
                        'fcst_init{fcst_init_hour_beg?fmt=%H%M}to'
                        +'{fcst_init_hour_end?fmt=%H%M}Z_'
                        'obs_init{obs_init_hour_beg?fmt=%H%M}to'
                        +'{obs_init_hour_end?fmt=%H%M}Z'
                    )
                filename_template_prefix+=(
                    '_fcst_lead{fcst_lead?fmt=%s}'
                    +'_fcst{fcst_var?fmt=%s}{fcst_level?fmt=%s}'
                    +'{fcst_thresh?fmt=%s}{interp_mthd?fmt=%s}_'
                    +'obs{obs_var?fmt=%s}{obs_level?fmt=%s}'
                    +'{obs_thresh?fmt=%s}{interp_mthd?fmt=%s}_'
                    +'vxmask{vx_mask?fmt=%s}'
                )
                if 'DESC_LIST' in lists_to_loop:
                    filename_template_prefix = (
                        filename_template_prefix
                        +'_desc{desc?fmt=%s}'
                    )
                if 'OBS_LEAD_LIST' in lists_to_loop:
                    filename_template_prefix = (
                        filename_template_prefix
                        +'_obs_lead{obs_lead?fmt=%s}'
                    )
                if 'INTERP_PNTS_LIST' in lists_to_loop:
                    filename_template_prefix = (
                        filename_template_prefix
                        +'_interp_pnts{interp_pnts?fmt=%s}'
                    )
                if 'COV_THRESH_LIST' in lists_to_loop:
                    filename_template_prefix = (
                        filename_template_prefix
                        +'_cov_thresh{cov_thresh?fmt=%s}'
                    )
                if 'ALPHA_LIST' in lists_to_loop:
                    filename_template_prefix = (
                        filename_template_prefix
                        +'_alpha{alpha?fmt=%s}'
                    )
                filename_template = filename_template_prefix
            else:
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
                            filename_template = (
                                filename_template+'_'
                                +list_name.replace('_', '').lower()
                                +config_dict[list_name].replace('"', '')+'Z'
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
                                        **stringsub_dict,
                                        skip_missing_tags=self.forMakePlots)
        return output_filename

    def get_lookin_dir(self, dir_path, lists_to_loop, lists_to_group, config_dict):
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
        if '?fmt=' in dir_path:
            stringsub_dict = self.build_stringsub_dict(lists_to_loop,
                                                       lists_to_group, 
                                                       config_dict)
            dir_path_filled = do_string_sub(dir_path,
                                            **stringsub_dict)
        else:
            dir_path_filled = dir_path
        if '*' in dir_path_filled:
            self.logger.debug(f"Expanding wildcard path: {dir_path_filled}")
            dir_path_filled_all = ' '.join(sorted(glob.glob(dir_path_filled)))
            self.logger.warning(f"Wildcard expansion found no matches")
        else:
            dir_path_filled_all = dir_path_filled
        lookin_dir = dir_path_filled_all
        return lookin_dir

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
            util.find_indices_in_config_section(r'MODEL(\d+)$',
                                                self.config,
                                                'config',
                                                noID=True).keys()
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
                    # if MakePlots is run
                    if self.runMakePlots:
                        model_out_stat_filename_template = 'NA'
                        model_out_stat_filename_type = 'NA'
                    else:
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

        level_input = util.getlist(
            self.config.getstr('config', f'{data_type}_LEVEL_LIST', '')
        )

        for level in level_input:
            level = level.strip('(').strip(')')
            level = f'{util.remove_quotes(level)}'
            level_list.append(level)

        return level_list

    def process_job_args(self, job_type, job, model_info,
                         lists_to_loop_items, lists_to_group_items, runtime_settings_dict):

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
                                     lists_to_group_items,
                                     runtime_settings_dict)
        )
        output_file = os.path.join(self.c_dict['OUTPUT_DIR'],
                                   output_filename)

        # substitute output filename in JOB_ARGS line
        job = job.replace(f'[{job_type}_file]', output_file)
        job = job.replace(f'[{job_type}_filename]', output_file)

        # add output file path to runtime_settings_dict
        runtime_settings_dict[f'{job_type.upper()}_FILENAME'] = output_file

        return job

    def get_runtime_settings_dict_list(self):
        runtime_settings_dict_list = []
        c_dict_list = self.get_c_dict_list()
        for c_dict in c_dict_list:
            runtime_settings = self.get_runtime_settings(c_dict)
            runtime_settings_dict_list.extend(runtime_settings)

        # Loop over run settings.
        formatted_runtime_settings_dict_list = []
        for runtime_settings_dict in runtime_settings_dict_list:
            if self.forMakePlots:
                loop_lists = c_dict['LOOP_LIST_ITEMS_MAKE_PLOTS']
                group_lists = c_dict['GROUP_LIST_ITEMS_MAKE_PLOTS']
            else:
                loop_lists = c_dict['LOOP_LIST_ITEMS']
                group_lists = c_dict['GROUP_LIST_ITEMS']

            # Set up stat_analysis -lookin argument, model and obs information
            # and stat_analysis job.
            model_info = self.get_model_obtype_and_lookindir(runtime_settings_dict,
                                                             loop_lists,
                                                             group_lists,
                                                             )
            if model_info is None:
                return None

            runtime_settings_dict['JOB'] = self.get_job_info(model_info,
                                                             runtime_settings_dict,
                                                             loop_lists,
                                                             group_lists,
                                                             )

            # Set up forecast and observation valid
            # and initialization time information.
            runtime_settings_dict = (
                self.format_valid_init(runtime_settings_dict)
            )
            formatted_runtime_settings_dict_list.append(runtime_settings_dict)

        return formatted_runtime_settings_dict_list

    def get_runtime_settings(self, c_dict):

        # Parse whether all expected METplus config _LIST variables
        # to be treated as a loop or group.
        group_lists = c_dict['GROUP_LIST_ITEMS']
        loop_lists = c_dict['LOOP_LIST_ITEMS']

        if self.forMakePlots:
            group_lists = c_dict['GROUP_LIST_ITEMS_MAKE_PLOTS']
            loop_lists = c_dict['LOOP_LIST_ITEMS_MAKE_PLOTS']

        runtime_setup_dict = {}
        # Fill setup dictionary for MET config variable name
        # and its value as a string for group lists.
        for group_list in group_lists:
            runtime_setup_dict_name = group_list.replace('_LIST', '')
            add_quotes = False if 'THRESH' in group_list else True

            # if preparing for MakePlots, change
            # commas to _ and * to ALL in list items
            if self.forMakePlots:
                formatted_list = []
                for format_list in c_dict[group_list]:
                    formatted_list.append(format_list.replace(',', '_')
                                          .replace('*', 'ALL'))
            else:
                formatted_list = c_dict[group_list]
            runtime_setup_dict[runtime_setup_dict_name] = (
                [self.list_to_str(formatted_list,
                                  add_quotes=add_quotes)]
            )

        # Fill setup dictionary for MET config variable name
        # and its value as a list for loop lists. Some items
        # in lists need to be formatted now, others done later.

        for loop_list in loop_lists:
            # if not a threshold list, add quotes around each value in list
            # if loop_list not in self.format_later_list and 'THRESH' not in loop_list:
            if 'THRESH' not in loop_list:
                c_dict[loop_list] = [f'"{value}"' for value in c_dict[loop_list]]

            runtime_setup_dict_name = loop_list.replace('_LIST', '')
            runtime_setup_dict[runtime_setup_dict_name] = (
                c_dict[loop_list]
            )

        # Create run time dictionary with all the combinations
        # of settings to be run.
        runtime_setup_dict_names = sorted(runtime_setup_dict)
        runtime_settings_dict_list = (
            [dict(zip(runtime_setup_dict_names, prod)) for prod in
             itertools.product(*(runtime_setup_dict[name] for name in
             runtime_setup_dict_names))]
        )

        return runtime_settings_dict_list

    def get_field_units(self, index):
        """! Get units of fcst and obs fields if set based on VAR<n> index
             @params index VAR<n> index corresponding to other [FCST/OBS] info
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

    def get_c_dict_list(self):
        # if fields were not specified with [FCST/OBS]_VAR<n>_* variables
        # return and array with only self.c_dict
        if not self.c_dict['VAR_LIST']:
            return [copy.deepcopy(self.c_dict)]

        # otherwise, use field information to build lists with single items
        # make individual dictionaries for each threshold
        var_info_list = self.c_dict['VAR_LIST']
        c_dict_list = []
        for var_info in var_info_list:
            fcst_units, obs_units = self.get_field_units(var_info['index'])

            run_fourier = (
                self.config.getbool('config',
                                    'VAR' + var_info['index'] + '_FOURIER_DECOMP',
                                    False)
            )
            if run_fourier:
                fourier_wave_num_pairs = util.getlist(
                    self.config.getstr('config',
                                       'VAR' + var_info['index'] + '_WAVE_NUM_LIST',
                                       '')
                )
            else:
                # if not running fourier, use a list
                # containing an empty string to loop one iteration
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
                    c_dict = {}
                    c_dict['index'] = var_info['index']
                    c_dict['FCST_VAR_LIST'] = [
                        var_info['fcst_name']
                    ]
                    c_dict['OBS_VAR_LIST'] = [
                        var_info['obs_name']
                    ]
                    c_dict['FCST_LEVEL_LIST'] = [
                        var_info['fcst_level']
                    ]
                    c_dict['OBS_LEVEL_LIST'] = [
                        var_info['obs_level']
                    ]

                    c_dict['FCST_THRESH_LIST'] = []
                    c_dict['OBS_THRESH_LIST'] = []
                    if fcst_thresh:
                        thresh_formatted = self.format_thresh(fcst_thresh)
                        c_dict['FCST_THRESH_LIST'].append(thresh_formatted)

                    if obs_thresh:
                        thresh_formatted = self.format_thresh(obs_thresh)
                        c_dict['OBS_THRESH_LIST'].append(thresh_formatted)

                    c_dict['FCST_UNITS_LIST'] = []
                    c_dict['OBS_UNITS_LIST'] = []
                    if fcst_units:
                        c_dict['FCST_UNITS_LIST'].append(fcst_units)
                    if obs_units:
                        c_dict['OBS_UNITS_LIST'].append(obs_units)

                    c_dict['run_fourier'] = run_fourier
                    if pair:
                        c_dict['INTERP_MTHD_LIST'] = ['WV1_' + pair]
                    else:
                        c_dict['INTERP_MTHD_LIST'] = []

                    self.add_other_lists_to_c_dict(c_dict)

                    c_dict_list.append(c_dict)

        # if preparing for MakePlots, combine levels and thresholds for each name
        if self.forMakePlots:
            output_c_dict_list = []
            for c_dict in c_dict_list:
                if c_dict['index'] not in [conf['index'] for conf in output_c_dict_list]:
                    output_c_dict_list.append(c_dict)
                else:
                    for output_dict in output_c_dict_list:
                        if c_dict['index'] == output_dict['index']:

                            for level in c_dict['FCST_LEVEL_LIST']:
                                if level not in output_dict['FCST_LEVEL_LIST']:
                                    output_dict['FCST_LEVEL_LIST'].append(level)

                            for level in c_dict['OBS_LEVEL_LIST']:
                                if level not in output_dict['OBS_LEVEL_LIST']:
                                    output_dict['OBS_LEVEL_LIST'].append(level)

                            for thresh in c_dict['FCST_THRESH_LIST']:
                                if thresh not in output_dict['FCST_THRESH_LIST']:
                                    output_dict['FCST_THRESH_LIST'].append(thresh)

                            for thresh in c_dict['OBS_THRESH_LIST']:
                                if thresh not in output_dict['OBS_THRESH_LIST']:
                                    output_dict['OBS_THRESH_LIST'].append(thresh)


            return output_c_dict_list

        return c_dict_list

    def add_other_lists_to_c_dict(self, c_dict):
        """! Using GROUP_LIST_ITEMS and LOOP_LIST_ITEMS, add lists from
             self.c_dict that are not already in c_dict.
             @param c_dict dictionary to add values to
        """
        # add group and loop lists
        lists_to_add = self.list_categories
        if self.runMakePlots:
            lists_to_add.extend(self.list_categories_make_plots)

        for list_category in lists_to_add:
            list_items = self.c_dict[list_category]
            if list_category not in c_dict:
                c_dict[list_category] = list_items

            for list_item in list_items:
                if list_item not in c_dict:
                    c_dict[list_item] = self.c_dict[list_item]

    def get_model_obtype_and_lookindir(self, runtime_settings_dict, loop_lists, group_lists):
        """! Reads through model info dictionaries for given run. Sets lookindir command line
             argument. Sets MODEL and OBTYPE values in runtime setting dictionary.
             @param runtime_settings_dict dictionary containing all settings used in next run
             @returns last model info dictionary is successful, None if not.
        """
        lookin_dirs = []
        model_list = []
        reference_list = []
        obtype_list = []
        dump_row_filename_list = []
        # get list of models to process
        models_to_run = [model.strip().replace('"', '') for model in runtime_settings_dict['MODEL'].split(',')]
        for model_info in self.c_dict['MODEL_INFO_LIST']:
            # skip model if not in list of models to process
            if model_info['name'] not in models_to_run:
                continue

            model_list.append(model_info['name'])
            reference_list.append(model_info['reference_name'])
            obtype_list.append(model_info['obtype'])
            dump_row_filename_list.append(model_info['dump_row_filename_template'])
            # set MODEL and OBTYPE to single item to find lookin dir
            runtime_settings_dict['MODEL'] = '"'+model_info['name']+'"'
            runtime_settings_dict['OBTYPE'] = '"'+model_info['obtype']+'"'
            # don't get lookin dir if getting settings for MakePlots
            if not self.forMakePlots:
                lookin_dirs.append(self.get_lookin_dir(model_info['dir'],
                                                       loop_lists,
                                                       group_lists,
                                                       runtime_settings_dict,
                                                       )
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
        runtime_settings_dict['MODEL_REFERENCE_NAME'] = self.list_to_str(reference_list)
        runtime_settings_dict['OBTYPE'] = self.list_to_str(obtype_list)

        # return last model info dict used
        return model_info

    def get_job_info(self, model_info, runtime_settings_dict, loop_lists, group_lists):
        """! Get job information and concatenate values into a string
             @params model_info model information to use to determine output file paths
             @params runtime_settings_dict dictionary containing all settings used in next run
             @returns string containing job information to pass to StatAnalysis config file
        """
        job = '-job ' + self.c_dict['JOB_NAME'] + ' ' + self.c_dict['JOB_ARGS']
        for job_type in ['dump_row', 'out_stat']:
            if f"-{job_type}" in self.c_dict['JOB_ARGS']:
                job = self.process_job_args(job_type,
                                            job,
                                            model_info,
                                            loop_lists,
                                            group_lists,
                                            runtime_settings_dict,
                                            )

        return job

    def run_stat_analysis(self):
        """! This runs stat_analysis over a period of valid
             or initialization dates for a job defined by
             the user.
        """
        self.forMakePlots = False

        runtime_settings_dict_list = self.get_runtime_settings_dict_list()
        if not runtime_settings_dict_list:
            return False

        self.run_stat_analysis_job(runtime_settings_dict_list)

        # if running MakePlots, get its runtime_settings_dict_list and call
        if self.runMakePlots:
            self.logger.debug("Preparing settings to pass to MakePlots wrapper")
            self.forMakePlots = True
            runtime_settings_dict_list = (
                self.get_runtime_settings_dict_list()
            )
            if not runtime_settings_dict_list:
                return False

            self.MakePlotsWrapper.create_plots(runtime_settings_dict_list)
            if self.MakePlotsWrapper.errors:
                self.log_error("MakePlots produced "
                               f"{self.MakePlotsWrapper.errors} errors.")

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

            self.job_args = None
            # Set environment variables and run stat_analysis.
            for name, value in runtime_settings_dict.items():
                self.add_env_var(name, value)

            # send environment variables to logger
            self.set_environment_variables()

            # set lookin dir
            self.logger.debug(f"Setting -lookindir to {runtime_settings_dict['LOOKIN_DIR']}")
            self.lookindir = runtime_settings_dict['LOOKIN_DIR']
            self.job_args = runtime_settings_dict['JOB']

            self.build()

            self.clear()

    def create_output_directories(self, runtime_settings_dict):
        """! Check if output filename is set for dump_row or out_stat. If set,
             Check if the file already exists and if it should be skipped.

             @param runtime_settings_dict dictionary containing filename info
             @returns True if job should be run, False if it should be skipped
        """
        run_job = True
        for job_type in ['dump_row', 'out_stat']:
            output_path = (
                runtime_settings_dict.get(f'{job_type.upper()}_FILENAME')
            )
            if output_path:
                if not self.find_and_check_output_file(
                        output_path_template=output_path):
                    run_job = False

        return run_job

    def run_all_times(self):
        date_type = self.c_dict['DATE_TYPE']
        self.c_dict['DATE_BEG'] = self.c_dict[date_type+'_BEG']
        self.c_dict['DATE_END'] = self.c_dict[date_type+'_END']
        self.run_stat_analysis()
        return self.all_commands

    def run_at_time(self, input_dict):
        loop_by_init = util.is_loop_by_init(self.config)
        if loop_by_init is None:
            return

        if loop_by_init:
            loop_by = 'INIT'
        else:
            loop_by = 'VALID'

        self.c_dict['DATE_TYPE'] = loop_by

        run_date = input_dict[loop_by.lower()].strftime('%Y%m%d')
        self.c_dict['DATE_BEG'] = run_date
        self.c_dict['DATE_END'] = run_date
        self.run_stat_analysis()
