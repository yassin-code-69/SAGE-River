"""Study-area (AOI) definition and the common 10 m analysis grid.

The AOI is written once by `select_aoi.py` (after Sentinel-2 inspection) to data/aoi/aoi.geojson and
data/aoi/grid.json; every other script loads it from there so all products share one grid.
"""
import json

from pyproj import Transformer

import config as C
from pc_access import Grid

AOI_GEOJSON = C.DATA / "aoi" / "aoi.geojson"
GRID_JSON = C.DATA / "aoi" / "grid.json"


def save_aoi(name, bounds_utm, rationale, extra=None):
    """bounds_utm: (xmin, ymin, xmax, ymax) in WORK_CRS metres (snapped to 10 m)."""
    xmin, ymin, xmax, ymax = [round(v / C.PIXEL) * C.PIXEL for v in bounds_utm]
    grid = Grid(C.WORK_CRS, (xmin, ymin, xmax, ymax), C.PIXEL)
    tr = Transformer.from_crs(C.WORK_CRS, "EPSG:4326", always_xy=True)
    ring = [tr.transform(x, y) for x, y in ((xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin))]
    feat = {"type": "FeatureCollection", "features": [{
        "type": "Feature",
        "properties": {"name": name, "crs_analysis": C.WORK_CRS, "bounds_utm": [xmin, ymin, xmax, ymax],
                       "width_km": (xmax - xmin) / 1000, "height_km": (ymax - ymin) / 1000,
                       "rationale": rationale, **(extra or {})},
        "geometry": {"type": "Polygon", "coordinates": [[list(map(lambda v: round(v, 6), p)) for p in ring]]}}]}
    AOI_GEOJSON.write_text(json.dumps(feat, indent=1))
    GRID_JSON.write_text(json.dumps(grid.to_dict(), indent=1))
    return grid


def load_grid():
    g = json.loads(GRID_JSON.read_text())
    return Grid(g["crs"], g["bounds"], g["res"])


def load_aoi_ll(bbox=False):
    js = json.loads(AOI_GEOJSON.read_text())
    ring = js["features"][0]["geometry"]["coordinates"][0]
    if not bbox:
        return ring
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    return (min(lons), min(lats), max(lons), max(lats))


def aoi_props():
    return json.loads(AOI_GEOJSON.read_text())["features"][0]["properties"]
