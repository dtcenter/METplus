#! /usr/bin/env python3

import sys
import subprocess
import shlex

import get_use_case_commands

def main():
    categories, subset_list = get_use_case_commands.handle_command_line_args()
    all_commands = get_use_case_commands.main(categories,
                                              subset_list,
                                              work_dir=os.environ.get('DOCKER_WORK_DIR'))

    isOK = True
    for cmd in all_commands:
        print(cmd)
        try:
            subprocess.run(shlex.split(cmd), check=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed: {cmd} -- {err}")
            isOK = False

    if not isOK:
        sys.exit(1)

if __name__ == '__main__':
    main()
