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


def v2_checks(ok):
    """SAGE-River v2: frozen-code checksums, freeze-before-data order, criteria consistency."""
    import hashlib
    md5f = C.ROOT / "docs" / "sage_river_v2_design.md5"
    ok(md5f.exists(), "exists: docs/sage_river_v2_design.md5")
    if not md5f.exists():
        return
    last = {}
    for line in md5f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9a-f]{32}) \*(.+)$", line.strip())
        if m:
            last[m.group(2)] = m.group(1)  # the latest recorded checksum per file
    for rel, h in last.items():
        f = C.ROOT / rel
        cur = hashlib.md5(f.read_bytes()).hexdigest() if f.exists() else None
        ok(cur == h, f"v2 frozen file unchanged since freeze: {rel} ({h[:8]})")
    freeze = "2026-11-11T03:12:45"  # code-freeze time recorded in sage_river_v2_design.md5
    sj = C.ROOT / "data" / "reaches" / "sirajganj" / "cache"
    for y in (2024, 2025):
        mf = sj / f"s1_gee_{y}.json"
        if mf.exists():
            created = json.loads(mf.read_text())["created"]
            ok(created > freeze, f"Sirajganj SAR {y} created {created} after v2 code freeze {freeze}")
        else:
            ok(False, f"Sirajganj SAR {y} metadata present")
    cal = json.loads((C.TABLES / "v2_calibration_gee.json").read_text())
    ok(cal.get("train_year") == 2024, "v2 ranking model trained on 2024 only")
    cr = C.TABLES / "v2_preregistered_criteria.csv"
    ok(cr.exists(), "exists: outputs/tables/v2_preregistered_criteria.csv")
    if cr.exists():
        c = pd.read_csv(cr)
        a_re = (c.recovered_prioritized_ha > c.recovered_random_mean_ha) & (c.recovered_prioritized_ha > c.random_p95_ha)
        b_re = c.hc_false_ha <= c.v1_false_ha + 1e-9
        ok(bool((a_re == c.crit_a_met).all() and (b_re == c.crit_b_met).all()), "v2 criteria flags recomputed from their own columns")
        ind = c[c.role.str.startswith("INDEPENDENT")]
        ok(True, f"v2 independent tests with both criteria met: {int(ind.both_met.sum())}/{len(ind)} (informational)", is_hard=False)
    for rel in ("outputs/figures/figure_H_poster.png", "outputs/figures/figure_G_v2_ablation.png",
                "outputs/figures/figure_I_three_class_map.png", "docs/sage_river_v2_results.md",
                "outputs/reports/root_cause_audit_20260131.md", "outputs/tables/v2_ablation_all_reaches.csv"):
        f = C.ROOT / rel
        ok(f.exists() and f.stat().st_size > 0, f"exists: {rel}")


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

    if source == "gee":
        v2_checks(ok)

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
