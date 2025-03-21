from metpy.interpolate import log_interpolate_1d

# Function to interpolate in a column
# This function takes:
# prs_lev --> the pressure level of the data
# hgt_col_isobaric --> a vector of geopotential height values for the current model column on pressure levels
# station_id --> An integer value representing the current station (model grid cell) being processed. This
#                is used to subset the data being passed in.
#
# This function creates a vector of pressure levels using the isobaricInhPa coordinate value of the geopotential height
# column, to interpolate from a single pressure level to a geopotential height value. It returns a single
# geopotential height value corresponding to the pressure value passed in.
def interp_column(prs_lev,hgt_col_isobaric,station_id):

  plev = prs_lev.isel(sid=station_id).values
  pcol = hgt_col_isobaric.isel(sid=station_id).isobaricInhPa.values
  pcol = pcol * 100.0
  zcol = hgt_col_isobaric.isel(sid=station_id).values
  return log_interpolate_1d(plev,pcol,zcol,axis=0)[0]
