#!/usr/bin/env python

"""
Program Name: extract_tiles_wrapper.py
Contact(s): Julie Prestopnik, Minna Win, George McCabe, Jim Frimel
Abstract: Extracts tiles to be used by series_analysis
Parameters: None
Input Files: tc_pairs data
Output Files: tiled grib2 files
Condition codes: 0 for success, 1 for failure

"""

import metplus_check_python_version

import os
import sys
import met_util as util
import feature_util
from tc_stat_wrapper import TCStatWrapper
from command_builder import CommandBuilder
import time_util

'''!@namespace ExtractTilesWrapper
@brief Runs  Extracts tiles to be used by series_analysis.
Call as follows:
@code{.sh}
extract_tiles_wrapper.py [-c /path/to/user.template.conf]
@endcode
'''


class ExtractTilesWrapper(CommandBuilder):
    """! Takes tc-pairs data and regrids paired data to an n x m grid as
         specified in the config file.
    """

    # pylint: disable=too-many-instance-attributes
    # Eleven is needed in this case.
    # pylint: disable=too-few-public-methods
    # Much of the data in the class are used to perform tasks, rather than
    # having methods operating on them.

    def __init__(self, config, logger):
        self.app_name = 'extract_tiles'
        super().__init__(config, logger)
        met_bin_dir = self.config.getdir('MET_BiN_DIR', '')
        self.tc_pairs_dir = self.config.getdir('EXTRACT_TILES_PAIRS_INPUT_DIR')
        self.overwrite_flag = self.config.getbool('config',
                                              'EXTRACT_TILES_OVERWRITE_TRACK')
        self.addl_filter_opts = \
            self.config.getstr('config', 'EXTRACT_TILES_FILTER_OPTS')
        self.filtered_out_dir = self.config.getdir('EXTRACT_TILES_OUTPUT_DIR')
        self.tc_stat_exe = os.path.join(met_bin_dir, 'tc_stat')

    def run_at_time(self, input_dict):
        """!Loops over loop strings and calls run_at_time_loop_string() to process data
        Args:
            input_dict:  Time dictionary
        Returns:
            None
        """

        # Do some set up
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string
            self.run_at_time_loop_string(input_dict)

    def run_at_time_loop_string(self, input_dict):
        """!Get TC-paris data then regrid tiles centered on the storm.

        Get TC-pairs track data and GFS model data, do any necessary
        processing then regrid the forecast and analysis files to a
        30 x 30 degree tile centered on the storm.
        Args:
            input_dict:  Time dictionary
        Returns:

            None: invokes regrid_data_plane to create a netCDF file from two
                    extratropical storm track files.
        """

        # Do some set up
        time_info = time_util.ti_calculate(input_dict)
        init_time = time_info['init_fmt']
        tmp_dir = self.config.getdir('TMP_DIR')

        self.logger.info("Begin extract tiles")
        cur_init = init_time[0:8]+"_"+init_time[8:10]

        # Before proceeding, make sure we have input data.
        if not self.tc_files_exist():
            self.log_error("No tc pairs data found at {}" \
                           .format(self.tc_pairs_dir))
            sys.exit(1)

        # Create the name of the filter file we need to find.  If
        # the filter file doesn't yet exist, then run TC_STAT
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(self.filtered_out_dir, cur_init,
                                   filter_filename)
        if util.file_exists(filter_name) and not self.overwrite_flag:
            self.logger.debug("Filter file exists, using Track data file: {}"\
                              .format(filter_name))
        else:
            # Invoke MET tool tc stat via the tc stat wrapper...
            filtering_ok = self.do_filtering(cur_init, filter_name)
            if filtering_ok != 0:
                self.log_error("There was a problem running MET tc stat, please check your METplus "\
                               "config file settings.s")
                sys.exit(1)

        # Now get unique storm ids from the filter file,
        # filter_yyyymmdd_hh.tcst
        sorted_storm_ids = util.get_storm_ids(filter_name, self.logger)

        # Useful debugging info: Check for empty sorted_storm_ids, if empty,
        # continue to the next time.
        if not sorted_storm_ids:
            # No storms found for init time, cur_init
            msg = "No storms were found for {} ...continue to next in list"\
              .format(cur_init)
            self.logger.debug(msg)
            return

        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # /tmp directory where each file contains information based on storm.
        if not self.create_results_files(sorted_storm_ids, cur_init, filter_name, tmp_dir):
            self.log_error("There was a problem with processing storms from the filtered result, "\
                    "please check your METplus config file settings or your write permissions for your "\
                    "tmp directory.")

        util.prune_empty(self.filtered_out_dir, self.logger)

    def tc_files_exist(self):
        ''' Check that there are tc_pairs data files (.tcst) which are needed as input
            to the extract tiles wrapper

            Args:

            Return:
                True if .tcst files exist, False otherwise

        '''

        tc_pairs_nc_output_regex = ".*.tcst"
        output_files_list = util.get_files(self.tc_pairs_dir, tc_pairs_nc_output_regex, self.logger)
        if len(output_files_list) == 0:
            return False
        else:
            return True

    def do_filtering(self, cur_init, filter_name):
        ''' run TC_STAT because the filter output file hasn't yet been created
            by the MET tc stat tool.

            Args:
                @param cur_init:  The current init time of interest
                @param filter_name: The full filename of the file that will contain filtered results generated
                                    by the MET tool tc stat.
            Return:
                0 if MET tc stat tool completed successfully (which will
                create a filter_name file (which was defined/created in run_at_time()
                in the output directory).
        '''

        # Create the storm track by applying the
        # filter options defined in the config/param file.
        # Use TCStatWrapper to build up the tc_stat command and invoke
        # the MET tool tc_stat to perform the filtering.
        tiles_list = util.get_files(self.tc_pairs_dir, ".*tcst", self.logger)
        tiles_list_str = ' '.join(tiles_list)

        tcs = TCStatWrapper(self.config, self.logger)
        tcs.build_tc_stat(self.filtered_out_dir, cur_init,
                          tiles_list_str, self.addl_filter_opts)

        # Remove any empty files and directories that can occur
        # from filtering.
        util.prune_empty(filter_name, self.logger)

        return 0

    def create_results_files(self, sorted_storm_ids, cur_init, filter_name, tmp_dir):
        ''' Create the tmp files that contain filtered results- one tmp file per storm, then
            invoke retrieve_and_regrid to create the final output as netCDF forecast and analysis (obs)
            files.

            Args:
                @param sorted_storm_ids:
                @param cur_init: The current init time of interest
                @param filter_name: The full file name of the filter file generated by tc stat
                @param tmp_dir: The location of the tmp directory where these tmp files will be saved



            Return:
             0 if successful in creating the tmp files (one per storm) in the tmp_dir
        '''

        processed_file = False
        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # /tmp/<pid> directory.
        for cur_storm in sorted_storm_ids:
            storm_output_dir = os.path.join(self.filtered_out_dir,
                                            cur_init, cur_storm)
            header = open(filter_name, "r").readline()
            util.mkdir_p(storm_output_dir)

            tmp_filename = "filter_" + cur_init + "_" + cur_storm
            full_tmp_filename = os.path.join(tmp_dir, tmp_filename)

            storm_match_list = util.grep(cur_storm, filter_name)

            # open with w+ to overwrite if it exists and create it if not
            with open(full_tmp_filename, "w") as tmp_file:
                # copy over header information
                tmp_file.write(header)
                for storm_match in storm_match_list:
                    tmp_file.write(storm_match)

            feature_util.retrieve_and_regrid(full_tmp_filename, cur_init,
                                             cur_storm, self.filtered_out_dir,
                                             self.config)

            # remove tmp file
            os.remove(full_tmp_filename)
            processed_file = True

        return processed_file

if __name__ == "__main__":
    util.run_stand_alone(__file__, "ExtractTiles")
