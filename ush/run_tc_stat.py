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


def tc_stat(p, logger, tc_cmd, filtered_output_dir):
    ''' Create the call to MET tool TC-STAT to subset tc-pairs output
        based on the criteria specified in the parameter/config file.
         Args:
           p     : reference to ConfigMaster parm/config object constants_pdef
           logger: the logger to which all log messages are directed

           tc_cmd(string) : tc_stat cmd 
                            The optional arguments read from the 
                            config/parm file should have already been
                            appended to these args.

           filtered_output_dir:  The directory where the filtered files 
                                 will be saved.
         Returns:
            None: if no error, then invoke MET tool TC-STAT and 
                  subsets tc-pairs data, creating a filter.tcst file.

            Raises CalledProcessError

    '''

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    
    # get the process id to be used to identify the output
    # amongst different users and runs.
    cur_pid = str(os.getpid())

    # Logging output: TIME UTC |TYPE (DEBUG, INFO, WARNING, etc.) |
    # [File : function]| Message
    msg = ("INFO |  [" + cur_filename +  ":" + "cur_function] |" +
           "BEGIN run_tc_stat")
    logger.info(msg)
    
    # Create the arguments to pass to the MET Tool TC-STAT
    util.mkdir_p(filtered_output_dir)

    # Make call to tc_stat, capturing any stderr and stdout to the MET Plus log.
    try:
        tc_stat_out = subprocess.check_output(tc_cmd, stderr=subprocess.STDOUT, shell=True )
        msg = ("INFO|" + cur_filename + ':' + cur_function + 
               '|tc command:' + tc_cmd)
        logger.info(msg)
    except subprocess.CalledProcessError, e:
        msg = ("ERROR| " + cur_filename + ":" + cur_function + 
               " from calling MET TC-STAT with command:" + tc_cmd)
        logger.error(msg)
        pass


if __name__ == "__main__":

    p = P.Params()
    p.init(__doc__)
    logger = util.get_logger(p)

    init_list = util.gen_init_list(p.opt["INIT_DATE_BEG"], p.opt["INIT_DATE_END"], p.opt["INIT_HOUR_INC"], p.opt["INIT_HOUR_END"])

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
   
    # Does nothing right now, meant to be imported by another script.

    
    

