#!/usr/bin/env python

import os
from collections import defaultdict
from create_met_poly import create_poly

os.environ["VALID_BEG_IN"] = "2018041400"
os.environ["VALID_END_IN"] = "2018041500"

ens_num_list = ["01","02","03","04","05","06","07","08","09"]
varstuff={"REFC":["L0","MergedReflectivityQCComposite","Z500"],"MXUPHL":["Z2000-5000","RotationTrack60min","Z500"]}

#TODO...  Switch to Burkley's mask
polymaskfile = create_poly(os.environ.get("VALID_BEG_IN"))
os.environ["POLY_FILE"] = polymaskfile

os.environ["FCST_INPUT_DIR_IN"] = "/raid/efp/se2018/ftp/gsd"
os.environ["GEN_SEQ_IN"] = "0, 12"
os.environ["FCST_INIT_INTERVAL_IN"] = "12"
os.environ["FCST_MAX_FCST_IN"] = "36"

os.environ["OBS_INPUT_DIR_IN"] = "/raid/roberts/data/obs/mrms"
os.environ["OBS_INPUT_TEMPLATE_IN"] = "{valid?fmt=%Y}/{valid?fmt=%m}/{valid?fmt=%d}/mrms.MergedReflectivityQCComposite.{valid?fmt=%Y%m%d}_{valid?fmt=%H%M%S}.grib2"
os.environ["OB_TYPE_IN"] = "MRMS"
os.environ["OBS_EXACT_VALID_TIME_IN"] = "false"

#Loop through members, variables below need to change
for ens_num in ens_num_list:
    os.environ["FCST_INPUT_TEMPLATE_IN"] = "{init?fmt=%Y%m%d%H}/hrrre"+ens_num+"_{init?fmt=%Y%m%d%H}f{lead?fmt=%HHH}.grib2"
    os.environ["MODEL_TYPE_IN"] = "HRRRe"+ens_num

    for vv in varstuff:
        os.environ["FCST_VAR_IN"] = vv
        os.environ["FCST_LVL_IN"] = varstuff[vv][0]

        os.environ["OBS_VAR_IN"] = varstuff[vv][1]
        os.environ["OBS_LVL_IN"] = varstuff[vv][2]

        os.environ["OUT_DIR_IN"] = "/raid/efp/se2018/ftp/dtc/HRRRe"+ens_num
             
        os.system('./master_metplus.py -c ../parm/use_cases/hwt/grid2grid_hwt_env.conf')
