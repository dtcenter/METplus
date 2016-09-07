#!/usr/bin/python
from __future__ import print_function

import constants_pdef as P
import logging
import re
import os
import sys
import met_util as util
import errno

def run_series_analysis(type):
    ''' Perform a series analysis of extra tropical cyclone
        paired data based on either lead time (forecast hour) or
        init time (YYYYMMDDhh).  This involves invoking the
        run_series_analysis script, followed by generating graphics
        using the plot_data_plane and convert.  The series analysis by
        lead time will also generate an animated gif.

        A pre-requisite is the presence of the filter file and storm files
        (currently 30 x 30 degree tiles) for the specified init and lead times.
   
        Args:
            type (string):  The method to be employed for running the series analysis- lead (forecast hour) or
                           init.  

        Returns:
            None: creates graphics corresponding to the extra tropical cyclone data specified by init time or lead time



    '''
    # Retrieve the parameters from the param file and
    # perform any necessary set-up.
    p = P.Params()
    p.init(__doc__)
    fhr_beg = p.opt["FHR_BEG"]
    fhr_end = p.opt["FHR_END"]
    out_dir = p.opt["OUT_DIR"]
    proj_dir = p.opt["PROJ_DIR"]

    plot_data_plane_exe = p.opt["PLOT_DATA_PLANE"]
    var_list = p.opt["VAR_LIST"]
    stat_list = p.opt["STAT_LIST"]
    init_time_list = p.opt["INIT_LIST"]
    logger = util.get_logger(p)
    
    cur_ = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name 

    # Convert method type of 'lead' or 'init' to uppercase for easier checking later on...
    series_method_type = type.upper() 


    # Generate the commands for invoking the series_analysis script.  The commands will be different, as they
    # are based on either the init time or lead (fcst hour) time.
    if series_method_type == 'LEAD':
        # Series analysis based on lead (forecast hour)
        try:
            analysis_by_lead_time(proj_dir, fhr_beg, fhr_end, out_dir, var_list, stat_list, logger, p)
                
        except OSError as e:
            # Since Python 2.6 doesn't have FileNotFoundError until Python 3.3 
            if e.errno == errno.ENOENT:
                logger.error("ERROR: Analysis by lead time, tiles don't exist")
            else:
                raise
        
        
    elif series_method_type == 'INIT':
        # Series analysis based on init time
        logger.info(cur_ + "|" + cur_function + "series analysis by init time")
    else:
       # Unrecognized method type requested
       logger.error("ERROR: Unrecognized method requested for performing series analysis")
       raise ValueError("Unrecognized series analysis method was requested: only LEAD and INIT are currently supported")
          

    
def analysis_by_lead_time(proj_dir, fhr_beg, fhr_end, out_dir, var_list, stat_list, logger, p):
    '''Invoke the series_analysis script based on lead time (forecast hour) 
       Create the command:
         series_analysis -fcst <OUT_DIR>/FCST_FILES_F<CUR_FHR>
                         -obs <OUT_DIR>/ANLY_FILES_F<CUR_FHR>
                         -out <OUT_DIR>/series_F<CURR_FHR_<NAME>_<LEVEL>.nc 
                         -config SeriesAnalysisConfig_by_lead

      Args:
        proj_dir:   The topmost directory where the grib2 storm track files 
                    reside.

        fhr_beg:    The beginning forecast hour.
        
        fhr_end:    The ending forecast hour.
 
        out_dir:    The output directory, where output will be saved.

        var_list:   A list of variables to process.
 
        stat_list:  A list of statistics of interest.

        logger  :   The logging object to which logging will be saved.

        p:          The handle to the config master.  



      Returns:
        None:       Creates graphics plots for files corresponding to each
                    forecast lead time.



    '''
    
    # Check for the existence of the storm track tiles and raise an error if these are missing.
    # Get a list of the grb2 forecast tiles in <proj_dir>/series_analysis/*/*/FCST_TILE_F<cur_fhr>.grb2
    tile_dir_list = [proj_dir,'/series_analysis/']
    tile_dir = ''.join(tile_dir_list)
    anly_regex = "ANLY_TILE_F[0-9]{3}.*.grb2"
    anly_tiles = get_files(tile_dir,anly_regex)
    fcst_regex = "FCST_TILE_F[0-9]{3}.*.grb2"
    fcst_tiles = get_files(tile_dir,fcst_regex)
    num_anly_tiles = len(anly_tiles)
    num_fcst_tiles = len(fcst_tiles)
    series_analysis_exe = p.opt["SERIES_ANALYSIS"]

    # Preliminary check for mismatched fcst and analysis
    # regridded tiles.
    if num_anly_tiles != num_fcst_tiles:
        # Something is wrong, we are missing
        # either an ANLY tile file or a FCST tile
        # file, this presages an issue.
        logger.warn("WARNING: There are a different number of anly and fcst tiles, there should be the same number...")
         
    # Check that there are analysis and forecast tiles (which were, or should have been created earlier by extract_tiles).
    if num_anly_tiles == 0 :
        # Cannot proceed, either the necessary 30x30 degree analysis tiles are missing
        logger.error("ERROR: No anly tile files were found  "+ tile_dir)
        raise OSError("No anlysis tiles were found")
    elif num_fcst_tiles == 0 :
        # Cannot proceed, either the necessary 30x30 degree fcst tiles are missing
        logger.error("ERROR: No fcst tile files were found  "+ tile_dir)
        raise OSError("No fcst tiles were found")
    else:
        # Create the command for running the series_analysis application
        logger.info("Creating the command for series_analysis...")    
    
        # Gather all the regridded 30x30 tiles that correspond to the lead time range and
        # save these to an ASCII file, one for analysis tiles and another for forecast tiles.
        # These files are passed into the command for running series_analysis under the -fcst and -obs
        # options.
        anly_file_regexp = ".*/([0-9]{8}_[0-9]{2}/.*/ANLY_TILE_F([0-9]{3}).*_([0-9]{8}_[0-9]{4}_[0-9]{3})).grb2"
        fcst_file_regexp = ".*/([0-9]{8}_[0-9]{2}/.*/FCST_TILE_F([0-9]{3}).*_([0-9]{8}_[0-9]{4}_[0-9]{3})).grb2"
    
        # Get the series analysis config file based on the 
        # type/methodology of  series analysis: by lead or by init time
        series_anly_configuration_file = p.opt["CONFIG_BY_LEAD"]
   
        # Create the -fcst param and -obs param, these are just the
        # filenames of the ASCII files that contain a list of the
        # FCST and ANLY tile files.

        # Retrieve all the forecast tiles that correspond to the
        # forecast range of interest (lead times)
        for fcst in fcst_tiles:
            prog = re.compile(fcst_file_regexp)
            match_fcst = re.match(prog,fcst)
            storm_subdir = match_fcst.group(1)
            fcst_hr = match_fcst.group(2)
            lead_out_dir_parms = [out_dir, '/series_F',fcst_hr]
            lead_out_dir = ''.join(lead_out_dir_parms)
            fcst_files_hr_list = ['FCST_FILES_F', fcst_hr]
            fcst_files_hr_dir = ''.join(fcst_files_hr_list)
            anly_files_hr_list = ['ANLY_FILES_F', fcst_hr]
            anly_files_hr_dir = ''.join(anly_files_hr_list)
            ascii_fcst_tiles_path = os.path.join(lead_out_dir, fcst_files_hr_dir) 
            ascii_fcst_tiles_filename = os.path.join(lead_out_dir, fcst_files_hr_dir)
            ascii_anly_tiles_filename = os.path.join(lead_out_dir, anly_files_hr_dir)
            fcst_tile_file_parts = [lead_out_dir,'/FCST_FILES_F',fcst_hr,'.grb2']
            fcst_tile_file_list = ''.join(fcst_tile_file_parts)            

            # Create the directory where the fcst and anly ASCII files will reside
            fcst_anly_tile_file_dir_parts = [lead_out_dir,'/FCST_FILES_F',fcst_hr]
            fcst_anly_tile_file_dir = ''.join(fcst_anly_tile_file_dir_parts)
            util.mkdir_p(lead_out_dir)  


            # For each FCST_TILE_F<cur_fhr>*.grb2 file, check if there is a corresponding
            # ANLY_TILE_F<cur_fhr>*.grb2 file.  If it doesn't exist, log this info and 
            # proceed to the next FCST_TILE_F file, since there isn't always a one-to-one
            # match between all FCST and ANLY tile files.  The ANLY Tile files only encompass 
            # the 000 lead time (fcst hour), whereas the FCST Tile files encompass 003, 006, 012,
            # 018, 024, 030, ...etc. hour lead times (forecast hours). Expect only one ANLY file
            # to match for every yyyymmdd_HH (init time) grouping.
            anly_tile_file = find_matching_tile(fcst)
            if anly_tile_file not in anly_tiles:
                logger.info("No analysis tile file "+ anly_tile_file +" for this forecast hour and fcst file " + fcst "  continuing...")
            
            else: 
                # Create two ASCII files, one which lists all the ANLY tile files and another for 
                # all the FCST tile files
                # Proceed with saving/appending the analysis and forecast filenames to their corresponding ASCII files.
                # ASCII file containing all FCST files
                create_ascii_file('FCST', ascii_fcst_tiles_filename, fcst, logger)  
                create_ascii_file('ANLY', ascii_anly_tiles_filename, anly_tile_file, logger)  
    
                # Create the -fcst and -obs params
                fcst_param_list = ['-fcst ', ascii_fcst_tiles_filename]
                fcst_param = ''.join(fcst_param_list)
                obs_param_list = ['-obs ', ascii_anly_tiles_filename]
                obs_param = ''.join(obs_param_list)
                logger.info("fcst param: "+fcst_param)
                logger.info("obs param: "+ obs_param)

                # Create the series analysis command
                config_param_list = ['-config  ', series_anly_configuration_file]
                config_param = ''.join(config_param_list)
    

                # Create the -out param and invoke the series_analysis script
                for cur_var in var_list:
                    # Get the name and level which are needed to create the -out param
                    # and set the NAME and LEVEL environment variables which are required by the 
                    # series_analysis application
                    match = re.match(r'(.*)/(.*)',cur_var)
                    name = match.group(1)
                    level = match.group(2)
                    os.environ['NAME'] = name
                    os.environ['LEVEL'] = level  
                    out_param_list = ['-out ', out_dir,'/series_F',fcst_hr,'/', 'series_F',fcst_hr,'_', name, '_', level, '.nc']
                    out_param = ''.join(out_param_list)  
                    logger.info("out param: "+ out_param)
    
                # Create the full series analysis command
                series_analysis_cmd_list = [series_analysis_exe,' ', fcst_param, ' ', obs_param, ' ', config_param, ' ', out_param]
                series_analysis_cmd = ''.join(series_analysis_cmd_list)
                logger.info("series analysis cmd: "+series_analysis_cmd)
                os.system(series_analysis_cmd)                    

    # Create the output directory for the animation plots
    animation_dir = os.path.join(proj_dir, '/series_analysis/series_animat')
    logger.info("Creating animation directory " + animation_dir

    # Generate a plot for each variable of interest
    for var in var_list:
        match = re.match(r'(.*)/(.*)',cur_var)
        name = match.group(1)
        level = match.group(2)
        os.environ['NAME'] = name
        os.environ['LEVEL'] = level  
            
        for stat in stat_list:
            # Set the CUR_STAT environment variable required by the plot data plane binary  
            os.environ['CUR_STAT'] = stat

            # Retrieve all the netCDF files that were created by the run series analysis step above
            anly_regex = "ANLY_TILE_F[0-9]{3}.*.grb2"
            anly_tiles = get_files(tile_dir,anly_regex)
            nc_regex = "*.nc"
            # TODO finish this section, figure out how to get the dir where the netCDF files are saved 
            # as a result of running the run series analysis step 
            nc_dir_parts = [proj_dir,'/series_analysis/series_F]
            nc_dir = ''.join(nc_dir_parts)
            

             


def create_ascii_file(type, ascii_tiles_filename, tiles_filename, logger):
    ''' Create an ASCII file containing a list of the 30 x 30 tile files that
        were created by extract_tiles.

        Args:
           type (string): The type of tile, either FCST or ANLY.
           ascii_tiles_filename (string): The filename that will contain a list of
                                          all the fcst or anly 
                                          30x30 tile files.
           tiles_filename : The full filename of the 30x30 tile file
           logger:  The logger to which all logging occurs
  
        Returns:
           ascii_output_file : An ASCII file with the full filepath of the tiles corresponding
                        to the type requested  (FCST or ANLY)

    '''

    
    try:
        with open(ascii_tiles_filename, 'a') as ascii_output_file:
            ascii_output_file.write(tiles_filename)   
            ascii_output_file.write("\n")
            
    except IOError as e:
        logger.error("Could not create requested ASCII file ") 



def find_matching_tile(fcst_file):
    ''' Find the corresponding ANLY 30x30 tile file to the 
        fcst tile file.
       
        Args:
          fcst_file_list (string):  The fcst file (full path) that 
                               is used to derive the corresponding
                               analysis file name.

        Returns:
          anly_from_fcst (string): The name of the analysis tile file
                                   that corresponds to the same lead time
                                   as the input fcst tile. 
    '''
    
    # Derive the ANLY file name from the FCST file.
    anly_from_fcst = re.sub(r'FCST','ANLY', fcst_file)

    return anly_from_fcst



def get_files(filedir, filename_regex):
    ''' Get all the files (with a particular
        naming format) by walking 
        through the directories.
    
        Args:
          filedir (String):  The topmost directory from which the
                             search begins.
          filename_regex (string):  The regular expression that
                                    defines the naming format
                                    of the files of interest.
       Returns:
          file_paths (string): a list of filenames (with full filepath)       

    '''
    file_paths = []
    # Walk the tree
    for root, directories, files in os.walk(filedir):
        for filename in files:
            # add it to the list only if it is a match
            # to the specified format
            #prog = re.compile(filename_regex)
            match = re.match(filename_regex, filename)
            
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root,filename)
                file_paths.append(filepath)
            else:
                continue
    return file_paths


if __name__ == "__main__":
    run_series_analysis("lead")
#    run_series_analysis("init")

