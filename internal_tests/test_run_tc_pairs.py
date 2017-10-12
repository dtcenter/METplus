#!/usr/bin/env python

from __future__ import print_function

import unittest
import os
import config_metplus
from run_tc_pairs import TcPairs
import csv
import re
import shutil
import produtil.setup


class TestRunTcPairs(unittest.TestCase):
    def setUp(self):
        """ Run run_tc_pairs.py based on the metplus.conf file in the
            $METPLUS_BASE/parm directory, then base all unit tests on
            the output from that run.
        """
        self.p = self.get_config()
        rtcp = TcPairs(self.p)
        rtcp.main()

    def tearDown(self):
        shutil.rmtree(self.p.getdir('TRACK_DATA_SUBDIR_MOD'))
        shutil.rmtree(self.p.getdir('TC_PAIRS_DIR'))

    @staticmethod
    def get_config():
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='test run_tc_pairs',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False,
                                 jobname='test run_tc_pairs')
        produtil.log.postmsg('unit test for run_tc_pairs is starting')

        # Read in the configuration object CONFIG_INST
        config_instance = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = config_instance.getdir('MET_BASE')

        return config_instance

    def test_no_empty_mod_dir(self):
        """ Verify that we are creating the ATCF files. """
        tc_pairs_dir = self.p.getdir('TC_PAIRS_DIR')
        self.assertTrue(os.listdir(tc_pairs_dir))

    def test_no_empty_tcp_dir(self):
        """ Verify that we are creating tc pair output"""
        tc_pairs_dir = self.p.getdir('TC_PAIRS_DIR')
        self.assertTrue(os.listdir(tc_pairs_dir))

    def test_one_less_column(self):
        """ Tests the read_modify_write_file() method.
            Verify that the output in the track_data_atcf directory
            has one fewer column than the input track data.
        """
        track_data_dir = self.p.getdir('TRACK_DATA_DIR')
        track_data_subdir_mod = self.p.getdir('TRACK_DATA_SUBDIR_MOD')

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
        track_data_dir = self.p.getdir('TRACK_DATA_DIR')
        track_data_subdir_mod = self.p.getdir('TRACK_DATA_SUBDIR_MOD')
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

        tc_pairs_dir = self.p.getdir('TC_PAIRS_DIR')
        track_data_subdir_mod = self.p.getdir('TRACK_DATA_SUBDIR_MOD')

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

if __name__ == "__main__":
    unittest.main()
