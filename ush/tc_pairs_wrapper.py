#!/usr/bin/env python

"""
Program Name: tc_pairs_wrapper.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Invokes the MET tool tc_pairs to parse ADeck and BDeck ATCF_by_pairs files,
          filter the data, and match them up
History Log:  Initial version
Usage:
Parameters: None
Input Files: adeck and bdeck files
Output Files: tc_pairs files
Condition codes: 0 for success, 1 for failure

"""

from __future__ import (print_function, division)

import collections
import os
import sys
import re
import csv
import produtil.setup
from produtil.run import ExitStatusException
# TODO - critical  must import met_util before CommandBuilder
# MUST import met_util BEFORE command_builder, else it breaks stand-alone
from command_builder import CommandBuilder
import met_util as util
import config_metplus
from string_template_substitution import StringSub

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

    def __init__(self, p, logger):
        super(TcPairsWrapper, self).__init__(p, logger)
        self.config = p
        self.app_path = os.path.join(p.getdir('MET_INSTALL_DIR'),
                                     'bin/tc_pairs')
        self.app_name = os.path.basename(self.app_path)
        if self.logger is None:
            self.logger = util.get_logger(self.p, sublog='TcPairs')
        self.cmd = ''
        self.logger.info("Initialized TcPairsWrapper")
        self.tcp_dict = self.create_tcp_dict()

    def create_tcp_dict(self):
        """! Create a dictionary containing all the values set in the config file.
             This will make it easier for unit testing.

             Args:

             Returns:
                 tcp_dict - A dictionary of the values from the config file

        """
        # pylint:disable=protected-access
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug("DEBUG|" + cur_filename + "|" + cur_function + ": creating the tc_pairs dictionary with"
                                                                         " values from the config file")
        tcp_dict = dict()
        tcp_dict['MISSING_VAL_TO_REPLACE'] = self.config.getstr('config', 'MISSING_VAL_TO_REPLACE')
        tcp_dict['MISSING_VAL'] = self.config.getstr('config', 'MISSING_VAL')
        tcp_dict['TRACK_TYPE'] = self.config.getstr('config', 'TRACK_TYPE')
        tcp_dict['INIT_BEG'] = self.config.getstr('config', 'INIT_BEG')
        tcp_dict['INIT_END'] = self.config.getstr('config', 'INIT_END')
        tcp_dict['INIT_INCREMENT'] = int(self.config.getint('config', 'INIT_INCREMENT') / 3600)
        tcp_dict['INIT_HOUR_END'] = self.config.getstr('config', 'INIT_HOUR_END')
        tcp_dict['INIT_INCLUDE'] = self.config.getstr('config', 'INIT_INCLUDE')
        tcp_dict['INIT_EXCLUDE'] = self.config.getstr('config', 'INIT_EXCLUDE')
        tcp_dict['VALID_BEG'] = self.config.getstr('config', 'VALID_BEG')
        tcp_dict['VALID_END'] = self.config.getstr('config', 'VALID_END')
        tcp_dict['ADECK_TRACK_DATA_DIR'] = self.config.getdir('ADECK_TRACK_DATA_DIR')
        tcp_dict['BDECK_TRACK_DATA_DIR'] = self.config.getdir('BDECK_TRACK_DATA_DIR')
        tcp_dict['TRACK_DATA_SUBDIR_MOD'] = self.config.getdir('TRACK_DATA_SUBDIR_MOD')
        tcp_dict['ADECK_FILE_PREFIX'] = self.config.getstr('config', 'ADECK_FILE_PREFIX')
        tcp_dict['TC_PAIRS_DIR'] = self.config.getdir('TC_PAIRS_DIR')
        tcp_dict['ADECK_FILE_PREFIX'] = self.config.getstr('config', 'ADECK_FILE_PREFIX')
        tcp_dict['BDECK_FILE_PREFIX'] = self.config.getstr('config', 'BDECK_FILE_PREFIX')
        tcp_dict['TOP_LEVEL_DIRS'] = self.config.getstr('config', 'TOP_LEVEL_DIRS')
        tcp_dict['MET_INSTALL_DIR'] = self.config.getdir('MET_INSTALL_DIR')
        tcp_dict['OUTPUT_BASE'] =  self.config.getstr('dir', 'OUTPUT_BASE')
        tcp_dict['BASIN'] =  self.config.getstr('config', 'BASIN')
        tcp_dict['CYCLONE'] = util.getlist(self.config.getstr('config', 'CYCLONE'))
        tcp_dict['MODEL'] = util.getlist(self.config.getstr('config', 'MODEL'))
        tcp_dict['STORM_ID'] = util.getlist(self.config.getstr('config', 'STORM_ID'))
        tcp_dict['BASIN'] = util.getlist(self.config.getstr('config', 'BASIN'))
        tcp_dict['STORM_NAME'] = util.getlist(self.config.getstr('config', 'STORM_NAME'))
        tcp_dict['DLAND_FILE'] = self.config.getstr('config', 'DLAND_FILE')
        tcp_dict['FORECAST_TMPL'] = self.config.getraw('filename_templates', 'FORECAST_TMPL')
        tcp_dict['REFERENCE_TMPL'] = self.config.getraw('filename_templates', 'REFERENCE_TMPL')

        return tcp_dict

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

        self.logger.debug("DEBUG|run_tc_pairs.py|read_modify_write_file")

        # pylint:disable=protected-access
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug("DEBUG|" + cur_filename + "|" + cur_function)

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
        self.logger.debug("DEBUG|" + cur_function + "|" + cur_filename +
                          " finished")

    def run_all_times(self):
        """! Build up the command to invoke the MET tool tc_pairs.
        """

        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.info(cur_filename + '|' + cur_function +
                         "|Started run_all_times in TcPairsWrapper")

        # Set up the environment variable to be used in the TCPairs Config
        # file (TC_PAIRS_CONFIG_FILE)
        self.set_env_vars()

        # Differentiate between non-ATCF_by_pairs data and ATCF_by_pairs track data based on
        # the TRACK_TYPE
        track_type = self.tcp_dict['TRACK_TYPE']
        if track_type == "extra_tropical_cyclone":
            self.process_non_atcf()
        else:
            self.process_atcf()

        self.logger.info("Completed run_all_times in TcPairsWrapper")

    def process_non_atcf(self):
        """! Original implementation of this wrapper- for
             extra-tropical-cyclone data in non-ATCF_by_pairs format
             We need to do extra processing in the form of replacing -99
             with -9999 for missing values, removing the third column,
             which contains the YYYYMMDDhh_lon_lat_Cy and creating a column
             with the year and Cy (annual cyclone number) and setting this
             to the second column.

           Args:

           Returns:
               Nothing, creates the command to invoke MET tc_pairs and
               then calls another function to run the command
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(cur_filename + '|' + cur_function +
                          '| building command for non-ATCF_by_pairs track data...')

        missing_values = \
            (self.tcp_dict['MISSING_VAL_TO_REPLACE'],
             self.tcp_dict['MISSING_VAL'])

        # Get the desired YYYYMMDD_HH init increment list
        # convert the increment INIT_INC from seconds to hours
        init_list = util.gen_init_list(
            self.tcp_dict['INIT_BEG'],
            self.tcp_dict['INIT_END'],
            self.tcp_dict['INIT_INCREMENT'],
            self.tcp_dict['INIT_HOUR_END'])

        # get a list of YYYYMM values
        year_month_list = []
        for init in init_list:
            if init[0:6] not in year_month_list:
                year_month_list.append(init[0:6])

        # Get a directory path listing of the dated subdirectories
        # (YYYYMM format) in the track_data directory
        dir_list = []
        # Get a list of all the year_month directories in the
        # track data directory specified in the config file.

        # Since the atrack and btrack data are in the same directory, use the
        # directory specified in the ATRACK_DATA_DIR
        atrack_dir = self.tcp_dict['ADECK_TRACK_DATA_DIR']
        for year_month in os.listdir(atrack_dir):
            # if the full directory path isn't an empty directory,
            # check if the current year_month is the requested time.
            if os.path.isdir(os.path.join(atrack_dir)) \
                    and year_month in year_month_list:
                dir_list.append(os.path.join(atrack_dir, year_month))

        if not dir_list:
            self.logger.warning("ERROR | [" + cur_filename + ":" +
                                cur_function + "] | There are no dated"
                                               "sub-directories (YYYYMM) " +
                                "with input data as expected in: " +
                                self.config.getdir('TRACK_DATA_DIR'))
            exit(0)

        # Get a list of files in the dated subdirectories
        for cur_dir in dir_list:
            track_files_for_date = os.listdir(cur_dir)

            # Create an atcf output directory for writing the modified
            # files
            adeck_mod = os.path.join(
                self.tcp_dict['TRACK_DATA_SUBDIR_MOD'],
                os.path.basename(cur_dir))
            bdeck_mod = os.path.join(
                self.tcp_dict['TRACK_DATA_SUBDIR_MOD'],
                os.path.basename(cur_dir))
            produtil.fileop.makedirs(adeck_mod, logger=self.logger)

            # Iterate over the files, modifying them and writing new output
            # files if necessary ("extra_tropical_cyclone" track type), and
            # run tc_pairs
            for cur_track_file in track_files_for_date:
                # Check to see if the files have the ADeck prefix
                if cur_track_file.startswith(
                        self.tcp_dict['ADECK_FILE_PREFIX']):
                    # Create the output directory for the pairs, if
                    # it doesn't already exist
                    pairs_out_dir = \
                        os.path.join(self.tcp_dict['TC_PAIRS_DIR'],
                                     os.path.basename(cur_dir))
                    produtil.fileop.makedirs(pairs_out_dir, logger=self.logger)

                    # Perform the extra processing for non-ATCF_by_pairs formatted
                    # extra_tropical_cyclone data.
                    # Form the adeck and bdeck input filename paths
                    adeck_in_file_path = os.path.join(cur_dir,
                                                      cur_track_file)
                    bdeck_in_file_path = re.sub(
                        self.tcp_dict['ADECK_FILE_PREFIX'],
                        self.tcp_dict['BDECK_FILE_PREFIX'],
                        adeck_in_file_path)
                    adeck_file_path = os.path.join(adeck_mod,
                                                   cur_track_file)
                    bdeck_file_path = os.path.join(bdeck_mod, re.sub(
                        self.tcp_dict['ADECK_FILE_PREFIX'],
                        self.tcp_dict['BDECK_FILE_PREFIX'],
                        cur_track_file))

                    # Get the YYYYMM e.g 201203 in amlq2012033118.gfso.0004
                    year_month = cur_track_file[4:10]

                    # Get the MM from the YYYYMM
                    storm_month = year_month[-2:]

                    # Set up the adeck and bdeck track file paths for the
                    # extra tropical cyclone data.
                    self.setup_tropical_track_dirs(adeck_in_file_path,
                                                   adeck_file_path,
                                                   storm_month,
                                                   missing_values)

                    # Read in the bdeck file, modify it,
                    # and write a new bdeck file
                    # Check for existence of data and overwrite if desired
                    self.setup_tropical_track_dirs(bdeck_in_file_path,
                                                   bdeck_file_path,
                                                   storm_month,
                                                   missing_values)

                    # Run tc_pairs
                    self.cmd = self.build_non_atcf_tc_pairs(pairs_out_dir,
                                                            adeck_file_path,
                                                            bdeck_file_path,
                                                            cur_track_file)
                    self.build()

    def process_atcf(self):
        """! Create the arguments to run MET tc_pairs on ATCF_by_pairs formatted input data.
             Args:

             Returns:

        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(
            cur_filename + '|' + cur_function +
            '| Processing ATCF_by_pairs track files...')

        # Get the filename templates
        adeck_input_dir = self.tcp_dict['ADECK_TRACK_DATA_DIR']
        bdeck_input_dir = self.tcp_dict['BDECK_TRACK_DATA_DIR']
        fcst_filename_tmpl = self.tcp_dict['FORECAST_TMPL']
        reference_filename_tmpl = self.tcp_dict['REFERENCE_TMPL']
        top_level_dir = self.tcp_dict['TOP_LEVEL_DIRS'].lower()
        if top_level_dir == 'yes':
            by_dir = True
        else:
            by_dir = False

        # Commands common to both methods of invoking tc_pairs
        pairs_out_dir = self.tcp_dict['TC_PAIRS_DIR']
        produtil.fileop.makedirs(pairs_out_dir, logger=self.logger)

        # User specifies to run tc_pairs with top-level dirs for A-deck and B-deck input files
        if by_dir:
            # Invoke MET tc_pairs with top-level directories
            tc_pairs_exe = os.path.join(self.tcp_dict['MET_INSTALL_DIR'],
                                        'bin/tc_pairs')
            outfile = os.path.join(self.tcp_dict['TC_PAIRS_DIR'], "tc_pairs")
            cmd_list = [tc_pairs_exe,
                        " -adeck ",
                        adeck_input_dir, " -bdeck ",
                        bdeck_input_dir, " -config ",
                        self.config.getstr('config', 'TC_PAIRS_CONFIG_FILE'),
                        " -out ", outfile, " -v 50"]

            self.cmd = ''.join(cmd_list)
            self.logger.debug("DEBUG | [" + cur_filename + ":" +
                              cur_function + "] | " +
                              "Running tc_pairs with command: " +
                              self.cmd)

            self.build()
        else:
            # Invoke tc_pairs with A-deck and B-deck filenames. Get a list of all the input files (A-deck and B-deck),
            # and filter based on one or all of the following criteria: date, region, cyclone.

            init_list = util.gen_init_list(
                self.tcp_dict['INIT_BEG'],
                self.tcp_dict['INIT_END'],
                int(self.tcp_dict['INIT_INCREMENT'] / 3600),
                self.tcp_dict['INIT_HOUR_END'])

            # Look for files in the A-Deck and B-Deck
            # directories for files with times that are within the init time window. Employ
            # StringTemplateSubstitution to create a regex for the filename to assist in identifying the date,
            # region, and cyclone from the file name (if available) to perform filtering of input data prior to invoking
            # tc_pairs, making it run more efficiently.
            all_adeck_files = self.get_input_track_files(adeck_input_dir)
            all_bdeck_files = self.get_input_track_files(bdeck_input_dir)

            # Create the appropriate string template substitution object, based on what is defined in the
            # filename_templates
            (adeck_input_file_regex, adeck_sorted_keywords) = self.create_filename_regex(fcst_filename_tmpl)
            (bdeck_input_file_regex, bdeck_sorted_keywords) = self.create_filename_regex(reference_filename_tmpl)

            filtered_adeck_files = self.filter_input(all_adeck_files, init_list, adeck_input_file_regex,
                                                     adeck_sorted_keywords, fcst_filename_tmpl)
            filtered_bdeck_files = self.filter_input(all_bdeck_files, init_list, bdeck_input_file_regex,
                                                     bdeck_sorted_keywords, reference_filename_tmpl)

            # Unlike the other MET tools, the tc_pairs usage for this use case is:
            # tc_pairs\
            #  -adeck <top-level dir or file> \
            #  -bdeck <top-level dir or file> \
            #  -config <file>
            # [-out base] \
            # [-log file] \
            # [ -v level ]

            # Combine each A-Deck file with each B-Deck file (not performant, but since we made all attempts to
            # filter both A-Deck and B-Deck files based on date, region and cyclone, we have hopefully reduced
            # the number of pairings).
            config_file = self.tcp_dict['TC_PAIRS_CONFIG_FILE']
            tc_pairs_exe = os.path.join(self.tcp_dict['MET_INSTALL_DIR'],
                                        'bin/tc_pairs')
            out_base = self.tcp_dict['OUTPUT_BASE']
            for adeck in filtered_adeck_files:
                # Use the adeck base filename to create the output .tcst file
                basename = basename(adeck)
                m = re.match(r'(.*).dat', basename)
                if m:
                    filename_only = m.group(1)
                else:
                    self.logger.warning(
                        cur_function + "|" + cur_filename + ": A-deck filename doesn't have .dat extension, "
                                                            "using the A-deck filename as the base output .tcst file")
                    filename_only = adeck
                outfile = os.path.join(pairs_out_dir, filename_only)

                for bdeck in filtered_bdeck_files:
                    # cmd_list = [tc_pairs_exe, " -adeck ", adeck, " -bdeck ", bdeck, " -config ", config_file]
                    cmd_list = [tc_pairs_exe, " -adeck ", adeck, " -bdeck ", bdeck, " -config ", config_file, " -out ",
                                outfile, " -v 50"]
                    self.cmd = ''.join(cmd_list)
                    self.logger.debug("DEBUG | [" + cur_filename + ":" +
                                      cur_function + "] | " +
                                      "Running tc_pairs with command: " +
                                      self.cmd)
                    self.build()

    def get_date_format_info(self, tmpl):
        """! From the filename_templates template for the input track file, determine the format of the date:

             Args:
                @parm tmpl - The filename template as defined in the filename_templates section of the config file
             Returns:
                 date_len  - The length of the expected date string: 4 if YYYY, 6 if YYYYMM, 8 if YYYYMMDD and 10
                             if YYYYMMDDhh
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ":Determining date format information...")
        # Determine if we have YYYY, YYYYMM, YYYYMMDD, or YYYYMMDDhh for
        # the date string
        # date_format_match = re.match(r'(?i)\A(?:(%+[a-z])*)\Z', tmpl)
        date_format_match = re.match(r'.*\{date\?fmt=([\%+\w]{2,8}).*dat', tmpl)
        if date_format_match:
            # Determine whether we have YYYY (%Y), YYYYMM (%Y%m), YYYYMMdd (%Y%m%d), or YYYYMMddhh (%Y%m%d%h)
            first_match = date_format_match.group(1)
            match_len = len(first_match)
            if match_len == 8:
                # year month day hour, %Y%m%d%h
                date_len = 10
            elif match_len == 6:
                # year month day, %Y%m%d
                date_len = 8
            elif match_len == 4:
                # year month, %Y%m
                date_len = 6
            elif match_len == 2:
                # year, %Y
                date_len = 4
            else:
                self.logger.error(
                    'Date format specified in the filename_templates section does not match expected %Y, %Y%m, %Y%m%d, ' +
                    'or %Y%m%d%h format')
                exit(1)
        else:
            # No match return 0
            return 0
        return date_len

    def create_filename_regex(self, tmpl):
        """! Creates the regex of the forecast or reference filename as defined in the filename_template section
             of the config file.

           Args:
               @param tmpl - The filename template describing the forecast or reference input track file (full filepath)

           Returns:
               tuple of two values:
               input_file_regex - A regex string representing the filename. This will be useful when filtering based on
                             date, region, or cyclone.
               keywords_ordered -  A list of keywords, in the order in which they were found in the template string.
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ":Generating the filename regex from the filename_templates section.")

        # To filter files on the criteria of date, region, or cyclone (or any combination),
        # Use dummy values for the region and cyclone, to create a string template substitution object.
        # This string template substitution object will be used to replace the key-values in the filename
        # template with its corresponding regex.
        region = 'yz'
        cyclone = '00'
        date = '20170704'
        misc = 'misc_stuff'

        # The string template substitution object will be initialized based on what combination of the
        # keywords have been specified in the filename_templates section: date, region, cyclone. Since
        date_match = re.match(r'.*\{date\?fmt=(.*?)\}.*', tmpl)
        region_match = re.match(r'.*\{region\?fmt=(.*?)\}', tmpl)
        cyclone_match = re.match(r'.*\{cyclone\?fmt=(.*?)\}', tmpl)
        misc_match = re.match(r'.*\{misc\?fmt=(.*?)\}', tmpl)

        # Rather than having multiple if-elif to account for every possible combination of keywords in a
        # filename_template , store the keywords in a dictionary and use **kwargs to invoke StringSub with
        # this dictionary of keyword argument. Determine the order in which the keywords appear in the filename_template
        # and order the keywords, to facilitate filtering.
        keyword_index = {}
        if date_match:
            kwargs = {'date': date}
            [(m.start(), m.end()) for m in re.finditer(r".*\{date\?fmt=(.*?)\}.", tmpl)]
            keyword_index['date'] = m.start(1)
        if region_match:
            kwargs['region'] = region
            [(m.start(), m.end()) for m in re.finditer(r".*\{region\?fmt=(.*?)\}", tmpl)]
            keyword_index['region'] = m.start(1)
        if cyclone_match:
            kwargs['cyclone'] = cyclone
            [(m.start(), m.end()) for m in re.finditer(r".*\{cyclone\?fmt=(.*?)\}", tmpl)]
            keyword_index['cyclone'] = m.start(1)
        if misc_match:
            kwargs['misc'] = misc
            [(m.start(), m.end()) for m in re.finditer(r".*\{misc\?fmt=(.*?)\}", tmpl)]
            keyword_index['misc'] = m.start(1)
        string_sub = StringSub(self.logger, tmpl, **kwargs)
        input_file_regex = string_sub.create_cyclone_regex()

        # Get a list of the keywords in the order in which they appeared in the filename_template description
        ordered = collections.OrderedDict(sorted(keyword_index.items(), key=lambda t: t[1]))
        keywords_ordered = ordered.keys()
        return input_file_regex, keywords_ordered

    def filter_input(self, all_input_files, init_list, input_file_regex, sorted_keywords, tmpl):
        """! Filter the input track file based on any or all of the following:
             date, region, cyclone.

             Args:
                 @param all_input_files  -  a list of all the input track files (full file path)
                 @param init_list        -  a list of all init times in YYYYMMDD_hh format that define
                                     the initialization time window.
                 @param input_file_regex -  the regex describing the input file's format (full file path)
                 @param sorted_keywords  -  a list of keywords, in the order in which they appear in the
                                            filename_template description
                 @param tmpl             - the filename template for the A-deck or B-deck file, defined in the
                                           filename_templates section of the config file

            Returns:
                filtered_input    - a list of filtered input track files (full file path)
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ": Filtering track file input")

        # Eight possible combinations: date only, region only, cyclone only, (date, region, cyclone), (date, region),
        # (date, cyclone), (cyclone, region), (no date, no region, no cyclone)
        by_date = False
        by_region = False
        by_cyclone = False
        if 'date' in sorted_keywords:
            by_date = True
        if 'region' in sorted_keywords:
            by_region = True
        if 'cyclone' in sorted_keywords:
            by_cyclone = True
        if by_date and by_region and by_cyclone:
            filtered_by_date = self.filter_by_date(all_input_files, input_file_regex, init_list, tmpl, sorted_keywords)
            filtered_by_region = self.filter_by_region(filtered_by_date, input_file_regex, tmpl, sorted_keywords)
            filtered = self.filter_by_cyclone(filtered_by_region, input_file_regex, tmpl, sorted_keywords)
        elif by_date and by_region:
            filtered_by_date = self.filter_by_date(all_input_files, input_file_regex, init_list, tmpl, sorted_keywords)
            filtered = self.filter_by_region(filtered_by_date, input_file_regex, tmpl, sorted_keywords)
        elif by_date and by_cyclone:
            filtered_by_date = self.filter_by_date(all_input_files, input_file_regex, init_list, tmpl, sorted_keywords)
            filtered = self.filter_by_cyclone(filtered_by_date, input_file_regex, tmpl, sorted_keywords)
        elif by_region and by_cyclone and not by_date:
            filtered_by_region = self.filter_by_region(all_input_files, input_file_regex, init_list, tmpl,
                                                       sorted_keywords)
            filtered = self.filter_by_cyclone(filtered_by_region, input_file_regex, tmpl, sorted_keywords)
        elif by_date and not by_region and not by_cyclone:
            filtered = self.filter_by_date(all_input_files, input_file_regex, init_list, tmpl, sorted_keywords)
        elif not by_date and by_region and not by_cyclone:
            filtered = self.filter_by_region(all_input_files, input_file_regex, tmpl, sorted_keywords)
        elif not by_date and not by_region and by_cyclone:
            filtered = self.filter_by_cyclone(all_input_files, input_file_regex, tmpl, sorted_keywords)
        else:
            # Nothing to filter by, return the original input data
            return all_input_files
        return filtered

    def filter_by_date(self, input_data, file_regex, init_list, tmpl, sorted_keywords):
        """! Filter the input data by date

             Args:
                 @param input_data  - A list of all input data (full file path)
                 @param file_regex - The regex for the input file
                 @param init_list   - A list of all init times that define the initialization time window
                 @param tmpl        - The filename template for the A-deck or B-deck input, as specified in the
                                     filename_templates section of the config file.  Needed to assist in the
                                     extraction of dates from the directory or filename of the A-deck or B-deck input.
                 @param sorted_keywords - List of keywords, in the order in which they appear.
             Returns:
                 filtered_by_date - A list of all input data that lie within the initialization time window
                                   (full filepath)

        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ": Filtering track file input by date...")
        date_len = self.get_date_format_info(tmpl)
        regex_comp = re.compile(file_regex)
        group_number = sorted_keywords.index('date') + 1
        if date_len == 0:
            # No match to date?=fmt in filename_templates description, return the input file
            return input_data

        filtered_by_date = []
        for cur_init in init_list:
            # Match the init time granularity to the input data's granularity for ease in filtering by date.
            if date_len == 10:
                # %Y%m%d%h -> YYYYMMDDhh
                cur_year = cur_init[0:4]
                cur_month = cur_init[4:6]
                cur_day = cur_init[6:8]
                # Start at 9 instead of 8 because of '_' in init_list's YYYYMMDD_hh.
                cur_hour = cur_init[9:11]
                cur_init_date = int(cur_year + cur_month + cur_day + cur_hour)
            elif date_len == 8:
                # %Y%m%d -> YYYYMMDD
                cur_year = cur_init[0:4]
                cur_month = cur_init[4:6]
                cur_day = cur_init[6:8]
                cur_init_date = int(cur_year + cur_month + cur_day)
            elif date_len == 6:
                # %Y%m -> YYYYMM
                cur_year = cur_init[0:4]
                cur_month = cur_init[4:6]
                cur_init_date = int(cur_year + cur_month)
            elif date_len == 4:
                # %Y -> YYYY
                cur_init_date = int(cur_init[0:4])

            for cur_input in input_data:
                # Compare the current init time with that of the input data's time
                input_date_match = re.match(regex_comp, cur_input)
                if input_date_match:
                    input_date = int(input_date_match.group(group_number))
                    if input_date <= cur_init_date:
                        if cur_input not in filtered_by_date:
                            filtered_by_date.append(cur_input)

        return filtered_by_date

    def filter_by_region(self, input_data, input_file_regex, tmpl, sorted_keywords):
        """! Filter the input data by region

                    Args:
                        @param input_data  - A list of all input data (full file path)
                        @param input_file_regex - The regex of the filename/directory for track input data.
                        @param tmpl        - The filename template for the A-deck or B-deck input, as specified in the
                                            filename_templates section of the config file.  Needed to assist in the
                                            extraction of dates from the directory or filename of the A-deck or B-deck input.
                        @sorted_keywords - A list of keywords, in the order in which they appear.
                    Returns:
                        filtered_by_region - A list of all input data that correspond to the list of regions requested

               """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ": Filtering track file input by region...")
        # Get a list of the regions of interest
        regions_from_conf = util.getlist(self.tcp_dict['BASIN'])
        regions = []
        for region in regions_from_conf:
            regions.append(region.lower())
        group_number = sorted_keywords.index('region') + 1
        filtered = []
        if regions:
            # Extract the region based on the filename template
            for cur_data in input_data:
                regex_comp = re.compile(input_file_regex)
                match = re.match(regex_comp, cur_data)
                if match:
                    data_match = match.group(group_number).lower()
                    if data_match in regions:
                        filtered.append(cur_data)
        else:
            return input_data

        return filtered

    def filter_by_cyclone(self, input_data, input_file_regex, tmpl, sorted_keywords):
        """! Filter the input data by cyclone

                    Args:
                        @param input_data  - A list of all input data (full file path)
                        @param input_file_regex - The regex of the filename/directory for track input data.
                        @param tmpl        - The filename template for the A-deck or B-deck input, as specified in the
                                            filename_templates section of the config file.  Needed to assist in the
                                            extraction of dates from the directory or filename of the A-deck or B-deck input.
                        @sorted_keywords - A list of keywords, in the order in which they appear.
                    Returns:
                        filtered_by_cyclone - A list of all input data that correspond to the list of regions requested

               """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ": Filtering track file input by cyclone...")

        # Get a list of the cyclones of interest
        cyclones = util.getlist(self.tcp_dict['CYCLONE'])
        group_number = sorted_keywords.index('cyclone') + 1
        filtered = []
        if cyclones:
            # Extract the cyclone based on the filename template
            for cur_data in input_data:
                regex_comp = re.compile(input_file_regex)
                match = re.match(regex_comp, cur_data)
                if match:
                    data_match = match.group(group_number).lower()
                    if data_match in cyclones:
                        filtered.append(cur_data)
        else:
            return input_data

        return filtered

    def get_input_track_files(self, input_dir):
        """! Get all the input track files in the A-deck or B-deck input directory.
             Args:
                 input_dir  - the directory of the A-deck or B-deck input
             Returns:
                 all_track_files - a list of all the input track files (full filepath)
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ": Creating a list of input A-deck or B-deck track files")

        # Retrieve full file path for every file in the input directory
        all_track_files = []
        for dirs, _, files in os.walk(input_dir):
            for f in files:
                all_track_files.append(os.path.join(dirs, f))

        return all_track_files

    def set_env_vars(self):
        """! Set up all the environment variables that are assigned in the MET+ config file which are
            to be used by the MET TC-pairs config file.

             Args:
                 nothing - retrieves necessary MET+ config values via class attributes

             Returns:
                 nothing - sets the environment variables
        """
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        self.logger.debug(
            cur_function + '|' + cur_filename + ': Setting environment variables that will be used by '
                                                'MET...')

        # For all cases below, we need to do some pre-processing so that
        #  Python will use " and not ' because currently MET doesn't
        # support single-quotes.

        # INIT_BEG, INIT_END
        tmp_init_beg = self.tcp_dict['INIT_BEG']
        tmp_init_end = self.tcp_dict['INIT_END']

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

        # INIT_INC and INIT_EXC
        # Used to set init_inc in "TC_PAIRS_CONFIG_FILE"
        tmp_init_inc = util.getlist(
            self.tcp_dict['INIT_INCLUDE'])
        tmp_init_exc = util.getlist(
            self.tcp_dict['INIT_EXCLUDE'])
        if not tmp_init_inc:
            # self.add_env_var('PB2NC_STATION_ID', "[]")
            self.add_env_var(b'INIT_INCLUDE', "[]")
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file after removing whitespace
            # and replacing ' with ".
            init_inc = str(tmp_init_inc).replace("\'", "\"")
            init_inc_str = ''.join(init_inc.split())
            self.add_env_var(b'INIT_INCLUDE', str(init_inc_str))

        if not tmp_init_exc:
            # self.add_env_var('PB2NC_STATION_ID', "[]")
            self.add_env_var(b'INIT_EXCLUDE', "[]")
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file after removing whitespace
            # and replacing ' with ".
            init_exc = str(tmp_init_exc).replace("\'", "\"")
            init_exc_str = ''.join(init_exc.split())
            self.add_env_var(b'INIT_EXCLUDE', str(init_exc_str))

        # MODEL
        tmp_model = self.tcp_dict['MODEL']
        if not tmp_model:
            # Empty, MET is expecting [] to indicate all models are to be included
            self.add_env_var(b'MODEL', "[]")
        else:
            # Replace ' with " and remove whitespace
            model = str(tmp_model).replace("\'", "\"")
            model_str = ''.join(model.split())
            self.add_env_var(b'MODEL', str(model_str))

        # STORM_ID
        tmp_storm_id = self.tcp_dict['STORM_ID']
        if not tmp_storm_id:
            # Empty, use all storm_ids, indicate this to MET via '[]'
            self.add_env_var(b'STORM_ID', "[]")
        else:
            # Replace ' with " and remove whitespace
            storm_id = str(tmp_storm_id).replace("\'", "\"")
            storm_id_str = ''.join(storm_id.split())
            self.add_env_var(b'STORM_ID', str(storm_id_str))

        # BASIN
        tmp_basin = self.tcp_dict['BASIN']
        if tmp_basin:
            # Empty, we want all basins.  Send MET '[]' to indicate that
            # we want all the basins.
            self.add_env_var(b'BASIN', "[]")
        else:
            # Replace any ' with " and remove whitespace.
            basin = str(tmp_basin).replace("\'", "\"")
            basin_str = ''.join(basin.split())
            self.add_env_var(b'BASIN', str(basin_str))

        # CYCLONE
        tmp_cyclone = self.tcp_dict['CYCLONE']
        if not tmp_cyclone:
            # Empty, use all cyclones, send '[]' to MET.
            self.add_env_var(b'CYCLONE', "[]")
        else:
            # Replace ' with " and get rid of any whitespace
            cyclone = str(tmp_cyclone).replace("\'", "\"")
            cyclone_str = ''.join(cyclone.split())
            self.add_env_var(b'CYCLONE', str(cyclone_str))

        # STORM_NAME
        tmp_storm_name =  self.tcp_dict['STORM_NAME']
        if not tmp_storm_name:
            # Empty, equivalent to 'STORM_NAME = "[]"; in MET config file,
            # use all storm names.
            self.add_env_var(b'STORM_NAME', "[]")
        else:
            storm_name = str(tmp_storm_name).replace("\'", "\"")
            storm_name_str = ''.join(storm_name.split())
            self.add_env_var(b'STORM_NAME', str(storm_name_str))

        # Valid time window variables
        valid_beg = self.config.getstr('config', 'VALID_BEG')
        self.add_env_var(b'VALID_BEG', str(valid_beg))

        valid_end = self.config.getstr('config', 'VALID_END')
        self.add_env_var(b'VALID_END', str(valid_end))

        # DLAND_FILE
        tmp_dland_file = self.tcp_dict['DLAND_FILE']
        self.add_env_var(b'DLAND_FILE', str(tmp_dland_file))

    def setup_tropical_track_dirs(self, deck_input_file_path, deck_file_path,
                                  storm_month, missing_values):
        """! Set up the adeck or bdeck file paths.  If these
             correspond to a tropical storm, then perform additional
             processing via read_modify_write_file to conform to
             ATCF_by_pairs format.

             Args:
                   @param deck_input_file_path: the adeck or bdeck input
                                               filepath
                   @param deck_file_path:  the adeck or bdeck filepath to be
                                          created
                   @param storm_month:  Month of the storm
                   @param missing_values: The value specified in the config
                                          file to indicate missing values/
                                          missing data in the data file.
                                          Typical values are -9999.
        """

        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Check to see if the output file exists already.  If it
        # does exist either check a force overwrite option
        # (add) or log a message telling the user to delete the
        # existing data if they want a fresh run
        # Read in the adeck/bdeck file, modify it, and
        # write a new adeck/bdeck file
        # Check for existence of data and overwrite if desired
        if os.path.exists(deck_file_path):
            if self.config.getbool('config', 'TRACK_DATA_MOD_FORCE_OVERWRITE'):
                self.logger.debug("DEBUG | [" + cur_filename +
                                  ":" + cur_function + "] | " +
                                  "Writing modified csv file: "
                                  + deck_file_path +
                                  ", replacing " +
                                  "existing data because " +
                                  "TRACK_DATA_MOD_FORCE_" +
                                  "OVERWRITE is set to True")
                self.read_modify_write_file(deck_input_file_path,
                                            storm_month,
                                            missing_values,
                                            deck_file_path)
            else:
                self.logger.debug("DEBUG | [" + cur_filename +
                                  ":" + cur_function + "] | " +
                                  "Using existing modified csv"
                                  "file: " + deck_file_path +
                                  ", because " +
                                  "track_data_mod_force_" +
                                  "overwrite is set to False")
        else:
            self.logger.debug("DEBUG | [" + cur_filename + ":"
                              + cur_function + "] | " +
                              "Writing modified csv file: " +
                              deck_file_path)
            self.read_modify_write_file(deck_input_file_path,
                                        storm_month,
                                        missing_values,
                                        deck_file_path)

    def build_non_atcf_tc_pairs(self, pairs_output_dir, adeck_file_path,
                                bdeck_file_path, date_file):
        """! Build up the command that is used to run the MET tool,
             tc_pairs.
             Args:
                 @param pairs_output_dir: output directory of paired track data
                 @param adeck_file_path: the location of the adeck track data, as file or top-level directory
                 @param bdeck_file_path: the location of the bdeck track data, as file or top-level directory
                 @param date_file: the current date file from a list of all
                                   possible date files in the input directory, used
                                   to over ride the default output name created by MET tc_pairs.
                                   Default is None-allow MET to name the output file.
            Returns:
                 a list of commands

        """

        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        pairs_out_file = os.path.join(pairs_output_dir, date_file)
        pairs_out_file_with_suffix = pairs_out_file + ".tcst"
        if os.path.exists(pairs_out_file_with_suffix):
            if self.config.getbool('config', 'TC_PAIRS_FORCE_OVERWRITE'):
                self.logger.debug("DEBUG | [" + cur_filename +
                                  ":" + cur_function + "] | " +
                                  "Writing tc_pairs output file: "
                                  + pairs_out_file + ", replacing"
                                  + " existing " +
                                  " data because TC_PAIRS_FORCE" +
                                  "_OVERWRITE is set to True")

        tc_pairs_exe = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                    'bin/tc_pairs')
        cmd_list = [tc_pairs_exe, " -adeck ",
                    adeck_file_path, " -bdeck ",
                    bdeck_file_path, " -config ",
                    self.config.getstr('config', 'TC_PAIRS_CONFIG_FILE'),
                    " -out ", pairs_out_file]
        cmd = ''.join(cmd_list)
        self.logger.debug("DEBUG | [" + cur_filename + ":" +
                          cur_function + "] | " +
                          "Running tc_pairs with command: " +
                          cmd)

        return cmd

    def get_command(self):
        """! Over-ride CommandBuilder's get_command because unlike other MET tools,
             tc_pairs handles input files differently- namely, through flags -adeck and -bdeck and doesn't
             require an output file, as there is a default.
        Build command to run from arguments"""
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        return self.cmd

    def build(self):
        """! Override CommandBuilder's build() since tc_pairs handles input and output differently from the other
             MET tools"""
        # Since this wrapper is not using the CommandBuilder to build the cmd,
        # we need to add the met verbosity level to the cmd created before we
        # run the command.
        self.cmd = self.cmdrunner.insert_metverbosity_opt(self.cmd)

        try:
            (ret, self.cmd) = self.cmdrunner.run_cmd(self.cmd, sleeptime=.00001,
                                                     app_name=self.app_name)

            if not ret == 0:
                raise ExitStatusException(
                    '%s: non-zero exit status' % (repr(self.cmd),), ret)

        except ExitStatusException as ese:
            self.logger.error(ese)
            exit(ret)


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='run_tc_pairs',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_pairs')
        produtil.log.postmsg('run_tc_pairs is starting')

        CONFIG_INST = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')
        TCP = TcPairsWrapper(CONFIG_INST, logger=None)
        TCP.run_all_times()
        produtil.log.postmsg('run_tc_pairs completed')
    except Exception as exc:
        produtil.log.jlogger.critical(
            'run_tc_pairs failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)
