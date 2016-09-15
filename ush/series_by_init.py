#!/usr/bin/python

from __future__ import print_function

import constants_pdef as P
import logging
import re
import os
import sys
import met_util as util
import errno


def main():
    # Create ConfigMaster param object
    p = P.Params()
    p.init(__doc__)    
    logger = util.get_logger(p)

    analysis_by_init_time(p,logger)



def analysis_by_init_time(p,logger):
    ''' Invoke the series analysis script based on
        the init time in the format YYYYMMDD_hh

         Args:
             p: The ConfigMaster param object
             logger:  The log to which all logging messages are sent
             

 
         Returns:
              None:  Creates graphical plots of storm tracks


    '''
    # Retrieve any necessary values from the param file(s)
    init_time_list = p.opt["INIT_LIST"]
    var_list = p.opt["VAR_LIST"]
    stat_list = p.opt["STAT_LIST"]
    proj_dir = p.opt["PROJ_DIR"]
    out_dir_base = p.opt["OUT_DIR"]
    series_anly_config_file = p.opt["CONFIG_FILE_INIT"]
    series_analysis_exe = p.opt["SERIES_ANALYSIS"]
    plot_data_plane_exe = p.opt["PLOT_DATA_PLANE"]
    convert_exe = p.opt["CONVERT_EXE"]
    tr_exe  = p.opt["TR_EXE"]
    cut_exe = p.opt["CUT_EXE"]
    ncap2_exe = p.opt["NCAP2_EXE"]
    fcst_tile_regex = p.opt["FCST_TILE_REGEX"]
    anly_tile_regex = p.opt["ANLY_TILE_REGEX"]
    

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

 
    # Check for the existence of forecast and analysis tile files
    tile_dir_parts = [proj_dir, '/series_analysis/']
    tile_dir = ''.join(tile_dir_parts)
    try:
        util.check_for_tiles(tile_dir, fcst_tile_regex, anly_tile_regex, logger)
    except OSError as e:
        logger.error("Missing 30x30 tile files.  Extract tiles needs to be run")
        raise
     
    
    # Get a list of the forecast tile files
    fcst_tiles = util.get_files(tile_dir, fcst_tile_regex, logger)
    
    for cur_init in init_time_list:
        # Get all the storm ids for storm track pairs that correspond to this
        # init time.
        storm_list = get_storms_for_init(cur_init, out_dir_base, logger)    
        if not storm_list:
            logger.error('ERROR| No storm ids found, exiting')
            sys.exit(1)
        else:
            for cur_storm in storm_list:
                
                # Generate the -fcst, -obs, -config, and -out parameter values for invoking
                # the MET series_analysis binary.
                output_dir_parts = [out_dir_base, '/',cur_init, '/',cur_storm, '/']
                output_dir = ''.join(output_dir_parts) 

                # First get the filenames for the gridded forecast and analysis 30x30 tiles
                # that were created by extract_tiles. These files are aggregated by 
                # init time and storm id.
                anly_grid_regexp = ".*ANLY_TILE_F.*grb2"
                fcst_grid_regexp = ".*FCST_TILE_F.*grb2"
                anly_grid_files = util.get_files(output_dir, anly_grid_regexp, logger)
                fcst_grid_files = util.get_files(output_dir, fcst_grid_regexp, logger)
               
                # Now do some checking to make sure we aren't missing either the forecast or
                # analysis files, if so log the error and exit.
                if not anly_grid_files or not fcst_grid_files:
                     logger.error('ERROR| No gridded analysis or forecast files found, exiting')
                     sys.exit(1)

                # Generate the -fcst portion (forecast file)
                # -fcst file_1 file_2 file_3 ... file_n
                # or
                # -fcst fcst_ASCII_filename
                # where fcst_ASCII_filename contains the full file path
                # and filename of each gridded fcst file.
                # The latter is preferred when dealing with a large number of files.
                fcst_param = '-fcst '
                for cur_fcst in fcst_grid_files:          
                    fcst_param += cur_fcst
                    fcst_param += ' '
#                logger.info('fcst param: '+fcst_param)

                # Generate the -obs portion (analysis file)
                # -obs obs_file1 obs_file2 obs_file3 ... obs_filen
                # or
                # -obs obs_ASCII_filename
                # where obs_ASCII_filename contains the full file path
                # and filename of each gridded analysis file.
                obs_param = ' -obs '
                for cur_anly in anly_grid_files:          
                    obs_param += cur_anly 
                    obs_param += ' '
#                logger.info('obs param: '+obs_param)
    
                # Generate the -out portion, get the NAME and corresponding LEVEL for
                # each variable.  
                for cur_var in var_list:
                   name,level = util.get_name_level(cur_var, logger) 
                   # Set the NAME and LEVEL environment variables, this is required
                   # by the MET series_analysis binary.
                   os.environ['NAME'] = name
                   os.environ['LEVEL'] = level
                   series_anly_output_parts = [output_dir, 'series_', name,'_',level, '.nc']
                   series_anly_output_fname = ''.join(series_anly_output_parts)
                   out_param_parts = ['-out ', series_anly_output_fname]
                   out_param = ''.join(out_param_parts)
                   #logger.info('out param: '+ out_param)

                   # Now put everything together to create the command for running the 
                   # MET series_analysis binary:
                   # -fcst <file> -obs <obs_file> -out <output file> -config <series analysis config file>
                   command_parts = [ series_analysis_exe, ' ', fcst_param, ' ', obs_param, ' -config ', series_anly_config_file, ' ',  out_param ] 
                   command = ''.join(command_parts)
                   #logger.info('command: '+ command)
                   os.system(command)
                   
                   # Now we need to invoke the MET tool plot_data_plane to generate plots that are
                   # recognized by the MET viewer.
                   # Get the number of forecast tile files, the name of the first and last in the list
                   # to be used by the -title option.
                   num,beg,end = get_fcst_file_info(fcst_tiles, logger)
                   #logger.info('num,beg, and end for title:'+ str(num) + ' ' + beg + ' ' + end)

                   # Assemble the input file, output file, field string, and title
                   plot_data_plane_input_fname = series_anly_output_fname
                   #logger.info('plot data plane input fname: '+ plot_data_plane_input_fname)
                   for cur_stat in stat_list:
                       plot_data_plane_output = [output_dir,'series_',name, '_',level,'_',cur_stat,'.ps' ]
                       plot_data_plane_output_fname = ''.join(plot_data_plane_output)
                       os.environ['CUR_STAT'] = cur_stat 
                       field_string_parts = ["'name=",'"series_cnt_', cur_stat,'";', 'level="', level, '";', "'"]
                       field_string = ''.join(field_string_parts)
                   #    logger.info('Field string: '+ field_string)
                       title_parts = [' -title "GFS Init ', cur_init, ' Storm ',cur_storm, str(num), \
                                      ' Forecasts (', beg, ' to ', end, '), ', cur_stat, ' for ', cur_var, '"' ]
                       title = ''.join(title_parts)
                   #    logger.info('Title: ' + title)
                      
                       # Now assemble the entire plot data plane command
                       data_plane_command_parts = [plot_data_plane_exe, ' ', plot_data_plane_input_fname, ' ', plot_data_plane_output_fname, ' ', \
                                                   field_string,' ', title ]
                        

                       data_plane_command = ''.join(data_plane_command_parts)
                       logger.info("data_plane_command: " + data_plane_command)
                       os.system(data_plane_command)

                       # Now assemble the command to convert the postscript file to png
                       png_fname = plot_data_plane_output_fname.replace('.ps','.png')
                       convert_parts = [convert_exe, ' -rotate 90 -background white -flatten ', plot_data_plane_output_fname,' ', png_fname]
                       convert = ''.join(convert_parts)
                   #    logger.info('Convert: '+convert)
                                 
      
def get_fcst_file_info(fcst_tiles_list, logger):
    ''' Get the number of all the gridded forecast 30x30 tile files
        created by extract_tiles, and from a sorted list, determine the filename of the first and last
        files.  This information is used to create the title value to the -title opt in plot_data_plane.
    
        Args:
           fcst_tiles_list:  A list containing the full file names of all the forecast tile files
           logger:  The logger to which all logging messages will be directed.


        Returns:
           num, beg, end:  A tuple representing the number of forecast tile files, and the first and 
                           last file.
        

    '''

    # For logging 
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    
    # Get the number of forecast tile files
    num = len(fcst_tiles_list)
   
    # Get a sorted list of the forecast tile files and only return the 
    # first and last
    sorted_fcst_tiles = sorted(fcst_tiles_list)
    beg = sorted_fcst_tiles[0]
    end = sorted_fcst_tiles[-1]

    return num,beg,end
     
        

def get_storms_for_init(cur_init, out_dir_base, logger):
    ''' Retrieve all the filter files which have the .tcst
        extension.  Inside each file, extract the STORM_ID
        and append to the list, storm_list.  
        
        Args:
           cur_init : the init time

           out_dir_base (string):  The directory where one should start
                              searching for the filter files with 
                              .tcst file extension.

           logger : The logger to which all log messages are directed. 

        Returns:
           storm_dict: A dict of all the storms ids aggregated by init times
                       (i.e. key=init time, value = list of storm ids corresponding
                        to that init time)

 
    '''
    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    logger.info(cur_function)
    filter_set = set()
    storm_list = []

    # Retrieve filter files, first create the filename
    # by piecing together the out_dir_base with the cur_init.
    filter_parts = [out_dir_base,'/',cur_init,'/filter_',cur_init, '.tcst']    
    filter_file = ''.join(filter_parts)
    
    # Now that we have the filter filename for the init time, let's
    # extract all the storm ids in this filter file.
    storm_list = util.get_storm_ids(filter_file,logger)
        
    return storm_list
    
    
    
        
     




















if __name__ == "__main__":
    main()
