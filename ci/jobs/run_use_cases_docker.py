#! /usr/bin/env python3

import os
import sys
import subprocess
import shlex

import get_use_case_commands

# add ci/util to sys path to get diff utility
diff_util_dir = os.path.join(os.environ.get('GITHUB_WORKSPACE'),
                             'ci',
                             'util')
sys.path.insert(0, diff_util_dir)
from diff_util import compare_dir

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
        if reqs:
            reqs_fmt = f"{';'.join(reqs)};"
        else:
            reqs_fmt = ''
        print(f'{reqs}\n{cmd}')
        full_cmd = f"{reqs_fmt}{cmd}"
        try:
            subprocess.run(full_cmd, check=True, shell=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed: {full_cmd} -- {err}")
            isOK = False

    if compare and isOK:
        print('******************************')
        print("Comparing output to truth data")
        truth_dir = '/data/truth'
        output_dir = '/data/output'
        if not compare_dir(truth_dir, output_dir, debug=True):
            isOK = False

    if not isOK:
        sys.exit(1)

if __name__ == '__main__':
    main()
