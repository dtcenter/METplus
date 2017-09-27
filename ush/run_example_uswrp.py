#! /usr/bin/env python

# from produtil.run import batchexe, run, checkrun
import config_launcher
import logging
import met_util as util
import getopt
import sys

from CG_pcp_combine import CG_pcp_combine
from CG_grid_stat import CG_grid_stat
from CG_regrid_data_plane import CG_regrid_data_plane


def usage():
    print("Usage statement")
    print ('''
Usage: run_example_uswrp.py [ -c /path/to/additional/conf_file] [options]

    -c|--config <arg0>      Specify custom configuration file to use
    -r|--runtime <arg0>     Specify initialization time to process
    -h|--help               Display this usage statement
''')


def main():
    logger = logging.getLogger('run_example')
    init_time = 0
    start_time = 0
    end_time = 0
    time_interval = 1
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
    logger = util.get_logger(p)
    logger.setLevel(logging.DEBUG)

    if start_time == 0:
        start_time = p.getstr('config', 'START_TIME')
        end_time = p.getstr('config', 'END_TIME')
        time_interval = p.getstr('config', 'TIME_INTERVAL')

    # Get the list of processes to call
    process_list = util.getlist(p.getstr('config', 'PROCESS_LIST'))

    model_type = p.getstr('config', 'MODEL_TYPE')
    fcst_vars = util.getlist(p.getstr('config', 'FCST_VARS'))
    lead_seq = util.getlistint(p.getstr('config', 'LEAD_SEQ'))

    init_time = start_time
    while init_time <= end_time:
        print("")
        print("****************************************")
        print("* RUNNING MET+")
        print("* EVALUATING " + model_type + " at init time: " + init_time)
        print("****************************************")
        logger.info("****************************************")
        logger.info("* RUNNING MET+")
        logger.info("* EVALUATING " + model_type +
                    " at init time: " + init_time)
        logger.info("****************************************")

        for lead in lead_seq:
            for fcst_var in fcst_vars:
                # loop over models to compare
                accums = util.getlist(p.getstr('config', fcst_var+"_ACCUM"))
                ob_types = util.getlist(p.getstr('config', fcst_var+"_OBTYPE"))
                for accum in accums:
                    for ob_type in ob_types:
                        if lead < int(accum):
                            continue

                        obs_var = p.getstr('config', ob_type+"_VAR")
                        logger.info("")
                        logger.info("")
                        logger.info("For " + init_time + " F" + str(lead) +
                                    ", processing " + model_type + "_" +
                                    fcst_var + "_"+accum + " vs " + ob_type +
                                    " " + obs_var + "_" + accum)

                        valid_time = util.shift_time(init_time, lead)
                        data_interval = p.getint('config',
                                                 ob_type+'_DATA_INTERVAL')
                        if int(valid_time[8:10]) % data_interval != 0:

                            logger.warning("No observation for valid time: " +
                                           valid_time+". Skipping...")
                            continue

                        for process in process_list:
                            if process == "pcp_combine":
                                run_pcp = CG_pcp_combine(p, logger)
                                run_pcp.run_at_time(valid_time, accum,
                                                    ob_type, fcst_var)
                            elif process == "regrid_data_plane":
                                run_regrid = CG_regrid_data_plane(p, logger)
                                run_regrid.run_at_time(valid_time, accum,
                                                       ob_type)
                            elif process == "grid_stat":
                                run_grid_stat = CG_grid_stat(p, logger)
                                run_grid_stat.run_at_time(init_time, lead,
                                                          accum, ob_type,
                                                          fcst_var)
                            else:
                                print("ERROR: Invalid process in process list")
                                exit(1)

        init_time = util.shift_time(init_time, int(time_interval))

    (logger).info("END OF EXECUTION")


if __name__ == "__main__":
    main()
