#!/usr/bin/env python3
"""
inspect_zarr.py

Inspect a Zarr field via zarr_reader.py and optionally write the extracted data
(including lat/lon) to a compressed .npz for later plotting.

Usage:
  python inspect_zarr.py zarr.conf
  python inspect_zarr.py zarr.conf --write out.npz

Output .npz contains:
  - data: extracted array (whatever selection produced)
  - lat:  2D latitude (y,x) after the same y/x subsetting (or empty if unavailable)
  - lon:  2D longitude (y,x) after the same y/x subsetting (or empty if unavailable)
  - dims: dimension names as strings
  - meta_json: JSON metadata string
"""

from __future__ import annotations

import argparse
import json
import configparser

import numpy as np
import zarr

from zarr_reader import read_forecast_from_conf, parse_range

def _load_zarr_latlon_from_conf(conf_path: str):
    """
    Open the Zarr store and extract latitude/longitude arrays, applying the same
    y/x subsetting from the config.
    """
    cfgp = configparser.ConfigParser()
    cfgp.read(conf_path)
    c = cfgp["config"]

    store_path = c.get("FCST_ZARR_STORE")
    lat_name = c.get("FCST_ZARR_LAT_VAR", fallback="latitude")
    lon_name = c.get("FCST_ZARR_LON_VAR", fallback="longitude")

    y_sel = parse_range(c.get("FCST_Y_RANGE", fallback=None))
    x_sel = parse_range(c.get("FCST_X_RANGE", fallback=None))

    root = zarr.open(store_path, mode="r")
    if lat_name not in root or lon_name not in root:
        return None, None

    lat = np.asarray(root[lat_name][:])
    lon = np.asarray(root[lon_name][:])

    # Apply same y/x slicing as data selection (assumes config uses y/x in the same grid)
    if y_sel is not None and y_sel != slice(None):
        lat = lat[y_sel, :]
        lon = lon[y_sel, :]
    if x_sel is not None and x_sel != slice(None):
        lat = lat[:, x_sel]
        lon = lon[:, x_sel]

    return lat, lon


def main():
    ap = argparse.ArgumentParser(
        description="Inspect a Zarr field via zarr_reader.py and optionally write data+lat/lon to .npz"
    )
    ap.add_argument("conf", help="Path to Zarr config file (e.g., config.conf)")
    ap.add_argument(
        "--write",
        default=None,
        metavar="OUT.npz",
        help="If set, write a compressed .npz containing data, lat, lon, dims, and meta_json",
    )
    args = ap.parse_args()

    res = read_forecast_from_conf(args.conf)

    print("\n==============================")
    print("ZARR READ SUMMARY")
    print("==============================")

    print("Store path     :", res.meta.get("store_path"))
    print("Variable       :", res.meta.get("var_name"))
    print("Original shape :", res.meta.get("original_shape"))
    print("Chunks         :", res.meta.get("chunks"))

    print("\nSelected dims  :", res.dims)
    print("Selection tuple:", res.selection)
    print("Selectors dict :", res.selectors)

    print("\nData shape     :", res.data.shape)
    print("Data dtype     :", res.data.dtype)

    size_mb = res.data.nbytes / (1024**2)
    print(f"Data size      : {size_mb:.2f} MB")

    if res.data.size:
        print("Min / Max      :", np.nanmin(res.data), "/", np.nanmax(res.data))
        print("Mean / Std     :", np.nanmean(res.data), "/", np.nanstd(res.data))

    print("\n==============================")
    print("COORDINATE INFO (FROM STORE)")
    print("==============================")
    for name, info in res.meta.get("coord_info", {}).items():
        print(f"{name}: shape={info['shape']} dtype={info['dtype']}")

    print("\n==============================")
    print("SELECTED COORDINATE VALUES")
    print("==============================")
    for dim, values in res.meta.get("selected_coords", {}).items():
        if values is None:
            continue
        print(f"\n{dim.upper()} VALUES:")
        print("  count:", len(values))
        if len(values) <= 10:
            print("  values:", values)
        else:
            print("  first :", values[0])
            print("  last  :", values[-1])

    print("\n==============================")
    print("SPATIAL SAMPLE (Top-left 5x5)")
    print("==============================")
    if res.data.ndim >= 2:
        idx = (0,) * (res.data.ndim - 2)
        patch = res.data[idx + (slice(0, 5), slice(0, 5))]
        print(patch)

    if args.write:
        lat, lon = _load_zarr_latlon_from_conf(args.conf)

        if lat is None:
            lat = np.array([])
        if lon is None:
            lon = np.array([])

        meta_json = json.dumps(res.meta, indent=2, default=str)

        np.savez_compressed(
            args.write,
            data=res.data,
            lat=lat,
            lon=lon,
            dims=np.array(res.dims, dtype=object),
            meta_json=np.array(meta_json, dtype=object),
        )

        print("\n==============================")
        print("WROTE OUTPUT (.npz)")
        print("==============================")
        print("Saved to:", args.write)
        print("Contains: data, lat, lon, dims, meta_json")

    print("\n==============================")
    print("DONE")
    print("==============================")

if __name__ == "__main__":
    main()
