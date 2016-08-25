#!/usr/bin/python
from __future__ import print_function

import constants_pdef as P
import logging
import re
import os
import sys
import met_util as util
import errno

def run_series_analysis(type, check_input=True ):
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
            check_input(boolean): default is TRUE- check for input data before performing any tasks

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

    series_analysis_exe = p.opt["SERIES_ANALYSIS"]
    plot_data_plane_exe = p.opt["PLOT_DATA_PLANE"]
    var_list = p.opt["VAR_LIST"]
    init_time_list = p.opt["INIT_LIST"]
    log_dir = p.opt["LOG_DIR"]
    log_ = p.opt["LOG_FILENAME"]
    logger = util.get_logger(p)
   
    
    cur_ = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name 

    # Convert method type of 'lead' or 'init' to uppercase for easier checking later on...
    series_method_type = type.upper() 


    # Generate the commands for invoking the series_analysis script.  The commands will be different, as they
    # are based on either the init time or lead (fcst hour) time.
    check_input=False
    if series_method_type == 'LEAD':
        # Series analysis based on lead (forecast hour)
        if check_input:
            try:
                check_for_storm_track_files(series_method_type, fhr_beg, fhr_end, init_time_list, proj_dir)
            except ValueError:
                logger.error("ERROR: One or more storm track tiles is missing, exiting")

        try:
            analysis_by_lead_time(proj_dir, fhr_beg, fhr_end, out_dir, var_list, logger, p)
                
        except:
            logger.error("ERROR: Analysis by lead time, tiles don't exist")
        
        
    elif series_method_type == 'INIT':
        # Series analysis based on init time
        logger.info(cur_ + "|" + cur_function + "series analysis by init time")
    else:
       # Unrecognized method type requested
       logger.error("ERROR: Unrecognized method requested for performing series analysis")
       raise ValueError("Unrecognized series analysis method was requested: only LEAD and INIT are currently supported")
          

    
def analysis_by_lead_time(proj_dir, fhr_beg, fhr_end, out_dir, var_list,logger, p):
    '''Invoke the series_analysis script based on lead time (forecast hour) 
       Create the command:
         series_analysis -fcst <OUT_DIR>/FCST_FILES_F<CUR_FHR>
                         -obs <OUT_DIR>/ANLY_FILES_F<CUR_FHR>
                         -out <OUT_DIR>/series_F<CURR_FHR_<NAME>_<LEVEL>.nc 
                         -config SeriesAnalysisConfig_by_lead
    '''

    logger.info("Creating series analysis command for init time")
    
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
    print('out dir: %s', out_dir)

    if num_anly_tiles == 0 :
        # Cannot proceed, either the necessary 30x30 degree analysis tiles are missing
        logger.error("ERROR: No anly tile files were found  "+ tile_dir)
        print("ERROR: no analysis tiles found")
        raise FileNotFoundError("No anlysis tiles were found")
    elif num_fcst_tiles == 0 :
        # Cannot proceed, either the necessary 30x30 degree fcst tiles are missing
        logger.error("ERROR: No fcst tile files were found  "+ tile_dir)
        print("ERROR: no fcst tiles found")
        raise FileNotFoundError("No fcst tiles were found")
    else:
        # Create the command for running the series_analysis application
        logger.info("Creating the command for series_analysis")    
    
        # Gather all the regridded 30x30 tiles that correspond to the lead time range and
        # save these to an ASCII file, one for analysis tiles and another for forecast tiles.
        # These files are passed into the command for running series_analysis under the -fcst and -obs
        # options.
        anly_file_regexp = ".*/([0-9]{8}_[0-9]{2}/.*/ANLY_TILE_F([0-9]{3}).*_([0-9]{8}_[0-9]{4}_[0-9]{3})).grb2"
        fcst_file_regexp = ".*/([0-9]{8}_[0-9]{2}/.*/FCST_TILE_F([0-9]{3}).*_([0-9]{8}_[0-9]{4}_[0-9]{3})).grb2"
    
        # Get the -config param file name
        config_param = p.opt["CONFIG_BY_LEAD"]
   
        # Create the -fcst param
        # Retrieve all the forecast tiles that correspond to the
        # forecast range of interest (lead times)
        for fcst in fcst_tiles:
            prog = re.compile(fcst_file_regexp)
            #print("fcst file: {}".format(fcst))
            match_fcst = re.match(fcst_file_regexp,fcst)
            storm_subdir = match_fcst.group(1)
            fcst_hr = match_fcst.group(2)
            lead_out_dir_parms = [out_dir, '/series_F',fcst_hr]
            lead_out_dir = ''.join(lead_out_dir_parms)
            fcst_param_list = [lead_out_dir,'/FCST_FILES_F',fcst_hr, '.grb2']
            fcst_param = ''.join(fcst_param_list)            
            print("fcst_param: %s", fcst_param)

            # Create the -obs param
            # Retrieve all the analysis tiles that correspond to the
            # forecast range of interest
            for anly in anly_tiles:
                prog = re.compile(anly_file_regexp)
                #print("anly file: {}".format(anly))
                match_anly = re.match(anly_file_regexp,anly)
                anly_fcst_hr = match_anly.group(2)
            
                obs_param_list = [out_dir_param, '/ANLY_FILES_F', anly_fcst_hr, '.grb2']
                obs_param = ''.join(obs_param_list)
                #print("obs_param: %s",obs_param)
            
            # Create the -out param and invoke the series_analysis script
            for cur_var in var_list:
                # Get the name and level which are needed to create the -out param
                match = re.match(r'(.*)/(.*)',cur_var)
                name = match.group(1)
                level = match.group(2)
                out_param_list = [out_dir,'/series_F',fcst,'_', name, '_', level, '.nc']
                out_param = ''.join(out_param_list)  
                #print("full args: %s",out_param)
            




def check_for_storm_track_files(series_method_type, fhr_beg, fhr_end, init_time_list, proj_dir):
    # TODO implement this, for now return True
    return True


def get_files(filedir, filename_regex):
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
    run_series_analysis("lead" )
#    run_series_analysis("init")

