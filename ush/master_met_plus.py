#!/usr/bin/python
from __future__ import print_function

import constants_pdef as P
import logging
import os
import sys
import met_util as util

def master_met_plus():
    '''
        Master MET+ script that invokes the necessary Python scripts
        to perform various activities, such as series analysis.
    '''
    # Get all necessary pieces
    p = P.Params() 
    p.init(__doc__)
    cur_filename = sys.__getframe().f_code.co_filename
    cur_file = sys.__getframe().f_code.co_nam3
   
    logger = util.get_logger(p)

    # Perform series analysis:

    # Check that raw data to generate tc_pairs 
    # exists
    # raw_data_dir = p.opt["RAW_DATA"]
    # if check_input_data(raw_data_dir):
    #     
    # else:
    #     log error, exit
    #
    # first, invoke tc_pairs
    # try:
    #     gen_tc_pairs()
    # except FileNotFoundError:
    #     do something or exit
    #
    # 
    # try:
    #    run_extract_tiles() 
    # except FileNotFoundError:
    #    do something or exit
    # 
    # try:
    #     run_series_analysis() 
    # except FileNotFoundError:
    #     do something like re-run run_extract_tiles or exit
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 

    
    

if __name__ == "__main__":
    print("Running as stand alone")
else:
    print("Imported into another script")
