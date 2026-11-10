"""Build per-acquisition Sentinel-1 VV stacks (speckle-filtered, dB) on the study grid.

Two interchangeable sources, recorded in every output's metadata:
  * "gee"  : COPERNICUS/S1_GRD sigma0 (Earth Engine) - the published baseline's data source (preferred)
  * "pc"   : Microsoft Planetary Computer sentinel-1-rtc gamma0 (no-login fallback; terrain-flattened gamma0,
             no incidence-angle band -> angle mask cannot be applied; thresholds must be recalibrated)

Filtering follows the released Freihardt & Frey code: linear units -> normalised circular kernel of
radius 7 px (ee.Kernel.circle(radius=7)) -> dB. The paper-described square 7x7 boxcar is available as an
alternative ("square7") for the paper/code discrepancy check.

Usage:
  python s1_stack.py --source gee --year 2025       # needs Earth Engine project in data/metadata/gee_project.json
  python s1_stack.py --source pc  --year 2025
Outputs: data/cache/s1_<source>_<year>.npz + .json (dates, product IDs, platform, orbit, filter, grid)
"""
import argparse
import json
from datetime import date, datetime, timedelta

import numpy as np
from scipy import ndimage

import config as C
from aoi import load_grid, load_aoi_ll


# ---------------------------------------------------------------- kernels (local implementation)
def kernel(name):
    if name == "circle7":  # matches ee.Kernel.circle({radius:7, units:'pixels', normalize:true})
        r = 7
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        k = (xx ** 2 + yy ** 2 <= r * r).astype("float64")
    elif name == "square7":
        k = np.ones((7, 7))
    else:
        raise ValueError(name)
    return k / k.sum()


def filter_linear_to_db(lin, kname):
    """Normalised convolution that ignores NaN (masked) pixels, like GEE's masked convolve."""
    valid = np.isfinite(lin) & (lin > 0)
    k = kernel(kname)
    num = ndimage.convolve(np.where(valid, lin, 0.0), k, mode="constant")
    den = ndimage.convolve(valid.astype("float64"), k, mode="constant")
    with np.errstate(invalid="ignore", divide="ignore"):
        out = num / den
        db = 10.0 * np.log10(out)
    db[(den < 0.5) | ~valid] = np.nan
    return db.astype("float32")


# ---------------------------------------------------------------- Earth Engine source
def gee_init():
    import ee
    proj = json.loads((C.DATA / "metadata" / "gee_project.json").read_text())["project"]
    ee.Initialize(project=proj)
    return ee


def gee_collection(ee, region, start, end, orbit=C.REL_ORBIT):
    col = (ee.ImageCollection(C.FF["collection"]).filterBounds(region)
           .filter(ee.Filter.eq("instrumentMode", "IW"))
           .filter(ee.Filter.eq("resolution_meters", 10))
           .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
           .filter(ee.Filter.eq("orbitProperties_pass", C.FF["pass"]))
           .filterDate(start, end))
    if orbit is not None:
        col = col.filter(ee.Filter.eq("relativeOrbitNumber_start", orbit))
    return col


def gee_stack(start, end, kname="circle7"):
    ee = gee_init()
    grid = load_grid()
    lon0, lat0, lon1, lat1 = load_aoi_ll(bbox=True)
    region = ee.Geometry.Rectangle([lon0, lat0, lon1, lat1])
    col = gee_collection(ee, region, start, end)
    props = col.aggregate_array("system:index").getInfo()
    times = col.aggregate_array("system:time_start").getInfo()
    plats = col.aggregate_array("platform_number").getInfo()
    orbs = col.aggregate_array("relativeOrbitNumber_start").getInfo()
    by_date = {}
    for pid, t, p, o in zip(props, times, plats, orbs):
        d = datetime.utcfromtimestamp(t / 1000).date().isoformat()
        by_date.setdefault(d, []).append({"id": pid, "platform": "S1" + str(p), "rel_orbit": o, "time_ms": t})
    dates = sorted(by_date)
    xmin, ymin, xmax, ymax = grid.bounds
    req_grid = {"dimensions": {"width": grid.width, "height": grid.height},
                "affineTransform": {"scaleX": grid.res, "shearX": 0, "translateX": xmin,
                                    "shearY": 0, "scaleY": -grid.res, "translateY": ymax},
                "crsCode": grid.crs}
    if kname == "circle7":
        k = ee.Kernel.circle(radius=7, units="pixels", normalize=True)   # released code
    else:
        k = ee.Kernel.square(radius=3, units="pixels", normalize=True)   # paper text: 7x7 boxcar

    def per_image(img):
        # F&F order: per-image angle mask (30-45 deg) -> toNatural -> convolve in the image's native 10 m grid -> toDB
        ang = img.select("angle")
        vv = img.select("VV").updateMask(ang.gt(C.FF["angle_min"])).updateMask(ang.lt(C.FF["angle_max"]))
        filt = ee.Image(10.0).pow(vv.divide(10.0)).convolve(k).log10().multiply(10.0).rename("VVf")
        return filt.addBands(ang.rename("angle"))

    def one_day(d):
        d0 = date.fromisoformat(d)
        # slices of the same pass/day are filtered individually, then mosaicked so each acquisition counts once
        out = col.filterDate(d, (d0 + timedelta(days=1)).isoformat()).map(per_image).mosaic().toFloat().unmask(-9999)
        for attempt in range(4):
            try:
                arr = ee.data.computePixels({"expression": out, "fileFormat": "NUMPY_NDARRAY", "grid": req_grid})
                break
            except Exception as e:
                if attempt == 3:
                    raise
                print("  retry", d, str(e)[:120], flush=True)
        v = arr["VVf"].astype("float32")
        a = arr["angle"].astype("float32")
        v[v <= -9998] = np.nan
        a[a <= -9998] = np.nan
        return v, a

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one_day, dates))
    arrays = [r[0] for r in res]
    angles = [r[1] for r in res]
    meta = []
    for d, v, a in zip(dates, arrays, angles):
        meta.append({"date": d, "products": by_date[d],
                     "angle_min": float(np.nanmin(a)) if np.isfinite(a).any() else None,
                     "angle_max": float(np.nanmax(a)) if np.isfinite(a).any() else None})
        print("  GEE", d, [x["id"] for x in by_date[d]], "valid frac %.3f" % np.isfinite(v).mean(), flush=True)
    return np.stack(arrays), np.stack(angles), meta


# ---------------------------------------------------------------- Planetary Computer source
def pc_stack(start, end, kname="circle7"):
    from rasterio.enums import Resampling
    from pc_access import read_to_grid, search
    grid = load_grid()
    bbox = load_aoi_ll(bbox=True)
    items = search("sentinel-1-rtc", bbox, start, end,
                   query={"sat:orbit_state": {"eq": "ascending"}, "sat:relative_orbit": {"eq": C.REL_ORBIT}})
    by_date = {}
    for it in items:
        d = it.datetime.date().isoformat()
        by_date.setdefault(d, []).append(it)
    from concurrent.futures import ThreadPoolExecutor

    def one_day(d):
        lin = None
        for it in by_date[d]:  # mosaic slices of the same pass
            a = read_to_grid(it.assets["vv"].href, grid, resampling=Resampling.average, nodata=None)
            lin = a if lin is None else np.where(np.isnan(lin), a, lin)
        return filter_linear_to_db(lin, kname)

    days = sorted(by_date)
    with ThreadPoolExecutor(6) as ex:
        arrays = list(ex.map(one_day, days))
    meta = []
    for d, arr in zip(days, arrays):
        meta.append({"date": d, "products": [{"id": it.id, "platform": it.properties.get("platform"),
                                               "rel_orbit": it.properties.get("sat:relative_orbit")} for it in by_date[d]]})
        print("  PC", d, [it.id for it in by_date[d]], "valid frac %.3f" % np.isfinite(arr).mean(), flush=True)
    return np.stack(arrays), None, meta


def build(source, year, kname="circle7"):
    Y = C.YEARS[year]
    out = {}
    for part in ("pre", "post_pool"):
        s, e = Y[part]
        print(f"[{source}] {year} {part} {s}..{e}")
        if source == "gee":
            arr, ang, meta = gee_stack(s, e, kname)
        else:
            arr, ang, meta = pc_stack(s, e, kname)
        out[part] = (arr, ang, meta)
    tag = f"s1_{source}_{year}" + ("" if kname == "circle7" else f"_{kname}")
    np.savez_compressed(C.CACHE / f"{tag}.npz", pre=out["pre"][0], post=out["post_pool"][0],
                        **({"pre_angle": out["pre"][1], "post_angle": out["post_pool"][1]} if source == "gee" else {}))
    (C.CACHE / f"{tag}.json").write_text(json.dumps({
        "source": source, "year": year, "filter": kname, "grid": load_grid().to_dict(),
        "pre_window": Y["pre"], "post_window": Y["post_pool"],
        "pre": out["pre"][2], "post": out["post_pool"][2],
        "created": datetime.now().isoformat(timespec="seconds")}, indent=1))
    print("saved", tag)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["gee", "pc"], required=True)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--filter", default="circle7", choices=["circle7", "square7"])
    a = ap.parse_args()
    build(a.source, a.year, a.filter)
