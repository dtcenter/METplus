#! /usr/bin/env python3

import sys
import os
import glob

# strings to search for to find errors
error_str = 'ERROR'
command_start_str = 'COPYABLE ENVIRONMENT FOR NEXT COMMAND'
check_logfile_string = "Check the logfile for more information on why it failed"

def run(output_dir, replacement_dir=None):
    """! Search for logs under output_dir that have MET errors and print the
         commands that have errors to the screen. Assumes logs are either in
         {output_dir}/logs or {output_dir}/<subdir>/logs where <subdir> is
         any subdirectory under the output directory
         @param output_dir directory to search for logs
         @param replacement_dir directory to replace for output_dir to find
          files. This is needed when running through Travis because the
          directory in Travis differs from the directory listed in the log
          files because the are run in the Docker container.
    """
    # pytest logs directory is in top level of output_dir
    log_topdir_glob = os.path.join(output_dir,
                                   'logs',
                                   '*')

    # use case logs directory are in each subdirectory in output_dir
    log_subdir_glob = os.path.join(output_dir,
                                   '*',
                                   'logs',
                                   '*')
    logs_with_errors = set()

    # get list of log files that have MET errors in them using check_logfile_string
    all_log_files = glob.glob(log_topdir_glob) + glob.glob(log_subdir_glob)
    for log_file in all_log_files:

        with open(log_file, 'r') as file_handle:
            lines = file_handle.readlines()

        for line in lines:
            if check_logfile_string in line:
                error_log = line.split(':')[-1].strip()
                logs_with_errors.add(error_log)

    # find error lines and get text for command that contains the error
    for log_file in logs_with_errors:
        try:
            if replacement_dir:
                local_log_file = log_file.replace(replacement_dir, output_dir)

            with open(local_log_file, 'r') as file_handle:
                lines = file_handle.readlines()
        except OSError:
            print(f"ERROR: Could not open {local_log_file}")
            continue

        error_indices = []
        command_start_indices = []
        for index, line in enumerate(lines):
            if line.startswith(error_str):
                error_indices.append(index)
            if command_start_str in line:
                command_start_indices.append(index)

        if not error_indices:
            continue

        lines_to_print = set()
        for index, command_start_2 in enumerate(command_start_indices):
            if index == 0:
                continue

            command_start_1 = command_start_indices[index-1]
            # check if any error lines are found between command start lines
            for error_index in error_indices:
                if error_index > command_start_1 and error_index < command_start_2:
                    lines_to_print.add((command_start_1, command_start_2))

        for start_index, end_index in lines_to_print:
            print(f"\nPrinting lines {start_index} to {end_index} "
                  f"from {local_log_file}")
            for line in lines[start_index:end_index]:
                print(line.strip())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Must supply directory to search as argument")
        sys.exit(1)
    elif len(sys.argv) > 2:
        replacement_dir = sys.argv[2]
    else:
        replacement_dir = None

    output_dir = sys.argv[1]
    run(output_dir, replacement_dir)

