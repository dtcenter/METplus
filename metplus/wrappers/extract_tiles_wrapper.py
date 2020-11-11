"""
Program Name: extract_tiles_wrapper.py
Contact(s): Julie Prestopnik, Minna Win, George McCabe, Jim Frimel
Abstract: Extracts tiles to be used by series_analysis
Parameters: None
Input Files: tc_pairs data
Output Files: tiled grib2 files
Condition codes: 0 for success, 1 for failure

"""

import os
import sys
from datetime import datetime

from ..util import met_util as util
from ..util import feature_util
from ..util import do_string_sub
from .tc_stat_wrapper import TCStatWrapper
from . import CommandBuilder
from ..util import time_util

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

    def __init__(self, config):
        self.app_name = 'extract_tiles'
        super().__init__(config)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['PAIRS_INPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_PAIRS_INPUT_DIR', '')
        )
        if not c_dict['PAIRS_INPUT_DIR']:
            self.log_error('Must set EXTRACT_TILES_PAIRS_INPUT_DIR to run '
                           'ExtractTiles wrapper')

            c_dict['GRID_INPUT_DIR'] = (
                self.config.getdir('EXTRACT_TILES_GRID_INPUT_DIR', '')
            )
            if not c_dict['GRID_INPUT_DIR']:
                self.log_error('Must set EXTRACT_TILES_GRID_INPUT_DIR to run '
                               'ExtractTiles wrapper')

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_OUTPUT_DIR', '')
        )
        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set EXTRACT_TILES_OUTPUT_DIR to run '
                           'ExtractTiles wrapper')

        c_dict['FILTERED_OUTPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'EXTRACT_TILES_FILTERED_OUTPUT_TEMPLATE',
                               '')
        )
        if not c_dict['FILTERED_OUTPUT_TEMPLATE']:
            self.log_error('Must set EXTRACT_TILES_FILTERED_OUTPUT_TEMPLATE '
                           'to run ExtractTiles wrapper')

        c_dict['SKIP_IF_OUTPUT_EXISTS'] = (
            self.config.getbool('config',
                                'EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS',
                                False)
        )
        c_dict['TC_STAT_FILTER_OPTS'] = (
            self.config.getstr('config', 'EXTRACT_TILES_FILTER_OPTS', '')
        )
        if not c_dict['TC_STAT_FILTER_OPTS']:
            self.log_error('Must set EXTRACT_TILES_FILTER_OPTS to run '
                           'ExtractTiles wrapper')

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_OUTPUT_DIR', '')
        )
        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set EXTRACT_TILES_OUTPUT_DIR to run '
                           'ExtractTiles wrapper')

        return c_dict

    def run_at_time(self, input_dict):
        """!Loops over loop strings and calls run_at_time_loop_string() to
            process data

            @param input_dict dictionary containing initialization time
        """

        # loop over custom loop list. If not defined,
        # it will run once with an empty string as the custom string
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string
            self.run_at_time_loop_string(input_dict)

    def run_at_time_loop_string(self, input_dict):
        """!Read TCPairs track data into TCStat to filter the data. Using the
            resulting track data, run RegridDataPlane on the model data to
            create tiles centered on the storm.

            @param input_dict dictionary containing initialization time
        """

        # Calculate other time information from available time info
        time_info = time_util.ti_calculate(input_dict)

        self.logger.debug("Begin extract tiles")
        init_fmt = time_info['init'].strftime('%Y%m%d_%H')

        # Before proceeding, make sure we have input data.
        if not self.tc_files_exist():
            self.log_error("No TCPairs data found in "
                           f"{self.c_dict['PAIRS_INPUT_DIR']}")
            return

        # Create the name of the filter file we need to find.  If
        # the filter file doesn't yet exist, then run TCStat
        filter_filename = (
            do_string_sub(self.c_dict['FILTERED_OUTPUT_TEMPLATE'],
                          **time_info)
        )
        filter_name = os.path.join(self.c_dict['OUTPUT_DIR'],
                                   filter_filename)

        if (util.file_exists(filter_name) and
                self.c_dict['SKIP_IF_OUTPUT_EXISTS']):
            self.logger.debug("Filter file exists, using Track data file: {}"\
                              .format(filter_name))
        else:
            # Invoke MET tool tc stat via the tc stat wrapper...
            if not self.do_filtering(time_info, filter_name):
                return

        # Now get unique storm ids from the filter file
        sorted_storm_ids = util.get_storm_ids(filter_name, self.logger)

        # Useful debugging info: Check for empty sorted_storm_ids, if empty,
        # continue to the next time.
        if not sorted_storm_ids:
            # No storms found for init time, init_fmt
            self.logger.debug(f"No storms were found for {init_fmt}"
                              "...continue to next in list")
            return

        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # tmp directory where each file contains information based on storm.
        if not self.create_results_files(sorted_storm_ids,
                                         init_fmt,
                                         filter_name):
            self.log_error("There was a problem with processing storms from the filtered result, "\
                    "please check your METplus config file settings or your write permissions for your "\
                    "tmp directory.")

        util.prune_empty(self.c_dict['OUTPUT_DIR'], self.logger)

    def tc_files_exist(self):
        """! Check that there are tc_pairs data files (.tcst) which are needed
            as input to the extract tiles wrapper

            @returns True if .tcst files exist, False otherwise
        """

        tc_pairs_nc_output_regex = ".*.tcst"
        output_files_list = util.get_files(self.c_dict['PAIRS_INPUT_DIR'],
                                           tc_pairs_nc_output_regex)
        return len(output_files_list) != 0

    def do_filtering(self, time_info, filter_name):
        """! run TCStat to filter TCPairs data

            @param time_info time dictionary for current run
            @param filter_name full path of the file that will contain
             filtered results generated by the MET tool tc_stat
        """

        # Create the storm track by applying the
        # filter options defined in the config/param file.
        # Use TCStatWrapper to build up the tc_stat command and invoke
        # the MET tool tc_stat to perform the filtering.
        cur_init = time_info['init'].strftime('%Y%m%d_%H')
        job_args = (f"-job filter {self.c_dict['TC_STAT_FILTER_OPTS']}"
                    f' -dump_row {filter_name}')
        override_dict = {'TC_STAT_JOB_ARGS': job_args,
                         'TC_STAT_INIT_INCLUDE': cur_init,
                         'TC_STAT_LOOKIN_DIR': self.c_dict['PAIRS_INPUT_DIR'],
                         'TC_STAT_OUTPUT_DIR': self.c_dict['OUTPUT_DIR'],
                         'TC_STAT_MATCH_POINTS': True,
                         }
        tc_stat_wrapper = TCStatWrapper(self.config, override_dict)
        if not tc_stat_wrapper.isOK:
            return False

        if not tc_stat_wrapper.run_at_time(time_info):
            return False

        # Remove any empty files and directories that can occur
        # from filtering.
        util.prune_empty(filter_name, self.logger)
        return True

    def create_results_files(self, sorted_storm_ids, cur_init, filter_name):
        ''' Create the tmp files that contain filtered results- one tmp file per storm, then
            invoke retrieve_and_regrid to create the final output as netCDF forecast and analysis (obs)
            files.

            Args:
                @param sorted_storm_ids:
                @param cur_init: The current init time of interest
                @param filter_name: The full file name of the filter file generated by tc stat

            Return:
             0 if successful in creating the tmp files (one per storm) in the tmp_dir
        '''
        tmp_dir = self.config.getdir('TMP_DIR')
        processed_file = False
        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # /tmp/<pid> directory.
        for cur_storm in sorted_storm_ids:
            storm_output_dir = os.path.join(self.c_dict['OUTPUT_DIR'],
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
                                             cur_storm, self.c_dict['OUTPUT_DIR'],
                                             self.config)

            # remove tmp file
            os.remove(full_tmp_filename)
            processed_file = True

        return processed_file
