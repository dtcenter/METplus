#!/usr/bin/env python

'''
Program Name: extract_tiles.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Extracts tiles to be used by series_analysis History Log:  Initial version 
Usage: extract_tiles.py
Parameters: None
Input Files: tc_pairs data
Output Files: tiled grib2 files
Condition codes: 0 for success, 1 for failure

'''

from __future__ import (print_function, division )

import constants_pdef as P
import logging
import os
import sys
import met_util as util
import time
import re
import subprocess
import string_template_substitution as sts
import run_tc_stat as tcs

def main():
    '''Get TC-pairs track data and GFS model data, do any necessary 
       processing then regrid the forecast and analysis files to a 
       30x 30 degree tile centered on the storm.
      
       Args:
           None 

       Returns:

           None: invokes regrid_data_plane to create a netCDF file from two 
                 extratropical storm track files.

    '''

    # Retrieve parameters from corresponding param file
   
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    init_times = util.gen_init_list(p.opt["INIT_DATE_BEG"], p.opt["INIT_DATE_END"], p.opt["INIT_HOUR_INC"], p.opt["INIT_HOUR_END"])    
    output_dir = p.opt["OUT_DIR"]
    project_dir = p.opt["PROJ_DIR"]
    overwrite_flag = p.opt["OVERWRITE_TRACK"]
    addl_filter_opts = p.opt["EXTRACT_TILES_FILTER_OPTS"]
    filtered_out_dir = p.opt["EXTRACT_OUT_DIR"]
    tc_stat_exe = p.opt["TC_STAT"]
    regrid_data_plane_exe = p.opt["REGRID_DATA_PLANE_EXE"]


    # get the process id to be used to identify the output
    # amongst different users and runs.
    cur_pid = str(os.getpid())
    tmp_dir = os.path.join(p.opt["TMP_DIR"], cur_pid)
   
    # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
    # [File : function]| Message logger.info("INFO |  [" + 
    # cur_filename +  ":" + "cur_function] |" + "BEGIN extract_tiles")
    
    # Process TC pairs by initialization time
    for cur_init in init_times:
        msg = ("INFO| [" + cur_filename + ":" + cur_function +  
               " ] |Begin processing for initialization time: " + cur_init)
        logger.info(msg)
        year_month = util.extract_year_month(cur_init, logger)
        
       # Create the name of the filter file we need to find.  If 
       # the file doesn't exist, then run TC_STAT 
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(filtered_out_dir, cur_init, filter_filename)

        if util.file_exists(filter_name) and overwrite_flag == False:
            msg = ("INFO| [" + cur_filename + ":" + cur_function +  
                   " ] | Filter file exists, using Track data file: " + 
                   filter_name)
            logger.info(msg)
        else:
           # Create the storm track by applying the
           # filter options defined in the constants_pdef.py file.
            filter_path = os.path.join(filtered_out_dir, cur_init)
            util.mkdir_p(filter_path)
            tc_cmd_list = [tc_stat_exe, " -job filter -lookin ", 
                           project_dir,"/tc_pairs/", year_month, 
                           " -init_inc ", cur_init, 
                           " -match_points true -dump_row ", 
                           filter_name, " ", addl_filter_opts]

            # Call run_tc_stat to do the actual filtering.
            tc_cmd = ''.join(tc_cmd_list)
            tcs.tc_stat(p, logger, tc_cmd, 
                        filtered_out_dir)
            msg = ("INFO| [" + cur_filename + ":" + cur_function +  
                   " ] | tc command: " + tc_cmd)
            logger.info(msg)
            
        # Now get unique storm ids from the filter file, 
        # filter_yyyymmdd_hh.tcst
        sorted_storm_ids = util.get_storm_ids(filter_name, logger)
       
        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and 
        # search for the presence of the storm id.  Store this 
        # corresponding row of data into a temporary file in the 
        # /tmp/<pid> directory.
       
        storm_match_list = [] 
        for cur_storm in sorted_storm_ids:
            msg = ("INFO| [" + cur_filename + ":" + cur_function +  
                   " ] | Processing storm: " + cur_storm)
            logger.info(msg)
            storm_output_dir = os.path.join(filtered_out_dir,cur_init, 
                                            cur_storm)
            util.mkdir_p(storm_output_dir)
            util.mkdir_p(tmp_dir)
            tmp_file = "filter_" + cur_init + "_" + cur_storm
            tmp_filename = os.path.join(tmp_dir, tmp_file)
            
            storm_match_list = util.grep(cur_storm, filter_name)
            with open(tmp_filename, "a+") as tmp_file:
               for storm_match in storm_match_list:
                   tmp_file.write(storm_match)
               
            # Peform regridding of the forecast and analysis files 
            # to a 30 x 30 degree tile centered on the storm
            util.retrieve_and_regrid(tmp_filename, cur_init, cur_storm, filtered_out_dir,
                                     logger, p)
           

        # end of for cur_storm 
    # end of for cur_init

    # Check for empty files and directories in the filtered_out_dir 
    util.prune_empty(filtered_out_dir, p, logger)

    # Clean up the tmp directory
    subprocess.call(["rm", "-rf", tmp_dir])





if __name__ == "__main__":
    p = P.Params()
    p.init(__doc__)  ## Put description of the code here
    logger = util.get_logger(p)
    main()
