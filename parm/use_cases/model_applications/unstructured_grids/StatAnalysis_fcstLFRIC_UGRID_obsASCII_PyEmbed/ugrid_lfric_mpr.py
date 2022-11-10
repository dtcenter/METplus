from __future__ import print_function

import math
import pandas as pd
import numpy as np
import os
from glob import glob
import sys
import xarray as xr
import datetime as dt
import iris
from iris.experimental.ugrid import PARSE_UGRID_ON_LOAD
#geovista from https://github.com/bjlittle/geovista/
import geovista as gv
import geovista.theme
from geovista.common import to_xyz
import netCDF4
import pyvista as pv
from pykdtree.kdtree import KDTree

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

print(f"{iris.__version__=}")
print(f"{gv.__version__=}")

########################################################################

def read_ascii_obs(files):
    paths = sorted(glob(files))
    datasets = [pd.read_table(p, header=None, delim_whitespace=True) for p in paths]
    combined = pd.concat(datasets)
    return combined

def load_ugrid(
    fname: str,
    data: Optional[bool] = False,
    constraint: Optional[str] = None,
    verbose: Optional[bool] = False
) -> pv.PolyData:
#    fname = BASE_DIR / fname
    with PARSE_UGRID_ON_LOAD.context():
        cube = iris.load_cube(fname, constraint=constraint)
        
    if cube.ndim > 1:
        cube = cube[(0,) * (cube.ndim - 1)]
    
    if verbose:
        print(cube)
    
    data = cube.data if data else None
        
    face_node = cube.mesh.face_node_connectivity
    indices = face_node.indices_by_location()
    lons, lats = cube.mesh.node_coords

    mesh = gv.Transform.from_unstructured(
        lons.points,
        lats.points,
        indices,
        data=data,
        start_index=face_node.start_index,
        name=cube.name(),
    )

    if data is None:
        mesh.active_scalars_name = None
    
    return mesh

def info(mesh: pv.PolyData) -> None:
    print(f"The mesh is a C{int(math.sqrt(mesh.n_cells / 6))}, with 6 panels, {int(mesh.n_cells / 6):,d} cells per panel, and {mesh.n_cells:,d} cells.")

def find_nearest(tree, points, poi, k):
    # lat/lon to xyz
    xyz = to_xyz(*poi)
    
    # find the k nearest euclidean neighbours
    dist, idxs = tree.query(xyz, k=k)
    
    if idxs.ndim > 1:
        idxs = idxs[0]
    
    # retieve the associated xyz points of the k nearest neighbours
    nearest = points[idxs]
    
    return xyz, nearest, idxs

def to_centers(mesh: pv.PolyData) -> pv.PolyData:
    tmp = mesh.copy()
    tmp.clear_cell_data()
    tmp.clear_point_data()
    tmp.clear_field_data()
    return tmp.cell_centers()

########################################################################
print('Python Script:\t', sys.argv[0])

# Input is directory of .nc lfric files and a directory of ascii obs filess

if len(sys.argv) == 3:
    # Read the input file as the first argument
    input_fcst_dir = os.path.expandvars(sys.argv[1])
    input_obs_dir = os.path.expandvars(sys.argv[2])
    try:
        print("Input Forecast Dir:\t" + repr(input_fcst_dir))
        print("Input Observations Dir:\t" + repr(input_obs_dir))

        #Read all obs from directory
        obs_data = read_ascii_obs(input_obs_dir+'/*.ascii')
        print(obs_data.shape)
        obs_data = obs_data.iloc[::1000, :]#thin for testing
        obs_data = obs_data.rename(columns={0:'message_type', 1:'station_id', 2:'obs_valid_time', 3:'obs_lat', 4:'obs_lon', \
                             5:'elevation', 6:'var_name', 7:'level', 8:'height', 9:'qc_string', 10:'obs_value'})
   
        obs_vars = ['UGRD', 'VGRD', 'TMP', 'RH']
        fcst_vars = ['u10m', 'v10m', 't1p5m', 'rh1p5m']

        #open the netcdf forecast to access data values and list of times
        fcst_data = xr.open_dataset(input_fcst_dir)
        fcst_times = pd.to_datetime(fcst_data.coords['time_centered'])

        match_df = pd.DataFrame(columns=['message_type', 'station_id', 'obs_valid_time', 'obs_lat', 'obs_lon', \
                'elevation', 'var_name', 'level', 'height', 'qc_string', 'obs_value', 'idx_nearest, fcst_value'])

        for idx1, (obs_var, fcst_var) in enumerate(zip(obs_vars, fcst_vars)):
        
            #load forecast as an iris cube
            fcst_mesh = load_ugrid(input_fcst_dir, constraint=fcst_var)
            info(fcst_mesh)
        
            #get indices of nearest cell center
            fcst_centers = to_centers(fcst_mesh)
            points = fcst_centers.points
            tree = KDTree(points)

            #get the forecast data values loaded
            fcst_df = fcst_data[fcst_var].to_dataframe()
            print(fcst_df)
        
            #get obs data for variable
            var_data = obs_data.loc[obs_data['var_name'] == obs_var].reset_index(drop=True)

            for idx2, row in var_data.iterrows():
                xyz, nearest, idx_nearest = find_nearest(tree, points, [row['obs_lat'], row['obs_lon']], k=1)
                var_data.at[idx2,'idx_nearest'] = int(idx_nearest)

                #get the obs time, search for closest in the forecast data
                time = dt.datetime.strptime(row['obs_valid_time'],'%Y%m%d_%H%M%S')
                match_time = min(fcst_times, key=lambda  d: abs(d - time))
                match_idx = np.argmin(np.abs(fcst_times - time))

                #add matched fcst value to data
                var_data.at[idx2, 'fcst_value'] = fcst_df.loc[(match_idx,int(idx_nearest)), fcst_var]
                var_data.at[idx2, 'fcst_lat'] = fcst_df.loc[(match_idx,int(idx_nearest)), 'Mesh2d_face_x']
                var_data.at[idx2, 'fcst_lon'] = fcst_df.loc[(match_idx,int(idx_nearest)), 'Mesh2d_face_y']
                var_data.at[idx2, 'fcst_time'] = fcst_df.loc[(match_idx,int(idx_nearest)), 'time_centered']
                
            #check results
            #with pd.option_context('display.max_rows', None):
            #    print(var_data[['obs_lat','fcst_lat','obs_lon','fcst_lon','obs_value','fcst_value','obs_valid_time','fcst_time']])
            with pd.option_context('display.max_columns', 500, 'display.max_rows', 100, 'display.width', 500):
                print(var_data)
            ob_vals = var_data['obs_value'].values
            f_vals = var_data['fcst_value'].values

            match_df = pd.concat([match_df, var_data], ignore_index=True)

        nlocs = len(match_df.index)
        print('Number of locations in matched set: ' + str(nlocs)) 
            
        # Add additional columns
        match_df['lead'] = '000000'
        match_df['MPR'] = 'MPR'
        match_df['nobs'] = nlocs
        match_df['index'] = range(0,nlocs)
        match_df['na'] = 'NA'
        match_df['QC'] = '0'

        # Arrange columns in MPR format
        cols = ['na','na','lead','obs_valid_time','obs_valid_time','lead','obs_valid_time',
                'obs_valid_time','var_name','na','lead','var_name','na','na',
                'var_name','na','na','lead','na','na','na','na','MPR',
                'nobs','index','station_id','obs_lat','obs_lon',
                'level','na','fcst_value','obs_value',
                'QC','na','na']
        
        match_df = match_df[cols]

        # Into a list and all to strings
        mpr_data = [list( map(str,i) ) for i in match_df.values.tolist() ]

    except NameError: 
        print("Can't find the input files or the variables.")
        print("Variables in this file:\t" + repr(var_list))
else:
    print("ERROR: ugrid_lfric_mpr.py -> Must specify directory of files.\n")
    sys.exit(1)

########################################################################

