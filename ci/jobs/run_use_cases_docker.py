#! /usr/bin/env python3

import os
import sys
import subprocess
import shlex

import get_use_case_commands

def main():
    categories, subset_list = get_use_case_commands.handle_command_line_args()
    categories_list = categories.split(',')
    all_commands = get_use_case_commands.main(categories_list,
                                              subset_list,
                                              work_dir=os.environ.get('GITHUB_WORKSPACE'))

    isOK = True
    for cmd, reqs in all_commands:
        print(f'{reqs}\n{cmd}')
        full_cmd = f"{';'.join(reqs)};{cmd}"
        try:
            subprocess.run(shlex.split(full_cmd), check=True, shell=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed: {full_cmd} -- {err}")
            isOK = False

    if not isOK:
        sys.exit(1)

if __name__ == '__main__':
    main()
