"""Sentinel-1 scene inventory for the final AOI + Figure A.

Sources (all queried for the exact final AOI polygon/bbox):
  * GEE  COPERNICUS/S1_GRD  (primary, if Earth Engine is initialised)
  * ASF  search API (GRD_HD, IW)                         - independent public catalogue
  * PC   Planetary Computer sentinel-1-rtc STAC          - independent public catalogue
Counts are reported per unique ACQUISITION = (platform, relative orbit, UTC date); several GRD slices of the
same pass over the AOI count once.

Outputs:
  outputs/tables/sentinel1_scene_inventory.csv         (one row per GRD product, primary source)
  outputs/tables/sentinel1_acquisitions.csv            (one row per acquisition, all sources merged)
  outputs/tables/sentinel1_counts_by_year_orbit.csv
  outputs/tables/sentinel1_window_counts.csv           (Nov / Nov-Dec / Nov-Jan / Nov-Apr per season, R114 ASC)
  outputs/tables/sentinel1_source_comparison.csv
  outputs/figures/figure_A_scene_availability.png/.pdf
"""
import csv
import io
import json
import sys
from datetime import date, datetime

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

import config as C
from aoi import load_aoi_ll

START, END = "2014-10-01", "2026-11-11"


def wkt_polygon():
    ring = load_aoi_ll()
    return "POLYGON((" + ",".join(f"{x:.5f} {y:.5f}" for x, y in ring) + "))"


def inv_gee():
    import ee
    proj = json.loads((C.DATA / "metadata" / "gee_project.json").read_text())["project"]
    ee.Initialize(project=proj)
    ring = load_aoi_ll()
    region = ee.Geometry.Polygon([ring])
    col = (ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(region).filterDate(START, END)
           .filter(ee.Filter.eq("instrumentMode", "IW")))
    names = ["system:index", "system:time_start", "platform_number", "orbitProperties_pass", "relativeOrbitNumber_start",
             "transmitterReceiverPolarisation", "resolution_meters", "instrumentMode"]
    vals = {n: col.aggregate_array(n).getInfo() for n in names}
    rows = []
    for i in range(len(vals["system:index"])):
        t = datetime.utcfromtimestamp(vals["system:time_start"][i] / 1000)
        rows.append({"source": "GEE", "product_id": vals["system:index"][i], "datetime_utc": t.isoformat(),
                     "date": t.date().isoformat(), "platform": "S1" + str(vals["platform_number"][i]),
                     "pass": vals["orbitProperties_pass"][i], "rel_orbit": int(vals["relativeOrbitNumber_start"][i]),
                     "polarisations": "+".join(vals["transmitterReceiverPolarisation"][i]),
                     "resolution_m": vals["resolution_meters"][i], "mode": vals["instrumentMode"][i]})
    return pd.DataFrame(rows)


def inv_asf():
    url = ("https://api.daac.asf.alaska.edu/services/search/param?dataset=SENTINEL-1&processingLevel=GRD_HD&beamMode=IW"
           f"&intersectsWith={requests.utils.quote(wkt_polygon())}&start={START}T00:00:00Z&end={END}T23:59:59Z&output=csv")
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    rows = []
    for x in csv.DictReader(io.StringIO(r.text)):
        t = datetime.fromisoformat(x["Start Time"].replace("Z", "+00:00"))
        rows.append({"source": "ASF", "product_id": x["Granule Name"], "datetime_utc": t.replace(tzinfo=None).isoformat(),
                     "date": t.date().isoformat(), "platform": "S1" + x["Platform"][-1],  # "Sentinel-1A" -> "S1A"
                     "pass": x["Ascending or Descending?"].upper(), "rel_orbit": int(x["Path Number"]),
                     "polarisations": x["Granule Name"][14:16], "resolution_m": 10, "mode": "IW"})
    return pd.DataFrame(rows)


def inv_pc():
    from pc_access import search
    bbox = load_aoi_ll(bbox=True)
    rows = []
    for y0 in range(2014, 2027):
        items = search("sentinel-1-rtc", bbox, f"{y0}-01-01", f"{y0}-12-31T23:59:59Z", max_items=2000)
        for it in items:
            p = it.properties
            rows.append({"source": "PC_RTC", "product_id": it.id, "datetime_utc": it.datetime.replace(tzinfo=None).isoformat(),
                         "date": it.datetime.date().isoformat(), "platform": "S1" + p.get("platform", "?")[-1].upper(),
                         "pass": p.get("sat:orbit_state", "").upper(), "rel_orbit": int(p.get("sat:relative_orbit", -1)),
                         "polarisations": "+".join(p.get("sar:polarizations", [])), "resolution_m": 10, "mode": "IW"})
    return pd.DataFrame(rows)


def acquisitions(df):
    g = df.groupby(["source", "platform", "rel_orbit", "pass", "date"]).agg(n_products=("product_id", "size"),
                                                                           product_ids=("product_id", lambda s: ";".join(sorted(s)))).reset_index()
    return g


def window_counts(acq, source):
    a = acq[(acq.source == source) & (acq.rel_orbit == C.REL_ORBIT)].copy()
    a["d"] = pd.to_datetime(a["date"]).dt.date
    rows = []
    for y in range(2014, 2026):
        def n(s, e):
            return int(((a.d >= s) & (a.d < e)).sum())
        rows.append({"source": source, "season": f"{y}/{y + 1}", "orbit": f"R{C.REL_ORBIT} ASC",
                     "Nov": n(date(y, 11, 1), date(y, 12, 1)), "Nov-Dec": n(date(y, 11, 1), date(y + 1, 1, 1)),
                     "Nov-Jan": n(date(y, 11, 1), date(y + 1, 2, 1)), "Nov-Apr": n(date(y, 11, 1), date(y + 1, 5, 1))})
    return pd.DataFrame(rows)


def figure_A(acq, src, wc):
    a = acq[acq.source == src].copy()
    a["year"] = pd.to_datetime(a["date"]).dt.year
    a["orbit"] = a.apply(lambda r: f"R{r.rel_orbit} {'ASC' if r['pass'].startswith('A') else 'DSC'}", axis=1)
    tab = a.groupby(["year", "orbit", "platform"]).size().unstack(["orbit", "platform"], fill_value=0)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), dpi=200, gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axes[0]
    years = sorted(a.year.unique())
    orbits = sorted(a.orbit.unique())
    plats = sorted(a.platform.unique())
    colors = {"S1A": "#1f4e79", "S1B": "#7fb3d5", "S1C": "#f0a202", "S1D": "#2a9d8f"}
    w = 0.38
    for oi, orb in enumerate(orbits):
        bottom = np.zeros(len(years))
        for pl in plats:
            vals = np.array([tab.get((orb, pl), pd.Series(dtype=int)).get(y, 0) for y in years])
            if vals.sum() == 0:
                continue
            x = np.arange(len(years)) + (oi - 0.5) * w
            ax.bar(x, vals, w * 0.95, bottom=bottom, color=colors.get(pl, "grey"),
                   hatch="" if "ASC" in orb else "//", edgecolor="white", linewidth=0.4,
                   label=f"{orb} · {pl}")
            bottom += vals
    ax.set_xticks(np.arange(len(years)))
    ax.set_xticklabels(years, rotation=45)
    ax.set_ylabel("Unique acquisitions over AOI")
    ax.set_title(f"(a) Sentinel-1 IW acquisitions per year and relative orbit [{src}; 2026 to 10 Nov]", loc="left", fontsize=11)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.32)
    ax.legend(fontsize=8, ncol=3, frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax2 = axes[1]
    w2 = wc[(wc.source == src)].copy()
    w2 = w2[w2.season.isin([f"{y}/{y + 1}" for y in range(2017, 2026)])]
    cols = ["Nov", "Nov-Dec", "Nov-Jan", "Nov-Apr"]
    pal = ["#c0392b", "#e67e22", "#2a9d8f", "#1f4e79"]
    xs = np.arange(len(w2))
    for i, c in enumerate(cols):
        ax2.bar(xs + (i - 1.5) * 0.2, w2[c].values, 0.19, color=pal[i], label=c)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(w2.season, rotation=45, fontsize=8)
    ax2.set_ylabel(f"R{C.REL_ORBIT} ascending acquisitions")
    ax2.set_title("(b) Post-monsoon window length vs scenes available", loc="left", fontsize=11)
    ax2.set_ylim(0, 20.5)
    ax2.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax2.legend(fontsize=8, frameon=False, title="window starting 1 Nov", title_fontsize=8, ncol=4, loc="upper left")
    ax2.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(C.FIGS / "figure_A_scene_availability.png", bbox_inches="tight")
    fig.savefig(C.FIGS / "figure_A_scene_availability.pdf", bbox_inches="tight")
    plt.close(fig)


def main(use_gee):
    frames = []
    if use_gee:
        frames.append(inv_gee())
    frames.append(inv_asf())
    frames.append(inv_pc())
    prod = pd.concat(frames, ignore_index=True)
    primary = "GEE" if use_gee else "ASF"
    prod[prod.source == primary].sort_values("datetime_utc").to_csv(C.TABLES / "sentinel1_scene_inventory.csv", index=False)
    prod.sort_values(["source", "datetime_utc"]).to_csv(C.TABLES / "sentinel1_products_all_sources.csv", index=False)
    acq = acquisitions(prod)
    acq.to_csv(C.TABLES / "sentinel1_acquisitions.csv", index=False)
    a2 = acq.copy()
    a2["year"] = pd.to_datetime(a2["date"]).dt.year
    a2.groupby(["source", "year", "rel_orbit", "pass", "platform"]).size().rename("n_acquisitions").reset_index() \
        .to_csv(C.TABLES / "sentinel1_counts_by_year_orbit.csv", index=False)
    wc = pd.concat([window_counts(acq, s) for s in acq.source.unique()])
    wc.to_csv(C.TABLES / "sentinel1_window_counts.csv", index=False)
    # source comparison on acquisition keys (date, rel_orbit)
    keys = {s: set(zip(acq[acq.source == s].date, acq[acq.source == s].rel_orbit)) for s in acq.source.unique()}
    comp = []
    srcs = sorted(keys)
    for i, s1 in enumerate(srcs):
        for s2 in srcs[i + 1:]:
            # PC RTC starts later in some regions; compare over the common period
            comp.append({"source_1": s1, "source_2": s2, "n_1": len(keys[s1]), "n_2": len(keys[s2]),
                         "common": len(keys[s1] & keys[s2]), "only_1": len(keys[s1] - keys[s2]), "only_2": len(keys[s2] - keys[s1]),
                         "only_1_examples": ";".join(f"{d}/R{o}" for d, o in sorted(keys[s1] - keys[s2])[:15]),
                         "only_2_examples": ";".join(f"{d}/R{o}" for d, o in sorted(keys[s2] - keys[s1])[:15])})
    pd.DataFrame(comp).to_csv(C.TABLES / "sentinel1_source_comparison.csv", index=False)
    figure_A(acq, primary, wc)
    print(pd.DataFrame(comp).to_string())
    print(wc[wc.source == primary].to_string())


if __name__ == "__main__":
    if "--figure-only" in sys.argv:  # redraw Figure A from the saved CSVs (no catalogue queries)
        acq = pd.read_csv(C.TABLES / "sentinel1_acquisitions.csv")
        wc = pd.read_csv(C.TABLES / "sentinel1_window_counts.csv")
        figure_A(acq, "GEE" if "GEE" in set(acq.source) else "ASF", wc)
    else:
        main(use_gee="--gee" in sys.argv)
