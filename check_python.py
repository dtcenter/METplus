import argparse
import subprocess
import sys
import re

def main():
    if is_python_version_compatible():
        check_packages()
    else:
        print('Exiting')
        sys.exit(1)
def is_python_version_compatible():
    """Determine whether the user's Python version is what is
        supported.

        Args:

        Returns:
            True if user's python version is compatible with what is supported,
            False otherwise.
    """
    major = sys.version_info.major
    minor = sys.version_info.minor
    your_version = (str)(major)+ '.' + (str)(minor)
    if major != 3:
        print('Only Python 3.6 is supported, you have version ', your_version)
        return False
    else:
        if minor != 6:
            # Print warning that minimum supported
            # version of Python is 3.6
          print(f'Only Python 3.6 is supported, you have version {your_version}')
          return False
        else:
            # OK
            print(f'You are using the correct version of Python: {your_version}')
            return True

def check_packages():
    """Check if the packages installed on the computer on which you
        are executing this script is what is needed.
    """
    required_packages = get_required()
    print(f'required: {required_packages}')
    actual_packages = get_actual()
    print(f'actual_packages: {actual_packages}')

def get_required():
    # Retrieve the requirements.txt file from the METplus top-level directory
    # and store this information in a dictionary, where the key is the package/module
    # and the value is the version.
    requirements_file = "./requirements.txt"
    required_packages = []
    required_dict = {}

    # Get the packages that are required
    with open(requirements_file, 'r') as file:
        for line in file:
            #print(line.strip())
            split_str = line.split('==')
            # print(split_str)
            required_dict['package'] = split_str[0]
            #print(required_dict)
            required_dict['version'] = split_str[1].rstrip()
            # print(f'required dict {required_dict}')
            required_packages.append(required_dict)
            required_dict={}

    # print(required_packages)
    return(required_packages)

def get_actual():
    """""Now run 'pip freeze' on this computer to get the
             actual, currently installed packages/modules.
    """
    with open("actual.txt", "w+") as output:
        subprocess.call(['pip', 'freeze'],  stdout=output)

    # For each package/module in the requirements.txt file, keep track
    # of any missing packages/modules and also keep track of mismatched
    # versions.
    actual_packages = []
    actual_dict = {}
    with open("actual.txt", "r") as file:
        for line in file:
            # print(line.strip())
            split_str = line.split('==')
            # print(split_str)
            actual_dict['package'] = split_str[0]
            # print(required_dict)
            actual_dict['version'] = split_str[1].rstrip()
            # print(f'required dict {required_dict}')
            actual_packages.append(actual_dict)
            actual_dict = {}
        # print(f'actual dict: {actual_packages}')
        return actual_packages


if __name__ == "__main__":
    v = '3.6'
    print('Checking your python version is  {}...'.format(v))
    main()