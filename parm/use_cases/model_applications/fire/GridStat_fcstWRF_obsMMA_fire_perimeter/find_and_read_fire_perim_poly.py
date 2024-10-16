import sys
import os
from datetime import datetime, timedelta
from glob import glob
import xml.etree.ElementTree as ET

KML_TEMPLATE = 'N328SF_%m%d%Y%H*.kml'
VALID_FORMAT = '%Y%m%d%H'

if len(sys.argv) != 4:
    print("ERROR: Must supply input directory, valid time (YYYYMMDDHH), and output directory to script")
    sys.exit(1)

# read input directory
input_dir = sys.argv[1]

# parse valid time
try:
    valid_time = datetime.strptime(sys.argv[2], VALID_FORMAT)
except ValueError:
    print(f"ERROR: Invalid format for valid time: {sys.argv[2]} (Should match {VALID_FORMAT})")
    sys.exit(1)

# get previous hour valid time
valid_one_hour_ago = valid_time - timedelta(hours=1)

# build output path
output_dir = sys.argv[3]
output_file = f"fire_perim_{valid_time.strftime('%Y%m%d_%H')}.poly"
output_path = os.path.join(output_dir, output_file)

# create output directory if it does not exist
os.makedirs(output_dir, exist_ok=True)

# find input file
input_file = None
input_glob = os.path.join(input_dir, valid_time.strftime(KML_TEMPLATE))
found_files =  glob(input_glob)

# if no files were found, search one hour ago
if not found_files:
    input_glob = os.path.join(input_dir, valid_one_hour_ago.strftime(KML_TEMPLATE))
    found_files =  glob(input_glob)

    if not found_files:
        print(f"ERROR: Could not find any files for {valid_time} in {input_dir}")
        sys.exit(1)

    # if multiple files are found for previous hour, use last file
    if len(found_files) > 1:
        print(f"WARNING: Found multiple files: {found_files}")
        print(f"Processing the LAST file")
        input_file = found_files[-1]

elif len(found_files) > 1:
    print(f"WARNING: Found multiple files: {found_files}")
    print(f"Processing the FIRST file")

if not input_file:
    input_file = found_files[0]

print(f"Parsing file: {input_file}")

tree = ET.parse(input_file)
root = tree.getroot()

search_path = './/kml:Document/kml:Placemark/kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates'
namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

coordinates = root.find(search_path, namespaces).text.split()

with open(output_path, 'w') as file_handle:
    file_handle.write(f'FIRE_PERIM\n')
    for coord in coordinates:
        lon, lat, elev = coord.split(',')
        file_handle.write(f'{lat} {lon}\n')

print(f"Wrote output to {output_path}")
