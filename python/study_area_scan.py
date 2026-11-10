"""Study-area reconnaissance: Sentinel-2 L2A Feb-Mar median composites (2025 vs 2026) for candidate Jamuna reaches.

Purpose: find outer-bank reaches with visible vegetation -> sand/water conversion during the 2025 monsoon
before fixing the 10-15 km study reach. 30 m reconnaissance resolution (final analysis uses 10 m).
COG overviews are read (20 m for 10 m bands) to keep downloads small.

Outputs:
  data/cache/recon/recon_<box>_<year>.npz/.json
  outputs/maps/recon_<box>.png  (RGB 2025 | RGB 2026 | NDVI-loss overlay)
Run: .venv\\Scripts\\python.exe python\\study_area_scan.py [box ...]
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer
from rasterio.enums import Resampling

import config as C
from pc_access import Grid, read_to_grid, search

BOXES = {  # lon_min, lat_min, lon_max, lat_max
    "kurigram": (89.55, 25.30, 89.95, 25.85),
    "bogura_gaibandha": (89.50, 24.75, 89.85, 25.30),
    "sirajganj": (89.55, 24.10, 89.95, 24.75),
}
RES = 30.0
WINDOWS = {2025: ("2025-02-01", "2025-03-31"), 2026: ("2026-02-01", "2026-03-31")}
SCL_BAD = {0, 1, 3, 8, 9, 10}
OUTDIR = C.CACHE / "recon"
OUTDIR.mkdir(parents=True, exist_ok=True)


def make_grid(bbox):
    tr = Transformer.from_crs("EPSG:4326", C.WORK_CRS, always_xy=True)
    xs, ys = [], []
    for lon in (bbox[0], bbox[2]):
        for lat in (bbox[1], bbox[3]):
            x, y = tr.transform(lon, lat)
            xs.append(x); ys.append(y)
    b = (np.floor(min(xs) / RES) * RES, np.floor(min(ys) / RES) * RES, np.ceil(max(xs) / RES) * RES, np.ceil(max(ys) / RES) * RES)
    return Grid(C.WORK_CRS, b, RES)


def scene_arrays(item, grid):
    a = item.assets
    scl = read_to_grid(a["SCL"].href, grid, resampling=Resampling.nearest, nodata=0)
    bad = np.isnan(scl) | np.isin(np.nan_to_num(scl, nan=0).astype(int), list(SCL_BAD))
    pb = float(item.properties.get("s2:processing_baseline", "0") or 0)
    off = 1000.0 if pb >= 4.0 else 0.0
    out = {}
    for b in ("B02", "B03", "B04", "B08", "B11"):
        ov = 0 if b in ("B02", "B03", "B04", "B08") else None  # 10 m bands: first overview = 20 m
        arr = read_to_grid(a[b].href, grid, resampling=Resampling.average, nodata=0, overview_level=ov)
        arr = (arr - off) / 10000.0
        arr[bad] = np.nan
        out[b] = arr
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (out["B08"] - out["B04"]) / (out["B08"] + out["B04"])
        mndwi = (out["B03"] - out["B11"]) / (out["B03"] + out["B11"])
    return {"ndvi": ndvi.astype("float32"), "mndwi": mndwi.astype("float32"),
            "rgb": np.dstack([out["B04"], out["B03"], out["B02"]]).astype("float32")}


def composite(box, year):
    bbox = BOXES[box]
    grid = make_grid(bbox)
    s, e = WINDOWS[year]
    items = search("sentinel-2-l2a", bbox, s, e, query={"eo:cloud_cover": {"lt": 15}})
    by_tile = {}
    for it in items:
        by_tile.setdefault(it.properties.get("s2:mgrs_tile"), []).append(it)
    chosen = []
    for t, its in by_tile.items():
        chosen += sorted(its, key=lambda i: i.properties["eo:cloud_cover"])[:5]
    print(box, year, "items", len(items), "tiles", sorted(by_tile), "chosen", len(chosen), flush=True)
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda it: scene_arrays(it, grid), chosen))
    ndvi = np.nanmedian(np.stack([r["ndvi"] for r in res]), axis=0)
    mndwi = np.nanmedian(np.stack([r["mndwi"] for r in res]), axis=0)
    rgb = np.nanmedian(np.stack([r["rgb"] for r in res]), axis=0)
    del res
    np.savez_compressed(OUTDIR / f"recon_{box}_{year}.npz", ndvi=ndvi, mndwi=mndwi, rgb=rgb)
    (OUTDIR / f"recon_{box}_{year}.json").write_text(json.dumps({"grid": grid.to_dict(), "window": WINDOWS[year],
                                                                  "items": [i.id for i in chosen]}, indent=1))
    return grid, ndvi, mndwi, rgb


def panel(box):
    g, n25, w25, rgb25 = composite(box, 2025)
    _, n26, w26, rgb26 = composite(box, 2026)
    loss = (n25 > 0.35) & (n26 < 0.15)
    tr = Transformer.from_crs(C.WORK_CRS, "EPSG:4326", always_xy=True)
    xmin, ymin, xmax, ymax = g.bounds
    fig, ax = plt.subplots(1, 3, figsize=(18, 10), dpi=130)
    for a, img, t in ((ax[0], rgb25, "S2 Feb-Mar 2025"), (ax[1], rgb26, "S2 Feb-Mar 2026")):
        a.imshow(np.nan_to_num(np.clip(img / 0.25, 0, 1), nan=1), extent=(xmin, xmax, ymin, ymax))
        a.set_title(t)
    ax[2].imshow(np.nan_to_num(n26, nan=0), cmap="Greys_r", vmin=-0.3, vmax=0.8, extent=(xmin, xmax, ymin, ymax))
    ax[2].imshow(np.ma.masked_where(~loss, loss.astype(float)), cmap="autumn", alpha=1, extent=(xmin, xmax, ymin, ymax))
    ax[2].set_title("red/yellow: NDVI>0.35 (2025) -> <0.15 (2026)")
    for a in ax:
        a.set_xticks(np.arange(np.ceil(xmin / 5000) * 5000, xmax, 5000))
        a.set_yticks(np.arange(np.ceil(ymin / 5000) * 5000, ymax, 5000))
        a.tick_params(labelsize=6)
        a.grid(alpha=0.35, lw=0.4)
    fig.suptitle(f"Reconnaissance {box}: UTM45N grid lines every 5 km", fontsize=11)
    fig.tight_layout()
    fig.savefig(C.MAPS / f"recon_{box}.png", bbox_inches="tight")
    plt.close(fig)
    print(box, "loss pixels (30 m):", int(loss.sum()), "≈ ha:", round(loss.sum() * 0.09, 1), flush=True)


if __name__ == "__main__":
    for b in (sys.argv[1:] or list(BOXES)):
        panel(b)
