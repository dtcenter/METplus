#! /usr/bin/env python3

################################################################################
# Name: setup_next_release_data.py
# Author: George McCabe (mccabe@ucar.edu)
# Description: Run this script from the DTC web server after cutting an
#  official release to set up the data directory for the next upcoming
#  release. For example, if 4.0.0 was just created, then run this script
#  with 4.1 as the argument. If 4.1.0 was just created, then run this
#  script with 5.0 as the argument unless it has been decided that we will
#  create a 4.2 release. The script will create a directory for the new
#  version and create symbolic links for each data set to point to the
#  version of that data set that was last updated. For example, if the
#  climate data set has not been updated since v3.1, then the symbolic link
#  will point into the v3.1 directory to that appropriate tar file.
# Usage: setup_next_release_data.py v5.0
################################################################################

import sys
import os
import re
import shutil

DATA_DIR = '/home/met_test/METplus_Data'
VOLUME_MOUNT_FILE = 'volume_mount_directories'

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
        elif os.path.isfile(filepath):
            print(f"\nFound file: {filepath}")
        else:
            print(f"ERROR: Unexpected non-file found: {filepath}")
            return False

        filepath = os.path.realpath(filepath)
        filename = os.path.basename(filepath)
        print(f"Real path: {filepath}")

        # skip files that have a timestamp of .sav in the name
        if '.sav' in filename or sum(x.isdigit() for x in filename) > 7:
            print(f"Skipping file flagged as duplicate: {filename}")
            continue

        linkname = f"{'-'.join(filename.split('-')[0:-1])}.tgz"
        linkpath = os.path.join(version_dir, linkname)
        print(f"Creating symbolic link:\n"
              f"  TO: {filepath}\n  AT: {linkpath}")
        os.symlink(filepath, linkpath)
        found_files = True

    # if found files to link, copy volume_mount_directories file
    if found_files:
        print(f"Copying {VOLUME_MOUNT_FILE} from {check_dir} to {version_dir}")
        from_file = os.path.join(check_dir, VOLUME_MOUNT_FILE)
        to_file = os.path.join(version_dir, VOLUME_MOUNT_FILE)
        if not os.path.exists(from_file):
            print(f"ERROR: {VOLUME_MOUNT_FILE} does not exist in {check_dir}")
            print(f"Please copy the latest version of this file into {version_dir}")
            sys.exit(1)

        shutil.copyfile(from_file, to_file)

    return found_files

def usage():
    print(f"Usage: {os.path.basename(__file__)} vX.Y\n"
          f"Example: {os.path.basename(__file__)} v5.0")
    sys.exit(1)

def main(new_version):
    match = re.match(r'^v([0-9]+)\.([0-9]+)', new_version)
    if not match:
        print(f"ERROR: Version does not match vX.Y format: {new_version}")
        usage()

    major = int(match.group(1))
    minor = int(match.group(2))

    version = f'v{major}.{minor}'
    print(f"Handling {version}")

    version_dir = os.path.join(DATA_DIR, version)

    if os.path.exists(version_dir):
        print(f"ERROR: Directory already exists: {version_dir}")
        sys.exit(1)

    print(f"Creating directory: {version_dir}")
    os.makedirs(version_dir)

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
            check_dir = os.path.join(DATA_DIR, cur_version)
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
        usage()

    new_version = sys.argv[1]
    if not main(new_version):
        print("ERROR: Something went wrong")
        sys.exit(1)
