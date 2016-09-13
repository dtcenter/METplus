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
    proj_dir = p.opt["PROJ_DIR"]
    out_dir_base = p.opt["OUT_DIR"]
    series_anly_config_file = p.opt["CONFIG_FILE_INIT"]
    series_analysis_exe = p.opt["SERIES_ANALYSIS"]
    plot_data_plane_exe = p.opt["PLOT_DATA_PLANE"]
    tr_exe  = p.opt["TR_EXE"]
    cut_exe = p.opt["CUT_EXE"]
    ncap2_exe = p.opt["NCAP2_EXE"]
    
    
    logger.info('Inside analysis by init time')
    logger.info('BY INIT: PROJ_DIR= ' + proj_dir + ' output dir = ' + out_dir_base)
    storm_list = get_all_storms(init_time_list,out_dir_base,logger)    
    if storm_list:
        for cur_storm in storm_list:
           logger.info('after calling function, cur storm: '+cur_storm)
    else:
        logger.info('no storm list ')
    for cur_init in init_time_list:
        ouput_dir = os.path.join(out_dir_base, cur_init)
          
    

def get_all_storms(init_list, out_dir_base, logger):
    ''' Retrieve all the filter files which have the .tcst
        extension.  Inside each file, extract the STORM_ID
        and append to the list, storm_list.  
        
        Args:
           init_time_list : A list of the init times, used in
                            searching for filter files. 

           out_dir_base (string):  The directory where one should start
                              searching for the filter files with 
                              .tcst file extension.

           logger : The logger to which all log messages are directed. 

        Returns:
           storm_list: A list of all the storms 

 
    '''

    logger.info("Retrieving all storms")
    storm_list = []
    filter_list = []
    # Retrieve filter files, first create the filename
    # by piecing together the out_dir_base with the cur_init.
    for cur_init in init_list:
        filter_parts = [out_dir_base,'/',cur_init,'/filter_',cur_init, '.tcst']    
        filter_file = ''.join(filter_parts)
        logger.info('filter file from get_all_storms: '+ filter_file)
        if filter_file not in storm_list:
            filter_list.append(filter_file)
      
    return storm_list
    
    
    
        
     




















if __name__ == "__main__":
    main()
