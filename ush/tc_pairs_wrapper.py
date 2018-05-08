#!/usr/bin/env python

"""
Program Name: tc_pairs_wrapper.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Invokes the MET tool tc_pairs to parse ADeck and BDeck ATCF files,
          filter the data, and match them up
History Log:  Initial version
Usage:
Parameters: None
Input Files: adeck and bdeck files
Output Files: tc_pairs files
Condition codes: 0 for success, 1 for failure

"""

from __future__ import (print_function, division)

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

'''!@namespace TcPairsWrapper
@brief Wraps the MET tool tc_pairs to parse ADeck and BDeck ATCF files,
filter the data, and match them up.
Call as follows:
@code{.sh}
tc_pairs_wrapper.py [-c /path/to/user.template.conf]
@endcode
'''


class TcPairsWrapper(CommandBuilder):
    """!Wraps the MET tool, tc_pairs to parse and match ATCF adeck and
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

        # Differentiate between non-ATCF data and ATCF track data based on
        # the TRACK_TYPE
        if self.config.getstr('config',
                              'TRACK_TYPE') == "extra_tropical_cyclone":
            self.process_non_ATCF()

        else:
            self.process_ATCF()

        self.logger.info("Completed run_all_times in TcPairsWrapper")

    def process_non_ATCF(self):
        """! Original implementation of this wrapper- for
             extra-tropical-cyclone data in non-ATCF format
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
                          '| building command for non-ATCF track data...')

        missing_values = \
            (self.config.getstr('config', 'MISSING_VAL_TO_REPLACE'),
             self.config.getstr('config', 'MISSING_VAL'))

        # Get the desired YYYYMMDD_HH init increment list
        # convert the increment INIT_INC from seconds to hours
        init_list = util.gen_init_list(
            self.config.getstr('config', 'INIT_BEG'),
            self.config.getstr('config', 'INIT_END'),
            int(self.config.getint('config', 'INIT_INCREMENT') / 3600),
            self.config.getstr('config', 'INIT_HOUR_END'))

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
        atrack_dir = self.config.getdir('ADECK_TRACK_DATA_DIR')
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
                self.config.getdir('TRACK_DATA_SUBDIR_MOD'),
                os.path.basename(cur_dir))
            bdeck_mod = os.path.join(
                self.config.getdir('TRACK_DATA_SUBDIR_MOD'),
                os.path.basename(cur_dir))
            produtil.fileop.makedirs(adeck_mod, logger=self.logger)

            # Iterate over the files, modifying them and writing new output
            # files if necessary ("extra_tropical_cyclone" track type), and
            # run tc_pairs
            for cur_track_file in track_files_for_date:
                # Check to see if the files have the ADeck prefix
                if cur_track_file.startswith(
                        self.config.getstr('config', 'ADECK_FILE_PREFIX')):
                    # Create the output directory for the pairs, if
                    # it doesn't already exist
                    pairs_out_dir = \
                        os.path.join(self.config.getdir('TC_PAIRS_DIR'),
                                     os.path.basename(cur_dir))
                    produtil.fileop.makedirs(pairs_out_dir, logger=self.logger)

                    # Perform the extra processing for non-ATCF formatted
                    # extra_tropical_cyclone data.
                    # Form the adeck and bdeck input filename paths
                    adeck_in_file_path = os.path.join(cur_dir,
                                                      cur_track_file)
                    bdeck_in_file_path = re.sub(
                        self.config.getstr('config', 'ADECK_FILE_PREFIX'),
                        self.config.getstr('config', 'BDECK_FILE_PREFIX'),
                        adeck_in_file_path)
                    adeck_file_path = os.path.join(adeck_mod,
                                                   cur_track_file)
                    bdeck_file_path = os.path.join(bdeck_mod, re.sub(
                        self.config.getstr('config', 'ADECK_FILE_PREFIX'),
                        self.config.getstr('config', 'BDECK_FILE_PREFIX'),
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
                    self.cmd = self.build_tc_pairs(pairs_out_dir,
                                                   cur_track_file,
                                                   adeck_file_path,
                                                   bdeck_file_path)
                    self.build()

    def process_ATCF(self):
        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        self.logger.debug(
            cur_filename + '|' + cur_function +
            '| Processing ATCF track files...')

        # Get the filename templates
        adeck_input_dir = self.config.getstr('dir', 'ADECK_TRACK_DATA_DIR')
        bdeck_input_dir = self.config.getstr('dir', 'BDECK_TRACK_DATA_DIR')
        fcst_filename_tmpl = self.config.getraw('filename_templates',
                                                'FCST_TMPL')
        reference_filename_tmpl = self.config.getraw('filename_templates',
                                                     'REFERENCE_TMPL')

        # Filter down track data based on init time window.
        # Get the init time window from the INIT_BEG, INIT_END, INIT_HOUR_END,
        # and INIT_INCREMENT in the config file as a list of init times.
        # Convert the increment INIT_INCREMENT from seconds to hours
        init_list = util.gen_init_list(
            self.config.getstr('config', 'INIT_BEG'),
            self.config.getstr('config', 'INIT_END'),
            int(self.config.getint('config', 'INIT_INCREMENT') / 3600),
            self.config.getstr('config', 'INIT_HOUR_END'))

        # Set up the adeck and bdeck file paths

        # Run tc_pairs
        # self.cmd = self.build_tc_pairs(pairs_out_dir, cur_track_file,
        #                                adeck_file_path, bdeck_file_path)
        # self.build()

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

        # INIT_INC and INIT_EXC
        # Used to set init_inc in "TC_PAIRS_CONFIG_FILE"
        tmp_init_inc = util.getlist(
            self.config.getstr('config', 'INIT_INCLUDE'))
        tmp_init_exc = util.getlist(
            self.config.getstr('config', 'INIT_EXCLUDE'))
        if not tmp_init_inc:
            # self.add_env_var('PB2NC_STATION_ID', "[]")
            os.environ['INIT_INCLUDE'] = "[]"
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file after removing whitespace
            # and replacing ' with ".
            init_inc = str(tmp_init_inc).replace("\'", "\"")
            init_inc_str = ''.join(init_inc.split())
            os.environ['INIT_INCLUDE'] = str(init_inc_str)

        if not tmp_init_exc:
            # self.add_env_var('PB2NC_STATION_ID', "[]")
            os.environ['INIT_EXCLUDE'] = "[]"
        else:
            # Not empty, set the environment variable to the
            # value specified in the MET+ config file after removing whitespace
            # and replacing ' with ".
            init_exc = str(tmp_init_exc).replace("\'", "\"")
            init_exc_str = ''.join(init_exc.split())
            os.environ['INIT_EXCLUDE'] = str(init_exc_str)

        # MODEL
        tmp_model = util.getlist(self.config.getstr('config', 'MODEL'))
        if not tmp_model:
            # Empty, MET is expecting [] to indicate all models are to be included
            os.environ['MODEL'] = "[]"
        else:
            # Replace ' with " and remove whitespace
            model = str(tmp_model).replace("\'", "\"")
            model_str = ''.join(model.split())
            os.environ['MODEL'] = str(model_str)

        # STORM_ID
        tmp_storm_id = util.getlist(self.config.getstr('config', 'STORM_ID'))
        if not tmp_storm_id:
            # Empty, use all storm_ids, indicate this to MET via '[]'
            os.environ['STORM_ID'] = "[]"
        else:
            # Replace ' with " and remove whitespace
            storm_id = str(tmp_storm_id).replace("\'", "\"")
            storm_id_str = ''.join(storm_id.split())
            os.environ['STORM_ID'] = str(storm_id_str)

        # BASIN
        tmp_basin = util.getlist(self.config.getstr('config', 'BASIN'))
        if tmp_basin:
            # Empty, we want all basins.  Send MET '[]' to indicate that
            # we want all the basins.
            os.environ['BASIN'] = "[]"
        else:
            # Replace any ' with " and remove whitespace.
            basin = str(tmp_basin).replace("\'", "\"")
            basin_str = ''.join(basin.split())
            os.environ['BASIN'] = str(basin_str)

        # CYCLONE
        tmp_cyclone = util.getlist(self.config.getstr('config', 'CYCLONE'))
        if not tmp_cyclone:
            # Empty, use all cyclones, send '[]' to MET.
            os.environ['CYCLONE'] = "[]"
        else:
            # Replace ' with " and get rid of any whitespace
            cyclone = str(tmp_cyclone).replace("\'", "\"")
            cyclone_str = ''.join(cyclone.split())
            os.environ['CYCLONE'] = str(cyclone_str)

        # STORM_NAME
        tmp_storm_name = util.getlist(
            self.config.getstr('config', 'STORM_NAME'))
        if not tmp_storm_name:
            # Empty, equivalent to 'STORM_NAME = "[]"; in MET config file,
            # use all storm names.
            os.environ['STORM_NAME'] = "[]"
        else:
            storm_name = str(tmp_storm_name).replace("\'", "\"")
            storm_name_str = ''.join(storm_name.split())
            os.environ['STORM_NAME'] = str(storm_name_str)

        # Valid time window variables
        valid_beg = self.config.getstr('config', 'VALID_BEG')
        os.environ['VALID_BEG'] = str(valid_beg)

        valid_end = self.config.getstr('config', 'VALID_END')
        os.environ['VALID_END'] = str(valid_end)

        # DLAND_FILE
        tmp_dland_file = self.config.getstr('config', 'DLAND_FILE')
        os.environ['DLAND_FILE'] = tmp_dland_file

    def setup_tropical_track_dirs(self, deck_input_file_path, deck_file_path,
                                  storm_month, missing_values):
        """! Set up the adeck or bdeck file paths.  If these
             correspond to a tropical storm, then perform additional
             processing via read_modify_write_file to conform to
             ATCF format.

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

    def build_tc_pairs(self, pairs_output_dir, date_file, adeck_file_path,
                       bdeck_file_path):
        """! Build up the command that is used to run the MET tool,
             tc_pairs.
             Args:
                 @param pairs_output_dir: output directory of paired track data
                 @param date_file: the current date file from a list of all
                                   possible date files in the input directory.
                 @param adeck_file_path: the location of the adeck track output
                 @param bdeck_file_path: the location of the bdeck track output
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
        tc_pairs_exe = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
                                    'bin/tc_pairs')
        cmd_list = [tc_pairs_exe, " -adeck ",
                    adeck_file_path, " -bdeck ",
                    bdeck_file_path, " -config ",
                    self.config.getstr('config', 'TC_PAIRS_CONFIG_FILE'),
                    " -out ", pairs_out_file]
        cmd = ''.join(cmd_list)
        # self.logger.debug("cmd = " + cmd)
        if os.path.exists(pairs_out_file_with_suffix):
            if self.config.getbool('config', 'TC_PAIRS_FORCE_OVERWRITE'):
                self.logger.debug("DEBUG | [" + cur_filename +
                                  ":" + cur_function + "] | " +
                                  "Writing tc_pairs output file: "
                                  + pairs_out_file + ", replacing"
                                  + " existing " +
                                  " data because TC_PAIRS_FORCE" +
                                  "_OVERWRITE is set to True")
        else:
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
