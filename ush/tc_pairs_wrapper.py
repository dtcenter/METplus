#!/usr/bin/env python

"""
Program Name: tc_pairs_wrapper.py
Contact(s): Julie Prestopnik, Minna Win, Jim Frimel, George McCabe
Abstract: Invokes the MET tool tc_pairs to parse ADeck and BDeck files (ATCF formatted and SBU GFS extra
          tropical cyclone, non-ATCF formatted),
          filter the data, and match them up or just pass in the top level ADeck and BDeck directories to
          MET tc_pairs (slower)
History Log:  Initial version
Usage:
Parameters: None
Input Files: adeck and bdeck files
Output Files: tc_pairs files
Condition codes: 0 for success, 1 for failure

"""

from __future__ import print_function, division, unicode_literals

import collections
import os
import sys
import re
import csv
import datetime
import glob
import produtil.setup
import datetime
from produtil.run import ExitStatusException
import time_util
import met_util as util
import config_metplus
from string_template_substitution import StringSub
from string_template_substitution import get_tags
from command_builder import CommandBuilder

'''!@namespace TcPairsWrapper
@brief Wraps the MET tool tc_pairs to parse ADeck and BDeck ATCF_by_pairs files,
filter the data, and match them up.
Call as follows:
@code{.sh}
tc_pairs_wrapper.py [-c /path/to/user.template.conf]
@endcode
'''

class TcPairsWrapper(CommandBuilder):
    """!Wraps the MET tool, tc_pairs to parse and match ATCF_by_pairs adeck and
       bdeck files.  Pre-processes extra tropical cyclone data.
    """

    def __init__(self, config, logger):
        super(TcPairsWrapper, self).__init__(config, logger)
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                     'bin/tc_pairs')
        self.app_name = os.path.basename(self.app_path)
        self.cmd = ''
        self.adeck = []
        self.bdeck = []
        self.edeck = []
        self.c_dict = self.create_c_dict()

    def create_c_dict(self):
        """! Create a dictionary containing all the values set in the config file.
             This will make it easier for unit testing.

             Args:

             Returns:
                 c_dict - A dictionary of the values from the config file

        """
        c_dict = dict()
        c_dict['MISSING_VAL_TO_REPLACE'] = self.config.getstr('config',
                                                                'TC_PAIRS_MISSING_VAL_TO_REPLACE', '-99')
        c_dict['MISSING_VAL'] = self.config.getstr('config', 'TC_PAIRS_MISSING_VAL', '-9999')
        c_dict['TC_PAIRS_CONFIG_FILE'] = self.config.getstr('config',
                                                            'TC_PAIRS_CONFIG_FILE')

        c_dict['INIT_BEG'] = self.config.getraw('config', 'INIT_BEG')
        c_dict['INIT_END'] = self.config.getraw('config', 'INIT_END')
        c_dict['INIT_TIME_FMT'] = self.config.getstr('config', 'INIT_TIME_FMT')
        c_dict['INIT_INCREMENT'] = self.config.getint('config', 'INIT_INCREMENT')

        c_dict['INIT_INCLUDE'] = util.getlist(
            self.config.getstr('config', 'INIT_INCLUDE'))
        c_dict['INIT_EXCLUDE'] = util.getlist(
            self.config.getstr('config', 'INIT_EXCLUDE'))
        c_dict['VALID_BEG'] = self.config.getstr('config', 'VALID_BEG')
        c_dict['VALID_END'] = self.config.getstr('config', 'VALID_END')
        c_dict['ADECK_DIR'] = \
                self.config.getdir('TC_PAIRS_ADECK_INPUT_DIR', '')
        c_dict['BDECK_DIR'] = \
                self.config.getdir('TC_PAIRS_BDECK_INPUT_DIR')
        c_dict['EDECK_DIR'] = \
                self.config.getdir('TC_PAIRS_EDECK_INPUT_DIR', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_PAIRS_OUTPUT_DIR')
        c_dict['READ_ALL_FILES'] = self.config.getbool('config',
                                                        'TC_PAIRS_READ_ALL_FILES')
        c_dict['OUTPUT_BASE'] = self.config.getstr('dir', 'OUTPUT_BASE')
        c_dict['CYCLONE'] = util.getlist(
            self.config.getstr('config', 'TC_PAIRS_CYCLONE', ''))
        c_dict['MODEL'] = util.getlist(self.config.getstr('config', 'MODEL', ''))
        c_dict['STORM_ID'] = util.getlist(
            self.config.getstr('config', 'TC_PAIRS_STORM_ID', ''))
        c_dict['BASIN'] = util.getlist(self.config.getstr('config', 'TC_PAIRS_BASIN', ''))
        c_dict['STORM_NAME'] = util.getlist(
            self.config.getstr('config', 'TC_PAIRS_STORM_NAME'))
        c_dict['DLAND_FILE'] = self.config.getstr('config', 'TC_PAIRS_DLAND_FILE')

        c_dict['ADECK_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'TC_PAIRS_ADECK_TEMPLATE',
                                                      '')
        c_dict['BDECK_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'TC_PAIRS_BDECK_TEMPLATE')
        c_dict['EDECK_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'TC_PAIRS_EDECK_TEMPLATE',
                                                      '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'TC_PAIRS_OUTPUT_TEMPLATE')
        c_dict['SKIP_REFORMAT'] = self.config.getbool('config',
                                                      'TC_PAIRS_SKIP_IF_REFORMAT_EXISTS',
                                                      False)
        c_dict['SKIP_OUTPUT'] = self.config.getbool('config',
                                                      'TC_PAIRS_SKIP_IF_OUTPUT_EXISTS',
                                                      False)
        c_dict['REFORMAT_DECK'] = self.config.getbool('config',
                                                       'TC_PAIRS_REFORMAT_DECK',
                                                       False)
        c_dict['REFORMAT_DECK_TYPE'] = \
                self.config.getstr('config', 'TC_PAIRS_REFORMAT_TYPE',
                                   'SBU')
        c_dict['REFORMAT_DIR'] = self.config.getdir('TC_PAIRS_REFORMAT_DIR',
                         os.path.join(c_dict['OUTPUT_BASE'],'track_data_atcf'))

        c_dict['GET_ADECK'] = True if c_dict['ADECK_TEMPLATE'] else False
        c_dict['GET_EDECK'] = True if c_dict['EDECK_TEMPLATE'] else False

        return c_dict

    def run_all_times(self):
        """! Build up the command to invoke the MET tool tc_pairs.
        """
        # if running in READ_ALL_FILES mode, call tc_pairs once and exit
        if self.c_dict['READ_ALL_FILES']:
            # Set up the environment variable to be used in the tc_pairs Config
            self.set_env_vars(None)
            self.bdeck = [self.c_dict['BDECK_DIR']]

            adeck_dir = self.c_dict['ADECK_DIR']
            edeck_dir = self.c_dict['EDECK_DIR']

            if adeck_dir:
                self.adeck = [adeck_dir]

            if edeck_dir:
                self.edeck = [edeck_dir]

            self.outdir = self.c_dict['OUTPUT_DIR']
            self.outfile = 'tc_pairs'

            cmd = self.get_command()
            if cmd is None:
                self.logger.error("Could not generate command")
                return

            output_path = self.get_output_path()+'.tcst'
            if os.path.isfile(output_path) and self.c_dict['SKIP_OUTPUT'] is True:
                self.logger.debug('Skip running tc_pairs because '+\
                                  'output file {} already exists'.format(output_path)+\
                                  'Change TC_PAIRS_SKIP_IF_OUTPUT_EXISTS to False to '+\
                                  'overwrite file')
            else:
                self.build()

            return True

        # use init begin as run time (start of the storm)
        input_dict = {'init' :
                      datetime.datetime.strptime(self.c_dict['INIT_BEG'],
                                                 self.c_dict['INIT_TIME_FMT'])
                      }

        self.run_at_time(input_dict)

    def run_at_time(self, input_dict):
        """! Create the arguments to run MET tc_pairs
             Args:
                 input_dict dictionary containing init or valid time
             Returns:
        """
        # fill in time info dictionary
        time_info = time_util.ti_calculate(input_dict)

        # Set up the environment variable to be used in the TCPairs Config
        # file (TC_PAIRS_CONFIG_FILE)
        self.set_env_vars(time_info)

        # set output dir
        self.outdir = self.c_dict['OUTPUT_DIR']

        # get items to filter bdeck files
        # set each to default wildcard character unless specified in conf
        basin_list = [ '??' ]
        cyclone_list = [ '*' ]
        model_list = [ '*' ]
        storm_id_list = [ '*' ]
        use_storm_id = False

        if self.c_dict['STORM_ID']:
            storm_id_list = self.c_dict['STORM_ID']
            use_storm_id = True

        # if storm id and any other filter is set, error and exit

        if self.c_dict['BASIN']:
            if use_storm_id:
                self.logger.error('Cannot filter by both BASIN and STORM_ID')
                exit(1)
            basin_list = self.c_dict['BASIN']

        if self.c_dict['CYCLONE']:
            if use_storm_id:
                self.logger.error('Cannot filter by both CYCLONE and STORM_ID')
                exit(1)
            cyclone_list = self.c_dict['CYCLONE']

        if self.c_dict['MODEL']:
            model_list = self.c_dict['MODEL']

        if use_storm_id:
            for storm_id in storm_id_list:
                # pull out info from storm_id and process
                match = re.match('(\w{2})(\d{2})(\d{4})', storm_id)
                if not match:
                    self.logger.error('Incorrect STORM_ID format: {}'
                                      .format(storm_id))
                    exit(1)

                basin = match.group(1).lower()
                cyclone = match.group(2)
                year =  match.group(3)

                init_year = time_info['init'].strftime('%Y')
                if year != init_year:
                    msg = 'Year specified in STORM_ID {}'.format(storm_id) +\
                          ' ({})'.format(year) +\
                          ' does not match init time year {}'.format(init_year)
                    msg += '. Skipping...'
                    self.logger.warning(msg)
                    continue

                self.process_data(basin, cyclone, time_info, model_list)
        else:
            for basin in [basin.lower() for basin in basin_list]:
                for cyclone in cyclone_list:
                    self.process_data(basin, cyclone, time_info, model_list)


        return True

    def set_env_vars(self, time_info):
        """! Set up all the environment variables that are assigned
             in the METplus config file which are to be used by the MET
            TC-pairs config file.

             Args:
                 nothing - retrieves necessary MET+ config values via
                           class attributes

             Returns:
                 nothing - sets the environment variables
        """
        # pylint:disable=protected-access
        print_list = ['INIT_BEG', 'INIT_END', 'INIT_INCLUDE', 'INIT_EXCLUDE',
                      'MODEL', 'STORM_ID', 'BASIN', 'CYCLONE', 'STORM_NAME',
                      'VALID_BEG', 'VALID_END', 'DLAND_FILE']

        # For all cases below, we need to do some pre-processing so that
        #  Python will use " and not ' because currently MET doesn't
        # support single-quotes.

        # INIT_BEG, INIT_END
        # pull out YYYYMMDD from INIT_BEG/END
        tmp_init_beg = self.c_dict['INIT_BEG'][0:8]
        tmp_init_end = self.c_dict['INIT_END'][0:8]

        if not tmp_init_beg:
            self.add_env_var(b'INIT_BEG', "")
        else:
            init_beg = str(tmp_init_beg).replace("\'", "\"")
            init_beg_str = ''.join(init_beg.split())
            self.add_env_var(b'INIT_BEG', str(init_beg_str))

        if not tmp_init_end:
            self.add_env_var(b'INIT_END', "")
        else:
            init_end = str(tmp_init_end).replace("\'", "\"")
            init_end_str = ''.join(init_end.split())
            self.add_env_var(b'INIT_END', str(init_end_str))

        # INIT_INCLUDE and INIT_EXCLUDE
        # Used to set init_inc in "TC_PAIRS_CONFIG_FILE"
        tmp_init_inc = self.c_dict['INIT_INCLUDE']
        if not tmp_init_inc:
            self.add_env_var('INIT_INCLUDE', "[]")
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file after removing whitespace
            # and replacing ' with ".
            init_inc = str(tmp_init_inc).replace("\'", "\"")
            init_inc_str = ''.join(init_inc.split())
            self.add_env_var('INIT_INCLUDE', str(init_inc_str))

        tmp_init_exc = self.c_dict['INIT_EXCLUDE']
        if not tmp_init_exc:
            # Empty, MET is expecting [] to indicate all models are
            # to be included
            self.add_env_var('INIT_EXCLUDE', "[]")
        else:
            # Replace ' with " and remove whitespace
            init_exc = str(tmp_init_exc).replace("\'", "\"")
            init_exc_str = ''.join(init_exc.split())
            self.add_env_var('INIT_EXCLUDE', str(init_exc_str))

        # MODEL
        tmp_model = self.c_dict['MODEL']
        if not tmp_model:
            # Empty, MET is expecting [] to indicate all models are to be
            # included
            self.add_env_var('MODEL', "[]")
        else:
            # Replace ' with " and remove whitespace
            model = str(tmp_model).replace("\'", "\"")
            model_str = ''.join(model.split())
            self.add_env_var(b'MODEL', str(model_str))

        # STORM_ID
        tmp_storm_id = self.c_dict['STORM_ID']
        if not tmp_storm_id:
            # Empty, use all storm_ids, indicate this to MET via '[]'
            self.add_env_var('STORM_ID', "[]")
        else:
            # Replace ' with " and remove whitespace
            storm_id = str(tmp_storm_id).replace("\'", "\"")
            storm_id_str = ''.join(storm_id.split())
            self.add_env_var(b'STORM_ID', str(storm_id_str))

        # BASIN
        tmp_basin = self.c_dict['BASIN']
        if not tmp_basin:
            # Empty, we want all basins.  Send MET '[]' to indicate that
            # we want all the basins.
            self.add_env_var('BASIN', "[]")
        else:
            # Replace any ' with " and remove whitespace.
            basin = str(tmp_basin).replace("\'", "\"")
            basin_str = ''.join(basin.split())
            self.add_env_var(b'BASIN', str(basin_str))

        # CYCLONE
        tmp_cyclone = self.c_dict['CYCLONE']
        if not tmp_cyclone:
            # Empty, use all cyclones, send '[]' to MET.
            self.add_env_var('CYCLONE', "[]")
        else:
            # add storm month to each cyclone item if reformatting SBU
            if self.c_dict['REFORMAT_DECK'] and \
               self.c_dict['REFORMAT_DECK_TYPE'] == 'SBU':
                if time_info is None:
                    storm_month = self.c_dict['INIT_BEG'][4:6]
                else:
                    storm_month = time_info['init'].strftime('%m')
                tmp_cyclone = [storm_month + c for c in tmp_cyclone]

            # Replace ' with " and get rid of any whitespace
            cyclone = str(tmp_cyclone).replace("\'", "\"")
            cyclone_str = ''.join(cyclone.split())
            self.add_env_var(b'CYCLONE', str(cyclone_str))

        # STORM_NAME
        tmp_storm_name = self.c_dict['STORM_NAME']
        if not tmp_storm_name:
            # Empty, equivalent to 'STORM_NAME = "[]"; in MET config file,
            # use all storm names.
            self.add_env_var('STORM_NAME', "[]")
        else:
            storm_name = str(tmp_storm_name).replace("\'", "\"")
            storm_name_str = ''.join(storm_name.split())
            self.add_env_var(b'STORM_NAME', str(storm_name_str))

        # Valid time window variables
        tmp_valid_beg = self.c_dict['VALID_BEG']
        tmp_valid_end = self.c_dict['VALID_END']

        if not tmp_valid_beg:
            self.add_env_var(b'VALID_BEG', "")
        else:
            valid_beg = str(tmp_valid_beg).replace("\'", "\"")
            valid_beg_str = ''.join(valid_beg.split())
            self.add_env_var(b'VALID_BEG', str(valid_beg_str))

        if not tmp_valid_end:
            self.add_env_var(b'VALID_END', "")
        else:
            valid_end = str(tmp_valid_end).replace("\'", "\"")
            valid_end_str = ''.join(valid_end.split())
            self.add_env_var(b'VALID_END', str(valid_end_str))

        # DLAND_FILE
        tmp_dland_file = self.c_dict['DLAND_FILE']
        self.add_env_var(b'DLAND_FILE', str(tmp_dland_file))

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

    def process_data(self, basin, cyclone, time_info, model_list):
        # get bdeck file
        bdeck_files = []

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
        ss = StringSub(self.logger,
                       self.c_dict['BDECK_TEMPLATE'],
                       basin=basin,
                       cyclone=cyclone,
                       **time_info)
        bdeck_glob = os.path.join(self.c_dict['BDECK_DIR'],
                                  ss.doStringSub())
        self.logger.debug('Looking for BDECK: {}'.format(bdeck_glob))

        # get all files that match expression
        bdeck_files = sorted(glob.glob(bdeck_glob))

        # if no bdeck_files found
        if len(bdeck_files) == 0:
            self.logger.warning('No BDECK files found')
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
                ss = StringSub(self.logger,
                               self.c_dict['BDECK_TEMPLATE'],
                               basin=basin_regex,
                               cyclone=cyclone_regex,
                               **time_info)
                bdeck_regex = os.path.join(self.c_dict['BDECK_DIR'],
                                           ss.doStringSub())

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

            # create lists for deck files, put bdeck in list so it can be handled
            # the same as a and e for reformatting even though it will always be
            # size 1
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
                self.logger.debug('Could not find any corresponding '
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
                ss = StringSub(self.logger,
                               self.c_dict['OUTPUT_TEMPLATE'],
                               basin=current_basin,
                               cyclone=current_cyclone,
                               **time_info)
                output_file = ss.doStringSub()
            else:
                output_file = 'tc_pairs'
            self.outfile = output_file

            # build command and run tc_pairs
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("Could not generate command")
                return

            output_path = self.get_output_path()+'.tcst'
            if os.path.isfile(output_path) and self.c_dict['SKIP_OUTPUT'] is True:
                self.logger.debug('Skip running tc_pairs because '+\
                                  'output file {} already exists'.format(output_path)+\
                                  'Change TC_PAIRS_SKIP_IF_OUTPUT_EXISTS to False to '+\
                                  'overwrite file')
            else:
                self.build()

    def find_deck_files(self, deck, basin, cyclone, model_list,
                        time_info):
        deck_list = []
        # get matching adeck wildcard expression for first model
        ss = StringSub(self.logger,
                       self.c_dict[deck+'DECK_TEMPLATE'],
                       basin=basin,
                       cyclone=cyclone,
                       model=model_list[0],
                       **time_info)
        deck_expr = os.path.join(self.c_dict[deck+'DECK_DIR'],
                                  ss.doStringSub())

        # add adeck files if they exist
        for model in model_list:
            deck_glob = deck_expr.replace(model_list[0], model)
            self.logger.debug('Looking for {}DECK file: {}'.format(deck,
                                                                   deck_glob))
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
            if os.path.isfile(outfile) and self.c_dict['SKIP_REFORMAT'] is True:
                self.logger.debug('Skip processing {} because '.format(deck) +\
                                  'reformatted file already exists. Change '+\
                                  'TC_PAIRS_SKIP_IF_REFORMAT_EXISTS to False to '+\
                                  'overwrite file')
            else:
                self.logger.debug('Reformatting {} to {}'.format(deck, outfile))
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
            self.logger.error("No app path specified. You must use a subclass")
            return None

        if not self.adeck and not self.edeck:
            self.logger.error('Neither ADECK nor EDECK files set')
            return None

        if not self.bdeck:
            self.logger.error('BDECK file not set')
            return None

        config_file = self.c_dict['TC_PAIRS_CONFIG_FILE']
        if config_file is None:
            self.logger.error('Config file not set')
            return None

        output_path = self.get_output_path()
        if output_path is '':
            self.logger.error('Output path not set')
            return None

        # create directory containing output file if it doesn't exist
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        cmd = '{} -v {}'.format(self.app_path, self.verbose)
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
        out_file = open(out_csvfile, "wb")

        # Tell the write to use the line separator
        # "\n" instead of the DOS "\r\n"
        writer = csv.writer(out_file, lineterminator="\n")

        with open(in_csvfile) as csvfile:

            in_file_reader = csv.reader(csvfile)

            # enumerate returns a tuple but only the row is useful
            # for this application.  Ignoring 'index' is reasonable.
            for index, row in enumerate(in_file_reader):
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

if __name__ == "__main__":
    util.run_stand_alone("tc_pairs_wrapper", "TcPairs")
