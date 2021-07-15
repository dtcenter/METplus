#! /usr/bin/env python3

import os

# Read environment variables that start with METPLUS_INPUT and
# print list of files found in text file set as value

# check inputs 0-9
for index in range(0, 10):
    env_var_name = f'METPLUS_INPUT{index}'
    print(f'Checking environment variable: {env_var_name}')
    file_list_path = os.environ.get(env_var_name)
    if not file_list_path:
        print(f'{env_var_name} is not set or empty')
        continue

    if not os.path.exists(file_list_path):
        print(f'File does not exist: {file_list_path}')
        continue

    with open(file_list_path, 'r') as file_handle:
        input_lines = file_handle.read().splitlines()

    print(f'Contents of {file_list_path}')
    for line in input_lines:
        print(line)

    print()

print(f'End of {__file__} script')
