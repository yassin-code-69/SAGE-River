"""SAGE-River v2 — quality-aware, erosion-sensitive mapping with prioritized review.

Implements docs/sage_river_v2_design.md (pre-registered). v1 code and results are untouched; v2 reads v1's frozen
parameters (selected_parameters_<tag>.json) and adds:
  * SAR-only map-date geometry (pre-event channel, bank buffer, distance to bank)
  * three classes: 2 = HIGH-CONFIDENCE EROSION, 1 = POSSIBLE EROSION (REVIEW), 0 = LIKELY STABLE
  * a patch-ranking model (logistic regression) trained ONLY on the validation year (2024)
  * a review simulation (oracle analyst) comparing prioritized vs random review at equal area budgets
The Sentinel-2 reference is used only for (i) training labels in 2024 and (ii) scoring — never as a test-time input.

Usage:  python sage_v2.py --tag gee              (reach from SAGE_REACH, default kurigram)
Outputs: outputs[/reaches/<reach>]/tables/v2_*_<tag>.csv|json
"""
import argparse
import itertools
import json
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import ndimage
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import config as C
import sage_methods as M
from experiment_runner import load, nearest_k
from metrics import evaluate

D_REVIEW_GRID = [100, 200, 300, 500, 750, 1000]
BUDGETS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50, 1.0]
N_RANDOM = 500
CHANNEL_MIN_PX = 10000   # 1 km2 at 10 m
BUFFER_PX = 3            # 30 m
FEATURES = ["mean_delta", "mean_vote_frac", "mean_pre_margin", "min_dist_bank", "log_area_ha", "touches_bank", "frac_v1conf"]
EIGHT = np.ones((3, 3))


# ------------------------------------------------------------------ map-date SAR geometry
def sar_geometry(pre, T_pre):
    low = np.isfinite(pre) & (pre < T_pre)
    lab, n = ndimage.label(low, structure=EIGHT)
    if n == 0:
        chan = np.zeros_like(low)
    else:
        sizes = ndimage.sum(low, lab, index=np.arange(1, n + 1))
        chan = np.isin(lab, np.flatnonzero(sizes >= CHANNEL_MIN_PX) + 1)
    buffer = ndimage.binary_dilation(chan, structure=EIGHT, iterations=BUFFER_PX)
    dist = ndimage.distance_transform_edt(~chan) * C.PIXEL
    return chan, buffer, dist


def params_for(sel, k):
    T = sel["thresholds"]
    p = nearest_k(sel["params_by_k"], k)
    delta = p["delta_AG"] if (k >= 2 and p.get("m_rule")) else p["delta_G"]
    m = None
    if k >= 2 and p.get("m_rule"):
        m = k if p["m_rule"] == "unanimous" else M.majority_m(k)
    return T["T_pre"], T["T_scene"], nearest_k(T["T_post"], k), m, delta, p["delta_G"]


def v2_classes(pre, post, sel, geom, dom, D_review):
    """Return class map (2 HC, 1 REVIEW, 0 STABLE, -2 outside domain/no data) and per-pixel evidence."""
    chan, buffer, dist = geom
    k = post.shape[0]
    T_pre, T_scene, T_post_k, m, delta, delta_G = params_for(sel, k)
    if m is not None:
        v1 = M.agreement(pre, post, T_pre, T_scene, m=m, delta=delta)
    else:
        v1 = M.gated(pre, post, T_pre, T_post_k, delta_G)
    v1_conf = v1 == 1
    votes_conf = np.sum(post < T_scene - delta, axis=0)
    votes_poss = np.sum(post < T_scene + delta, axis=0)
    with np.errstate(all="ignore"):
        post_mean = np.nanmean(post, axis=0) if k > 1 else post[0]
    valid = np.isfinite(pre) & np.isfinite(post_mean) & dom
    cand = (((pre > T_pre - delta) & (votes_poss >= 1)) | v1_conf) & valid
    lab, n = ndimage.label(cand, structure=EIGHT)
    ids = np.arange(1, n + 1)
    touches = np.zeros(n + 1, dtype=bool)
    mind = np.full(n + 1, np.inf)
    if n:
        touches[1:] = ndimage.maximum(buffer.astype(np.uint8), lab, index=ids) > 0
        mind[1:] = ndimage.minimum(dist, lab, index=ids)
    hc = v1_conf & cand & touches[lab]
    review = cand & ~hc & (mind[lab] <= D_review)
    cls = np.zeros(pre.shape, dtype=np.int8)
    cls[review] = 1
    cls[hc] = 2
    cls[~valid] = -2
    ev = {"delta": pre - post_mean, "vote_frac": votes_conf / k, "pre_margin": pre - T_pre, "dist": dist,
          "buffer": buffer, "v1_conf": v1_conf, "cand": cand, "cand_lab": lab, "cand_mind": mind, "v1": v1}
    return cls, ev


def review_patches(cls, ev, ref=None):
    """Connected REVIEW patches with map-date features (and evaluation-only targets if ref is given)."""
    rv = cls == 1
    lab, n = ndimage.label(rv, structure=EIGHT)
    if n == 0:
        return lab, pd.DataFrame(columns=["pid"] + FEATURES)
    ids = np.arange(1, n + 1)
    area_px = ndimage.sum(rv, lab, ids)
    df = pd.DataFrame({
        "pid": ids,
        "area_px": area_px,
        "mean_delta": ndimage.mean(np.nan_to_num(ev["delta"]), lab, ids),
        "mean_vote_frac": ndimage.mean(ev["vote_frac"], lab, ids),
        "mean_pre_margin": ndimage.mean(np.nan_to_num(ev["pre_margin"]), lab, ids),
        "min_dist_bank": ndimage.minimum(ev["dist"], lab, ids),
        "touches_bank": (ndimage.maximum(ev["buffer"].astype(np.uint8), lab, ids) > 0).astype(float),
        "frac_v1conf": ndimage.mean(ev["v1_conf"].astype(float), lab, ids),
    })
    df["log_area_ha"] = np.log10(df.area_px * 0.01)
    if ref is not None:
        pos = (ref == 1) & rv
        known = np.isin(ref, (0, 1)) & rv
        df["ero_px"] = ndimage.sum(pos, lab, ids)
        df["known_px"] = ndimage.sum(known, lab, ids)
        df["ero_frac"] = np.where(df.known_px > 0, df.ero_px / df.known_px.clip(lower=1), 0.0)
        df["target"] = (df.ero_frac >= 0.5).astype(int)
    return lab, df


# ------------------------------------------------------------------ calibration on the validation year
def calibrate_v2(D, sel):
    """D_review by the pre-registered 90 % rule, then the ranking model — validation year only."""
    pre, ref, dom = D["pre_comp"], D["ref"], D["domain"]
    T_pre = sel["thresholds"]["T_pre"]
    geom = sar_geometry(pre, T_pre)
    K = D["post"].shape[0]
    combs = [c for k in C.K_LIST if k <= K for c in itertools.combinations(range(K), k)]
    # D_review rule
    covered = {d: 0.0 for d in D_REVIEW_GRID}
    total = 0.0
    for comb in combs:
        cls, ev = v2_classes(pre, D["post"][list(comb)], sel, geom, dom, D_review=np.inf)
        target = (ref == 1) & ev["cand"] & (cls != 2)
        total += target.sum()
        md = ev["cand_mind"][ev["cand_lab"]]
        for d in D_REVIEW_GRID:
            covered[d] += (target & (md <= d)).sum()
    frac = {d: covered[d] / total if total else np.nan for d in D_REVIEW_GRID}
    D_review = next((d for d in D_REVIEW_GRID if frac[d] >= 0.90), D_REVIEW_GRID[-1])
    # ranking model
    rows = []
    for comb in combs:
        cls, ev = v2_classes(pre, D["post"][list(comb)], sel, geom, dom, D_review)
        _, df = review_patches(cls, ev, ref)
        df["k"] = len(comb)
        rows.append(df)
    tr = pd.concat(rows, ignore_index=True)
    tr = tr[tr.known_px > 0]
    scaler = StandardScaler().fit(tr[FEATURES].values)
    model = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000).fit(scaler.transform(tr[FEATURES].values), tr.target.values)
    cal = {"D_review_m": D_review, "D_review_coverage": {str(d): round(float(f), 4) for d, f in frac.items()},
           "features": FEATURES, "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(),
           "coef": model.coef_[0].tolist(), "intercept": float(model.intercept_[0]),
           "n_train_patches": int(len(tr)), "n_train_positive": int(tr.target.sum()),
           "train_year": int(D.get("year", 2024)), "frozen_at": datetime.now().isoformat(timespec="seconds")}
    return cal, geom


def score_patches(df, cal):
    if df.empty:
        return np.array([])
    X = (df[cal["features"]].values - np.array(cal["scaler_mean"])) / np.array(cal["scaler_scale"])
    z = X @ np.array(cal["coef"]) + cal["intercept"]
    return 1.0 / (1.0 + np.exp(-z))


# ------------------------------------------------------------------ review simulation
def simulate(cls, ev, ref, dom, cal, rng):
    """Return one row per budget for: prioritized v2, random v2 (mean/p05/p95), random review of v1 UNCERTAIN."""
    lab, df = review_patches(cls, ev, ref)
    known = np.isin(ref, (0, 1)) & dom
    ref_pos = (ref == 1) & known
    total_ref = ref_pos.sum()
    hc = (cls == 2) & known
    tp_hc = int((hc & ref_pos).sum())
    fp_hc = int((hc & (ref == 0)).sum())
    n_known = int(known.sum())
    stable_known = int(((cls == 0) & known).sum())
    review_area = df.area_px.values.astype(float) if len(df) else np.array([])
    review_ero = df.ero_px.values.astype(float) if len(df) else np.array([])
    tot_rev = review_area.sum()
    out = []

    def rec_at(order, b):
        if tot_rev == 0 or len(order) == 0:
            return 0.0, 0.0
        a = review_area[order]; e = review_ero[order]
        cum = np.cumsum(a)
        budget = b * tot_rev
        nfull = int(np.searchsorted(cum, budget, side="right"))
        rec = e[:nfull].sum()
        used = cum[nfull - 1] if nfull > 0 else 0.0
        if nfull < len(order) and budget > used:  # partial review of the next patch (area-proportional)
            rec += e[nfull] * (budget - used) / a[nfull]
        return float(rec), float(min(budget, tot_rev))

    pri = np.argsort(-score_patches(df, cal) + 1e-9 * np.arange(len(df))) if len(df) else np.array([], int)
    rand_orders = [rng.permutation(len(df)) for _ in range(N_RANDOM)] if len(df) else []
    # v1 UNCERTAIN patches (random order), budget in the same absolute ha as v2 review effort
    v1u = (ev["v1"] == -1) & dom
    lab1, n1 = ndimage.label(v1u, structure=EIGHT)
    if n1:
        ids1 = np.arange(1, n1 + 1)
        a1 = ndimage.sum(v1u, lab1, ids1).astype(float)
        e1 = ndimage.sum(v1u & ref_pos, lab1, ids1).astype(float)
    else:
        a1 = e1 = np.array([])
    for b in BUDGETS:
        rec_p, eff = rec_at(pri, b)
        rr = np.array([rec_at(o, b)[0] for o in rand_orders]) if rand_orders else np.array([0.0])
        # v1 random review with the same effort (px)
        r1 = []
        for _ in range(100 if n1 else 1):
            if not n1:
                r1.append(0.0); break
            o = rng.permutation(n1)
            cum = np.cumsum(a1[o]); nf = int(np.searchsorted(cum, eff, side="right"))
            val = e1[o][:nf].sum()
            used = cum[nf - 1] if nf > 0 else 0.0
            if nf < n1 and eff > used:
                val += e1[o][nf] * (eff - used) / a1[o][nf]
            r1.append(val)
        for name, rec in (("v2_prioritized", rec_p), ("v2_random_mean", rr.mean()), ("v2_random_p05", np.percentile(rr, 5)),
                          ("v2_random_p95", np.percentile(rr, 95)), ("v1_uncertain_random_mean", float(np.mean(r1)))):
            tp = tp_hc + rec
            fn = total_ref - tp
            f1 = 2 * tp / (2 * tp + fp_hc + fn) if (2 * tp + fp_hc + fn) > 0 else np.nan
            out.append({"budget_frac": b, "review_effort_ha": eff * 0.01, "strategy": name, "recovered_ha": rec * 0.01,
                        "hc_tp_ha": tp_hc * 0.01, "hc_false_ha": fp_hc * 0.01, "missed_ha": fn * 0.01,
                        "reference_erosion_ha": total_ref * 0.01, "review_area_ha": tot_rev * 0.01,
                        "review_erosion_ha": review_ero.sum() * 0.01, "stable_erosion_ha": float(((cls == 0) & ref_pos).sum() * 0.01),
                        "coverage_auto": (int(hc.sum()) + stable_known) / n_known if n_known else np.nan,
                        "f1_full_area": f1, "precision_full_area": tp / (tp + fp_hc) if (tp + fp_hc) else np.nan,
                        "recall_full_area": tp / total_ref if total_ref else np.nan})
    return out


def v2_pred_map(cls, reviewed=None):
    """Prediction map for metrics.evaluate at budget 0: HC = erosion, REVIEW/STABLE = non-erosion."""
    pred = np.zeros(cls.shape, dtype=np.int8)
    pred[cls == 2] = 1
    pred[cls == -2] = M.NODATA
    return pred


def run(tag):
    source = tag.split("_")[0]
    suffix = tag[len(source):]
    sel = json.loads((C.TABLES / f"selected_parameters_{tag}.json").read_text())
    rng = np.random.default_rng(C.RANDOM_SEED)
    V = load(source, 2024, suffix); V["year"] = 2024
    cal, geom24 = calibrate_v2(V, sel)
    (C.TABLES / f"v2_calibration_{tag}.json").write_text(json.dumps(cal, indent=1))
    print("v2 FROZEN:", json.dumps({k: cal[k] for k in ("D_review_m", "D_review_coverage", "coef", "intercept", "n_train_patches", "n_train_positive")}))
    rows_sim, rows_abl = [], []
    for year in (2024, 2025):
        D = V if year == 2024 else load(source, 2025, suffix)
        pre, ref, dom = D["pre_comp"], D["ref"], D["domain"]
        geom = geom24 if year == 2024 else sar_geometry(pre, sel["thresholds"]["T_pre"])
        K = D["post"].shape[0]
        sets = [("A", c) for k in C.K_LIST if k <= K for c in itertools.combinations(range(K), k)] + \
               [("B", tuple(range(k))) for k in C.K_CHRONO if k <= K]
        for exp, comb in sets:
            cls, ev = v2_classes(pre, D["post"][list(comb)], sel, geom, dom, cal["D_review_m"])
            meta = {"year": year, "tag": tag, "experiment": exp, "k": len(comb), "subset": "-".join(map(str, comb)),
                    "dates": ";".join(D["dates"][i] for i in comb), "role": ("calibration (in-sample)" if year == 2024 else
                                                                            ("EXPLORATORY" if C.REACH == "kurigram" else "INDEPENDENT TEST"))}
            for r in simulate(cls, ev, ref, dom, cal, rng):
                r.update(meta); rows_sim.append(r)
            e = evaluate(v2_pred_map(cls), ref, dom)
            e.update(meta); e.update({"method": "SAGE_v2_HC_only", "review_area_ha": float((cls == 1).sum() * 0.01),
                                      "stable_area_ha": float(((cls == 0) & dom).sum() * 0.01)})
            rows_abl.append(e)
    sim = pd.DataFrame(rows_sim)
    sim.to_csv(C.TABLES / f"v2_review_simulation_{tag}.csv", index=False)
    pd.DataFrame(rows_abl).to_csv(C.TABLES / f"v2_hc_only_metrics_{tag}.csv", index=False)
    summ = sim[sim.experiment == "A"].groupby(["year", "role", "k", "budget_frac", "strategy"]).agg(
        n_subsets=("recovered_ha", "size"), review_effort_ha=("review_effort_ha", "mean"), recovered_ha=("recovered_ha", "mean"),
        missed_ha=("missed_ha", "mean"), hc_false_ha=("hc_false_ha", "mean"), f1_full_area=("f1_full_area", "mean"),
        recall_full_area=("recall_full_area", "mean"), coverage_auto=("coverage_auto", "mean"),
        review_area_ha=("review_area_ha", "mean"), review_erosion_ha=("review_erosion_ha", "mean"),
        stable_erosion_ha=("stable_erosion_ha", "mean"), reference_erosion_ha=("reference_erosion_ha", "first")).reset_index()
    summ.to_csv(C.TABLES / f"v2_review_summary_{tag}.csv", index=False)
    print("done", C.REACH, tag)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="gee")
    run(ap.parse_args().tag)
