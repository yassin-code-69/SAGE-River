"""SAGE-River v2 reporting: ablation table + figures, from saved CSVs only (no recomputation of results).

  python v2_report.py tables     -> outputs/tables/v2_ablation_all_reaches.csv
  python v2_report.py charts     -> outputs/figures/figure_G_v2_ablation.png, figure_H_review_curve.png
  SAGE_REACH=<reach> python v2_report.py map   -> <reach outputs>/figures/figure_I_three_class_map.png
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

import config as C

TAG = "gee"
SIR = C.ROOT / "outputs" / "reaches" / "sirajganj"
# key: (outputs dir, label, file tag, evaluation year)
REACHES = {"kurigram": (C.ROOT / "outputs", "Kurigram 2025 — EXPLORATORY (design informed by it)", "gee", 2025),
           "sirajganj": (SIR, "Sirajganj–Kazipur 2025 — INDEPENDENT (local calibration; 12 ha reference)", "gee", 2025),
           "sirajganj_transfer2024": (SIR, "Sirajganj–Kazipur 2024 — INDEPENDENT TRANSFER (Kurigram parameters; 60 ha)", "gee_transferK", 2024)}
NAVY, TEAL, ORANGE = "#14284b", "#1a9e9e", "#e8590c"


def ablation_rows(reach, out_dir, year=2025, tag=TAG):
    t = out_dir / "tables"
    if not (t / f"v2_review_summary_{tag}.csv").exists():
        return []
    A = pd.read_csv(t / f"experiment_A_summary_{tag}.csv")
    S = pd.read_csv(t / f"v2_review_summary_{tag}.csv")
    H = pd.read_csv(t / f"v2_hc_only_metrics_{tag}.csv")
    rows = []
    for k in (2, 3, 6, 8):
        a = A[(A.year == year) & (A.k == k)].set_index("method")
        if a.empty:
            continue

        def add(label, method, f1, prec, rec, false_ha, missed_ha, cov, effort=0.0, f1_dec=np.nan, abst=np.nan):
            rows.append({"reach": reach, "year": year, "k": k, "step": label, "method": method, "f1_full_area": f1, "precision": prec,
                         "recall_full_area": rec, "false_erosion_ha": false_ha, "missed_erosion_ha": missed_ha,
                         "decision_coverage": cov, "review_effort_ha": effort, "f1_decided_px": f1_dec, "abstained_erosion_ha": abst})

        for lab, m in (("0 published σ⁰ thresholds (reference)", "BASE_published"), ("1a adapted baseline (class-separability T)", "BASE_calibrated"),
                       ("1b adapted baseline (F1-tuned T)", "BASE_F1tuned"), ("2a + agreement (majority)", "A_majority"),
                       ("2b + agreement (unanimous)", "A_unanimous")):
            if m in a.index:
                r = a.loc[m]
                add(lab, m, r.f1_mean, r.precision_mean, r.recall_mean, r.false_erosion_ha_mean, r.missed_erosion_ha_mean, 1.0)
        for lab, m in (("3 + confidence gating (G)", "G_gated"), ("4 SAGE-River v1 (A+G)", "AG_agree+gate")):
            if m in a.index:
                r = a.loc[m]
                add(lab, m, r.f1_abst_nonero_mean, r.precision_mean, r.recall_all_pixels_mean, r.false_erosion_ha_mean,
                    r.missed_erosion_ha_mean + r.abstained_erosion_ha_mean, r.coverage_mean, f1_dec=r.f1_mean, abst=r.abstained_erosion_ha_mean)
        s = S[(S.year == year) & (S.k == k)]
        h = H[(H.year == year) & (H.k == k) & (H.experiment == "A")]
        if len(h):
            add("5a SAGE-River v2, no review (HC only)", "v2_HC", h.f1.mean(), h.precision.mean(), h.recall.mean(), h.false_erosion_ha.mean(),
                h.missed_erosion_ha.mean(), float(s[(s.budget_frac == 0) & (s.strategy == "v2_prioritized")].coverage_auto.mean()))
        for b, lab in ((0.10, "5b v2 + 10 % prioritized review"), (0.20, "5c v2 + 20 % prioritized review"), (0.20, "5d v2 + 20 % RANDOM review")):
            strat = "v2_random_mean" if "RANDOM" in lab else "v2_prioritized"
            r = s[(s.budget_frac == b) & (s.strategy == strat)]
            if len(r):
                r = r.iloc[0]
                add(lab, strat, r.f1_full_area, np.nan, r.recall_full_area, r.hc_false_ha, r.missed_ha, r.coverage_auto, effort=r.review_effort_ha)
    return rows


def tables():
    rows = []
    for reach, (out_dir, label, tag, year) in REACHES.items():
        rows += [dict(r, evaluation=label, tag=tag) for r in ablation_rows(reach, out_dir, year, tag)]
    df = pd.DataFrame(rows)
    df.to_csv(C.ROOT / "outputs" / "tables" / "v2_ablation_all_reaches.csv", index=False)
    print(df[df.k.isin([3, 8])].round(3).to_string(index=False))


def charts():
    abl = pd.read_csv(C.ROOT / "outputs" / "tables" / "v2_ablation_all_reaches.csv")
    steps = ["1b adapted baseline (F1-tuned T)", "2b + agreement (unanimous)", "3 + confidence gating (G)", "4 SAGE-River v1 (A+G)",
             "5a SAGE-River v2, no review (HC only)", "5b v2 + 10 % prioritized review", "5c v2 + 20 % prioritized review",
             "5d v2 + 20 % RANDOM review"]
    short = ["Baseline\n(F1-tuned)", "+A\n(unanim.)", "+G", "v1\n(A+G)", "v2\nHC only", "v2 +10 %\nprioritized", "v2 +20 %\nprioritized", "v2 +20 %\nrandom"]
    cols = ["#a0522d", "#8e44ad", TEAL, "#e67e22", ORANGE, "#c0392b", "#8b0000", "#9e9e9e"]
    reaches = [r for r in REACHES if r in set(abl.reach)]
    fig, axes = plt.subplots(1, len(reaches), figsize=(8 * len(reaches), 5.6), dpi=200, squeeze=False)
    for ax, reach in zip(axes[0], reaches):
        d = abl[(abl.reach == reach)]
        x = np.arange(len(steps))
        for j, k in enumerate((3, 8)):
            vals = [d[(d.step == s) & (d.k == k)].f1_full_area.mean() for s in steps]
            ax.bar(x + (j - 0.5) * 0.4, vals, 0.38, color=cols, alpha=0.55 if k == 3 else 1.0, edgecolor="black", linewidth=0.4,
                   hatch="//" if k == 3 else "")
            for xi, v in zip(x, vals):
                if np.isfinite(v):
                    ax.text(xi + (j - 0.5) * 0.4, v + 0.01, f"{v:.2f}", ha="center", fontsize=7, rotation=90)
        ax.set_xticks(x); ax.set_xticklabels(short, fontsize=8)
        ax.set_ylim(0, 1.08); ax.set_ylabel("full-area F1")
        ax.set_title(REACHES[reach][1], loc="left", fontsize=11, color=NAVY)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(handles=[Patch(facecolor="white", edgecolor="black", hatch="//", label="k = 3 scenes"),
                           Patch(facecolor="grey", edgecolor="black", label="k = 8 scenes")], fontsize=8, loc="upper left")
    fig.suptitle("Ablation (mean over all scene subsets). Review = simulated oracle analyst on map-date-ranked patches.", fontsize=11, color=NAVY)
    fig.tight_layout()
    fig.savefig(C.ROOT / "outputs" / "figures" / "figure_G_v2_ablation.png", bbox_inches="tight")
    plt.close(fig)
    # review curves
    fig, axes = plt.subplots(len(reaches), 2, figsize=(13, 4.8 * len(reaches)), dpi=200, squeeze=False)
    for i, reach in enumerate(reaches):
        s = pd.read_csv(REACHES[reach][0] / "tables" / f"v2_review_summary_{REACHES[reach][2]}.csv")
        for j, k in enumerate((3, 8)):
            ax = axes[i, j]
            d = s[(s.year == REACHES[reach][3]) & (s.k == k)]
            if d.empty:
                continue
            g = {st: d[d.strategy == st].sort_values("budget_frac") for st in d.strategy.unique()}
            x = g["v2_prioritized"].review_effort_ha.values
            ax.fill_between(x, g["v2_random_p05"].recovered_ha.values, g["v2_random_p95"].recovered_ha.values, color="grey", alpha=0.25,
                            label="random review, 5–95 % of 500 orders")
            ax.plot(x, g["v2_random_mean"].recovered_ha.values, color="grey", lw=2, ls="--", label="random review (mean)")
            ax.plot(x, g["v1_uncertain_random_mean"].recovered_ha.values, color="#8e44ad", lw=1.6, ls=":", label="v1 UNCERTAIN, random review")
            ax.plot(x, g["v2_prioritized"].recovered_ha.values, color=ORANGE, lw=2.8, marker="o", label="v2 prioritized review")
            tot = g["v2_prioritized"].review_erosion_ha.iloc[0]
            ax.axhline(tot, color=ORANGE, lw=0.8, alpha=0.5)
            ax.text(x.max(), tot, f" erosion inside REVIEW = {tot:.1f} ha", fontsize=7, va="bottom", ha="right", color=ORANGE)
            ax.set_xlabel("review effort (ha of REVIEW class inspected)")
            ax.set_ylabel("reference erosion recovered (ha)")
            ax.set_title(f"{REACHES[reach][1]} · k = {k}", loc="left", fontsize=8.5, color=NAVY)
            ax.grid(alpha=0.3)
            if i == 0 and j == 0:
                ax.legend(fontsize=8, frameon=False, loc="lower right")
    fig.suptitle("Erosion recovered vs review effort (2025; mean over all C(8,k) subsets). Ranking uses map-date SAR features only.", fontsize=11, color=NAVY)
    fig.tight_layout()
    fig.savefig(C.ROOT / "outputs" / "figures" / "figure_H_review_curve.png", bbox_inches="tight")
    plt.close(fig)
    # compact poster version: k = 3, one panel per reach, x = % of REVIEW area, y = % of erosion inside REVIEW
    fig, axes = plt.subplots(1, len(reaches), figsize=(6.4 * len(reaches), 4.6), dpi=220, squeeze=False)
    for ax, reach in zip(axes[0], reaches):
        s = pd.read_csv(REACHES[reach][0] / "tables" / f"v2_review_summary_{REACHES[reach][2]}.csv")
        d = s[(s.year == REACHES[reach][3]) & (s.k == 3)]
        g = {st: d[d.strategy == st].sort_values("budget_frac") for st in d.strategy.unique()}
        x = 100 * g["v2_prioritized"].budget_frac.values
        tot = g["v2_prioritized"].review_erosion_ha.iloc[0]
        pct = lambda v: 100 * v / tot if tot else v
        ax.fill_between(x, pct(g["v2_random_p05"].recovered_ha.values), pct(g["v2_random_p95"].recovered_ha.values), color="grey", alpha=0.25,
                        label="random review (5–95 %)")
        ax.plot(x, pct(g["v2_random_mean"].recovered_ha.values), color="grey", lw=2, ls="--", label="random review (mean)")
        ax.plot(x, pct(g["v1_uncertain_random_mean"].recovered_ha.values), color="#8e44ad", lw=1.8, ls=":",
                label="v1 UNCERTAIN, random review (same ha)")
        ax.plot(x, pct(g["v2_prioritized"].recovered_ha.values), color=ORANGE, lw=3, marker="o", label="SAGE-River v2 prioritized")
        r20 = g["v2_prioritized"][g["v2_prioritized"].budget_frac == 0.2].recovered_ha.iloc[0]
        q20 = g["v2_random_mean"][g["v2_random_mean"].budget_frac == 0.2].recovered_ha.iloc[0]
        ax.annotate(f"20 % effort: {r20:.1f} ha vs {q20:.1f} ha random", (20, pct(r20)), xytext=(32, pct(r20) - 22), fontsize=9,
                    arrowprops=dict(arrowstyle="->", color=NAVY), color=NAVY)
        ax.set_xlabel("review effort (% of REVIEW area inspected)")
        ax.set_ylabel("% of erosion inside REVIEW recovered")
        ax.set_title(REACHES[reach][1].replace(" — ", "\n") + f"\nk = 3 · erosion inside REVIEW = {tot:.1f} ha", loc="left", fontsize=8.5, color=NAVY)
        ax.set_xlim(0, 100); ax.set_ylim(0, 105); ax.grid(alpha=0.3)
        ax.legend(fontsize=8, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(C.ROOT / "outputs" / "figures" / "figure_H_poster.png", bbox_inches="tight")
    plt.close(fig)


def three_class_map():
    import sage_v2 as V
    from experiment_runner import load
    sel = json.loads((C.TABLES / f"selected_parameters_{TAG}.json").read_text())
    cal = json.loads((C.TABLES / f"v2_calibration_{TAG}.json").read_text())
    D = load(TAG, 2025)
    pre, ref, dom = D["pre_comp"], D["ref"], D["domain"]
    geom = V.sar_geometry(pre, sel["thresholds"]["T_pre"])
    comb = (0, 1, 2)
    cls, ev = V.v2_classes(pre, D["post"][list(comb)], sel, geom, dom, cal["D_review_m"])
    lab, df = V.review_patches(cls, ev, ref)
    score = V.score_patches(df, cal)
    order = np.argsort(-score)
    rank = np.zeros(len(df) + 1)
    cum = np.cumsum(df.area_px.values[order]) / df.area_px.sum() if len(df) else []
    for pos, idx in enumerate(order):
        rank[df.pid.values[idx]] = cum[pos]  # cumulative review fraction when this patch is reached
    rmap = np.where(cls == 1, rank[lab], np.nan)
    g = C.ROOT  # noqa
    from aoi import load_grid
    grid = load_grid()
    ext = [0, grid.width * grid.res / 1000, 0, grid.height * grid.res / 1000]
    z = np.load(C.DATA / "reference" / "s2_reference_2025.npz")
    bg = np.nan_to_num(np.clip(z["rgb_post"] / 0.22, 0, 1), nan=1) * 0.55 + 0.45
    fig, ax = plt.subplots(figsize=(15, 7.6), dpi=200)
    ax.imshow(bg, extent=ext)
    tiers = np.full(cls.shape, np.nan)
    tiers[(cls == 1) & (rmap <= 0.10)] = 1
    tiers[(cls == 1) & (rmap > 0.10) & (rmap <= 0.30)] = 2
    tiers[(cls == 1) & (rmap > 0.30)] = 3
    tiers[cls == 2] = 0
    cmap = ListedColormap(["#d7191c", "#fdae61", "#ffe08a", "#c8d6e5"])
    ax.imshow(np.ma.masked_invalid(tiers), cmap=cmap, vmin=-0.5, vmax=3.5, extent=ext, interpolation="nearest")
    ax.contour(np.flipud((ref == 1).astype(float)), levels=[0.5], colors="cyan", linewidths=0.7, extent=ext, origin="lower")
    ax.set_xlabel("km (AOI-local)"); ax.set_ylabel("km")
    ax.set_title(f"SAGE-River v2, first three scenes ({D['dates'][0]} … {D['dates'][2]}) — {C.REACH} 2025", color=NAVY)
    ax.legend(handles=[Patch(color="#d7191c", label="HIGH-CONFIDENCE erosion"),
                       Patch(color="#fdae61", label="REVIEW — top 10 % priority"),
                       Patch(color="#ffe08a", label="REVIEW — 10–30 % priority"),
                       Patch(color="#c8d6e5", label="REVIEW — lower priority"),
                       Patch(edgecolor="cyan", facecolor="none", label="Sentinel-2 reference erosion (evaluation only)")],
              fontsize=8, loc="lower left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(C.FIGS / "figure_I_three_class_map.png", bbox_inches="tight")
    plt.close(fig)
    print("map written", C.FIGS / "figure_I_three_class_map.png")


if __name__ == "__main__":
    {"tables": tables, "charts": charts, "map": three_class_map}[sys.argv[1]]()
