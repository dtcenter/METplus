#!/usr/bin/env python

import os

os.environ["FCST_INPUT_DIR_IN"] = "/raid/efp/se2018/ftp/gsd"
os.environ["OBS_INPUT_DIR_IN"] = "/raid/efp/se2018/ftp/gsd"

os.environ["FCST_INPUT_TEMPLATE_IN"] = "{init?fmt=%Y%m%d%H}/hrrre01_{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.grib2"
os.environ["OBS_INPUT_TEMPLATE_IN"] = "{valid?fmt=%Y%m%d%H}/hrrre01_{valid?fmt=%Y%m%d%H}f000.grib2"

os.environ["MODEL_TYPE_IN"] = "HRRRe01"
os.environ["OB_TYPE_IN"] = "MRMS"

os.environ["FCST_VAR_IN"] = "REFC"
os.environ["FCST_LVL_IN"] = "L0"

os.environ["FCST_MAX_FCST_IN"] = "48"

os.environ["OUT_DIR_IN"] = "/path/to/username/metout"

os.system('./master_metplus.py -c ../parm/use_cases/hwt/grid2grid_hwt_env.conf')
