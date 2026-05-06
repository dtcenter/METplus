#!/usr/bin/env python3

from __future__ import annotations

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz", help="Input .npz containing data+lat+lon")
    ap.add_argument("out_png", help="Output PNG")
    ap.add_argument("--title", default=None)
    ap.add_argument("--cbar_label", default="Value")
    ap.add_argument("--cmap", default="viridis")
    ap.add_argument("--nbins", type=int, default=10, help="Number of discrete bins")
    ap.add_argument("--vmin", type=float, default=None, help="Manual colorbar minimum")
    ap.add_argument("--vmax", type=float, default=None, help="Manual colorbar maximum")
    ap.add_argument("--dpi", type=int, default=220)
    args = ap.parse_args()

    with np.load(args.npz, allow_pickle=True) as f:
        data = np.asarray(f["data"])
        lat = np.asarray(f["lat"])
        lon = np.asarray(f["lon"])

    field = np.squeeze(data)
    if field.ndim != 2:
        raise ValueError(f"Expected 2D field. Got {field.shape}")

    if lat.shape != field.shape or lon.shape != field.shape:
        raise ValueError("Shape mismatch between field and lat/lon")

    # ----------------------------
    # Color limits
    # ----------------------------
    if args.vmin is not None and args.vmax is not None:
        vmin = args.vmin
        vmax = args.vmax
    else:
        vmin = float(np.nanpercentile(field, 1))
        vmax = float(np.nanpercentile(field, 99))

    if vmax <= vmin:
        raise ValueError("vmax must be greater than vmin")

    bins = np.linspace(vmin, vmax, args.nbins + 1)

    cmap = plt.get_cmap(args.cmap, args.nbins)
    norm = mcolors.BoundaryNorm(bins, cmap.N)

    # ----------------------------
    # Cartopy
    # ----------------------------
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.ticker as mticker

    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.LambertConformal(
        central_longitude=-100,
        central_latitude=35,
        standard_parallels=(33, 45),
    )

    fig = plt.figure(figsize=(15, 9))
    ax = plt.axes(projection=map_crs)

    # Auto-zoom
    mask = np.isfinite(field)
    lat_valid = lat[mask]
    lon_valid = lon[mask]

    lat_min, lat_max = float(lat_valid.min()), float(lat_valid.max())
    lon_min, lon_max = float(lon_valid.min()), float(lon_valid.max())

    lat_margin = 0.05 * (lat_max - lat_min)
    lon_margin = 0.05 * (lon_max - lon_min)

    ax.set_extent(
        [lon_min - lon_margin, lon_max + lon_margin,
         lat_min - lat_margin, lat_max + lat_margin],
        crs=data_crs,
    )

    # Field first
    pm = ax.pcolormesh(
        lon,
        lat,
        field,
        transform=data_crs,
        cmap=cmap,
        norm=norm,
        shading="auto",
        zorder=1,
    )

    # Borders on top
    ax.add_feature(
        cfeature.NaturalEarthFeature("physical", "coastline", "10m", facecolor="none"),
        linewidth=1.0, edgecolor="black", zorder=5,
    )

    ax.add_feature(
        cfeature.NaturalEarthFeature("cultural", "admin_0_boundary_lines_land", "10m", facecolor="none"),
        linewidth=1.0, edgecolor="black", zorder=6,
    )

    ax.add_feature(
        cfeature.NaturalEarthFeature("cultural", "admin_1_states_provinces_lines", "10m", facecolor="none"),
        linewidth=0.6, edgecolor="black", zorder=7,
    )

    # Gridlines
    gl = ax.gridlines(
        crs=data_crs,
        draw_labels=True,
        linewidth=0.6,
        linestyle="--",
        alpha=0.6,
        zorder=8,
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlocator = mticker.FixedLocator(np.arange(-180, -40, 10))
    gl.ylocator = mticker.FixedLocator(np.arange(0, 81, 10))

    # Discrete colorbar
    cbar = plt.colorbar(
        pm,
        ax=ax,
        orientation="horizontal",
        pad=0.06,
        shrink=0.85,
        boundaries=bins,
        ticks=bins,
        spacing="proportional",
    )
    cbar.set_label(args.cbar_label)

    if args.title:
        ax.set_title(args.title)

    plt.tight_layout()
    plt.savefig(args.out_png, dpi=args.dpi)
    plt.close(fig)

    print("Saved:", args.out_png)
    print("vmin/vmax:", vmin, vmax)
    print("Bins:", bins)

if __name__ == "__main__":
    main()
