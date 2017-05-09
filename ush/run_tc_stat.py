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

import produtil.setup
from produtil.run import batchexe, run, checkrun
import logging
import os
import sys
import met_util as util
import time
import re
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

    # Create the arguments to pass to the MET Tool TC-STAT
    util.mkdir_p(filtered_output_dir)

    # Make call to tc_stat, capturing any stderr and stdout to the MET Plus log.
    try:
        tc_cmd = batchexe('sh')['-c',tc_cmd].err2out()
        #tc_cmd = batchexe(tc_cmd.split()[0])[tc_cmd.split()[1:]].err2out() 
        checkrun(tc_cmd)
    except produtil.run.ExitStatusException as ese:
        msg = ("ERROR| " + cur_filename + ":" + cur_function + 
               " from calling MET TC-STAT with command:" + tc_cmd.to_shell())
        logger.error(msg)
        logger.error({}.format(ese))
        pass


if __name__ == "__main__":

    # sleep is for debugging in pycharm so I can attach to this process
    # from the os.system call in master_met_plus.py
    #import time
    #time.sleep(60)

    # Testing constants_pdef until produtil is fully integrated.
    #import constants_pdef as P
    #test = P.Params()
    #test.init(__doc__) ## Put description of the code here

    # Does nothing right now, meant to be imported by another script.


    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_stat',jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run_tc_stat')
        produtil.log.postmsg('run_tc_stat is starting')

        # Read in the configuration object p
        import config_launcher
        if len(sys.argv) == 3:
            p = config_launcher.load_baseconfs(sys.argv[2])
        else:
            p = config_launcher.load_baseconfs()
        logger = util.get_logger(p)
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = p.getdir('MET_BASE')


        init_list = util.gen_init_list(p.getstr('config', 'INIT_DATE_BEG'),
                                       p.getstr('config', 'INIT_DATE_END'),
                                       p.getint('config', 'INIT_HOUR_INC'),
                                       p.getstr('config', 'INIT_HOUR_END'))


        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        produtil.log.postmsg('run_tc_stat completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'run_tc_stat failed: %s'%(str(e),),exc_info=True)
        sys.exit(2)

    
    

