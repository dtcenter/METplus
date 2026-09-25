import sys
import time
import datetime as dt

import numpy as np
from dateutil.relativedelta import relativedelta

import function_library_withDetrend as fl


# =================================================================
# USER CONFIGURATION: ORIENTATION & OPTIONAL PROCESSING FLAGS
# =================================================================
FLIP_OBS = True
FLIP_MODELS = False
DEFAULT_DETREND = True
DEFAULT_SMART_MASK = True
# =================================================================


def _parse_bool_arg(value, arg_name):
    true_values = {'1', 'true', 't', 'yes', 'y', 'on'}
    false_values = {'0', 'false', 'f', 'no', 'n', 'off'}
    normalized = str(value).strip().lower()

    if normalized in true_values:
        return True
    if normalized in false_values:
        return False

    raise ValueError(f"Invalid boolean value for {arg_name}: '{value}'")


def _get_optional_flags(argv):
    detrend_data = _parse_bool_arg(argv[10], 'detrend') if len(argv) > 10 else DEFAULT_DETREND
    smart_mask = _parse_bool_arg(argv[11], 'smart_mask') if len(argv) > 11 else DEFAULT_SMART_MASK
    return detrend_data, smart_mask


def _get_units(variable, field):
    if variable in ['tmpsfc', 'tmp2m']:
        return 'deg C'
    if variable == 'prate':
        return 'mm/day'
    if 'tercile' in field:
        return 'percent'
    return 'unitless'


def _get_target_index(target_year, available_years):
    years = np.asarray(available_years).astype(int)
    matches = np.nonzero(years == int(target_year))[0]

    if matches.size == 0:
        raise IndexError(f"Target year {target_year} is outside available years: {years.tolist()}")

    return int(matches[0])


def main():
    start_time = time.time()
    print("-------------------------------------------------------------------")
    print("Starting NMME Pre-processing Wrapper (Manual Flip Enforced)")
    print("-------------------------------------------------------------------")

    if len(sys.argv) < 10:
        print("Usage: python wrapper_combined.py <init> <lead> <var> <clim_per> <models> <path> <time_per> <target_yr> <field> [detrend] [smart_mask]")
        sys.exit(1)

    init_month, lead_time, variable = sys.argv[1], sys.argv[2], sys.argv[3]
    clim_period, model_arg = sys.argv[4], sys.argv[5]
    base_path, time_period = sys.argv[6], sys.argv[7]
    target_year, field = sys.argv[8], sys.argv[9]
    detrend_data, smart_mask = _get_optional_flags(sys.argv)

    model_input = [model_arg]
    init_time_str = target_year + init_month
    init_time = dt.datetime.strptime(init_time_str, "%Y%m")
    val_time = init_time + relativedelta(months=int(lead_time))
    units = _get_units(variable, field)

    print(f"Runtime options: detrend={detrend_data}, smart_mask={smart_mask}")

    try:
        config = fl.setup(model_input, clim_period)

        v = None
        obs_mask = None
        is_observation = (model_arg == 'obs')
        should_flip = False

        if is_observation:
            print(">>> MODE: OBSERVATION PROCESSING")
            should_flip = FLIP_OBS

            verif, anom, std_anom, clim, std, obs_years = fl.create_obs_anomalies(
                base_path, clim_period, variable, init_month, lead_time, time_period,
                detrend=detrend_data
            )

            target_idx = _get_target_index(target_year, obs_years)

            if smart_mask and 'tercile' in field:
                obs_mask = np.isnan(anom[target_idx, :, :])

            if field == 'raw':
                v = verif[target_idx, :, :]
            elif field == 'anom':
                v = anom[target_idx, :, :]
            elif field == 'std_anom':
                v = std_anom[target_idx, :, :]
            elif field == 'clim_mean':
                v = clim
            elif field == 'clim_std':
                v = std
            elif 'tercile' in field:
                obs_terciles = fl.create_obs_terciles(anom, std_anom, variable)
                if field == 'lower_tercile':
                    v = obs_terciles[0, target_idx, :, :]
                elif field == 'middle_tercile':
                    v = obs_terciles[1, target_idx, :, :]
                elif field == 'upper_tercile':
                    v = obs_terciles[2, target_idx, :, :]

        else:
            print(">>> MODE: MODEL FORECAST PROCESSING")
            should_flip = FLIP_MODELS

            if field == 'raw':
                v = fl.open_and_process_models(
                    base_path, variable, time_period, init_month, lead_time,
                    target_year, config, return_members=False
                )
                if detrend_data:
                    trend_val = fl.get_trend_value(base_path, variable, time_period, init_month, lead_time, config, target_year)
                    v = v - trend_val
                    print(f"    Applied trend removal to raw forecast for year {target_year}")

            elif 'clim' in field:
                clim_mean, std_mean, _ = fl.calc_clim(
                    base_path, variable, time_period, init_month, lead_time,
                    config, return_members=False, detrend=detrend_data
                )
                v = clim_mean if field == 'clim_mean' else std_mean

            elif field in ['anom', 'std_anom']:
                clim_mean, std_mean, _ = fl.calc_clim(
                    base_path, variable, time_period, init_month, lead_time,
                    config, return_members=False, detrend=detrend_data
                )
                fcst_mean = fl.open_and_process_models(
                    base_path, variable, time_period, init_month, lead_time,
                    target_year, config, return_members=False
                )

                if detrend_data:
                    trend_val = fl.get_trend_value(base_path, variable, time_period, init_month, lead_time, config, target_year)
                    fcst_mean = fcst_mean - trend_val
                    print(f"    Applied trend removal to forecast for year {target_year}")

                anom, std_anom = fl.calc_anom(fcst_mean, clim_mean, std_mean)
                v = anom if field == 'anom' else std_anom

            elif 'tercile' in field:
                clim_mem, std_mem, ptiles_mem = fl.calc_clim(
                    base_path, variable, time_period, init_month, lead_time,
                    config, return_members=True, detrend=detrend_data
                )
                fcst_mem = fl.open_and_process_models(
                    base_path, variable, time_period, init_month, lead_time,
                    target_year, config, return_members=True
                )

                if detrend_data:
                    trend_val = fl.get_trend_value(base_path, variable, time_period, init_month, lead_time, config, target_year)
                    fcst_mem = fcst_mem - trend_val
                    print(f"    Applied trend removal to forecast members for year {target_year}")

                probs = fl.create_terciles(fcst_mem, clim_mem, std_mem, ptiles_mem, variable)
                if field == 'lower_tercile':
                    v = probs[0, :, :]
                elif field == 'middle_tercile':
                    v = probs[1, :, :]
                elif field == 'upper_tercile':
                    v = probs[2, :, :]

        if v is None:
            raise NameError("Data variable 'v' was not assigned.")

        var = np.asarray(v, dtype=np.float64)
        var[var < -800] = np.nan
        var[var > 800] = np.nan

        if smart_mask and 'tercile' in field:
            var = np.nan_to_num(var, nan=0.0)

        if smart_mask and is_observation and obs_mask is not None and var.shape == obs_mask.shape:
            var[obs_mask] = np.nan
            print("    ACTION: Re-applied ocean mask to Observation data.")

        met_data = np.squeeze(var).copy()

        if should_flip:
            print("    ACTION: Flipping data (np.flipud) to align with MET Grid.")
            met_data = np.flipud(met_data).copy()
        else:
            print("    ACTION: Data orientation preserved (No Flip applied).")

        grid_data = {
            'name': 'Global_1x1', 'type': 'LatLon',
            'lat_ll': -90.0, 'lon_ll': 0.0, 'delta_lat': 1.0, 'delta_lon': 1.0,
            'Nlat': 181, 'Nlon': 360,
        }

        attrs = {
            'valid': str(val_time.strftime("%Y%m%d")) + '_' + str(val_time.strftime("%H%M%S")),
            'init': str(init_time.strftime("%Y%m%d")) + '_' + str(init_time.strftime("%H%M%S")),
            'lead': lead_time,
            'name': variable,
            'accum': '00', 'level': 'ground', 'units': units,
            'long_name': f"{variable} {field}",
            'grid': grid_data
        }

    except Exception as exc:
        print(f"ERROR: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    return met_data, attrs


print(f"PYTHON SCRIPT ARGUMENTS: {sys.argv}")
met_data, attrs = main()
