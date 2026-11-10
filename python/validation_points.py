"""Stratified validation points for checking the automatic Sentinel-2 reference by visual interpretation.

Step 1 (sample):  python validation_points.py sample <year>
   -> data/reference/validation_points_<year>.csv  (id, stratum, row, col, x, y, lon, lat, auto_label)
   -> outputs/reports/validation_chips_<year>_<n>.png  (sheets of 20 chips: pre RGB | post RGB, crosshair)
Step 2 (labels):  visual labels are written into the CSV column `visual_label`
                  (1 eroded, 0 not eroded, -1 cannot tell) — by the analyst, then spot-checked by the team.
Step 3 (score):   python validation_points.py score <year>  -> outputs/tables/reference_point_agreement_<year>.csv
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import Transformer

import config as C
from aoi import load_grid

HALF = 30  # chip half-size in pixels (30 px = 300 m -> 600 m chips)
N_PER_STRATUM = {"ref_erosion": 50, "ref_nonerosion_near_bank": 50, "ref_uncertain": 20}


def sample(year):
    z = np.load(C.DATA / "reference" / f"s2_reference_{year}.npz")
    ref, dom = z["ref"], z["domain"]
    rng = np.random.default_rng(C.RANDOM_SEED + year)
    # "near bank": non-erosion domain pixels within 300 m of a reference-erosion or channel-edge pixel
    from scipy import ndimage
    chan_edge = ndimage.binary_dilation(np.isin(z["cls_post"], (1, 2)), iterations=30) & dom
    strata = {
        "ref_erosion": (ref == 1) & dom,
        "ref_nonerosion_near_bank": (ref == 0) & chan_edge,
        "ref_uncertain": (ref == -1) & dom,
    }
    g = load_grid()
    tr = Transformer.from_crs(C.WORK_CRS, "EPSG:4326", always_xy=True)
    rows = []
    h, w = ref.shape
    for s, mask in strata.items():
        mask = mask.copy()
        mask[:HALF, :] = mask[-HALF:, :] = False
        mask[:, :HALF] = mask[:, -HALF:] = False
        idx = np.flatnonzero(mask.ravel())
        if idx.size == 0:
            continue
        pick = rng.choice(idx, size=min(N_PER_STRATUM[s], idx.size), replace=False)
        for p in pick:
            r, c = divmod(int(p), w)
            x = g.bounds[0] + (c + 0.5) * g.res
            y = g.bounds[3] - (r + 0.5) * g.res
            lon, lat = tr.transform(x, y)
            rows.append({"stratum": s, "row": r, "col": c, "x": x, "y": y, "lon": round(lon, 6), "lat": round(lat, 6),
                         "auto_label": int(ref[r, c])})
    df = pd.DataFrame(rows).sample(frac=1, random_state=year).reset_index(drop=True)  # shuffle: blind to stratum
    df.insert(0, "id", [f"P{year}_{i:03d}" for i in range(len(df))])
    df["visual_label"] = ""
    df["visual_note"] = ""
    df["team_check"] = ""
    df.to_csv(C.DATA / "reference" / f"validation_points_{year}.csv", index=False)
    chips(year, df, z)
    print(df.stratum.value_counts())


def chips(year, df, z):
    pre, post = z["rgb_pre"], z["rgb_post"]
    per = 20
    for sheet in range(int(np.ceil(len(df) / per))):
        sub = df.iloc[sheet * per:(sheet + 1) * per]
        fig, axes = plt.subplots(5, 8, figsize=(16, 10.5), dpi=110)
        for i, ax in enumerate(axes.ravel()):
            ax.axis("off")
        for j, (_, p) in enumerate(sub.iterrows()):
            r, c = int(p.row), int(p.col)
            for t, img in enumerate((pre, post)):
                ax = axes.ravel()[2 * j + t]
                chip = img[r - HALF:r + HALF, c - HALF:c + HALF]
                ax.imshow(np.nan_to_num(np.clip(chip / 0.25, 0, 1), nan=1))
                ax.plot([HALF - 0.5], [HALF - 0.5], marker="+", color="magenta", ms=14, mew=2)
                ax.set_title(f"{p.id} {'Feb-Mar ' + str(year) if t == 0 else 'Feb-Mar ' + str(year + 1)}", fontsize=7)
        fig.suptitle(f"Validation chips {year} sheet {sheet} (600 m x 600 m, crosshair = point; stratum hidden)", fontsize=10)
        fig.tight_layout()
        fig.savefig(C.REPORTS / f"validation_chips_{year}_{sheet}.png")
        plt.close(fig)


def score(year):
    df = pd.read_csv(C.DATA / "reference" / f"validation_points_{year}.csv")
    df = df[df.visual_label.astype(str).str.strip() != ""].copy()
    df["visual_label"] = df.visual_label.astype(int)
    out = []
    for s, g in df.groupby("stratum"):
        dec = g[g.visual_label >= 0]
        out.append({"year": year, "stratum": s, "n_points": len(g), "n_visual_decided": len(dec),
                    "visual_eroded": int((dec.visual_label == 1).sum()), "visual_not_eroded": int((dec.visual_label == 0).sum()),
                    "visual_cannot_tell": int((g.visual_label < 0).sum()),
                    "agreement_with_auto_label": float(np.mean(dec.visual_label == dec.auto_label)) if len(dec) and s != "ref_uncertain" else np.nan})
    res = pd.DataFrame(out)
    res.to_csv(C.TABLES / f"reference_point_agreement_{year}.csv", index=False)
    print(res.to_string())


if __name__ == "__main__":
    {"sample": sample, "score": score}[sys.argv[1]](int(sys.argv[2]))
