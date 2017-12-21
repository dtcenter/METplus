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
from produtil.run import batchexe
from produtil.run import run
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
        self.config = self.p
        if self.logger is None:
            self.logger = util.get_logger(self.p)

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

        missing_values = \
            (self.config.getstr('config', 'MISSING_VAL_TO_REPLACE'),
             self.config.getstr('config', 'MISSING_VAL'))

        # Get the desired YYYYMMDD_HH init increment list
        # convert the increment INIT_INC from seconds to hours
        init_list = util.gen_init_list(
            self.config.getstr('config', 'INIT_BEG'),
            self.config.getstr('config', 'INIT_END'),
            int(self.config.getint('config', 'INIT_INC')/3600),
            self.config.getstr('config', 'INIT_HOUR_END'))

        # get a list of YYYYMM values
        year_month_list = []
        for init in init_list:
            if init[0:6] not in year_month_list:
                year_month_list.append(init[0:6])

        # Set up the environment variable to be used in the TCPairs Config
        # file (TC_PAIRS_CONFIG_FILE)
        # Used to set init_inc in "TC_PAIRS_CONFIG_FILE"
        # Need to do some pre-processing so that Python will use " and not '
        # because currently MET
        # doesn't support single-quotes
        tmp_init_string = str(init_list)
        tmp_init_string = tmp_init_string.replace("\'", "\"")
        os.environ['INIT_INC'] = tmp_init_string

        # Get a directory path listing of the dated subdirectories
        # (YYYYMM format) in the track_data directory
        dir_list = []
        # Get a list of all the year_month directories in the
        # track data directory specified in the config file.
        for year_month in os.listdir(self.config.getdir('TRACK_DATA_DIR')):
            # if the full directory path isn't an empty directory,
            # check if the current year_month is the requested time.
            if os.path.isdir(os.path.join(self.config.getdir('TRACK_DATA_DIR'),
                                          year_month)) \
                    and year_month in year_month_list:
                dir_list.append(
                    os.path.join(self.config.getdir('TRACK_DATA_DIR'),
                                 year_month))

        if not dir_list:
            self.logger.warning("ERROR | [" + cur_filename + ":" +
                                cur_function + "] | There are no dated"
                                               "sub-directories (YYYYMM) " +
                                "with input data as expected in: " +
                                self.config.getdir('TRACK_DATA_DIR'))
            exit(0)

        # Get a list of files in the dated subdirectories
        for mydir in dir_list:
            myfiles = os.listdir(mydir)
            # Need to do extra processing if track_type is extra_tropical
            # cyclone
            if self.config.getstr('config',
                                  'TRACK_TYPE') == "extra_tropical_cyclone":
                # Create an atcf output directory for writing the modified
                # files
                adeck_mod = os.path.join(
                    self.config.getdir('TRACK_DATA_SUBDIR_MOD'),
                    os.path.basename(mydir))
                bdeck_mod = os.path.join(
                    self.config.getdir('TRACK_DATA_SUBDIR_MOD'),
                    os.path.basename(mydir))
                produtil.fileop.makedirs(adeck_mod, logger=self.logger)

            # Iterate over the files, modifying them and writing new output
            # files if necessary ("extra_tropical_cyclone" track type), and
            # run tc_pairs
            for myfile in myfiles:
                # Check to see if the files have the ADeck prefix
                if myfile.startswith(
                        self.config.getstr('config', 'ADECK_FILE_PREFIX')):
                    # Create the output directory for the pairs, if
                    # it doesn't already exist
                    pairs_out_dir = \
                        os.path.join(self.config.getdir('TC_PAIRS_DIR'),
                                     os.path.basename(mydir))
                    produtil.fileop.makedirs(pairs_out_dir, logger=self.logger)

                    # Need to do extra processing if track_type is
                    # extra_tropical_cyclone
                    if self.config.getstr('config',
                                          'TRACK_TYPE') == \
                            "extra_tropical_cyclone":

                        # Form the adeck and bdeck input filename paths
                        adeck_in_file_path = os.path.join(mydir, myfile)
                        bdeck_in_file_path = re.sub(
                            self.config.getstr('config', 'ADECK_FILE_PREFIX'),
                            self.config.getstr('config', 'BDECK_FILE_PREFIX'),
                            adeck_in_file_path)
                        adeck_file_path = os.path.join(adeck_mod, myfile)
                        bdeck_file_path = os.path.join(bdeck_mod, re.sub(
                            self.config.getstr('config', 'ADECK_FILE_PREFIX'),
                            self.config.getstr('config', 'BDECK_FILE_PREFIX'),
                            myfile))

                        # Get the storm number e.g. 0004 in
                        # amlq2012033118.gfso.0004
                        # split_basename = myfile.split(".")

                        # Get the YYYYMM e.g 201203 in amlq2012033118.gfso.0004
                        year_month = myfile[4:10]

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
                    else:
                        # Set up the adeck and bdeck file paths
                        adeck_file_path = os.path.join(mydir, myfile)
                        bdeck_file_path = re.sub(
                            self.config.getstr('config', 'ADECK_FILE_PREFIX'),
                            self.config.getstr('config', 'BDECK_FILE_PREFIX'),
                            adeck_file_path)

                    # Run tc_pairs
                    cmd = self.build_tc_pairs(pairs_out_dir, myfile,
                                              adeck_file_path, bdeck_file_path)
                    cmd = batchexe('sh')['-c', cmd].err2out()
                    ret = run(cmd, sleeptime=.00001)
                    if ret != 0:
                        self.logger.error("ERROR | [" + cur_filename +
                                          ":" + cur_function + "] | " +
                                          "Problem executing: " +
                                          cmd.to_shell())
                        exit(0)

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
