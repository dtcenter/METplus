import sys
import os
import time
import numpy as np
import datetime as dt
import xarray as xr
from dateutil.relativedelta import *
import function_library as fl

# =================================================================
# USER CONFIGURATION: ORIENTATION FLAGS
# =================================================================
FLIP_OBS = True      # Set to True to flip Observation data (North <-> South)
FLIP_MODELS = False   # Set to True to flip Model data (North <-> South)
# =================================================================

def main():
    start_time = time.time()
    print("-------------------------------------------------------------------")
    print("Starting NMME Pre-processing Wrapper (Manual Flip Enforced)")
    print("-------------------------------------------------------------------")

    if len(sys.argv) < 10:
        print("Usage: python wrapper_combined.py <init> <lead> <var> <clim_per> <models> <path> <time_per> <target_yr> <field>")
        sys.exit(1)

    init_month, lead_time, variable = sys.argv[1], sys.argv[2], sys.argv[3]
    clim_period, model_arg = sys.argv[4], sys.argv[5]
    base_path, time_period = sys.argv[6], sys.argv[7]
    target_year, field = sys.argv[8], sys.argv[9]

    model_input = [model_arg]
    init_time_str = target_year + init_month
    init_time = dt.datetime.strptime(init_time_str, "%Y%m")
    lead_val = int(lead_time)
    val_time = init_time + relativedelta(months=lead_val)

    # Unit Logic
    if variable in ['tmpsfc', 'tmp2m']:
        units = 'deg C'
    elif variable == 'prate':
        units = 'mm/day'
    else:
        units = 'unitless'
        if 'tercile' in field: units = 'percent'

    try:
        config = fl.setup(model_input, clim_period)

        # Parse Start Year for Obs logic
        try:
            sep = '_' if '_' in clim_period else '-'
            file_start_year = int(clim_period.split(sep)[0])
        except:
            file_start_year = 1982
            print("WARNING: Defaulting obs start year to 1982.")

        v = None
        is_observation = (model_arg == 'obs')

        # Determine if we need to flip based on the flags at the top
        should_flip = False

        # ==================================================================
        # BRANCH A: OBSERVATIONS
        # ==================================================================
        if is_observation:
            print(">>> MODE: OBSERVATION PROCESSING")
            should_flip = FLIP_OBS

            # Process Data
            verif, anom, std_anom, clim, std = fl.create_obs_anomalies(
                base_path, clim_period, variable, init_month, lead_time, time_period
            )

            target_idx = int(target_year) - file_start_year
            if target_idx < 0 or target_idx >= anom.shape[0]:
                raise IndexError(f"Target year {target_year} is outside range.")

            if field == 'raw': v = verif[target_idx, :, :]
            elif field == 'anom': v = anom[target_idx, :, :]
            elif field == 'std_anom': v = std_anom[target_idx, :, :]
            elif field == 'clim_mean': v = clim
            elif field == 'clim_std': v = std
            elif 'tercile' in field:
                obs_terciles = fl.create_obs_terciles(anom, std_anom, variable)
                if field == 'lower_tercile': v = obs_terciles[0, target_idx, :, :]
                elif field == 'middle_tercile': v = obs_terciles[1, target_idx, :, :]
                elif field == 'upper_tercile': v = obs_terciles[2, target_idx, :, :]

        # ==================================================================
        # BRANCH B: MODELS
        # ==================================================================
        else:
            print(">>> MODE: MODEL FORECAST PROCESSING")
            should_flip = FLIP_MODELS

            # Process Data
            if field == 'raw':
                v = fl.open_and_process_models(base_path, variable, time_period, init_month, lead_time, target_year, config, return_members=False)
            elif 'clim' in field:
                clim_mean, std_mean, _ = fl.calc_clim(base_path, variable, time_period, init_month, lead_time, config, return_members=False)
                v = clim_mean if field == 'clim_mean' else std_mean
            elif field in ['anom', 'std_anom']:
                clim_mean, std_mean, _ = fl.calc_clim(base_path, variable, time_period, init_month, lead_time, config, return_members=False)
                fcst_mean = fl.open_and_process_models(base_path, variable, time_period, init_month, lead_time, target_year, config, return_members=False)
                anom, std_anom = fl.calc_anom(fcst_mean, clim_mean, std_mean)
                v = anom if field == 'anom' else std_anom
            elif 'tercile' in field:
                clim_mem, std_mem, ptiles_mem = fl.calc_clim(base_path, variable, time_period, init_month, lead_time, config, return_members=True)
                fcst_mem = fl.open_and_process_models(base_path, variable, time_period, init_month, lead_time, target_year, config, return_members=True)
                probs = fl.create_terciles(fcst_mem, clim_mem, std_mem, ptiles_mem, variable)
                if field == 'lower_tercile': v = probs[0,:,:]
                elif field == 'middle_tercile': v = probs[1,:,:]
                elif field == 'upper_tercile': v = probs[2,:,:]

        # ------------------------------------------------------------------
        # FINAL PROCESSING
        # ------------------------------------------------------------------
        if v is None: raise NameError("Data variable 'v' was not assigned.")

        var = np.float64(v)
        var[var < -800] = np.nan
        var[var > 800]  = np.nan
        met_data = np.squeeze(var).copy()

        # --- FLIP LOGIC ---
        if should_flip:
            print("    ACTION: Flipping data (np.flipud) to align with MET Grid.")
            met_data = np.flipud(met_data).copy()
        else:
            print("    ACTION: Data orientation preserved (No Flip applied).")

        # Grid Definition (South-to-North)
        grid_data = {
            'name': 'Global_1x1', 'type': 'LatLon',
            'lat_ll': -90.0, 'lon_ll': 0.0, 'delta_lat': 1.0, 'delta_lon': 1.0,
            'Nlat': 181, 'Nlon': 360,
        }

        attrs = {
            'valid': str(val_time.strftime("%Y%m%d"))+'_'+str(val_time.strftime("%H%M%S")),
            'init': str(init_time.strftime("%Y%m%d"))+'_'+str(init_time.strftime("%H%M%S")),
            'lead':  lead_time,
            'name':  variable,
            'accum': '00', 'level': 'ground', 'units': units,
            'long_name': f"{variable} {field}",
            'grid': grid_data
        }

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    return met_data, attrs

print(f"PYTHON SCRIPT ARGUMENTS: {sys.argv}")
met_data, attrs = main()
