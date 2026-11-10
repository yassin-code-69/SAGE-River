"""SAGE-River experiments: calibration (2024 only), Experiment A (scene budgets), Experiment B (chronological).

Integrity rules implemented here
  * 2024 = validation year: thresholds, agreement level m and margin delta are chosen ONLY from 2024.
  * Parameters are frozen to outputs/tables/selected_parameters.json BEFORE any 2025 metric is computed.
  * 2025 = test year: evaluated once with frozen parameters.
  * All methods share the same scene pool, preprocessing, reference and evaluation domain.
  * Experiment A uses EXHAUSTIVE combinations of the post-monsoon pool (overlapping, not independent).
  * Experiment B uses only the first k acquisitions after 1 November (no future scenes).

Usage: python experiment_runner.py --source gee|pc
"""
import argparse
import itertools
import json
from datetime import datetime

import numpy as np
import pandas as pd

import config as C
import sage_methods as M
from metrics import evaluate

THR_GRID = np.round(np.arange(-24.0, -5.95, 0.05), 2)


def load(source, year, suffix=""):
    s1 = np.load(C.CACHE / f"s1_{source}_{year}{suffix}.npz")
    s1meta = json.loads((C.CACHE / f"s1_{source}_{year}{suffix}.json").read_text())
    ref = np.load(C.DATA / "reference" / f"s2_reference_{year}.npz")
    pre = s1["pre"]
    post = s1["post"]
    with np.errstate(all="ignore"):
        pre_comp = np.nanmean(pre, axis=0)  # F&F: temporal mean of filtered dB images
    dates = [d["date"] for d in s1meta["post"]]
    return {"pre_comp": pre_comp.astype("float32"), "post": post, "dates": dates, "ref": ref["ref"],
            "domain": ref["domain"], "cls_pre": ref["cls_pre"], "cls_post": ref["cls_post"],
            "cls_asof": ref["cls_asof"] if "cls_asof" in ref.files else None, "s1meta": s1meta}


def domain_view(D):
    """Restrict every per-pixel array to evaluation-domain pixels, shaped (1, N): identical metrics, ~10x faster.
    (Decision rules are pixel-wise, so cropping does not change any prediction inside the domain.)"""
    dom = D["domain"]
    V = dict(D)
    V["pre_comp"] = D["pre_comp"][dom][None, :]
    V["post"] = D["post"][:, dom][:, None, :]
    V["ref"] = D["ref"][dom][None, :]
    V["domain"] = np.ones((1, int(dom.sum())), dtype=bool)
    for k in ("cls_pre", "cls_post", "cls_asof"):
        V[k] = None if D[k] is None else D[k][dom][None, :]
    return V


# ---------------------------------------------------------------- threshold calibration (Youden J)
def youden_threshold(veg_vals, low_vals):
    """Threshold t maximising TPR - FPR for the rule 'vegetation if value > t'."""
    v = np.sort(veg_vals[np.isfinite(veg_vals)])
    s = np.sort(low_vals[np.isfinite(low_vals)])
    tpr = 1.0 - np.searchsorted(v, THR_GRID, side="right") / v.size
    fpr = 1.0 - np.searchsorted(s, THR_GRID, side="right") / s.size
    j = tpr - fpr
    i = int(np.argmax(j))
    return float(THR_GRID[i]), float(j[i]), int(v.size), int(s.size)


def calibrate(D, rng):
    """Class-separability thresholds from the 2024 validation year only."""
    rows = []
    veg_pre = D["cls_pre"] == 0
    low_pre = np.isin(D["cls_pre"], (1, 2))
    t, j, nv, ns = youden_threshold(D["pre_comp"][veg_pre], D["pre_comp"][low_pre])
    rows.append({"quantity": "T_pre (pre composite)", "k": "all-pre", "threshold_db": t, "youden_J": j, "n_veg": nv, "n_sandwater": ns})
    T = {"T_pre": t, "T_post": {}}
    veg_post = D["cls_post"] == 0
    low_post = np.isin(D["cls_post"], (1, 2))
    idx_v = np.flatnonzero(veg_post.ravel())
    idx_l = np.flatnonzero(low_post.ravel())
    idx_v = rng.choice(idx_v, size=min(60000, idx_v.size), replace=False)
    idx_l = rng.choice(idx_l, size=min(60000, idx_l.size), replace=False)
    K = D["post"].shape[0]
    flat = D["post"].reshape(K, -1)
    for k in C.K_LIST:
        if k > K:
            continue
        vv, ll = [], []
        for comb in itertools.combinations(range(K), k):
            with np.errstate(all="ignore"):
                comp = np.nanmean(flat[list(comb)], axis=0)
            vv.append(comp[idx_v]); ll.append(comp[idx_l])
        t, j, nv, ns = youden_threshold(np.concatenate(vv), np.concatenate(ll))
        T["T_post"][k] = t
        rows.append({"quantity": "T_post (k-scene composite)", "k": k, "threshold_db": t, "youden_J": j, "n_veg": nv, "n_sandwater": ns})
    T["T_scene"] = T["T_post"][1]
    return T, pd.DataFrame(rows)


def nearest_k(d, k):
    """Value calibrated for k, or — if the validation pool had fewer than k scenes — for the largest k' < k.
    (Documented fallback: e.g. a 6-scene 2024 pool provides no k=8 calibration.)"""
    keys = sorted(int(x) for x in d.keys())
    if k in keys:
        return d[k] if k in d else d[str(k)]
    kk = max(x for x in keys if x <= k)
    return d[kk] if kk in d else d[str(kk)]


# ---------------------------------------------------------------- method evaluation
def run_methods(D, comb, T, params, include_pub=True):
    pre = D["pre_comp"]
    post = D["post"][list(comb)]
    k = len(comb)
    ref, dom = D["ref"], D["domain"]
    res = []

    def add(name, pred, **kw):
        r = evaluate(pred, ref, dom)
        r.update({"method": name, "k": k, "subset": "-".join(str(i) for i in comb), **kw})
        res.append(r)

    if include_pub:
        add("BASE_published", M.baseline(pre, post, C.FF["T_6mo"], C.FF["T_1mo"]), T_pre=C.FF["T_6mo"], T_post=C.FF["T_1mo"])
    Tp, Tk, Ts = T["T_pre"], nearest_k(T["T_post"], k), T["T_scene"]
    add("BASE_calibrated", M.baseline(pre, post, Tp, Tk), T_pre=Tp, T_post=Tk)
    if k >= 2:
        add("A_majority", M.agreement(pre, post, Tp, Ts, m=M.majority_m(k)), m=M.majority_m(k), T_pre=Tp, T_post=Ts)
        if k > 2:
            add("A_unanimous", M.agreement(pre, post, Tp, Ts, m=k), m=k, T_pre=Tp, T_post=Ts)
    if params is not None:
        p = nearest_k(params, k)
        if "T_pre_F1tuned" in p:
            add("BASE_F1tuned", M.baseline(pre, post, p["T_pre_F1tuned"], p["T_post_F1tuned"]),
                T_pre=p["T_pre_F1tuned"], T_post=p["T_post_F1tuned"])
        add("G_gated", M.gated(pre, post, Tp, Tk, p["delta_G"]), delta=p["delta_G"], T_pre=Tp, T_post=Tk)
        if k >= 2 and p["m_AG"] is not None:
            # m is chosen on 2024 as a RULE (majority or unanimous) and transferred as that rule to other k
            m_rule = p.get("m_rule", "majority")
            m = k if m_rule == "unanimous" else M.majority_m(k)
            add("AG_agree+gate", M.agreement(pre, post, Tp, Ts, m=m, delta=p["delta_AG"]),
                m=m, m_rule=m_rule, delta=p["delta_AG"], T_pre=Tp, T_post=Ts)
    return res


def select_parameters(D, T):
    """Grid search on 2024 ONLY. Rule (pre-registered in config.py): maximise mean F1 on decided pixels
    over all subsets of size k, subject to mean decision coverage >= COVERAGE_MIN."""
    K = D["post"].shape[0]
    pre, ref, dom = D["pre_comp"], D["ref"], D["domain"]
    rows, params = [], {}
    for k in C.K_LIST:
        if k > K:
            continue
        combs = list(itertools.combinations(range(K), k))
        Tp, Tk, Ts = T["T_pre"], T["T_post"][k], T["T_scene"]
        best_g = (None, -1)
        for d in C.DELTAS:
            f1s, covs = [], []
            for comb in combs:
                r = evaluate(M.gated(pre, D["post"][list(comb)], Tp, Tk, d), ref, dom)
                f1s.append(r["f1"]); covs.append(r["coverage"])
            mf, mc = float(np.nanmean(f1s)), float(np.mean(covs))
            rows.append({"k": k, "component": "G", "m": None, "delta": d, "mean_f1": mf, "mean_coverage": mc})
            if mc >= C.COVERAGE_MIN and mf > best_g[1]:
                best_g = (d, mf)
        best_ag = (None, None, -1)
        if k >= 2:
            ms = sorted({M.majority_m(k), k})
            for m in ms:
                for d in C.DELTAS:
                    f1s, covs = [], []
                    for comb in combs:
                        r = evaluate(M.agreement(pre, D["post"][list(comb)], Tp, Ts, m=m, delta=d), ref, dom)
                        f1s.append(r["f1"]); covs.append(r["coverage"])
                    mf, mc = float(np.nanmean(f1s)), float(np.mean(covs))
                    rule = "majority" if m == M.majority_m(k) else "unanimous"
                    rows.append({"k": k, "component": "AG", "m": m, "m_rule": rule, "delta": d, "mean_f1": mf, "mean_coverage": mc})
                    if mc >= C.COVERAGE_MIN and mf > best_ag[2]:
                        best_ag = (m, d, mf, rule)
        # Fairness control: give the BASELINE the same advantage SAGE gets (erosion-F1 tuning on 2024).
        # 2-D grid of threshold offsets around the class-separability thresholds.
        best_b = (Tp, Tk, -1)
        for dp in np.arange(-2.0, 2.01, 0.5):
            for dq in np.arange(-3.0, 3.01, 0.5):
                f1s = [evaluate(M.baseline(pre, D["post"][list(comb)], Tp + dp, Tk + dq), ref, dom)["f1"] for comb in combs]
                mf = float(np.nanmean(f1s))
                rows.append({"k": k, "component": "BASE_F1tuned", "m": None, "delta": None, "T_pre": round(Tp + dp, 2),
                             "T_post": round(Tk + dq, 2), "mean_f1": mf, "mean_coverage": 1.0})
                if mf > best_b[2]:
                    best_b = (round(float(Tp + dp), 2), round(float(Tk + dq), 2), mf)
        params[str(k)] = {"delta_G": best_g[0] if best_g[0] is not None else 0.0,
                          "m_AG": best_ag[0], "m_rule": best_ag[3] if len(best_ag) > 3 else None,
                          "delta_AG": best_ag[1] if best_ag[1] is not None else 0.0,
                          "T_pre_F1tuned": best_b[0], "T_post_F1tuned": best_b[1],
                          "calibrated_on_k": k}
    return params, pd.DataFrame(rows)


def experiment_A(D, T, params, year, source):
    K = D["post"].shape[0]
    rows = []
    for k in C.K_LIST:
        if k > K:
            continue
        for comb in itertools.combinations(range(K), k):
            for r in run_methods(D, comb, T, params):
                r.update({"year": year, "source": source, "dates": ";".join(D["dates"][i] for i in comb)})
                rows.append(r)
    return pd.DataFrame(rows)


def experiment_B(D, T, params, year, source):
    rows = []
    ref_asof = None
    if D["cls_asof"] is not None:
        ref_asof = np.full(D["ref"].shape, -1, dtype=np.int8)
        ref_asof[D["ref"] == 0] = 0
        ref_asof[(D["ref"] == 1) & np.isin(D["cls_asof"], (1, 2))] = 1  # eroded AND already sand/water by mid-Dec
    for k in C.K_CHRONO:
        comb = tuple(range(k))
        map_date = D["dates"][k - 1]
        for r in run_methods(D, comb, T, params):
            r.update({"year": year, "source": source, "map_available_date": map_date, "reference": "cumulative_FebMar_next_year",
                      "dates": ";".join(D["dates"][:k])})
            rows.append(r)
        if ref_asof is not None:
            D2 = dict(D)
            D2["ref"] = ref_asof
            for r in run_methods(D2, comb, T, params):
                r.update({"year": year, "source": source, "map_available_date": map_date, "reference": "asof_mid_December",
                          "dates": ";".join(D["dates"][:k])})
                rows.append(r)
    return pd.DataFrame(rows)


def add_derived(df):
    """Full-coverage scores for abstaining methods, computed from the saved confusion counts:
    *_abst_nonero : UNCERTAIN treated as non-erosion (conservative map)
    *_abst_ero    : UNCERTAIN treated as erosion (liberal map)."""
    df = df.copy()
    tp, fp, fn = df.TP, df.FP, df.FN
    ap, an = df.abstained_ref_erosion_px, df.abstained_ref_nonerosion_px
    df["f1_abst_nonero"] = 2 * tp / (2 * tp + fp + fn + ap)
    df["iou_abst_nonero"] = tp / (tp + fp + fn + ap)
    df["recall_abst_nonero"] = tp / (tp + fn + ap)
    df["f1_abst_ero"] = 2 * (tp + ap) / (2 * (tp + ap) + fp + an + fn)
    df["precision_abst_ero"] = (tp + ap) / (tp + ap + fp + an)
    return df


def summarise(df):
    df = add_derived(df)
    keys = ["year", "source", "method", "k"]
    agg = df.groupby(keys).agg(
        n_subsets=("f1", "size"),
        f1_mean=("f1", "mean"), f1_median=("f1", "median"), f1_sd=("f1", "std"), f1_min=("f1", "min"), f1_max=("f1", "max"),
        precision_mean=("precision", "mean"), precision_sd=("precision", "std"),
        recall_mean=("recall", "mean"), recall_sd=("recall", "std"),
        iou_mean=("iou", "mean"), iou_sd=("iou", "std"),
        coverage_mean=("coverage", "mean"), uncertain_pct_mean=("uncertain_pct", "mean"),
        false_erosion_ha_mean=("false_erosion_ha", "mean"), missed_erosion_ha_mean=("missed_erosion_ha", "mean"),
        abstained_erosion_ha_mean=("abstained_erosion_ha", "mean"), recall_all_pixels_mean=("recall_all_pixels", "mean"),
        reference_erosion_ha=("reference_erosion_ha", "first"),
        f1_abst_nonero_mean=("f1_abst_nonero", "mean"), f1_abst_nonero_sd=("f1_abst_nonero", "std"),
        iou_abst_nonero_mean=("iou_abst_nonero", "mean"),
        f1_abst_ero_mean=("f1_abst_ero", "mean"), precision_abst_ero_mean=("precision_abst_ero", "mean"),
    ).reset_index()
    return agg


def resummarise(tag):
    """Rebuild summary tables from the saved per-subset CSV (no recomputation of maps)."""
    A = pd.read_csv(C.TABLES / f"experiment_A_all_subsets_{tag}.csv")
    summarise(A).to_csv(C.TABLES / f"experiment_A_summary_{tag}.csv", index=False)
    B = add_derived(pd.read_csv(C.TABLES / f"experiment_B_chronological_{tag}.csv"))
    B.to_csv(C.TABLES / f"experiment_B_chronological_{tag}.csv", index=False)


def main(source, filt="circle7"):
    suffix = "" if filt == "circle7" else f"_{filt}"
    tag = source + suffix
    rng = np.random.default_rng(C.RANDOM_SEED)
    log = {"started": datetime.now().isoformat(timespec="seconds"), "source": source}
    # ---------------- validation year
    Vfull = load(source, 2024, suffix)
    T, cal = calibrate(Vfull, rng)  # class samples from the whole AOI (2024 only)
    cal.to_csv(C.TABLES / f"calibration_thresholds_2024_{tag}.csv", index=False)
    V = domain_view(Vfull)
    log["pool_sizes"] = {"2024": int(Vfull["post"].shape[0])}
    params, grid = select_parameters(V, T)
    grid.to_csv(C.TABLES / f"parameter_selection_2024_{tag}.csv", index=False)
    frozen = {"source": source, "filter": filt, "thresholds": {"T_pre": T["T_pre"], "T_post": {str(k): v for k, v in T["T_post"].items()},
                                               "T_scene": T["T_scene"]},
              "published": {"T_pre": C.FF["T_6mo"], "T_post": C.FF["T_1mo"]},
              "params_by_k": params, "selection_rule": f"max mean F1 (decided px) s.t. mean coverage >= {C.COVERAGE_MIN} on 2024",
              "frozen_at": datetime.now().isoformat(timespec="seconds")}
    (C.TABLES / f"selected_parameters_{tag}.json").write_text(json.dumps(frozen, indent=1))
    print("FROZEN parameters:", json.dumps(frozen, indent=1))
    # ---------------- run both years with frozen parameters
    allA, allB = [], []
    for year in (2024, 2025):
        if year == 2024:
            D = V
        else:
            D25 = load(source, 2025, suffix)
            log["pool_sizes"]["2025"] = int(D25["post"].shape[0])
            D = domain_view(D25)
            del D25
        A = experiment_A(D, T, params, year, source)
        B = experiment_B(D, T, params, year, source)
        allA.append(A); allB.append(B)
    A = pd.concat(allA); B = pd.concat(allB)
    A.to_csv(C.TABLES / f"experiment_A_all_subsets_{tag}.csv", index=False)
    summarise(A).to_csv(C.TABLES / f"experiment_A_summary_{tag}.csv", index=False)
    B.to_csv(C.TABLES / f"experiment_B_chronological_{tag}.csv", index=False)
    log["finished"] = datetime.now().isoformat(timespec="seconds")
    (C.REPORTS / f"experiment_log_{tag}.json").write_text(json.dumps(log, indent=1))
    print("done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["gee", "pc"], required=True)
    ap.add_argument("--filter", default="circle7", choices=["circle7", "square7"])
    a = ap.parse_args()
    main(a.source, a.filter)
