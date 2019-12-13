import argparse
import subprocess
import sys
import re

def main():
    check_python_version()
    check_packages()
    return 0

def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    your_version = (str)(major)+ '.' + (str)(minor)
    if major != 3:
        print('Only Python 3.6 is supported, you have version ', your_version)
        sys.exit(1)
    else:
        if minor != 6:
            # Print warning that minimum supported
            # version of Python is 3.6
            print('Only Python 3.6 is supported, you have version {major}.{minor}')
        else:
            # OK
            print('You are using the correct version of Python: ', your_version)

def check_packages():
    """Check if the packages installed on the computer on which you
        are executing this script is what is needed.
    """

    # Retrieve the requirements.txt file from the METplus top-level directory
    # and store this information in a dictionary, where the key is the package/module
    # and the value is the version.
    requirements_file = "./requirements.txt"
    required_packages = []
    required_dict = {}
    with open(requirements_file, 'r') as file:
        for line in file:
            #print(line.strip())
            split_str = line.split('==')
            print(split_str)
            required_dict['package'] = split_str[0]
            required_dict['version'] = split_str[1].split()
            required_packages.append(required_dict)

        print(required_packages)






    # Now run 'pip freeze' on this computer and do the same.


    # For each package/module in the requirements.txt file, keep track
    # of any missing packages/modules and also keep track of mismatched
    # versions.


if __name__ == "__main__":
    v = '3.6'
    print('Checking your python version is at least {}...'.format(v))
    main()