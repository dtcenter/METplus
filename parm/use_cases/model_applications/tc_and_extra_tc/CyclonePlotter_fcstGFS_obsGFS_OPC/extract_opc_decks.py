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

# function to extract start date from stormname (stormname contains date 1st observed, lat-lon 1st observed)
def startswith_date(storm_name, search_date):
    storm_date = str(storm_name).split('_')[0].strip()
    return storm_date.startswith(search_date)

input_file = sys.argv[1]
output_dir = sys.argv[2]
search_date = sys.argv[3]

# name of ADECK & BDECK files contain search date
adeck_filename = f'adeck.{search_date}.dat'
bdeck_filename = f'bdeck.{search_date}.dat'

adeck_path = os.path.join(output_dir, adeck_filename)
bdeck_path = os.path.join(output_dir, bdeck_filename)

# using pandas (pd), read input file
pd_data = pd.read_csv(input_file, names=atcf_headers_trak)

# get adeck - all lines that match the desired date for YYYYMMDDHH (init time)
init_matches = pd_data['YYYYMMDDHH'].apply(startswith_date, args=(search_date,))
adeck = pd_data[init_matches]

# get all 0 hour analyses data
pd_0hr_data = pd_data[pd_data['TAU'] == 0]

# get list of STORMNAMEs from adeck data
all_storms = adeck.STORMNAME.unique()

# get lines where forecast hour is 0 and STORMNAME is in ADECK list
only_adeck_storms = pd_0hr_data['STORMNAME'].isin(all_storms)
bdeck = pd_0hr_data[only_adeck_storms]

# create output directory if not already there
if not os.path.exists(output_dir):
    print(f"Creating output directory: {output_dir}")
    os.makedirs(output_dir)

# write ADECK
print(f"Writing adeck to {adeck_path}")
adeck.to_csv(adeck_path, header=False, index=False)

# write BDECK
print(f"Writing bdeck to {bdeck_path}")
bdeck.to_csv(bdeck_path, header=False, index=False)
