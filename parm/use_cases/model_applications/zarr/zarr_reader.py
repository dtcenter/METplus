# zarr_reader.py
from __future__ import annotations

import configparser
from dataclasses import dataclass
from typing import Optional, Union, Tuple, Dict, Any, List

import numpy as np
import zarr

IndexSel = Union[int, slice]

def parse_range(val: Optional[str]):
    """
    Supports:
      5          -> int
      0,10       -> slice(0,10)
      [0,7]      -> list [0,7]
      0,7,9      -> list [0,7,9]
      None       -> None
    """
    if val is None:
        return None

    val = val.strip()
    if not val:
        return None

    # List syntax: [0,7]
    if val.startswith("[") and val.endswith("]"):
        parts = val[1:-1].split(",")
        return [int(p.strip()) for p in parts if p.strip()]

    parts = [p.strip() for p in val.split(",") if p.strip()]

    if len(parts) == 1:
        return int(parts[0])

    if len(parts) == 2:
        return slice(int(parts[0]), int(parts[1]))

    # More than 2 → treat as list
    return [int(p) for p in parts]


def open_zarr_store(path: str):
    try:
        return zarr.open_consolidated(path, mode="r")
    except Exception:
        return zarr.open_group(path, mode="r")


def _mutually_exclusive(cfg: configparser.SectionProxy, keys: List[str]) -> Optional[str]:
    defined = [k for k in keys if cfg.get(k, fallback=None) is not None]
    if len(defined) > 1:
        raise ValueError(f"Only one of {', '.join(keys)} may be defined. Found: {defined}")
    return defined[0] if defined else None


def _nearest_index(coord: np.ndarray, value: float) -> Tuple[int, float]:
    coord = np.asarray(coord, dtype=np.float64)
    idx = int(np.argmin(np.abs(coord - float(value))))
    return idx, float(coord[idx])


def _extract_selected_coord(root, coord_name: Optional[str], selector):
    """
    Return coordinate values corresponding to selector:
      - int
      - slice
      - list/tuple/np.ndarray of indices
    Keeps output 1D (even for int selection).
    """
    if coord_name is None or coord_name not in root:
        return None

    coord = np.asarray(root[coord_name][:])

    if selector is None:
        return coord

    if isinstance(selector, int):
        return coord[selector:selector + 1]

    if isinstance(selector, slice):
        return coord[selector]

    # NEW: list/tuple/np.ndarray indexing
    if isinstance(selector, (list, tuple, np.ndarray)):
        return coord[np.array(selector, dtype=int)]

    return coord


@dataclass
class ZarrReadResult:
    data: np.ndarray
    dims: List[str]
    selection: Tuple[Any, ...]
    selectors: Dict[str, Any]
    meta: Dict[str, Any]


def read_forecast_from_conf(
    conf_path: str,
    *,
    time_sel: Optional[IndexSel] = None,
    lead_sel: Optional[IndexSel] = None,
    level_sel: Optional[IndexSel] = None,
    y_sel: Optional[IndexSel] = None,
    x_sel: Optional[IndexSel] = None,
) -> ZarrReadResult:
    """
    Read data from a Zarr store using a MET-style config.

    If *_sel is provided, it overrides config selection keys.

    Returns:
      ZarrReadResult with:
        - data: numpy array
        - dims: list of dim names in order (e.g., ["time","lead","level","y","x"])
        - selection: tuple used to index the Zarr array
        - selectors: dict mapping dim->selector
        - meta: includes selected coordinate values for time/lead/level (when available)
    """
    config = configparser.ConfigParser()
    config.read(conf_path)
    cfg = config["config"]

    # ---- Required ----
    store_path = cfg.get("FCST_ZARR_STORE")
    var_name = cfg.get("FCST_ZARR_VAR")
    dims = [d.strip() for d in cfg.get("FCST_ZARR_DIMS").split(",")]

    # ---- Optional coordinate vars ----
    time_var = cfg.get("FCST_ZARR_TIME_VAR", fallback=None)
    lead_var = cfg.get("FCST_ZARR_LEAD_VAR", fallback=None)
    level_var = cfg.get("FCST_ZARR_LEVEL_VAR", fallback=None)
    lat_var = cfg.get("FCST_ZARR_LAT_VAR", fallback=None)
    lon_var = cfg.get("FCST_ZARR_LON_VAR", fallback=None)

    root = open_zarr_store(store_path)

    if var_name not in root:
        raise ValueError(f"Variable '{var_name}' not found in store.")

    arr = root[var_name]

    if len(dims) != arr.ndim:
        raise ValueError(f"Dimension mapping mismatch: mapping={dims}, array_rank={arr.ndim}")

    # -------------------------------------------------------
    # TIME selection
    # -------------------------------------------------------
    if time_sel is None:
        time_key = _mutually_exclusive(cfg, ["FCST_TIME_RANGE", "FCST_TIME_INDEX"])
        time_sel = parse_range(cfg.get(time_key)) if time_key else None

    # -------------------------------------------------------
    # LEAD selection
    # -------------------------------------------------------
    if lead_sel is None:
        lead_key = _mutually_exclusive(cfg, ["FCST_LEAD_RANGE", "FCST_LEAD_INDEX"])
        lead_sel = parse_range(cfg.get(lead_key)) if lead_key else None

    # -------------------------------------------------------
    # LEVEL selection (range / index / value)
    # -------------------------------------------------------
    if level_sel is None:
        level_key = _mutually_exclusive(cfg, ["FCST_LEVEL_RANGE", "FCST_LEVEL_INDEX", "FCST_LEVEL_VALUE"])
        if level_key == "FCST_LEVEL_RANGE":
            level_sel = parse_range(cfg.get(level_key))

        elif level_key == "FCST_LEVEL_INDEX":
            level_sel = int(cfg.get(level_key))

        elif level_key == "FCST_LEVEL_VALUE":
            if level_var is None:
                raise ValueError("FCST_LEVEL_VALUE provided but FCST_ZARR_LEVEL_VAR not set.")
            if level_var not in root:
                raise ValueError(f"Level variable '{level_var}' not found in Zarr store.")

            level_array = np.asarray(root[level_var][:], dtype=np.float64)
            level_value = float(cfg.get(level_key))
            idx, actual = _nearest_index(level_array, level_value)

            print(f"[zarr_reader] Selecting level value {level_value} at index {idx} (actual={actual})")
            level_sel = idx

    # -------------------------------------------------------
    # Spatial selection
    # -------------------------------------------------------
    if y_sel is None:
        y_sel = parse_range(cfg.get("FCST_Y_RANGE", fallback=None))
    if x_sel is None:
        x_sel = parse_range(cfg.get("FCST_X_RANGE", fallback=None))

    # -------------------------------------------------------
    # Build selectors (dict) and selection tuple
    # -------------------------------------------------------
    selectors: Dict[str, Any] = {d: slice(None) for d in dims}

    if time_sel is not None and "time" in selectors:
        selectors["time"] = time_sel
    if lead_sel is not None and "lead" in selectors:
        selectors["lead"] = lead_sel
    if level_sel is not None and "level" in selectors:
        selectors["level"] = level_sel
    if y_sel is not None and "y" in selectors:
        selectors["y"] = y_sel
    if x_sel is not None and "x" in selectors:
        selectors["x"] = x_sel

    selection = tuple(selectors[d] for d in dims)

    # -------------------------------------------------------
    # Read data
    # -------------------------------------------------------
    data = np.asarray(arr[selection])

    # -------------------------------------------------------
    # Extract selected coordinate values (time/lead/level + lat/lon metadata)
    # -------------------------------------------------------
    selected_coords: Dict[str, Any] = {}

    for dim_name in dims:
        coord_var = None
        if dim_name == "time":
            coord_var = time_var
        elif dim_name == "lead":
            coord_var = lead_var
        elif dim_name == "level":
            coord_var = level_var

        if coord_var:
            selected_coords[dim_name] = _extract_selected_coord(root, coord_var, selectors.get(dim_name))

    # lat/lon arrays can be huge; store only basic info
    coord_info: Dict[str, Any] = {}
    for coord_name in [time_var, lead_var, level_var, lat_var, lon_var]:
        if coord_name and coord_name in root:
            coord_info[coord_name] = {
                "shape": tuple(root[coord_name].shape),
                "dtype": str(root[coord_name].dtype),
            }

    meta: Dict[str, Any] = {
        "store_path": store_path,
        "var_name": var_name,
        "original_shape": tuple(arr.shape),
        "chunks": arr.chunks,
        "coord_info": coord_info,
        "selected_coords": selected_coords,
    }

    return ZarrReadResult(
        data=data,
        dims=dims,
        selection=selection,
        selectors=selectors,
        meta=meta,
    )


def get_coord_array_from_conf(conf_path: str, coord_key: str) -> np.ndarray:
    """
    load a coordinate array by name from the same config.

    Example:
      get_coord_array_from_conf(conf, "FCST_ZARR_LEAD_VAR") -> lead_time array
    """
    config = configparser.ConfigParser()
    config.read(conf_path)
    cfg = config["config"]

    store_path = cfg.get("FCST_ZARR_STORE")
    coord_name = cfg.get(coord_key, fallback=None)
    if coord_name is None:
        raise ValueError(f"{coord_key} not set in config.")

    root = open_zarr_store(store_path)
    if coord_name not in root:
        raise ValueError(f"Coordinate '{coord_name}' not found in store.")
    return np.asarray(root[coord_name][:])

