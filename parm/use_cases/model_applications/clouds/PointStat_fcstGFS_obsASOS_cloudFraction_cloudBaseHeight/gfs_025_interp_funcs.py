from metpy.interpolate import log_interpolate_1d

# Function to interpolate in a column
def interp_column(prs_lev,hgt_col_isobaric,station_id):

  plev = prs_lev.isel(sid=station_id).values
  pcol = hgt_col_isobaric.isel(sid=station_id).isobaricInhPa.values
  pcol = pcol * 100.0
  zcol = hgt_col_isobaric.isel(sid=station_id).values
  return log_interpolate_1d(plev,pcol,zcol,axis=0)[0]
