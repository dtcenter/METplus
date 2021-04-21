import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tdr_utils

if len(sys.argv) < 5:
    print("Must specify exactly one input file, variable name, mission ID (YYMMDDID), level (in km)")
    sys.exit(1)

# Read the input file as the first argument
input_file   = os.path.expandvars(sys.argv[1])
var_name     = sys.argv[2]
mission_name = sys.argv[3]
level_km     = float(sys.argv[4])

met_data, attrs = tdr_utils.main(input_file, var_name, mission_name, level_km)
