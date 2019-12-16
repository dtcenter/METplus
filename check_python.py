#!/usr/bin/env python

import subprocess
import sys
import re

# Global
SUPPORTED_VERSION = '3.6'
#SUPPORTED_VERSION = '3.7'

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
    print('Checking your python version is  {}...'.format(SUPPORTED_VERSION))

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
    actual_packages = get_actual_packages()
    missing_packages_list = find_missing_packages(required_packages, actual_packages)
    print_missing_packages(missing_packages_list, required_packages)
    mismatched_versions_list = find_mismatched_packages(required_packages, actual_packages)
    print_mismatched_versions(mismatched_versions_list)

def get_required_packages():
    ''''Retrieve the requirements.txt file from the METplus top-level directory
       and store this information in a dictionary, where the key is the package/module
       and the value is the version. Create a dictionary
        containing the names of the packages (key) and their
        corresponding version numbers (value).
   '''
    requirements_file = "./requirements.txt"
    required_dict = {}
    # Get the packages that are required
    with open(requirements_file, 'r') as file:
        for line in file:
            split_str = line.split('==')
            required_dict[split_str[0]] = split_str[1].rstrip()
    return(required_dict)

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
    actual_dict = {}
    with open("actual.txt", "r") as file:
        for line in file:
            split_str = line.split('==')
            actual_dict[split_str[0]] = split_str[1].rstrip()
        return actual_dict

def find_missing_packages(required_packages, actual_packages):
    '''Find any packages that are missing from the user's host and print
       output to stdout and create a text file indicating the missing package and its
       version.

       Args:
           required_packages:  A dictionary of required packages
           actual_packages:  A dictionary of packages on the user's host

       Returns:
            A list containing the  missing packages with their corresponding
            versions

    '''

    missing_packages_list = []
    # Get a list of all the keys in the required_packages and for the
    # actual_packages and check for the absence of packages based
    # on the keys.
    required_keys = []
    for required in required_packages:
        required_keys.append(required)

    actual_keys = []
    for actual in actual_packages:
        actual_keys.append(actual)

    # Now search for missing packages in the user's environment
    for required in required_keys:
        if required not in actual_keys:
            missing_packages_list.append(required)
    return missing_packages_list

def print_missing_packages(missing_packages_list, required_packages):
    '''

    :param missing_packages_list:  A list of the missing packages
    :param required_packages:  A dictionary of package:version that are
                                                required to run METplus
    :return:
        Nothing, prints to stdout and creates a text output file containing
        a list of the missing Python packages/modules and their corresponding
        version numbers.
    '''

    # Create a list of the missing packages and their versions to print to
    # stdout
    print('\n=================================================\n')
    print('MISSING PACKAGES that need to be installed...\n')
    print('=================================================\n')
    print('Package                      Version\n')
    print('-------------------------------------\n')
    with open('./missing_packages.txt', 'w+') as outfile:
        outfile.write("==========================================\n")
        outfile.write("Missing packages that you need to install:\n")
        outfile.write("==========================================\n")
        outfile.write("Package               Version\n")
        outfile.write("------------------------------\n")
        for missing in missing_packages_list:
            outfile.write(f'{missing:20}  {required_packages[missing]:10}\n')
            print(f'{missing:20}          {required_packages[missing]:10}')
        print("\n")

def find_mismatched_packages(required_packages, actual_packages):
    ''' Find which user's packages are mismatched from the
        required packages.

        Args:
            required_packages: A dictionary of required packages:versions
            actual_packages: A dictionary of packages:versions that are
                                        installed on the user's computer

        Returns:
            A list of a tuple containing the package name,
            the incorrect version, and  the required version that is installed
            on the user's computer.

    '''
    missing_packages_list = []
    # Get a list of all the keys in the required_packages and for the
    # actual_packages and check for the absence of packages based
    # on the keys.
    required_keys = []
    for required in required_packages:
        required_keys.append(required)

    actual_keys = []
    for actual in actual_packages:
        actual_keys.append(actual)

    # Now search for mismatched versions in the user's environment
    mismatched_list = []
    for required in required_keys:
        if required in actual_keys:
            if required_packages[required] != actual_packages[required]:
                mismatch_tuple = (required, actual_packages[required], required_packages[required])
                mismatched_list.append(mismatch_tuple)
    return mismatched_list

def print_mismatched_versions(mismatched_versions_list):
        '''
        Prints to stdout and to a file, the packages with mismatched version
        the required version.

        :param mismatched_version_list:  The list of tuples containing the
        package, the user's version, and the required version
        :return:
        None, prints to stdout and wriite to a file a list of the packages, the
        currently installed version, and the required version.
        '''
        print("============================\n")
        print("Mismatched package versions\n")
        print("============================\n")
        print(f"Required Package             Installed Version    Required Version\n")
        print(f"-------------------------------------------------------------------\n")
        with open('./mismatched.txt', 'w+') as outfile:
            outfile.write("=====================================\n")
            outfile.write("Mismatched package versions found...\n")
            outfile.write("=====================================\n")
            outfile.write(f"Required Package             Installed Version    Required Version\n")
            outfile.write(f"---------------------------------------------------------------------\n")

            for mismatch in mismatched_versions_list:
                outfile.write(f'{mismatch[0]:20}           {mismatch[1]:10}         {mismatch[2]:10}\n')
                print(f' {mismatch[0]:20}        {mismatch[1]:10}          {mismatch[2]:10}')




if __name__ == "__main__":
    main()
