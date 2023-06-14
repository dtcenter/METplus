"""
Program Name: tc_pairs_wrapper.py
Contact(s): Julie Prestopnik, Minna Win, Jim Frimel, George McCabe
Abstract: Invokes the MET tool tc_pairs to parse ADeck and BDeck files
   (ATCF formatted and SBU GFS extra tropical cyclone, non-ATCF formatted),
   filter the data, and match them up or just pass in the top level
   ADeck and BDeck directories to MET tc_pairs (slower)
History Log:  Initial version
Usage:
Parameters: None
Input Files: adeck and bdeck files
Output Files: tc_pairs files
Condition codes: 0 for success, 1 for failure

"""

import os
import re
import csv
import datetime
import glob

from ..util import getlist, get_lead_sequence, skip_time, mkdir_p
from ..util import ti_calculate
from ..util import do_string_sub
from ..util import get_tags, find_indices_in_config_section
from ..util.met_config import add_met_config_dict_list
from ..util import time_generator, log_runtime_banner, add_to_time_input
from . import CommandBuilder

'''!@namespace TCPairsWrapper
@brief Wraps the MET tool tc_pairs to parse ADeck and BDeck ATCF_by_pairs
 files, filter the data, and match them up.
Call as follows:
@code{.sh}
tc_pairs_wrapper.py [-c /path/to/user.template.conf]
@endcode
'''

class TCPairsWrapper(CommandBuilder):
    """!Wraps the MET tool, tc_pairs to parse and match ATCF_by_pairs adeck and
       bdeck files.  Pre-processes extra tropical cyclone data.
    """

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_STORM_ID',
        'METPLUS_BASIN',
        'METPLUS_CYCLONE',
        'METPLUS_STORM_NAME',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_INIT_INC',
        'METPLUS_INIT_EXC',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_DLAND_FILE',
        'METPLUS_CONSENSUS_LIST',
        'METPLUS_WRITE_VALID',
        'METPLUS_VALID_INC',
        'METPLUS_VALID_EXC',
        'METPLUS_CHECK_DUP',
        'METPLUS_INTERP12',
        'METPLUS_MATCH_POINTS',
        'METPLUS_DIAG_INFO_MAP_LIST',
        'METPLUS_DIAG_CONVERT_MAP_LIST',
    ]

    WILDCARDS = {
        'basin': '??',
        'cyclone': '*',
    }

    REGEXES = {
        'storm_id': r'^(\w{2})(\d{2})(\d{4})$',
        'basin': r'[a-zA-Z]{2}',
        'cyclone': r'[0-9]{2,4}',
    }

    def __init__(self, config, instance=None):
        self.app_name = 'tc_pairs'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """! Create a dictionary containing all the values set in the
         config file. This will make it easier for unit testing.

             @returns Dictionary of the values from the config file
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_PAIRS_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        c_dict['MISSING_VAL_TO_REPLACE'] = (
            self.config.getstr('config',
                               'TC_PAIRS_MISSING_VAL_TO_REPLACE', '-99')
        )
        c_dict['MISSING_VAL'] = (
            self.config.getstr('config', 'TC_PAIRS_MISSING_VAL', '-9999')
        )

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('TCPairsConfig_wrapped')

        self.add_met_config(name='init_beg',
                            data_type='string',
                            metplus_configs=['TC_PAIRS_INIT_BEG',
                                             'INIT_BEG'])

        self.add_met_config(name='init_end',
                            data_type='string',
                            metplus_configs=['TC_PAIRS_INIT_END',
                                             'INIT_END'])

        self.add_met_config(name='init_inc',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_INIT_INCLUDE',
                                             'TC_PAIRS_INIT_INC',
                                             'INIT_INCLUDE'])

        self.add_met_config(name='init_exc',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_INIT_EXCLUDE',
                                             'TC_PAIRS_INIT_EXC',
                                             'INIT_EXCLUDE'])

        self.add_met_config(name='valid_inc',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_VALID_INCLUDE',
                                             'TC_PAIRS_VALID_INC',
                                             'VALID_INCLUDE'])

        self.add_met_config(name='valid_exc',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_VALID_EXCLUDE',
                                             'TC_PAIRS_VALID_EXC',
                                             'VALID_EXCLUDE'])

        self.add_met_config(name='write_valid',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_WRITE_VALID'])

        self.add_met_config(name='valid_beg',
                            data_type='string',
                            metplus_configs=['TC_PAIRS_VALID_BEG',
                                             'VALID_BEG'])

        self.add_met_config(name='valid_end',
                            data_type='string',
                            metplus_configs=['TC_PAIRS_VALID_END',
                                             'VALID_END'])

        self.add_met_config(name='dland_file',
                            data_type='string',
                            metplus_configs=['TC_PAIRS_DLAND_FILE'])

        self.add_met_config(name='model',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_MODEL',
                                             'MODEL'])

        self.add_met_config(name='storm_name',
                            data_type='list',
                            metplus_configs=['TC_PAIRS_STORM_NAME'])

        self._handle_consensus()

        self.add_met_config(name='check_dup',
                            data_type='bool')

        self.add_met_config(name='interp12',
                            data_type='string',
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config(name='match_points', data_type='bool')

        self._handle_diag_info_map()

        self._handle_diag_convert_map()

        # if unset, set match_points to TRUE to match old default in wrapped
        if not self.env_var_dict.get('METPLUS_MATCH_POINTS'):
            self.env_var_dict['METPLUS_MATCH_POINTS'] = 'match_points = TRUE;'

        c_dict['INIT_INCLUDE'] = getlist(
            self.get_wrapper_or_generic_config('INIT_INCLUDE')
        )
        c_dict['INIT_EXCLUDE'] = getlist(
            self.get_wrapper_or_generic_config('INIT_EXCLUDE')
        )
        c_dict['VALID_BEG'] = self.get_wrapper_or_generic_config('VALID_BEG')
        c_dict['VALID_END'] = self.get_wrapper_or_generic_config('VALID_END')
        c_dict['ADECK_DIR'] = self.config.getdir('TC_PAIRS_ADECK_INPUT_DIR',
                                                 '')
        c_dict['BDECK_DIR'] = self.config.getdir('TC_PAIRS_BDECK_INPUT_DIR',
                                                 '')
        c_dict['EDECK_DIR'] = self.config.getdir('TC_PAIRS_EDECK_INPUT_DIR',
                                                 '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_PAIRS_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error('TC_PAIRS_OUTPUT_DIR must be set')

        c_dict['READ_ALL_FILES'] = (
            self.config.getbool('config',
                                'TC_PAIRS_READ_ALL_FILES',
                                False)
        )

        # get list of models to process
        c_dict['MODEL_LIST'] = getlist(
            self.config.getraw('config', 'MODEL', '')
        )
        # if no models are requested, set list to contain a single string
        # that is the wildcard character '*'
        if not c_dict['MODEL_LIST']:
            c_dict['MODEL_LIST'] = ['*']

        self._read_storm_info(c_dict)

        c_dict['STORM_NAME_LIST'] = getlist(
            self.config.getraw('config', 'TC_PAIRS_STORM_NAME')
        )
        c_dict['DLAND_FILE'] = self.config.getraw('config',
                                                  'TC_PAIRS_DLAND_FILE')

        c_dict['ADECK_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_PAIRS_ADECK_TEMPLATE',
                               '')
        )

        c_dict['BDECK_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_PAIRS_BDECK_TEMPLATE')
        )

        c_dict['EDECK_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_PAIRS_EDECK_TEMPLATE',
                               '')
        )

        # read optional -diag argument variables
        self._handle_diag(c_dict)

        # handle output template
        output_template = (
            self.config.getraw('config', 'TC_PAIRS_OUTPUT_TEMPLATE')
        )
        # set output name to tc_pairs if not specified
        if not output_template:
            output_template = 'tc_pairs'

        c_dict['OUTPUT_TEMPLATE'] = output_template

        c_dict['SKIP_REFORMAT'] = (
            self.config.getbool('config',
                                'TC_PAIRS_SKIP_IF_REFORMAT_EXISTS',
                                False)
        )
        c_dict['SKIP_OUTPUT'] = (
            self.config.getbool('config',
                                'TC_PAIRS_SKIP_IF_OUTPUT_EXISTS',
                                False)
        )
        c_dict['REFORMAT_DECK'] = self.config.getbool('config',
                                                      'TC_PAIRS_REFORMAT_DECK',
                                                      False)
        c_dict['REFORMAT_DECK_TYPE'] = (
                self.config.getstr('config', 'TC_PAIRS_REFORMAT_TYPE',
                                   'SBU')
        )
        c_dict['REFORMAT_DIR'] = self.config.getdir('TC_PAIRS_REFORMAT_DIR',
                                                    '')
        if c_dict['REFORMAT_DECK'] and not c_dict['REFORMAT_DIR']:
            self.log_error('Must set TC_PAIRS_REFORMAT_DIR if '
                           'TC_PAIRS_REFORMAT_DECK is True')

        c_dict['GET_ADECK'] = True if c_dict['ADECK_TEMPLATE'] else False
        c_dict['GET_EDECK'] = True if c_dict['EDECK_TEMPLATE'] else False

        self.handle_description()

        c_dict['SKIP_LEAD_SEQ'] = (
            self.config.getbool('config',
                                'TC_PAIRS_SKIP_LEAD_SEQ',
                                False)
        )

        # check for settings that cause differences moving from v4.1 to v5.0
        # warn and update run setting to preserve old behavior
        if (self.config.has_option('config', 'LOOP_ORDER') and
            self.config.getstr_nocheck('config', 'LOOP_ORDER') == 'times' and
            not self.config.has_option('config', 'TC_PAIRS_RUN_ONCE')):
            self.logger.warning(
                'LOOP_ORDER has been deprecated. LOOP_ORDER has been set to '
                '"times" and TC_PAIRS_RUN_ONCE is not set. '
                'Forcing TC_PAIRS_RUN_ONCE=False to preserve behavior prior to '
                'v5.0.0. Please remove LOOP_ORDER and set '
                'TC_PAIRS_RUN_ONCE=False to preserve previous behavior and '
                'remove this warning message.'
            )
            c_dict['RUN_ONCE'] = False
            return c_dict

        # only run once if True
        c_dict['RUN_ONCE'] = self.config.getbool('config',
                                                 'TC_PAIRS_RUN_ONCE',
                                                 True)
        return c_dict

    def run_all_times(self):
        """! Build up the command to invoke the MET tool tc_pairs.
        """
        # use first run time
        input_dict = next(time_generator(self.config))
        if not input_dict:
            return self.all_commands

        add_to_time_input(input_dict,
                          instance=self.instance)
        log_runtime_banner(self.config, input_dict, self)

        # if running in READ_ALL_FILES mode, call tc_pairs once and exit
        if self.c_dict['READ_ALL_FILES']:
            return self._read_all_files(input_dict)

        if not self.c_dict['RUN_ONCE']:
            return super().run_all_times()

        self.logger.debug('Only processing first run time. Set '
                          'TC_PAIRS_RUN_ONCE=False to process all run times.')
        self.run_at_time(input_dict)
        return self.all_commands

    def run_at_time(self, input_dict):
        """! Create the arguments to run MET tc_pairs
             Args:
                 input_dict dictionary containing init or valid time
             Returns:
        """
        input_dict['instance'] = self.instance if self.instance else ''
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string

            # if skipping lead sequence, only run once per init/valid time
            if self.c_dict['SKIP_LEAD_SEQ']:
                lead_seq = [0]
            else:
                lead_seq = get_lead_sequence(self.config, input_dict)

            for lead in lead_seq:
                input_dict['lead'] = lead
                time_info = ti_calculate(input_dict)

                if skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
                    self.logger.debug('Skipping run time')
                    continue

                self.run_at_time_loop_string(time_info)

    def run_at_time_loop_string(self, time_info):
        """! Create the arguments to run MET tc_pairs

         @param time_info dictionary containing time information
        """
        # set output dir
        self.outdir = self.c_dict['OUTPUT_DIR']

        # string substitute config file in case custom string is used
        self.c_dict['CONFIG_FILE'] = do_string_sub(self.c_dict['CONFIG_FILE'],
                                                   **time_info)

        if self.c_dict.get('STORM_ID_LIST'):
            return self._loop_storm_ids(time_info)

        return self._loop_basin_and_cyclone(time_info)

    def _read_storm_info(self, c_dict):
        """! Read config variables that specify the storms to process. Report
        an error if attempting to filter by storm_id if also specifying
        basin or cyclone. Sets c_dict depending on what is set: STORM_ID_LIST
        if filtering by storm_id, or CYCLONE_LIST and BASIN_LIST otherwise

        @param c_dict dictionary to populate with values from config
        @returns None
        """
        storm_id_list = getlist(
            self.config.getraw('config', 'TC_PAIRS_STORM_ID', '')
        )
        cyclone_list = getlist(
            self.config.getraw('config', 'TC_PAIRS_CYCLONE', '')
        )
        basin_list = getlist(
            self.config.getraw('config', 'TC_PAIRS_BASIN', '')
        )

        if storm_id_list:
            # if using storm id and any other filter is set, report an error
            if basin_list:
                self.log_error('Cannot filter by both BASIN and STORM_ID')

            if cyclone_list:
                self.log_error('Cannot filter by both CYCLONE and STORM_ID')

            c_dict['STORM_ID_LIST'] = storm_id_list
            return

        # if storm_id is not used, set cyclone and basin lists if they are set
        if cyclone_list:
            c_dict['CYCLONE_LIST'] = cyclone_list

        if basin_list:
            c_dict['BASIN_LIST'] = basin_list

    def _handle_consensus(self):
        dict_items = {
            'name': 'string',
            'members': 'list',
            'required': ('list', 'remove_quotes'),
            'min_req': 'int',
            'write_members': 'bool',
        }
        return_code = add_met_config_dict_list(config=self.config,
                                               app_name=self.app_name,
                                               output_dict=self.env_var_dict,
                                               dict_name='consensus',
                                               dict_items=dict_items)
        if not return_code:
            self.isOK = False

    def _handle_diag_info_map(self):
        dict_items = {
            'diag_source': 'string',
            'track_source': 'string',
            'field_source': 'string',
            'match_to_track': 'list',
            'diag_name': 'list',
        }
        return_code = add_met_config_dict_list(config=self.config,
                                               app_name=self.app_name,
                                               output_dict=self.env_var_dict,
                                               dict_name='diag_info_map',
                                               dict_items=dict_items)
        if not return_code:
            self.isOK = False

    def _handle_diag_convert_map(self):
        dict_items = {
            'diag_source': 'string',
            'key': 'list',
            'convert': ('string', 'remove_quotes,add_x'),
        }
        return_code = add_met_config_dict_list(config=self.config,
                                               app_name=self.app_name,
                                               output_dict=self.env_var_dict,
                                               dict_name='diag_convert_map',
                                               dict_items=dict_items)
        if not return_code:
            self.isOK = False

    def _handle_diag(self, c_dict):
        diag_indices = list(
            find_indices_in_config_section(r'TC_PAIRS_DIAG_TEMPLATE(\d+)$',
                                           self.config,
                                           index_index=1).keys()
        )
        if not diag_indices:
            return

        diag_info_list = []
        for idx in diag_indices:
            template = (
                self.config.getraw('config', f'TC_PAIRS_DIAG_TEMPLATE{idx}')
            )
            diag_dir = (
                self.config.getdir(f'TC_PAIRS_DIAG_DIR{idx}', '')
            )
            if diag_dir:
                template = os.path.join(diag_dir, template)

            source = (
                self.config.getraw('config', f'TC_PAIRS_DIAG_SOURCE{idx}')
            )
            if not source:
                self.log_error(f'TC_PAIRS_DIAG_SOURCE{idx} must be set if '
                               f'TC_PAIRS_DIAG_TEMPLATE{idx} is set')
                continue
            diag_info = {
                'template': template,
                'source': source,
            }
            diag_info_list.append(diag_info)

        c_dict['DIAG_INFO_LIST'] = diag_info_list

    def _loop_storm_ids(self, time_info):
        for storm_id in self.c_dict['STORM_ID_LIST']:

            # set current storm ID to be set an environment variable
            self.c_dict['STORM_ID'] = [storm_id]

            # pull out basin, cyclone, and year from storm ID
            basin, cyclone = self._parse_storm_id(storm_id)
            if not basin:
                return

            # set storm ID in time dict so it can be used in filename templates
            time_info['storm_id'] = storm_id

            self.process_data(basin, cyclone, time_info)

        return True

    def _parse_storm_id(self, storm_id):
        """! Extract basin and cyclone from storm_id if possible.

        @param storm_id string to parse
        @returns tuple of basin and cyclone as lowercase strings or
         wildcard expressions if cannot parse info from storm_id
        """
        match = re.match(self.REGEXES['storm_id'], storm_id)
        if not match:
            self.logger.debug("Could not parse basin and cyclone from "
                              f"storm ID ({storm_id}). Using wildcard "
                              "for both")
            return self.WILDCARDS['basin'], self.WILDCARDS['cyclone']

        basin = match.group(1).lower()
        cyclone = match.group(2)

        return basin, cyclone

    def _loop_basin_and_cyclone(self, time_info):
        """! Loop over basin and cyclone lists and process for each combination

        @param time_info dictionary containing time information
        """

        # use list containing wildcard string if basin or cyclone are not set
        basin_list = self.c_dict.get('BASIN_LIST',
                                     [self.WILDCARDS['basin']])

        cyclone_list = self.c_dict.get('CYCLONE_LIST',
                                       [self.WILDCARDS['cyclone']])

        for basin in basin_list:
            # set variables to be set as environment variables
            # unless wildcard expression is set
            if basin != self.WILDCARDS['basin']:
                self.c_dict['BASIN'] = [basin]

            for cyclone in cyclone_list:
                if cyclone != self.WILDCARDS['cyclone']:
                    self.c_dict['CYCLONE'] = [cyclone]
                self.process_data(basin.lower(), cyclone, time_info)

        return True

    def set_environment_variables(self, time_info):
        """! Set up all the environment variables that are assigned
             in the METplus config file which are to be used by the MET
            TC-pairs config file.

             Args:
                 nothing - retrieves necessary MET+ config values via
                           class attributes

             Returns:
                 nothing - sets the environment variables
        """
        # handle old method for setting env vars in MET config files
        init_beg = self.get_env_var_value('METPLUS_INIT_BEG').strip('"')
        self.add_env_var('INIT_BEG', init_beg)

        init_end = self.get_env_var_value('METPLUS_INIT_END').strip('"')
        self.add_env_var('INIT_END', init_end)

        valid_beg = self.get_env_var_value('METPLUS_VALID_BEG').strip('"')
        self.add_env_var('VALID_BEG', valid_beg)

        valid_end = self.get_env_var_value('METPLUS_VALID_END').strip('"')
        self.add_env_var('VALID_END', valid_end)

        init_inc = self.get_env_var_value('METPLUS_INIT_INCLUDE',
                                          item_type='list')
        self.add_env_var('INIT_INCLUDE', init_inc)

        init_exc = self.get_env_var_value('METPLUS_INIT_EXCLUDE',
                                          item_type='list')
        self.add_env_var('INIT_EXCLUDE', init_exc)

        model = self.get_env_var_value('METPLUS_MODEL',
                                       item_type='list')
        self.add_env_var('MODEL', model)

        # STORM_ID
        storm_id = '[]'
        if self.c_dict.get('STORM_ID'):
            storm_id = str(self.c_dict['STORM_ID']).replace("'", '"')

            storm_id_fmt = f"storm_id = {storm_id};"
            self.env_var_dict['METPLUS_STORM_ID'] = storm_id_fmt

        self.add_env_var('STORM_ID', storm_id)

        # BASIN
        basin = '[]'
        if self.c_dict.get('BASIN'):
            basin = str(self.c_dict['BASIN']).replace("'", '"')

            basin_fmt = f"basin = {basin};"
            self.env_var_dict['METPLUS_BASIN'] = basin_fmt

        self.add_env_var('BASIN', basin)

        # CYCLONE
        cyclone = '[]'
        if self.c_dict.get('CYCLONE'):
            cyclone = self.c_dict.get('CYCLONE')
            # add storm month to each cyclone item if reformatting SBU
            if self.c_dict['REFORMAT_DECK'] and \
               self.c_dict['REFORMAT_DECK_TYPE'] == 'SBU':
                storm_month = time_info['init'].strftime('%m')
                cyclone = [storm_month + c for c in cyclone]

            cyclone = str(cyclone).replace("'", '"')

            cyclone_fmt = f"cyclone = {cyclone};"
            self.env_var_dict['METPLUS_CYCLONE'] = cyclone_fmt

        self.add_env_var('CYCLONE', cyclone)

        # STORM_NAME
        storm_name = '[]'
        if self.c_dict.get('STORM_NAME'):
            storm_name = str(self.c_dict['STORM_NAME']).replace("'", '"')

            storm_name_fmt = f"storm_name = {storm_name};"
            self.env_var_dict['METPLUS_STORM_NAME'] = storm_name_fmt

        self.add_env_var('STORM_NAME', storm_name)

        # DLAND_FILE
        self.add_env_var('DLAND_FILE', self.c_dict['DLAND_FILE'])

        super().set_environment_variables(time_info)

    def process_data(self, basin, cyclone, time_info):
        """!Find requested files and run tc_pairs

            @param basin region of storm from config
            @param cyclone ID number of cyclone from config
            @param time_info dictionary with timing info for current run
        """
        bdeck_files, wildcard_used = self._get_bdeck(basin, cyclone, time_info)
        if not bdeck_files:
            return

        # find corresponding adeck or edeck files
        for bdeck_file in bdeck_files:
            self.clear()
            self.logger.debug(f'Found BDECK: {bdeck_file}')

            # get current basin/cyclone that corresponds to bdeck
            current_basin, current_cyclone = (
                self._get_basin_cyclone_from_bdeck(bdeck_file, wildcard_used,
                                                   basin, cyclone, time_info)
            )
            if current_basin is None or current_cyclone is None:
                continue

            time_storm_info = time_info.copy()
            time_storm_info['basin'] = current_basin
            time_storm_info['cyclone'] = current_cyclone

            # create lists for deck files, put bdeck in list so it can
            # be handled the same as a and e for reformatting even though
            # it will always be size 1
            bdeck_list = [bdeck_file]
            adeck_list = []
            edeck_list = []

            # get adeck files
            if self.c_dict['GET_ADECK']:
                adeck_list = self.find_a_or_e_deck_files('A', time_storm_info)
            # get edeck files
            if self.c_dict['GET_EDECK']:
                edeck_list = self.find_a_or_e_deck_files('E', time_storm_info)

            if not adeck_list and not edeck_list:
                self.log_error('Could not find any corresponding '
                               'ADECK or EDECK files')
                continue

            # reformat extra tropical cyclone files if necessary
            if self.c_dict['REFORMAT_DECK']:
                adeck_list = self.reformat_files(adeck_list, 'A', time_info)
                bdeck_list = self.reformat_files(bdeck_list, 'B', time_info)
                edeck_list = self.reformat_files(edeck_list, 'E', time_info)

            self.args.append(f"-bdeck {' '.join(bdeck_list)}")
            if adeck_list:
                self.args.append(f"-adeck {' '.join(adeck_list)}")
            if edeck_list:
                self.args.append(f"-edeck {' '.join(edeck_list)}")

            # find -diag file if requested
            if not self._get_diag_file(time_storm_info):
                return []

            # change wildcard basin/cyclone to 'all' for output filename
            if current_basin == self.WILDCARDS['basin']:
                time_storm_info['basin'] = 'all'
            if current_cyclone == self.WILDCARDS['cyclone']:
                time_storm_info['cyclone'] = 'all'

            if not self.find_and_check_output_file(time_info=time_storm_info,
                                                   check_extension='.tcst'):
                return []

            # Set up the environment variable to be used in the TCPairs Config
            self.set_environment_variables(time_storm_info)

            self.build()

    def _get_bdeck(self, basin, cyclone, time_info):
        """! Use glob to get all bdeck files that match the basin and cyclone

        @param basin string to substitute for basin in template
        @param cyclone string to substitute for cyclone in template
        @param time_info dictionary with timing info for current run
        @returns tuple of the list of files that match and a boolean that is
         True if a wildcard was used to find them,
         or (None, False) if none were found
        """
        # get search expression for bdeck files to pass to glob
        bdeck_template = os.path.join(self.c_dict['BDECK_DIR'],
                                      self.c_dict['BDECK_TEMPLATE'])
        bdeck_glob = do_string_sub(bdeck_template,
                                   basin=basin,
                                   cyclone=cyclone,
                                   **time_info)
        self.logger.debug('Looking for BDECK: {}'.format(bdeck_glob))

        # get all files that match expression
        bdeck_files = sorted(glob.glob(bdeck_glob))

        if bdeck_files:
            wildcard_used = '*' in bdeck_glob or '?' in bdeck_glob
            return bdeck_files, wildcard_used

        # if no bdeck_files found
        self.log_error(f'No BDECK files found searching for basin {basin} '
                       f'and cyclone {cyclone} using template '
                       f"{self.c_dict['BDECK_TEMPLATE']}")
        return [], False

    def _get_basin_cyclone_from_bdeck(self, bdeck_file, wildcard_used,
                                      basin, cyclone, time_info):
        """! Set current basin and cyclone from bdeck file.
        If basin or cyclone are a wildcard, these will be replaced by
        the value pulled from the bdeck file.
        """
        # if wildcard is not used in glob expression, return basin and cyclone
        if not wildcard_used:
            return basin, cyclone

        # set regex expressions for basin and cyclone if wildcard is used
        # cast cyclone value to integer if it is not a wildcard
        if cyclone == self.WILDCARDS['cyclone']:
            cyclone_regex = self.REGEXES['cyclone']
        else:
            cyclone_regex = cyclone

        if basin == self.WILDCARDS['basin']:
            basin_regex = self.REGEXES['basin']
        else:
            basin_regex = basin

        # get regex expression to pull out basin and cyclone
        bdeck_template = os.path.join(self.c_dict['BDECK_DIR'],
                                      self.c_dict['BDECK_TEMPLATE'])
        # capture any template tags as regex matches to find correct tag
        bdeck_template = bdeck_template.replace('{', '({').replace('}', '})')

        bdeck_regex = do_string_sub(bdeck_template,
                                    basin=basin_regex,
                                    cyclone=cyclone_regex,
                                    **time_info)

        # capture wildcard values in template - must replace ? wildcard
        # character after substitution because ? is used in template tags
        bdeck_regex = bdeck_regex.replace('*', '(.*)').replace('?', '(.)')
        self.logger.debug(f'Regex to extract basin/cyclone: {bdeck_regex}')

        match = re.match(bdeck_regex, bdeck_file)
        if not match:
            return basin, cyclone

        current_basin = basin
        current_cyclone = cyclone

        matches = match.groups()
        # get template tags and wildcards from template
        tags = get_tags(bdeck_template)
        if len(matches) != len(tags):
            self.log_error("Number of regex match groups does not match "
                           "number of tags found:\n"
                           f"Regex pattern: {bdeck_template}\n"
                           f"Matches: {matches}\nTags: {tags}")
            return None, None

        for match, tag in zip(matches, tags):
            # if basin/cyclone if found, get value
            if tag == 'basin' and basin == self.WILDCARDS['basin']:
                current_basin = match
            elif (tag == 'cyclone' and
                  cyclone == self.WILDCARDS['cyclone']):
                current_cyclone = match

        return current_basin, current_cyclone

    def find_a_or_e_deck_files(self, deck, time_info):
        """!Find ADECK or EDECK files that correspond to the BDECk file found

            @param deck type of deck (A or E)
            @param time_info dictionary with timing/storm info for current run
        """
        deck_list = []
        template = os.path.join(self.c_dict[deck+'DECK_DIR'],
                                self.c_dict[deck+'DECK_TEMPLATE'])

        # get matching adeck wildcard expression for first model
        deck_expr = do_string_sub(template,
                                  model=self.c_dict['MODEL_LIST'][0],
                                  **time_info)

        # add adeck files if they exist for each model
        for model in self.c_dict['MODEL_LIST']:
            deck_glob = deck_expr.replace(self.c_dict['MODEL_LIST'][0], model)
            self.logger.debug(f'Looking for {deck}DECK file: {deck_glob} '
                              f'for model ({model}) using template {template}')
            deck_files = glob.glob(deck_glob)
            if not deck_files:
                continue

            for deck_file in deck_files:
                # if deck exists, add to list
                if os.path.isfile(deck_file) and deck_file not in deck_list:
                    self.logger.debug('Adding {}DECK: {}'.format(deck,
                                                                 deck_file))
                    deck_list.append(deck_file)

        return deck_list

    def reformat_files(self, file_list, deck_type, time_info):
        """!Reformat track data to match expected ATCF format

            @param file_list list of files to reformat
            @param deck_type type of deck (A or E)
            @param time_info dictionary with timing info for current run
            @returns list of output files that are in ATCF format
        """
        storm_month = time_info['init'].strftime('%m')
        missing_values = \
            (self.c_dict['MISSING_VAL_TO_REPLACE'],
             self.c_dict['MISSING_VAL'])
        deck_dir = self.c_dict[deck_type+'DECK_DIR']
        reformat_dir = self.c_dict['REFORMAT_DIR']

        outfiles = []
        for deck in file_list:
            outfile = deck.replace(deck_dir,
                                   reformat_dir)
            if os.path.isfile(outfile) and self.c_dict.get('SKIP_REFORMAT'):
                self.logger.debug(f'Skip processing {deck} because '
                                  'reformatted file already exists. Change '
                                  'TC_PAIRS_SKIP_IF_REFORMAT_EXISTS to '
                                  'False to overwrite file')
            else:
                self.logger.debug(f'Reformatting {deck} to {outfile}')
                self.read_modify_write_file(deck, storm_month,
                                            missing_values, outfile)

            outfiles.append(outfile)

        return outfiles

    def get_command(self):
        """! Over-ride CommandBuilder's get_command because unlike other MET
             tools, tc_pairs handles input files differently- namely,
             through flags -adeck and -bdeck and doesn't require an
             output file, as there is a default.
             Build command to run from arguments
        """
        output_path = self.get_output_path()
        if not output_path:
            self.log_error('Output path not set')
            return None

        cmd = (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
               f" {' '.join(self.args)}"
               f" -config {self.c_dict['CONFIG_FILE']}"
               f" -out {output_path}")
        return cmd

    @staticmethod
    def read_modify_write_file(in_csvfile, storm_month, missing_values,
                               out_csvfile):
        """!Reads CSV file, reformat file by adding the month to the 2nd
        column storm number, delete the 3rd column, replace missing values,
        and write a new CSV file with the modified content.

        @param in_csvfile input csv file that is being parsed
        @param storm_month storm month to prepend to storm number
        @param missing_values tuple containing a missing data value to find in
        the columns and the value to replace it with, e.g. (-9, -9999)
        @param out_csvfile the output csv file
        """
        # create output directory if it does not exist
        mkdir_p(os.path.dirname(out_csvfile))

        # Open the output csv file
        out_file = open(out_csvfile, "w", newline='')

        # Tell the write to use the line separator
        # "\n" instead of the DOS "\r\n"
        writer = csv.writer(out_file, lineterminator="\n")

        with open(in_csvfile, newline='') as csvfile:

            in_file_reader = csv.reader(csvfile)

            for row in in_file_reader:
                # Create a list for the modified lines
                row_list = []

                # Replace the second column (storm number) with
                # the month followed by the storm number
                # e.g. Replace 0006 with 010006
                # this is done because this data has many storms per month
                # and we need to know which storm we are processing if running
                # over multiple months
                row[1] = " " + storm_month + (row[1]).strip()

                # Iterate over the items, deleting or modifying the columns
                for item in row:
                    # Delete the third column
                    if item == row[2]:
                        continue
                    # Replace MISSING_VAL_TO_REPLACE=missing_values[0] with
                    # MISSING_VAL=missing_values[1]
                    if item.strip() == missing_values[0]:
                        item = " " + missing_values[1]
                    # Create a new row to write
                    row_list.append(item)

                # Write the modified file
                writer.writerow(row_list)

        out_file.close()

    def _read_all_files(self, input_dict):
        """! Handle setting up a command that skips logic to determine which
        files to pass into the application and instead passes in the
        directories to search for files to let the application determine
        which data to process

        @param input_dict dictionary containing some time information
        @returns list of tuples containing commands that are run and which env
         vars were set for the command
        """
        # use full list of storm/model info if running once for all files
        self.c_dict['STORM_ID'] = self.c_dict.get('STORM_ID_LIST', '')
        self.c_dict['CYCLONE'] = self.c_dict.get('CYCLONE_LIST', '')
        self.c_dict['BASIN'] = self.c_dict.get('BASIN_LIST', '')

        # Set up the environment variable to be used in the tc_pairs Config
        self.args.append(f"-bdeck {self.c_dict['BDECK_DIR']}")

        if self.c_dict['ADECK_DIR']:
            self.args.append(f"-adeck {self.c_dict['ADECK_DIR']}")

        if self.c_dict['EDECK_DIR']:
            self.args.append(f"-edeck {self.c_dict['EDECK_DIR']}")

        # get output filename from template
        time_info = ti_calculate(input_dict)
        time_storm_info = self._add_storm_info_to_dict(time_info)

        # handle -diag file if requested
        if not self._get_diag_file(time_storm_info):
            return []

        if not self.find_and_check_output_file(time_info=time_storm_info,
                                               check_extension='.tcst'):
            return []

        self.set_environment_variables(time_storm_info)

        self.build()
        return self.all_commands

    def _get_diag_file(self, time_info):
        """! Get optional -diag argument file path if requested.

        @param time_info dictionary containing values to substitute into
         filename template
        @returns True if file was found successfully or no file was requested.
         False if the file does not exist.
        """
        if not self.c_dict.get('DIAG_INFO_LIST'):
            return True

        time_info_copy = time_info.copy()
        for diag_info in self.c_dict.get('DIAG_INFO_LIST'):
            self.c_dict['DIAG_INPUT_TEMPLATE'] = diag_info['template']
            all_files = []
            for model in self.c_dict['MODEL_LIST']:
                time_info_copy['model'] = model
                filepaths = self.find_data(time_info_copy, data_type='DIAG',
                                           return_list=True)
                if filepaths:
                    all_files.extend(filepaths)

            if not all_files:
                self.log_error('Could not get -diag files')
                return False

            # remove duplicate files
            all_files = sorted(list(set(all_files)))

            arg = f"-diag {diag_info['source']} {' '.join(all_files)}"
            self.args.append(arg)

        return True

    def _add_storm_info_to_dict(self, time_info):
        """! Read from self.c_dict and add storm information to dictionary.
          Assumes each value read from c_dict is a list. Set value to 'all'
          unless there is a single item in the list. Used to ensure that
          output filenames do not include wildcard characters
        """
        time_storm_info = time_info.copy()
        storm_id = self.c_dict.get('STORM_ID')
        storm_id = storm_id[0] if len(storm_id) == 1 else 'all'

        basin = self.c_dict.get('BASIN')
        basin = basin[0] if len(basin) == 1 else 'all'

        cyclone = self.c_dict.get('CYCLONE')
        cyclone = cyclone[0] if len(cyclone) == 1 else 'all'

        time_storm_info['storm_id'] = storm_id
        time_storm_info['basin'] = basin
        time_storm_info['cyclone'] = cyclone

        for item in ['model', 'storm_name']:
            value = self.c_dict.get(f'{item.upper()}_LIST')
            value = 'all' if len(value) != 1 or value[0] == '*' else value[0]
            time_storm_info[item] = value

        return time_storm_info
