import sys
import time
import datetime as dt
from types import SimpleNamespace

import numpy as np
from dateutil.relativedelta import relativedelta

import function_library as fl


# =================================================================
# USER CONFIGURATION: ORIENTATION & OPTIONAL PROCESSING FLAGS
# =================================================================
FLIP_OBS = True
FLIP_MODELS = False
DEFAULT_DETREND = False
DEFAULT_SMART_MASK = False
# =================================================================

TERCILE_INDEX = {'lower_tercile': 0, 'middle_tercile': 1, 'upper_tercile': 2}


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


def _get_tercile(data, field):
    """Return the slice of data along the first axis that matches the tercile field, or None."""
    idx = TERCILE_INDEX.get(field)
    return None if idx is None else data[idx]


def _get_obs_field(opts):
    """
    Compute the requested observation field.
    Returns the data and an optional mask of missing obs points to re-apply later.
    """
    verif, anom, std_anom, clim, std, obs_years = fl.create_obs_anomalies(
        opts.base_path, opts.clim_period, opts.variable, opts.init_month,
        opts.lead_time, opts.time_period, detrend=opts.detrend
    )

    target_idx = _get_target_index(opts.target_year, obs_years)
    field = opts.field

    obs_mask = None
    if opts.smart_mask and 'tercile' in field:
        obs_mask = np.isnan(anom[target_idx, :, :])

    simple_fields = {
        'raw': lambda: verif[target_idx, :, :],
        'anom': lambda: anom[target_idx, :, :],
        'std_anom': lambda: std_anom[target_idx, :, :],
        'clim_mean': lambda: clim,
        'clim_std': lambda: std,
    }
    if field in simple_fields:
        return simple_fields[field](), obs_mask

    if 'tercile' in field:
        obs_terciles = fl.create_obs_terciles(anom, std_anom, opts.variable)
        return _get_tercile(obs_terciles[:, target_idx, :, :], field), obs_mask

    return None, obs_mask


def _open_fcst(opts, config, return_members, label):
    """Read target year forecast and remove trend if requested."""
    fcst = fl.open_and_process_models(
        opts.base_path, opts.variable, opts.time_period, opts.init_month,
        opts.lead_time, opts.target_year, config, return_members=return_members
    )
    if opts.detrend:
        trend_val = fl.get_trend_value(
            opts.base_path, opts.variable, opts.time_period, opts.init_month,
            opts.lead_time, config, opts.target_year
        )
        fcst = fcst - trend_val
        print(f"    Applied trend removal to {label} for year {opts.target_year}")
    return fcst


def _calc_clim(opts, config, return_members):
    return fl.calc_clim(
        opts.base_path, opts.variable, opts.time_period, opts.init_month,
        opts.lead_time, config, return_members=return_members,
        detrend=opts.detrend
    )


def _get_model_field(opts, config):
    """Compute the requested model forecast field."""
    field = opts.field

    if field == 'raw':
        return _open_fcst(opts, config, False, 'raw forecast')

    if 'clim' in field:
        clim_mean, std_mean, _ = _calc_clim(opts, config, return_members=False)
        return clim_mean if field == 'clim_mean' else std_mean

    if field in ['anom', 'std_anom']:
        clim_mean, std_mean, _ = _calc_clim(opts, config, return_members=False)
        fcst_mean = _open_fcst(opts, config, False, 'forecast')
        anom, std_anom = fl.calc_anom(fcst_mean, clim_mean, std_mean)
        return anom if field == 'anom' else std_anom

    if 'tercile' in field:
        clim_mem, std_mem, ptiles_mem = _calc_clim(opts, config, return_members=True)
        fcst_mem = _open_fcst(opts, config, True, 'forecast members')
        probs = fl.create_terciles(fcst_mem, clim_mem, std_mem, ptiles_mem, opts.variable)
        return _get_tercile(probs, field)

    return None


def _prepare_met_data(v, opts, is_observation, obs_mask, should_flip):
    """Mask out-of-range values, apply smart mask, and orient data for MET."""
    var = np.asarray(v, dtype=np.float64)
    var[var < -800] = np.nan
    var[var > 800] = np.nan

    if opts.smart_mask and 'tercile' in opts.field:
        var = np.nan_to_num(var, nan=0.0)

    if opts.smart_mask and is_observation and obs_mask is not None and var.shape == obs_mask.shape:
        var[obs_mask] = np.nan
        print("    ACTION: Re-applied ocean mask to Observation data.")

    met_data = np.squeeze(var).copy()

    if should_flip:
        print("    ACTION: Flipping data (np.flipud) to align with MET Grid.")
        return np.flipud(met_data).copy()

    print("    ACTION: Data orientation preserved (No Flip applied).")
    return met_data


def _build_attrs(opts, init_time, val_time):
    grid_data = {
        'name': 'Global_1x1', 'type': 'LatLon',
        'lat_ll': -90.0, 'lon_ll': 0.0, 'delta_lat': 1.0, 'delta_lon': 1.0,
        'Nlat': 181, 'Nlon': 360,
    }

    return {
        'valid': val_time.strftime("%Y%m%d_%H%M%S"),
        'init': init_time.strftime("%Y%m%d_%H%M%S"),
        'lead': opts.lead_time,
        'name': opts.variable,
        'accum': '00', 'level': 'ground', 'units': _get_units(opts.variable, opts.field),
        'long_name': f"{opts.variable} {opts.field}",
        'grid': grid_data
    }


def _parse_args(argv):
    if len(argv) < 10:
        print("Usage: python wrapper_combined.py <init> <lead> <var> <clim_per> <models> <path> <time_per> <target_yr> <field> [detrend] [smart_mask]")
        sys.exit(1)

    detrend_data, smart_mask = _get_optional_flags(argv)
    return SimpleNamespace(
        init_month=argv[1], lead_time=argv[2], variable=argv[3],
        clim_period=argv[4], model_arg=argv[5],
        base_path=argv[6], time_period=argv[7],
        target_year=argv[8], field=argv[9],
        detrend=detrend_data, smart_mask=smart_mask,
    )


def _process(opts):
    config = fl.setup([opts.model_arg], opts.clim_period)

    is_observation = (opts.model_arg == 'obs')
    obs_mask = None
    if is_observation:
        print(">>> MODE: OBSERVATION PROCESSING")
        should_flip = FLIP_OBS
        v, obs_mask = _get_obs_field(opts)
    else:
        print(">>> MODE: MODEL FORECAST PROCESSING")
        should_flip = FLIP_MODELS
        v = _get_model_field(opts, config)

    if v is None:
        raise NameError("Data variable 'v' was not assigned.")

    return _prepare_met_data(v, opts, is_observation, obs_mask, should_flip)


def main():
    start_time = time.time()
    print("-------------------------------------------------------------------")
    print("Starting NMME Pre-processing Wrapper (Manual Flip Enforced)")
    print("-------------------------------------------------------------------")

    opts = _parse_args(sys.argv)

    init_time = dt.datetime.strptime(opts.target_year + opts.init_month, "%Y%m")
    val_time = init_time + relativedelta(months=int(opts.lead_time))

    print(f"Runtime options: detrend={opts.detrend}, smart_mask={opts.smart_mask}")

    try:
        met_data = _process(opts)
        attrs = _build_attrs(opts, init_time, val_time)
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
