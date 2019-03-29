#!/usr/bin/env python
from __future__ import print_function

'''!@namespace master_metplus
Main script the processes all the tasks in the PROCESS_LIST
'''

import os
import sys
import logging
import getopt
import config_launcher
import time
from datetime import datetime, timedelta
import calendar
import shutil
import produtil.setup
# from produtil.run import run
import met_util as util
import config_metplus

from ensemble_stat_wrapper import EnsembleStatWrapper
from pcp_combine_wrapper import PcpCombineWrapper
from grid_stat_wrapper import GridStatWrapper
from regrid_data_plane_wrapper import RegridDataPlaneWrapper
from tc_pairs_wrapper import TcPairsWrapper
from extract_tiles_wrapper import ExtractTilesWrapper
from series_by_lead_wrapper import SeriesByLeadWrapper
from series_by_init_wrapper import SeriesByInitWrapper
from stat_analysis_wrapper import StatAnalysisWrapper
from make_plots_wrapper import MakePlotsWrapper
from mode_wrapper import ModeWrapper
from mtd_wrapper import MTDWrapper
from usage_wrapper import UsageWrapper
from command_builder import CommandBuilder
from tcmpr_plotter_wrapper import TCMPRPlotterWrapper
# Keep cyclone_plotter commented out in repository. It requires cartopy
# If cartopy is not present then master_metplus will error and exit.
#from cyclone_plotter_wrapper import CyclonePlotterWrapper
from pb2nc_wrapper import PB2NCWrapper
from point_stat_wrapper import PointStatWrapper
from tc_stat_wrapper import TcStatWrapper
from gempak_to_cf_wrapper import GempakToCFWrapper

'''!@var logger
The logging.Logger for log messages
'''
logger = None


def main():
    """!Main program.

    Master METplus script that invokes the necessary Python scripts
    to perform various activities, such as series analysis."""

    # Used for logging and usage statment
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Setup Task logger, Until Conf object is created, Task logger is
    # only logging to tty, not a file.
    logger = logging.getLogger('master_metplus')
    logger.info('Starting METplus v{}'
                .format(util.get_version_number()))

    # Parse arguments, options and return a config instance.
    p = config_metplus.setup(filename=cur_filename)

    # check for deprecated config items and warn user to remove/replace them
    util.check_for_deprecated_config(p, logger)

    # set staging dir to OUTPUT_BASE/stage if not set
    if not p.has_option('dir', 'STAGING_DIR'):
        p.set('dir', 'STAGING_DIR', os.path.join(p.getdir('OUTPUT_BASE'),"stage"))

    # create temp dir if it doesn't exist already
    tmp_dir = util.getdir(p, 'TMP_DIR', logger)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)


    # NOW we have a conf object p, we can now get the logger
    # and set the handler to write to the LOG_METPLUS
    # TODO: Frimel setting up logger file handler.
    # Setting up handler i.e util.get_logger should be moved to
    # the setup wrapper and encapsulated in the config object.
    # than you would get it this way logger=p.log(). The config
    # object has-a logger we want.
    logger = util.get_logger(p)

    logger.info('Running METplus v{} called with command: {}'
                .format(util.get_version_number(), ' '.join(sys.argv)))

    # This is available in each subprocess from os.system BUT
    # we also set it in each process since they may be called stand alone.
    os.environ['MET_BASE'] = p.getdir('MET_BASE')

    # Use config object to get the list of processes to call
    process_list = util.getlist(p.getstr('config', 'PROCESS_LIST'))

    clock_time_obj = datetime.strptime(p.getstr('config', 'CLOCK_TIME'), '%Y%m%d%H%M%S')

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
            logger = p.log(item)
            command_builder = getattr(sys.modules[__name__], item + "Wrapper")(
                p, logger)
        except AttributeError:
            raise NameError("Process %s doesn't exist" % item)
            exit()

        processes.append(command_builder)

    loop_order = p.getstr('config', 'LOOP_ORDER', '')
    if loop_order == '':
        loop_order = p.getstr('config', 'LOOP_METHOD')

    if loop_order == "processes":
        for process in processes:
            # referencing using repr(process.app_name) in
            # log since it may be None,
            # if not set in the command builder subclass' contsructor,
            # and no need to generate an exception because of that.
            produtil.log.postmsg('master_metplus Calling run_all_times '
                                 'in: %s wrapper.' % repr(process.app_name))
            process.run_all_times()

    elif loop_order == "times":
        use_init = util.is_loop_by_init(p)
        if use_init:
            time_format = p.getstr('config', 'INIT_TIME_FMT')
            start_t = util.getraw_interp(p, 'config', 'INIT_BEG')
            end_t = util.getraw_interp(p, 'config', 'INIT_END')
            time_interval = p.getint('config', 'INIT_INCREMENT')
        else:
            time_format = p.getstr('config', 'VALID_TIME_FMT')
            start_t = util.getraw_interp(p, 'config', 'VALID_BEG')
            end_t = util.getraw_interp(p, 'config', 'VALID_END')
            time_interval = p.getint('config', 'VALID_INCREMENT')

        if time_interval < 60:
            logger.error("time_interval parameter must be "
                  "greater than 60 seconds")
            exit(1)

        loop_time = util.get_time_obj(start_t, time_format,
                                      clock_time_obj, logger)
        end_time = util.get_time_obj(end_t, time_format,
                                     clock_time_obj, logger)
        while loop_time <= end_time:
            run_time = loop_time.strftime("%Y%m%d%H%M")
            logger.info("****************************************")
            logger.info("* RUNNING METplus")
            if use_init:
                logger.info("*  at init time: " + run_time)
                p.set('config', 'CURRENT_INIT_TIME', run_time)
                os.environ['METPLUS_CURRENT_INIT_TIME'] = run_time
            else:
                logger.info("*  at valid time: " + run_time)
                p.set('config', 'CURRENT_VALID_TIME', run_time)
                os.environ['METPLUS_CURRENT_VALID_TIME'] = run_time
            logger.info("****************************************")
            for process in processes:
                input_dict = {}
                input_dict['now'] = clock_time_obj

                if use_init:
                    input_dict['init'] = loop_time
                else:
                    input_dict['valid'] = loop_time

                process.run_at_time(input_dict)
                process.clear()

            loop_time += timedelta(seconds=time_interval)

    else:
        logger.error("Invalid LOOP_METHOD defined. " + \
              "Options are processes, times")
        exit()

    # scrub staging directory if requested
    if p.getbool('config', 'SCRUB_STAGING_DIR', False) and os.path.exists(p.getdir('STAGING_DIR')):
        logger.info("Scrubbing staging dir: {}".format(p.getdir('STAGING_DIR')))
        shutil.rmtree(p.getdir('STAGING_DIR'))

    logger.info('METplus has successfully finished running.')

    exit()

    # TODO - remove this, I don't think this is being used.
    # If removing, also remove import produtil.run
    # If using ... than the run(cmd) will need to be correctly called.
    # for item in process_list:
    #
    #     cmd_shell = cmd.to_shell()
    #     logger.info("INFO | [" + cur_filename + ":" +
    #                 cur_function + "] | " + "Running: " + cmd_shell)
    #     ret = run(cmd)
    #     if ret != 0:
    #         logger.error("ERROR | [" + cur_filename + ":" +
    #                     cur_function + "] | " + "Problem executing: " +
    #                     cmd_shell)
    #         exit(0)


if __name__ == "__main__":
    try:
        # If jobname is not defined, in log it is 'NO-NAME'
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus')

        main()
    except Exception as e:
        produtil.log.jlogger.critical(
            'master_metplus  failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
