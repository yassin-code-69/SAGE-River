"""Independent Sentinel-2 L2A reference for outer-bank erosion (vegetated land -> sand/water).

Reference = an independent OPTICAL SENSOR reference, NOT field ground truth.

Per evaluation year Y (monsoon Y):
  pre composite  : Feb-Mar of year Y        (before monsoon Y)
  post composite : Feb-Mar of year Y+1      (after monsoon Y; LATER than every SAR post scene)
  as-of composite: 10 Nov - 15 Dec of year Y (optional; used to separate erosion visible by mid-December)

Classes per composite (thresholds checked against visual point interpretation, see validation_points):
  VEG   : NDVI >= T_VEG
  WATER : MNDWI >= T_WATER
  SAND  : NDVI <  T_BARE and MNDWI < T_WATER  (bare sand / exposed bed)
  AMBIG : everything else, or < MIN_OBS clear observations

Reference label (int8): 1 erosion, 0 non-erosion, -1 uncertain (excluded from scoring)
  erosion     = VEG_pre AND (WATER|SAND)_post AND connected to the post-monsoon channel complex
  uncertain   = AMBIG in either composite, OR VEG_pre->nonveg_post patch NOT connected to the channel
                (e.g. harvested/fallow fields), OR too few clear observations
  non-erosion = everything else inside the evaluation domain

Evaluation domain = outer floodplain strip, OUTER_STRIP_M wide, measured outward from the pre-monsoon
channel-complex edge on each bank (row-wise; the Jamuna flows roughly north-south). In-channel chars and
sandbars are thereby excluded, following Freihardt & Frey's focus on outer riverbanks.
"""
import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from rasterio.enums import Resampling
from scipy import ndimage

import config as C
from aoi import load_aoi_ll, load_grid
from pc_access import read_to_grid, search

T_VEG = 0.30
T_BARE = 0.20
T_WATER = 0.00
MIN_OBS = 3
MAX_ITEMS = 14  # least-cloudy (date, tile) items per composite window
OUTER_STRIP_M = 1500.0
SCL_BAD = {0, 1, 3, 8, 9, 10}
BANDS = ("B02", "B03", "B04", "B08", "B11")


def _scene(item, grid):
    a = item.assets
    scl = read_to_grid(a["SCL"].href, grid, resampling=Resampling.nearest, nodata=0)
    bad = np.isnan(scl) | np.isin(np.nan_to_num(scl, nan=0).astype(int), list(SCL_BAD))
    pb = float(item.properties.get("s2:processing_baseline", "0") or 0)
    off = 1000.0 if pb >= 4.0 else 0.0  # harmonise L2A >= baseline 04.00 (same as S2_SR_HARMONIZED)
    out = {}
    for b in BANDS:
        arr = read_to_grid(a[b].href, grid, resampling=Resampling.bilinear, nodata=0)
        arr = (arr - off) / 10000.0
        arr[bad] = np.nan
        out[b] = arr
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (out["B08"] - out["B04"]) / (out["B08"] + out["B04"])
        mndwi = (out["B03"] - out["B11"]) / (out["B03"] + out["B11"])
    return {"ndvi": ndvi.astype("float32"), "mndwi": mndwi.astype("float32"),
            "rgb": np.dstack([out["B04"], out["B03"], out["B02"]]).astype("float16")}


def composite(start, end, max_cloud=60):
    """Median S2 composite on the AOI grid; cached per window in data/cache/s2_<start>_<end>.npz."""
    cache = C.CACHE / f"s2_{start}_{end}.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=False)
        meta = json.loads(cache.with_suffix(".json").read_text())
        return {k: z[k] for k in z.files}, meta
    comp, meta = _composite(start, end, max_cloud)
    np.savez_compressed(cache, **comp)
    cache.with_suffix(".json").write_text(json.dumps(meta, indent=1))
    return comp, meta


def _composite(start, end, max_cloud=60):
    grid = load_grid()
    bbox = load_aoi_ll(bbox=True)
    items = search("sentinel-2-l2a", bbox, start, end, query={"eo:cloud_cover": {"lt": max_cloud}})
    # one item per (date, tile); drop exact duplicates of reprocessed products
    seen, chosen = set(), []
    for it in sorted(items, key=lambda i: i.properties["eo:cloud_cover"]):
        key = (it.datetime.date(), it.properties.get("s2:mgrs_tile"))
        if key not in seen:
            seen.add(key)
            chosen.append(it)
    chosen = chosen[:MAX_ITEMS]  # least-cloudy first; memory cap (documented)
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda it: _scene(it, grid), chosen))
    ndvi = np.stack([r["ndvi"] for r in res])
    mndwi = np.stack([r["mndwi"] for r in res])
    st = {"rgb": np.stack([r["rgb"] for r in res]).astype("float32")}
    del res
    # per-date mosaics can double-count a date covered by two tiles; nobs counts unique dates
    dates = np.array([it.datetime.date().toordinal() for it in chosen])
    valid = np.isfinite(ndvi)
    nobs = np.zeros(ndvi.shape[1:], dtype=np.int16)
    for d in np.unique(dates):
        nobs += np.any(valid[dates == d], axis=0)
    comp = {
        "ndvi": np.nanmedian(ndvi, axis=0).astype("float32"),
        "mndwi": np.nanmedian(mndwi, axis=0).astype("float32"),
        "rgb": np.nanmedian(st["rgb"], axis=0).astype("float32"),
        "nobs": nobs,
    }
    meta = {"window": [start, end], "n_items": len(chosen),
            "items": [{"id": it.id, "date": it.datetime.date().isoformat(), "cloud": it.properties["eo:cloud_cover"],
                       "tile": it.properties.get("s2:mgrs_tile")} for it in chosen]}
    return comp, meta


def classify(comp):
    ndvi, mndwi, nobs = comp["ndvi"], comp["mndwi"], comp["nobs"]
    cls = np.full(ndvi.shape, 3, dtype=np.int8)  # 3 = AMBIG
    water = mndwi >= T_WATER
    veg = (ndvi >= T_VEG) & ~water
    sand = (ndvi < T_BARE) & ~water
    cls[sand] = 2
    cls[water] = 1
    cls[veg] = 0
    cls[(nobs < MIN_OBS) | ~np.isfinite(ndvi) | ~np.isfinite(mndwi)] = 3
    return cls  # 0 VEG, 1 WATER, 2 SAND, 3 AMBIG


def channel_complex(cls):
    """Sand/water components connected to the largest water body (the active Jamuna channels)."""
    water = cls == 1
    lab_w, n_w = ndimage.label(water, structure=np.ones((3, 3)))
    if n_w == 0:
        return np.zeros_like(water)
    sizes = ndimage.sum(water, lab_w, index=np.arange(1, n_w + 1))
    main_water = lab_w == (1 + int(np.argmax(sizes)))
    nonveg = (cls == 1) | (cls == 2)
    lab, n = ndimage.label(nonveg, structure=np.ones((3, 3)))
    keep = np.unique(lab[main_water])
    keep = keep[keep > 0]
    return np.isin(lab, keep)


def outer_strip(chan_pre, res=C.PIXEL, width_m=OUTER_STRIP_M):
    """Row-wise outer-bank strips just outside the westmost/eastmost channel-complex pixel."""
    h, w = chan_pre.shape
    n = int(round(width_m / res))
    dom = np.zeros_like(chan_pre, dtype=bool)
    side = np.zeros(chan_pre.shape, dtype=np.int8)  # 1 west bank, 2 east bank
    for i in range(h):
        cols = np.flatnonzero(chan_pre[i])
        if cols.size == 0:
            continue
        lo, hi = cols[0], cols[-1]
        a0 = max(0, lo - n)
        dom[i, a0:lo] = True
        side[i, a0:lo] = 1
        b1 = min(w, hi + 1 + n)
        dom[i, hi + 1:b1] = True
        side[i, hi + 1:b1] = 2
    # rows where the channel edge touches the AOI border are not valid outer-bank rows on that side
    return dom, side


def build_reference(year, use_asof=True):
    Y = C.YEARS[year]
    pre, mpre = composite(*Y["s2_pre"])
    post, mpost = composite(*Y["s2_post"])
    cpre, cpost = classify(pre), classify(post)
    chan_pre = channel_complex(cpre)
    chan_post = channel_complex(cpost)
    dom, side = outer_strip(chan_pre)
    cand = (cpre == 0) & np.isin(cpost, (1, 2))
    ref = np.zeros(cpre.shape, dtype=np.int8)
    ref[cand & chan_post] = 1
    ref[cand & ~chan_post] = -1
    ref[(cpre == 3) | (cpost == 3)] = -1
    ref[~dom] = -1
    out = {"ref": ref, "domain": dom, "side": side, "cls_pre": cpre, "cls_post": cpost,
           "ndvi_pre": pre["ndvi"], "ndvi_post": post["ndvi"], "mndwi_pre": pre["mndwi"], "mndwi_post": post["mndwi"],
           "rgb_pre": pre["rgb"], "rgb_post": post["rgb"], "nobs_pre": pre["nobs"], "nobs_post": post["nobs"]}
    meta = {"year": year, "pre": mpre, "post": mpost,
            "thresholds": {"T_VEG": T_VEG, "T_BARE": T_BARE, "T_WATER": T_WATER, "MIN_OBS": MIN_OBS,
                           "OUTER_STRIP_M": OUTER_STRIP_M}}
    if use_asof:
        s = f"{year}-11-10"
        e = f"{year}-12-16"
        asof, masof = composite(s, e)
        casof = classify(asof)
        out["cls_asof"] = casof
        out["rgb_asof"] = asof["rgb"]
        out["nobs_asof"] = asof["nobs"]
        meta["asof"] = masof
    stats = {"domain_px": int(dom.sum()), "ref_erosion_px": int((ref == 1).sum()), "ref_nonerosion_px": int((ref == 0).sum()),
             "ref_uncertain_in_domain_px": int(((ref == -1) & dom).sum())}
    meta["stats"] = stats
    # AOI-level (not tile-level) optical data quality
    import pandas as pd
    q = []
    for lab, comp_nobs, m in (("pre", pre["nobs"], mpre), ("post", post["nobs"], mpost)) + \
            ((("asof", out["nobs_asof"], meta["asof"]),) if use_asof else ()):
        q.append({"year": year, "composite": lab, "window": "..".join(m["window"]), "n_items": m["n_items"],
                  "aoi_median_clear_dates": float(np.median(comp_nobs)),
                  "aoi_frac_px_ge3_clear": float(np.mean(comp_nobs >= MIN_OBS)),
                  "domain_frac_px_ge3_clear": float(np.mean(comp_nobs[dom] >= MIN_OBS)) if dom.any() else np.nan})
    qf = C.TABLES / "s2_reference_quality.csv"
    old = pd.read_csv(qf) if qf.exists() else pd.DataFrame()
    if len(old):
        old = old[old.year != year]
    pd.concat([old, pd.DataFrame(q)]).to_csv(qf, index=False)
    np.savez_compressed(C.DATA / "reference" / f"s2_reference_{year}.npz", **out)
    (C.DATA / "reference" / f"s2_reference_{year}.json").write_text(json.dumps(meta, indent=1))
    print(year, stats)
    return out, meta


if __name__ == "__main__":
    import sys
    years = [int(a) for a in sys.argv[1:]] or [2024, 2025]
    for y in years:
        build_reference(y)
