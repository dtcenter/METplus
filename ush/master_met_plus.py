#!/usr/bin/env python
from __future__ import print_function

'''!@namespace master_met_plus
Main script the processes all the tasks in the PROCESS_LIST
'''

import os
import sys
import logging
import getopt
import config_launcher
import time
import datetime
import calendar
import produtil.setup
from produtil.run import batchexe, run  # , checkrun
import met_util as util
import config_metplus

from pcp_combine_wrapper import PcpCombineWrapper
from grid_stat_wrapper import GridStatWrapper
from regrid_data_plane_wrapper import RegridDataPlaneWrapper
from tc_pairs_wrapper import TcPairsWrapper
from extract_tiles_wrapper import ExtractTilesWrapper
from series_by_lead_wrapper import SeriesByLeadWrapper
from series_by_init_wrapper import SeriesByInitWrapper
#from mode_wrapper import ModeWrapper
from usage_wrapper import UsageWrapper
from command_builder import CommandBuilder
from tcmpr_plotter_wrapper import TCMPRPlotterWrapper

'''!@var logger
The logging.Logger for log messages
'''
logger = None


def usage():
    print("Usage statement")
    print ('''
Usage: master_met_plus.py [ -c /path/to/additional/conf_file] [options]
    -c|--config <arg0>      Specify custom configuration file to use
    -r|--runtime <arg0>     Specify initialization time to process
    -h|--help               Display this usage statement
''')


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

    short_opts = "c:r:h"
    long_opts = ["config=",
                 "help",
                 "runtime="]
    # All command line input, get options and arguments
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError as err:
        print(str(err))
        usage('SCRIPT IS EXITING DUE TO UNRECOGNIZED COMMAND LINE OPTION')
    for k, v in opts:
        if k in ('-c', '--config'):
            # adds the conf file to the list of arguments.
            print("ADDED CONF FILE: "+v)
            args.append(config_launcher.set_conf_file_path(v))
        elif k in ('-h', '--help'):
            usage()
            exit()
        elif k in ('-r', '--runtime'):
            start_time = v
            end_time = v
        else:
            assert False, "UNHANDLED OPTION"
    if not args:
        args = None
    (parm, infiles, moreopt) = config_launcher.parse_launch_args(args,
                                                                 usage,
                                                                 None,
                                                                 logger)
    p = config_launcher.launch(infiles, moreopt)

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
    processes = []
    for item in process_list:
      try:
        command_builder = getattr(sys.modules[__name__], item+"Wrapper")(p, logger)
      except AttributeError:
        raise NameError("Process %s doesn't exist" % item)
        exit()

      processes.append(command_builder)

    if p.getstr('config', 'LOOP_METHOD') == "processes":
        for process in processes:
            process.run_all_times()

    elif p.getstr('config', 'LOOP_METHOD') == "times":
        time_format = p.getstr('config', 'INIT_TIME_FMT')
        start_t = p.getstr('config', 'INIT_BEG')
        end_t = p.getstr('config', 'INIT_END')
        time_interval = p.getint('config', 'INIT_INC')
        if time_interval < 60:
            print("ERROR: time_interval parameter must be greater than 60 seconds")
            exit(1)
        
        init_time = calendar.timegm(time.strptime(start_t, time_format))
        end_time = calendar.timegm(time.strptime(end_t, time_format))
        while init_time <= end_time:
            run_time = time.strftime("%Y%m%d%H%M", time.gmtime(init_time))            
            print("")
            print("****************************************")
            print("* RUNNING MET+")
            print("* at init time: " + run_time)
            print("****************************************")
            logger.info("****************************************")
            logger.info("* RUNNING MET+")
            logger.info("*  at init time: " + run_time)
            logger.info("****************************************")            
            for process in processes:
                process.run_at_time(run_time)
                process.clear()

            init_time += time_interval

    else:
        print("ERROR: Invalid LOOP_METHOD defined. " + \
              "Options are processes, times")
        exit()
    exit()
    for item in process_list:

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
