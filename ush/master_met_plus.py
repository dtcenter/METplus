#!/usr/bin/env python
from __future__ import print_function

'''!@namespace master_met_plus
Main script the processes all the tasks in the PROCESS_LIST
'''

import os
import sys
import logging

import produtil.setup
from produtil.run import batchexe, run  # , checkrun
import met_util as util
import config_metplus

'''!@var logger
The logging.Logger for log messages
'''
logger = None

def main():
    """!Main program.

    Master MET+ script that invokes the necessary Python scripts
    to perform various activities, such as series analysis."""

    # Job Logger
    produtil.log.jlogger.info('Top of master_met_plus')

    # Setup Task logger, Until Conf object is created, Task logger is
    # only logging to tty, not a file.
    logger = logging.getLogger('master_met_plus')
    logger.info('logger Top of master_met_plus.')

    # Used for logging and usage statment
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Creates a configuration object.
    #p = config_metplus.setup(sys.argv, usage, logger)
    p = config_metplus.setup(filename=cur_filename,logger=logger)

    # NOW I have a conf object p, I can now setup the handler
    # to write to the LOG_FILENAME.
    logger = util.get_logger(p)

    # This is available in each subprocess from os.system BUT
    # we also set it in each process since they may be called stand alone.
    os.environ['MET_BASE'] = p.getdir('MET_BASE')

    # Use config object to get the list of processes to call
    process_list = util.getlist(p.getstr('config', 'PROCESS_LIST'))

    # Keep this comment.
    # When running commands in the process_list, reprocess the
    # original command line using (item))[sys.argv[1:]].
    #
    # You could call each task (ie. run_tc_pairs.py) without any args since
    # the final METPLUS_CONF file was just created from config_metplus.setup,
    # and each task, also calls setup, which use an existing final conf
    # file over command line args.
    #
    # both work ...
    # Note: Using (item))sys.argv[1:], is preferable since
    # it doesn't depend on the conf file existing.
    for item in process_list:
        #cmd = batchexe("%s" % (item))
        cmd = batchexe("%s" % (item))[sys.argv[1:]]
        cmd_shell = cmd.to_shell()
        logger.info("INFO | [" + cur_filename + ":" +
                    cur_function + "] | " + "Running: " + cmd_shell)
        ret = run(cmd)
        if ret != 0:
            logger.error("ERROR | [" + cur_filename + ":" +
                        cur_function + "] | " + "Problem executing: " +
                        cmd_shell)
            exit(0)


if __name__ == "__main__":
    try:
        # If jobname is not defined, in log it is 'NO-NAME'
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus')
        produtil.log.postmsg('master_met_plus is starting')

        main()
        produtil.log.postmsg('master_met_plus completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'master_metplus  failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
