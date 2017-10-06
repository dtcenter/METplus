#!/usr/bin/env python

from __future__ import print_function

import unittest
import os
import re
import shutil
import config_metplus
from series_by_init import SeriesByInit
import met_util as util
import produtil.setup


class TestSeriesByInit(unittest.TestCase):
    def setUp(self):
        self.p = self.get_config()
        self.logger = util.get_logger(self.p)
        self.sbi = SeriesByInit(self.p, self.logger)

    def tearDown(self):
        shutil.rmtree(self.sbi.series_out_dir)
        shutil.rmtree(self.sbi.series_filtered_out_dir)

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

    def test_anly_fcst_ascii_files_exist(self):
        """ Test that in the series_init_filtered directory, the
            tmp_anly_regridded.txt and tmp_fcst_regridded.txt files
            exist.
        """
        self.sbi.run_all_times()
        filter_output_dir = self.sbi.series_filtered_out_dir
        filter_files_list = os.listdir(filter_output_dir)
        fcst_count = 0
        anly_count = 0
        for filter_file in filter_files_list:
            match_fcst = re.match(r'^tmp_fcst_regridded.txt', filter_file)
            match_anly = re.match(r'^tmp_anly_regridded.txt', filter_file)
            if match_fcst:
                fcst_count += 1
            if match_anly:
                anly_count += 1
        self.assertTrue(fcst_count == 1 and anly_count == 1)

    def test_check_filtering_ok(self):
        """ For a given filter condition, ensure that the filter criteria
                is met.  Perform a simple filtering based on basin=ML and
                make sure all subdirectories created in the series_init
               _filtered directory begin with ML.
        """
        self.sbi.run_all_times()
        filter_output_dir = self.sbi.series_filtered_out_dir
        dated_filter_files_list = os.listdir(filter_output_dir)
        self.sbi.filter_opts = "EXTRACT_TILES_FILTER_OPTS = -basin ML"

        # Get the storm subdirs in the dated_filter_files_list
        for dated_filter_file in dated_filter_files_list:
            potential_dir = os.path.join(filter_output_dir, dated_filter_file)
            if os.path.isdir(potential_dir):
                storm_subdir_list = os.listdir(potential_dir)
                for storm_subdir in storm_subdir_list:
                    potential_storm_dir = os.path.join(potential_dir,
                                                       storm_subdir)
                    if os.path.isdir(potential_storm_dir):
                        match = re.match(r'^ML', storm_subdir)
                        self.assertTrue(match)

    # def test_fcst_anly_ascii_files_not_empty(self):
    #     """ Verify that the ANLY_ASCII_FILES_<storm-month-date> and
    #         FCST_ASCII_FILES_<storm-month-date> text file (which contain
    #         a list of all the files to be included in the series analysis) in
    #         the series_analysis_int/YYYYMMDD_hh/storm directory are
    #         not empty files.
    #     """
    #     self.sbi.run_all_times()
    #     anly_ascii_ok = False
    #     fcst_ascii_ok = False
    #     dated_dir_list = os.listdir(self.sbi.series_out_dir)
    #     # Get the storm sub-directories in each dated sub-directory
    #     for dated_dir in dated_dir_list:
    #         dated_dir_path = os.path.join(self.sbi.series_out_dir, dated_dir)
    #         # Get a list of the storm sub-dirs in this directory
    #         all_storm_list = os.listdir(dated_dir_path)
    #         for each_storm in all_storm_list:
    #             full_storm_dirname = os.path.join(dated_dir_path, each_storm)
    #             # Now get the list of files for each storm sub-dir.
    #             all_files = os.listdir(full_storm_dirname)
    #             for each_file in all_files:
    #                 full_filepath = os.path.join(full_storm_dirname, each_file)
    #                 if os.path.isfile(full_filepath):
    #                     if full_filepath.startswith("ANLY_ASCII_FILES"):
    #                         if os.stat(full_filepath).st_size > 0:
    #                             anly_ascii_ok = True
    #                     if full_filepath.startswith("FCST_ASCII_FILES"):
    #                         if os.stat(full_filepath).st_size > 0:
    #                             fcst_ascii_ok = True
    #                     self.assertTrue(anly_ascii_ok and fcst_ascii_ok)

    def test_netcdf_files_created(self):
        """ Verify that NetCDF files were created by series_analysis"""
        self.sbi.run_all_times()
        dated_dir_list = os.listdir(self.sbi.series_out_dir)
        netcdf_file_counter = 0

        # Get the storm sub-directories in each dated sub-directory
        for dated_dir in dated_dir_list:
            dated_dir_path = os.path.join(self.sbi.series_out_dir, dated_dir)
            # Get a list of the storm sub-dirs in this directory
            all_storm_list = os.listdir(dated_dir_path)
            for each_storm in all_storm_list:
                full_storm_dirname = os.path.join(dated_dir_path, each_storm)
                # Now get the list of files for each storm sub-dir.
                all_files = os.listdir(full_storm_dirname)
                for each_file in all_files:
                    full_filepath = os.path.join(full_storm_dirname, each_file)
                    if os.path.isfile(full_filepath):
                        if full_filepath.endswith('.nc'):
                            netcdf_file_counter += 1

        self.assertTrue(netcdf_file_counter > 0)

    def test_output_exists(self):
        """ Make sure that the series_analysis_init output
            directory isn't empty.  If so, then something went wrong with
            building the command or in the series_init run.
        """
        self.sbi.run_all_times()
        output_dir = self.sbi.series_out_dir
        self.assertTrue(os.listdir(output_dir))

    def test_check_for_created_graphics_files(self):
        """ Check that the expected NetCDF, png, and Postscript files
            are present in the series_analysis_init/<storm month-number date
            subdirectory.
        """
        self.sbi.run_all_times()
        output_dir = self.sbi.series_out_dir
        dated_filter_files_list = os.listdir(output_dir)
        # Get the storm sub-dirs in the first dated_filter_files_list
        first_dated_subdir = os.path.join(output_dir, dated_filter_files_list[0])
        storm_subdir_list = os.listdir(first_dated_subdir)
        first_storm_subdir = os.path.join(first_dated_subdir, storm_subdir_list[0])
        # Search for files ending in .nc, .ps, and .png
        nc_results = []
        png_results = []
        ps_results = []
        for each_file in os.listdir(first_storm_subdir):
            if each_file.endswith('.nc'):
                nc_results.append(each_file)
            if each_file.endswith('.png'):
                png_results.append(each_file)
            if each_file.endswith('.ps'):
                ps_results.append(each_file)

        self.assertTrue(nc_results and png_results and ps_results)

if __name__ == "__main__":
    unittest.main()
