#!/usr/bin/env python

from __future__ import print_function

import constants_pdef as P
import re
import os
import sys
import met_util as util
import subprocess


def analysis_by_init_time():
    ''' Invoke the series analysis script based on
        the init time in the format YYYYMMDD_hh

         Args:

 
         Returns:
              None:  Creates graphical plots of storm tracks


    '''
    # Retrieve any necessary values (dirs, executables) 
    # from the param file(s)
    var_list = p.opt["VAR_LIST"]
    stat_list = p.opt["STAT_LIST"]
    series_analysis_exe = p.opt["SERIES_ANALYSIS"]
    plot_data_plane_exe = p.opt["PLOT_DATA_PLANE"]
    convert_exe = p.opt["CONVERT_EXE"]
    series_anlysis_config_file = p.opt["SERIES_ANALYSIS_BY_INIT_CONFIG_PATH"]
    regrid_with_MET_tool = p.opt["REGRID_USING_MET_TOOL"]
    extract_tiles_dir = p.opt["EXTRACT_OUT_DIR"]
    series_out_dir = p.opt["SERIES_INIT_OUT_DIR"]
    series_filtered_out_dir = p.opt["SERIES_INIT_FILTERED_OUT_DIR"]
    background_map = p.opt["BACKGROUND_MAP"]
    series_filter_opts = p.opt["SERIES_ANALYSIS_FILTER_OPTS"]

    # Set up the environment variable to be used in the Series Analysis
    #   Config file (SERIES_ANALYSIS_BY_LEAD_CONFIG_PATH)
    # Used to set cnt  value in output_stats in "SERIES_ANALYSIS_BY_LEAD_CONFIG_PATH"
    # Need to do some pre-processing so that Python will use " and not '
    #  because currently MET doesn't support single-quotes
    tmp_stat_string = str(stat_list)
    tmp_stat_string = tmp_stat_string.replace("\'", "\"")
    os.environ['STAT_LIST'] = tmp_stat_string

    if regrid_with_MET_tool:
        # Regridding via MET Tool regrid_data_plane.
        fcst_tile_regex = p.opt["FCST_NC_TILE_REGEX"]
        anly_tile_regex = p.opt["ANLY_NC_TILE_REGEX"]
    else:
        # Regridding via wgrib2 tool.
        fcst_tile_regex = p.opt["FCST_TILE_REGEX"]
        anly_tile_regex = p.opt["ANLY_TILE_REGEX"]

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    logger.info("Starting series analysis by init time")

    # Initialize the tile_dir to point to the extract_tiles_dir.
    # And retrieve a list of init times based on the data available in
    # the extract tiles directory.
    tile_dir = extract_tiles_dir
    init_times = util.get_updated_init_times(tile_dir, p, logger)

    # Check for input tile data.
    try:
        util.check_for_tiles(tile_dir, fcst_tile_regex, anly_tile_regex, logger)
    except OSError as e:
        msg = ("Missing 30x30 tile files.  " +
               "Extract tiles needs to be run")
        logger.error(msg)

    # If applicable apply any filtering via tc_stat, as indicated in the
    # constants_pdef.py parameter/config file.
    if series_filter_opts:
        util.apply_series_filters(tile_dir, init_times, series_filtered_out_dir, p, logger)

        # Clean up any empty files and directories that could arise as a result of filtering
        util.prune_empty(series_filtered_out_dir, p, logger)

        # Get the list of all the files that were created as a result
        # of applying the filter options.
        #  First, make sure that the series_lead_filtered_out directory isn't
        # empty.  If so, then no files fall within the filter criteria.
        if os.listdir(series_filtered_out_dir):
            # The series filter directory has data, use this directory as
            # input for series analysis.
            tile_dir = series_filtered_out_dir

            # Generate the tmp_anly and tmp_fcst files used to validate filtering and for troubleshooting
            # The tmp_fcst and tmp_anly ASCII files contain the
            # list of files that meet the filter criteria.
            filtered_dirs_list = util.get_files(tile_dir, ".*.", logger)
            util.create_filter_tmp_files(filtered_dirs_list, series_filtered_out_dir, p, logger)

        else:
            msg = ("INFO| Applied series filter options, no results..." +
                   "using extract tiles data for series analysis input.")
            logger.debug(msg)
            tile_dir = extract_tiles_dir
            filtered_dirs_list = util.get_files(tile_dir, ".*.", logger)

    else:
        # No additional filtering was requested.  Use the data in the extract tiles directory
        # as input for series analysis.
        # source of input tile data.
        filtered_dirs_list = util.get_files(tile_dir, ".*.", logger)
        tile_dir = extract_tiles_dir

    # From the filtered files list, extract the init time and storm id and
    # create a sorted list of the init times.
    filter_init_times = set()
    for f in filtered_dirs_list:
        # Retrieve the file path that contains the init time and storm id.
        match = re.match(r'.*/([0-9]{8}_[0-9]{2,3})/([A-Za-z]{2}[0-9]{10})/', f)
        if match:
            init_storm = match.group(1)
            init_storm_dir = match.group(0)

            # Add this path if the directory isn't empty
            if os.listdir(init_storm_dir):
                filter_init_times.add(init_storm)
            else:
                # Directory is empty, go to next one in the filtered_dirs_list.
                continue
        else:
            continue

    # Create FCST and ANLY ASCII files based on init time and storm id.  These are arguments to the
    # -fcst and -obs arguments to the MET Tool series_analysis.
    # First, get an updated list of init times, since filtering can reduce the amount of init times.
    filter_init_times = util.get_updated_init_times(tile_dir, p, logger)
    sorted_filter_init = sorted(filter_init_times)
    fcst_ascii_file_base = 'FCST_ASCII_FILES_'
    anly_ascii_file_base = 'ANLY_ASCII_FILES_'

    for cur_init in sorted_filter_init:
        # Get all the storm ids for storm track pairs that
        # correspond to this init time.
        storm_list = get_storms_for_init(cur_init, tile_dir, logger)
        if len(storm_list) == 0:
            # No storms for this init time,
            # check next init time in list
            continue
        else:
            for cur_storm in storm_list:
                # Generate the -fcst, -obs, -config, and
                # -out parameter values for invoking
                # the MET series_analysis binary.

                # First get the filenames for the gridded forecast and
                # analysis (30 deg x30 deg tiles that were created by
                # extract_tiles). These files are aggregated by
                # init time and storm id.
                anly_grid_regex = ".*ANLY_TILE_F.*grb2"
                fcst_grid_regex = ".*FCST_TILE_F.*grb2"

                if regrid_with_MET_tool:
                    anly_grid_regex = ".*ANLY_TILE_F.*nc"
                    fcst_grid_regex = ".*FCST_TILE_F.*nc"

                anly_grid_files = util.get_files(tile_dir,
                                                 anly_grid_regex, logger)
                fcst_grid_files = util.get_files(tile_dir,
                                                 fcst_grid_regex, logger)

                # Now do some checking to make sure we aren't
                # missing either the forecast or
                # analysis files, if so log the error and proceed to next
                # storm in the list.
                if len(anly_grid_files) == 0 or len(fcst_grid_files) == 0:
                    # No gridded analysis or forecast
                    # files found, continue
                    continue

                # Now create the FCST and ANLY ASCII files based on cur_init and cur_storm:
                create_fcst_anly_to_ascii_file(fcst_grid_files, cur_init, cur_storm, fcst_ascii_file_base,
                                               series_out_dir, logger)
                create_fcst_anly_to_ascii_file(fcst_grid_files, cur_init, cur_storm, anly_ascii_file_base,
                                               series_out_dir, logger)
                util.prune_empty(series_out_dir, p, logger)

    # Clean up any remaining empty files and dirs
    util.prune_empty(series_out_dir, p, logger)
    logger.debug("Finished creating FCST and ANLY ASCII files, and cleaning empty files and dirs")

    # Now assemble the -fcst, -obs, and -out arguments and invoke the MET Tool: series_analysis.
    for cur_init in sorted_filter_init:
        storm_list = get_storms_for_init(cur_init, tile_dir, logger)
        for cur_storm in storm_list:
            if len(storm_list) == 0:
                # No storm ids found for cur_init
                # check next init time in the list.
                continue
            else:
                # Generate the -obs portion (analysis file)
                # These are the gridded observation files.
                # -obs obs_file1 obs_file2 obs_file3 ... obs_filen
                # or
                #  -obs obs_ASCII_filename
                # where obs_ASCII_filename contains the full file path
                # and filename of each gridded analysis file.  We will
                # use the FCST ASCII filename created above.
                fcst_ascii_fname_parts = [fcst_ascii_file_base, cur_storm]
                fcst_ascii_fname = ''.join(fcst_ascii_fname_parts)
                fcst_ascii = os.path.join(series_out_dir, cur_init,
                                          cur_storm, fcst_ascii_fname)
                fcst_param_parts = ['-fcst ', fcst_ascii]
                fcst_param = ''.join(fcst_param_parts)
                msg = ("DEBUG|[" + cur_function + ":" + cur_filename + "]" +
                       "fcst param: " + fcst_param)
                logger.debug(msg)

                # Generate the -obs portion (analysis file)
                # These are the gridded observation files.
                # -obs obs_file1 obs_file2 obs_file3 ... obs_filen
                # or
                # -obs obs_ASCII_filename
                # where obs_ASCII_filename contains the full file path
                # and filename of each gridded analysis file.  We will
                # use the ANLY ASCII file generated above.
                anly_ascii_fname_parts = [anly_ascii_file_base, cur_storm]
                anly_ascii_fname = ''.join(anly_ascii_fname_parts)
                anly_ascii = os.path.join(series_out_dir, cur_init,
                                          cur_storm, anly_ascii_fname)
                obs_param_parts = [' -obs ', anly_ascii]
                obs_param = ''.join(obs_param_parts)
                msg = ("DEBUG|[" + cur_function + ":" + cur_filename + "]" +
                       "obs param: " + obs_param)
                logger.debug(msg)

                # Generate the -out portion, get the NAME and
                # corresponding LEVEL for each variable.
                output_dir = os.path.join(series_out_dir, cur_init,
                                          cur_storm)
                util.mkdir_p(output_dir)

                for cur_var in var_list:
                    name, level = util.get_name_level(cur_var, logger)

                    # Set the NAME and LEVEL environment variables, this
                    # is required by the MET series_analysis binary.
                    os.environ['NAME'] = name
                    os.environ['LEVEL'] = level

                    # Set the NAME to name_level if regrid_data_plane
                    # was used to regrid.
                    if regrid_with_MET_tool:
                        os.environ['NAME'] = name + "_" + level

                    series_anly_output_parts = [output_dir, '/',
                                                'series_', name, '_',
                                                level, '.nc']
                    series_anly_output_fname = ''.join(
                        series_anly_output_parts)

                    out_param_parts = ['-out ', series_anly_output_fname]
                    out_param = ''.join(out_param_parts)

                    # Now put everything together to create the
                    # command for running the MET series_analysis binary:
                    # -fcst <file> -obs <obs_file> -out <output file>
                    # -config <series analysis config file>
                    command_parts = [series_analysis_exe, ' ',
                                     fcst_param, ' ', obs_param,
                                     ' -config ', series_anlysis_config_file,
                                     ' ', out_param]
                    command = ''.join(command_parts)

                    msg = ('INFO|[' + cur_filename + ':' +
                           cur_function + ']|' +
                           'SERIES ANALYSIS COMMAND: ' + command)
                    logger.debug(msg)

                    # Using shell=True because we aren't relying
                    # on external input for creating the command
                    # to the MET series analysis binary
                    met_result = subprocess.check_output(command,
                                                         stderr=subprocess.STDOUT,
                                                         shell=True)

                    # Now we need to invoke the MET tool
                    # plot_data_plane to generate plots that are
                    # recognized by the MET viewer.
                    # Get the number of forecast tile files,
                    # the name of the first and last in the list
                    # to be used by the -title option.
                    if tile_dir == extract_tiles_dir:
                        # Since filtering was not requested, or
                        # the additional filtering doesn't yield results,
                        # search the series_out_dir
                        num, beg, end = get_fcst_file_info(series_out_dir,
                                                           cur_init, cur_storm,
                                                           p, logger)
                    else:
                        # Search the series_filtered_out_dir for the filtered files.
                        num, beg, end = get_fcst_file_info(series_filtered_out_dir,
                                                           cur_init, cur_storm,
                                                           p, logger)

                    # Assemble the input file, output file, field string,
                    # and title
                    plot_data_plane_input_fname = series_anly_output_fname
                    for cur_stat in stat_list:
                        plot_data_plane_output = [output_dir,
                                                  '/series_',
                                                  name, '_',
                                                  level, '_',
                                                  cur_stat, '.ps']
                        plot_data_plane_output_fname = ''.join(
                            plot_data_plane_output)
                        os.environ['CUR_STAT'] = cur_stat

                        # Create versions of the arg based on
                        # whether the background map is requested
                        # in constants_pdef.py.
                        map_data = ' map_data={ source=[];}'

                        if background_map:
                            # Flag set to True, draw background map.
                            field_string_parts = ["'name=", '"series_cnt_',
                                                  cur_stat, '";',
                                                  'level="', level, '";',
                                                  "'"]
                        else:
                            field_string_parts = ["'name=", '"series_cnt_',
                                                  cur_stat, '";',
                                                  'level="', level, '";',
                                                  map_data, "'"]

                        field_string = ''.join(field_string_parts)
                        title_parts = [' -title "GFS Init ', cur_init,
                                       ' Storm ', cur_storm, ' ',
                                       str(num), ' Forecasts (',
                                       str(beg), ' to ', str(end),
                                       '),', cur_stat, ' for ',
                                       cur_var, '"']
                        title = ''.join(title_parts)

                        # Now assemble the entire plot data plane command
                        data_plane_command_parts = [plot_data_plane_exe,
                                                    ' ',
                                                    plot_data_plane_input_fname,
                                                    ' ',
                                                    plot_data_plane_output_fname,
                                                    ' ', field_string, ' ', title]

                        data_plane_command = ''.join(
                            data_plane_command_parts)

                        # Using shell=True because we aren't
                        # relying on external input
                        # for creating the command to the MET series
                        # analysis binary
                        data_plane_result = subprocess.check_output(
                            data_plane_command,
                            stderr=subprocess.STDOUT,
                            shell=True)

                        # Now assemble the command to convert the
                        # postscript file to png
                        png_fname = plot_data_plane_output_fname.replace(
                            '.ps', '.png')
                        convert_parts = [convert_exe, ' -rotate 90',
                                         ' -background white -flatten ',
                                         plot_data_plane_output_fname,
                                         ' ', png_fname]
                        convert = ''.join(convert_parts)

                        # Using shell=True because we aren't relying
                        # on external input for creating the command to
                        # the MET series analysis binary
                        convert_results = subprocess.check_output(convert,
                                                                  stderr=subprocess.STDOUT,
                                                                  shell=True)
    logger.info("Finished series analysis by init time")


def get_fcst_file_info(dir_to_search, cur_init, cur_storm, p, logger):
    ''' Get the number of all the gridded forecast 30x30 tile 
        files for a given storm id and init time
        (created by extract_tiles). Determine the filename of the 
        first and last files.  This information is used to create 
        the title value to the -title opt in plot_data_plane.
    
        Args:
           dir_to_search: The directory of the gridded files of interest.
           cur_init:  The init time of interest.
           cur_storm:  The storm id of interest.
           p        : The reference to constants_pdef.py param/config file.
           logger:  The logger to which all logging messages 
                    will be directed.


        Returns:
           num, beg, end:  A tuple representing the number of 
                           forecast tile files, and the first and 
                           last file.

                          sys.exit(1) otherwise
        

    '''

    regrid_with_MET_tool = p.opt["REGRID_USING_MET_TOOL"]

    # For logging 
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Get a sorted list of the forecast tile files for the init 
    # time of interest for all the storm ids and return the 
    # forecast hour corresponding to the first and last file.
    # base_dir_to_search = os.path.join(output_dir, cur_init)
    gridded_dir = os.path.join(dir_to_search, cur_init, cur_storm)
    search_regex = ".*FCST_TILE.*.grb2"

    if regrid_with_MET_tool:
        search_regex = ".*FCST_TILE.*.nc"

    files_of_interest = util.get_files(gridded_dir, search_regex,
                                       logger)
    sorted_files = sorted(files_of_interest)
    if len(files_of_interest) == 0:
        msg = ("ERROR:|[" + cur_filename + ":" +
               cur_function + "]|exiting, no files found for " +
               "init time of interest" +
               " and directory:" + dir_to_search)
        logger.error(msg)
        sys.exit(1)

    first = sorted_files[0]
    last = sorted_files[-1]

    # Extract the forecast hour from the first and last
    # filenames.
    match_beg = re.search(".*FCST_TILE_(F[0-9]{3}).*.grb2", first)
    match_end = re.search(".*FCST_TILE_(F[0-9]{3}).*.grb2", last)
    if regrid_with_MET_tool:
        match_beg = re.search(".*FCST_TILE_(F[0-9]{3}).*.nc", first)
        match_end = re.search(".*FCST_TILE_(F[0-9]{3}).*.nc", last)
    if match_beg:
        beg = match_beg.group(1)
    else:
        msg = ("ERROR|[" + cur_filename + ":" + cur_function + "]| " +
               "Unexpected file format encountered, exiting...")
        logger.error(msg)
        sys.exit(1)
    if match_end:
        end = match_end.group(1)
    else:
        msg = ("ERROR|[" + cur_filename + ":" + cur_function +
               "]| " +
               "Unexpected file format encountered, exiting...")
        logger.error(msg)
        sys.exit(1)

    # Get the number of forecast tile files
    num = len(sorted_files)

    return num, beg, end


def get_storms_for_init(cur_init, out_dir_base, logger):
    ''' Retrieve all the filter files which have the .tcst
        extension.  Inside each file, extract the STORM_ID
        and append to the list, if the storm_list directory
        exists.
        
        Args:
           cur_init : the init time

           out_dir_base (string):  The directory where one should start
                                   searching for the filter file(s)
                                   - those with a .tcst file extension.

           logger : The logger to which all log messages are directed. 

        Returns:
           storm_list: A list of all the storms ids that correspond to this init time and actually
                             has a directory in the init dir (additional filtering in a previous step
                             may result in missing storm ids even though they are in the filter.tcst file)
 
    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Retrieve filter files, first create the filename
    # by piecing together the out_dir_base with the cur_init.
    filter_filename = "filter_" + cur_init + ".tcst"
    filter_file = os.path.join(out_dir_base, cur_init, filter_filename)

    # Now that we have the filter filename for the init time, let's
    # extract all the storm ids in this filter file.
    storm_list = util.get_storm_ids(filter_file, logger)

    return storm_list


def create_fcst_anly_to_ascii_file(fcst_anly_grid_files, cur_init, cur_storm, fcst_anly_filename_base,
                                   series_out_dir, logger):
    ''' Create ASCII file for either the FCST or ANLY files that are aggregated based on init time
        and storm id.

        Args:
                fcst_anly_grid_files:       A list of the FCST or ANLY gridded files under consideration.



                cur_init:                  The initialization time of interest

                cur_storm:                 The storm id of interest

                fcst_anly_filename_base:   The base name of the ASCII file (either ANLY_ASCII_FILES_ or
                                           FCST_ASCII_FILES_ which will be appended with the
                                           storm id.

                series_out_dir:            The directory where all the output from series analysis will be saved.

                logger:                    The logger to which all logging will be directed.

        Returns:
               None:                       Creates an ASCII file containing a list of either FCST or ANLY
                                           files based on init time and storm id.


    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Create an ASCII file containing a list of all
    # the fcst or analysis tiles.
    fcst_anly_ascii_fname_parts = [fcst_anly_filename_base, cur_storm]
    fcst_anly_ascii_fname = ''.join(fcst_anly_ascii_fname_parts)
    fcst_anly_ascii_dir = os.path.join(series_out_dir, cur_init,
                                       cur_storm)
    util.mkdir_p(fcst_anly_ascii_dir)
    fcst_anly_ascii = os.path.join(fcst_anly_ascii_dir, fcst_anly_ascii_fname)

    # Sort the files in the fcst_anly_grid_files list.
    sorted_fcst_anly_grid_files = sorted(fcst_anly_grid_files)
    tmp_param = ''
    for cur_fcst_anly in sorted_fcst_anly_grid_files:
        # Write out the files that pertain to this storm and
        # don't write if already in tmp_param.
        if cur_fcst_anly not in tmp_param and cur_storm in cur_fcst_anly:
            tmp_param += cur_fcst_anly
            tmp_param += '\n'
    # Now create the fcst or analysis ASCII file
    try:
        with open(fcst_anly_ascii, 'a') as f:
            f.write(tmp_param)
    except IOError as e:
        msg = ("ERROR|[" + cur_filename + ":" +
               cur_function + "]| " +
               "Could not create requested ASCII file:  " +
               fcst_anly_ascii)
        logger.error(msg)

    if os.stat(fcst_anly_ascii).st_size == 0:
        # Just in case there are any empty fcst ASCII or anly ASCII files at this point,
        # explicitly remove them (and any resulting empty directories)
        #  so they don't cause any problems with further processing
        # steps.
        util.prune_empty(fcst_anly_ascii_dir, p, logger)

if __name__ == "__main__":
    p = P.Params()
    p.init(__doc__)
    logger = util.get_logger(p)
    analysis_by_init_time()
