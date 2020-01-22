#!/usr/bin/env python

import os
from os.path import dirname, realpath
import glob
import shutil
import subprocess
import filecmp
import logging
import config_launcher
import time
import calendar
import met_util as util

metplus_home = dirname(dirname(dirname(realpath(__file__))))
use_case_dir = os.path.join(metplus_home,"parm/use_cases")

# all use cases that work with this script
all_use_cases = [
                use_case_dir + "/met_tool_wrapper/ASCII2NC/ASCII2NC.conf",
                use_case_dir + "/met_tool_wrapper/CustomIngest/CustomIngest.conf",
                use_case_dir + "/met_tool_wrapper/EnsembleStat/EnsembleStat.conf",
                use_case_dir + "/met_tool_wrapper/Example/Example.conf",
                use_case_dir + "/met_tool_wrapper/GridStat/GridStat.conf",
                use_case_dir + "/met_tool_wrapper/MODE/MODE.conf",
                use_case_dir + "/met_tool_wrapper/MTD/MTD.conf",
                use_case_dir + "/met_tool_wrapper/PB2NC/PB2NC.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_sum.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_add.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_bucket.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_custom.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_derive.conf",
#                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/pcp_subtract.conf",
                use_case_dir + "/met_tool_wrapper/PointStat/PointStat.conf",
                use_case_dir + "/met_tool_wrapper/RegridDataPlane/RegridDataPlane.conf",
                use_case_dir + "/met_tool_wrapper/SeriesByInit/SeriesByInit.conf",
                use_case_dir + "/met_tool_wrapper/SeriesByLead/SeriesByLead.conf",
#                use_case_dir + "/met_tool_wrapper/StatAnalysis/StatAnalysis.conf",
                use_case_dir + "/met_tool_wrapper/TCPairs/TCPairs_A.conf",
                use_case_dir + "/met_tool_wrapper/TCPairs/TCPairs_B.conf",
                use_case_dir + "/met_tool_wrapper/TCStat/TCStat.conf",
                use_case_dir + "/model_applications/convection_allowing_models/hrrr_ensemble_sfc.conf",
                use_case_dir + "/model_applications/convection_allowing_models/hrrr_ensemble_sfc_wildcard.conf",
                use_case_dir + "/model_applications/medium_range/anom.conf",
                use_case_dir + "/model_applications/medium_range/anom_height.conf",
                use_case_dir + "/model_applications/medium_range/conus_surface.conf",
                use_case_dir + "/model_applications/medium_range/feature_relative.conf",
                use_case_dir + "/model_applications/medium_range/feature_relative.conf," + use_case_dir + "/model_applications/medium_range/series_by_init_12-14_to_12-16.conf",
                use_case_dir + "/model_applications/medium_range/feature_relative.conf," + use_case_dir + "/model_applications/medium_range/series_by_lead_all_fhrs.conf",
                use_case_dir + "/model_applications/medium_range/feature_relative.conf," + use_case_dir + "/model_applications/medium_range/series_by_lead_by_fhr_grouping.conf",
                use_case_dir + "/model_applications/medium_range/sfc.conf",
                use_case_dir + "/model_applications/medium_range/upper_air.conf",
                use_case_dir + "/model_applications/precipitation/hrefmean-vs-s4.conf",
                use_case_dir + "/model_applications/precipitation/phpt-mtd.conf",
                use_case_dir + "/model_applications/precipitation/phpt-vs-s4grib.conf",
                use_case_dir + "/model_applications/precipitation/precip.conf",
                use_case_dir + "/model_applications/precipitation/precip_continuous.conf",
                use_case_dir + "/model_applications/precipitation/ruc-vs-s2grib.conf",
                use_case_dir + "/model_applications/tc_and_extra_tc/tc_stat_filter.conf",
              ]

plotting_use_cases = [
                use_case_dir + "/met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf",
                use_case_dir + "/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf",
                use_case_dir + "/model_applications/tc_and_extra_tc/cyclone_plotter.conf",
                use_case_dir + "/model_applications/tc_and_extra_tc/tcmpr_mean_median_box.conf",
              ]

# if METPLUS_DISABLE_PLOTTING is not set or set to empty string, add plotting use cases
if 'METPLUS_DISABLE_PLOTTING' not in os.environ or not os.environ['METPLUS_DISABLE_PLOTTING']:
    all_use_cases += plotting_use_cases

# list of use cases to run
# to run a subset of use cases, uncomment the 2nd variable and copy
# use cases from all_use_cases. this makes it easier to clean up after
# running so that git doesn't complain about differences
use_cases_to_run = all_use_cases
#use_cases_to_run = [
#                use_case_dir+"/met_tool_wrapper/ASCII2NC.conf",
#    ]

def get_param_list(param):
    conf = metplus_home+"/internal_tests/use_cases/system.conf"
    params = param.split(",")
    params = params + [conf]
    return params


def get_params(param):
    params = get_param_list(param)

    logger = logging.getLogger('master_metplus')    

    # read confs
    (parm, infiles, moreopt) = config_launcher.parse_launch_args(params,
                                                                 None, None,
                                                                 logger,
                                                                 util.baseinputconfs)
    p = config_launcher.launch(infiles, moreopt)

    return params, p

def run_test_use_case(param, test_metplus_base):

    params, p = get_params(param)
    out_dir = os.path.join(p.getdir('OUTPUT_BASE'), os.path.basename(params[-2]))

    cmd = os.path.join(test_metplus_base, "ush", "master_metplus.py")
    for parm in params:
        cmd += " -c "+parm
    cmd += ' -c dir.OUTPUT_BASE='+out_dir
    print("CMD:"+cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()

def main():

    if os.environ.get('METPLUS_TEST_METPLUS_BASE') is None:
        test_metplus_base = metplus_home
    else:
        test_metplus_base = os.environ['METPLUS_TEST_METPLUS_BASE']

    if not test_metplus_base:
        test_metplus_base = metplus_home

    print("Starting test script")
    print("Running " + test_metplus_base + " to test")

    output_base_prev = os.environ['METPLUS_TEST_PREV_OUTPUT_BASE']
    output_base = os.environ['METPLUS_TEST_OUTPUT_BASE']


    # if there are files in output base, prompt user to copy them to prev output base
    if os.path.exists(output_base) and os.listdir(output_base):

        # if prev exists, ask user to wipe it out
        if os.path.exists(output_base_prev):

            print("OUTPUT_BASE for previous run exists:" + output_base_prev)
            user_answer = input("Would you like to remove all files? (y/n)[n]")

            if user_answer and user_answer[0] == 'y':
                print("Removing " + output_base_prev + " and all files under")
                shutil.rmtree(output_base_prev)
            else:
                print("Directory must be empty to proceed with tests")
                exit(1)

        print("Moving " + output_base + " to " + output_base_prev)
        os.rename(output_base, output_base_prev)

    for param_file in use_cases_to_run:
        param = param_file.replace(metplus_home, test_metplus_base)
        run_test_use_case(param, test_metplus_base)

    # compare results with commands if prev output base has files
    if not os.path.exists(output_base_prev) or not os.listdir(output_base_prev):
        print("No files were found in previous OUTPUT_BASE: " + output_base_prev +\
              "\nRun this script again to compare results to previous run")
        exit(0)

    print("\nIf files or directories were only found in one run, they will appear when you run the following:\n")
    diff_cmd = f"diff -r {output_base_prev} {output_base} | grep Only"
    print(diff_cmd)

    print("\nCompare the output from previous run (" + output_base_prev + ") to this run"+\
          " (" + output_base + ").\nRun the following to compare results:")
    print(f"diff -r {output_base_prev} {output_base} | grep -v Binary | grep -v SSH | grep -v CONDA | grep -v OLDPWD | grep -v tmp | grep -v CLOCK_TIME | grep -v XDG | grep -v GSL | grep -v METPLUS | grep -v \"METplus took\" | grep -v \"Finished\" | grep -v \"\-\-\-\" | egrep -v \"^[[:digit:]]*c[[:digit:]]*$\" | less")
    
if __name__ == "__main__":
    main()
