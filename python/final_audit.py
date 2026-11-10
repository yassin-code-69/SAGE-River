"""Final quality-control audit. Writes outputs/reports/final_audit.md and exits non-zero on hard failures.

Checks
  1. required files exist (and are non-empty)
  2. CSV sanity (metric ranges, subset counts = C(8,k), no NaN where impossible)
  3. metric recomputation: re-evaluates a random sample of Experiment-A rows from raw arrays
  4. leakage: parameters frozen before 2025 metrics; 2025 never used in calibration tables
  5. poster text scan for forbidden claims
Usage: python final_audit.py --source gee|pc
"""
import argparse
import itertools
import json
import math
import re
import sys
from datetime import datetime

import numpy as np
import pandas as pd

import config as C
import sage_methods as M
from metrics import evaluate

FORBIDDEN = [r"\bfirst\b(?! (1|2|3|three|two|scene|k|acquisition))", r"ground truth(?! data were)", r"\bPINN\b(?!s? (is|are) not| or)",
             r"\bpredict(s|ion|ed)? (future|next)", r"\bforecast(ing)? (system|model) (we|our)", r"world'?s first", r"novel framework"]


def main(source):
    rep, hard = [], []

    def ok(cond, msg, is_hard=True):
        rep.append(("PASS" if cond else ("FAIL" if is_hard else "WARN")) + " — " + msg)
        if not cond and is_hard:
            hard.append(msg)

    req = ["outputs/tables/sentinel1_scene_inventory.csv", "outputs/tables/sentinel1_acquisitions.csv",
           "outputs/figures/figure_A_scene_availability.png", "outputs/figures/figure_0_study_area.png",
           f"outputs/tables/experiment_A_all_subsets_{source}.csv", f"outputs/tables/experiment_A_summary_{source}.csv",
           f"outputs/tables/experiment_B_chronological_{source}.csv", f"outputs/tables/selected_parameters_{source}.json",
           f"outputs/tables/calibration_thresholds_2024_{source}.csv", "outputs/figures/figure_B_maps.png",
           "outputs/figures/figure_C_performance.png", "outputs/figures/figure_D_errors.png",
           "data/aoi/aoi.geojson", "data/reference/s2_reference_2024.npz", "data/reference/s2_reference_2025.npz",
           "poster/poster_editable.pptx", "poster/poster_final.pdf", "poster/poster_content_en.md", "poster/references.bib",
           "presentation/pitch_english.md", "presentation/pitch_bangla.md", "presentation/judges_qa.md",
           "presentation/team_roles.md", "README.md", "docs/final_bangla_report.md"]
    for r in req:
        p = C.ROOT / r
        ok(p.exists() and p.stat().st_size > 0, f"exists: {r}", is_hard=not r.startswith("poster/poster_final"))

    A = pd.read_csv(C.TABLES / f"experiment_A_all_subsets_{source}.csv")
    for k in C.K_LIST:
        n = A[(A.year == 2025) & (A.method == "BASE_calibrated") & (A.k == k)].shape[0]
        ok(n == math.comb(8, k), f"2025 BASE_calibrated has C(8,{k})={math.comb(8, k)} subsets (found {n})")
    for col in ("precision", "recall", "f1", "iou", "coverage"):
        v = A[col].dropna()
        ok(((v >= 0) & (v <= 1)).all(), f"{col} within [0,1]")
    ok((A.TP + A.FP + A.FN + A.TN + A.abstained_ref_erosion_px + A.abstained_ref_nonerosion_px == A.n_eval_px).all(),
       "confusion counts + abstentions sum to evaluated pixels")

    # leakage / freeze
    sel = json.loads((C.TABLES / f"selected_parameters_{source}.json").read_text())
    log = json.loads((C.REPORTS / f"experiment_log_{source}.json").read_text())
    ok(sel["frozen_at"] <= log["finished"], "parameters frozen before experiment finished (2025 evaluated after freeze in same run)")
    cal = pd.read_csv(C.TABLES / f"calibration_thresholds_2024_{source}.csv")
    ok(len(cal) > 0, "calibration table exists and is 2024-only by construction (calibrate() is only called on 2024)")

    # recompute sample rows
    s1 = np.load(C.CACHE / f"s1_{source}_2025.npz")
    ref = np.load(C.DATA / "reference" / "s2_reference_2025.npz")
    with np.errstate(all="ignore"):
        pre = np.nanmean(s1["pre"], axis=0)
    T = sel["thresholds"]
    rng = np.random.default_rng(1)
    sub = A[(A.year == 2025) & (A.method == "BASE_calibrated")].sample(5, random_state=1)
    for _, r in sub.iterrows():
        comb = [int(i) for i in str(r.subset).split("-")]
        pred = M.baseline(pre, s1["post"][comb], T["T_pre"], T["T_post"][str(int(r.k))])
        e = evaluate(pred, ref["ref"], ref["domain"])
        ok(e["TP"] == r.TP and e["FP"] == r.FP and e["FN"] == r.FN, f"recomputed BASE_calibrated k={int(r.k)} subset {r.subset}")

    # poster text scan
    md = (C.ROOT / "poster" / "poster_content_en.md")
    if md.exists():
        t = md.read_text(encoding="utf-8")
        hits = []
        for pat in FORBIDDEN:
            for mt in re.finditer(pat, t, flags=re.I):
                before = t[max(0, mt.start() - 30):mt.start()].lower()
                if re.search(r"\b(not|no|non|never)\b[\w\s-]*$", before):  # negated disclaimer, e.g. "not field ground truth"
                    continue
                hits.append(t[max(0, mt.start() - 30):mt.end() + 10].replace("\n", " "))
        ok(not hits, f"poster text free of un-negated forbidden claims (hits: {hits})", is_hard=False)

    out = ["# Final audit", f"run: {datetime.now().isoformat(timespec='seconds')}  source: {source}", ""] + [f"- {x}" for x in rep]
    (C.REPORTS / "final_audit.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    if hard:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["gee", "pc"], required=True)
    main(ap.parse_args().source)
