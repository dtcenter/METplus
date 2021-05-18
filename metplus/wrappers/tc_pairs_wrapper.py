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

from ..util import time_util
from ..util import met_util as util
from ..util import do_string_sub
from ..util import get_tags
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
        'METPLUS_INIT_INCLUDE',
        'METPLUS_INIT_EXCLUDE',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_DLAND_FILE',
    ]

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'tc_pairs'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)
        self.adeck = []
        self.bdeck = []
        self.edeck = []

    def create_c_dict(self):
        """! Create a dictionary containing all the values set in the
         config file. This will make it easier for unit testing.

             @returns Dictionary of the values from the config file
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_PAIRS_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['MISSING_VAL_TO_REPLACE'] = (
            self.config.getstr('config',
                               'TC_PAIRS_MISSING_VAL_TO_REPLACE', '-99')
        )
        c_dict['MISSING_VAL'] = (
            self.config.getstr('config', 'TC_PAIRS_MISSING_VAL', '-9999')
        )
        c_dict['CONFIG_FILE'] = self.config.getraw('config',
                                                   'TC_PAIRS_CONFIG_FILE',
                                                   '')
        if not c_dict['CONFIG_FILE']:
            self.log_error("TC_PAIRS_CONFIG_FILE is required to "
                           "run TCPairs wrapper")

        self.set_met_config_string(self.env_var_dict,
                                   ['TC_PAIRS_INIT_BEG',
                                    'INIT_BEG'],
                                   'init_beg',
                                   'METPLUS_INIT_BEG')

        self.set_met_config_string(self.env_var_dict,
                                   ['TC_PAIRS_INIT_END',
                                    'INIT_END'],
                                   'init_end',
                                   'METPLUS_INIT_END')

        self.set_met_config_list(self.env_var_dict,
                                 ['TC_PAIRS_INIT_INCLUDE',
                                  'INIT_INCLUDE'],
                                 'init_inc',
                                 'METPLUS_INIT_INCLUDE')

        self.set_met_config_list(self.env_var_dict,
                                 ['TC_PAIRS_INIT_EXCLUDE',
                                  'INIT_EXCLUDE'],
                                 'init_inc',
                                 'METPLUS_INIT_EXCLUDE')

        self.set_met_config_string(self.env_var_dict,
                                   ['TC_PAIRS_VALID_BEG',
                                    'VALID_BEG'],
                                   'valid_beg',
                                   'METPLUS_VALID_BEG')

        self.set_met_config_string(self.env_var_dict,
                                   ['TC_PAIRS_VALID_END',
                                    'VALID_END'],
                                   'valid_end',
                                   'METPLUS_VALID_END')

        self.set_met_config_string(self.env_var_dict,
                                   'TC_PAIRS_DLAND_FILE',
                                   'dland_file',
                                   'METPLUS_DLAND_FILE')

        self.set_met_config_list(self.env_var_dict,
                                 'MODEL',
                                 'model',
                                 'METPLUS_MODEL')

        init_time_fmt = self.config.getstr('config', 'INIT_TIME_FMT')
        clock_time = datetime.datetime.strptime(
            self.config.getstr('config',
                               'CLOCK_TIME'),
            '%Y%m%d%H%M%S'
        )

        init_beg = self.config.getraw('config', 'INIT_BEG')
        init_beg_dt = util.get_time_obj(init_beg,
                                        init_time_fmt,
                                        clock_time,
                                        logger=self.logger)
        c_dict['INIT_BEG'] = init_beg_dt.strftime('%Y%m%d_%H%M%S')

        c_dict['INIT_INCLUDE'] = util.getlist(
            self.get_wrapper_or_generic_config('INIT_INCLUDE')
        )
        c_dict['INIT_EXCLUDE'] = util.getlist(
            self.get_wrapper_or_generic_config('INIT_EXCLUDE')
        )
        c_dict['VALID_BEG'] = self.get_wrapper_or_generic_config('VALID_BEG')
        c_dict['VALID_END'] = self.get_wrapper_or_generic_config('VALID_END')
        c_dict['ADECK_DIR'] = \
                self.config.getdir('TC_PAIRS_ADECK_INPUT_DIR', '')
        c_dict['BDECK_DIR'] = \
                self.config.getdir('TC_PAIRS_BDECK_INPUT_DIR')
        c_dict['EDECK_DIR'] = \
                self.config.getdir('TC_PAIRS_EDECK_INPUT_DIR', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_PAIRS_OUTPUT_DIR')
        c_dict['READ_ALL_FILES'] = (
            self.config.getbool('config',
                                'TC_PAIRS_READ_ALL_FILES')
        )
        c_dict['OUTPUT_BASE'] = self.config.getstr('dir', 'OUTPUT_BASE')
        c_dict['CYCLONE_LIST'] = util.getlist(
            self.config.getstr('config', 'TC_PAIRS_CYCLONE', '')
        )
        c_dict['MODEL_LIST'] = util.getlist(
            self.config.getstr('config',
                               'MODEL', '')
        )
        c_dict['STORM_ID_LIST'] = util.getlist(
            self.config.getstr('config', 'TC_PAIRS_STORM_ID', '')
        )
        c_dict['BASIN_LIST'] = util.getlist(
            self.config.getstr('config',
                               'TC_PAIRS_BASIN',
                               '')
        )
        c_dict['STORM_NAME'] = util.getlist(
            self.config.getraw('config', 'TC_PAIRS_STORM_NAME')
        )
        c_dict['DLAND_FILE'] = self.config.getraw('config',
                                                  'TC_PAIRS_DLAND_FILE')

        c_dict['ADECK_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'TC_PAIRS_ADECK_TEMPLATE',
                               '')
        )

        c_dict['BDECK_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'TC_PAIRS_BDECK_TEMPLATE')
        )

        c_dict['EDECK_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'TC_PAIRS_EDECK_TEMPLATE',
                               '')
        )

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'TC_PAIRS_OUTPUT_TEMPLATE')
        )
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

        if c_dict['STORM_ID_LIST']:
            # if using storm id and any other filter is set, report an error
            if c_dict['BASIN_LIST']:
                self.log_error('Cannot filter by both BASIN and STORM_ID')

            if c_dict['CYCLONE_LIST']:
                self.log_error('Cannot filter by both CYCLONE and STORM_ID')

            # check storm ID format
            for storm_id in c_dict['STORM_ID_LIST']:
                # pull out info from storm_id and process
                match = re.match(r'(\w{2})(\d{2})(\d{4})', storm_id)
                if not match:
                    self.log_error(f'Incorrect STORM_ID format: {storm_id}')

        self.handle_description()

        return c_dict

    def run_all_times(self):
        """! Build up the command to invoke the MET tool tc_pairs.
        """
        # use init begin as run time (start of the storm)
        input_dict = {'init':
                      datetime.datetime.strptime(self.c_dict['INIT_BEG'],
                                                 '%Y%m%d_%H%M%S')
                      }

        # if running in READ_ALL_FILES mode, call tc_pairs once and exit
        if self.c_dict['READ_ALL_FILES']:

            # use full list of storm/model info if running once for all files
            self.c_dict['STORM_ID'] = self.c_dict['STORM_ID_LIST']
            self.c_dict['CYCLONE'] = self.c_dict['CYCLONE_LIST']
            self.c_dict['BASIN'] = self.c_dict['BASIN_LIST']
            self.c_dict['MODEL'] = self.c_dict['MODEL_LIST']

            # Set up the environment variable to be used in the tc_pairs Config
            self.set_environment_variables(None)
            self.bdeck = [self.c_dict['BDECK_DIR']]

            adeck_dir = self.c_dict['ADECK_DIR']
            edeck_dir = self.c_dict['EDECK_DIR']

            if adeck_dir:
                self.adeck = [adeck_dir]

            if edeck_dir:
                self.edeck = [edeck_dir]

            if self.c_dict['OUTPUT_TEMPLATE']:
                # get output filename from template
                time_info = time_util.ti_calculate(input_dict)
                self.add_storm_info_to_dict(time_info)

                output_file = do_string_sub(self.c_dict['OUTPUT_TEMPLATE'],
                                            **time_info)
            else:
                output_file = 'tc_pairs'

            self.outdir = self.c_dict['OUTPUT_DIR']
            self.outfile = output_file

            output_path = self.get_output_path()+'.tcst'
            if os.path.isfile(output_path) and self.c_dict.get('SKIP_OUTPUT'):
                self.logger.debug('Skip running tc_pairs because '
                                  f'output file {output_path} already exists'
                                  'Change TC_PAIRS_SKIP_IF_OUTPUT_EXISTS to '
                                  'False to overwrite file')
            else:
                self.build()

            return self.all_commands

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
            self.run_at_time_loop_string(input_dict)

    def run_at_time_loop_string(self, input_dict):
        """! Create the arguments to run MET tc_pairs
             Args:
                 input_dict dictionary containing init or valid time
             Returns:
        """
        # fill in time info dictionary
        time_info = time_util.ti_calculate(input_dict)

        if util.skip_time(time_info, self.c_dict.get('SKIP_TIMES', {})):
            self.logger.debug('Skipping run time')
            return

        # set output dir
        self.outdir = self.c_dict['OUTPUT_DIR']

        # string substitute config file in case custom string is used
        self.c_dict['CONFIG_FILE'] = do_string_sub(self.c_dict['CONFIG_FILE'],
                                                   **time_info)

        model_list = ['*']
        if self.c_dict['MODEL_LIST']:
            model_list = self.c_dict['MODEL_LIST']

        if self.c_dict['STORM_ID_LIST']:
            for storm_id in self.c_dict['STORM_ID_LIST']:
                # pull out info from storm_id and process
                match = re.match(r'(\w{2})(\d{2})(\d{4})', storm_id)
                if not match:
                    return False

                self.c_dict['STORM_ID'] = [storm_id]

                basin = match.group(1).lower()
                cyclone = match.group(2)
                year = match.group(3)

                init_year = time_info['init'].strftime('%Y')
                if year != init_year:
                    msg = (f'Year specified in STORM_ID {storm_id} '
                           f'({year}) does not match '
                           f'init time year {init_year}. Skipping...')
                    self.logger.warning(msg)
                    continue

                self.process_data(basin, cyclone, model_list, time_info)

            return True

        basin_list = ['??']
        cyclone_list = ['*']

        if self.c_dict['BASIN_LIST']:
            basin_list = self.c_dict['BASIN_LIST']

        if self.c_dict['CYCLONE_LIST']:
            cyclone_list = self.c_dict['CYCLONE_LIST']

        for basin in basin_list:
            if basin != '??':
                self.c_dict['BASIN'] = [basin]
            for cyclone in cyclone_list:
                if cyclone != '*':
                    self.c_dict['CYCLONE'] = [cyclone]
                self.process_data(basin.lower(), cyclone, model_list, time_info)

        return True

    def add_storm_info_to_dict(self, time_info):
        """! Read from self.c_dict and add storm information to dictionary.
          Assumes each value read from c_dict is a list. Set value to 'all'
          unless there is a single item in the list.
        """
        storm_id = self.c_dict['STORM_ID']
        storm_id = storm_id[0] if len(storm_id) == 1 else 'all'

        storm_name = self.c_dict['STORM_NAME']
        storm_name = storm_name[0] if len(storm_name) == 1 else 'all'

        basin = self.c_dict['BASIN']
        basin = basin[0] if len(basin) == 1 else 'all'

        cyclone = self.c_dict['CYCLONE']
        cyclone = cyclone[0] if len(cyclone) == 1 else 'all'

        model = self.c_dict['MODEL']
        model = model[0] if len(model) == 1 else 'all'

        time_info['storm_id'] = storm_id
        time_info['storm_name'] = storm_name
        time_info['basin'] = basin
        time_info['cyclone'] = cyclone
        time_info['model'] = model

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
            # add storm month to each cyclone item if reformatting SBU
            if self.c_dict['REFORMAT_DECK'] and \
               self.c_dict['REFORMAT_DECK_TYPE'] == 'SBU':
                if time_info is None:
                    storm_month = self.c_dict['INIT_BEG'][4:6]
                else:
                    storm_month = time_info['init'].strftime('%m')
                cyclone = [storm_month + c for c in self.c_dict['CYCLONE']]

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

    def process_data(self, basin, cyclone, model_list, time_info):
        """!Find requested files and run tc_pairs

            @param basin region of storm from config
            @param cyclone ID number of cyclone from config
            @param model_list list of models that be available
            @param time_info dictionary with timing info for current run
        """

        # set regex expressions for basin and cyclone if wildcard is used
        # cast cyclone value to integer if it is not a wildcard
        if cyclone != '*':
            cyclone_regex = cyclone
        else:
            cyclone_regex = "([0-9]{2,4})"

        if basin != '??':
            basin_regex = basin
        else:
            basin_regex = "([a-zA-Z]{2})"

        # get search expression for bdeck files to pass to glob
        string_sub = do_string_sub(self.c_dict['BDECK_TEMPLATE'],
                                   basin=basin,
                                   cyclone=cyclone,
                                   **time_info)
        bdeck_glob = os.path.join(self.c_dict['BDECK_DIR'],
                                  string_sub)
        self.logger.debug('Looking for BDECK: {}'.format(bdeck_glob))

        # get all files that match expression
        bdeck_files = sorted(glob.glob(bdeck_glob))

        # if no bdeck_files found
        if len(bdeck_files) == 0:
            template = self.c_dict['BDECK_TEMPLATE']
            self.log_error(f'No BDECK files found searching for basin {basin} '
                           f'and cyclone {cyclone} using template {template}')
            return False

        # find corresponding adeck or edeck files
        for bdeck_file in bdeck_files:
            self.logger.debug('Found BDECK: {}'.format(bdeck_file))

            # set current basin and cyclone from bdeck file
            # if basin or cyclone are a wildcard, these will be
            # replaced by the value pulled from the bdeck file
            current_basin = basin
            current_cyclone = cyclone

            # if wildcard was used in bdeck, pull out what was
            # substituted for * to find corresponding bdeck file
            matches = []
            if '*' in bdeck_glob or '?' in bdeck_glob:
                # get regex expression to pull out basin and cyclone
                string_sub = do_string_sub(self.c_dict['BDECK_TEMPLATE'],
                                           basin=basin_regex,
                                           cyclone=cyclone_regex,
                                           **time_info)
                bdeck_regex = os.path.join(self.c_dict['BDECK_DIR'],
                                           string_sub)

                # capture wildcard values in template
                bdeck_regex = bdeck_regex.replace('*', '(.*)')
                bdeck_regex = bdeck_regex.replace('?', '(.)')

                match = re.match(bdeck_regex, bdeck_file)
                if match:
                    matches = match.groups()
                    tags = get_tags(self.c_dict['BDECK_TEMPLATE'])
                    match_count = 0
                    for tag in tags:
                        # if wildcard is set for tag found, get value
                        # if wildcard if found in template, increment index
                        if tag == 'basin' and basin == '??':
                            current_basin = matches[match_count]
                            match_count += 1
                        elif tag == 'cyclone' and cyclone == '*':
                            current_cyclone = matches[match_count]
                            match_count += 1
                        elif tag == '*' or tag == '?':
                            match_count += 1

            # create lists for deck files, put bdeck in list so it can
            # be handled the same as a and e for reformatting even though
            # it will always be size 1
            bdeck_list = [bdeck_file]
            adeck_list = []
            edeck_list = []

            # get adeck files
            if self.c_dict['GET_ADECK']:
                adeck_list = self.find_deck_files('A', current_basin,
                                                  current_cyclone, model_list,
                                                  time_info)
            # get edeck files
            if self.c_dict['GET_EDECK']:
                edeck_list = self.find_deck_files('E', current_basin,
                                                  current_cyclone, model_list,
                                                  time_info)

            if not adeck_list and not edeck_list:
                self.log_error('Could not find any corresponding '
                               'ADECK or EDECK files')
                continue

            # reformat extra tropical cyclone files if necessary
            if self.c_dict['REFORMAT_DECK']:
                adeck_list = self.reformat_files(adeck_list, 'A', time_info)
                bdeck_list = self.reformat_files(bdeck_list, 'B', time_info)
                edeck_list = self.reformat_files(edeck_list, 'E', time_info)

            self.adeck = adeck_list
            self.bdeck = bdeck_list
            self.edeck = edeck_list

            if self.c_dict['OUTPUT_TEMPLATE']:
                # get output filename from template
                output_file = do_string_sub(self.c_dict['OUTPUT_TEMPLATE'],
                                            basin=current_basin,
                                            cyclone=current_cyclone,
                                            **time_info)
            else:
                output_file = 'tc_pairs'
            self.outfile = output_file

            # Set up the environment variable to be used in the TCPairs Config
            # file (TC_PAIRS_CONFIG_FILE)
            self.set_environment_variables(time_info)

            output_path = self.get_output_path()+'.tcst'
            if os.path.isfile(output_path) and self.c_dict.get('SKIP_OUTPUT'):
                self.logger.debug('Skip running tc_pairs because '
                                  f'output file {output_path} already exists. '
                                  'Change TC_PAIRS_SKIP_IF_OUTPUT_EXISTS to '
                                  'False to overwrite file')
            else:
                self.build()

    def find_deck_files(self, deck, basin, cyclone, model_list, time_info):
        """!Find ADECK or EDECK files that correspond to the BDECk file found

            @param deck type of deck (A or E)
            @param basin region of storm from config
            @param cyclone ID number of cyclone from config
            @param model_list list of models that be available
            @param time_info dictionary with timing info for current run
        """
        deck_list = []
        template = self.c_dict[deck+'DECK_TEMPLATE']
        # get matching adeck wildcard expression for first model
        string_sub = do_string_sub(template,
                                   basin=basin,
                                   cyclone=cyclone,
                                   model=model_list[0],
                                   **time_info)
        deck_expr = os.path.join(self.c_dict[deck+'DECK_DIR'],
                                 string_sub)

        # add adeck files if they exist
        for model in model_list:
            deck_glob = deck_expr.replace(model_list[0], model)
            self.logger.debug(f'Looking for {deck}DECK file: {deck_glob} '
                              f'using template {template}')
            deck_files = glob.glob(deck_glob)
            if not deck_files:
                continue

            # there should only be 1 file that matches
            deck_file = deck_files[0]

            # if deck exists, add to list
            if os.path.isfile(deck_file):
                self.logger.debug('Adding {}DECK: {}'.format(deck, deck_file))
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
        if self.app_path is None:
            self.log_error("No app path specified. You must use a subclass")
            return None

        if not self.adeck and not self.edeck:
            self.log_error('Neither ADECK nor EDECK files set')
            return None

        if not self.bdeck:
            self.log_error('BDECK file not set')
            return None

        config_file = self.c_dict['CONFIG_FILE']
        if not config_file:
            self.log_error('Config file not set')
            return None

        output_path = self.get_output_path()
        if not output_path:
            self.log_error('Output path not set')
            return None

        # create directory containing output file if it doesn't exist
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        cmd = '{} -v {}'.format(self.app_path, self.c_dict['VERBOSITY'])
        cmd += ' -bdeck {}'.format(' '.join(self.bdeck))

        if self.adeck:
            cmd += ' -adeck {}'.format(' '.join(self.adeck))

        if self.edeck:
            cmd += ' -edeck {}'.format(' '.join(self.edeck))

        cmd += ' -config {} -out {}'.format(config_file, output_path)

        return cmd

    def read_modify_write_file(self, in_csvfile, storm_month, missing_values,
                               out_csvfile):
        """! Reads, modifies and writes file
              Args:
                @param in_csvfile input csv file that is being parsed
                @param storm_month The storm month
                @param missing_values a tuple where (MISSING_VAL_TO_REPLACE,
                                                     MISSING_VAL)
                @param out_csvfile the output csv file
                @param logger the log where logging is directed
        """
        # create output directory if it does not exist
        if not os.path.exists(os.path.dirname(out_csvfile)):
            os.makedirs(os.path.dirname(out_csvfile))

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
                    elif item.strip() == missing_values[0]:
                        item = " " + missing_values[1]
                    # Create a new row to write
                    row_list.append(item)

                # Write the modified file
                writer.writerow(row_list)

        csvfile.close()
        out_file.close()
