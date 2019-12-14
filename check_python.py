import argparse
import subprocess
import sys
import re

# Global
# SUPPORTED_VERSION = '3.6'
SUPPORTED_VERSION = '3.7'

def main():
    if is_python_version_compatible():
        check_packages()
    else:
        print('Exiting')
        sys.exit(1)

def get_supported_major_minor():
    '''Deconstruct the supported version string into
       a major and minor number
       Args:

       Returns:
       :return:  A tuple of major, minor values
    '''

    match = re.match(r'([0-9]{1,3}).([0-9]{1,3})' , SUPPORTED_VERSION)
    if match:
        supported_major = match.group(1)
        supported_minor = match.group(2)
    return supported_major, supported_minor

def is_python_version_compatible():
    """Determine whether the user's Python version is what is
        supported.
        Args:
        Returns:
            True if user's python version is compatible with what is supported,
            False otherwise.
    """
    major = str(sys.version_info.major)
    minor = str(sys.version_info.minor)
    your_version = major + '.' + minor
    supported_major, supported_minor = get_supported_major_minor()
    if major != supported_major:
        print('Only Python {SUPPORTED_VERSION} is supported, you have version ', your_version)
        return False
    else:
        if minor != supported_minor:
            # Print warning that minimum supported
            # version of Python is 3.6
          print(f'Only Python {SUPPORTED_VERSION} is supported, you have version {your_version}')
          return False
        else:
            # OK
            print(f'You are using the correct version of Python: {your_version}')
            return True

def check_packages():
    """Check if the packages installed on the computer on which you
        are executing this script is what is needed.
    """
    required_packages = get_required_packages()
    print(f'required: {required_packages}')
    actual_packages = get_actual_packages()
    print(f'actual_packages: {actual_packages}')
    missing_packages_list = find_missing_packages(required_packages, actual_packages)

def get_required_packages():
    ''''Retrieve the requirements.txt file from the METplus top-level directory
       and store this information in a dictionary, where the key is the package/module
       and the value is the version.
   '''
    requirements_file = "./requirements.txt"
    required_packages = []

    # Get the packages that are required
    with open(requirements_file, 'r') as file:
        for line in file:
            split_str = line.split('==')
            required_dict = {}
            required_dict['package'] = split_str[0]
            required_dict['version'] = split_str[1].rstrip()
            required_packages.append(required_dict)
    return(required_packages)

def get_actual_packages():
    """Now run 'pip freeze' on this computer to get the
             actual, currently installed packages/modules.
    """
    with open("actual.txt", "w+") as output:
        subprocess.call(['pip', 'freeze'],  stdout=output)

    # For each package/module in the requirements.txt file, keep track
    # of any missing packages/modules and also keep track of mismatched
    # versions.
    actual_packages = []
    with open("actual.txt", "r") as file:
        for line in file:
            split_str = line.split('==')
            actual_dict = {}
            actual_dict['package'] = split_str[0]
            actual_dict['version'] = split_str[1].rstrip()
            actual_packages.append(actual_dict)
        return actual_packages

def find_missing_packages(required_packages, actual_packages):
    '''Find any packages that are missing from the user's host and print
       output to stdout and create a text file indicating the missing package and its
       version.

       Args:
           required_packages:  The list of required packages
           actual_packages:  The list of packages on the user's host

       Returns:
            A list containing the missing packages (and versions)

    '''

    missing_packages_list = []
    # Get a list of all the keys in the required_packages and for the
    # actual_packages and check for the absence of packages based
    # on the keys.
    required_keys = []
    for required in required_packages:
        required_keys.append(required['package'])
    actual_keys = []
    for actual in actual_packages:
        actual_keys.append(actual['package'])

    # Now search for missing packages in the user's environment
    for required in required_keys:
        if required not in actual_keys:
            missing_packages_list.append(required)
    print(f'missing packages: {missing_packages_list}')

if __name__ == "__main__":

    print('Checking your python version is  {}...'.format(SUPPORTED_VERSION))
    maj, min = get_supported_major_minor()
    print(f'major version {maj}, minor version {min}')
    main()