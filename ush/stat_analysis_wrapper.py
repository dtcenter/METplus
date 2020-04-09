#!/usr/bin/env python

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

import metplus_check_python_version

import logging
import os
import copy
import met_util as util
import re
import subprocess
import datetime
import itertools
import string_template_substitution as sts
from command_builder import CommandBuilder


class StatAnalysisWrapper(CommandBuilder):
    """! Wrapper to the MET tool stat_analysis which is used to filter 
         and summarize data from MET's point_stat, grid_stat, 
         ensemble_stat, and wavelet_stat
    """
    def __init__(self, config, logger):
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin/stat_analysis')
        self.app_name = os.path.basename(self.app_path)
        super().__init__(config, logger)
        
    def set_lookin_dir(self, lookindir):
        self.lookindir = "-lookin "+lookindir+" "
   
    def get_command(self):
        if self.app_path is None:
            self.log_error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        if self.lookindir == "":
            self.log_error(self.app_name+": No lookin directory specified")
            return None
        
        cmd += self.lookindir
         
        if self.param != "":
            cmd += "-config " + self.param + " "
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
            self.config.getstr('config','LOG_STAT_ANALYSIS_VERBOSITY',
                               c_dict['VERBOSITY'])
        )
        c_dict['LOOP_ORDER'] = self.config.getstr('config', 'LOOP_ORDER')
        c_dict['PROCESS_LIST'] = self.config.getstr('config', 'PROCESS_LIST')
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 
                                                   'STAT_ANALYSIS_CONFIG_FILE')
        c_dict['OUTPUT_BASE_DIR'] = (
            self.config.getdir('STAT_ANALYSIS_OUTPUT_DIR')
        )
        c_dict['GROUP_LIST_ITEMS'] = util.getlist(
            self.config.getstr('config', 'GROUP_LIST_ITEMS')
        )
        c_dict['LOOP_LIST_ITEMS'] = util.getlist(
            self.config.getstr('config', 'LOOP_LIST_ITEMS')
        )
        c_dict['VAR_LIST'] = util.parse_var_list(self.config)
        c_dict['MODEL_LIST'] = util.getlist(
            self.config.getstr('config', 'MODEL_LIST', '')
        )
        c_dict['DESC_LIST'] = util.getlist(
            self.config.getstr('config', 'DESC_LIST', '')
        )
        c_dict['FCST_LEAD_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_LEAD_LIST', '')
        )
        c_dict['OBS_LEAD_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_LEAD_LIST', '')
        )
        c_dict['FCST_VALID_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_VALID_HOUR_LIST', '')
        )
        c_dict['FCST_INIT_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_INIT_HOUR_LIST', '')
        )
        c_dict['OBS_VALID_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_VALID_HOUR_LIST', '')
        )
        c_dict['OBS_INIT_HOUR_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_INIT_HOUR_LIST', '')
        )
        c_dict['VX_MASK_LIST'] = util.getlist(
            self.config.getstr('config', 'VX_MASK_LIST', '')
        )
        c_dict['INTERP_MTHD_LIST'] = util.getlist(
            self.config.getstr('config', 'INTERP_MTHD_LIST', '')
        )
        c_dict['INTERP_PNTS_LIST'] = util.getlist(
            self.config.getstr('config', 'INTERP_PNTS_LIST', '')
        )
        c_dict['COV_THRESH_LIST'] = util.getlist(
            self.config.getstr('config', 'COV_THRESH_LIST', '')
        )
        c_dict['ALPHA_LIST'] = util.getlist(
            self.config.getstr('config', 'ALPHA_LIST', '')
        )
        c_dict['LINE_TYPE_LIST'] = util.getlist(
            self.config.getstr('config', 'LINE_TYPE_LIST', '')
        )
        return c_dict

    def list_to_str(self, list_of_values):
        """! Turn a list of values into a single string so it can be 
             set to an environment variable and read by the MET 
             stat_analysis config file.
                 
             Args:
                 list_of_values - list of values
  
             Returns:
                 list_as_str    - string created from list_of_values
                                  with the values separated by commas 
        """
        list_as_str=''
        if len(list_of_values) > 0:
            for lt in range(len(list_of_values)):
                if lt == len(list_of_values)-1:
                    list_as_str = list_as_str+'"'+str(list_of_values[lt]+'"')
                else:
                    list_as_str = list_as_str+'"'+str(list_of_values[lt]+'", ')
        return list_as_str
    
    def set_lists_loop_or_group(self, config_lists_to_group_items,
                                config_lists_to_loop_items, config_dict):
        """! Determine whether the lists from the METplus config file
             should treat the items in that list as a group or items 
             to be looped over based on user settings, the values
             in the list, and process being run.
             
             Args:
                 config_lists_to_group_items - list of the METplus 
                                               config list names
                                               to group the list's 
                                               items set by user
                 config_lists_to_loop_items  - list of the METplus 
                                               config list names
                                               to loop over the 
                                               list's items set by 
                                               user
                 config_dict                 - dictionary containing
                                               the configuration 
                                               information
             
             Returns: 
                 lists_to_group_items        - list of all the list names 
                                               whose items are being 
                                               grouped together
                 lists_to_loop_items         - list of all the list names 
                                               whose items are being
                                               looped over 
        """
        expected_config_lists = [
             'MODEL_LIST', 'DESC_LIST',
             'FCST_LEAD_LIST', 'OBS_LEAD_LIST',
             'FCST_VALID_HOUR_LIST', 'FCST_INIT_HOUR_LIST',
             'OBS_VALID_HOUR_LIST', 'OBS_INIT_HOUR_LIST',
             'FCST_VAR_LIST', 'OBS_VAR_LIST',
             'FCST_UNITS_LIST', 'OBS_UNITS_LIST',
             'FCST_LEVEL_LIST', 'OBS_LEVEL_LIST',
             'VX_MASK_LIST', 'INTERP_MTHD_LIST',
             'INTERP_PNTS_LIST', 'FCST_THRESH_LIST',
             'OBS_THRESH_LIST', 'COV_THRESH_LIST',
             'ALPHA_LIST', 'LINE_TYPE_LIST'
        ]
        if (self.c_dict['LOOP_ORDER'] == 'processes' 
                and 'MakePlots' in self.c_dict['PROCESS_LIST']):
            lists_to_group_items = config_lists_to_group_items
            lists_to_loop_items = config_lists_to_loop_items
            for config_list in expected_config_lists:
                if (not config_list in config_lists_to_group_items
                        and not config_list in config_lists_to_loop_items):
                    if config_list == 'LINE_TYPE_LIST':
                        lists_to_group_items.append(config_list)
                    elif config_dict[config_list] == []:
                        self.logger.warning(config_list+" is empty, "
                                            +"will be treated as group.")
                        lists_to_group_items.append(config_list)
                    else:
                        lists_to_loop_items.append(config_list)
                elif (config_list in config_lists_to_loop_items
                          and config_dict[config_list] == []):
                    self.logger.warning(config_list+" is empty, "
                                        +"will be treated as group.")
                    lists_to_group_items.append(config_list)
                    lists_to_loop_items.remove(config_list)
        else:
            lists_to_group_items = config_lists_to_group_items
            lists_to_loop_items = config_lists_to_loop_items
            for config_list in expected_config_lists:
                if (not config_list in config_lists_to_group_items
                        and not config_list in config_lists_to_loop_items):
                    lists_to_group_items.append(config_list)
                elif (config_list in config_lists_to_loop_items
                          and config_dict[config_list] == []):
                    self.logger.warning(config_list+" is empty, "
                                        +"will be treated as group.")
                    lists_to_group_items.append(config_list)
                    lists_to_loop_items.remove(config_list)
        self.logger.debug("Items in these lists will be grouped together: "
                          +', '.join(lists_to_group_items))
        self.logger.debug("Items in these lists will be looped over: "
                          +', '.join(lists_to_loop_items))
        return lists_to_group_items, lists_to_loop_items

    def format_thresh(self, thresh):
        """! Format thresholds for file naming 
           
             Args:
                 thresh         - string of the treshold(s)
           
             Return:
                 thresh_symbol  - string of the threshold(s)
                                  with symbols
                 thresh_letters - string of the threshold(s) 
                                  with letters 
        """
        thresh_list = thresh.split(' ')
        thresh_symbol = ''
        thresh_letter = ''
        for thresh in thresh_list:
            if thresh == '':
                continue
            thresh_value = thresh
            for opt in ['>=', '>', '==','!=','<=', '<',
                        'ge', 'gt', 'eq', 'ne', 'le', 'lt']:
                if opt in thresh_value:
                    thresh_opt = opt
                    thresh_value = thresh_value.replace(opt, '')
            if thresh_opt in ['>', 'gt']:
                thresh_symbol+='>'+thresh_value
                thresh_letter+='gt'+thresh_value
            elif thresh_opt in ['>=', 'ge']:
                thresh_symbol+='>='+thresh_value
                thresh_letter+='ge'+thresh_value
            elif thresh_opt in ['<', 'lt']:
                thresh_symbol+='<'+thresh_value
                thresh_letter+='lt'+thresh_value
            elif thresh_opt in ['<=', 'le']:
                thresh_symbol+='<='+thresh_value
                thresh_letter+='le'+thresh_value
            elif thresh_opt in ['==', 'eq']:
                thresh_symbol+='=='+thresh_value
                thresh_letter+='eq'+thresh_value
            elif thresh_opt in ['!=', 'ne']:
                thresh_symbol+='!='+thresh_value
                thresh_letter+='ne'+thresh_value
        return thresh_symbol, thresh_letter

    def build_stringsub_dict(self, date_beg, date_end, date_type,
                             lists_to_loop, lists_to_group, config_dict):
        """! Build a dictionary with list names, dates, and commonly
             used identifiers to pass to string_template_substitution.
            
             Args:
                 date_beg       - string of the beginning date in
                                  YYYYMMDD form
                 date_end       - string of the end date in YYYYMMDD
                                  form
                 date_type      - string of the date type, either
                                  VALID or INIT
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
        stringsub_dict_keys = []
        for loop_list in lists_to_loop:
            list_name = loop_list.replace('_LIST', '')
            stringsub_dict_keys.append(list_name.lower())
        for group_list in lists_to_group:
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
        for special_key in special_keys:
            stringsub_dict_keys.append(special_key)
        stringsub_dict = dict.fromkeys(stringsub_dict_keys, '')
        nkeys_start = len(stringsub_dict_keys)
        # Set full date information
        fcst_hour_list = (
            config_dict['FCST_'+date_type+'_HOUR'].replace('"', '').split(', ')
        )
        obs_hour_list = (
            config_dict['OBS_'+date_type+'_HOUR'].replace('"', '').split(', ')
        )
        if fcst_hour_list != ['']:
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
        if obs_hour_list != ['']:
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
        if fcst_hour_list == obs_hour_list:
            stringsub_dict[date_type.lower()+'_beg'] = (
                 stringsub_dict['fcst_'+date_type.lower()+'_beg']
            )
            stringsub_dict[date_type.lower()+'_end'] = (
                 stringsub_dict['fcst_'+date_type.lower()+'_end']
            )
            if (stringsub_dict[date_type.lower()+'_beg']
                    == stringsub_dict[date_type.lower()+'_end']):
                 stringsub_dict[date_type.lower()] = (
                     stringsub_dict['fcst_'+date_type.lower()+'_beg']
                 )
        if (fcst_hour_list != ['']
                and obs_hour_list == ['']):
            stringsub_dict[date_type.lower()+'_beg'] = (
                stringsub_dict['fcst_'+date_type.lower()+'_beg']
            )
            stringsub_dict[date_type.lower()+'_end'] = (
                stringsub_dict['fcst_'+date_type.lower()+'_end']
            )
            if (stringsub_dict[date_type.lower()+'_beg']
                    == stringsub_dict[date_type.lower()+'_end']):
                stringsub_dict[date_type.lower()] = (
                    stringsub_dict['fcst_'+date_type.lower()+'_beg']
                )
        if (fcst_hour_list == ['']
                and obs_hour_list != ['']):
            stringsub_dict[date_type.lower()+'_beg'] = (
                stringsub_dict['obs_'+date_type.lower()+'_beg']
            )
            stringsub_dict[date_type.lower()+'_end'] = (
                stringsub_dict['obs_'+date_type.lower()+'_end']
            )
            if (stringsub_dict[date_type.lower()+'_beg']
                    == stringsub_dict[date_type.lower()+'_end']):
                stringsub_dict[date_type.lower()] = (
                    stringsub_dict['obs_'+date_type.lower()+'_beg']
                )
        # Set loop information
        for loop_list in lists_to_loop:
            list_name = loop_list.replace('_LIST', '')
            list_name_value = (
                config_dict[list_name].replace('"', '').replace(' ', '')
            )
            if 'THRESH' in list_name:
                thresh_symbol, thresh_letter = self.format_thresh(
                    list_name_value
                )
                stringsub_dict[list_name.lower()] = thresh_letter
            elif list_name == 'MODEL':
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
                .replace(',', '_')
            )
            if 'THRESH' in list_name:
                thresh_symbol, thresh_letter = self.format_thresh(
                    config_dict[list_name]
                )
                stringsub_dict[list_name.lower()] = (
                    thresh_letter.replace(',', '_')
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
            else:
                stringsub_dict[list_name.lower()] = list_name_value
        nkeys_end = len(stringsub_dict_keys)
        # Some lines for debugging if needed in future
        #self.logger.info(nkeys_start)
        #self.logger.info(nkeys_end)
        #for key, value in stringsub_dict.items():
        #    self.logger.info("{} ({})".format(key, value))
        return stringsub_dict

    def get_output_filename(self, output_type, filename_template,
                            filename_type, date_beg, date_end, date_type,
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
                 date_beg          - string of the beginning date in
                                     YYYYMMDD form
                 date_end          - string of the end date in YYYYMMDD
                                     form
                 date_type         - string of the date type, either
                                     VALID or INIT
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
        stringsub_dict = self.build_stringsub_dict(date_beg, date_end,
                                                   date_type, lists_to_loop,
                                                   lists_to_group, config_dict)

        if filename_type == 'default':
            if ('MakePlots' in self.c_dict['PROCESS_LIST'] 
                        and output_type == 'dump_row'):
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
                                +config_dict[list_name]+'Z'
                            )
                        else:
                            filename_template = (
                                filename_template+'_'
                                +list_name.replace('_', '').lower()
                                +config_dict[list_name].replace('"', '')
                            )
        self.logger.debug("Building "+output_type+" filename from "
                          +filename_type+" template: "+filename_template)
        ss = sts.StringSub(self.logger,
                           filename_template,
                           **stringsub_dict)
        output_filename = ss.do_string_sub()
        if filename_type == 'default': 
            output_filename = output_filename+'_'+output_type+'.stat'
        return output_filename

    def get_lookin_dir(self, dir_path, date_beg, date_end, date_type,
                       lists_to_loop, lists_to_group, config_dict):
        """!Fill in necessary information to get the path to
            the lookin directory to pass to stat_analysis.
             
             Args:
                 dir_path          - string of the user provided
                                     directory path
                 date_beg          - string of the beginning date in
                                     YYYYMMDD form
                 date_end          - string of the end date in YYYYMMDD
                                     form
                 date_type         - string of the date type, either
                                     VALID or INIT
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
            stringsub_dict = self.build_stringsub_dict(date_beg, date_end, 
                                                       date_type, 
                                                       lists_to_loop, 
                                                       lists_to_group, 
                                                       config_dict)
            ss = sts.StringSub(self.logger,
                               dir_path,
                               **stringsub_dict)
            dir_path_filled = ss.do_string_sub()
        else:
            dir_path_filled = dir_path
        if '*' in dir_path_filled:
            dir_path_filled_all = str(
                subprocess.check_output('ls -d '+dir_path_filled, shell=True)
            )
            dir_path_filled_all = (
                dir_path_filled_all[1:].replace("'","").replace('\\n', ' ')
            )
            dir_path_filled_all = dir_path_filled_all[:-1]
        else:
            dir_path_filled_all = dir_path_filled
        lookin_dir = dir_path_filled_all
        return lookin_dir

    def format_valid_init(self, date_beg, date_end, date_type,
                          config_dict):
        """! Format the valid and initialization dates and
             hours for the MET stat_analysis config file.

             Args:
                 date_beg    - string of the beginning date in
                               YYYYMMDD form
                 date_end    - string of the end date in YYYYMMDD
                               form
                 date_type   - string of the date type, either
                               VALID or INIT
                 config_dict - dictionary containing the
                               configuration information

             Returns:
                 config_dict - dictionary containing the
                               edited configuration information
                               for valid and initialization dates
                               and hours 
        """
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
        all_conf = self.config.keys('config')
        model_indices = []
        regex = re.compile(r'MODEL(\d+)$')
        for conf in all_conf:
            result = regex.match(conf)
            if result is not None:
                model_indices.append(result.group(1))
        for m in model_indices:
            if self.config.has_option('config', 'MODEL'+m):
                model_name = self.config.getstr('config', 'MODEL'+m)
                model_reference_name = (
                    self.config.getstr('config', 'MODEL'+m+'_REFERENCE_NAME',
                                       model_name)
                )
                if self.config.has_option('dir',
                                          'MODEL'+m
                                          +'_STAT_ANALYSIS_LOOKIN_DIR'):
                    model_dir = (
                        self.config.getraw('dir',
                                           'MODEL'+m
                                           +'_STAT_ANALYSIS_LOOKIN_DIR')
                    )
                else:
                    self.log_error("MODEL"+m+"_STAT_ANALYSIS_LOOKIN_DIR "
                                      +"was not set.")
                    exit(1)
                if self.config.has_option('config', 'MODEL'+m+'_OBTYPE'):
                    model_obtype = (
                        self.config.getstr('config', 'MODEL'+m+'_OBTYPE')
                    )
                else:
                    self.log_error("MODEL"+m+"_OBTYPE was not set.")
                    exit(1)
                for output_type in [ 'DUMP_ROW', 'OUT_STAT' ]:
                    if (self.config.has_option('filename_templates', 'MODEL'+m
                                               +'_STAT_ANALYSIS_'+output_type
                                               +'_TEMPLATE')):
                        model_filename_template = (
                            self.config.getraw('filename_templates', 
                                               'MODEL'+m+'_STAT_ANALYSIS_'
                                               +output_type+'_TEMPLATE')
                        )
                        if model_filename_template == '':
                            model_filename_template = (
                                '{model?fmt=%s}_{obtype?fmt=%s}_'
                            )
                            model_filename_type = 'default'
                        else:
                            model_filename_type = 'user'
                    else:
                        if (self.config.has_option('filename_templates',
                                                   'STAT_ANALYSIS_'
                                                   +output_type+'_TEMPLATE')):
                            model_filename_template = (
                                self.config.getraw('filename_templates',
                                                   'STAT_ANALYSIS_'
                                                   +output_type+'_TEMPLATE')
                            )
                            if model_filename_template == '':
                                model_filename_template = (
                                    '{model?fmt=%s}_{obtype?fmt=%s}_'
                                )
                                model_filename_type = 'default'
                            else:
                                model_filename_type = 'user'
                        else:
                            if 'MakePlots' in self.c_dict['PROCESS_LIST']:
                                model_filename_template = (
                                    model_reference_name+'_{obtype?fmt=%s}_'
                                )
                            else:
                                model_filename_template = (
                                    '{model?fmt=%s}_{obtype?fmt=%s}_'
                                )
                            model_filename_type = 'default'
                    if output_type == 'DUMP_ROW':
                         model_dump_row_filename_template = (
                             model_filename_template
                         )
                         model_dump_row_filename_type = model_filename_type
                    elif output_type == 'OUT_STAT':
                        if 'MakePlots' in self.c_dict['PROCESS_LIST']:
                            model_out_stat_filename_template = 'NA'
                            model_out_stat_filename_type = 'NA'
                        else:
                            model_out_stat_filename_template = (
                                model_filename_template
                            )
                            model_out_stat_filename_type = model_filename_type
            else:
                self.log_error("MODEL"+m+" was not set.")
                exit(1)
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
        return model_info_list, model_indices

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
            level = f"'{util.remove_quotes(level)}'"
            level_list.append(level)

        return level_list

    def run_stat_analysis_job(self, date_beg, date_end, date_type):
        """! This runs stat_analysis over a period of valid
             or initialization dates for a job defined by
             the user.
              
             Args:
                 date_beg    - string of the beginning date in
                               YYYYMMDD form
                 date_end    - string of the end date in YYYYMMDD
                               form
                 date_type   - string of the date type, either
                               VALID or INIT
            
             Returns:

        """
        self.c_dict['JOB_NAME'] = self.config.getstr('config', 
                                                     'STAT_ANALYSIS_JOB_NAME')
        self.c_dict['JOB_ARGS'] = self.config.getstr('config', 
                                                     'STAT_ANALYSIS_JOB_ARGS')
        self.c_dict['VAR_LIST'] = util.parse_var_list(self.config)
        self.c_dict['FCST_VAR_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_VAR_LIST', '')
        )
        self.c_dict['OBS_VAR_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_VAR_LIST', '')
        )
        self.c_dict['FCST_UNITS_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_UNITS_LIST', '')
        )
        self.c_dict['OBS_UNITS_LIST'] = util.getlist(
            self.config.getstr('config', 'OBS_UNITS_LIST', '')
        )

        self.c_dict['FCST_LEVEL_LIST'] = self.get_level_list('FCST')
        self.c_dict['OBS_LEVEL_LIST'] = self.get_level_list('OBS')

        self.c_dict['FCST_THRESH_LIST'] = util.getlist(
            self.config.getstr('config', 'FCST_THRESH_LIST', '')
        )
        self.c_dict['OBS_THRESH_LIST'] =  util.getlist(
            self.config.getstr('config', 'OBS_THRESH_LIST', '')
        ) 
        # Do some preprocessing, formatting, and gathering
        # of config information.
        formatted_c_dict = copy.deepcopy(self.c_dict)
        model_info_list, model_indices = self.parse_model_info()
        if self.c_dict['MODEL_LIST'] == []:
            if model_indices > 0:
                self.logger.warning("MODEL_LIST was left blank, "
                                    +"creating with MODELn information.")
                model_name_list = []
                for model_info in model_info_list:
                    model_name_list.append(model_info['name'])
                formatted_c_dict['MODEL_LIST'] = model_name_list
            else:
                self.log_error("No model information was found.")
                exit(1)
        for fcst_valid_hour in self.c_dict['FCST_VALID_HOUR_LIST']:
            index = self.c_dict['FCST_VALID_HOUR_LIST'].index(fcst_valid_hour)
            formatted_c_dict['FCST_VALID_HOUR_LIST'][index] = (
                fcst_valid_hour.ljust(6,'0')
            )
        for fcst_init_hour in self.c_dict['FCST_INIT_HOUR_LIST']:
            index = self.c_dict['FCST_INIT_HOUR_LIST'].index(fcst_init_hour)
            formatted_c_dict['FCST_INIT_HOUR_LIST'][index] = (
                fcst_init_hour.ljust(6,'0')
            )
        for obs_valid_hour in self.c_dict['OBS_VALID_HOUR_LIST']:
            index = self.c_dict['OBS_VALID_HOUR_LIST'].index(obs_valid_hour)
            formatted_c_dict['OBS_VALID_HOUR_LIST'][index] = (
                obs_valid_hour.ljust(6,'0')
            )
        for obs_init_hour in self.c_dict['OBS_INIT_HOUR_LIST']:
            index = self.c_dict['OBS_INIT_HOUR_LIST'].index(obs_init_hour)
            formatted_c_dict['OBS_INIT_HOUR_LIST'][index] = (
                obs_init_hour.ljust(6,'0')
            )
        for fcst_lead in self.c_dict['FCST_LEAD_LIST']:
            index = self.c_dict['FCST_LEAD_LIST'].index(fcst_lead)
            if len(fcst_lead)%2 == 0:
                formatted_fcst_lead = fcst_lead.ljust(6,'0')
            else:
                formatted_fcst_lead = fcst_lead.ljust(7,'0')
            formatted_c_dict['FCST_LEAD_LIST'][index] = formatted_fcst_lead
        for obs_lead in self.c_dict['OBS_LEAD_LIST']:
            index = self.c_dict['OBS_LEAD_LIST'].index(obs_lead)
            if len(obs_lead)%2 == 0:
                formatted_obs_lead = obs_lead.ljust(6,'0')
            else:
                formatted_obs_lead = obs_lead.ljust(7,'0')
            formatted_c_dict['OBS_LEAD_LIST'][index] = formatted_obs_lead
        # Parse whether all expected METplus config _LIST variables
        # to be treated as a loop or group.
        config_lists_to_group_items = formatted_c_dict['GROUP_LIST_ITEMS']
        config_lists_to_loop_items = formatted_c_dict['LOOP_LIST_ITEMS']
        lists_to_group_items, lists_to_loop_items = (
            self.set_lists_loop_or_group(config_lists_to_group_items, 
                                         config_lists_to_loop_items,
                                         formatted_c_dict)
        )
        runtime_setup_dict = {}
        # Fill setup dictionary for MET config variable name
        # and its value as a string for group lists.
        for list_to_group_items in lists_to_group_items:
            runtime_setup_dict_name = list_to_group_items.replace('_LIST', '')
            if 'THRESH' in list_to_group_items:
                runtime_setup_dict_value = (
                    [', '.join(formatted_c_dict[list_to_group_items])]
                )
            else:
                runtime_setup_dict_value = (
                    [self.list_to_str(formatted_c_dict[list_to_group_items])]
                )
            runtime_setup_dict[runtime_setup_dict_name] = (
                runtime_setup_dict_value
            )
        # Fill setup dictionary for MET config variable name
        # and its value as a list for loop lists. Some items
        # in lists need to be formatted now, others done later.
        format_later_list = [
            'MODEL_LIST', 'FCST_VALID_HOUR_LIST', 'OBS_VALID_HOUR_LIST',
            'FCST_INIT_HOUR_LIST','OBS_INIT_HOUR_LIST'
        ]
        for list_to_loop_items in lists_to_loop_items:
            if list_to_loop_items not in format_later_list:
                for item in formatted_c_dict[list_to_loop_items]:
                    index = formatted_c_dict[list_to_loop_items].index(item)
                    if 'THRESH' in list_to_loop_items:
                        formatted_c_dict[list_to_loop_items][index] = (
                            item
                        )
                    else:
                        formatted_c_dict[list_to_loop_items][index] = (
                            '"'+item+'"'
                        )
            runtime_setup_dict_name = list_to_loop_items.replace('_LIST', '')
            runtime_setup_dict_value = formatted_c_dict[list_to_loop_items]
            runtime_setup_dict[runtime_setup_dict_name] = (
                runtime_setup_dict_value
            )
        # Create run time dictionary with all the combinations
        # of settings to be run. 
        runtime_setup_dict_names = sorted(runtime_setup_dict)
        runtime_settings_dict_list = (
            [dict(zip(runtime_setup_dict_names, prod)) for prod in
             itertools.product(*(runtime_setup_dict[name] for name in
             runtime_setup_dict_names))]
        )
        # Loop over run settings.
        for runtime_settings_dict in runtime_settings_dict_list:
            self.param = self.c_dict['CONFIG_FILE']
            # Set up stat_analysis -lookin argument, model and obs information
            # and stat_analysis job.
            job = '-job '+self.c_dict['JOB_NAME']+' '+self.c_dict['JOB_ARGS']
            nmodels = len(runtime_settings_dict['MODEL'].split(', '))
            if nmodels == 1:
                for m in model_indices:
                    model_check = (
                        runtime_settings_dict['MODEL'].replace('"', '')
                    )
                    if self.config.getstr('config', 'MODEL'+m) == model_check:
                        break
                model_info = model_info_list[int(m)-1]
                runtime_settings_dict['MODEL'] = '"'+model_info['name']+'"'
                runtime_settings_dict['OBTYPE'] = '"'+model_info['obtype']+'"'
                lookin_dir = self.get_lookin_dir(model_info['dir'], date_beg,
                                                 date_end, date_type, 
                                                 lists_to_loop_items, 
                                                 lists_to_group_items,
                                                 runtime_settings_dict)
                if '-dump_row' in self.c_dict['JOB_ARGS']:
                    dump_row_filename_template = (
                        model_info['dump_row_filename_template']
                    )
                    dump_row_filename_type = (
                        model_info['dump_row_filename_type']
                    )
                if '-out_stat' in self.c_dict['JOB_ARGS']:
                    out_stat_filename_template = (
                        model_info['out_stat_filename_template']
                    )
                    out_stat_filename_type = (
                        model_info['out_stat_filename_type']
                    )
            else:
                lookin_dir = ''
                model_list = []
                obtype_list = []
                for m in model_indices:
                    model_info = model_info_list[int(m)-1]
                    model_list.append(model_info['name'])
                    obtype_list.append(model_info['obtype'])
                    lookin_dir_m = self.get_lookin_dir(model_info['dir'], 
                                                       date_beg, date_end,
                                                       date_type, 
                                                       lists_to_loop_items, 
                                                       lists_to_group_items,
                                                       runtime_settings_dict)
                    lookin_dir = lookin_dir+' '+lookin_dir_m
                runtime_settings_dict['MODEL'] = self.list_to_str(model_list)
                runtime_settings_dict['OBTYPE'] = self.list_to_str(obtype_list)
                if '-dump_row' in self.c_dict['JOB_ARGS']:
                    dump_row_filename_template = (
                        self.config.getraw('filename_templates',
                                           'STAT_ANALYSIS_DUMP_ROW_TEMPLATE',
                                           '')
                    )
                    if dump_row_filename_template == '':
                        dump_row_filename_type = 'default'
                    else:
                        dump_row_filename_type = 'user'
                if '-out_stat' in self.c_dict['JOB_ARGS']:
                    out_stat_filename_template = (
                        self.config.getraw('filename_templates',
                                           'STAT_ANALYSIS_OUT_STAT_TEMPLATE',
                                           '')
                    )
                    if out_stat_filename_template == '':
                        out_stat_filename_type = 'default'
                    else:
                        out_stat_filename_type = 'user'
            runtime_settings_dict['-lookin'] = lookin_dir
            self.set_lookin_dir(runtime_settings_dict['-lookin'])
            if '-dump_row' in self.c_dict['JOB_ARGS']:
                dump_row_filename = (
                    self.get_output_filename('dump_row', 
                                             dump_row_filename_template,
                                             dump_row_filename_type,
                                             date_beg, date_end,
                                             date_type, lists_to_loop_items, 
                                             lists_to_group_items,
                                             runtime_settings_dict)
                )
                dump_row_file = os.path.join(self.c_dict['OUTPUT_BASE_DIR'],
                                             dump_row_filename)
                job = job.replace('[dump_row_file]', dump_row_file)
                job = job.replace('[dump_row_filename]', dump_row_file)
                dump_row_output_dir = dump_row_file.rpartition('/')[0]
                if not os.path.exists(dump_row_output_dir):
                   util.mkdir_p(dump_row_output_dir)
            if '-out_stat' in self.c_dict['JOB_ARGS']:
                out_stat_filename = (
                    self.get_output_filename('out_stat', 
                                             out_stat_filename_template,
                                             out_stat_filename_type,
                                             date_beg, date_end,
                                             date_type,lists_to_loop_items, 
                                             lists_to_group_items,
                                             runtime_settings_dict)
                )
                out_stat_file = os.path.join(self.c_dict['OUTPUT_BASE_DIR'],
                                             out_stat_filename)
                job = job.replace('[out_stat_file]', out_stat_file)
                job = job.replace('[out_stat_filename]', out_stat_file)
                out_stat_output_dir = out_stat_file.rpartition('/')[0]
                if not os.path.exists(out_stat_output_dir):
                   util.mkdir_p(out_stat_output_dir)
            runtime_settings_dict['JOB'] = job 
            # Set up forecast and observation valid
            # and initialization time information.
            runtime_settings_dict = (
                self.format_valid_init(date_beg, date_end, date_type, 
                                       runtime_settings_dict)
            )
            # Set environment variables and run stat_analysis.
            self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
            for name, value in runtime_settings_dict.items():
                self.add_env_var(name, value)
                self.logger.debug(name+": "+value)
            cmd = self.get_command()
            if cmd is None:
                self.log_error("stat_analysis could not generate command")
                return

            # send environment variables to logger
            self.print_all_envs()

            self.build()
            self.clear()

    def filter_for_plotting(self):
        """! Special case for running stat_analysis over a period of 
             valid or initialization dates for a filter job, so 
             MakePlots can be run correctly following StatAnalysis.
             This method loops over MODEL_LIST, . 
             Args:

             Returns:

        """
        # Do checks for bad configuration file options.
        bad_config_variable_list = [
            'FCST_VAR_LIST', 'FCST_LEVEL_LIST', 
            'FCST_THRESH_LIST', 'FCST_UNITS_LIST',
            'OBS_VAR_LIST', 'OBS_LEVEL_LIST', 
            'OBS_THRESH_LIST', 'OBS_UNITS_LIST'
        ]
        for bad_config_variable in bad_config_variable_list:
            if self.config.has_option('config',
                                      bad_config_variable):
                self.log_error("Bad config option for running StatAnalysis "
                                  "followed by MakePlots. Please remove "
                                  +bad_config_variable+" and set using FCST/OBS_VARn")
                exit(1)
        loop_group_accepted_options = [ 
            'FCST_VALID_HOUR_LIST', 'FCST_INIT_HOUR_LIST', 
            'OBS_VALID_HOUR_LIST', 'OBS_INIT_HOUR_LIST'
        ]
        for config_list in self.c_dict['GROUP_LIST_ITEMS']:
            if config_list not in loop_group_accepted_options:
                self.log_error("Bad config option for running StatAnalysis "
                                  +"followed by MakePlots. Only accepted "
                                  +"values in GROUP_LIST_ITEMS are "
                                  +"FCST_VALID_HOUR_LIST, "
                                  +"FCST_INIT_HOUR_LIST, "
                                  +"OBS_VALID_HOUR_LIST, "
                                  +"OBS_INIT_HOUR_LIST. "
                                  +"Found "+config_list)
                exit(1) 
        for config_list in self.c_dict['LOOP_LIST_ITEMS']:
            if config_list not in loop_group_accepted_options:
                self.log_error("Bad config option for running StatAnalysis "
                                  +"followed by MakePlots. Only accepted "
                                  +"values in LOOP_LIST_ITEMS are "
                                  +"FCST_VALID_HOUR_LIST, "
                                  +"FCST_INIT_HOUR_LIST, "
                                  +"OBS_VALID_HOUR_LIST, "
                                  +"OBS_INIT_HOUR_LIST. "
                                  +"Found "+config_list)
                exit(1)
        # Do checks for required configuration file options that are
        # defined by user.
        required_config_variable_list = [ 
            'VX_MASK_LIST', 'FCST_LEAD_LIST', 'LINE_TYPE_LIST' 
            ]
        for required_config_variable in required_config_variable_list:
            if len(self.c_dict[required_config_variable]) == 0:
                self.log_error(required_config_variable+" has no items. "
                                  +"This list must have items to run "
                                  +"StatAnalysis followed by MakePlots.")
                exit(1)
        # Do some preprocessing, formatting, and gathering
        # of config information.
        date_type = self.c_dict['DATE_TYPE']
        formatted_c_dict = copy.deepcopy(self.c_dict)
        model_info_list, model_indices = self.parse_model_info()
        if self.c_dict['MODEL_LIST'] == []:
            if model_indices > 0:
                self.logger.warning("MODEL_LIST was left blank, "
                                    +"creating with MODELn information.")
                model_name_list = []
                for model_info in model_info_list:
                    model_name_list.append(model_info['name'])
                formatted_c_dict['MODEL_LIST'] = model_name_list
            else:
                self.log_error("No model information was found.")
                exit(1)
        # Add additional variable information to
        # c_dict['VAR_LIST'] and make individual dictionaries
        # for each threshold
        var_info_c_dict_list = self.c_dict['VAR_LIST']
        var_info_list = []
        for var_info_c_dict in var_info_c_dict_list:
            n = var_info_c_dict['index']
            fcst_units = self.config.getstr('config', 
                                            'FCST_VAR'+n+'_UNITS',
                                            '')
            obs_units = self.config.getstr('config', 
                                           'OBS_VAR'+n+'_UNITS',
                                           '')
            if len(obs_units) == 0 and len(fcst_units) != 0:
                obs_units = fcst_units
            if len(fcst_units) == 0 and len(obs_units) != 0:
                fcst_units = obs_units
            run_fourier = (
                self.config.getbool('config', 
                                    'VAR'+n+'_FOURIER_DECOMP',
                                    False)
            )
            fourier_wave_num_pairs = util.getlist(
                self.config.getstr('config', 
                                   'VAR'+n+'_WAVE_NUM_LIST',
                                   '')
            )
            if len(var_info_c_dict['fcst_thresh']) > 0:
                for fcst_thresh in var_info_c_dict['fcst_thresh']:
                    thresh_index = (
                        var_info_c_dict['fcst_thresh'].index(fcst_thresh)
                    )
                    obs_thresh = (
                        var_info_c_dict['obs_thresh'][thresh_index]
                    )
                    if run_fourier == False:
                        var_info = {}
                        var_info['index'] = var_info_c_dict['index']
                        var_info['fcst_name'] = [ 
                            var_info_c_dict['fcst_name'] 
                        ]
                        var_info['obs_name'] = [ 
                            var_info_c_dict['obs_name'] 
                        ]
                        var_info['fcst_level'] = [ 
                            var_info_c_dict['fcst_level']
                        ]
                        var_info['obs_level'] = [ 
                            var_info_c_dict['obs_level'] 
                        ]
                        var_info['fcst_extra'] = [ 
                            var_info_c_dict['fcst_extra'] 
                        ]
                        var_info['obs_extra'] = [ 
                            var_info_c_dict['obs_extra']
                        ]
                        var_info['fcst_thresh'] = [fcst_thresh]
                        var_info['obs_thresh'] = [obs_thresh]
                        if len(fcst_units) == 0:
                            var_info['fcst_units'] = []
                        else:
                            var_info['fcst_units'] = [fcst_units]
                        if len(obs_units) == 0:
                            var_info['obs_units'] = []
                        else:
                            var_info['obs_units'] = [obs_units]
                        var_info['run_fourier'] = run_fourier
                        var_info['fourier_wave_num'] = []
                        var_info_list.append(var_info)
                    else:
                        for pair in fourier_wave_num_pairs:
                            var_info = {}
                            var_info['index'] = var_info_c_dict['index']
                            var_info['fcst_name'] = [ 
                                var_info_c_dict['fcst_name'] 
                            ]
                            var_info['obs_name'] = [ 
                                var_info_c_dict['obs_name']
                            ]
                            var_info['fcst_level'] = [ 
                                var_info_c_dict['fcst_level'] 
                            ]
                            var_info['obs_level'] = [ 
                                var_info_c_dict['obs_level'] 
                            ]
                            var_info['fcst_extra'] = [ 
                                var_info_c_dict['fcst_extra']
                            ]
                            var_info['obs_extra'] = [ 
                                var_info_c_dict['obs_extra']
                            ]
                            var_info['fcst_thresh'] = [fcst_thresh]
                            var_info['obs_thresh'] = [obs_thresh]
                            if len(fcst_units) == 0:
                                var_info['fcst_units'] = []
                            else:
                                var_info['fcst_units'] = [fcst_units]
                            if len(obs_units) == 0:
                                var_info['obs_units'] = []
                            else:
                                var_info['obs_units'] = [obs_units]
                            var_info['run_fourier'] = run_fourier
                            var_info['fourier_wave_num'] = ['WV1_'+pair]
                            var_info_list.append(var_info)
            else:
                if run_fourier == False:
                    var_info = {}
                    var_info['index'] = var_info_c_dict['index'] 
                    var_info['fcst_name'] = [var_info_c_dict['fcst_name']]
                    var_info['obs_name'] = [var_info_c_dict['obs_name']]
                    var_info['fcst_level'] = [var_info_c_dict['fcst_level']]
                    var_info['obs_level'] = [var_info_c_dict['obs_level']]
                    var_info['fcst_extra'] = [var_info_c_dict['fcst_extra']]
                    var_info['obs_extra'] = [var_info_c_dict['obs_extra']]
                    var_info['fcst_thresh'] = [] 
                    var_info['obs_thresh'] = []
                    if len(fcst_units) == 0:
                        var_info['fcst_units'] = []
                    else:
                        var_info['fcst_units'] = [fcst_units]
                    if len(obs_units) == 0:
                        var_info['obs_units'] = []
                    else:
                        var_info['obs_units'] = [obs_units]
                    var_info['run_fourier'] = run_fourier
                    var_info['fourier_wave_num'] = []
                    var_info_list.append(var_info)
                else:
                    for pair in fourier_wave_num_pairs:
                        var_info = {}
                        var_info['index'] = var_info_c_dict['index']
                        var_info['fcst_name'] = [ 
                            var_info_c_dict['fcst_name']
                        ]
                        var_info['obs_name'] = [ 
                            var_info_c_dict['obs_name'] 
                        ]
                        var_info['fcst_level'] = [ 
                            var_info_c_dict['fcst_level'] 
                        ]
                        var_info['obs_level'] = [ 
                            var_info_c_dict['obs_level'] 
                        ]
                        var_info['fcst_extra'] = [ 
                            var_info_c_dict['fcst_extra'] 
                        ]
                        var_info['obs_extra'] = [ 
                            var_info_c_dict['obs_extra'] 
                        ]
                        var_info['fcst_thresh'] = []
                        var_info['obs_thresh'] = []
                        if len(fcst_units) == 0:
                            var_info['fcst_units'] = []
                        else:
                            var_info['fcst_units'] = [fcst_units]
                        if len(obs_units) == 0:
                            var_info['obs_units'] = []
                        else:
                            var_info['obs_units'] = [obs_units]
                        var_info['run_fourier'] = run_fourier
                        var_info['fourier_wave_num'] = ['WV1_'+pair]
                        var_info_list.append(var_info)
        for fcst_valid_hour in self.c_dict['FCST_VALID_HOUR_LIST']:
            index = self.c_dict['FCST_VALID_HOUR_LIST'].index(fcst_valid_hour)
            formatted_c_dict['FCST_VALID_HOUR_LIST'][index] = (
                fcst_valid_hour.ljust(6,'0')
            )
        for fcst_init_hour in self.c_dict['FCST_INIT_HOUR_LIST']:
            index = self.c_dict['FCST_INIT_HOUR_LIST'].index(fcst_init_hour)
            formatted_c_dict['FCST_INIT_HOUR_LIST'][index] = (
                fcst_init_hour.ljust(6,'0')
            )
        for obs_valid_hour in self.c_dict['OBS_VALID_HOUR_LIST']:
            index = self.c_dict['OBS_VALID_HOUR_LIST'].index(obs_valid_hour)
            formatted_c_dict['OBS_VALID_HOUR_LIST'][index] = (
                obs_valid_hour.ljust(6,'0')
            )
        for obs_init_hour in self.c_dict['OBS_INIT_HOUR_LIST']:
            index = self.c_dict['OBS_INIT_HOUR_LIST'].index(obs_init_hour)
            formatted_c_dict['OBS_INIT_HOUR_LIST'][index] = (
                obs_init_hour.ljust(6,'0')
            )
        for fcst_lead in self.c_dict['FCST_LEAD_LIST']:
            index = self.c_dict['FCST_LEAD_LIST'].index(fcst_lead)
            if len(fcst_lead)%2 == 0:
                formatted_fcst_lead = fcst_lead.ljust(6,'0')
            else:
                formatted_fcst_lead = fcst_lead.ljust(7,'0')
            formatted_c_dict['FCST_LEAD_LIST'][index] = formatted_fcst_lead
        for obs_lead in self.c_dict['OBS_LEAD_LIST']:
            index = self.c_dict['OBS_LEAD_LIST'].index(obs_lead)
            if len(obs_lead)%2 == 0:
                formatted_obs_lead = obs_lead.ljust(6,'0')
            else:
                formatted_obs_lead = obs_lead.ljust(7,'0')
            formatted_c_dict['OBS_LEAD_LIST'][index] = formatted_obs_lead
        output_base_dir = self.c_dict['OUTPUT_BASE_DIR']
        if not os.path.exists(output_base_dir):
            util.mkdir_p(output_base_dir)
        # Loop through variables and add information
        # to a special variable dictionary
        for var_info in var_info_list:
            var_info_formatted_c_dict = copy.deepcopy(formatted_c_dict)
            var_info_formatted_c_dict['FCST_VAR_LIST'] = var_info['fcst_name']
            var_info_formatted_c_dict['FCST_LEVEL_LIST'] = (
                var_info['fcst_level'] 
            )
            var_info_formatted_c_dict['FCST_UNITS_LIST'] = (
                var_info['fcst_units']
            )
            var_info_formatted_c_dict['OBS_VAR_LIST'] = var_info['obs_name']
            var_info_formatted_c_dict['OBS_LEVEL_LIST'] = (
                var_info['obs_level']
            )
            var_info_formatted_c_dict['OBS_UNITS_LIST'] = (
                var_info['obs_units']
            )
            var_info_formatted_c_dict['FCST_THRESH_LIST'] = (
                var_info['fcst_thresh']
            )
            var_info_formatted_c_dict['OBS_THRESH_LIST'] = (
                var_info['obs_thresh']
            )
            if var_info['run_fourier'] == True:
                for fvn in var_info['fourier_wave_num']:
                    var_info_formatted_c_dict['INTERP_MTHD_LIST'] \
                    .append(fvn)
            # Parse whether all expected METplus config _LIST variables
            # to be treated as a loop or group.
            config_lists_to_group_items = (
                var_info_formatted_c_dict['GROUP_LIST_ITEMS']
            )
            config_lists_to_loop_items = (
                var_info_formatted_c_dict['LOOP_LIST_ITEMS']
            )
            lists_to_group_items, lists_to_loop_items = (
                self.set_lists_loop_or_group(config_lists_to_group_items,
                                             config_lists_to_loop_items,
                                             var_info_formatted_c_dict)
            )
            runtime_setup_dict = {}
            # Fill setup dictionary for MET config variable name
            # and its value as a string for group lists.
            for list_to_group_items in lists_to_group_items:
                runtime_setup_dict_name = (
                    list_to_group_items.replace('_LIST', '')
                )
                if 'THRESH' in list_to_group_items:
                    runtime_setup_dict_value = [
                        ' '.join(
                            var_info_formatted_c_dict[list_to_group_items]
                        )
                    ]
                else:
                    runtime_setup_dict_value = [
                        self.list_to_str(
                            var_info_formatted_c_dict[list_to_group_items]
                        )
                    ]
                runtime_setup_dict[runtime_setup_dict_name] = (
                    runtime_setup_dict_value
                )
            # Fill setup dictionary for MET config variable name
            # and its value as a list for loop lists. Some items
            # in lists need to be formatted now, others done later.
            format_later_list = [
                'MODEL_LIST', 'FCST_VALID_HOUR_LIST', 'OBS_VALID_HOUR_LIST',
                'FCST_INIT_HOUR_LIST','OBS_INIT_HOUR_LIST'
            ]
            for list_to_loop_items in lists_to_loop_items:
                runtime_setup_dict_name = list_to_loop_items.replace('_LIST', 
                                                                     '')
                if list_to_loop_items not in format_later_list:
                    for item in \
                             var_info_formatted_c_dict[list_to_loop_items]:
                        index = (
                            var_info_formatted_c_dict[list_to_loop_items] \
                            .index(item)
                        )
                        if 'THRESH' in list_to_loop_items:
                            var_info_formatted_c_dict[list_to_loop_items] \
                                    [index] \
                                = item
                        else:
                            var_info_formatted_c_dict[list_to_loop_items] \
                                    [index] \
                                = '"'+item+'"'
                runtime_setup_dict_name = list_to_loop_items.replace('_LIST', 
                                                                     '')
                runtime_setup_dict_value = (
                    var_info_formatted_c_dict[list_to_loop_items]
                )
                runtime_setup_dict[runtime_setup_dict_name] = (
                    runtime_setup_dict_value
                )
            # Create run time dictionary with all the combinations
            # of settings to be run.
            runtime_setup_dict_names = sorted(runtime_setup_dict)
            runtime_settings_dict_list = (
                [dict(zip(runtime_setup_dict_names, prod)) for prod in
                itertools.product(*(runtime_setup_dict[name] for name in
                runtime_setup_dict_names))]
            )
            # Loop over run settings.
            for runtime_settings_dict in runtime_settings_dict_list:
                self.param = self.c_dict['CONFIG_FILE']
                # Set up stat_analysis -lookin argument, model and obs
                # information and stat_analysis job.
                job = '-job filter -dump_row '
                for m in model_indices:
                    model_check = (
                        runtime_settings_dict['MODEL'].replace('"', '')
                    )
                    if (self.config.getstr('config', 'MODEL'+m) 
                            == model_check):
                        break
                model_info = model_info_list[int(m)-1]
                runtime_settings_dict['MODEL'] = '"'+model_info['name']+'"'
                runtime_settings_dict['OBTYPE'] = '"'+model_info['obtype']+'"'
                lookin_dir = self.get_lookin_dir(model_info['dir'], 
                                                 self.c_dict[date_type+'_BEG'],
                                                 self.c_dict[date_type+'_END'],
                                                 date_type, 
                                                 lists_to_loop_items,
                                                 lists_to_group_items,
                                                 runtime_settings_dict)
                runtime_settings_dict['-lookin'] = lookin_dir
                self.set_lookin_dir(runtime_settings_dict['-lookin'])
                dump_row_filename_template = (
                    model_info['dump_row_filename_template']
                )
                dump_row_filename_type = model_info['dump_row_filename_type']
                dump_row_filename = (
                    self.get_output_filename('dump_row', 
                                             dump_row_filename_template, 
                                             dump_row_filename_type,
                                             self.c_dict[date_type+'_BEG'],
                                             self.c_dict[date_type+'_END'],
                                             date_type, lists_to_loop_items, 
                                             lists_to_group_items,
                                             runtime_settings_dict)
                )
                dump_row_file = os.path.join(self.c_dict['OUTPUT_BASE_DIR'],
                                             dump_row_filename)
                dump_row_output_dir = dump_row_file.rpartition('/')[0]
                if not os.path.exists(dump_row_output_dir):
                   util.mkdir_p(dump_row_output_dir)
                runtime_settings_dict['JOB'] = job+dump_row_file
                # Set up forecast and observation valid and 
                # initialization time information.
                runtime_settings_dict = (
                    self.format_valid_init(self.c_dict[date_type+'_BEG'], 
                                           self.c_dict[date_type+'_END'], 
                                           date_type, 
                                           runtime_settings_dict)
                )
                # Set environment variables and run stat_analysis.
                self.logger.debug("STAT_ANALYSIS RUN SETTINGS....")
                for name, value in runtime_settings_dict.items():
                    self.add_env_var(name, value)
                    self.logger.debug(name+": "+value)
                cmd = self.get_command()
                if cmd is None:
                    self.log_error("stat_analysis could not generate "+
                                      "command")
                    return

                # send environment variables to logger
                self.print_all_envs()

                self.build()
                self.clear()

    def run_all_times(self):
        self.c_dict['DATE_TYPE'] = self.config.getstr('config', 'DATE_TYPE')
        self.c_dict['VALID_BEG'] = self.config.getstr('config', 'VALID_BEG',
                                                                '')
        self.c_dict['VALID_END'] = self.config.getstr('config', 'VALID_END',
                                                      '')
        self.c_dict['INIT_BEG'] = self.config.getstr('config', 'INIT_BEG', '')
        self.c_dict['INIT_END'] = self.config.getstr('config', 'INIT_END', '')
        date_type = self.c_dict['DATE_TYPE']
        if date_type not in ['VALID', 'INIT']:
            self.log_error("DATE_TYPE must be VALID or INIT")
            exit(1)
        if 'MakePlots' in self.c_dict['PROCESS_LIST']:
            self.filter_for_plotting()
        else:
            date_beg = self.c_dict[date_type+'_BEG']
            date_end = self.c_dict[date_type+'_END']
            self.run_stat_analysis_job(date_beg, date_end, date_type)

    def run_at_time(self, input_dict):
        loop_by = self.config.getstr('config', 'LOOP_BY')
        if loop_by in ['VALID', 'INIT']:
            date = input_dict[loop_by.lower()].strftime('%Y%m%d')
            self.run_stat_analysis_job(date, date, loop_by)
        else:
            self.log_error("LOOP_BY must be VALID or INIT")
            exit(1)

if __name__ == "__main__":
    util.run_stand_alone(__file__, "StatAnalysis")
