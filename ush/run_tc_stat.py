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


def tc_stat(p, logger, req_action, cur_init, input_args):
    ''' Create the call to MET tool TC-STAT to subset tc-pairs output
        based on the criteria specified in the parameter/config file.
         Args:
           p : referenct to ConfigMaster parm/config object constants_pdef
           logger: the logger to which all log messages are directed
           req_action (string): "extract_tiles" or "series_analysis"
           input_args(string) : arguments already created from elsewhere. The optional
                       arguments read from the config/parm file will be appended to these args.
           cur_init:  The current init time, used only if the input_args list is empty or None
         Returns:
            None: if no error, then invoke MET tool TC-STAT and subsets tc-pairs data, creating a filter.tcst file.
            1:  if an error has been encountered

    '''

    # Retrieve parameters from corresponding param file

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    
    output_dir = p.opt["OUT_DIR"]
    filtered_output_dir = p.opt["FILTER_OUT_DIR"]
    project_dir = p.opt["PROJ_DIR"]
    tc_stat_exe = p.opt["TC_STAT"]

    # Read in the filter options from the param/config file.
    action = req_action.upper()
    if action == 'EXTRACT_TILES':
        filter_opts = p.opt["EXTRACT_TILES_FILTER_OPTS"]
    elif action == 'SERIES_ANALYSIS':
        filter_opts = p.opt["SERIES_ANALYSIS_FILTER_OPTS"]
    else:
        logger.error('ERROR|' + cur_filename+':'+cur_function+'|' + action_type + ' is unsupported, only EXTRACT_TILES or SERIES_ANALYSIS is currently supported')
        sys.exit(1)

    # get the process id to be used to identify the output
    # amongst different users and runs.
    cur_pid = str(os.getpid())

    # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) | [File : function]| Message
    logger.info("INFO |  [" + cur_filename +  ":" + "cur_function] |" + "BEGIN run_tc_stat")
    
    # Create the arguments to pass to the MET Tool TC-STAT
    filter_path = os.path.join(filtered_output_dir, cur_init)
    util.mkdir_p(filter_path)

    if len(input_args) > 0:
        # Called from within extract_tiles.py, where an argument list has already
        # been created. Append the optional args from the config/param file to the input_args
        args_seq = [input_args, ' ', filter_opts]
        logger.info("Input args found, appending optional args") 
    else:
        # For running stand-alone, a cur_init needs to be provided.
        # The optional args are the only arguments, create a well-formed argument list for running 
        # MET Tool TC-STAT. 
        logger.info("No input args found, create full args list with optional args")
        year_month =  util.extract_year_month(cur_init, logger)
        filter_filename = "filter_" + cur_init + ".tcst"
        filter_name = os.path.join(filtered_output_dir, cur_init, filter_filename)
        args_seq = [tc_stat_exe, " -job filter -lookin ", project_dir,"/tc_pairs/", year_month, " -init_inc ", cur_init, " -match_points true -dump_row ", filter_name, ' ', filter_opts]
 
    tc_cmd = ''.join(args_seq)
    logger.info("INFO|" + cur_filename + ':' + cur_function + '|' + tc_cmd)
   
    # Make call to tc_stat, capturing any stderr and stdout to the MET Plus log.
    try:
        tc_pairs_out = subprocess.check_output(tc_cmd, stderr=subprocess.STDOUT, shell=True )
        logger.info("INFO| [tc_pairs ]|" + tc_pairs_out)
    
    except subprocess.CalledProcessError, e:
        print("inside tc_stat, error e: ", e)
        pass


if __name__ == "__main__":
    # Running from extract_tiles, input init time
    p = P.Params()
    p.init(__doc__)
    logger = util.get_logger(p)

    init_list = p.opt["INIT_LIST"]

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    type = 'EXTRACT_TILES' 
    for cur_init in init_list:
        tc_stat(p,logger,type,cur_init, '' )

    

