#!/usr/bin/env python

'''
Program Name: run_tc_pairs.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Runs tc_pairs to parse ADeck and BDeck ATCF files, filter the data, and match them up
History Log:  Initial version 
Usage: run_tc_pairs.py
Parameters: None
Input Files: adeck and bdeck files
Output Files: tc_pairs files
Condition codes: 0 for success, 1 for failure

'''

from __future__ import (print_function, division )

import constants_pdef as P
import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess


def read_modify_write_file(in_csvfile, MM, p, out_csvfile, logger):

    # Used for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Open the output csv file
    out_file = open(out_csvfile, "wb")
    # Tell the write to use the line separator "\n" instead of the DOS "\r\n"
    writer = csv.writer(out_file, lineterminator="\n")
    
    with open(in_csvfile) as csvfile:

        in_file_reader = csv.reader(csvfile)
        for index, row in enumerate(in_file_reader):
            
            # Create a list for the modified lines
            row_list = []
            
            # Replace the second column (storm number) with the month followed by the storm number
            # e.g. Replace 0006 with 010006
            row[1] = " " + MM + (row[1]).strip()

            # Iterate over the items, deleting or modifying the columns
            for item in row:
            
                # Delete the third column
                if item == row[2]:
                    continue
                # Replace MISSING_VAL_TO_REPLACE with MISSING_VAL
                elif (item.strip() == p.opt["MISSING_VAL_TO_REPLACE"]):
                    item = " " + p.opt["MISSING_VAL"]
                # Create a new row to write
                row_list.append(item)

            # Write the modified file
            writer.writerow(row_list)

    csvfile.close()
    out_file.close()
                            

    
def main():
    
    # Retrieve parameters from corresponding param file
    p = P.Params()
    p.init(__doc__)  ## Put description of the code here
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    logger = util.get_logger(p)

    # Get the desired YYYYMM from INIT_LIST
    YYYYMM_list = []
    for init in p.opt["INIT_LIST"]:
        if init[0:6] not in YYYYMM_list:
            YYYYMM_list.append(init[0:6])

    # Set up the environment variable to be used in the TCPairs Config file (TC_PAIRS_CONFIG_PATH)
    # Used to set init_inc in "TC_PAIRS_CONFIG_PATH"
    # Need to do some pre-processing so that Python will use " and not ' because currently MET
    # doesn't support single-quotes
    tmp_init_string = str(p.opt["INIT_LIST"])
    tmp_init_string = tmp_init_string.replace("\'","\"")
    os.environ['INIT_INC'] = tmp_init_string

    # Get a directory path listing of the dated subdirectories (YYYYMM format) in the track_data directory
    dir_list = []
    for YYYYMM in os.listdir(p.opt["TRACK_DATA_DIR"]):
        if os.path.isdir(os.path.join(p.opt["TRACK_DATA_DIR"], YYYYMM)):
            if (YYYYMM in YYYYMM_list):
                dir_list.append(os.path.join(p.opt["TRACK_DATA_DIR"], YYYYMM))

    
    if (dir_list == []):
        logger.warning("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "There are no dated sub-directories (YYYYMM) with input data as expected in: " + p.opt["TRACK_DATA_DIR"])
        exit(0)
       
    # Get a list of files in the dated subdirectories 
    for mydir in dir_list:
        myfiles = os.listdir(mydir)
        # Need to do extra processing if track_type is extra_tropical_cyclone
        if (p.opt["TRACK_TYPE"] == "extra_tropical_cyclone"):
            
            # Create an atcf output directory for writing the modified files
            adeck_mod = os.path.join(p.opt["TRACK_DATA_SUBDIR_MOD"], os.path.basename(mydir))
            bdeck_mod = os.path.join(p.opt["TRACK_DATA_SUBDIR_MOD"], os.path.basename(mydir))

            # If the output directory doesn't exist, create it
            if not os.path.exists(adeck_mod):
                mkdir_cmd = "mkdir -p %s" % (adeck_mod)
                logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Making output directory: " + adeck_mod)
                ret = subprocess.check_output(mkdir_cmd, stderr=subprocess.STDOUT, shell=True)
                if ret != 0:
                    logger.error("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "Problem executing: " + mkdir_cmd)
                    exit(0)
        
        # Iterate over the files, modifying them and writing new output files if necessary ("extra_tropical_cyclone" track type), and run tc_pairs
        for myfile in myfiles:
            
            # Check to see if the files have the ADeck prefix
            if myfile.startswith(p.opt["ADECK_FILE_PREFIX"]):
                
                # Create the output directory for the pairs, if it doesn't already exist
                pairs_out_dir = os.path.join(p.opt["TC_PAIRS_DIR"], os.path.basename(mydir))
                if not os.path.exists(pairs_out_dir):
                    mkdir_cmd = "mkdir -p %s" % (pairs_out_dir)
                    logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Making output directory: " + pairs_out_dir)
                    ret = subprocess_check_output(mkdir_cmd, stderr=subprocess.STDOUT, shell=True)
                    if ret != 0:
                        logger.error("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "Problem executing: " + mkdir_cmd)
                        exit(0)
                    

                # Need to do extra processing if track_type is extra_tropical_cyclone
                if (p.opt["TRACK_TYPE"] == "extra_tropical_cyclone"):

                    # Form the adeck and bdeck input filename paths
                    adeck_in_file_path = os.path.join(mydir, myfile)
                    bdeck_in_file_path = re.sub(p.opt["ADECK_FILE_PREFIX"],p.opt["BDECK_FILE_PREFIX"], adeck_in_file_path)
                    adeck_file_path = os.path.join(adeck_mod, myfile)
                    bdeck_file_path = os.path.join(bdeck_mod, re.sub(p.opt["ADECK_FILE_PREFIX"],p.opt["BDECK_FILE_PREFIX"], myfile))
    
                    # Get the storm number e.g. 0004 in amlq2012033118.gfso.0004
                    split_basename = myfile.split(".")
                    storm_num = split_basename[-1]
    
                    # Get the YYYYMM e.g 201203 in amlq2012033118.gfso.0004
                    YYYYMM = myfile[4:10]
            
                    # Get the MM from the YYYYMM
                    MM = YYYYMM[-2:]

                    # HERE
                    # Before calling this function (twice below) check to see if the output file exists already.  If it does exist
                    # either check a force overwrite option (add) or log a message telling the user to delete the existing data
                    # if they want a fresh run

                    
                    # Read in the adeck file, modify it, and write a new adeck file
                    # Check for existence of data and overwrite if desired
                    if os.path.exists(adeck_file_path):
                        if (p.opt["TRACK_DATA_MOD_FORCE_OVERWRITE"]):
                            logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Writing modified csv file: " + adeck_file_path + ", replacing existing data because TRACK_DATA_MOD_FORCE_OVERWRITE is set to True")
                            read_modify_write_file(adeck_in_file_path, MM, p, adeck_file_path, logger)
                        else:
                            logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Using existing modified csv file: "  + adeck_file_path + ", because TRACK_DATA_MOD_FORCE_OVERWRITE is set to False")
                    else:
                        logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Writing modified csv file: " + adeck_file_path)
                        read_modify_write_file(adeck_in_file_path, MM, p, adeck_file_path, logger)
                
                    # Read in the bdeck file, modify it, and write a new bdeck file
                    # Check for existence of data and overwrite if desired
                    if os.path.exists(bdeck_file_path):
                        if (p.opt["TRACK_DATA_MOD_FORCE_OVERWRITE"]):
                            logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Writing modified csv file: "  + bdeck_file_path + ", replacing existing data because TRACK_DATA_MOD_FORCE_OVERWRITE is set to True")
                            read_modify_write_file(bdeck_in_file_path, MM, p, bdeck_file_path, logger)
                        else:
                            logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Using existing modified csv file: "  + bdeck_file_path + ", because TRACK_DATA_MOD_FORCE_OVERWRITE is set to False")
                    else:
                        logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Writing modified csv file: " + bdeck_file_path)
                        read_modify_write_file(bdeck_in_file_path, MM, p, bdeck_file_path, logger)

                else:

                    # Set up the adeck and bdeck file paths
                    adeck_file_path = os.path.join(mydir, myfile)
                    bdeck_file_path = re.sub(p.opt["ADECK_FILE_PREFIX"],p.opt["BDECK_FILE_PREFIX"], adeck_file_path)
    
                # Run tc_pairs
                pairs_out_file = os.path.join(pairs_out_dir, myfile)
                pairs_out_file_with_suffix = pairs_out_file + ".tcst"
                if os.path.exists(pairs_out_file_with_suffix):
                    if (p.opt["TC_PAIRS_FORCE_OVERWRITE"]):
                        logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Writing tc_pairs output file: "  + pairs_out_file + ", replacing existing data because TC_PAIRS_FORCE_OVERWRITE is set to True")
                        cmd = p.opt["TC_PAIRS"] + " -adeck " + adeck_file_path + " -bdeck " + bdeck_file_path + " -config " + p.opt["TC_PAIRS_CONFIG_PATH"] + " -out " + pairs_out_file
                        logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Running tc_pairs with command: " + cmd)
                        ret = subprocess_check_output(cmd, stderr=subprocess.STDOUT, shell=True)
                        if ret != 0:
                            logger.error("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "Problem executing: " + cmd)
                            exit(0)
                    else:
                        logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Existing tc_pairs output file: "  + pairs_out_file + ", is available for use. To overwrite set TC_PAIRS_FORCE_OVERWRITE to True")
                else:
                    cmd = p.opt["TC_PAIRS"] + " -adeck " + adeck_file_path + " -bdeck " + bdeck_file_path + " -config " + p.opt["TC_PAIRS_CONFIG_PATH"] + " -out " + pairs_out_file
                    logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Running tc_pairs with command: " + cmd)
                    ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
                    if ret != 0:
                        logger.error("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "Problem executing: " + cmd)
                        exit(0)
               
    
if __name__ == "__main__":
    main()


