#! /usr/bin/env python3

import sys
import os
import pandas as pd

atcf_headers_trak=['BASIN','CYCLONE','STORMNAME','YYYYMMDDHH','TECHNUM/MIN','TECH','TAU','LAT','LON',
                   'VMAX','MSLP','TY','RAD','WINDCODE','RAD1','RAD2','RAD3','RAD4','POUTER',
                   'ROUTER','RMW','GUSTS','EYE','SUBREGION','MAXSEAS','INITIALS','DIR','SPEED','F1','F2',
                   'STORMNAME2','DEPTH','SEAS','SEASCODE','SEAS1','SEAS2','SEAS3','SEAS4']

num_args = len(sys.argv) - 1

if num_args < 3:
    print("ERROR: Not enough arguments")
    sys.exit(1)

def startswith_date(storm_name, search_date):
    storm_date = str(storm_name).split('_')[0].strip()
    return storm_date == search_date

input_file = sys.argv[1]
output_dir = sys.argv[2]
search_date = sys.argv[3]

adeck_filename = f'adeck.{search_date}.dat'
bdeck_filename = f'bdeck.{search_date}.dat'

adeck_path = os.path.join(output_dir, adeck_filename)
bdeck_path = os.path.join(output_dir, bdeck_filename)

pd_data = pd.read_csv(input_file, names=atcf_headers_trak)

# get adeck - all lines that match the desired date for YYYYMMDDHH (init time)
init_matches = pd_data['YYYYMMDDHH'].apply(startswith_date, args=(search_date,))
adeck = pd_data[init_matches]

# get all 0 hour data
pd_0hr_data = pd_data[pd_data['TAU'] == 0]

# get list of STORMNAMEs from adeck data
all_storms = adeck.STORMNAME.unique()

# get lines where forecast hour is 0 and STORMNAME is in ADECK list
only_adeck_storms = pd_0hr_data['STORMNAME'].isin(all_storms)
bdeck = pd_0hr_data[only_adeck_storms]

if not os.path.exists(output_dir):
    print(f"Creating output directory: {output_dir}")
    os.makedirs(output_dir)

print(f"Writing adeck to {adeck_path}")
adeck.to_csv(adeck_path, header=False, index=False)

print(f"Writing bdeck to {bdeck_path}")
bdeck.to_csv(bdeck_path, header=False, index=False)
