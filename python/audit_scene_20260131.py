"""Root-cause audit of the 31 Jan 2026 Sentinel-1 scene that produced ~150-197 ha of false erosion.

Checks (implementation first, physics second):
  1 metadata of all 2025/26 post-monsoon RTC items (platform, orbit, processing fields)
  2 raw (unfiltered) RTC integrity over the AOI: valid fraction, zeros/negatives, NaN, value range
  3 geolocation: FFT phase-correlation shift of each scene vs 19 Jan 2026 (filtered dB)
  4 radiometric stability on stable targets (S2-stable vegetation far from channel, bright settlements,
    permanent water) per date
  5 anomaly morphology: connected patches of single-scene false erosion, sizes, distance to channel
  6 independent corroboration: nearest descending (R150) RTC scene; GEE sigma0 scene if available;
    Sentinel-2 L2A scenes within +/- 12 days (MNDWI/NDVI of the anomaly patches vs control fields)
  7 threshold check: fraction of S2-vegetated domain pixels below the thresholds per date
Writes outputs/reports/root_cause_audit_20260131.md, outputs/tables/audit_20260131_*.csv,
outputs/figures/supp_audit_20260131.png
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rasterio.enums import Resampling
from scipy import ndimage

import config as C
import sage_methods as M
from aoi import load_aoi_ll, load_grid
from pc_access import read_to_grid, search
from reference_validation import _scene as s2_scene

BAD = "2026-01-31"
REF_DATE = "2026-01-19"


def phase_shift(a, b):
    """Sub-pixel-free integer shift (dy, dx) maximising cross-correlation of b w.r.t. a (FFT phase correlation)."""
    a = np.nan_to_num(a - np.nanmean(a)); b = np.nan_to_num(b - np.nanmean(b))
    F = np.fft.fft2(a) * np.conj(np.fft.fft2(b))
    r = np.fft.ifft2(F / (np.abs(F) + 1e-9)).real
    dy, dx = np.unravel_index(np.argmax(r), r.shape)
    if dy > a.shape[0] // 2: dy -= a.shape[0]
    if dx > a.shape[1] // 2: dx -= a.shape[1]
    return int(dy), int(dx), float(r.max())


def main():
    out = {}
    grid = load_grid()
    bbox = load_aoi_ll(bbox=True)
    meta = json.loads((C.CACHE / "s1_pc_2025.json").read_text())
    dates = [d["date"] for d in meta["post"]]
    z = np.load(C.CACHE / "s1_pc_2025.npz")
    post = z["post"]
    with np.errstate(all="ignore"):
        pre = np.nanmean(z["pre"], axis=0)
    ref = np.load(C.DATA / "reference" / "s2_reference_2025.npz")
    dom, refm, cls_pre, cls_post = ref["domain"], ref["ref"], ref["cls_pre"], ref["cls_post"]
    sel = json.loads((C.TABLES / "selected_parameters_pc.json").read_text())

    # 1 metadata
    items = search("sentinel-1-rtc", bbox, "2025-11-01", "2026-02-01",
                   query={"sat:relative_orbit": {"eq": 114}, "sat:orbit_state": {"eq": "ascending"}})
    rows = []
    for it in sorted(items, key=lambda i: i.datetime):
        p = it.properties
        rows.append({"date": it.datetime.date().isoformat(), "id": it.id, "platform": p.get("platform"),
                     "abs_orbit": p.get("sat:absolute_orbit"), "rel_orbit": p.get("sat:relative_orbit"),
                     "processing_level": p.get("processing:level"), "software": json.dumps(p.get("processing:software")),
                     "product_type": p.get("s1:product_type"), "resolution": p.get("s1:resolution"),
                     "instrument_mode": p.get("sar:instrument_mode"), "polarizations": "+".join(p.get("sar:polarizations", [])),
                     "proj_epsg": p.get("proj:epsg"), "datetime": p.get("datetime")})
    md = pd.DataFrame(rows)
    md.to_csv(C.TABLES / "audit_20260131_metadata.csv", index=False)
    out["metadata"] = md
    # 2 raw integrity (re-read unfiltered RTC VV for the bad and the reference scene)
    raw = {}
    integ = []
    for d in (BAD, REF_DATE):
        it = [i for i in items if i.datetime.date().isoformat() == d][0]
        a = read_to_grid(it.assets["vv"].href, grid, resampling=Resampling.average, nodata=None)
        raw[d] = a
        v = a[np.isfinite(a)]
        integ.append({"date": d, "valid_frac": float(np.isfinite(a).mean()), "n_zero": int((v == 0).sum()), "n_negative": int((v < 0).sum()),
                      "min_linear": float(v.min()), "p1_db": float(10 * np.log10(np.percentile(v[v > 0], 1))),
                      "median_db": float(10 * np.log10(np.median(v[v > 0]))), "p99_db": float(10 * np.log10(np.percentile(v[v > 0], 99))),
                      "max_linear": float(v.max())})
    integ = pd.DataFrame(integ)
    out["integrity"] = integ
    # 3 geolocation
    iref = dates.index(REF_DATE)
    geo = []
    for i, d in enumerate(dates):
        dy, dx, peak = phase_shift(post[iref], post[i])
        geo.append({"date": d, "shift_rows_px": dy, "shift_cols_px": dx, "corr_peak": round(peak, 4)})
    geo = pd.DataFrame(geo)
    out["geolocation"] = geo
    # 4 radiometric stability on stable targets
    from reference_validation import channel_complex
    chan = channel_complex(cls_pre)  # main Jamuna channel complex only (ponds excluded)
    dist_ch = ndimage.distance_transform_edt(~chan) * C.PIXEL
    stable_veg = (cls_pre == 0) & (cls_post == 0) & (dist_ch > 2000)
    water = (cls_pre == 1) & (cls_post == 1)
    bright = pre > np.nanpercentile(pre, 98)
    rad = []
    for i, d in enumerate(dates):
        v = post[i]
        rad.append({"date": d, "stable_veg_median_db": float(np.nanmedian(v[stable_veg])),
                    "stable_veg_p05_db": float(np.nanpercentile(v[stable_veg], 5)),
                    "settlement_median_db": float(np.nanmedian(v[bright])), "water_median_db": float(np.nanmedian(v[water])),
                    "frac_stableveg_below_-12.7": float(np.mean(v[stable_veg] < -12.7)),
                    "frac_domainveg_below_-12.7": float(np.mean(v[(cls_post == 0) & dom] < -12.7)),
                    "frac_domainveg_below_Tscene": float(np.mean(v[(cls_post == 0) & dom] < sel["thresholds"]["T_scene"]))})
    rad = pd.DataFrame(rad)
    out["radiometry"] = rad
    # 5 anomaly morphology (published thresholds, single scene)
    ib = dates.index(BAD)
    p_bad = M.baseline(pre, post[[ib]], C.FF["T_6mo"], C.FF["T_1mo"])
    fp = (p_bad == 1) & (refm == 0) & dom
    lab, n = ndimage.label(fp, structure=np.ones((3, 3)))
    sizes = ndimage.sum(fp, lab, index=np.arange(1, n + 1)) * 0.01
    dist_fp = dist_ch[fp]
    morph = {"fp_ha": float(fp.sum() * 0.01), "n_patches": int(n), "patches_ge_1ha": int((sizes >= 1).sum()),
             "largest_patch_ha": float(sizes.max()) if n else 0, "median_dist_to_channel_m": float(np.median(dist_fp)),
             "frac_fp_west_bank": float(np.mean(ref["side"][fp] == 1))}
    out["morphology"] = morph
    # 6a descending scene nearest in time
    desc = search("sentinel-1-rtc", bbox, "2026-01-25", "2026-02-08",
                  query={"sat:relative_orbit": {"eq": 150}, "sat:orbit_state": {"eq": "descending"}})
    corro = []
    big = lab > 0
    big_ids = np.flatnonzero(sizes >= 1) + 1
    anomaly = np.isin(lab, big_ids)
    control = (cls_pre == 0) & (cls_post == 0) & dom & ~ndimage.binary_dilation(anomaly, iterations=20)
    for it in sorted(desc, key=lambda i: i.datetime):
        a = read_to_grid(it.assets["vv"].href, grid, resampling=Resampling.average, nodata=None)
        db = 10 * np.log10(np.where(a > 0, a, np.nan))
        corro.append({"source": "PC RTC R150 descending", "date": it.datetime.date().isoformat(), "id": it.id,
                      "anomaly_median_db": float(np.nanmedian(db[anomaly])), "control_median_db": float(np.nanmedian(db[control]))})
    for d in (BAD, REF_DATE):
        db = 10 * np.log10(np.where(raw[d] > 0, raw[d], np.nan))
        corro.append({"source": "PC RTC R114 ascending (unfiltered)", "date": d, "id": "",
                      "anomaly_median_db": float(np.nanmedian(db[anomaly])), "control_median_db": float(np.nanmedian(db[control]))})
    gee_file = C.CACHE / "s1_gee_2025.npz"
    if gee_file.exists():
        g = np.load(gee_file)
        gm = json.loads((C.CACHE / "s1_gee_2025.json").read_text())
        gd = [d["date"] for d in gm["post"]]
        for d in (BAD, REF_DATE):
            if d in gd:
                v = g["post"][gd.index(d)]
                corro.append({"source": "GEE S1_GRD sigma0 R114 (circle7)", "date": d, "id": ";".join(x["id"] for x in gm["post"][gd.index(d)]["products"]),
                              "anomaly_median_db": float(np.nanmedian(v[anomaly])), "control_median_db": float(np.nanmedian(v[control]))})
    # 6b Sentinel-2 within +/- 12 days
    s2items = search("sentinel-2-l2a", bbox, "2026-01-19", "2026-02-12", query={"eo:cloud_cover": {"lt": 30}})
    seen = set()
    for it in sorted(s2items, key=lambda i: i.datetime):
        key = it.datetime.date()
        if key in seen:
            continue
        seen.add(key)
        sc = s2_scene(it, grid)
        nd, mw = sc["ndvi"], sc["mndwi"]
        if np.isfinite(nd[anomaly]).mean() < 0.5:
            continue
        corro.append({"source": "Sentinel-2 L2A", "date": key.isoformat(), "id": it.id,
                      "anomaly_median_db": None, "control_median_db": None,
                      "anomaly_ndvi": float(np.nanmedian(nd[anomaly])), "control_ndvi": float(np.nanmedian(nd[control])),
                      "anomaly_mndwi": float(np.nanmedian(mw[anomaly])), "control_mndwi": float(np.nanmedian(mw[control])),
                      "anomaly_frac_mndwi_gt0": float(np.nanmean(mw[anomaly] > 0)), "control_frac_mndwi_gt0": float(np.nanmean(mw[control] > 0))})
    corro = pd.DataFrame(corro)
    out["corroboration"] = corro
    for k in ("integrity", "geolocation", "radiometry", "corroboration"):
        out[k].to_csv(C.TABLES / f"audit_20260131_{k}.csv", index=False)
    (C.TABLES / "audit_20260131_morphology.json").write_text(json.dumps(morph, indent=1))
    # figure
    fig, ax = plt.subplots(1, 3, figsize=(16, 6), dpi=160)
    sl = np.s_[:, 250:900]
    ax[0].imshow(post[iref][sl], vmin=-22, vmax=-2, cmap="gray"); ax[0].set_title(f"RTC VV {REF_DATE} (filtered dB)")
    ax[1].imshow(post[ib][sl], vmin=-22, vmax=-2, cmap="gray"); ax[1].set_title(f"RTC VV {BAD} (filtered dB)")
    ax[2].imshow((post[ib] - post[iref])[sl], vmin=-8, vmax=8, cmap="RdBu"); ax[2].set_title(f"difference {BAD} − {REF_DATE} (dB)")
    for a in ax:
        a.contour(anomaly[sl].astype(float), levels=[0.5], colors="yellow", linewidths=0.6)
        a.axis("off")
    fig.suptitle("West floodplain: anomaly patches (yellow) — localized darkening, not a scene-wide offset", fontsize=11)
    fig.tight_layout(); fig.savefig(C.FIGS / "supp_audit_20260131.png", bbox_inches="tight"); plt.close(fig)
    for k, v in out.items():
        print("=====", k); print(v.to_string(index=False) if isinstance(v, pd.DataFrame) else v)


if __name__ == "__main__":
    main()
