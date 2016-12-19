#!/usr/bin/python

from __future__ import print_function

import constants_pdef as P
import logging
import re
import os
import sys
import met_util as util
import errno
import subprocess
import run_tc_stat as tcs



def analysis_by_init_time():
    ''' Invoke the series analysis script based on
        the init time in the format YYYYMMDD_hh

         Args:

 
         Returns:
              None:  Creates graphical plots of storm tracks


    '''
    # Create ConfigMaster param object
    p = P.Params()
    p.init(__doc__)    
      

    # Retrieve any necessary values (dirs, executables) 
    # from the param file(s)
    init_time_list = p.opt["INIT_LIST"]
    var_list = p.opt["VAR_LIST"]
    stat_list = p.opt["STAT_LIST"]
    proj_dir = p.opt["PROJ_DIR"]
    tc_stat_exe = p.opt["TC_STAT"]
    series_analysis_exe = p.opt["SERIES_ANALYSIS"]
    plot_data_plane_exe = p.opt["PLOT_DATA_PLANE"]
    regrid_data_plane_exe = p.opt["REGRID_DATA_PLANE"]
    convert_exe = p.opt["CONVERT_EXE"]
    tr_exe  = p.opt["TR_EXE"]
    cut_exe = p.opt["CUT_EXE"]
    ncap2_exe = p.opt["NCAP2_EXE"]
    rm_exe = p.opt["RM_EXE"]
    series_anly_config_file = p.opt["CONFIG_FILE_INIT"]
    MET_regrid = p.opt["REGRID_USING_MET_TOOL"]  
    filter_opts = p.opt["SERIES_ANALYSIS_FILTER_OPTS"]
    cur_pid = str(os.getpid()) 
    tmp_dir = os.path.join(p.opt["TMP_DIR"], cur_pid)
    extract_tiles_dir = p.opt["EXTRACT_OUT_DIR"]
    series_out_dir = p.opt["SERIES_INIT_OUT_DIR"]
    series_filtered_out_dir = p.opt["SERIES_INIT_FILTERED_OUT_DIR"]
    background_map = p.opt["BACKGROUND_MAP"]

    if MET_regrid:
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

 
    # Check for the existence of forecast and analysis tile files
    tile_dir = extract_tiles_dir
    print("tile_dir before check_for_tiles: ", tile_dir)
    try:
        util.check_for_tiles(tile_dir, fcst_tile_regex, 
                             anly_tile_regex, logger)
    except OSError as e:
        msg = ("Missing 30x30 tile files.  " +
               "Extract tiles needs to be run")
        logger.error(msg)
        raise
     
    # Get a list of the forecast tile files
    fcst_tiles = util.get_files(tile_dir, fcst_tile_regex, logger)

    # Generate ASCII files that contain a list of all the forecast and 
    # analysis tiles that were created by the extract_tiles script.  
    # First clean up any existing ASCII files that may have been 
    # created in a previous run
    #cleanup_ascii(init_time_list,p,logger)

    # Apply any filtering, use MET Tool tc_stat.  Filter options
    # are defined in the constants_pdef.py param/config file.
    util.mkdir_p(series_filtered_out_dir)
    filter_filename = os.path.join(series_filtered_out_dir, "filter.tcst")
    print("filter_filename: ", filter_filename)
    tc_cmd_list = [tc_stat_exe, " -job filter ",
                   " -lookin ", extract_tiles_dir,
                   " -match_points true ",
                   " -dump_row ", filter_filename,
                   " ", filter_opts]
    tc_cmd = ''.join(tc_cmd_list)
    tcs.tc_stat(p,logger,tc_cmd, series_filtered_out_dir)
    msg = ("INFO|[" + cur_filename + ":" + cur_function + "]|" +
        "tc command: " + tc_cmd)  
    logger.info(msg)

    # Check that the filter.tcst file created by tc_stat isn't empty.
    # If it is, then continue using the files in the extract_tiles 
    # directory as input.  Otherwise, use the files in 
    # series_filtered_out_dir (created by applying the filter opts) 
    # as input.
    if os.stat(filter_filename).st_size == 0:
        msg = ("WARN|[" + cur_filename + ":" + cur_function + "]|" +
               "Empty filter file, filter options yield nothing..." +
               "using full dataset in extract tiles directory.")
        logger.warn(msg)
    else:
        # Now retrieve and regrid the files corresponding to the
        # storm ids in the filter file.
        tile_dir = series_filtered_out_dir
        print("tile_dir points to filtered dir: ", tile_dir)
        sorted_storm_ids = util.get_storm_ids(filter_filename, logger)
        storm_match_list = []
        for cur_storm in sorted_storm_ids:
            msg = ("INFO|[" + cur_filename + ":" + cur_function +
                   "]| Processing storm: " + cur_storm)
            logger.info(msg)

            for cur_init in init_time_list:
                storm_output_dir = os.path.join(series_filtered_out_dir,
                                                cur_init, cur_storm) 
                util.mkdir_p(storm_output_dir)
                util.mkdir_p(tmp_dir)
                tmp_file = "filter_" + cur_init + "_" + cur_storm
                tmp_filename = os.path.join(tmp_dir, tmp_file)
                storm_match_list = util.grep(cur_storm, filter_filename)
                with open(tmp_filename, "a+") as tmp_file:
                    for storm_match in storm_match_list:
                        tmp_file.write(storm_match)

                # Create the analysis and forecast files based
                # on the storms defined in the tmp_filename created
                # above, and store these in the series_filtered_out_dir.
                util.retrieve_and_regrid(tmp_filename, cur_init, 
                                         cur_storm, tile_dir, logger,p)

    # Clean up the tmp directory             
    subprocess.call(["rm", "-rf", tmp_dir])
    
    # Now generate the arguments to the MET Tool: series_analyis.
    print("before series analysis call, tile_dir: ", tile_dir)
    for cur_init in init_time_list:
        # Get all the storm ids for storm track pairs that 
        # correspond to this init time.
        storm_match_list = get_storms_for_init(cur_init, tile_dir, logger)    

        if not storm_match_list:
            msg = ('INFO|['+ cur_filename + ':' + cur_function + 
                   ']| No storm ids found, try next init time...')
            logger.info(msg)
            continue
        else:
            #for cur_storm in storm_list:
            for cur_storm in storm_match_list:
                
                # Generate the -fcst, -obs, -config, and 
                # -out parameter values for invoking
                # the MET series_analysis binary.
                output_dir = os.path.join(series_out_dir, cur_init, 
                                          cur_storm)
                print("output_dir: ", output_dir) 
                # First get the filenames for the gridded forecast and 
                # analysis 30x30 tiles that were created by 
                # extract_tiles. These files are aggregated by 
                # init time and storm id.
                anly_grid_regex = ".*ANLY_TILE_F.*grb2"
                fcst_grid_regex = ".*FCST_TILE_F.*grb2"
                anly_grid_files = util.get_files(series_filtered_out_dir, 
                                                 anly_grid_regex, logger)
                fcst_grid_files = util.get_files(series_filtered_out_dir,
                                                 fcst_grid_regex, logger)
               
                # Now do some checking to make sure we aren't 
                # missing either the forecast or
                # analysis files, if so log the error and exit.
                if not anly_grid_files or not fcst_grid_files:
                     msg = ('INFO|[' + cur_filename + ':' + 
                            cur_function + ']| ' +
                            'No gridded analysis or forecast' +
                            ' files found, continue')
                     logger.info(msg)
                     continue

                # Generate the -fcst portion (forecast file)
                # -fcst file_1 file_2 file_3 ... file_n
                # or
                # -fcst fcst_ASCII_filename
                # where fcst_ASCII_filename contains the full file path
                # and filename of each gridded fcst file.
                # The latter is preferred when dealing with a large 
                # number of files.
        
                # Create an ASCII file containing the forecast files. 
                fcst_ascii_fname_parts = ['FCST_ASCII_FILES_',cur_storm ]
                fcst_ascii_fname = ''.join(fcst_ascii_fname_parts)
                fcst_ascii = os.path.join(series_filtered_out_dir, 
                                          fcst_ascii_fname)
               

                # Sort the files in the fcst_grid_files list.
                sorted_fcst_grid_files = sorted(fcst_grid_files)
                tmp_fcst_param = ''
                for cur_fcst in sorted_fcst_grid_files:          
                    cur_tile = os.path.basename(cur_fcst)
                    tmp_fcst_param +=  cur_fcst
                    tmp_fcst_param += '\n'
              

                # Now create the ASCII file
                try:
                    with open(fcst_ascii, 'a') as f:
                        f.write(tmp_fcst_param)
                except IOError as e:
                    msg = ("ERROR|[" + cur_filename + ":" + 
                           cur_function + "]| " + 
                           "Could not create requested ASCII file:  " + 
                           fcst_ascii)
                    logger.error(msg)
                fcst_param_parts = ['-fcst ', fcst_ascii]
                fcst_param = ''.join(fcst_param_parts)

                # Generate the -obs portion (analysis file)
                # These are the gridded observation files.
                # -obs obs_file1 obs_file2 obs_file3 ... obs_filen
                # or
                # -obs obs_ASCII_filename
                # where obs_ASCII_filename contains the full file path
                # and filename of each gridded analysis file.

                # Create an ASCII file containing a list of all 
                # the analysis tiles.
                anly_ascii_fname_parts = ['ANLY_ASCII_FILES_',cur_storm ]
                anly_ascii_fname = ''.join(anly_ascii_fname_parts)
                anly_ascii = os.path.join(series_filtered_out_dir,
                                          anly_ascii_fname)
                obs_param_parts = [' -obs ', anly_ascii]
                obs_param = ''.join(obs_param_parts)

                # Sort the files in the anly_grid_files list.
                sorted_anly_grid_files = sorted(anly_grid_files)
                tmp_obs_param = ''
                for cur_anly in sorted_anly_grid_files:          
                    tmp_obs_param += cur_anly 
                    tmp_obs_param += '\n'

                # Now create the ASCII file
                try:
                    with open(anly_ascii, 'a') as f:
                        f.write(tmp_obs_param)
                except IOError as e:
                    msg = ("ERROR|[" + cur_filename + ":" + 
                           cur_function + "]| " + 
                           "Could not create requested ASCII file:  " + 
                           anly_ascii)
                    logger.error(msg)
                anly_param_parts = ['-obs ', anly_ascii]
                anly_param = ''.join(anly_param_parts)
                print("making output_dir: ", output_dir)
                util.mkdir_p(output_dir) 
                # Generate the -out portion, get the NAME and 
                # corresponding LEVEL for each variable.  
                for cur_var in var_list:
                   name,level = util.get_name_level(cur_var, logger) 
                   # Set the NAME and LEVEL environment variables, this 
                   # is required by the MET series_analysis binary.
                   os.environ['NAME'] = name
                   os.environ['LEVEL'] = level
                   series_anly_output_parts = [output_dir, '/',
                                               'series_', name,'_',
                                               level, '.nc']
                   series_anly_output_fname = ''.join(
                                             series_anly_output_parts)
                   
                   out_param_parts = ['-out ', series_anly_output_fname]
                   out_param = ''.join(out_param_parts)
                   print("out_param: ", out_param)

                   # Now put everything together to create the 
                   # command for running the MET series_analysis binary:
                   # -fcst <file> -obs <obs_file> -out <output file> 
                   # -config <series analysis config file>
                   command_parts = [series_analysis_exe, ' ', 
                                    fcst_param, ' ', obs_param, 
                                    ' -config ', series_anly_config_file,
                                    ' ',  out_param ] 
                   command = ''.join(command_parts)
       
                   msg = ('INFO|['+ cur_filename + ':' + 
                          cur_function +  ']|' +
                          'SERIES ANALYSIS COMMAND: ' + command)
                   logger.info(msg)

                   # Using shell=True because we aren't relying 
                   # on external input for creating the command 
                   # to the MET series analysis binary
                   print("series analysis cmd: ", command)
                   met_result = subprocess.check_output(command, 
                                               stderr=subprocess.STDOUT,
                                               shell=True)
                   logger.info('INFO|[MET series analysis] :' + 
                               met_result)
                   
                   # Now we need to invoke the MET tool 
                   # plot_data_plane to generate plots that are
                   # recognized by the MET viewer.
                   # Get the number of forecast tile files, 
                   # the name of the first and last in the list
                   # to be used by the -title option.
                   num,beg,end = get_fcst_file_info(series_filtered_out_dir, 
                                                    cur_init, cur_storm,
                                                    logger)

                   # Assemble the input file, output file, field string, 
                   # and title
                   plot_data_plane_input_fname = series_anly_output_fname
                   for cur_stat in stat_list:
                       plot_data_plane_output = [output_dir,
                                                 '/series_',
                                                 name, '_',
                                                 level,'_',
                                                 cur_stat,'.ps' ]
                       plot_data_plane_output_fname = ''.join(
                                                   plot_data_plane_output)
                       os.environ['CUR_STAT'] = cur_stat 
                       # Create versions of the arg based on
                       # whether the background map is requested
                       # in constants_pdef.py.
                       if background_map:
                           # Flag set to True, draw background map.
                           field_string_parts = ["'name=",'"series_cnt_', 
                                                 cur_stat,'";', 
                                                 'level="', level, '";',  
                                                 "'"]
                       else:
                           field_string_parts = ["'name=",'"series_cnt_', 
                                                 cur_stat,'";', 
                                                 'level="', level, '";',  
                                                 map_data,"'"]
                       
                       field_string = ''.join(field_string_parts)
                       print("field_string: ", field_string)
                       title_parts = [' -title "GFS Init ', cur_init, 
                                      ' Storm ',cur_storm, ' ', 
                                      str(num), ' Forecasts (', 
                                      str(beg), ' to ', str(end), 
                                     '), ', cur_stat, ' for ', 
                                     cur_var, '"' ]
                       title = ''.join(title_parts)
                     
                       # Now assemble the entire plot data plane command
                       data_plane_command_parts = [plot_data_plane_exe, 
                                            ' ',
                                            plot_data_plane_input_fname,
                                            ' ', 
                                            plot_data_plane_output_fname,
                                            ' ', \
                                            field_string,' ', title ]

                       data_plane_command = ''.join(
                                             data_plane_command_parts)
                       msg = ("INFO|[" + cur_filename + ":" +
                              cur_function + 
                              "]| DATA_PLANE_COMMAND: " + 
                              data_plane_command)
                       logger.info(msg)
                       # Using shell=True because we aren't 
                       # relying on external input 
                       # for creating the command to the MET series 
                       # analysis binary
                       data_plane_result = subprocess.check_output(
                                             data_plane_command,
                                             stderr=subprocess.STDOUT,
                                             shell=True)
                       msg = ('INFO|[MET data plane]: ' +
                                   data_plane_result)
                       logger.info(msg)

                       # Now assemble the command to convert the 
                       # postscript file to png
                       png_fname = plot_data_plane_output_fname.replace(
                                                   '.ps','.png')
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
                       logger.info('INFO|[convert ]: ' + convert_results)
                                 
      
def get_fcst_file_info(dir_to_search, cur_init, cur_storm, logger):
    ''' Get the number of all the gridded forecast 30x30 tile 
        files for a given storm id and init time
        (created by extract_tiles). Determine the filename of the 
        first and last files.  This information is used to create 
        the title value to the -title opt in plot_data_plane.
    
        Args:
           dir_to_search: The directory of the gridded files of interest.
           cur_init:  The init time of interest.
           cur_storm:  The storm id of interest.
           logger:  The logger to which all logging messages 
                    will be directed.


        Returns:
           num, beg, end:  A tuple representing the number of 
                           forecast tile files, and the first and 
                           last file.
        

    '''

    # For logging 
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    
   
    # Get a sorted list of the forecast tile files for the init 
    # time of interest for all the storm ids and return the 
    #forecast hour corresponding to the first and last file.
    #base_dir_to_search = os.path.join(output_dir, cur_init)
    gridded_dir = os.path.join(dir_to_search, cur_init, cur_storm)
    print("gridded_dir -e.g. the dir to search: ", gridded_dir)
    search_regex = ".*FCST_TILE.*.grb2"
    files_of_interest = util.get_files(gridded_dir, search_regex,  
                                       logger)
    sorted_files = sorted(files_of_interest)
    if len(files_of_interest) == 0:
        msg = ("ERROR:|[" + cur_filename + ":" +
               cur_function + "]|exiting, no files found for " +
               "init time of interest")
        logger.error(msg)
        sys.exit(1)

    first = sorted_files[0]
    last = sorted_files[-1]

    # Extract the forecast hour from the first and last
    # filenames.
    match_beg = re.search(".*FCST_TILE_(F[0-9]{3}).*.grb2", first)
    match_end = re.search(".*FCST_TILE_(F[0-9]{3}).*.grb2", last)
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
   
    return num,beg,end
     
        

def get_storms_for_init(cur_init, out_dir_base, logger):
    ''' Retrieve all the filter files which have the .tcst
        extension.  Inside each file, extract the STORM_ID
        and append to the list, storm_list.  
        
        Args:
           cur_init : the init time

           out_dir_base (string):  The directory where one should start
                                   searching for the filter file(s)
                                   - those with a .tcst file extension.

           logger : The logger to which all log messages are directed. 

        Returns:
           storm_dict: A dict of all the storms ids aggregated by 
                      init times (i.e. key=init time, 
                      value = list of storm ids corresponding to that
                      init time)
 
    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    filter_set = set()
    storm_list = []

    # Retrieve filter files, first create the filename
    # by piecing together the out_dir_base with the cur_init.
    filter_file = os.path.join(out_dir_base, 'filter.tcst')
    
    # Now that we have the filter filename for the init time, let's
    # extract all the storm ids in this filter file.
    storm_list = util.get_storm_ids(filter_file,logger)
        
    return storm_list
    
    
    
        
def cleanup_ascii(init_list, p, logger):
    ''' Remove any pre-existing FCST and ANLY ASCII
        files.

        Args:
            init_list:  A list containing the init times.
            p:  The ConfigMaster used to retrieve parameter values
            logger :  The logger to which any logging messages 
                      will be sent.

        Returns:
            None:  removes any existing FCST and ANLY ASCII files
                   containing a list of the gridded tiles from 
                   the extract_tiles script.
    
  
    '''
    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    fcst_ascii_regex = p.opt["FCST_ASCII_REGEX_INIT"]
    anly_ascii_regex = p.opt["ANLY_ASCII_REGEX_INIT"]
    out_dir_base = p.opt["SERIES_INIT_FILTERED_OUT_DIR"]
    rm_exe = p.opt["RM_EXE"]
    
    # Check for non-existent or empty directory, if empty,  no need to
    # proceed.
    if not os.path.exists(out_dir_base):
        return
    if os.listdir(out_dir_base) == []:
        return

    for cur_init in init_list:
        storm_list = get_storms_for_init(cur_init, out_dir_base, logger)
        for cur_storm in storm_list:
            output_dir_parts = [out_dir_base,'/',
                                cur_init,'/',cur_storm,'/']
            output_dir = ''.join(output_dir_parts)
            for root,directories,files in os.walk(output_dir):
                for cur_file in files:
                    fcst_match = re.match(fcst_ascii_regex, cur_file)
                    anly_match = re.match(anly_ascii_regex, cur_file)
                    rm_command_parts = [rm_exe, ' ', output_dir,
                                        '/', cur_file]
                    rm_cmd = ''.join(rm_command_parts)
                    if fcst_match:
                        os.system(rm_cmd)
                    if anly_match:
                        os.system(rm_cmd)




if __name__ == "__main__":
    p = P.Params()
    p.init(__doc__)
    logger = util.get_logger(p)
    analysis_by_init_time()
