#!/usr/bin/env python

"""
Program Name: extract_tiles.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Extracts tiles to be used by series_analysis
History Log: Initial version
Usage: extract_tiles.py
Parameters: None
Input Files: tc_pairs data
Output Files: tiled grib2 files
Condition codes: 0 for success, 1 for failure

"""

from __future__ import (print_function, division)

import produtil.setup
import os
import sys
import met_util as util
import run_tc_stat as tcs


"""!@namespace extract_tiles
 @brief Runs  Extracts tiles to be used by series_analysis.
 Call as follows:
 @code{.sh}
 extract_tils.py [-c /path/to/user.template.conf]
 @endcode
"""


def main():
    """! Get TC-paris data than regrid tiles centered on the storm.

    Get TC-pairs track data and GFS model data, do any necessary
    processing then regrid the forecast and analysis files to a
    30 x 30 degree tile centered on the storm.
       Args:

       Returns:

           None: invokes regrid_data_plane to create a netCDF file from two
                 extratropical storm track files.
    """

    # Retrieve parameters from corresponding param file

    # produtil.log.postmsg('Example postmsg, convenience function for
    # jlogger.info')

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    init_times = util.gen_init_list(p.getstr('config', 'INIT_DATE_BEG'),
                                    p.getstr('config', 'INIT_DATE_END'),
                                    p.getint('config', 'INIT_HOUR_INC'),
                                    p.getstr('config', 'INIT_HOUR_END'))
    tc_pairs_dir = p.getdir('TC_PAIRS_DIR')
    overwrite_flag = p.getbool('config', 'OVERWRITE_TRACK')
    addl_filter_opts = p.getstr('config', 'EXTRACT_TILES_FILTER_OPTS')
    filtered_out_dir = p.getdir('EXTRACT_OUT_DIR')
    tc_stat_exe = p.getexe('TC_STAT')

    # get the process id to be used to identify the output
    # amongst different users and runs.
    cur_pid = str(os.getpid())
    tmp_dir = os.path.join(p.getdir('TMP_DIR'), cur_pid)
    msg = ("INFO|[" + cur_filename + ":" + cur_function +
           "]|Begin extract tiles")
    logger.info(msg)

    # Check that there are tc_pairs data which is used as input
    if util.is_dir_empty(tc_pairs_dir):
        msg = ("ERROR|[" + cur_filename + ":" + cur_function +
               "]|No tc pairs data found at " + tc_pairs_dir + "Exiting...")
        logger.error(msg)
        sys.exit(1)

    # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
    # [File : function]| Message logger.info("INFO |  [" +
    # cur_filename +  ":" + "cur_function] |" + "BEGIN extract_tiles")
    # Process TC pairs by initialization time
    for cur_init in init_times:
        # Begin processing for initialization time, cur_init
        year_month = util.extract_year_month(cur_init, logger)

        # Create the name of the filter file we need to find.  If
        # the file doesn't exist, then run TC_STAT
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(filtered_out_dir, cur_init, filter_filename)
        if util.file_exists(filter_name) and not overwrite_flag:
            msg = ("DEBUG| [" + cur_filename + ":" + cur_function +
                   " ] | Filter file exists, using Track data file: " +
                   filter_name)
            logger.debug(msg)
        else:
            # Create the storm track by applying the
            # filter options defined in the constants_pdef.py file.
            filter_path = os.path.join(filtered_out_dir, cur_init)
            util.mkdir_p(filter_path)
            tc_cmd_list = [tc_stat_exe, " -job filter -lookin ",
                           tc_pairs_dir, "/", year_month,
                           " -init_inc ", cur_init,
                           " -match_points true -dump_row ",
                           filter_name, " ", addl_filter_opts]

            # Call run_tc_stat to do the actual filtering.
            tc_cmd = ''.join(tc_cmd_list)
            logger.debug("DEBUG|tc_cmd: " + tc_cmd)
            tcs.tc_stat(p, logger, tc_cmd,
                        filtered_out_dir)

            # Remove any empty files and directories that can occur
            # from filtering.
            util.prune_empty(filter_name, p, logger)
        # Now get unique storm ids from the filter file,
        # filter_yyyymmdd_hh.tcst
        sorted_storm_ids = util.get_storm_ids(filter_name, logger)
        # Check for empty sorted_storm_ids, if empty,
        # continue to the next time.
        if len(sorted_storm_ids) == 0:
            # No storms found for init time, cur_init
            msg = ("DEBUG|[" + cur_filename + ":" + cur_function + " ]|" +
                   "No storms were found for " + cur_init +
                   "...continue to next in list")
            logger.debug(msg)
            continue

        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # /tmp/<pid> directory.
        for cur_storm in sorted_storm_ids:
            storm_output_dir = os.path.join(filtered_out_dir, cur_init,
                                            cur_storm)
            header = open(filter_name, "r").readline()
            util.mkdir_p(storm_output_dir)
            util.mkdir_p(tmp_dir)
            tmp_file = "filter_" + cur_init + "_" + cur_storm
            tmp_filename = os.path.join(tmp_dir, tmp_file)

            storm_match_list = util.grep(cur_storm, filter_name)
            with open(tmp_filename, "a+") as tmp_file:
                # copy over header information
                tmp_file.write(header)
                for storm_match in storm_match_list:
                    tmp_file.write(storm_match)

            # Perform regridding of the forecast and analysis files
            # to a 30 x 30 degree tile centered on the storm
            util.retrieve_and_regrid(tmp_filename, cur_init,
                                     cur_storm, filtered_out_dir,
                                     logger, p)

        # end of for cur_storm
    # end of for cur_init

    # Remove any empty files and directories in the extract_tiles
    #  output directory
    util.prune_empty(filtered_out_dir, p, logger)

    # Clean up the tmp directory
    # subprocess.call(["rm", "-rf", tmp_dir])
    util.rmtree(tmp_dir)
    msg = ("INFO|[" + cur_function + ":" + cur_filename +
           "]| Finished extract tiles")
    logger.info(msg)

if __name__ == "__main__":

    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='extract_tiles',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='extract_tiles')
        produtil.log.postmsg('extract_tiles is starting')

        # Read in the configuration object p
        import config_launcher
        if len(sys.argv) == 3:
            p = config_launcher.load_baseconfs(sys.argv[2])
        else:
            p = config_launcher.load_baseconfs()
        logger = util.get_logger(p)
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = p.getdir('MET_BASE')
        main()
        produtil.log.postmsg('extract_tiles completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'extract_tiles failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
