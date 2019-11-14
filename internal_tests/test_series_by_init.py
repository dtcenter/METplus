#!/usr/bin/env python

import unittest
import os
import re
import config_metplus
from series_by_init_wrapper import SeriesByInitWrapper
import met_util as util
import produtil.setup
import sys


"""!This class can NOT be instantiated directly. It MUST be called from main.
    The main function operates outside of this class which sets up the METplus
    configuration object, $METPLUS_CONF, and runs series_by_init_wrapper. Than 
    all the unit tests in this class are based on the output from that one run.
"""
class TestSeriesByInit(unittest.TestCase):
    def __init__(self,*args):
        super(TestSeriesByInit,self).__init__(*args)
        # self.p is an instance variable BUT it will be the same
        # for all instances since TestSeriesByInit.config_inst is static.
        #self.p = TestSeriesByInit.config_inst
        self.sbi = TestSeriesByInit.sbi
        self.logger = self.sbi.logger

    def setUp(self):
        # Perform setup for each test.
        pass

    def tearDown(self):
        # Perform any cleanup after each test.
        pass
        #util.rmtree(self.sbi.series_out_dir)
        #util.rmtree(self.sbi.series_filtered_out_dir)

    def test_anly_fcst_ascii_files_exist(self):
        """ Test that in the series_init_filtered directory, the
            tmp_anly_regridded.txt and tmp_fcst_regridded.txt files
            exist.
        """
        #self.sbi.run_all_times()
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
        #self.sbi.run_all_times()
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
        #self.sbi.run_all_times()
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
        #self.sbi.run_all_times()
        output_dir = self.sbi.series_out_dir
        self.assertTrue(os.listdir(output_dir))

    def test_check_for_created_graphics_files(self):
        """ Check that the expected NetCDF, png, and Postscript files
            are present in the series_analysis_init/<storm month-number date
            subdirectory.
        """
        #self.sbi.run_all_times()
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
    # NOTE: We are using unittest in a non-conventional manner.
    # This is more of an integration test, testing the output of running
    # series by init.
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
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='test_series_by_init',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test_series_by_init')
        produtil.log.postmsg('test_series_by_init is starting')

        # Process command line args conf files, creates a conf object and final conf file.
        CONFIG_INST = config_metplus.setup()

        # This is specfic to this unit test class.
        # Set a class level variable, (a METPlus configuration object), that can be used
        # and referenced by a unit test object.
        TestSeriesByInit.config_inst = CONFIG_INST

        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        # Instantitates and runs series by init. Generating output.
        SBI = SeriesByInitWrapper(CONFIG_INST, logger=None)
        TestSeriesByInit.sbi = SBI
        SBI.run_all_times()
        produtil.log.postmsg('SeriesByInitWRapper.run_all_times completed')


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
        util.rmtree(SBI.series_out_dir)
        util.rmtree(SBI.series_filtered_out_dir)


    except Exception as exc:
        produtil.log.jlogger.critical(
            'test_series_by_init failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)

