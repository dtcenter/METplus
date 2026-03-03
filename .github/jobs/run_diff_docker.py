#! /usr/bin/env python3

# Used in GitHub Actions (in .github/actions/run_tests/entrypoint.sh)
# to obtain and run commands to run use cases from group,
# execute difference tests if requested, copy error logs and/or
# files that reported differences  into directory to make
# them available in GitHub Actions artifacts for easy review

import os
import sys
import subprocess
import shlex
import shutil

GITHUB_WORKSPACE = os.environ.get('GITHUB_WORKSPACE')

# add util directory to sys path to get diff utility
diff_util_dir = os.path.join(GITHUB_WORKSPACE, 'metplus', 'util')
sys.path.insert(0, diff_util_dir)
import diff_util

diff_util.SKIP_KEYWORDS = [
    'CyclonePlotter/cyclone/20150301.png',
    'plots/obs_elbow.png',
    'plots/fcst_elbow.png',
    'CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC/cyclone/20201007',
    'plots/MAKE_MAKI_timeseries',
    'UserScript_fcstGFS_obsERA_WeatherRegime',
    'PointStat_fcstWRF_obsMADIS_hurricane_matthew/wrf_plot',
]

diff_util.ROUNDING_OVERRIDES = {
    'UserScript_obsCFSR_obsOnly_MJO_ENSO': 5,
    'UserScript_fcstS2S_obsERAI_CrossSpectra': 4,
}

TRUTH_DIR = '/data/truth'
OUTPUT_DIR = '/data/output'
DIFF_DIR = '/data/diff'


def main():
    print('******************************')
    print("Comparing output to truth data")
    diff_files = diff_util.compare_dir(TRUTH_DIR, OUTPUT_DIR,
                                       debug=True, save_diff=True)

    # copy difference files into directory
    # so it can be easily downloaded and compared
    if diff_files:
        diff_util.copy_diff_output(diff_files, TRUTH_DIR, OUTPUT_DIR, DIFF_DIR)


if __name__ == '__main__':
    main()
