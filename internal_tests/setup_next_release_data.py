#! /usr/bin/env python3

################################################################################
# Script: setup_next_release_data.py
# Author: George McCabe, NCAR (May 2021)
# Description: Script run on DTCenter web server to create a directory to hold
#  sample input data for the upcoming release. The script takes a single
#  argument which is the major/minor version number, i.e. v4.1.
#  The directory must either not exist or be completely empty. The script
#  searches through the previous version numbers to find a directory that
#  contains files and/or symbolic links. It creates a symbolic link in the new
#  directory that points to the latest version of each sample data tarfile.
#  Note that we typically create releases named vX.0 and vX.1, but the script
#  will properly handle minor versions up to vX.5 if they exist just in case
#  we change our release naming convention.
# Usage: setup_next_release_data.py v4.1
################################################################################

import sys
import os
import re

data_dir = '/home/met_test/METplus_Data'

def get_files_from_dir(version_dir, check_dir):
    files = os.listdir(check_dir)
    if not files:
        return False

    print(f"Using {check_dir}")

    found_files = False
    for filename in files:
        if not filename.startswith('sample_data'):
            continue

        filepath = os.path.join(check_dir, filename)
        if os.path.islink(filepath):
            print(f"\nFound symbolic link: {filepath}")
            filepath = os.path.realpath(filepath)
            filename = os.path.basename(filepath)
            print(f"Real path: {filepath}")
        elif os.path.isfile(filepath):
            print(f"\nFound file: {filepath}")
        else:
            print(f"ERROR: Unexpected non-file found: {filepath}")
            return False

        linkname = f"{'-'.join(filename.split('-')[0:-1])}.tgz"
        linkpath = os.path.join(version_dir, linkname)
        print(f"Creating symbolic link:\n"
              f"  TO: {filepath}\n  AT: {linkpath}")
        os.symlink(filepath, linkpath)
        found_files = True

    return found_files
                
def main(new_version):
    match = re.match(r'^v([0-9]+)\.([0-9]+)', new_version)
    if not match:
        print(f"ERROR: Version does not match vX.Y format: {new_version}")
        sys.exit(1)

    major = int(match.group(1))
    minor = int(match.group(2))

    version = f'v{major}.{minor}'
    print(f"Handling {version}")

    version_dir = os.path.join(data_dir, version)

    if not os.path.exists(version_dir):
        print(f"Creating directory: {version_dir}")
        os.makedirs(version_dir)

    if os.listdir(version_dir):
        print(f"ERROR: Directory is not empty: {version_dir}")
        sys.exit(1)

    # loop down versions, i.e. 4.0, 3.1, 3.0, 2.X, etc.
    for cur_major in range(major, -1, -1):
        # if looking at the major version
        if cur_major == major:
            # if minor is 0, skip to next major
            if minor == 0:
                continue
            # otherwise start with 1 below minor version
            minor_start = minor - 1
        # if looking at lower than major, start minor
        # with 5 in case minor > 1 is created
        else:
            minor_start = 5

        for cur_minor in range(minor_start, -1, -1):
            cur_version = f'v{cur_major}.{cur_minor}'
            print(f"Looking for {cur_version}")
            check_dir = os.path.join(data_dir, cur_version)
            if os.path.exists(check_dir):
                if get_files_from_dir(version_dir, check_dir):
                    print("\nSymbolic links created "
                          f"successfully in {version_dir}")
                    return True

    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("ERROR: Must supply new major/minor version "
              "as argument, i.e. v4.0")
        sys.exit(1)

    new_version = sys.argv[1]
    if not main(new_version):
        print("Something went wrong")
        sys.exit(1)
