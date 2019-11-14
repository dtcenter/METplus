# Script: replace_confs.py
# Author: George McCabe, November 2019
# Description: Utility used to rename configuration variables in the METplus
#  wrappers. Modify the script to set the list of directories to search and
#  the dictionary containing the list of variables to replace. The script
#  prints a list of commands to the screen. These commands can be run to
#  find and replace all instances of the configuration variable listed.
#  After running the commands, review 'git diff' to make sure that all of
#  the changes are intended. For each change, documentation needs to be
#  updated to list the new configuration variable name and deprecate the old
#  name.

import os

# set this to the location of METplus you are using
top_level = '/d1/mccabe/METplus'

# list of directories to find/replace
search_dirs = [ 'internal_tests/pytests', 'ush', 'parm' ]

# dictionary of config items to be changed. key is old name, value is new name
change_dict = {

"MODEL_DATA_DIR": "EXTRACT_TILES_GRID_INPUT_DIR",
"NLAT": "EXTRACT_TILES_NLAT",
"NLON": "EXTRACT_TILES_NLON",
"DLAT": "EXTRACT_TILES_DLAT",
"DLON": "EXTRACT_TILES_DLON",
"LON_ADJ": "EXTRACT_TILES_LON_ADJ",
"LAT_ADJ": "EXTRACT_TILES_LAT_ADJ",

}

for key, value in change_dict.items():
    for search_dir in search_dirs:
        full_dir = os.path.join(top_level, search_dir)
        cmd = f"egrep -lRZ '{key}' {full_dir}/. | xargs -0 -l sed -i -e 's/{key}/{value}/g'"
        print(cmd)
