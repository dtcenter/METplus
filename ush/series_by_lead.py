#!/usr/bin/env python
from __future__ import print_function

import produtil.setup
from produtil.run import batchexe, run, checkrun
import re
import os
import sys
import met_util as util


def analysis_by_lead_time():
    ''' Perform a series analysis of extra tropical cyclone
        paired data based on lead time (forecast hour) 
        This requires invoking the MET run_series_analysis binary,
        followed by generating graphics that are recognized by 
        the MET viewer using the plot_data_plane and convert.  
        A pre-requisite is the presence of the filter file and storm files
        (currently 30 x 30 degree tiles) for the specified init and lead times.
   

       Invoke the series_analysis script based on lead time (forecast hour) 
       Create the command:
         series_analysis -fcst <FILTERED_OUT_DIR>/FCST_FILES_F<CUR_FHR>
                         -obs <FILTERED_OUT_DIR>/ANLY_FILES_F<CUR_FHR>
                         -out <OUT_DIR>/series_F<CURR_FHR_<NAME>_<LEVEL>.nc 
                         -config SeriesAnalysisConfig_by_lead
      Args:
        None


      Returns:
        None:       Creates graphics plots for files corresponding to each
                    forecast lead time.


    '''

    # produtil.log.postmsg('Example postmsg, convenience function for jlogger.info')

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Flag used to determine whether to use the forecast hour range and increment, or the
    # specified list of forecast hours in creating the Series-analysis command.
    # Support for GitHub Issue #3
    fhr_by_range = True

    # Retrieve any necessary values from the parm file(s)
    fhr_beg = p.getint('config', 'FHR_BEG')
    fhr_end = p.getint('config', 'FHR_END')
    fhr_inc = p.getint('config', 'FHR_INC')
    var_list = util.getlist(p.getstr('config', 'VAR_LIST'))
    stat_list = util.getlist(p.getstr('config', 'STAT_LIST'))
    plot_data_plane_exe = p.getexe('PLOT_DATA_PLANE')
    convert_exe = p.getexe('CONVERT_EXE')
    extract_tiles_dir = p.getdir('EXTRACT_OUT_DIR')
    series_lead_filtered_out_dir = p.getdir('SERIES_LEAD_FILTERED_OUT_DIR')
    series_lead_out_dir = p.getdir('SERIES_LEAD_OUT_DIR')
    background_map = p.getbool('config','BACKGROUND_MAP')
    regrid_with_MET_tool = p.getbool('config','REGRID_USING_MET_TOOL')
    series_filter_opts = p.getstr('config','SERIES_ANALYSIS_FILTER_OPTS')
    series_filter_opts.strip()

    # GitHub Issue #3 support
    fhr_of_interest = util.getlist(p.getstr('config', 'FHR_OF_INTEREST'))
    if len(fhr_of_interest) > 0:
        fhr_by_range = False

    # Set up the environment variable to be used in the Series Analysis
    #   Config file (SERIES_ANALYSIS_BY_LEAD_CONFIG_PATH)
    # Used to set cnt  value in output_stats in "SERIES_ANALYSIS_BY_LEAD_CONFIG_PATH"
    # Need to do some pre-processing so that Python will use " and not '
    #  because currently MET doesn't support single-quotes
    tmp_stat_string = str(stat_list)
    tmp_stat_string = tmp_stat_string.replace("\'", "\"")
    # For example, we want tmp_stat_string to look like
    #   '["TOTAL","FBAR"]', NOT "['TOTAL','FBAR']"
    os.environ['STAT_LIST'] = tmp_stat_string

    if regrid_with_MET_tool:
        # Regridding via MET Tool regrid_data_plane.
        fcst_tile_regex = p.getstr('regex_pattern','FCST_NC_TILE_REGEX')
        anly_tile_regex = p.getstr('regex_pattern','ANLY_NC_TILE_REGEX')
    else:
        # Regridding via wgrib2 tool.
        fcst_tile_regex = p.getstr('regex_pattern','FCST_TILE_REGEX')
        anly_tile_regex = p.getstr('regex_pattern','ANLY_TILE_REGEX')

    # Check for the existence of the storm track tiles and raise
    # an error if these are missing.
    # Get a list of the grb2 forecast tiles in 
    # <project dir>/series_analysis/*/*/FCST_TILE_F<cur_fhr>.grb2
    logger.info("Begin series analysis by lead...")
    # Initialize the tile_dir to the extract tiles output directory.
    # And retrieve a list of init times based on the data available in
    # the extract tiles directory.
    tile_dir = extract_tiles_dir
    init_times = util.get_updated_init_times(tile_dir, p, logger)
    
    try:
        util.check_for_tiles(tile_dir, fcst_tile_regex, anly_tile_regex, logger)
    except OSError as e:
        msg = ("ERROR|[ " + cur_filename + ":" +
               cur_function + "]| Missing 30x30 tile files." +
               "  Extract tiles needs to be run")
        logger.error(msg)

    # Apply optional filtering via tc_stat, as indicated in the
    # constants_pdef.py parameter/config file.
    if series_filter_opts:
        util.mkdir_p(series_lead_filtered_out_dir)
        util.apply_series_filters(tile_dir, init_times, series_lead_filtered_out_dir, p, logger)

        # Remove any empty files and directories to avoid
        # errors or performance degradation when performing
        # series analysis.
        util.prune_empty(series_lead_filtered_out_dir, p, logger)

        # Get the list of all the files that were created as a result
        # of applying the filter options.  Save this information, it
        # will be useful for troubleshooting and validating the correctness
        # of filtering.

        # First, make sure that the series_lead_filtered_out directory isn't
        # empty.  If so, then no files fall within the filter criteria.
        if os.listdir(series_lead_filtered_out_dir):
            # Filtering produces results, assign the tile_dir to
            # the filter output directory, series_lead_filtered_out_dir.
            filtered_files_list = util.get_files(tile_dir, ".*.", logger)
            tile_dir = series_lead_filtered_out_dir

            # Create the tmp_fcst and tmp_anly ASCII files containing the
            # list of files that meet the filter criteria.
            util.create_filter_tmp_files(filtered_files_list, series_lead_filtered_out_dir, p, logger)
            tile_dir = series_lead_filtered_out_dir
        else:
            # No data meet filter criteria, use data from extract tiles directory.
            msg = ("After applying filter options, no data meet filter criteria." +
                   "Continue using all available data in extract tiles directory.")
            logger.debug(msg)
            tile_dir = extract_tiles_dir

    else:
        # No additional filtering was requested.  The extract tiles directory is the
        # source of input tile data.
        tile_dir = extract_tiles_dir

    # Create the values for the -fcst, -obs, and other required
    # options for running the MET series_analysis binary.

    # GitHub issue #30
    # gracefully handle user's intent to process only one forecast hour (eg
    # FCST_INIT=FCST_END and FCST_INCR=0
    # If the user sets FCST_INCR=0 but has FCST_INIT != FCST_END, then
    # log an error and exit.
    fhr_diff = fhr_end - fhr_beg
    if fhr_diff == 0 and fhr_inc == 0:
        fhr_inc = 1
    elif fhr_inc == 0:
        logger.error('ERROR: fcst range indicated with increment of 0 hrs, please check the configuration file.'
                     '  Exiting...')
        sys.exit(1)
    # GitHub Issue #3 support:
    if fhr_by_range:
        start = fhr_beg
        end = fhr_end + 1
        step = fhr_inc
    else:
        start = 0
        end = len(fhr_of_interest)
        step = 1

    # Create the command for MET Series-analysis using either a list of specified forecast hours, or
    # a range of forecast hours with increment.
    if fhr_by_range:
        logger.debug("performing series analysis using range of fhrs...")
        perform_series_for_range(tile_dir, start, end, step, p, logger)
    else:
        # Perform "bucketed" series analysis (i.e. from user-defined list of forecast hours in the METplus config file)
        perform_series_for_bucket(tile_dir, start, end, p, logger)

    # Now create animation plots
    animate_dir = os.path.join(series_lead_out_dir, 'series_animate')
    msg = ('INFO|[' + cur_filename + ':' + cur_function +
           ']| Creating Animation Plots, create directory:' +
           animate_dir)
    logger.debug(msg)
    util.mkdir_p(animate_dir)

    # Generate a plot for each variable, statistic, and lead time.
    # First, retrieve all the netCDF files that were generated 
    # above by the run series analysis.
    logger.info('GENERATING PLOTS...')

    # Retrieve a list of all the netCDF files generated by 
    # MET Tool series analysis.
    nc_list = retrieve_nc_files(fhr_by_range, series_lead_out_dir, logger)

    # Check that we have netCDF files, if not, something went
    # wrong.
    if len(nc_list) == 0:
        logger.error("ERROR|" + cur_filename + ":" + cur_function +
                     "]|  could not find any netCDF files to convert to PS and PNG. "+
                     "Exiting...")
        sys.exit(1)
    else:
        msg = ("INFO|[" + cur_filename + ":" + cur_function +
               " Number of nc files found to convert to PS and PNG  : " +
               str(len(nc_list)))
        logger.debug(msg)

    for cur_var in var_list:
        # Get the name and level to set the NAME and LEVEL
        # environment variables that
        # are needed by the MET series analysis binary.
        match = re.match(r'(.*)/(.*)', cur_var)
        name = match.group(1)
        level = match.group(2)

        os.environ['NAME'] = name
        os.environ['LEVEL'] = level

        if regrid_with_MET_tool:
            os.environ['NAME'] = name + '_' + level

        # Retrieve only those netCDF files that correspond to
        # the current variable.
        nc_var_list = get_var_ncfiles(fhr_by_range, name, nc_list, logger)
        if len(nc_var_list) == 0:
            logger.debug("WARNING nc_var_list is empty for " + name + "_" + level + ", check for next variable...")
            continue

        # Iterate over the statistics, setting the CUR_STAT
        # environment variable...
        for cur_stat in stat_list:
            # Set environment variable required by MET
            # application Plot_Data_Plane.
            os.environ['CUR_STAT'] = cur_stat
            vmin, vmax = get_netcdf_min_max(fhr_by_range, nc_var_list, cur_stat, p, logger)
            msg = ("|INFO|[ " + cur_filename + ":" + cur_function +
                   "]| Plotting range for " + cur_var + " " +
                   cur_stat + ":  " + str(vmin) + " to " + str(vmax))
            logger.debug(msg)

            # Plot the output for each time
            # DEBUG
            logger.info("Create PS and PNG")
            for cur_nc in nc_var_list:
                # The postscript files are derived from
                # each netCDF file. The postscript filename is
                # created by replacing the '.nc' extension
                # with '_<cur_stat>.ps'. The png file is created
                # by replacing the '.ps'
                # extension of the postscript file with '.png'.
                repl_string = ['_', cur_stat, '.ps']
                repl = ''.join(repl_string)
                ps_file = re.sub('(\.nc)$', repl, cur_nc)

                # Now create the PNG filename from the
                # Postscript filename.
                png_file = re.sub('(\.ps)$', '.png', ps_file)

                # Extract the forecast hour from the netCDF
                # filename.
                if fhr_by_range:
                    match_fhr = re.match(
                        r'.*/series_F\d{3}/series_F(\d{3}).*\.nc', cur_nc)
                else:
                    match_fhr = re.match(
                        r'.*/series_F\d{3}_to_F\d{3}/series_F(\d{3})_to_F(\d{3}).*\.nc', cur_nc)

                if match_fhr:
                    fhr = match_fhr.group(1)
                else:
                    msg = ("WARNING: netCDF file format is " +
                           "unexpected. Try next file in list...")
                    logger.debug(msg)
                    continue

                # Get the max series_cnt_TOTAL value (i.e. nseries)
                nseries = get_nseries(fhr_by_range, cur_nc, p, logger)

                # Create the plot data plane command based on whether 
                # the background map was requested in the
                # constants_pdef.py param/config file.
                if background_map:
                    # Flag set to True, print background map.
                    map_data = ''
                else:
                    map_data = "map_data={source=[];}  "

                plot_data_plane_parts = [plot_data_plane_exe, ' ',
                                         cur_nc, ' ', ps_file, ' ',
                                         "'", 'name = ', '"',
                                         'series_cnt_', cur_stat, '";',
                                         'level=', '"(\*,\*)"; ',
                                         ' ', map_data,
                                         "'", ' -title ', '"GFS F',
                                         str(fhr),
                                         ' Forecasts (N = ', str(nseries),
                                         '), ', cur_stat, ' for ', cur_var,
                                         '"', ' -plot_range ', str(vmin),
                                         ' ', str(vmax)]

                plot_data_plane_cmd = ''.join(plot_data_plane_parts)
                plot_data_plane_cmd = batchexe('sh')['-c',plot_data_plane_cmd].err2out()
                #plot_data_plane_cmd = batchexe(plot_data_plane_cmd.split()[0])[plot_data_plane_cmd.split()[1:]].err2out()
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "]| plot_data_plane cmd: " +
                       plot_data_plane_cmd.to_shell())
                logger.debug(msg)
                plot_out = run(plot_data_plane_cmd)
                #plot_out = subprocess.check_output(plot_data_plane_cmd,
                #                                   stderr=subprocess.STDOUT,
                #                                   shell=True)

                # Create the convert command.
                convert_parts = [convert_exe, ' -rotate 90 ',
                                 ' -background white -flatten ',
                                 ps_file, ' ', png_file]
                convert_cmd = ''.join(convert_parts)
                convert_cmd = batchexe('sh')['-c',convert_cmd].err2out()
                #convert_cmd = batchexe(convert_cmd.split()[0])[convert_cmd.split()[1:]].err2out()
                convert_out = run(convert_cmd)
                #convert_out = subprocess.check_output(convert_cmd,
                #                                      stderr=
                #                                      subprocess.STDOUT,
                #                                      shell=True)

            # Create animated gif
            logger.info("Creating animated gifs")
            if fhr_by_range:
                series_dir = '/series_F*'
                series_fname_root = '/series_F*'
            else:
                series_dir = '/series_F*_to_F*'
                series_fname_root = '/series_F*_to_F*'
            gif_parts = [convert_exe,
                         ' -dispose Background -delay 100 ',
                         series_lead_out_dir, '/series_F*',
                         '/series_F*', '_', name, '_',
                         level, '_', cur_stat, '.png', '  ',
                         animate_dir, '/series_animate_', name, '_',
                         level, '_', cur_stat, '.gif']
            animate_cmd = ''.join(gif_parts)
            animate_cmd = batchexe('sh')['-c',animate_cmd].err2out()
            #animate_cmd = batchexe(animate_cmd.split()[0])[animate_cmd.split()[1:]].err2out()
            msg = ("INFO|[" + cur_filename + ":" + cur_function +
                   "]| animate command: " + animate_cmd.to_shell())
            logger.debug(msg)
            animate_out = run(animate_cmd)
            #animate_out = subprocess.check_output(animate_cmd,
            #                                      stderr=subprocess.STDOUT,
            #                                      shell=True)

    logger.info("Finished with series analysis by lead")


def perform_series_for_bucket(tile_dir, start, end, p, logger):
    # Used for logging.
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Retrieve necessary information from the config file.
    series_analysis_exe = p.getexe('SERIES_ANALYSIS')
    series_anly_configuration_file = p.getstr('config', 'SERIES_ANALYSIS_BY_LEAD_CONFIG_PATH')
    fhr_of_interest = util.getlist(p.getstr('config', 'FHR_OF_INTEREST'))

    series_lead_out_dir = p.getdir('SERIES_LEAD_OUT_DIR')
    var_list = util.getlist(p.getstr('config', 'VAR_LIST'))
    regrid_with_MET_tool = p.getbool('config', 'REGRID_USING_MET_TOOL')

    if regrid_with_MET_tool:
        # Regridding via MET Tool regrid_data_plane.
        fcst_tile_regex = p.getstr('regex_pattern', 'FCST_NC_TILE_REGEX')
        anly_tile_regex = p.getstr('regex_pattern', 'ANLY_NC_TILE_REGEX')
    else:
        # Regridding via wgrib2 tool.
        fcst_tile_regex = p.getstr('regex_pattern', 'FCST_TILE_REGEX')
        anly_tile_regex = p.getstr('regex_pattern', 'ANLY_TILE_REGEX')

    fcst_tiles_list = []
    anly_tiles_list = []
    fhr_bucket = str(start).zfill(3) + "_to_F" + str(fhr_of_interest[end-1]).zfill(3)

    # Create the output directory which will hold the series analysis results.
    util.mkdir_p(series_lead_out_dir)
    out_dir_parts = [series_lead_out_dir, '/', 'series_F', fhr_bucket]
    out_dir = ''.join(out_dir_parts)
    util.mkdir_p(out_dir)

    logger.debug("Performing series analysis on bucket of forecast hours...")
    for fhr in range(start, end):
        cur_fhr = str(fhr_of_interest[fhr]).zfill(3)
        msg = ('INFO|[' + cur_filename + ':' + cur_function +
               ']| Evaluating forecast hour ' + cur_fhr)
        logger.debug(msg)

        # Gather all the forecast gridded tile files
        # so they can be saved in ASCII files.
        cur_fcst_tiles_list = get_anly_or_fcst_files(tile_dir, "FCST", fcst_tile_regex,
                                                     cur_fhr, logger)
        cur_fcst_tiles = retrieve_fhr_tiles(cur_fcst_tiles_list, 'FCST', out_dir,
                                            cur_fhr, fcst_tile_regex, logger)

        # Location of FCST_FILES_Fhhh
        ascii_fcst_file_parts = [out_dir, '/FCST_FILES_F', fhr_bucket]
        ascii_fcst_file = ''.join(ascii_fcst_file_parts)

        fcst_tiles_list.append(cur_fcst_tiles)

        # Gather all the anly gridded tile files
        # so they can be saved in ASCII files.
        cur_anly_tiles_list = get_anly_or_fcst_files(tile_dir, "ANLY", anly_tile_regex,
                                                     cur_fhr, logger)
        cur_anly_tiles = retrieve_fhr_tiles(cur_anly_tiles_list, 'ANLY', out_dir,
                                            cur_fhr, anly_tile_regex, logger)

        # Location of ANLY_FILES_Fhhh files
        # filtering.
        ascii_anly_file_parts = [out_dir, '/ANLY_FILES_F', fhr_bucket]
        ascii_anly_file = ''.join(ascii_anly_file_parts)

        anly_tiles_list.append(cur_anly_tiles)

    # Now create the ASCII files needed for the -fcst and -obs
    try:
        if len(fcst_tiles_list) == 0:
            msg = ("INFO|[" + cur_filename + ":" +
                   cur_function + " No fcst_tiles for fhr bucket: " + str(start) + " to " + str(end) +
                   " Don't create FCST_F<fhr> ASCII file")
            logger.debug(msg)
        else:
            with open(ascii_fcst_file, 'a') as f:
                for fcst_tiles in fcst_tiles_list:
                    f.write(fcst_tiles)

    except IOError as e:
        msg = ("ERROR: Could not create requested" +
               " ASCII file: " + ascii_fcst_file)
        logger.error(msg)

    try:
        # Only write to the ascii_anly_file if
        # the anly_tiles string isn't empty.
        if len(anly_tiles_list) == 0:
            msg = ("INFO|[" + cur_filename + ":" +
                   cur_function + "No anly_tiles for fhr: " + fhr_bucket +
                   " Don't create ANLY_F<fhr> ASCII file")
            logger.debug(msg)
        else:
            with open(ascii_anly_file, 'a') as f:
                for anly_tiles in anly_tiles_list:
                    f.write(anly_tiles)

    except IOError as e:
        logger.error("ERROR: Could not create requested " +
                     "ASCII file: " + ascii_anly_file)

    # Remove any empty directories that result from
    # when no files are written.
    util.prune_empty(out_dir, p, logger)

    # -fcst and -obs params
    fcst_param_parts = ['-fcst ', ascii_fcst_file]
    fcst_param = ''.join(fcst_param_parts)
    obs_param_parts = ['-obs ', ascii_anly_file]
    obs_param = ''.join(obs_param_parts)
    logger.debug('fcst param: ' + fcst_param)
    logger.debug('obs param: ' + obs_param)

    # Create the -out param and invoke the MET series
    # analysis binary
    for cur_var in var_list:
        # Get the name and level to create the -out param
        # and set the NAME and LEVEL environment variables that
        # are needed by the MET series analysis binary.
        match = re.match(r'(.*)/(.*)', cur_var)
        name = match.group(1)
        level = match.group(2)
        os.environ['NAME'] = name
        os.environ['LEVEL'] = level

        # Set NAME to name_level if regridding with regrid data plane
        if regrid_with_MET_tool:
            os.environ['NAME'] = name + '_' + level
        out_param_parts = ['-out ', out_dir, '/series_F', fhr_bucket,
                           '_', name, '_', level, '.nc']
        out_param = ''.join(out_param_parts)

        # Create the full series analysis command.
        config_param_parts = ['-config ',
                              series_anly_configuration_file]
        config_param = ''.join(config_param_parts)
        series_analysis_cmd_parts = [series_analysis_exe, ' ',
                                     ' -v 4 ',
                                     fcst_param, ' ', obs_param,
                                     ' ', config_param, ' ',
                                     out_param]
        series_analysis_cmd = ''.join(series_analysis_cmd_parts)
        msg = ("INFO:[ " + cur_filename + ":" +
               cur_function + "]|series analysis command: " +
               series_analysis_cmd)
        logger.debug(msg)
        series_analysis_cmd = batchexe('sh')['-c', series_analysis_cmd].err2out()
        series_out = run(series_analysis_cmd)

        # Make sure there aren't any emtpy
        # files or directories that still persist.
        util.prune_empty(series_lead_out_dir, p, logger)


def perform_series_for_range(tile_dir, start, end, step, p, logger):
    """Performs a series analysis by lead time, based on a range and increment of forecast hours.
       Invokes the MET tool Series-analysis

       Args:
           tile_dir:  The location of the input data (output from running extract_tiles.py)
           start:     The first forecast hour
           end:       The last forecast hour
           step:      The time increment/step size between forecast hours
           p:         The instance to the configuration
           logger:    The logger to which all log messages are directed

       Returns:          None
    """

    # Used for logging.
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Retrieve necessary information from the config file.
    series_analysis_exe = p.getexe("SERIES_ANALYSIS")
    series_anly_configuration_file = p.getstr('config','SERIES_ANALYSIS_BY_LEAD_CONFIG_PATH')
    series_lead_out_dir = p.getdir('SERIES_LEAD_OUT_DIR')
    var_list = util.getlist(p.getstr('config', 'VAR_LIST'))
    regrid_with_MET_tool = p.getbool('config', 'REGRID_USING_MET_TOOL')

    if regrid_with_MET_tool:
        # Regridding via MET Tool regrid_data_plane.
        fcst_tile_regex = p.getstr('regex_pattern', 'FCST_NC_TILE_REGEX')
        anly_tile_regex = p.getstr('regex_pattern', 'ANLY_NC_TILE_REGEX')
    else:
        # Regridding via wgrib2 tool.
        fcst_tile_regex = p.getstr('regex_pattern', 'FCST_TILE_REGEX')
        anly_tile_regex = p.getstr('regex_pattern', 'ANLY_TILE_REGEX')

    for fhr in range(start, end, step):
        cur_fhr = str(fhr).zfill(3)
        msg = ('INFO|[' + cur_filename + ':' + cur_function +
               ']| Evaluating forecast hour ' + cur_fhr)
        logger.debug(msg)

        # Create the output directory where the netCDF series files
        # will be saved.
        util.mkdir_p(series_lead_out_dir)
        out_dir_parts = [series_lead_out_dir, '/', 'series_F', cur_fhr]
        out_dir = ''.join(out_dir_parts)
        util.mkdir_p(out_dir)

        # Gather all the forecast gridded tile files
        # so they can be saved in ASCII files.
        fcst_tiles_list = get_anly_or_fcst_files(tile_dir, "FCST", fcst_tile_regex,
                                                 cur_fhr, logger)
        fcst_tiles = retrieve_fhr_tiles(fcst_tiles_list, 'FCST', out_dir,
                                        cur_fhr, fcst_tile_regex, logger)

        # Location of FCST_FILES_Fhhh
        ascii_fcst_file_parts = [out_dir, '/FCST_FILES_F', cur_fhr]
        ascii_fcst_file = ''.join(ascii_fcst_file_parts)

        # Now create the ASCII files needed for the -fcst and -obs
        try:
            if len(fcst_tiles) == 0:
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + " No fcst_tiles for fhr: " + cur_fhr +
                       " Don't create FCST_F<fhr> ASCII file")
                logger.debug(msg)
                continue
            else:
                with open(ascii_fcst_file, 'a') as f:
                    f.write(fcst_tiles)

        except IOError as e:
            msg = ("ERROR: Could not create requested" +
                   " ASCII file: " + ascii_fcst_file)
            logger.error(msg)

        # Gather all the anly gridded tile files
        # so they can be saved in ASCII files.
        anly_tiles_list = get_anly_or_fcst_files(tile_dir, "ANLY", anly_tile_regex,
                                                 cur_fhr, logger)
        anly_tiles = retrieve_fhr_tiles(anly_tiles_list, 'ANLY', out_dir,
                                        cur_fhr, anly_tile_regex, logger)

        # Location of ANLY_FILES_Fhhh files
        # filtering.
        ascii_anly_file_parts = [out_dir, '/ANLY_FILES_F', cur_fhr]
        ascii_anly_file = ''.join(ascii_anly_file_parts)

        try:
            # Only write to the ascii_anly_file if
            # the anly_tiles string isn't empty.
            if len(anly_tiles) == 0:
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "No anly_tiles for fhr: " + cur_fhr +
                       " Don't create ANLY_F<fhr> ASCII file")
                logger.debug(msg)
                continue
            else:
                with open(ascii_anly_file, 'a') as f:
                    f.write(anly_tiles)

        except IOError as e:
            logger.error("ERROR: Could not create requested " +
                         "ASCII file: " + ascii_anly_file)

        # Remove any empty directories that result from
        # when no files are written.
        util.prune_empty(out_dir, p, logger)

        # -fcst and -obs params
        fcst_param_parts = ['-fcst ', ascii_fcst_file]
        fcst_param = ''.join(fcst_param_parts)
        obs_param_parts = ['-obs ', ascii_anly_file]
        obs_param = ''.join(obs_param_parts)
        logger.debug('fcst param: ' + fcst_param)
        logger.debug('obs param: ' + obs_param)

        # Create the -out param and invoke the MET series
        # analysis binary
        for cur_var in var_list:
            # Get the name and level to create the -out param
            # and set the NAME and LEVEL environment variables that
            # are needed by the MET series analysis binary.
            match = re.match(r'(.*)/(.*)', cur_var)
            name = match.group(1)
            level = match.group(2)
            os.environ['NAME'] = name
            os.environ['LEVEL'] = level

            # Set NAME to name_level if regridding with regrid data plane
            if regrid_with_MET_tool:
                os.environ['NAME'] = name + '_' + level
            out_param_parts = ['-out ', out_dir, '/series_F', cur_fhr,
                               '_', name, '_', level, '.nc']
            out_param = ''.join(out_param_parts)

            # Create the full series analysis command.
            config_param_parts = ['-config ',
                                  series_anly_configuration_file]
            config_param = ''.join(config_param_parts)
            series_analysis_cmd_parts = [series_analysis_exe, ' ',
                                         ' -v 4 ',
                                         fcst_param, ' ', obs_param,
                                         ' ', config_param, ' ',
                                         out_param]
            series_analysis_cmd = ''.join(series_analysis_cmd_parts)
            msg = ("INFO:[ " + cur_filename + ":" +
                   cur_function + "]|series analysis command: " +
                   series_analysis_cmd)
            logger.debug(msg)
            series_analysis_cmd = batchexe('sh')['-c', series_analysis_cmd].err2out()
            series_out = run(series_analysis_cmd)

            # Make sure there aren't any emtpy
            # files or directories that still persist.
    util.prune_empty(series_lead_out_dir, p, logger)


def get_nseries(fhr_by_range, nc_var_file, p, logger):
    '''Determine the number of series for this lead time and
       its associated variable via calculating the max series_cnt_TOTAL 
       value.

       Args:
             fhr_by_range:  Boolean value indicating whether series analysis was performed on a range of forecast
                          hours (True) or on a "bucket" of forecast hours (False).
             nc_var_file:  The netCDF file for a particular variable.
             p:             The ConfigMaster object.
             logger:        The logger to which all log messages are
                            sent.


       Returns:
             max (float):   The maximum value of series_cnt_TOTAL of all
                            the netCDF files for the variable cur_var.

             None:          If no max value is found.


    '''

    # Retrieve any necessary things from the config/param file.
    rm_exe = p.getexe('RM_EXE')
    ncap2_exe = p.getexe('NCAP2_EXE')
    ncdump_exe = p.getexe('NCDUMP_EXE')

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Determine the series_F<fhr> subdirectory where this netCDF file
    # resides.
    if fhr_by_range:
        match = re.match(r'(.*/series_F[0-9]{3})/series_F[0-9]{3}.*nc',
                         nc_var_file)
    else:
        match = re.match(r'(.*/series_F[0-9]{3}_to_F[0-9]{3})/series_F[0-9]{3}_to_F[0-9]{3}.*nc',
                         nc_var_file)

    if match:
        base_nc_dir = match.group(1)
    else:
        msg = ("ERROR\[" + cur_filename + ":" +
               cur_function + "]| " +
               "Cannot determine base directory path for " +
               "netCDF files... exiting")
        logger.error(msg)
        sys.exit(1)

    # Use NCO utility ncap2 to find the max for 
    # the variable and series_cnt_TOTAL pair.
    nseries_nc_path = os.path.join(base_nc_dir, 'nseries.nc')
    nco_nseries_cmd_parts = [ncap2_exe, ' -v -s ', '"',
                             'max=max(series_cnt_TOTAL)', '" ',
                             nc_var_file, ' ', nseries_nc_path]
    nco_nseries_cmd = ''.join(nco_nseries_cmd_parts)
    nco_nseries_cmd = batchexe('sh')['-c', nco_nseries_cmd].err2out()
    #nco_nseries_cmd = batchexe(nco_nseries_cmd.split()[0])[nco_nseries_cmd.split()[1:]].err2out()
    nco_out = run(nco_nseries_cmd)

    # Create an ASCII file with the max value, which can be parsed.
    nseries_txt_path = os.path.join(base_nc_dir, 'nseries.txt')
    ncdump_max_cmd_parts = [ncdump_exe, ' ', base_nc_dir,
                            '/nseries.nc > ', nseries_txt_path]
    ncdump_max_cmd = ''.join(ncdump_max_cmd_parts)
    ncdump_max_cmd = batchexe('sh')['-c', ncdump_max_cmd].err2out()
    #ncdump_max_cmd = batchexe(ncdump_max_cmd.split()[0])[ncdump_max_cmd.split()[1:]].err2out()
    ncdump_out = run(ncdump_max_cmd)
    
    # Look for the max value for this netCDF file.
    try:
        with open(nseries_txt_path, 'r') as fmax:
            for line in fmax:
                max_match = re.match(r'\s*max\s*=\s([-+]?\d*\.*\d*)', line)
                if max_match:
                    max = max_match.group(1)

                    # Clean up any intermediate .nc and .txt files
                    # WARNING Using rm -rf command.
                    nseries_list = [rm_exe+' -rf', ' ', base_nc_dir, '/nseries.*']
                    nseries_cmd = ''.join(nseries_list)
                    os.system(nseries_cmd)
                    return max

    except IOError as e:
        msg = ("ERROR|[" + cur_filename + ":" +
               cur_function + "]| cannot open the min text file")
        logger.error(msg)


def get_netcdf_min_max(fhr_by_range, nc_var_files, cur_stat, p, logger):
    '''Determine the min and max for all lead times for each 
       statistic and variable pairing.

       Args:
           fhr_by_range:  Boolean value indicating whether series analysis was performed on a range of forecast
                          hours (True) or on a "bucket" of forecast hours (False).
           nc_var_files:  A list of the netCDF files generated 
                          by the MET series analysis tool that 
                          correspond to the variable of interest.
           cur_stat:      The current statistic of interest: RMSE, 
                          MAE, ODEV, FDEV, ME, or TOTAL.
           p:             The ConfigMaster object, used to retrieve
                          values from the config/param file.
           logger:        The logger to which all log messages are 
                          directed.
          
       Returns:
           tuple (vmin, vmax)
               VMIN:  The minimum
               VMAX:  The maximum
       
    '''


    ncap2_exe = p.getexe('NCAP2_EXE')
    ncdump_exe = p.getexe('NCDUMP_EXE')

    max_temporary_files = []
    min_temporary_files = []

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Initialize the threshold values for min and max.
    VMIN = 999999.
    VMAX = -999999.

    for cur_nc in nc_var_files:
        # Determine the series_F<fhr> subdirectory where this
        # netCDF file resides.
        if fhr_by_range:
            match = re.match(r'(.*/series_F[0-9]{3})/series_F[0-9]{3}.*nc', cur_nc)
        else:
            match = re.match(r'(.*/series_F[0-9]{3}_to_F[0-9]{3})/series_F[0-9]{3}_to_F[0-9]{3}.*nc', cur_nc)
        if match:
            base_nc_dir = match.group(1)
            logger.debug("base nc dir: " + base_nc_dir)
        else:
            msg = ("ERROR|[" + cur_filename + ":" + cur_function +
                   "]| Cannot determine base directory path " +
                   "for netCDF files. Exiting...")
            logger.error(msg)
            sys.exit(1)

        # Create file paths for temporary files for min value...
        min_nc_path = os.path.join(base_nc_dir, 'min.nc')
        min_txt_path = os.path.join(base_nc_dir, 'min.txt')
        min_temporary_files.append(min_nc_path)
        min_temporary_files.append(min_txt_path)

        # Clean up any temporary min files that might have been left over from a previous run.
        cleanup_temporary_files(min_temporary_files)

        # Use NCO ncap2 to get the min for the current stat-var pairing.
        nco_min_cmd_parts = [ncap2_exe, ' -v -s ', '"',
                             'min=min(series_cnt_', cur_stat, ')',
                             '" ', cur_nc, ' ', min_nc_path]
        nco_min_cmd = ''.join(nco_min_cmd_parts)
        logger.debug('nco_min_cmd: ' + nco_min_cmd)
        nco_min_cmd = batchexe('sh')['-c', nco_min_cmd].err2out()
        nco_min_out = run(nco_min_cmd)

        # now set up file paths for the max value...
        max_nc_path = os.path.join(base_nc_dir, 'max.nc')
        max_txt_path = os.path.join(base_nc_dir, 'max.txt')
        max_temporary_files.append(max_nc_path)
        max_temporary_files.append(max_txt_path)

        # First, remove pre-existing max.txt and max.nc file from any previous run.
        cleanup_temporary_files(max_temporary_files)

        # Using NCO ncap2 to perform arithmetic processing to retrieve the max from each
        # netCDF file's stat-var pairing.
        nco_max_cmd_parts = [ncap2_exe, ' -v -s ', '"',
                             'max=max(series_cnt_', cur_stat, ')',
                             '" ', cur_nc, ' ', max_nc_path]
        nco_max_cmd = ''.join(nco_max_cmd_parts)
        logger.debug('nco_max_cmd: ' + nco_max_cmd)
        nco_max_cmd = batchexe('sh')['-c', nco_max_cmd].err2out()
        nco_out = run(nco_max_cmd)

        # Create ASCII files with the min and max values, using the
        # NCO utility ncdump.
        # These files can be parsed to determine the VMIN and VMAX.
        ncdump_min_cmd_parts = [ncdump_exe, ' ', base_nc_dir, '/min.nc > ', min_txt_path]
        ncdump_min_cmd = ''.join(ncdump_min_cmd_parts)
        ncdump_min_cmd = batchexe('sh')['-c', ncdump_min_cmd].err2out()
        ncdump_min_out = run(ncdump_min_cmd)

        ncdump_max_cmd_parts = [ncdump_exe, ' ', base_nc_dir,
                                '/max.nc > ', max_txt_path]
        ncdump_max_cmd = ''.join(ncdump_max_cmd_parts)
        ncdump_max_cmd = batchexe('sh')['-c', ncdump_max_cmd].err2out()
        ncdump_max_out = run(ncdump_max_cmd)

        # Search for 'min' in the min.txt file.
        try:
            with open(min_txt_path, 'r') as fmin:
                for line in fmin:
                    min_match = re.match(r'\s*min\s*=\s([-+]?\d*\.*\d*)',
                                         line)
                    if min_match:
                        cur_min = float(min_match.group(1))
                        if cur_min < VMIN:
                            VMIN = cur_min
        except IOError as e:
            msg = ("ERROR|[" + cur_filename + ":" + cur_function +
                   "]| cannot open the min text file")
            logger.error(msg)

        # Search for 'max' in the max.txt file.
        try:
            with open(max_txt_path, 'r') as fmax:
                for line in fmax:
                    max_match = re.match(r'\s*max\s*=\s([-+]?\d*\.*\d*)',
                                         line)
                    if max_match:
                        cur_max = float(max_match.group(1))
                        if cur_max > VMAX:
                            VMAX = cur_max
        except IOError as e:
            msg = ("ERROR|[" + cur_filename + ":" + cur_function +
                   "]| cannot open the max text file")
            logger.error(msg)

        # Clean up min.nc, min.txt, max.nc and max.txt temporary files.
        cleanup_temporary_files(min_temporary_files)
        cleanup_temporary_files(max_temporary_files)

    return VMIN, VMAX


def get_var_ncfiles(fhr_by_range, cur_var, nc_list, logger):
    ''' Retrieve only the netCDF files corresponding to this statistic
        and variable pairing.

        Args:
            fhr_by_range: The boolean value indicating whether series analysis was performed on a range of forecast hours
                       (True) or on a 'bucket' of forecast hours (False)
            cur_var:   The variable of interest.
            nc_list:  The list of all netCDF files that were generated 
                      by the MET utility run_series_analysis.
            logger:  The logger to which all logging messages are sent

        Returns:
            var_ncfiles: A list of netCDF files that
                              correspond to this variable.

    '''

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Create the regex to retrieve the variable name.
    # The variable is contained in the netCDF file name.
    var_ncfiles = []
    var_regex_parts = [".*series_F[0-9]{3}_", cur_var,
                       "_[0-9a-zA-Z]+.*nc"]
    if fhr_by_range:
        var_regex_parts = [".*series_F[0-9]{3}_", cur_var,
                           "_[0-9a-zA-Z]+.*nc"]
    else:
        var_regex_parts = [".*series_F[0-9]{3}_to_F[0-9]{3}_", cur_var,
                           "_[0-9a-zA-Z]+.*nc"]

    var_regex = ''.join(var_regex_parts)
    for cur_nc in nc_list:
        # Determine the variable from the filename
        match = re.match(var_regex, cur_nc)
        if match:
            var_ncfiles.append(cur_nc)

    return var_ncfiles


def retrieve_nc_files(fhr_by_range, base_dir, logger):
    '''Retrieve all the netCDF files that were created by the 
       MET series analysis binary.

       Args:
           fhr_by_range: Boolean, True indicates series analysis performed on a range of forecast hours, False
                         indicates that series analysis was performed on a bucket of forecast hours.
           base_dir: The base directory where all the 
                     series_F<fcst hour> sub-directories
                     are located.  The corresponding variable and 
                     statistic files for these forecast hours are 
                     found in these sub-directories.
                   
           logger:  The logger to which all log messages are directed.

       Returns:
           nc_list:  A list of the netCDF files (full path) created 
                     when the MET series analysis binary was invoked.
    '''

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    nc_list = []
    if fhr_by_range:
        filename_regex = "series_F[0-9]{3}.*nc"
    else:
        # filename_regex = "series_F[0-9]{3}_to_F[0-9]{3}.*nc"
        filename_regex = "series_F[0-9]{3}.*nc"

    # Get a list of all the series_F* directories
    # Use the met_utils function get_dirs to get only
    # the directories, as we are also generating
    # ASCII tmp_fcst and tmp_anly files in the
    # base_dir, which can cause problems if included in
    # the series_dir_list.
    series_dir_list = util.get_dirs(base_dir, p, logger)

    # Iterate through each of these series subdirectories
    # and create a list of all the netCDF files (full file path).
    for dir in series_dir_list:
        full_path = os.path.join(base_dir, dir)

        # Get a list of all the netCDF files for this subdirectory.
        nc_files_list = [f for f in os.listdir(full_path) if
                         os.path.isfile(os.path.join(full_path, f))]
        for cur_nc in nc_files_list:
            match = re.match(filename_regex, cur_nc)
            if match:
                nc_file = os.path.join(full_path, cur_nc)
                nc_list.append(nc_file)

    return nc_list


def retrieve_fhr_tiles(tile_list, file_type, cur_fhr, out_dir,
                       type_regex, logger):
    ''' Retrieves only the gridded tile files that
        correspond to the type.
        
        Args:
           tile_list:  List of tiles (full filepath).
           file_type : FCST or ANLY
           cur_fhr:    The current forecast hour
           out_dir:    The output directory 
           type_regex: The regex that corresponds to the tile 
                       filename for this type
           logger:     Logger to which all logging messages are passed.
        
        Returns:
           fhr_tiles (string):  A string of gridded tile names 
                                separated by newlines
    '''

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    type = file_type.upper()
    fhr_tiles = ''
    for cur_tile in tile_list:
        match = re.match(type_regex, cur_tile)
        if match:
            storm_subdir = match.group(0)
        else:
            msg = ("ERROR|[" + cur_filename + ":" +
                   cur_function +
                   "]| No matching storm id found, exiting...")
            logger.error(msg)
            return ''

        # Create the ASCII files for the forecast or analysis files
        if type == 'FCST':
            filename_base = 'FCST_FILES_F'
        else:
            filename_base = 'ANLY_FILES_F'

        tile_hr_parts = [filename_base, cur_fhr]
        tile_hr_dir = ''.join(tile_hr_parts)
        tile_full_filename = os.path.join(out_dir, tile_hr_dir)

        fhr_tiles += cur_tile
        fhr_tiles += '\n'

    return fhr_tiles


def find_matching_tile(fcst_file, anly_tiles, logger):
    ''' Find the corresponding ANLY 30x30 tile file to the 
        fcst tile file.
       
        Args:
          fcst_file_list (string):  The fcst file (full path) that 
                               is used to derive the corresponding
                               analysis file name.
          anly_tiles : The list of all available 30x30 analysis tiles.
          
          logger     : The logger to which all logging messages are
                       directed.

        Returns:
          anly_from_fcst (string): The name of the analysis tile file
                                   that corresponds to the same lead 
                                   time as the input fcst tile. 
    '''

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Derive the ANLY file name from the FCST file.
    anly_from_fcst = re.sub(r'FCST', 'ANLY', fcst_file)

    if anly_from_fcst in anly_tiles:
        return anly_from_fcst
    else:
        return None


def get_anly_or_fcst_files(filedir, type, filename_regex, cur_fhr, logger):
    ''' Get all the ANLY or FCST files by walking 
        through the directories starting at filedir.
    
        Args:
          filedir (String):  The topmost directory from which the
                             search begins.
          type:  FCST or ANLY
          filename_regex (string):  The regular expression that
                                    defines the naming format
                                    of the files of interest.

          cur_fhr: The current forecast hour for which we need to 
                   find the corresponding file

          logger:  The logger to which all log messages will be
                   directed.
       Returns:
          file_paths (string): a list of filenames (with full filepath)       

    '''

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    file_paths = []

    # Walk the tree
    for root, directories, files in os.walk(filedir):
        for filename in files:
            # add it to the list only if it is a match
            # to the specified format
            # prog = re.compile(filename_regex)
            match = re.match(filename_regex, filename)
            if match:
                # Now match based on the current forecast hour
                if type == 'FCST':
                    match_fhr = re.match(r'.*FCST_TILE_F([0-9]{3}).*',
                                         match.group())
                elif type == 'ANLY':
                    match_fhr = re.match(r'.*ANLY_TILE_F([0-9]{3}).*',
                                         match.group())

                if match_fhr:
                    if match_fhr.group(1) == cur_fhr:
                        # Join the two strings to form the full
                        # filepath.
                        filepath = os.path.join(root, filename)
                        file_paths.append(filepath)
            else:
                continue
    return file_paths


def cleanup_lead_ascii(p, logger):
    ''' Remove any pre-existing FCST and ANLY ASCII files 
        created by previous runs of series_by_lead.
        

        Args:
           p       : The ConfigMaster, used to retrieve the  
                     parameter values
           logger  : The logger to which all log messages are directed.
     
        Returns:
           None:    Removes any existing FCST and ANLY ASCII files 
                    which contains all the forecast and analysis 
                    gridded tiles.
    '''

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    fhr_beg = p.getint('config','FHR_BEG')
    fhr_end = p.getint('config','FHR_END')
    fhr_inc = p.getint('config','FHR_INC')
    fcst_ascii_regex = p.getstr('regex_pattern','FCST_ASCII_REGEX_LEAD')
    anly_ascii_regex = p.getstr('regex_pattern','ANLY_ASCII_REGEX_LEAD')
    rm_exe = p.getexe('RM_EXE')
    out_dir_base = p.getdir('SERIES_LEAD_OUT_DIR')

    for fhr in range(fhr_beg, fhr_end + 1, fhr_inc):
        cur_fhr = str(fhr).zfill(3)
        out_dir_parts = [out_dir_base, '/', 'series_F', cur_fhr]
        out_dir = ''.join(out_dir_parts)

        for root, directories, files in os.walk(out_dir):
            for cur_file in files:
                fcst_match = re.match(fcst_ascii_regex, cur_file)
                anly_match = re.match(anly_ascii_regex, cur_file)
                rm_file = os.path.join(out_dir, cur_file)
                if fcst_match:
                    os.remove(rm_file)
                if anly_match:
                    os.remove(rm_file)


def cleanup_temporary_files(list_of_files):
    """ Remove the files indicated in the list_of_files list.  The full file path must be indicated.

        Args:
            list_of_files: A list of files (full filepath) to be removed.
        Returns:
            None:  Removes the requested files.
    """
    for f in list_of_files:
        try:
            os.remove(f)
        except OSError as oe:
            # Raises exception if this doesn't exist (never created or already removed).  Ignore.
            pass

if __name__ == "__main__":
    # sleep is for debugging in pycharm so I can attach to this process
    # from the os.system call in master_met_plus.py
    #import time
    #time.sleep(60)

    # sys.argv[0]='/path/to/series_by_lead.py'
    # sys.argv[1]='-c'
    # sys.argv[2]='jfrimel_ocean_constants_pdef_a.py'

    # Testing constants_pdef until produtil is fully integrated.
    #import constants_pdef as P
    #test = P.Params()
    #test.init(__doc__)


    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='series_by_lead',jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='series_by_lead')
        produtil.log.postmsg('series_by_lead is starting')

        # Read in the conf object p
        import config_launcher
        if len(sys.argv) == 3:
            p = config_launcher.load_baseconfs(sys.argv[2])
        else:
            p = config_launcher.load_baseconfs()
        logger = util.get_logger(p)
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = p.getdir('MET_BASE')
        analysis_by_lead_time()
        produtil.log.postmsg('series_by_lead completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'series_by_lead failed: %s'%(str(e),),exc_info=True)
        sys.exit(2)
