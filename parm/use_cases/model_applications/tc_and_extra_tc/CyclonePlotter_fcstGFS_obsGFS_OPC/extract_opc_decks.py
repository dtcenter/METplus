#! /usr/bin/env python3

#
#  program extrack_opc_decks.py
#
#  reads in EMC 2020 cyclone data 
#  takes 3 command line arguments
#  1) input file (full path, eg, "/d2/projects/d2/projects/extra-tc_verif/gpfs/dell1/nco/ops/com/gentracks/prod/gentracks/{init?fmt=%Y}/trak.gfso.atcf_gen.glbl.{init?fmt=%Y}"
#  2) output directory (eg "{OUTPUT_BASE}/decks")
#  3) init time (YYYYMMDDHH)
#
#  reads all data in input file, creates ADECK using all points valid at init time (key 'YYYYMMDDHH', creates BDECK
#    using key ('STORMNAME') for all storms in ADECK where forecast key ('TAU') = '000' or 0 hrs
#  writes a single adeck and a single bdeck file containing all storms
#
#  further processed by TC_Pairs (extra-tropical) and CyclonePlotter in single use-case wrapper CyclonePlotter_fcst_GFS_obsGFS_OPC
#
#  written February 2021 by George McCabe (mccabe@ucar.edu)
#

import sys
import os
import pandas as pd

# column names/dictionary keys for the trak.data file
atcf_headers_trak=['BASIN','CYCLONE','STORMNAME','YYYYMMDDHH','TECHNUM/MIN','TECH','TAU','LAT','LON',
                   'VMAX','MSLP','TY','RAD','WINDCODE','RAD1','RAD2','RAD3','RAD4','POUTER',
                   'ROUTER','RMW','GUSTS','EYE','SUBREGION','MAXSEAS','INITIALS','DIR','SPEED','F1','F2',
                   'STORMNAME2','DEPTH','SEAS','SEASCODE','SEAS1','SEAS2','SEAS3','SEAS4']

# needs exactly 3 arguments (see above)
num_args = len(sys.argv) - 1

if num_args < 3:
    print("ERROR: Not enough arguments")
    sys.exit(1)
debug = 'debug' in sys.argv
# function to compare storm warning time to search time
def is_equal(column_val, search_string):
    return str(column_val).strip() == search_string

input_file = sys.argv[1]
output_dir = sys.argv[2]
search_date = sys.argv[3]

if debug:
    print(f"Running {__file__}\nSearch date: {search_date}")

# get 2 digit year to use in CYCLONE column substitute value
search_year = search_date[2:4]

# string to use in output file names for filtered adeck and bdeck files
file_prefix = f'deck.{search_date}.'

# an intermediate directory path for the separate files
adeck_base = os.path.join(output_dir, "adeck")
#bdeck_base = os.path.join(output_dir, "bdeck")

# create output directories if not already there
if not os.path.exists(adeck_base):
    print(f"Creating output directory: {adeck_base}")
    os.makedirs(adeck_base)

#if not os.path.exists(bdeck_base):
#    print(f"Creating output directory: {bdeck_base}")
#    os.makedirs(bdeck_base)

# using pandas (pd), read input file
print(f"Reading input file: {input_file}")
pd_data = pd.read_csv(input_file, names=atcf_headers_trak)

print(f"Filtering data...")

# get all 0 hour analyses data
print(f"Filtering data 0 (hr) in TAU (forecast hour) column for bdeck")
pd_0hr_data = pd_data[pd_data['TAU'] == 0]

# get adeck - all lines that match the desired date for YYYYMMDDHH (init time)
print(f"Filtering data with {search_date} in YYYYMMDDHH column for adeck")
init_matches = pd_data['YYYYMMDDHH'].apply(is_equal,
                                           args=(search_date,))
adeck = pd_data[init_matches]

# get list of STORMNAMEs from adeck data
all_storms = adeck.STORMNAME.unique()

# initialize counter to use to set output filenames with "cyclone" number
# to keep storms in separate files
index = 0

# loop over storms
for storm_name in all_storms:
    index_pad = str(index).zfill(4)

    # remove whitespace at beginning of storm name
    storm_name = storm_name.strip()

    # get 0hr data for given storm to use as bdeck
    storm_b_match = pd_0hr_data['STORMNAME'].apply(is_equal,
                                                   args=(storm_name,))
    storm_bdeck = pd_0hr_data[storm_b_match]
    if debug:
        print(f"Processing storm: {storm_name}")
    wrote_a = wrote_b = False

    #Logic for writing out Analysis files. Currently commented out,
    #but left in for possible future use
    if not storm_bdeck.empty:
    #    bdeck_filename = f'b{file_prefix}{index_pad}.dat'
    #    bdeck_path = os.path.join(bdeck_base, bdeck_filename)

    #    print(f"Writing bdeck to {bdeck_path}")
    #    storm_bdeck.to_csv(bdeck_path, header=False, index=False)
        wrote_b = True
    #else:
    #    print(f"BDECK for {storm_name} is empty. Skipping")

    # filter out adeck data for given storm
    storm_a_match = adeck['STORMNAME'].apply(is_equal,
                                             args=(storm_name,))
    storm_adeck = adeck[storm_a_match]

    if not storm_adeck.empty:
        adeck_filename = f'a{file_prefix}{index_pad}.dat'
        adeck_path = os.path.join(adeck_base, adeck_filename)
        if debug:
            print(f"Writing adeck to {adeck_path}")
        storm_adeck.to_csv(adeck_path, header=False, index=False)
        wrote_a = True
    else:
        if debug:
            print(f"ADECK for {storm_name} is empty. Skipping")

    if wrote_a or wrote_b:
        index += 1

print("Finished processing all storms")
