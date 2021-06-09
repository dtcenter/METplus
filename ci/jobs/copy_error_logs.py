#! /usr/bin/env python3

################################################################################
# Used in GitHub Actions (in .github/workflows/testing.yml) to copy logs for
# use cases that reported errors to another directory

import os
import shutil

def main(output_data_dir, error_logs_dir):
    """! Copy log output to error log directory if any use case failed """
    for use_case_dir in os.listdir(output_data_dir):
        log_dir = os.path.join(output_data_dir,
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

        output_dir = os.path.join(error_logs_dir,
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

if __name__ == '__main__':
    output_data_dir = sys.argv[1]
    error_logs_dir = sys.argv[2]
    main(output_data_dir, error_logs_dir)
