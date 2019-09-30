#!/usr/bin/env python

import os
from os.path import dirname, realpath
import glob
import subprocess
import filecmp
import logging
import config_launcher
import time
import calendar
import met_util as util

metplus_home = dirname(dirname(dirname(realpath(__file__))))
use_case_dir = os.path.join(metplus_home,"parm/use_cases")


# change these values to chose to run A or B
run_a = False
run_b = False

# list of use cases to run
param_files = [
                use_case_dir+"/qpf/examples/ruc-vs-s2grib.conf" ,
                use_case_dir+"/qpf/examples/phpt-vs-s4grib.conf" ,
                use_case_dir+"/qpf/examples/phpt-vs-mrms-qpe.conf" ,
                use_case_dir+"/qpf/examples/hrefmean-vs-mrms-qpe.conf" ,
                use_case_dir+"/qpf/examples/nationalblend-vs-mrms-qpe.conf" ,
                use_case_dir+"/qpf/examples/hrefmean-vs-qpe-gempak.conf" ,
                use_case_dir+"/grid_to_grid/examples/anom.conf" ,
                use_case_dir+"/grid_to_grid/examples/anom_height.conf",
                use_case_dir+"/grid_to_grid/examples/sfc.conf" ,
                use_case_dir+"/grid_to_grid/examples/precip.conf",
                use_case_dir+"/grid_to_grid/examples/precip_continuous.conf" ,
                use_case_dir+"/mode/examples/hrefmean-vs-mrms-qpe-mode.conf",
                use_case_dir+"/mode/examples/phpt-vs-qpe-mtd.conf",
                use_case_dir+"/ensemble/examples/hrrr_ensemble_sfc.conf" ,
                use_case_dir+"/grid_to_obs/grid_to_obs.conf,"+use_case_dir+"/grid_to_obs/examples/conus_surface.conf",
                use_case_dir+"/grid_to_obs/grid_to_obs.conf,"+use_case_dir+"/grid_to_obs/examples/upper_air.conf",
                use_case_dir+"/feature_relative/feature_relative.conf",
                use_case_dir+"/feature_relative/feature_relative.conf,"+use_case_dir+"/feature_relative/examples/series_by_init_12-14_to_12-16.conf" ,
                use_case_dir+"/feature_relative/feature_relative.conf,"+use_case_dir+"/feature_relative/examples/series_by_lead_all_fhrs.conf" ,
                use_case_dir+"/feature_relative/feature_relative.conf,"+use_case_dir+"/feature_relative/examples/series_by_lead_by_fhr_grouping.conf",
                use_case_dir+"/ensemble/examples/hrrr_ensemble_sfc_wildcard.conf",
                use_case_dir+"/track_and_intensity/examples/atcf_by_dir.conf",
                use_case_dir+"/track_and_intensity/examples/atcf_by_file.conf",
                use_case_dir+"/track_and_intensity/examples/hwrf.conf",
                use_case_dir+"/track_and_intensity/examples/hwrf_orig_files.conf",
                use_case_dir+"/track_and_intensity/examples/sbu.conf",
                use_case_dir+"/track_and_intensity/examples/track_and_intensity_ATCF.conf",
              ]

def get_param_list(param_a, param_b):
    metplus_home = dirname(dirname(dirname(realpath(__file__))))
    a_conf = metplus_home+"/internal_tests/use_cases/system.a.conf"
    b_conf = metplus_home+"/internal_tests/use_cases/system.b.conf"
    params_a = param_a.split(",")
    params_b = param_b.split(",")
    params_a = params_a + [a_conf]
    params_b = params_b + [b_conf]
    return params_a, params_b


def get_params(param_a, param_b):
    params_a, params_b = get_param_list(param_a, param_b)

    logger = logging.getLogger('master_metplus')    

    # read A confs
    (parm, infiles, moreopt) = config_launcher.parse_launch_args(params_a,
                                                                 None, None,
                                                                 logger,
                                                                 util.baseinputconfs)
    p = config_launcher.launch(infiles, moreopt)

    # read B confs     
    (parm, infiles, moreopt) = config_launcher.parse_launch_args(params_b,
                                                                 None, None,
                                                                 logger,
                                                                 util.baseinputconfs)
    p_b = config_launcher.launch(infiles, moreopt)
    return p, p_b

def run_test_use_case(param_a, param_b, run_a, run_b):
    params_a, params_b = get_param_list(param_a, param_b)
    p, p_b = get_params(param_a, param_b)
    a_dir = os.path.join(p.getdir('OUTPUT_BASE'), os.path.basename(params_a[-2]))
    b_dir = os.path.join(p_b.getdir('OUTPUT_BASE'), os.path.basename(params_b[-2]))

    # run A
    if run_a:
        metplus_base_a = os.environ['METPLUS_TEST_A_METPLUS_BASE']
        cmd = os.path.join(metplus_base_a, "ush", "master_metplus.py")
        for parm in params_a:
            cmd += " -c "+parm
        cmd += ' -c dir.OUTPUT_BASE='+a_dir
        print("CMD A:"+cmd)
        process = subprocess.Popen(cmd, shell=True)
        process.wait()

    # run B
    if run_b:
        metplus_base_b = os.environ['METPLUS_TEST_B_METPLUS_BASE']
        cmd = os.path.join(metplus_base_b, "ush", "master_metplus.py")
        for parm in params_b:
            cmd += " -c "+parm
        cmd += ' -c dir.OUTPUT_BASE='+b_dir
        print("CMD B:"+cmd)
        process = subprocess.Popen(cmd, shell=True)
        process.wait()

def main():



    metplus_base_a = os.environ['METPLUS_TEST_A_METPLUS_BASE']
    metplus_base_b = os.environ['METPLUS_TEST_B_METPLUS_BASE']
    print("Starting test script")

    for param_file in param_files:
        param_a = param_file.replace(metplus_home, metplus_base_a)
        param_b = param_file.replace(metplus_home, metplus_base_b)
        run_test_use_case(param_a, param_b, run_a, run_b)

    # compare results with commands
    output_base_a = os.environ['METPLUS_TEST_A_OUTPUT_BASE']
    output_base_b = os.environ['METPLUS_TEST_B_OUTPUT_BASE']


    print("Run the following to compare results:")
    print("diff -r {} {} | grep -v Binary | grep -v SSH_CLIENT | grep -v CONDA | grep -v OLDPWD | grep -v KRB5 | grep -v CLOCK_TIME | grep -v XDG | grep -v GSL | grep -v METPLUS".format(output_base_a, output_base_b))
    print("NOTE: pipe results to 'grep Only' to see which files were only in one output directory")
    
if __name__ == "__main__":
    main()
