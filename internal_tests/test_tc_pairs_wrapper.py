#!/usr/bin/env python

from __future__ import print_function

import unittest
import os
import config_metplus
from tc_pairs_wrapper import TcPairsWrapper
import csv
import re
import shutil
import met_util as util
import produtil.setup
import sys


"""!This class can NOT be instantiated directly. It MUST be called from main.
    The main function operates outside of this class which sets up the METplus
    configuration object, $METPLUS_CONF, used by all unit tests. 

    Each unit test calls TcPairsWrapper.run_at_time
"""

class TestTcPairsWrapper(unittest.TestCase):

    def __init__(self,*args):
        super(TestTcPairsWrapper,self).__init__(*args)
        # self.config is an instance variable BUT it will be the same
        # for all instances since TestRunTcPairs.config_inst is static.
        # We can really refer to TestRunTcPairs.config_inst
        # throughout the class and don't need to assign it to the
        # self.config instance variable.
        self.config = TestTcPairsWrapper.config_inst


    def setUp(self):
        """ Run run_tc_pairs.py based on the metplus.conf file in the
            $METPLUS_BASE/parm directory, then base all unit tests on
            the output from that run.
        """
        # Get the desired YYYYMMDD_HH init increment list
        # convert the increment INIT_INC from seconds to hours
        self.init_list = util.gen_init_list(
            self.config.getstr('config', 'INIT_BEG'),
            self.config.getstr('config', 'INIT_BEG'),
            int(self.config.getint('config', 'INIT_INC')/3600),
            self.config.getstr('config', 'INIT_HOUR_END'))

        # just run the first time
        #self.request_time = self.init_list[0]
        self.request_time = self.init_list
        
    def tearDown(self):
        shutil.rmtree(self.config.getdir('TRACK_DATA_SUBDIR_MOD'))
        shutil.rmtree(self.config.getdir('TC_PAIRS_DIR'))

    def test_no_empty_mod_dir(self):
        """ Verify that we are creating the ATCF files. """
        rtcp = TcPairsWrapper(self.config, logger=None)
        rtcp.run_at_time(self.request_time)
        tc_pairs_dir = self.config.getdir('TC_PAIRS_DIR')
        self.assertTrue(os.listdir(tc_pairs_dir))

    def test_no_empty_tcp_dir(self):
        """ Verify that we are creating tc pair output"""
        rtcp = TcPairsWrapper(self.config, logger=None)
        rtcp.run_at_time(self.request_time)
        tc_pairs_dir = self.config.getdir('TC_PAIRS_DIR')
        self.assertTrue(os.listdir(tc_pairs_dir))

    def test_one_less_column(self):
        """ Tests the read_modify_write_file() method.
            Verify that the output: in the track_data_atcf directory
            has one fewer column than the input track data.
        """
        rtcp = TcPairsWrapper(self.config, logger=None)
        rtcp.run_at_time(self.request_time)
        track_data_dir = self.config.getdir('TRACK_DATA_DIR')
        track_data_subdir_mod = self.config.getdir('TRACK_DATA_SUBDIR_MOD')

        # So that we have independence of the start and end times indicated
        # in the metplus.conf or any other conf file, perform the test as
        # follows:
        # 1) get a list of directories in the track_data_dir and
        #    track_data_subdir_mod
        # 2) use the first directory of each in #1
        # 3) then look at the first file in each of those directories in #2
        # We don't need to have matching dates and filename in the original and
        # modified files, since we are only interested in the *number* of
        # columns in the files.
        orig_dir_list = os.listdir(track_data_dir)
        mod_dir_list = os.listdir(track_data_subdir_mod)
        orig_first_file_list = os.listdir(
            os.path.join(track_data_dir, orig_dir_list[0]))
        mod_first_file_list = os.listdir(
            os.path.join(track_data_subdir_mod, mod_dir_list[0]))
        orig_first_file = orig_first_file_list[0]
        mod_first_file = mod_first_file_list[0]
        orig_tc_file = os.path.join(track_data_dir, orig_dir_list[0],
                                    orig_first_file)
        mod_tc_file = os.path.join(track_data_subdir_mod, mod_dir_list[0],
                                   mod_first_file)
        # Get the number of columns from the first row of the original and
        # modified files, respectively.
        with open(orig_tc_file) as f:
            reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
            first_row = next(reader)
            orig_num_cols = len(first_row)
        with open(mod_tc_file) as f:
            reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
            first_row = next(reader)
            mod_num_cols = len(first_row)

        self.assertTrue(mod_num_cols == (orig_num_cols - 1))

    def test_col2_format_ok(self):
        """Tests for proper behavior in the read_modify_write_file() method
           Verify that the second column of one of the modified tc track files
           does indeed have the month followed by the storm id:
           Get the first row of the first file in the same subdirectory of the
           modified and input directory (i.e. same month)
        """
        rtcp = TcPairsWrapper(self.config, logger=None)
        rtcp.run_at_time(self.request_time)
        track_data_dir = self.config.getdir('TRACK_DATA_DIR')
        track_data_subdir_mod = self.config.getdir('TRACK_DATA_SUBDIR_MOD')
        mod_dir_list = os.listdir(track_data_subdir_mod)

        # Get the first directory in the TRACK_DATA_SUBDIR_MOD directory and
        # the matching year-month dir in the TRACK_DATA_DIR directory.
        year_month_dir = mod_dir_list[0]
        mod_first_file_list = os.listdir(
            os.path.join(track_data_subdir_mod, year_month_dir))

        # Get the track file that corresponds to the modified track file's
        # first file.
        first_track_file = mod_first_file_list[0]
        mod_tc_file = os.path.join(track_data_subdir_mod, year_month_dir,
                                   first_track_file)
        orig_tc_file = os.path.join(track_data_dir, year_month_dir,
                                    first_track_file)

        # Get the month from the year_month_dir
        month_match = re.match(r'[0-9]{4}([0-9]{2})', year_month_dir)
        if month_match:
            month = month_match.group(1)

            # Get the number of columns from the first row of the original and
            # modified files, respectively.
            with open(orig_tc_file) as f:
                reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
                first_row = next(reader)
                orig_storm_id = first_row[1]
            with open(mod_tc_file) as f:
                reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
                first_row = next(reader)
                mod_storm_id = first_row[1]
            # Create the expected storm id and compare it to what was produced
            # in the modified file.
            expected_storm_id = month + orig_storm_id
            self.assertEqual(mod_storm_id, expected_storm_id)
        else:
            # If no match, something is wrong, force test to fail.
            self.asssertTrue(False)

        # Verify that the second column is the correct month and is the
        # combination of month and storm id.  Get the storm id from the
        # second column of the original (input file), create the expected
        # string and compare that to what we observe for the second column
        # in the modified file.
        self.assertTrue(True)

    def test_same_dates_in_mod_and_final_dir(self):
        """ Test that the dirs (i.e. dates) that were found in the modified dir
            are also found in the final track data output dir.  Verify that the
            list of dates in the TRACK_DATA_SUBDIR_MOD directory are equal to
            the list of dates in the TRACK_DATA_DIR directory.
        """
        rtcp = TcPairsWrapper(self.config, logger=None)
        tc_pairs_dir = self.config.getdir('TC_PAIRS_DIR')
        track_data_subdir_mod = self.config.getdir('TRACK_DATA_SUBDIR_MOD')
        rtcp.run_at_time(self.request_time)

        # First check that there are the same number of subdirectories in the
        # TC_PAIRS_DIR (the final output dir) and TRACK_DATA_SUBDIR_MOD
        # directories (i.e. the same number of year-month data).
        mod_year_month_list = os.listdir(track_data_subdir_mod)
        final_year_month_list = os.listdir(tc_pairs_dir)
        if len(final_year_month_list) == len(mod_year_month_list):
            # Make sure the dates in the TRACK_DATA_SUBDIR_MOD are found in the
            # TC_PAIRS_DIR.
            for year_month_dir in final_year_month_list:
                if year_month_dir not in mod_year_month_list:
                    # If the year_month directory in the final output directory
                    # doesn't exist in the mod directory, fail the test.
                    self.assertTrue(False)
        else:
            # If the directories don't have the same number of subdirectories,
            # something is wrong, force the test to fail.
            self.assertTrue(False)

        # If we get here, then the test passes
        self.assertTrue(True)

    def test_num_files_in_subdir_mod_for_201412(self):
        """ Verify that for INIT_DATE_BEG=20141205 and
            INIT_DATE_END=20141206 for GFS data in /d1/SBU/GFS,
            the track_data_atcf directory contains 450 files"""
        rtcp = TcPairsWrapper(self.config, logger=None)
        request_time = "20141205_00"
        rtcp.run_at_time(request_time)
        request_subdir = "201412"
        atcf_dir = os.path.join(
            self.config.getdir('TRACK_DATA_SUBDIR_MOD'),
            request_subdir)
        subdir_mod_file_list = os.listdir(atcf_dir)
        self.assertEquals(len(subdir_mod_file_list), 450)


if __name__ == "__main__":
    # NOTE: We are using unittest in a non-conventional manner.
    # This is more of an integration test, testing the output of running
    # tc_pairs_wrapper.py.
    #
    # main Assumes ALL arguments passed in are only for METplus configuration
    # file processing.
    # The unittest class also has its own set of command line arguments
    # but we will not use them and do not have logic in place to 
    # automatically handle using command arguments for both METplus
    # and the unittest framework.
    # 
    # So AFTER we use the conf file arguments we must pop the command 
    # lines args so the unittest class doesn't try to process the conf file
    # arguments as unittest arguments.

    try:
        print('\nEXITING, Do Not Run. This test file is not complete.')
        print('Must implement a run_at_time method in tc_pairs_wrapper.py\n')
        sys.exit(0)

        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='test_tc_pairs_wrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test_tc_pairs_wrapper')
        produtil.log.postmsg('test_tc_pairs_wrapper is starting')

        # Process command line args conf files, creates a conf object and final conf file.
        CONFIG_INST = config_metplus.setup()

        # This is specfic to this unit test class.
        # Set a class level variable, (a METPlus configuration object), that can be used
        # and referenced by a unit test object.
        TestTcPairsWrapper.config_inst = CONFIG_INST

        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        # Instantiates and runs tc pairs. Generating output.
        #TCP = TestTcPairsWrapper(CONFIG_INST, logger=None)
        #TCP.run_all_times()
        #produtil.log.postmsg('test_tc_pairs_wrapper run_all_times  completed')

        # Remove all conf file command line arguments from sys.argv,
        # except sys.argv[0]. Removing conf args allows unittest.main() 
        # to run, else it will fail.
        for arg in range(1, len(sys.argv)):
            sys.argv.pop()

        # Workaround - to pass in command line args to unittest.main()
        # You must code them in here ....
        # For example, uncomment the next line and you will see available options.
        # sys.argv.append('-h')

        # Setting exit=False allows unittest to return and NOT sys.exit, which
        # allows commands after unittest.main() to execute.
        unittest.main(exit=False)

        # Caveate to exit=False
        # It seems if you pass in an argument  than unittest will sys.exit
        # and these line do not get executed, 
        # at least for '-h' argument .... ie. sys.argv.append('-h')
        #shutil.rmtree(CONFIG_INST.getdir('TRACK_DATA_SUBDIR_MOD'))
        #shutil.rmtree(CONFIG_INST.getdir('TC_PAIRS_DIR'))

    except Exception as exc:
        produtil.log.jlogger.critical(
            'test_tc_pairs_wrapper failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)



