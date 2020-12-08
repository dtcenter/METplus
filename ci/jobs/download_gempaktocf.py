#!/usr/bin/env python3

"""! Downlaods GempakToCF.jar that is used to convert GEMPAK data to NetCDF"""

import os
import shlex
import subprocess

GEMPAK_TO_CF_URL = ('https://dtcenter.org/sites/default/files/community-code/'
                    'metplus/utilities/GempakToCF.jar')

def run(input_data_directory):
    """! Downloads GempakToCF.jar from website into input_data_directory

    @param input_data_directory destination to download file
    @returns True if successful, False if an error occurred
    """
    if not os.path.exists(input_data_directory):
        print(f"Creating directory: {input_data_directory}")
        os.makedirs(input_data_directory)

    print(f"Downloading {GEMPAK_TO_CF_URL} into {input_data_directory}")

    cmd = f"curl -L -O {GEMPAK_TO_CF_URL}"
    try:
        subprocess.run(shlex.split(cmd),
                       check=True,
                       cwd=input_data_directory)
    except subprocess.CalledProcessError as err:
        print(f"ERROR: Download failed: {os.path.basename(GEMPAK_TO_CF_URL)}")
        return False

    return True

if __name__ == "__main__":
    input_data_directory = os.path.join(os.environ['OWNER_BUILD_DIR'],
                                        'input')
    run(input_data_directory)
