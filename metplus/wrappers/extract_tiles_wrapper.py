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

        # get TCStat data dir/template to read
        # stat input directory is optional because the whole path can be
        # defined in the template
        c_dict['STAT_INPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_STAT_INPUT_DIR', '')
        )

        c_dict['STAT_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'EXTRACT_TILES_STAT_INPUT_TEMPLATE',
                               '')
        )
        if not c_dict['STAT_INPUT_TEMPLATE']:
            self.log_error('Must set EXTRACT_TILES_STAT_INPUT_TEMPLATE '
                           'to run ExtractTiles wrapper')

        # get gridded input directory to read
        # TODO: change this to read FCST/OBS INPUT DIRS!
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

        # Create the name of the filter file to use
        filter_filename = (
            do_string_sub(self.c_dict['STAT_INPUT_TEMPLATE'],
                          **time_info)
        )
        filter_path = os.path.join(self.c_dict['STAT_INPUT_DIR'],
                                   filter_filename)

        self.logger.debug(f"Looking for input stat file: {filter_path}")
        if not os.path.exists(filter_path):
            self.log_error(f"Could not find input stat file: {filter_path}")
            return

        # Now get unique storm ids from the filter file
        sorted_storm_ids = util.get_storm_ids(filter_path)

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
                                         filter_path):
            self.log_error("There was a problem with processing storms from the filtered result, "\
                    "please check your METplus config file settings or your write permissions for your "\
                    "tmp directory.")

        util.prune_empty(self.c_dict['OUTPUT_DIR'], self.logger)

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
