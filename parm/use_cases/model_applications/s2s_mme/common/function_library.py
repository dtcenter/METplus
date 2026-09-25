import os

import numpy as np
import xarray as xr

GEM5_2_NEMO = 'GEM5.2_NEMO'


# --------------------------------------------------------------------------------------------------
# 1. Define nMembers in each model
MODEL_SPECS = {
    'CFSv2': 24, 'NCAR_CCSM4': 10, 'GEM5_NEMO': 10, 'NASA_GEOS5v2': 4,
    'CanCM4i': 10, 'GFDL_SPEAR': 15, GEM5_2_NEMO: 20, 'CanESM5': 20,
    'SFS_Baseline': 9, 'NCAR_CESM1': 10, 'obs': 1
}

# 2. Define Model Groups
MODEL_GROUPS = {
    'NMME': ['CFSv2', 'NCAR_CCSM4', GEM5_2_NEMO, 'NASA_GEOS5v2', 'CanESM5', 'GFDL_SPEAR'],
    'miniNMME': ['CFSv2', 'NCAR_CCSM4', 'GFDL_SPEAR'],
    'miniNMME_addSFS': ['CFSv2', 'NCAR_CCSM4', 'GFDL_SPEAR', 'SFS_Baseline'],
    'miniNMME_replaceCFSwSFS': ['SFS_Baseline', 'NCAR_CCSM4', 'GFDL_SPEAR'],
    'NMMEwithCFS': ['CFSv2', 'NCAR_CCSM4', 'NCAR_CESM1', 'GFDL_SPEAR', GEM5_2_NEMO, 'CanESM5', 'NASA_GEOS5v2'],
    'NMMEwithSFS': ['SFS_Baseline', 'NCAR_CCSM4', 'NCAR_CESM1', 'GFDL_SPEAR', GEM5_2_NEMO, 'CanESM5', 'NASA_GEOS5v2'],
    'CFSandSFS': ['SFS_Baseline', 'CFSv2'],
}
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def detrend_grid(data_array, years):
    """
    Linearly detrends data at every grid point over the time dimension (axis 0).
    data_array: Shape (Time, Lat, Lon)
    years: 1D array of years corresponding to Time axis.
    Returns:
        detrended_data: Shape (Time, Lat, Lon) with trend removed (residuals + mean)
        slope_grid: Shape (Lat, Lon) - Slope per year
        intercept_grid: Shape (Lat, Lon)
    """
    print("    Calculating linear trend for removal...")
    n_t, n_lat, n_lon = data_array.shape

    if n_t < 2:
        print("    WARNING: Need at least two time steps to detrend. Returning original data.")
        nan_grid = np.full((n_lat, n_lon), np.nan)
        return data_array.copy(), nan_grid, nan_grid.copy()

    y_reshaped = data_array.reshape(n_t, -1)
    valid_mask = np.isfinite(y_reshaped).all(axis=0)

    detrended_flat = y_reshaped.copy()
    slope_flat = np.full(y_reshaped.shape[1], np.nan)
    intercept_flat = np.full(y_reshaped.shape[1], np.nan)

    if np.any(valid_mask):
        x = np.asarray(years, dtype=np.float64)
        y_valid = y_reshaped[:, valid_mask]

        coeffs = np.polyfit(x, y_valid, 1)
        slopes = coeffs[0, :]
        intercepts = coeffs[1, :]

        trend = np.outer(x, slopes) + intercepts
        means = np.mean(y_valid, axis=0)
        detrended_valid = y_valid - trend + means

        detrended_flat[:, valid_mask] = detrended_valid
        slope_flat[valid_mask] = slopes
        intercept_flat[valid_mask] = intercepts

    return (
        detrended_flat.reshape(n_t, n_lat, n_lon),
        slope_flat.reshape(n_lat, n_lon),
        intercept_flat.reshape(n_lat, n_lon),
    )
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def setup(model_input_list, clim_per_str):
    print('Running setup for model data choices and climate period...')

    if len(model_input_list) == 1 and model_input_list[0] in MODEL_GROUPS:
        selected_models = MODEL_GROUPS[model_input_list[0]]
    else:
        selected_models = model_input_list

    final_model_dict = {}
    for m in selected_models:
        if m in MODEL_SPECS:
            final_model_dict[m] = MODEL_SPECS[m]
        else:
            raise ValueError(f"Model '{m}' not supported.")

    n_ens = sum(final_model_dict.values())

    try:
        start_year, end_year = map(int, clim_per_str.split('_'))
        years = np.arange(start_year, end_year + 1, 1)
    except ValueError as exc:
        raise ValueError(f"Climatology format '{clim_per_str}' is invalid.") from exc

    print(f"    Climatology Period: {clim_per_str} (Years: {len(years)})")
    print(f"    Total Ensemble Members (nEns): {n_ens}")

    return {
        'model_dict': final_model_dict,
        'years': years,
        'model_out': list(final_model_dict.keys()),
        'climo': clim_per_str,
        'mems_total': n_ens
    }
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def open_and_process_models(base_path, variable, time_period,
                            init_month, lead_time, init_year,
                            config, return_members=False):

    mode_str = "Full Ensemble" if return_members else "Ensemble Mean"
    print(f"Opening target data for {variable} ({mode_str})...")

    model_order = config['model_out']
    ds_list = []
    grid_shape = (181, 360)

    for model_name in model_order:
        n_members = config['model_dict'][model_name]
        file_name = f"{model_name}.{variable}.{init_year}{init_month}.fcst.nc"
        full_path = os.path.join(base_path, model_name, file_name)

        try:
            if not os.path.exists(full_path):
                print(f"    WARNING: File missing: {full_path}")
                continue

            ds = xr.open_dataset(full_path, decode_times=False)
            if 'fcst' not in ds:
                print(f"    WARNING: 'fcst' variable missing in {full_path}")
                continue

            ds_subset = ds.isel(ensmem=slice(0, n_members))
            ds_list.append(ds_subset)

        except Exception as exc:
            print(f"    WARNING: Error reading {full_path}: {exc}")
            continue

    if not ds_list:
        print(f"    WARNING: No valid data found for {init_year}. Returning -9999 to MET.")
        return np.full(grid_shape, -9999.0)

    ds_combined = xr.concat(ds_list, dim='ensmem')
    fcst_data = ds_combined['fcst'].values
    fcst_data = np.where(np.abs(fcst_data) < 9999, fcst_data, np.nan)

    if np.isnan(fcst_data).all():
        print(f"    WARNING: Data for {init_year} is all-NaN. Returning -9999 to MET.")
        return np.full(grid_shape, -9999.0)

    lead_int = int(lead_time)

    try:
        if time_period == 'monthly':
            fcst_proc = fcst_data[:, lead_int, :, :]
        elif time_period == 'seasonal':
            leads_to_avg = slice(lead_int - 1, lead_int + 2)
            fcst_subset = fcst_data[:, leads_to_avg, :, :]
            fcst_proc = np.nanmean(fcst_subset, axis=1)
        else:
            raise ValueError(f"Unsupported time period: {time_period}")
    except IndexError:
        print(f"    WARNING: Lead time {lead_int} out of bounds for {init_year}. Returning NaNs.")
        return np.full(grid_shape, np.nan)

    if return_members:
        fcst = fcst_proc
    else:
        fcst = np.nanmean(fcst_proc, axis=0)

    if variable == 'prate':
        fcst = fcst * 86400
    elif variable in ['tmp2m', 'tmpsfc']:
        fcst = fcst - 273.15
        if variable == 'tmpsfc':
            fcst = np.where(fcst > 600, np.nan, fcst)

    print(f"    Shape of fcst array: {fcst.shape}")
    return fcst
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def _load_history_stack(base_path, variable, time_period, init_month, lead_time, config):
    """
    Helper to avoid duplication in climatology and detrending logic.
    Returns array of shape: (Years, Members, Lat, Lon)
    """
    clim_years = config['years']
    model_order = config['model_out']
    lead_int = int(lead_time)
    history_stack = []

    for year in clim_years:
        year_str = str(year)
        current_year_models = []

        for model_name in model_order:
            n_members = config['model_dict'][model_name]
            file_name = f"{model_name}.{variable}.{year_str}{init_month}.fcst.nc"
            full_path = os.path.join(base_path, model_name, file_name)

            if not os.path.exists(full_path):
                print(f"    WARNING: File missing for year {year_str}: {full_path}")
                continue

            try:
                ds = xr.open_dataset(full_path, decode_times=False)
                ds_subset = ds.isel(ensmem=slice(0, n_members))
                current_year_models.append(ds_subset)
            except Exception as exc:
                print(f"    WARNING: Error reading {full_path}: {exc}")
                continue

        if not current_year_models:
            print(f"    WARNING: No valid model data found for year {year_str}. Skipping.")
            continue

        try:
            ds_combined = xr.concat(current_year_models, dim='ensmem')
            fcst_data = ds_combined['fcst'].values
            fcst_data = np.where(np.abs(fcst_data) < 9999, fcst_data, np.nan)
        except Exception as exc:
            print(f"    WARNING: Error combining data for {year_str}: {exc}. Skipping.")
            continue

        if np.isnan(fcst_data).all():
            print(f"    WARNING: Data for {year_str} is entirely NaN. Skipping.")
            continue

        if time_period == 'monthly':
            data_proc = fcst_data[:, lead_int, :, :]
        elif time_period == 'seasonal':
            leads_to_avg = slice(lead_int - 1, lead_int + 2)
            fcst_subset = fcst_data[:, leads_to_avg, :, :]
            data_proc = np.nanmean(fcst_subset, axis=1)
        else:
            raise ValueError(f"Unsupported time period: {time_period}")

        history_stack.append(data_proc)

    if not history_stack:
        raise RuntimeError("CRITICAL ERROR: No valid years found for climatology.")

    full_hist_array = np.stack(history_stack, axis=0)

    if variable == 'prate':
        full_hist_array = full_hist_array * 86400
    elif variable in ['tmp2m', 'tmpsfc']:
        full_hist_array = full_hist_array - 273.15
        if variable == 'tmpsfc':
            full_hist_array = np.where(full_hist_array > 600, np.nan, full_hist_array)

    return full_hist_array
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def get_trend_value(base_path, variable, time_period, init_month, lead_time, config, target_year):
    """
    Get the trend adjustment to remove from a target year forecast.
    Returns a grid of values to subtract from the raw forecast.
    """
    clim_years = config['years']
    hist_array = _load_history_stack(base_path, variable, time_period, init_month, lead_time, config)
    hist_ens_mean = np.nanmean(hist_array, axis=1)

    _, slope, intercept = detrend_grid(hist_ens_mean, clim_years)
    hist_mean = np.nanmean(hist_ens_mean, axis=0)
    trend_val = (slope * int(target_year) + intercept) - hist_mean

    return trend_val
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def calc_clim(base_path, variable, time_period,
              init_month, lead_time, config,
              return_members=False, detrend=False):

    mode_str = "Member-Wise" if return_members else "Ensemble Mean"
    print(f"Calculating {mode_str} Climatology for {variable} (Detrend={detrend})...")

    clim_years = config['years']
    full_hist_array = _load_history_stack(base_path, variable, time_period, init_month, lead_time, config)

    if detrend:
        ens_mean_hist = np.nanmean(full_hist_array, axis=1)
        detrended_mean, _, _ = detrend_grid(ens_mean_hist, clim_years)
        adjustment = ens_mean_hist - detrended_mean
        adjustment = adjustment[:, np.newaxis, :, :]
        full_hist_array = full_hist_array - adjustment

    if return_members:
        clim = np.nanmean(full_hist_array, axis=0)
        stddev = np.nanstd(full_hist_array, axis=0)
        anoms = full_hist_array - clim
        ptiles = np.nanpercentile(anoms, [33, 66], axis=0)
    else:
        yearly_means = np.nanmean(full_hist_array, axis=1)
        clim = np.nanmean(yearly_means, axis=0)
        stddev = np.nanstd(yearly_means, axis=0)
        anoms = yearly_means - clim
        ptiles = np.nanpercentile(anoms, [33, 66], axis=0)

    print(f"    Climatology successfully calculated using {full_hist_array.shape[0]} valid years.")
    print(f"    clim shape: {clim.shape}")
    return clim, stddev, ptiles
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def calc_anom(fcst, clim, stddev):
    print('Calculating anomalies...')
    anom = fcst - clim
    with np.errstate(divide='ignore', invalid='ignore'):
        std_anom = anom / stddev
    std_anom = np.where(np.isfinite(std_anom), std_anom, np.nan)
    print(f'    anom Shape: {anom.shape}')
    return anom, std_anom
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def create_terciles(fcst, clim, stddev, ptiles, variable):
    print(f'Creating tercile probabilities for {variable} (Member-Wise)...')
    anoms = fcst - clim
    with np.errstate(divide='ignore', invalid='ignore'):
        std_anoms = anoms / stddev
    std_anoms = np.where(np.isfinite(std_anoms), std_anoms, np.nan)

    if variable in ['tmp2m', 'tmpsfc']:
        thresh_low, thresh_high = -0.43, 0.43
        field = std_anoms
    else:
        thresh_low, thresh_high = ptiles[0, :, :, :], ptiles[1, :, :, :]
        field = anoms

    ut_ones = np.where(field > thresh_high, 1, 0)
    lt_ones = np.where(field < thresh_low, 1, 0)
    mt_ones = np.where((field >= thresh_low) & (field <= thresh_high), 1, 0)

    total_members = field.shape[0]
    ut_prob = np.nansum(ut_ones, axis=0) / total_members
    lt_prob = np.nansum(lt_ones, axis=0) / total_members
    mt_prob = np.nansum(mt_ones, axis=0) / total_members

    terciles = np.array([lt_prob, mt_prob, ut_prob])
    print(f'    terciles shape: {terciles.shape}')
    return terciles
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def _parse_climo_start_year(clim_period):
    for separator in ('_', '-'):
        if separator in clim_period:
            return int(clim_period.split(separator)[0])
    raise ValueError(f"Unable to parse climatology period start year from '{clim_period}'.")
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def _get_obs_years(ds, target_month_idx):
    for coord_name in ('time', 'T'):
        if coord_name in ds.coords and hasattr(ds[coord_name], 'dt'):
            return np.asarray(ds[coord_name].dt.year.values)[target_month_idx::12].astype(int)
    return None
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def create_obs_anomalies(base_path, clim_period, variable, init_month, lead_time, time_period, detrend=False):
    init = int(init_month) - 1
    lead = int(lead_time)
    target_month_idx = (init + lead) % 12
    clim_str = clim_period.replace('_', '-')

    file_map = {
        'tmp2m': f"ghcn_cams.1x1.{clim_str}.mon.nc",
        'prate': f"cmap.1x1.{clim_str}.mon.nc",
        'tmpsfc': f"oisstv2.1.1x1.{clim_str}.mon.nc",
        'soilm1m': f"ERA5.soilm1m.1x1.{clim_str}.mon.nc"
    }
    var_map = {'tmp2m': 'tmp2m', 'prate': 'precip', 'tmpsfc': 'tmpsfc', 'soilm1m': 'soilm'}

    if '/cpc/nmme/' in base_path:
        obs_path = "/cpc/home/jinfanti/MET/S2S/PythonWrapper_NMME/nmme_met_development/obs_data/"
    else:
        obs_path = base_path

    full_path = os.path.join(obs_path, file_map[variable])

    ds = None
    obs_years = None
    try:
        ds = xr.open_dataset(full_path, decode_times=True)
        obs_years = _get_obs_years(ds, target_month_idx)
    except Exception:
        ds = None

    try:
        if ds is None:
            ds = xr.open_dataset(full_path, decode_times=False)

        obs_raw = ds[var_map.get(variable, variable)].values.astype(np.float64)
    except Exception as exc:
        raise FileNotFoundError(f"Error loading {full_path}: {exc}") from exc

    if time_period == 'seasonal':
        term_minus = np.roll(obs_raw, 1, axis=0)
        term_plus = np.roll(obs_raw, -1, axis=0)

        term_minus[0] = np.nan
        term_plus[-1] = np.nan

        stack_season = np.stack([term_minus, obs_raw, term_plus], axis=0)
        with np.errstate(invalid='ignore'):
            obs_processed = np.nanmean(stack_season, axis=0)
    elif time_period == 'monthly':
        obs_processed = obs_raw
    else:
        raise ValueError(f"Unsupported time period: {time_period}")

    obs_target_season = obs_processed[target_month_idx::12, :, :]

    if obs_years is None or len(obs_years) != obs_target_season.shape[0]:
        start_year = _parse_climo_start_year(clim_period)
        obs_years = np.arange(start_year, start_year + obs_target_season.shape[0])

    if detrend:
        obs_target_season, _, _ = detrend_grid(obs_target_season, obs_years.astype(np.float64))

    obs_clim = np.nanmean(obs_target_season, axis=0)
    obs_stddev = np.nanstd(obs_target_season, axis=0)
    verif_slice = obs_target_season
    obs_anom = verif_slice - obs_clim

    with np.errstate(divide='ignore', invalid='ignore'):
        obs_std_anom = obs_anom / obs_stddev

    obs_std_anom = np.where(np.isfinite(obs_std_anom), obs_std_anom, np.nan)

    return verif_slice, obs_anom, obs_std_anom, obs_clim, obs_stddev, obs_years
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def create_obs_terciles(obs_anom, obs_std_anom, variable):
    print(f'Creating observed terciles for {variable}...')
    if variable in ['tmp2m', 'tmpsfc']:
        thresh_low, thresh_high = -0.43, 0.43
        field = obs_std_anom
    else:
        thresh_low = np.percentile(obs_anom, 33, axis=0)
        thresh_high = np.percentile(obs_anom, 66, axis=0)
        field = obs_anom

    ut_ones = np.where(field > thresh_high, 1, 0)
    lt_ones = np.where(field < thresh_low, 1, 0)
    mt_ones = np.where((field >= thresh_low) & (field <= thresh_high), 1, 0)

    terciles_obs = np.stack([lt_ones, mt_ones, ut_ones], axis=0)
    print(f'    terciles_obs shape: {terciles_obs.shape}')
    return terciles_obs
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def create_dominant_tercile_fcst(terciles_fcst):
    max_indices = np.argmax(terciles_fcst, axis=0)
    dominant_tercile_model = max_indices + 1.0
    mask_check = np.nansum(terciles_fcst, axis=0)
    dominant_tercile_model = np.where(mask_check == 0, np.nan, dominant_tercile_model)
    dominant_tercile_model = np.where(np.isnan(mask_check), np.nan, dominant_tercile_model)
    return dominant_tercile_model
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
def create_dominant_tercile_obs(terciles_obs):
    max_indices = np.argmax(terciles_obs, axis=0)
    dominant_tercile_obs = max_indices + 1.0
    mask_check = np.nansum(terciles_obs, axis=0)
    dominant_tercile_obs = np.where(mask_check == 0, np.nan, dominant_tercile_obs)
    dominant_tercile_obs = np.where(np.isnan(mask_check), np.nan, dominant_tercile_obs)
    return dominant_tercile_obs
# --------------------------------------------------------------------------------------------------

