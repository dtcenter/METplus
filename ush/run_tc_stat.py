#!/usr/bin/env python

'''
Program Name: run_tc_stat.py
Contact(s): Julie Prestopnik, Minna Win
Abstract: Subset tc_pairs data using MET tool TC-STAT for use in
          extract_tiles.py or series analysis
          (via series_by_lead.py or series_by_init.py)
History log: Initial version
Usage: run_tc_stat.py
Parameters: None
Input Files: tc_pairs data
Output Files: subset of tc_pairs data
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


def tc_stat(p, logger, filter_opt, cur_time, tc_cmd, filtered_output_dir):
    ''' Create the call to MET tool TC-STAT to subset tc-pairs output
        based on the criteria specified in the parameter/config file.
         Args:
           p : reference to ConfigMaster parm/config object constants_pdef
           logger: the logger to which all log messages are directed
           filter_opt :  the filter option defined in the constants_pdef file
           tc_cmd(string) : tc_stat cmd already created from elsewhere. The optional
                       arguments read from the config/parm file will be appended to these args.
           cur_time:  The current time, used only if the tc_cmd list is empty or None
           filtered_output_dir:  The directory where the filtered files will be saved.
         Returns:
            None: if no error, then invoke MET tool TC-STAT and subsets tc-pairs data, creating a filter.tcst file.
            1:  if an error has been encountered

    '''

    # Retrieve parameters from corresponding param file

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    
    output_dir = p.opt["OUT_DIR"]
    project_dir = p.opt["PROJ_DIR"]
    tc_stat_exe = p.opt["TC_STAT"]


    # get the process id to be used to identify the output
    # amongst different users and runs.
    cur_pid = str(os.getpid())

    # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) | [File : function]| Message
    logger.info("INFO |  [" + cur_filename +  ":" + "cur_function] |" + "BEGIN run_tc_stat")
    
    # Create the arguments to pass to the MET Tool TC-STAT
    filter_path = os.path.join(filtered_output_dir, cur_time)
    util.mkdir_p(filter_path)

    if tc_cmd:
        # Called from within extract_tiles.py or series_by_[lead|init], where an argument list has already
        # been created. Append the filter_opt to the tc_cmd
        args_seq = [tc_cmd, ' ', filter_opt]
        logger.info("Input args found, appending optional args") 
    else:
        # For running stand-alone/testing, a cur_time needs to be provided.
        # The optional args are the only arguments, create a well-formed argument list for running 
        # MET Tool TC-STAT. 
        logger.info("No input args found, create full args list with optional args")
        year_month =  util.extract_year_month(cur_time, logger)
        filter_filename = "filter_" + cur_time + ".tcst"
        filter_name = os.path.join(filtered_output_dir, cur_time, filter_filename)
        args_seq = [tc_stat_exe, " -job filter -lookin ", project_dir,"/tc_pairs/", year_month, " -init_inc ", cur_time, " -match_points true -dump_row ", filter_name, ' ', ]
 
    tc_cmd = ''.join(args_seq)
    logger.info("INFO|" + cur_filename + ':' + cur_function + '|tc command:' + tc_cmd)
   
    # Make call to tc_stat, capturing any stderr and stdout to the MET Plus log.
    try:
        tc_stat_out = subprocess.check_output(tc_cmd, stderr=subprocess.STDOUT, shell=True )
    except subprocess.CalledProcessError, e:
        logger.error("ERROR| " + cur_filename + ":" + cur_function + " from calling MET TC-STAT with command:" + tc_cmd)
        pass


if __name__ == "__main__":

    # USED FOR TESTING...
    # Running from extract_tiles, input init time
    p = P.Params()
    p.init(__doc__)
    logger = util.get_logger(p)

    init_list = p.opt["INIT_LIST"]

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    filter_opt = p.opt["EXTRACT_TILES_FILTER_OPTS"]
    filtered_out_dir = p.opt["EXTRACT_FILTERED_OUT_DIR"]
    #filter_opt = p.opt["SERIES_ANALYSIS_FILTER_OPTS"]
    #filtered_out_dir = p.opt["SERIES_INIT_FILTERED_OUT_DIR"]
    for cur_time in init_list:
        tc_stat(p,logger,filter_opt, cur_time, '', filtered_out_dir )

    

