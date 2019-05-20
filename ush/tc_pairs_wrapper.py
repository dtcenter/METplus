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
# TODO - critical  must import grid_to_obs_util before CommandBuilder
# MUST import grid_to_obs_util BEFORE command_builder, else it breaks stand-alone
import time_util
import met_util as util
import config_metplus
from string_template_substitution import StringSub
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
        self.adeck = None
        self.bdeck = None
        self.c_dict = self.create_c_dict()

    def create_c_dict(self):
        """! Create a dictionary containing all the values set in the config file.
             This will make it easier for unit testing.

             Args:

             Returns:
                 c_dict - A dictionary of the values from the config file

        """
        # pylint:disable=protected-access
        c_dict = dict()
        c_dict['MISSING_VAL_TO_REPLACE'] = self.config.getstr('config',
                                                                'MISSING_VAL_TO_REPLACE', '-99')
        c_dict['MISSING_VAL'] = self.config.getstr('config', 'MISSING_VAL', '-9999')
#        c_dict['TRACK_TYPE'] = self.config.getstr('config', 'TRACK_TYPE')
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
        c_dict['ADECK_TRACK_DATA_DIR'] = \
                self.config.getdir('ADECK_TRACK_DATA_DIR')
        c_dict['BDECK_TRACK_DATA_DIR'] = \
                self.config.getdir('BDECK_TRACK_DATA_DIR')
#        c_dict['TRACK_DATA_SUBDIR_MOD'] = self.config.getdir(
#            'TRACK_DATA_SUBDIR_MOD')
#        c_dict['ADECK_FILE_PREFIX'] = self.config.getstr('config',
#                                                           'ADECK_FILE_PREFIX')
        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_PAIRS_DIR')
#        c_dict['ADECK_FILE_PREFIX'] = self.config.getstr('config',
#                                                           'ADECK_FILE_PREFIX')
#        c_dict['BDECK_FILE_PREFIX'] = self.config.getstr('config',
#                                                           'BDECK_FILE_PREFIX')
        c_dict['TOP_LEVEL_DIRS'] = self.config.getbool('config',
                                                        'TOP_LEVEL_DIRS')
        c_dict['OUTPUT_BASE'] = self.config.getstr('dir', 'OUTPUT_BASE')
        c_dict['CYCLONE'] = util.getlist(
            self.config.getstr('config', 'CYCLONE', ''))
        c_dict['MODEL'] = util.getlist(self.config.getstr('config', 'MODEL', ''))
        c_dict['STORM_ID'] = util.getlist(
            self.config.getstr('config', 'STORM_ID', ''))
        c_dict['BASIN'] = util.getlist(self.config.getstr('config', 'BASIN', ''))
        c_dict['STORM_NAME'] = util.getlist(
            self.config.getstr('config', 'STORM_NAME'))
        c_dict['DLAND_FILE'] = self.config.getstr('config', 'DLAND_FILE')

        c_dict['ADECK_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'TC_PAIRS_ADECK_TEMPLATE')
        c_dict['BDECK_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'TC_PAIRS_BDECK_TEMPLATE')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                       'TC_PAIRS_OUTPUT_TEMPLATE')
        c_dict['REFORMAT_ADECK'] = self.config.getbool('config',
                                                       'TC_PAIRS_REFORMAT_ADECK',
                                                       False)
        c_dict['REFORMAT_BDECK'] = self.config.getbool('config',
                                                       'TC_PAIRS_REFORMAT_BDECK',
                                                       False)
        c_dict['REFORMAT_DIR'] = self.config.getdir('TC_PAIRS_REFORMAT_DIR',
                         os.path.join(c_dict['OUTPUT_BASE'],'track_data_atcf'))

        return c_dict

    def run_all_times(self):
        """! Build up the command to invoke the MET tool tc_pairs.
        """
        # Set up the environment variable to be used in the TCPairs Config
        # file (TC_PAIRS_CONFIG_FILE)
        self.set_env_vars()

        # if running in TOP_LEVEL_DIRS mode, call tc_pairs once and exit
        if self.c_dict['TOP_LEVEL_DIRS']:
            self.adeck = [self.c_dict['ADECK_TRACK_DATA_DIR']]
            self.bdeck = [self.c_dict['BDECK_TRACK_DATA_DIR']]
            self.outdir = self.c_dict['OUTPUT_DIR']
            self.outfile = 'tc_pairs'

            cmd = self.get_command()
            if cmd is None:
                self.logger.error("Could not generate command")
                return

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

        # set output dir
        self.outdir = self.c_dict['OUTPUT_DIR']

        # get items to filter adeck files
        # set each to default wildcard character unless specified in conf
        basin_list = [ '*' ]
        cyclone_list = [ '*' ]
        date_list = [ '*' ]
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
#            if use_storm_id:
#                self.logger.error('Cannot filter by both MODEL and STORM_ID')
#               exit(1)
            model_list = self.c_dict['MODEL']

        if use_storm_id:
            for storm_id in storm_id_list:
                # pull out info from storm_id and process
                match = re.match('(\w{2})(\d*)(\d{4})', storm_id)
                if not match:
                    self.logger.error('Incorrect STORM_ID format: {}'
                                      .format(storm_id))
                    exit(1)

                basin = match.group(1).lower()
                cyclone = int(match.group(2))
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
                    self.process_data(basin, int(cyclone), time_info, model_list)


        return True

    def set_env_vars(self):
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
        # get adeck files
        # TODO: support edeck
        # TODO: add misc?
        adeck_files = []
        ss = StringSub(self.logger,
                       self.c_dict['ADECK_TEMPLATE'],
                       basin=basin,
                       cyclone=cyclone,
                       model=model_list[0],
                       **time_info)
        adeck_glob = os.path.join(self.c_dict['ADECK_TRACK_DATA_DIR'],
                                  ss.doStringSub())
        self.logger.debug('Looking for ADECK: {}'.format(adeck_glob))
        # get all files that match expression
        adeck_files = sorted(glob.glob(adeck_glob))

        # if no adeck_files found
        if len(adeck_files) == 0:
            return False

        # get matching bdeck wildcard expression
        ss = StringSub(self.logger,
                       self.c_dict['BDECK_TEMPLATE'],
                       basin=basin,
                       cyclone=cyclone,
                       **time_info)
        bdeck_glob = os.path.join(self.c_dict['BDECK_TRACK_DATA_DIR'],
                                  ss.doStringSub())

        # find corresponding bdeck and other model adeck files
        for adeck_file in adeck_files:
            # if wildcard was used in adeck, pull out what was
            # substituted for * to find corresponding bdeck file
            matches = []
            if '*' in adeck_glob:
                pattern = adeck_glob.replace('*', '(.*)')
                match = re.match(pattern, adeck_file)
                if match:
                    matches = match.groups()

            bdeck_file = bdeck_glob
            for m in matches:
                bdeck_file = bdeck_file.replace('*', m, 1)

            self.logger.debug('Looking for BDECK {}'.format(bdeck_file))

            # continue if bdeck file is not found
            if not os.path.isfile(bdeck_file):
                continue

            adeck_list = [adeck_file]
            bdeck_list = [bdeck_file]

            # add other adeck models if they exist
            for model in model_list[1:]:
                new_adeck = adeck_file.replace(model_list[0], model)
                if os.path.isfile(new_adeck):
                    self.logger.debug('Adding addition ADECK: {}'.format(new_adeck))
                    adeck_list.append(new_adeck)

            # reformat extra tropical cyclone files if necessary
            if self.c_dict['REFORMAT_ADECK']:
                adeck_list = self.reformat_files(adeck_list, 'A', time_info)

            if self.c_dict['REFORMAT_BDECK']:
                bdeck_list = self.reformat_files(bdeck_list, 'B', time_info)

            self.adeck = adeck_list
            self.bdeck = bdeck_list

            # get output filename from template
            # replacing * with info from adeck file
            ss = StringSub(self.logger,
                           self.c_dict['OUTPUT_TEMPLATE'],
                           basin=basin,
                           cyclone=cyclone,
                           **time_info)
            output_file = ss.doStringSub()

            # replace * in output file name with info from adeck file
            for m in matches:
                output_file = output_file.replace('*', m, 1)
            self.outfile = output_file

            # build command and run tc_pairs
            cmd = self.get_command()
            if cmd is None:
                self.logger.error("Could not generate command")
                return

            self.build()

    def reformat_files(self, file_list, deck_type, time_info):
        storm_month = time_info['init'].strftime('%m')
        missing_values = \
            (self.c_dict['MISSING_VAL_TO_REPLACE'],
             self.c_dict['MISSING_VAL'])
        deck_dir = self.c_dict[deck_type+'DECK_TRACK_DATA_DIR']
        reformat_dir = self.c_dict['REFORMAT_DIR']

        outfiles = []
        for deck in file_list:
            outfile = deck.replace(deck_dir,
                                   reformat_dir)
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

        if not self.adeck:
            self.logger.error('ADECK file not set')
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

        # TODO: Move adding app_path, verbose, and any other items that are
        #  in every MET command call to a function to be called instead
        cmd = '{} -v {}'.format(self.app_path, self.verbose)
        cmd += ' -adeck {} -bdeck {}'.format(' '.join(self.adeck),
                                             ' '.join(self.bdeck))
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
            # pylint:disable=unused-variable
            # enumerate returns a tuple but only the row is useful
            # for this application.  Ignoring 'index' is reasonable.
            for index, row in enumerate(in_file_reader):
                # Create a list for the modified lines
                row_list = []

                # Replace the second column (storm number) with
                # the month followed by the storm number
                # e.g. Replace 0006 with 010006
#                row[1] = " " + storm_month + (row[1]).strip()

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
