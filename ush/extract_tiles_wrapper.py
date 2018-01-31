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

from __future__ import (print_function, division)

import os
import sys
import datetime
import produtil.setup
from command_builder import CommandBuilder
import met_util as util
import config_metplus
from tc_stat_wrapper import TcStatWrapper

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

    def __init__(self, p, logger):
        super(ExtractTilesWrapper, self).__init__(p, logger)
        met_install_dir = p.getdir('MET_INSTALL_DIR')
        self.app_path = os.path.join(p.getdir('MET_INSTALL_DIR'), 'bin/tc_pairs')
        self.app_name = os.path.basename(self.app_path)
        self.tc_pairs_dir = self.p.getdir('TC_PAIRS_DIR')
        self.overwrite_flag = self.p.getbool('config',
                                             'OVERWRITE_TRACK')
        self.addl_filter_opts = \
            self.p.getstr('config', 'EXTRACT_TILES_FILTER_OPTS')
        self.filtered_out_dir = self.p.getdir('EXTRACT_OUT_DIR')
        self.tc_stat_exe = os.path.join(met_install_dir, 'bin/tc_stat')
        self.init_beg = self.p.getstr('config', 'INIT_BEG')[0:8]
        self.init_end = self.p.getstr('config', 'INIT_END')[0:8]
        self.init_hour_inc = int(self.p.getint('config', 'INIT_INC') / 3600)
        self.init_hour_end = self.p.getint('config', 'INIT_HOUR_END')
        if self.logger is None:
            self.logger = util.get_logger(self.p)
        self.config = self.p

    # pylint: disable=too-many-locals
    # 23 local variables are needed to perform the necessary work.
    def run_all_times(self):
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        init_time = datetime.datetime.strptime(self.init_beg, "%Y%m%d")
        end_time = datetime.datetime.strptime(self.init_end, "%Y%m%d")
        end_time = end_time + datetime.timedelta(hours=self.init_hour_end)

        # This is functionally equivalent to while loop below.
        # Get the desired YYYYMMDD_HH init increment list
        # init_list = util.gen_init_list(
        #    self.init_beg, self.init_end, self.init_hour_inc,
        #    str(self.init_hour_end))
        # while init_time in init_list
        #     self.run_at_time(init_time)

        # Loop from begYYYYMMDD to endYYYYMMDD incrementing by HH
        # and ending on the endYYYYMMDD_HH End Hour.
        while init_time <= end_time:
            self.run_at_time(init_time.strftime("%Y%m%d_%H"))
            init_time = init_time + datetime.timedelta(
                hours=self.init_hour_inc)

        # Remove any empty files and directories in the extract_tiles output
        # directory
        util.prune_empty(self.filtered_out_dir, self.logger)

        msg = ("INFO|[" + cur_function + ":" + cur_filename +
               "] | Finished extract tiles")
        self.logger.info(msg)

    def run_at_time(self, cur_init):
        """!Get TC-paris data then regrid tiles centered on the storm.

        Get TC-pairs track data and GFS model data, do any necessary
        processing then regrid the forecast and analysis files to a
        30 x 30 degree tile centered on the storm.
        Args:

        Returns:

            None: invokes regrid_data_plane to create a netCDF file from two
                    extratropical storm track files.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        # Used in logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # get the process id to be used to identify the output
        # amongst different users and runs.
        cur_pid = str(os.getpid())
        tmp_dir = os.path.join(self.config.getdir('TMP_DIR'), cur_pid)
        msg = ("INFO|[" + cur_filename + ":" + cur_function + "]"
               "|Begin extract tiles")
        self.logger.info(msg)

        # Check that there are tc_pairs data which are used as input
        if util.is_dir_empty(self.tc_pairs_dir):
            msg = ("ERROR|[" + cur_filename + ":" + cur_function + "]"
                   "|No tc pairs data found at " + self.tc_pairs_dir +
                   "Exiting...")
            self.logger.error(msg)
            sys.exit(1)

        # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
        # [File : function]| Message logger.info("INFO |  [" +
        # cur_filename +  ":" + "cur_function] |" + "BEGIN extract_tiles")
        # Process TC pairs by initialization time
        # Begin processing for initialization time, cur_init
        year_month = util.extract_year_month(cur_init, self.logger)

        # Create the name of the filter file we need to find.  If
        # the file doesn't exist, then run TC_STAT
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(self.filtered_out_dir, cur_init,
                                   filter_filename)

        if util.file_exists(filter_name) and not self.overwrite_flag:
            msg = ("DEBUG| [" + cur_filename + ":" + cur_function +
                   " ] | Filter file exists, using Track data file: " +
                   filter_name)
            self.logger.debug(msg)
        else:
            # Create the storm track by applying the
            # filter options defined in the config/param file.
            tile_dir_parts = [self.tc_pairs_dir, "/", year_month]
            tile_dir = ''.join(tile_dir_parts)
            # Use TcStatWrapper to build up the tc_stat command and invoke
            # the MET tool tc_stat to perform the filtering.
            tcs = TcStatWrapper(self.config)
            tcs.build_tc_stat(self.filtered_out_dir, cur_init,
                              tile_dir, self.addl_filter_opts)

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
            msg = ("DEBUG|[" + cur_filename + ":" + cur_function + " ]|" +
                   "No storms were found for " + cur_init +
                   "...continue to next in list")
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

            storm_match_list = util.grep(cur_storm, filter_name)
            with open(full_tmp_filename, "a+") as tmp_file:
                # copy over header information
                tmp_file.write(header)
                for storm_match in storm_match_list:
                    tmp_file.write(storm_match)

            # Perform regridding of the forecast and analysis files
            # to an n X n degree tile centered on the storm (dimensions
            # are indicated in the config/param file).
            util.retrieve_and_regrid(full_tmp_filename, cur_init,
                                     cur_storm, self.filtered_out_dir,
                                     self.logger, self.config)

        # end of for cur_storm

        # Remove any empty files and directories in the extract_tiles output
        # directory
        util.prune_empty(self.filtered_out_dir, self.logger)

        # Clean up the tmp directory if it exists
        if os.path.isdir(tmp_dir):
            util.rmtree(tmp_dir)
            msg = ("INFO|[" + cur_function + ":" + cur_filename + "]"
                   "| Finished extract tiles")
            self.logger.info(msg)


if __name__ == "__main__":

    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='extract_tiles',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='extract_tiles')
        produtil.log.postmsg('extract_tiles is starting')

        # Read in the configuration object CONFIG_INST
        CONFIG_INST = config_metplus.setup()
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        ET = ExtractTilesWrapper(CONFIG_INST, logger=None)
        ET.run_all_times()
        produtil.log.postmsg('extract_tiles completed')
    except Exception as exception:
        produtil.log.jlogger.critical(
            'extract_tiles failed: %s' % (str(exception),), exc_info=True)
        sys.exit(2)
