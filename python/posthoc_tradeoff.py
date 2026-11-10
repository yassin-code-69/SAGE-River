"""Post-hoc trade-off analysis (RQ3): F1 on decided pixels vs decision coverage for every delta (and m).

* 2024 rows come from the validation grid used for selection (parameter_selection_2024_<tag>.csv).
* 2025 rows are computed here AFTER parameters were frozen, for every delta/m — labelled POST-HOC; they were
  never used to choose anything. The frozen choice is marked in the figure.
Outputs: outputs/tables/posthoc_tradeoff_2025_<tag>.csv, outputs/figures/figure_F_tradeoff.png
Usage: python posthoc_tradeoff.py --tag pc
"""
import argparse
import itertools
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C
import sage_methods as M
from experiment_runner import domain_view, load, nearest_k
from metrics import evaluate


def main(tag):
    source = tag.split("_")[0]
    suffix = tag[len(source):]
    sel = json.loads((C.TABLES / f"selected_parameters_{tag}.json").read_text())
    T = sel["thresholds"]
    D = domain_view(load(source, 2025, suffix))
    K = D["post"].shape[0]
    rows = []
    for k in (1, 3, 8):
        if k > K:
            continue
        combs = list(itertools.combinations(range(K), k))
        Tp, Tk, Ts = T["T_pre"], nearest_k(T["T_post"], k), T["T_scene"]
        for d in C.DELTAS:
            rs = [evaluate(M.gated(D["pre_comp"], D["post"][list(c)], Tp, Tk, d), D["ref"], D["domain"]) for c in combs]
            rows.append({"k": k, "component": "G", "m_rule": None, "delta": d, "mean_f1": np.nanmean([r["f1"] for r in rs]),
                         "mean_precision": np.nanmean([r["precision"] for r in rs]), "mean_recall": np.nanmean([r["recall"] for r in rs]),
                         "mean_coverage": np.mean([r["coverage"] for r in rs])})
            if k >= 2:
                for rule in ("majority", "unanimous"):
                    m = k if rule == "unanimous" else M.majority_m(k)
                    rs = [evaluate(M.agreement(D["pre_comp"], D["post"][list(c)], Tp, Ts, m=m, delta=d), D["ref"], D["domain"]) for c in combs]
                    rows.append({"k": k, "component": "AG", "m_rule": rule, "delta": d, "mean_f1": np.nanmean([r["f1"] for r in rs]),
                                 "mean_precision": np.nanmean([r["precision"] for r in rs]),
                                 "mean_recall": np.nanmean([r["recall"] for r in rs]), "mean_coverage": np.mean([r["coverage"] for r in rs])})
    post = pd.DataFrame(rows)
    post.insert(0, "note", "POST-HOC on 2025 test; not used for selection")
    post.to_csv(C.TABLES / f"posthoc_tradeoff_2025_{tag}.csv", index=False)
    val = pd.read_csv(C.TABLES / f"parameter_selection_2024_{tag}.csv")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=200, sharey=True)
    for ax, k in zip(axes, (1, 3, 8)):
        kv = k if k in set(val.k) else max(x for x in set(val.k) if x <= k)
        p = nearest_k(sel["params_by_k"], k)
        for comp, rule, col, lab in (("G", None, "#1a9e9e", "G gating"), ("AG", "majority", "#e8590c", "A+G majority"),
                                     ("AG", "unanimous", "#8e44ad", "A+G unanimous")):
            for df, ls, yl in ((val[val.k == kv], "--", f"2024 val (k={kv})"), (post[post.k == k], "-", "2025 test (post-hoc)")):
                d = df[df.component == comp]
                if rule is not None:
                    d = d[d.m_rule == rule]
                if d.empty:
                    continue
                d = d.sort_values("delta")
                ax.plot(d.mean_coverage, d.mean_f1, ls=ls, marker="o", color=col, label=f"{lab} — {yl}", lw=1.8, ms=4)
                for _, r in d.iterrows():
                    if ls == "-":
                        ax.annotate(f"δ={r.delta:g}", (r.mean_coverage, r.mean_f1), fontsize=6, color=col, xytext=(2, 2), textcoords="offset points")
        # frozen choice on 2025 test
        dG = post[(post.k == k) & (post.component == "G") & (post.delta == p["delta_G"])]
        if not dG.empty:
            ax.scatter(dG.mean_coverage, dG.mean_f1, s=160, facecolors="none", edgecolors="black", lw=2, zorder=5, label="frozen G choice")
        if k >= 2 and p.get("m_rule"):
            dA = post[(post.k == k) & (post.component == "AG") & (post.m_rule == p["m_rule"]) & (post.delta == p["delta_AG"])]
            ax.scatter(dA.mean_coverage, dA.mean_f1, s=220, marker="*", facecolors="none", edgecolors="black", lw=1.5, zorder=5,
                       label="frozen A+G choice")
        ax.axvline(C.COVERAGE_MIN, color="grey", ls=":", lw=1)
        ax.set_title(f"k = {k} scenes", loc="left", color="#14284b")
        ax.set_xlabel("decision coverage (fraction of pixels decided)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("F1 on decided pixels")
    axes[0].legend(fontsize=6.5, frameon=False, loc="lower left")
    fig.suptitle("Abstention trade-off: wider δ → higher F1 on decided pixels but lower coverage (dotted line = 90 % coverage rule)",
                 fontsize=11, color="#14284b")
    fig.tight_layout()
    fig.savefig(C.FIGS / "figure_F_tradeoff.png", bbox_inches="tight")
    plt.close(fig)
    print(post.round(3).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="pc")
    main(ap.parse_args().tag)
