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
import produtil.setup
import met_util as util
from tc_stat_wrapper import TcStatWrapper

##@namespace ExtractTiles
# @brief Runs  Extracts tiles to be used by series_analysis.
# Call as follows:
# @code{.sh}
# extract_tiles.py [-c /path/to/user.template.conf]
# @endcode
#


class ExtractTiles(object):
    """! Takes tc-pairs data and regrids paired data to an nxm grid as
         specified in the config file.
    """

    # pylint: disable=too-many-instance-attributes
    # Eleven is needed in this case.
    # pylint: disable=too-few-public-methods
    # Much of the data in the class are used to perform tasks, rather than
    # having methods operating on them.

    def __init__(self, conf_instance):
        self.tc_pairs_dir = conf_instance.getdir('TC_PAIRS_DIR')
        self.overwrite_flag = conf_instance.getbool('config',
                                                    'OVERWRITE_TRACK')
        self.addl_filter_opts =\
            conf_instance.getstr('config', 'EXTRACT_TILES_FILTER_OPTS')
        self.filtered_out_dir = conf_instance.getdir('EXTRACT_OUT_DIR')
        self.tc_stat_exe = conf_instance.getexe('TC_STAT')
        self.init_date_beg = conf_instance.getstr('config', 'INIT_DATE_BEG')
        self.init_date_end = conf_instance.getstr('config', 'INIT_DATE_END')
        self.init_hour_inc = conf_instance.getint('config', 'INIT_HOUR_INC')
        self.init_hour_end = conf_instance.getstr('config', 'INIT_HOUR_END')
        self.logger = util.get_logger(conf_instance)
        self.config = conf_instance

    # pylint: disable=too-many-locals
    # 23 local variables are needed to perform the necessary work.
    def main(self):
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
        init_times = util.gen_init_list(self.init_date_beg,
                                        self.init_date_end,
                                        self.init_hour_inc,
                                        self.init_hour_end)

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
        for cur_init in init_times:
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
                continue

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
                print("full_tmp_filename: {}".format(full_tmp_filename))

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
        # end of for cur_init

        # Remove any empty files and directories in the extract_tiles output
        # directory
        util.prune_empty(self.filtered_out_dir, self.logger)

        # Clean up the tmp directory
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
        import config_launcher
        if len(sys.argv) == 3:
            CONFIG_INST = config_launcher.load_baseconfs(sys.argv[2])
        else:
            CONFIG_INST = config_launcher.load_baseconfs()
        LOGGER = util.get_logger(CONFIG_INST)
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        ET = ExtractTiles(CONFIG_INST)
        ET.main()
        produtil.log.postmsg('extract_tiles completed')
    except Exception as exception:
        produtil.log.jlogger.critical(
            'extract_tiles failed: %s' % (str(exception),), exc_info=True)
        sys.exit(2)
