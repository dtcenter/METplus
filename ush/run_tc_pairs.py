#!/usr/bin/env python

"""
Program Name: run_tc_pairs.py
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
import met_util as util
import config_metplus

'''!@namespace TcPairs
@brief Runs tc_pairs to parse ADeck and BDeck ATCF files,
filter the data, and match them up.

Call as follows:
@code{.sh}
run_tc_pairs.py [-c /path/to/user.template.conf]
@endcode
'''


class TcPairs(object):
    def __init__(self, config):
        self.logger = util.get_logger(config)
        # Retrieve any necessary values, from the configuration file object p.
        self.init_list = util.gen_init_list(
            config.getstr('config', 'INIT_DATE_BEG'),
            config.getstr('config', 'INIT_DATE_END'),
            config.getint('config', 'INIT_HOUR_INC'),
            config.getstr('config', 'INIT_HOUR_END'))
        self.track_data_dir = config.getdir('TRACK_DATA_DIR')
        self.track_type = config.getstr('config', 'TRACK_TYPE')
        self.track_data_subdir_mod = config.getdir('TRACK_DATA_SUBDIR_MOD')
        self.adeck_file_prefix = config.getstr('config', 'ADECK_FILE_PREFIX')
        self.bdeck_file_prefix = config.getstr('config', 'BDECK_FILE_PREFIX')
        self.track_data_mod_force_overwrite = \
            config.getbool('config', 'TRACK_DATA_MOD_FORCE_OVERWRITE')
        self.tc_pairs_dir = config.getdir('TC_PAIRS_DIR')
        self.tc_pairs_force_overwrite = \
            config.getbool('config', 'TC_PAIRS_FORCE_OVERWRITE')
        self.tc_pairs_exe = config.getexe('TC_PAIRS')
        self.tc_pairs_config_path = config.getstr('config',
                                                  'TC_PAIRS_CONFIG_PATH')
        self.missing_val_to_replace = config.getstr('config',
                                                    'MISSING_VAL_TO_REPLACE')
        self.missing_val = config.getstr('config', 'MISSING_VAL')

    def read_modify_write_file(self, in_csvfile, storm_month, missing_values,
                               out_csvfile, logger):
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
        # cur_filename = sys._getframe().f_code.co_filename
        # cur_function = sys._getframe().f_code.co_name

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
        logger.debug("DEBUG|run_tc_pairs.py|read_modify_write_file complete")

    def main(self):
        """!Main program.

        This is the main program"""

        # pylint:disable=protected-access
        # sys._getframe is a legitimate way to access the current
        # filename and method.
        # Used for logging information
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        missing_values = (self.missing_val_to_replace, self.missing_val)

        # Get the desired YYYYMM from the init list
        YYYYMM_list = []
        for init in self.init_list:
            if init[0:6] not in YYYYMM_list:
                YYYYMM_list.append(init[0:6])

        # Set up the environment variable to be used in the TCPairs Config
        # file (TC_PAIRS_CONFIG_PATH)
        # Used to set init_inc in "TC_PAIRS_CONFIG_PATH"
        # Need to do some pre-processing so that Python will use " and not '
        # because currently MET
        # doesn't support single-quotes
        tmp_init_string = str(self.init_list)
        tmp_init_string = tmp_init_string.replace("\'", "\"")
        os.environ['INIT_INC'] = tmp_init_string

        # Get a directory path listing of the dated subdirectories
        # (YYYYMM format) in the track_data directory
        dir_list = []
        for YYYYMM in os.listdir(self.track_data_dir):
            if os.path.isdir(os.path.join(self.track_data_dir, YYYYMM)):
                if YYYYMM in YYYYMM_list:
                    dir_list.append(os.path.join(self.track_data_dir, YYYYMM))

        if not dir_list:
            self.logger.warning("ERROR | [" + cur_filename + ":" +
                                cur_function + "] | There are no dated"
                                "sub-directories (YYYYMM) " +
                                "with input data as expected in: " +
                                self.track_data_dir)
            exit(0)

        # Get a list of files in the dated subdirectories
        for mydir in dir_list:
            myfiles = os.listdir(mydir)
            # Need to do extra processing if track_type is extra_tropical
            # cyclone
            if self.track_type == "extra_tropical_cyclone":
                # Create an atcf output directory for writing the modified
                # files
                adeck_mod = os.path.join(self.track_data_subdir_mod,
                                         os.path.basename(mydir))
                bdeck_mod = os.path.join(self.track_data_subdir_mod,
                                         os.path.basename(mydir))
                produtil.fileop.makedirs(adeck_mod, logger=self.logger)

            # Iterate over the files, modifying them and writing new output
            # files if necessary ("extra_tropical_cyclone" track type), and
            # run tc_pairs
            for myfile in myfiles:
                # Check to see if the files have the ADeck prefix
                if myfile.startswith(self.adeck_file_prefix):
                    # Create the output directory for the pairs, if
                    # it doesn't already exist
                    pairs_out_dir = os.path.join(self.tc_pairs_dir,
                                                 os.path.basename(mydir))
                    produtil.fileop.makedirs(pairs_out_dir, logger=self.logger)

                    # Need to do extra processing if track_type is
                    # extra_tropical_cyclone
                    if self.track_type == "extra_tropical_cyclone":

                        # Form the adeck and bdeck input filename paths
                        adeck_in_file_path = os.path.join(mydir, myfile)
                        bdeck_in_file_path = re.sub(self.adeck_file_prefix,
                                                    self.bdeck_file_prefix,
                                                    adeck_in_file_path)
                        adeck_file_path = os.path.join(adeck_mod, myfile)
                        bdeck_file_path = \
                            os.path.join(bdeck_mod,
                                         re.sub(
                                             self.adeck_file_prefix,
                                             self.bdeck_file_prefix,
                                             myfile))

                        # Get the storm number e.g. 0004 in
                        # amlq2012033118.gfso.0004
                        # split_basename = myfile.split(".")

                        # Get the YYYYMM e.g 201203 in amlq2012033118.gfso.0004
                        YYYYMM = myfile[4:10]

                        # Get the MM from the YYYYMM
                        storm_month = YYYYMM[-2:]

                        # HERE
                        # Before calling this function (twice below) check to
                        # see if the output file exists already.  If it
                        # does exist either check a force overwrite option
                        # (add) or log a message telling the user to delete the
                        # existing data if they want a fresh run
                        # Read in the adeck file, modify it, and
                        # write a new adeck file
                        # Check for existence of data and overwrite if desired
                        if os.path.exists(adeck_file_path):
                            if self.track_data_mod_force_overwrite:
                                self.logger.debug("DEBUG | [" + cur_filename +
                                                  ":" + cur_function + "] | " +
                                                  "Writing modified csv file: "
                                                  + adeck_file_path +
                                                  ", replacing " +
                                                  "existing data because " +
                                                  "TRACK_DATA_MOD_FORCE_" +
                                                  "OVERWRITE is set to True")
                                self.read_modify_write_file(adeck_in_file_path,
                                                            storm_month,
                                                            missing_values,
                                                            adeck_file_path,
                                                            self.logger)
                            else:
                                self.logger.debug("DEBUG | [" + cur_filename +
                                                  ":" + cur_function + "] | " +
                                                  "Using existing modified csv"
                                                  "file: " + adeck_file_path +
                                                  ", because " +
                                                  "track_data_mod_force_" +
                                                  "overwrite is set to False")
                        else:
                            self.logger.debug("DEBUG | [" + cur_filename + ":"
                                              + cur_function + "] | " +
                                              "Writing modified csv file: " +
                                              adeck_file_path)
                            self.read_modify_write_file(adeck_in_file_path,
                                                        storm_month,
                                                        missing_values,
                                                        adeck_file_path,
                                                        self.logger)

                        # Read in the bdeck file, modify it,
                        # and write a new bdeck file
                        # Check for existence of data and overwrite if desired
                        if os.path.exists(bdeck_file_path):
                            if self.track_data_mod_force_overwrite:
                                self.logger.debug("DEBUG | [" + cur_filename +
                                                  ":" + cur_function + "] | " +
                                                  "Writing modified csv file: "
                                                  + bdeck_file_path +
                                                  ", replacing existing data "
                                                  + "because TRACK_DATA_MOD_"
                                                  + "FORCE_OVERWRITE is set "
                                                  + "to True")
                                self.read_modify_write_file(bdeck_in_file_path,
                                                            storm_month,
                                                            missing_values,
                                                            bdeck_file_path,
                                                            self.logger)
                            else:
                                self.logger.debug("DEBUG | [" + cur_filename +
                                                  ":" + cur_function + "] | " +
                                                  "Using existing modified csv"
                                                  " file: " + bdeck_file_path +
                                                  ", because " +
                                                  "TRACK_DATA_MOD_FORCE"
                                                  "_OVERWRITE is set to False")
                        else:
                            self.logger.debug("DEBUG | [" + cur_filename +
                                              ":" + cur_function + "] | " +
                                              "Writing modified csv file: " +
                                              bdeck_file_path)
                            self.read_modify_write_file(bdeck_in_file_path,
                                                        storm_month,
                                                        missing_values,
                                                        bdeck_file_path,
                                                        self.logger)

                    else:

                        # Set up the adeck and bdeck file paths
                        adeck_file_path = os.path.join(mydir, myfile)
                        bdeck_file_path = re.sub(self.adeck_file_prefix,
                                                 self.bdeck_file_prefix,
                                                 adeck_file_path)

                    # Run tc_pairs
                    pairs_out_file = os.path.join(pairs_out_dir, myfile)
                    pairs_out_file_with_suffix = pairs_out_file + ".tcst"
                    if os.path.exists(pairs_out_file_with_suffix):
                        if self.tc_pairs_force_overwrite:
                            self.logger.debug("DEBUG | [" + cur_filename +
                                              ":" + cur_function + "] | " +
                                              "Writing tc_pairs output file: "
                                              + pairs_out_file + ", replacing"
                                              + " existing " +
                                              " data because TC_PAIRS_FORCE" +
                                              "_OVERWRITE is set to True")
                            cmd_list = [self.tc_pairs_exe, " -adeck ",
                                        adeck_file_path, " -bdeck ",
                                        bdeck_file_path, " -config ",
                                        self.tc_pairs_config_path, " -out ",
                                        pairs_out_file]
                            cmd = ''.join(cmd_list)
                            cmd = batchexe('sh')['-c', cmd].err2out()
                            self.logger.debug("DEBUG | [" + cur_filename + ":"
                                              + cur_function + "] | " +
                                              "Running tc_pairs with command: "
                                              + cmd.to_shell())
                            ret = run(cmd, sleeptime=.00001)
                            if ret != 0:
                                self.logger.error("ERROR | [" + cur_filename +
                                                  ":" + cur_function + "] | " +
                                                  "Problem executing: " +
                                                  cmd.to_shell())
                                exit(0)
                        else:
                            self.logger.debug("DEBUG | [" + cur_filename +
                                              ":" + cur_function + "] | " +
                                              "Existing tc_pairs output " +
                                              "file: " + pairs_out_file +
                                              ", is available for "
                                              + "use. To overwrite set " +
                                              "TC_PAIRS_FORCE_OVERWRITE " +
                                              "to True")
                    else:
                        cmd = self.tc_pairs_exe + " -adeck " + \
                              adeck_file_path + \
                              " -bdeck " + bdeck_file_path + " -config " + \
                              self.tc_pairs_config_path + " -out " + \
                              pairs_out_file
                        cmd = batchexe('sh')['-c', cmd].err2out()
                        self.logger.debug("DEBUG | [" + cur_filename + ":" +
                                          cur_function + "] | " +
                                          "Running tc_pairs with command: " +
                                          cmd.to_shell())
                        ret = run(cmd, sleeptime=.00001)
                        if ret != 0:
                            self.logger.error("ERROR | [" + cur_filename +
                                              ":" + cur_function + "] | " +
                                              "Problem executing: " +
                                              cmd.to_shell())
                            exit(0)


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='run_tc_pairs',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_pairs')
        produtil.log.postmsg('run_tc_pairs is starting')

        config_inst = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = config_inst.getdir('MET_BASE')
        TCP = TcPairs(config_inst)
        TCP.main()
        produtil.log.postmsg('run_tc_pairs completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'run_tc_pairs failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
