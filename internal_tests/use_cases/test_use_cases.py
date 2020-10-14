#!/usr/bin/env python3

"""
Program Name: test_use_cases.py
Contact(s): George McCabe
Abstract: Runs METplus use cases
History Log:  Initial version
Usage: test_use_cases.py <host> [--<use_case_category>]
<host> is the name of the host running the test or ID for running on machines that don't have constant $HOSTNAME ,
    i.e. docker
<use_case_category> is the section of use cases to process, i.e. met_tool_wrapper or precipitation
The user can add explicit use cases to run in the force_use_cases_to_run list to force specific use cases
    to run locally
Condition codes: 0 on success, 1 on failure
"""

import os
import sys
from os.path import dirname, realpath
import glob
import shutil
import subprocess
import filecmp
import logging
import time
import calendar
import argparse

from metplus.util import config_metplus

# keep track of use cases that failed to report at the end of execution
failed_runs = []

metplus_home = dirname(dirname(dirname(realpath(__file__))))
use_case_dir = os.path.join(metplus_home,"parm/use_cases")

# explicit list of use cases to run
# the use cases added here will be run regardless of command line arguments
force_use_cases_to_run = [

]

# all use cases sorted by category to be able to run subsets of tests easily in CI
use_cases = {}
use_cases['met_tool_wrapper'] = [
                use_case_dir + "/met_tool_wrapper/ASCII2NC/ASCII2NC.conf",
                use_case_dir + "/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding_user_py.conf",
                use_case_dir + "/met_tool_wrapper/PyEmbedIngest/PyEmbedIngest.conf",
                use_case_dir + "/met_tool_wrapper/EnsembleStat/EnsembleStat.conf",
                use_case_dir + "/met_tool_wrapper/EnsembleStat/EnsembleStat_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/Example/Example.conf",
                use_case_dir + "/met_tool_wrapper/GempakToCF/GempakToCF.conf",
                use_case_dir + "/met_tool_wrapper/GenVxMask/GenVxMask.conf",
                use_case_dir + "/met_tool_wrapper/GenVxMask/GenVxMask_multiple.conf",
                use_case_dir + "/met_tool_wrapper/GenVxMask/GenVxMask_with_arguments.conf",
                use_case_dir + "/met_tool_wrapper/GridDiag/GridDiag.conf",
                use_case_dir + "/met_tool_wrapper/GridStat/GridStat.conf",
                use_case_dir + "/met_tool_wrapper/GridStat/GridStat.conf," + use_case_dir + "/met_tool_wrapper/GridStat/GridStat_forecast.conf,dir.GRID_STAT_OUTPUT_DIR={OUTPUT_BASE}/met_tool_wrapper/GridStat/GridStat_multiple_config," + use_case_dir + "/met_tool_wrapper/GridStat/GridStat_observation.conf",
                use_case_dir + "/met_tool_wrapper/MODE/MODE.conf",
                use_case_dir + "/met_tool_wrapper/MTD/MTD.conf",
                use_case_dir + "/met_tool_wrapper/MTD/MTD_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/PB2NC/PB2NC.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_sum.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_add.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_bucket.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_user_defined.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_derive.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_loop_custom.conf",
#                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/PCPCombine/PCPCombine_subtract.conf",
                use_case_dir + "/met_tool_wrapper/PointStat/PointStat.conf",
                use_case_dir + "/met_tool_wrapper/Point2Grid/Point2Grid.conf",
                use_case_dir + "/met_tool_wrapper/PointStat/PointStat_once_per_field.conf",
                use_case_dir + "/met_tool_wrapper/RegridDataPlane/RegridDataPlane.conf",
                use_case_dir + "/met_tool_wrapper/RegridDataPlane/RegridDataPlane_multi_field_multi_file.conf",
                use_case_dir + "/met_tool_wrapper/RegridDataPlane/RegridDataPlane_multi_field_one_file.conf",
                use_case_dir + "/met_tool_wrapper/RegridDataPlane/RegridDataPlane_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/StatAnalysis/StatAnalysis.conf",
                use_case_dir + "/met_tool_wrapper/StatAnalysis/StatAnalysis_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis.conf",
                use_case_dir + "/met_tool_wrapper/SeriesAnalysis/SeriesAnalysis_python_embedding.conf",
                use_case_dir + "/met_tool_wrapper/TCGen/TCGen.conf",
                use_case_dir + "/met_tool_wrapper/TCPairs/TCPairs_extra_tropical.conf",
                use_case_dir + "/met_tool_wrapper/TCPairs/TCPairs_tropical.conf",
                use_case_dir + "/met_tool_wrapper/TCRMW/TCRMW.conf",
                use_case_dir + "/met_tool_wrapper/TCStat/TCStat.conf",
]

use_cases['climate'] = [
    use_case_dir + "/model_applications/climate/GridStat_fcstCESM_obsGFS_ConusTemp.conf",
    use_case_dir + "/model_applications/climate/MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf",
]

use_cases['convection_allowing_models'] = [
                use_case_dir + "/model_applications/convection_allowing_models/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf",
                use_case_dir + "/model_applications/convection_allowing_models/MODE_fcstHRRR_obsMRMS_Hail_GRIB2.conf",
                use_case_dir + "/model_applications/convection_allowing_models/EnsembleStat_fcstHRRR_fcstOnly_SurrogateSevere.conf",
                use_case_dir + "/model_applications/convection_allowing_models/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf",
                use_case_dir + "/model_applications/convection_allowing_models/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevereProb.conf",
                use_case_dir + "/model_applications/convection_allowing_models/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf",
]


use_cases['cryosphere'] = [
    use_case_dir + "/model_applications/cryosphere/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf",
]

use_cases['medium_range1'] = [
    use_case_dir + "/model_applications/medium_range/PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf",
    use_case_dir + "/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf",
    use_case_dir + "/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf",
#    use_case_dir + "/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf",
    use_case_dir + "/model_applications/medium_range/GridStat_fcstGFS_obsGFS_climoNCEP_MultiField.conf",
    use_case_dir + "/model_applications/medium_range/GridStat_fcstGFS_obsGFS_Sfc_MultiField.conf",
]

use_cases['medium_range2'] = [
    use_case_dir + "/model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf",
]

use_cases['medium_range3'] = [
    use_case_dir + "/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf",
]

use_cases['precipitation'] = [
                use_case_dir + "/model_applications/precipitation/GridStat_fcstGFS_obsCCPA_GRIB.conf",
                use_case_dir + "/model_applications/precipitation/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf",
                use_case_dir + "/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_Gempak.conf",
                use_case_dir + "/model_applications/precipitation/GridStat_fcstHREFmean_obsStgIV_NetCDF.conf",
                use_case_dir + "/model_applications/precipitation/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf",
                use_case_dir + "/model_applications/precipitation/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf",
                use_case_dir + "/model_applications/precipitation/MTD_fcstHRRR-TLE_obsMRMS.conf",
                use_case_dir + "/model_applications/precipitation/EnsembleStat_fcstWOFS_obsWOFS.conf",
]

use_cases['s2s'] = [
    use_case_dir + "/model_applications/s2s/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf",
]

use_cases['space_weather'] = [
    use_case_dir + "/model_applications/space_weather/GridStat_fcstGloTEC_obsGloTEC_vx7.conf",
    use_case_dir + "/model_applications/space_weather/GenVxMask_fcstGloTEC_FcstOnly_solar_altitude.conf",
]

use_cases['tc_and_extra_tc'] = [
    use_case_dir + "/model_applications/tc_and_extra_tc/TCRMW_fcstGFS_fcstOnly_gonzalo.conf",
#    use_case_dir + "/model_applications/tc_and_extra_tc/StatAnalysis_fcstHAFS.conf",
]

# The use cases below require additional dependencies and are no longer run via the use_cases dictionary
# They can be run using the --config option if needed
#    use_cases['met_tool_wrapper'].append(use_case_dir + "/met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf")
#    use_cases['met_tool_wrapper'].append(use_case_dir + "/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf")
#    use_cases['tc_and_extra_tc'].append(use_case_dir + "/model_applications/tc_and_extra_tc/Plotter_fcstGFS_obsGFS_ExtraTC.conf")
#    use_cases['tc_and_extra_tc'].append(use_case_dir + "/model_applications/tc_and_extra_tc/Plotter_fcstGFS_obsGFS_RPlotting.conf")

def get_param_list(param):
    conf = metplus_home+"/internal_tests/use_cases/system.conf"
    params = param.split(",")
    params = params + [conf]
    return params


def get_params(param):
    params = get_param_list(param)

    # read confs
    config = config_metplus.setup(params)

    return params, config

def run_test_use_case(param, test_metplus_base):
    global failed_runs

    params, config = get_params(param)

    # get list of actual param files (ignoring config value overrides)
    # to the 2nd last file to use as the output directory
    # last param file is always the system.conf file
    param_files = [param for param in params if os.path.exists(param)]

    out_dir = os.path.join(config.getdir('OUTPUT_BASE'), os.path.basename(param_files[-2]))

    cmd = os.path.join(test_metplus_base, "ush", "master_metplus.py")
    for parm in params:
        cmd += " -c "+parm
    cmd += ' -c dir.OUTPUT_BASE='+out_dir
    print("CMD:"+cmd)
    process = subprocess.Popen(cmd, shell=True)
    process.communicate()[0]
    returncode = process.returncode
    if returncode:
        failed_runs.append((cmd, out_dir))

#def print_error_logs(out_dir):
#    log_dir = os.path.join(out_dir, 'logs')

def handle_output_directories(output_base, output_base_prev):
    """!if there are files in output base, prompt user to copy them to prev output base
        Args:
            @param output_base directory to write output from the current test run
            @param output_base_prev directory containing files written from previous run
            to compare to the current run
    """
    if os.path.exists(output_base) and os.listdir(output_base):

        # if prev exists, ask user to wipe it out
        if os.path.exists(output_base_prev):

            print("OUTPUT_BASE for previous run exists:" + output_base_prev)
            user_answer = input("Would you like to remove all files? (y/n)[n]")

            if user_answer and user_answer[0] == 'y':
                print("Removing " + output_base_prev + " and all files in it.")
                shutil.rmtree(output_base_prev)
            else:
                print("Directory must be empty to proceed with tests")
                sys.exit(1)

        print("Moving " + output_base + " to " + output_base_prev)
        os.rename(output_base, output_base_prev)

def main():
    global failed_runs

    if not os.environ.get('METPLUS_TEST_METPLUS_BASE'):
        test_metplus_base = metplus_home
    else:
        test_metplus_base = os.environ['METPLUS_TEST_METPLUS_BASE']

    print("Starting test script")
    print("Running " + test_metplus_base + " to test")

    output_base_prev = os.environ['METPLUS_TEST_PREV_OUTPUT_BASE']
    output_base = os.environ['METPLUS_TEST_OUTPUT_BASE']

    # read command line arguments to determine which use cases to run
    parser = argparse.ArgumentParser()
    parser.add_argument('host_id', action='store')
    parser.add_argument('--met_tool_wrapper', action='store_true', required=False)
    parser.add_argument('--climate', action='store_true', required=False)
    parser.add_argument('--convection_allowing_models', action='store_true', required=False)
    parser.add_argument('--cryosphere', action='store_true', required=False)
    parser.add_argument('--medium_range1', action='store_true', required=False)
    parser.add_argument('--medium_range2', action='store_true', required=False)
    parser.add_argument('--precipitation', action='store_true', required=False)
    parser.add_argument('--s2s', action='store_true', required=False)
    parser.add_argument('--space_weather', action='store_true', required=False)
    parser.add_argument('--tc_and_extra_tc', action='store_true', required=False)
    parser.add_argument('--all', action='store_true', required=False)
    parser.add_argument('--config', action='append', required=False)
    parser.add_argument('--skip_output_check',
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    print(args.config)

    if args.skip_output_check:
        print("Skipping output directory check. Output from previous tests "
              "may be found in output directory")
    else:
        handle_output_directories(output_base, output_base_prev)

    if args.config:
        for use_case in args.config:
            config_args = use_case.split(',')
            config_list = []
            for config_arg in config_args:
                # if relative path, must be relative to parm/use_cases
                if not os.path.isabs(config_arg):
                    # check that the full path exists before adding
                    # use_case_dir in case item is a config value override
                    check_config_exists = os.path.join(use_case_dir, config_arg)
                    if os.path.exists(check_config_exists):
                        config_arg = check_config_exists

                config_list.append(config_arg)

            force_use_cases_to_run.append(','.join(config_list))

    # compile list of use cases to run
    use_cases_to_run = []

    # add explicit list of use cases to run
    use_cases_to_run.extend(force_use_cases_to_run)

    # add use case categories if they were provided on the command line

    # if 'all' was specified, add all use cases
    if args.__dict__.get('all'):
        print(f"Adding all use cases")
        for key, value in use_cases.items():
            print(f"Adding {key} use cases")
            use_cases_to_run.extend(value)
    else:
        for key in args.__dict__:
            if args.__dict__[key] and key in use_cases.keys():
                print(f"Adding {key} use cases")
                use_cases_to_run.extend(use_cases[key])

    # exit if use case list is empty
    if not use_cases_to_run:
        print("ERROR: No use cases specified")
        sys.exit(1)

    # run use cases
    for param_file in use_cases_to_run:
        param = param_file.replace(metplus_home, test_metplus_base)
        run_test_use_case(param, test_metplus_base)

    # compare results with commands if prev output base has files
    if not os.path.exists(output_base_prev) or not os.listdir(output_base_prev):
        print("No files were found in previous OUTPUT_BASE: " + output_base_prev +\
              "\nRun this script again to compare results to previous run")
    else:
        print("\nIf files or directories were only found in one run, they will appear when you run the following:\n")
        diff_cmd = f'diff -r {output_base_prev} {output_base} | grep "Only in" | less'
        print(diff_cmd)

        print("\nCompare the output from previous run (" + output_base_prev + ") to this run"+\
              " (" + output_base + ").\nRun the following to compare results:")
        print(f"diff -r {output_base_prev} {output_base} | grep -v Binary | grep -v SSH | grep -v CONDA | grep -v OLDPWD | grep -v tmp | grep -v CLOCK_TIME | grep -v XDG | grep -v GSL | grep -v METPLUS | grep -v \"METplus took\" | grep -v \"Finished\" | grep -v \"\-\-\-\" | egrep -v \"^[[:digit:]]*c[[:digit:]]*$\" | less")

    # list any commands that failed
    for failed_run, out_dir in failed_runs:
        print(f"ERROR: Use case failed: {failed_run}")
#        print_error_logs(out_dir)

    if len(failed_runs) > 0:
        print(f"\nERROR: {len(failed_runs)} use cases failed")
        sys.exit(1)

    print("\nINFO: All use cases returned 0. Success!")
    sys.exit(0)

if __name__ == "__main__":
    main()
