#! /usr/bin/env python3

# Used in GitHub Actions (in ci/actions/run_tests/entrypoint.sh)
# to obtain and run commands to run use cases from group,
# execute difference tests if requested, copy error logs and/or
# files that reported differences  into directory to make
# them available in GitHub Actions artifacts for easy review

import os
import sys
import subprocess
import shlex
import shutil

import get_use_case_commands

# add ci/util to sys path to get diff utility
diff_util_dir = os.path.join(os.environ.get('GITHUB_WORKSPACE'),
                             'ci',
                             'util')
sys.path.insert(0, diff_util_dir)
from diff_util import compare_dir

TRUTH_DIR = '/data/truth'
OUTPUT_DIR = '/data/output'
DIFF_DIR = '/data/diff'
ERROR_LOG_DIR = '/data/error_logs'

def copy_error_logs():
    """! Copy log output to error log directory if any use case failed """
    use_case_dirs = os.listdir(OUTPUT_DIR)
    for use_case_dir in use_case_dirs:
        log_dir = os.path.join(OUTPUT_DIR,
                               use_case_dir,
                               'logs')
        if not os.path.isdir(log_dir):
            continue

        # check if there are errors in the metplus.log file and
        # only copy directory if there are any errors
        metplus_log = os.path.join(log_dir, 'metplus.log')
        found_errors = False
        with open(metplus_log, 'r') as file_handle:
            if 'ERROR:' in file_handle.read():
                found_errors = True
        if not found_errors:
            continue

        output_dir = os.path.join(ERROR_LOG_DIR,
                                  use_case_dir)
        log_files = os.listdir(log_dir)
        for log_file in log_files:
            log_path = os.path.join(log_dir, log_file)
            output_path = os.path.join(output_dir, log_file)
            print(f"Copying {log_path} to {output_path}")
            # create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            shutil.copyfile(log_path, output_path)

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

    print(f'Copying {file_path} to\n{output_path}')
    try:
        shutil.copyfile(file_path, output_path)
    except OSError as err:
        print(f'Could not copy file. {err}')
        return False

    return True

def main():
    categories, subset_list, run_diff = (
        get_use_case_commands.handle_command_line_args()
    )
    categories_list = categories.split(',')
    all_commands = (
        get_use_case_commands.main(categories_list,
                                   subset_list,
                                   work_dir=os.environ.get('GITHUB_WORKSPACE'))
    )

    isOK = True
    for cmd, reqs in all_commands:
        reqs_fmt = ''
        print(cmd)
#        if reqs:
#            reqs_fmt = f"{';'.join(reqs)};"
#        else:
#            reqs_fmt = ''
#        print(f'{reqs}\n{cmd}')
        full_cmd = f"{reqs_fmt}{cmd}"
        try:
            subprocess.run(full_cmd, check=True, shell=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed: {full_cmd} -- {err}")
            isOK = False
            copy_error_logs()

    if run_diff and isOK:
        print('******************************')
        print("Comparing output to truth data")
        diff_files = compare_dir(TRUTH_DIR, OUTPUT_DIR,
                                 debug=True,
                                 save_diff=True)
        if diff_files:
            isOK = False

            # copy difference files into directory
            # so it can be easily downloaded and compared
            copy_diff_output(diff_files)

    if not isOK:
        sys.exit(1)

if __name__ == '__main__':
    main()
