#!/usr/bin/env python

import os
import glob
import subprocess
import filecmp
#import sys
import logging
#import getopt
import config_launcher
import time
#import datetime
import calendar
#import produtil.setup
#from produtil.run import batchexe, run  # , checkrun
import met_util as util
#import config_metplus

# TODO: move test results to separate file for readability

def run_test_use_case(param_a, param_b, run_a, run_b):
    metplus_home = "/d1/mccabe/METplus"
    a_conf = metplus_home+"/internal_tests/use_cases/system.a.conf"
    b_conf = metplus_home+"/internal_tests/use_cases/system.b.conf"
    params_a = param_a.split(",")
    params_b = param_b.split(",")
#    params_a = [ params, a_conf ]
#    params_b = [ params, b_conf ]
    params_a = params_a + [a_conf]
    params_b = params_b + [b_conf]
    print(params_a)
    all_good = True
#    params_a = [ param_file, a_conf ]
#    params_b = [ param_file, b_conf ]
    logger = logging.getLogger('master_metplus')    

    # read A confs
    (parm, infiles, moreopt) = config_launcher.parse_launch_args(params_a,
                                                                 None, None,
                                                                 logger)
    p = config_launcher.launch(infiles, moreopt)

    # read B confs     
    (parm, infiles, moreopt) = config_launcher.parse_launch_args(params_b,
                                                                 None, None,
                                                                 logger)
    p_b = config_launcher.launch(infiles, moreopt)    
    
    # run A
    if run_a:
        cmd = os.path.join(p.getstr('config', "METPLUS_BASE"),"ush","master_metplus.py")
        for parm in params_a:
            cmd += " -c "+parm
        print("CMD A:"+cmd)
        process = subprocess.Popen(cmd, shell=True)
        process.wait()

    # run B
    if run_b:
        cmd = os.path.join(p_b.getstr('config', "METPLUS_BASE"),"ush","master_metplus.py")
        for parm in params_b:
            cmd += " -c "+parm
        print("CMD B:"+cmd)
        process = subprocess.Popen(cmd, shell=True)
        process.wait()

    if not compare_results(p, p_b):
        all_good = False

    return all_good

def compare_results(p, p_b):
    a_dir = p.getstr('config', 'OUTPUT_BASE')
    b_dir = p_b.getstr('config', 'OUTPUT_BASE')

    print("****************************")
    print("* TEST RESULTS             *")
    print("****************************")
    good = True

    processes = util.getlist(p.getstr('config', 'PROCESS_LIST'))
    
    use_init = p.getbool('config', 'LOOP_BY_INIT')
    if use_init:
        time_format = p.getstr('config', 'INIT_TIME_FMT')
        start_t = p.getstr('config', 'INIT_BEG')
        end_t = p.getstr('config', 'INIT_END')
        time_interval = p.getint('config', 'INIT_INC')
    else:
        time_format = p.getstr('config', 'VALID_TIME_FMT')
        start_t = p.getstr('config', 'VALID_BEG')
        end_t = p.getstr('config', 'VALID_END')
        time_interval = p.getint('config', 'VALID_INC')
        
    loop_time = calendar.timegm(time.strptime(start_t, time_format))
    end_time = calendar.timegm(time.strptime(end_t, time_format))
    while loop_time <= end_time:
        run_time = time.strftime("%Y%m%d%H%M", time.gmtime(loop_time))
        print("Checking "+run_time)
        # TODO: Handle PcpCombine for each type of run (OBS vs FCST)
        for process in processes:
            print("Checking output from "+process)
            if process == "GridStat":
                # out_subdir = "uswrp/met_out/QPF/200508070000/grid_stat"
                out_a = p.getstr('config', "GRID_STAT_OUT_DIR")
                out_b = p_b.getstr('config', "GRID_STAT_OUT_DIR")
                glob_string = "{:s}/{:s}/grid_stat/*"
                files_a = glob.glob(glob_string.format(out_a, run_time))
                files_b = glob.glob(glob_string.format(out_b, run_time))
            elif process == "PcpCombineObs":
                out_a = p.getstr('config', "OBS_PCP_COMBINE_OUTPUT_DIR")
                out_b = p_b.getstr('config', "OBS_PCP_COMBINE_OUTPUT_DIR")
                glob_string = "{:s}/{:s}/*"
                files_a = glob.glob(glob_string.format(out_a, run_time[0:8]))
                files_b = glob.glob(glob_string.format(out_b, run_time[0:8]))
            elif process == "PcpCombineModel":
                out_a = p.getstr('config', "FCST_PCP_COMBINE_OUTPUT_DIR")
                out_b = p_b.getstr('config', "FCST_PCP_COMBINE_OUTPUT_DIR")
                glob_string = "{:s}/{:s}/*"
                files_a = glob.glob(glob_string.format(out_a, run_time[0:8]))
                files_b = glob.glob(glob_string.format(out_b, run_time[0:8]))
            elif process == "RegridDataPlane":
                out_a = p.getstr('config', "OBS_REGRID_DATA_PLANE_OUTPUT_DIR")
                out_b = p_b.getstr('config', "OBS_REGRID_DATA_PLANE_OUTPUT_DIR")
                glob_string = "{:s}/{:s}/*"
                files_a = glob.glob(glob_string.format(out_a, run_time[0:8]))
                files_b = glob.glob(glob_string.format(out_b, run_time[0:8]))
            elif process == "TcPairs":
                out_a = p.getstr('config', "TC_PAIRS_DIR")
                out_b = p_b.getstr('config', "TC_PAIRS_DIR")
                glob_string = "{:s}/{:s}/*"
                files_a = glob.glob(glob_string.format(out_a, run_time[0:8]))
                files_b = glob.glob(glob_string.format(out_b, run_time[0:8]))
            elif process == "ExtractTiles":
                # TODO FIX DIR
                out_a = p.getstr('config', "EXTRACT_OUT_DIR")
                out_b = p_b.getstr('config', "EXTRACT_OUT_DIR")
                glob_string = "{:s}/{:s}/*/*"
                date_dir = run_time[0:8]+"_"+run_time[8:10]
                files_a = glob.glob(glob_string.format(out_a, date_dir))
                files_b = glob.glob(glob_string.format(out_b, date_dir))
            elif process == "SeriesByInit": # TODO FIX DIR
                out_a = p.getstr('config', "SERIES_INIT_FILTERED_OUT_DIR")
                out_b = p_b.getstr('config', "SERIES_INIT_FILTERED_OUT_DIR")
                glob_string = "{:s}/{:s}/*/*"
                date_dir = run_time[0:8]+"_"+run_time[8:10]
                files_a = glob.glob(glob_string.format(out_a, date_dir))
                files_b = glob.glob(glob_string.format(out_b, date_dir))
            elif process == "SeriesByLead": # TODO FIX DIR
                out_a = p.getstr('config', "SERIES_LEAD_FILTERED_OUT_DIR")
                out_b = p_b.getstr('config', "SERIES_LEAD_FILTERED_OUT_DIR")
                glob_string = "{:s}/{:s}/*/*"
                date_dir = run_time[0:8]+"_"+run_time[8:10]
                files_a = glob.glob(glob_string.format(out_a, date_dir))
                files_b = glob.glob(glob_string.format(out_b, date_dir))
            else:
                print("PROCESS:"+process+" is not valid")
                continue

            if not compare_output_files(files_a, files_b, a_dir, b_dir):
                good = False

        loop_time += time_interval

    if good:
        print("Success")
    else:
        print("ERROR: Some differences")
    return good

def compare_output_files(files_a, files_b, a_dir, b_dir):
    good = True
    if len(files_a) == 0 and len(files_b) == 0:
        print("WARNING: No files in either directory")
        return True
    if len(files_a) == len(files_b):
        print("Equal number of output files: "+str(len(files_a)))
    else:
        print("ERROR: A output "+str(len(files_a))+" files, B output "+str(len(files_b))+" files")
        good = False

    for afile in files_a:
        bfile = afile.replace(a_dir, b_dir)
        # check if file exists in A and B
        if not os.path.exists(bfile):
            print("ERROR: "+os.path.basename(afile)+" missing in B")
            print(bfile)
            good = False
            continue

        # check if files are equivalent
        # TODO: Improve this, a file path difference in the file could
        #  report a difference when the data is the same
        # for netCDF:
        # ncdump infile1 infile2 outfile can be used then check how many outfile points are non-zero
#        if not filecmp.cmp(afile, bfile):
#            print("ERROR: Differences between "+afile+" and "+bfile)
#            good = False
    return good

def main():
    run_a = True
    run_b = True

    metplus_home = "/d1/mccabe/METplus"
    use_case_dir = os.path.join(metplus_home,"parm/use_cases")
    param_files = [
                    use_case_dir+"/qpf/examples/ruc-vs-s2grib.conf",
                    use_case_dir+"/qpf/examples/phpt-vs-s4grib.conf",
                    use_case_dir+"/qpf/examples/hrefmean-vs-qpe.conf",
                    use_case_dir+"/qpf/examples/hrefmean-vs-mrms-qpe.conf",
                    use_case_dir+"/qpf/examples/nationalblend-vs-mrms-qpe.conf" ,
#                    use_case_dir+"/feature_relative/feature_relative.conf,"+use_case_dir+"/feature_relative/examples/series_by_init_12-14_to_12-16.conf" #,
#                    use_case_dir+"/feature_relative/feature_relative.conf,"+use_case_dir+"/feature_relative/examples/series_by_lead_all_fhrs.conf" #,
#                    use_case_dir+"/feature_relative/feature_relative.conf,"+use_case_dir+"/feature_relative/examples/series_by_lead_by_fhr_grouping.conf" #,    
                    use_case_dir+"/grid_to_grid/grid2grid_anom.conf" ,
                    use_case_dir+"/grid_to_grid/grid2grid_anom_height.conf",
                    use_case_dir+"/grid_to_grid/grid2grid_sfc.conf" ,
                    use_case_dir+"/grid_to_grid/grid2grid_precip.conf"
                  ]

    all_good = True
    for param_file in param_files:
        param_a = param_file.replace(metplus_home,"/d1/mccabe/METplus.a")
        param_b = param_file.replace(metplus_home,"/d1/mccabe/METplus.b")
        if not run_test_use_case(param_a, param_b, run_a, run_b):
            all_good = False

    if all_good:
        print("ALL TESTS PASSED")
    else:
        print("ERROR: Some tests failed")

    

    
if __name__ == "__main__":
    main()
