#! /usr/bin/env python3

################################################################################
# Used in GitHub Actions (in ci/actions/run_tests/entrypoint.sh) to run cases
# For each use case group specified:
#  - create input Docker data volumes and get --volumes-from arguments
#  - build Docker image with conda environment and METplus branch image
#  - Run commands to run use cases


import os
import sys
import subprocess
import shlex
import shutil

import get_use_case_commands

OUTPUT_DIR = '/data/output'
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

def main():
    categories, subset_list, compare = (
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

    if compare and isOK:
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
