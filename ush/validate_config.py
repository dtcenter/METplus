#!/usr/bin/env python3

"""
Program Name: validate_config.py
Contact(s): George McCabe
Abstract: Checks configuration files and reports if anything needs to be changed
  Prompts user with the changes that will be made and asks if they want to have
  the changes made for them.
History Log:  Initial version
Usage: Call the same as master_metplus.py, 
  i.e. validate_config.py -c <config_file> -c <config_file>
Parameters: None
Input Files: Configuration files
Output Files:
Condition codes:
"""

import subprocess
import shlex
import sys
import os

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir)))

from metplus.util import config_metplus, validate_configuration_variables
from master_metplus import get_config_inputs_from_command_line

def main():
    config_inputs = get_config_inputs_from_command_line()

    # Parse arguments, options and return a config instance.
    config = config_metplus.setup(config_inputs)

    # validate configuration variables
    deprecatedIsOK, fieldIsOK, inoutbaseIsOk, metIsOK, sed_cmds = validate_configuration_variables(config)

    if metIsOK:
        print("No MET config files are using deprecated environment variables")

    # if everything is valid, report success and exit
    if deprecatedIsOK and fieldIsOK and inoutbaseIsOk and metIsOK:
        print("SUCCESS: Configuration passed all of the validation tests.")
        sys.exit(0)

    # if sed commands can be run, output lines that will be changed and ask
    # user if they want to run the sed command
    if sed_cmds:
        for cmd in sed_cmds:
            if cmd.startswith('#Add'):
                add_line = cmd.replace('#Add ', '')
                met_tool = None
                for suffix in ['_REGRID_TO_GRID', '_OUTPUT_PREFIX']:
                    if suffix in add_line:
                        met_tool = add_line.split(suffix)[0]
                        section = 'config'

                for suffix in ['_CLIMO_MEAN_INPUT_TEMPLATE']:
                    if suffix in add_line:
                        met_tool = add_line.split(suffix)[0]
                        section = 'filename_templates'

                if met_tool:
                    print(f"\nIMPORTANT: If it is not already set, add the following in the [{section}] section to "
                          f"your METplus configuration file that sets {met_tool}_CONFIG_FILE:\n")
                    print(add_line)
                    input("Make this change before continuing! [OK]")
                else:
                    print("ERROR: Something went wrong in the validate_config.py script. Please send an email to met_help@ucar.edu.")

                continue

            # remove -i from sed command to avoid replacing in the file
            cmd_no_inline = cmd.replace('sed -i', 'sed')
            split_cmd = shlex.split(cmd_no_inline)
            original_file = split_cmd[-1]

            # call sed command to get result of find/replace
            result = subprocess.check_output(split_cmd, encoding='utf-8').splitlines()

            # compare the result to the original file and show the differences
            with open(original_file, 'r') as f:
                original = [i.replace('\n', '') for i in f.readlines()]

            # if no differences, continue
            if result == original:
                continue

            print(f"\nThe following replacement is suggested for {original_file}\n")

            # loop over before and after files line by line and 
            for old, new in zip(original, result):

                if old != new:
                    print(f"Before:\n{old}\n")
                    print(f"After:\n{new}\n")

            # ask the user if they want to make the changes to their file (y/n default is no)
            run_sed = False
            user_answer = input(f"Would you like the make this change to {original_file}? (y/n)[n]")

            if user_answer and user_answer[0] == 'y':
                run_sed = True

            # if yes, run original sed command
            if run_sed:
                print(f"Running command: {cmd}")
                subprocess.run(shlex.split(cmd))
            else:
                print(f"Skipping sed command for {original_file}")

        print("\nFinished running sed commands.")
        print("\nRerun this script to ensure no other deprecated variables need to be replaced.")
        print("See METplus User's Guide for more information on how to change deprecated variables")


if __name__ == "__main__":
    main()
