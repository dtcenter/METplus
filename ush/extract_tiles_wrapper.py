#!/usr/bin/env python

"""
Program Name: ExtractTiles.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Extracts tiles to be used by series_analysis
History Log:  Initial version
Usage: ExtractTiles.py
Parameters: None
Input Files: tc_pairs data
Output Files: tiled grib2 files
Condition codes: 0 for success, 1 for failure

"""

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
        super().__init__(config, logger)
        met_install_dir = self.config.getdir('MET_INSTALL_DIR')
        self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'), 'bin/tc_pairs')
        self.app_name = os.path.basename(self.app_path)
        self.tc_pairs_dir = self.config.getdir('EXTRACT_TILES_PAIRS_INPUT_DIR')
        self.overwrite_flag = self.config.getbool('config',
                                              'EXTRACT_TILES_OVERWRITE_TRACK')
        self.addl_filter_opts = \
            self.config.getstr('config', 'EXTRACT_TILES_FILTER_OPTS')
        self.filtered_out_dir = self.config.getdir('EXTRACT_TILES_OUTPUT_DIR')
        self.tc_stat_exe = os.path.join(met_install_dir, 'bin/tc_stat')

    def run_at_time(self, input_dict):
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
        time_info = time_util.ti_calculate(input_dict)
        init_time = time_info['init_fmt']

        # Set the tmp dir where intermediate files (that
        # are used for filtering) will be saved.
        tmp_dir = self.config.getdir('TMP_DIR')
        self.logger.info("Begin extract tiles")

        cur_init = init_time[0:8]+"_"+init_time[8:10]

        # Check that there are tc_pairs data files (.tcst) which are needed as input
        # to the extract tiles wrapper
        tc_pairs_nc_output_regex = ".*.tcst"
        output_files_list = util.get_files(self.tc_pairs_dir, tc_pairs_nc_output_regex, self.logger)
        if len(output_files_list) == 0:
            self.log_error("No tc pairs data found at {}"\
                              .format(self.tc_pairs_dir))
            sys.exit(1)

        # Create the name of the filter file we need to find.  If
        # the file doesn't exist, then run TC_STAT
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(self.filtered_out_dir, cur_init,
                                   filter_filename)

        if util.file_exists(filter_name) and not self.overwrite_flag:
            self.logger.debug("Filter file exists, using Track data file: {}"\
                              .format(filter_name))
        else:
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

        # Now get unique storm ids from the filter file,
        # filter_yyyymmdd_hh.tcst
        sorted_storm_ids = util.get_storm_ids(filter_name, self.logger)

        # Check for empty sorted_storm_ids, if empty,
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
        # /tmp/<pid> directory.
        for cur_storm in sorted_storm_ids:
            storm_output_dir = os.path.join(self.filtered_out_dir,
                                            cur_init, cur_storm)
            header = open(filter_name, "r").readline()
            util.mkdir_p(storm_output_dir)
            util.mkdir_p(tmp_dir)
            tmp_filename = "filter_" + cur_init + "_" + cur_storm
            full_tmp_filename = os.path.join(tmp_dir, tmp_filename)

            # If this full_tmp_filename already exists for this storm
            # (from a previous run), then remove it.  Otherwise the file
            # will continue to be appended with the same information.
            # This in turn will lead to errors when this file is being read/parsed.
            if os.path.exists(full_tmp_filename):
                os.remove(full_tmp_filename)
            storm_match_list = util.grep(cur_storm, filter_name)
            with open(full_tmp_filename, "a+") as tmp_file:
                # copy over header information
                tmp_file.write(header)
                for storm_match in storm_match_list:
                    tmp_file.write(storm_match)

            # Perform regridding of the forecast and analysis files
            # to an n X n degree tile centered on the storm (dimensions
            # are indicated in the config/param file).
            feature_util.retrieve_and_regrid(full_tmp_filename, cur_init,
                                             cur_storm, self.filtered_out_dir,
                                             self.config)

        # end of for cur_storm

        # Remove any empty files and directories in the extract_tiles output
        # directory
        util.prune_empty(self.filtered_out_dir, self.logger)

        # Clean up the tmp directory if it exists
        if os.path.isdir(tmp_dir):
            util.rmtree(tmp_dir)


if __name__ == "__main__":
    util.run_stand_alone("extract_tiles_wrapper", "ExtractTiles")
