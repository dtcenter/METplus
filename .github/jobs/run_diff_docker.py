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
diff_util_dir = os.path.join(GITHUB_WORKSPACE,
                             'metplus',
                             'util')
sys.path.insert(0, diff_util_dir)
from diff_util import compare_dir

TRUTH_DIR = '/data/truth'
OUTPUT_DIR = '/data/output'
DIFF_DIR = '/data/diff'

def copy_diff_output(diff_files):
    """!  Loop through difference output and copy files
    to directory so it can be made available for comparison.
    Files will be put into the same directory with _truth or
    _output added before their file extension.

    @param diff_files list of tuples containing truth file path
     and file path of output that was just generated. Either tuple
     value may be an empty string if the file was not found.
    """
    for truth_file, out_file, _, diff_file in diff_files:
        if truth_file:
            copy_to_diff_dir(truth_file,
                             'truth')
        if out_file:
            copy_to_diff_dir(out_file,
                             'output')
        if diff_file:
            copy_to_diff_dir(diff_file,
                             'diff')

def copy_to_diff_dir(file_path, data_type):
    """! Generate output path based on input file path,
    adding text based on data_type to the filename, then
    copy input file to that output path.

    @param file_path full path of file to copy
    @param data_type data identifier, should be 'truth'
     or 'output'
    @returns True if success, False if there was a problem
     copying the file
    """
    if data_type == 'truth':
        data_dir = TRUTH_DIR
    else:
        data_dir = OUTPUT_DIR

    # replace data dir with diff directory
    diff_out = file_path.replace(data_dir, DIFF_DIR)

    # add data type identifier to filename before extension
    # if data is not difference output
    if data_type == 'diff':
        output_path = diff_out
    else:
        output_path, extension = os.path.splitext(diff_out)
        output_path = f'{output_path}_{data_type}{extension}'

    # create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        shutil.copyfile(file_path, output_path)
    except OSError as err:
        print(f'Could not copy file. {err}')
        return False

    return True

def main():
    print('******************************')
    print("Comparing output to truth data")
    diff_files = compare_dir(TRUTH_DIR, OUTPUT_DIR,
                             debug=True,
                             save_diff=True)

    # copy difference files into directory
    # so it can be easily downloaded and compared
    if diff_files:
        copy_diff_output(diff_files)

if __name__ == '__main__':
    main()
