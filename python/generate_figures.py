"""Poster figures from REAL outputs only (each figure checks that its input files exist).

Figure 0  study-area map                 outputs/figures/figure_0_study_area.png
Figure A  scene availability             (made by scene_analysis.py)
Figure B  sparse vs full-scene maps + reference overlay  figure_B_maps.png
Figure C  performance vs scene count     figure_C_performance.png
Figure D  error / uncertainty map        figure_D_errors.png
Figure E  chronological early mapping    figure_E_chronological.png
Usage: python generate_figures.py --source gee|pc
"""
import argparse
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

import config as C
import sage_methods as M
from aoi import aoi_props, load_grid

NAVY, TEAL, ORANGE, GREY = "#14284b", "#1a9e9e", "#e8590c", "#9e9e9e"
METHOD_STYLE = {
    "BASE_published": ("Baseline (published thresholds)", "#7f8c8d", "--", "s"),
    "BASE_calibrated": ("Baseline (2024-calibrated)", NAVY, "-", "o"),
    "BASE_F1tuned": ("Baseline (F1-tuned on 2024)", "#a0522d", ":", "P"),
    "A_majority": ("A: majority agreement", "#3d7cc9", "-", "^"),
    "A_unanimous": ("A: unanimous agreement", "#8e44ad", "-", "v"),
    "G_gated": ("G: confidence gating", TEAL, "-", "D"),
    "AG_agree+gate": ("SAGE-River A+G", ORANGE, "-", "*"),
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})


def extent():
    g = load_grid()
    xmin, ymin, xmax, ymax = g.bounds
    return [(xmin - xmin) / 1000, (xmax - xmin) / 1000, 0, (ymax - ymin) / 1000]


def rgb(img):
    return np.nan_to_num(np.clip(img / 0.22, 0, 1), nan=1.0)


def load_year(source, year):
    s1 = np.load(C.CACHE / f"s1_{source}_{year}.npz")
    meta = json.loads((C.CACHE / f"s1_{source}_{year}.json").read_text())
    ref = np.load(C.DATA / "reference" / f"s2_reference_{year}.npz")
    with np.errstate(all="ignore"):
        pre = np.nanmean(s1["pre"], axis=0)
    return pre, s1["post"], [d["date"] for d in meta["post"]], ref


def fig_C(source):
    df = pd.read_csv(C.TABLES / f"experiment_A_summary_{source}.csv")
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), dpi=200, sharex=True)
    panels = [("precision_mean", "precision_sd", "Precision (decided px)"), ("recall_mean", "recall_sd", "Recall (decided px)"),
              ("f1_mean", "f1_sd", "F1 (decided px)"), ("f1_abst_nonero_mean", "f1_abst_nonero_sd", "F1 if UNCERTAIN = non-erosion (full coverage)"),
              ("coverage_mean", None, "Decision coverage"), ("false_erosion_ha_mean", None, "False erosion area (ha, log scale)")]
    for year, ls_alpha in ((2025, 1.0),):
        d = df[df.year == year]
        for ax, (col, sd, title) in zip(axes.ravel(), panels):
            for m, (lab, colr, ls, mk) in METHOD_STYLE.items():
                dm = d[d.method == m].sort_values("k")
                if dm.empty:
                    continue
                ax.plot(dm.k, dm[col], ls=ls, color=colr, marker=mk, label=lab, lw=2, ms=7)
                if sd and dm[sd].notna().any():
                    ax.fill_between(dm.k, dm[col] - dm[sd].fillna(0), dm[col] + dm[sd].fillna(0), color=colr, alpha=0.10)
            ax.set_title(title, loc="left", fontsize=12, color=NAVY)
            ax.grid(alpha=0.3)
            ax.set_xticks(C.K_LIST)
            if col.startswith("false_erosion"):
                ax.set_yscale("log")
    for ax in axes[1]:
        ax.set_xlabel("number of post-monsoon Sentinel-1 scenes (k)")
    axes[0, 0].legend(fontsize=8.5, frameon=False, loc="lower right")
    fig.suptitle(f"Test monsoon 2025 — mean over all C(8,k) scene subsets (band = ±1 SD subset variability); source={source}",
                 fontsize=12, color=NAVY)
    fig.tight_layout()
    fig.savefig(C.FIGS / "figure_C_performance.png", bbox_inches="tight")
    fig.savefig(C.FIGS / "figure_C_performance.pdf", bbox_inches="tight")
    plt.close(fig)


def _cls_map(pred, ref, dom):
    """0 outside / 1 TN / 2 TP / 3 FP / 4 FN / 5 abstained / 6 ref uncertain."""
    out = np.zeros(pred.shape, dtype=np.int8)
    inside = dom
    out[inside & (ref == -1)] = 6
    ok = inside & np.isin(ref, (0, 1))
    out[ok & (pred == 0) & (ref == 0)] = 1
    out[ok & (pred == 1) & (ref == 1)] = 2
    out[ok & (pred == 1) & (ref == 0)] = 3
    out[ok & (pred == 0) & (ref == 1)] = 4
    out[ok & (pred == -1)] = 5
    return out


CMAP = ListedColormap(["#00000000", "#ffffff00", "#1b9e77", "#e8590c", "#7b2cbf", "#9e9e9e", "#00000000"])
LEG = [Patch(color="#1b9e77", label="correct erosion (TP)"), Patch(color="#e8590c", label="false erosion (FP)"),
       Patch(color="#7b2cbf", label="missed erosion (FN)"), Patch(color="#9e9e9e", label="UNCERTAIN (abstained)")]


def maps_for(source, year, comb, params):
    pre, post, dates, ref = load_year(source, year)
    from experiment_runner import nearest_k
    T = params["thresholds"]
    k = len(comb)
    p = nearest_k(params["params_by_k"], k)
    Tk = nearest_k(T["T_post"], k)
    sub = post[list(comb)]
    base = M.baseline(pre, sub, T["T_pre"], Tk)
    if k >= 2 and p["m_AG"] is not None:
        m = k if p.get("m_rule") == "unanimous" else M.majority_m(k)
        sage = M.agreement(pre, sub, T["T_pre"], T["T_scene"], m=m, delta=p["delta_AG"])
        lab = f"SAGE A+G (m={m} of {k}, δ={p['delta_AG']} dB)"
    else:
        sage = M.gated(pre, sub, T["T_pre"], Tk, p["delta_G"])
        lab = f"G only (δ={p['delta_G']} dB; k=1 has no agreement)"
    return base, sage, lab, ref["ref"], [dates[i] for i in comb]


def _crop(arr, ext_full, box):
    """Crop a full-AOI array to box=(x0,x1,y0,y1) in AOI-local km; returns array and its extent."""
    g = load_grid()
    x0, x1, y0, y1 = box
    c0, c1 = int(x0 * 1000 / g.res), int(x1 * 1000 / g.res)
    r0, r1 = int((g.height * g.res - y1 * 1000) / g.res), int((g.height * g.res - y0 * 1000) / g.res)
    return arr[r0:r1, c0:c1], [x0, x1, y0, y1]


def _overlay(ax, bg, pred, ref, dom, refm, box, title):
    b, e = _crop(rgb(bg), None, box)
    ax.imshow(b, extent=e)
    cm, _ = _crop(_cls_map(pred, ref, dom), None, box)
    ax.imshow(cm, cmap=CMAP, vmin=0, vmax=6, extent=e, interpolation="nearest")
    rr, _ = _crop((refm == 1).astype(float), None, box)
    ax.contour(np.flipud(rr), levels=[0.5], colors="cyan", linewidths=0.9, extent=e, origin="lower")
    ax.set_title(title, fontsize=10, color=NAVY)
    ax.set_xlabel("km (AOI-local)")


def tuned_baseline(pre, sub, params, k):
    from experiment_runner import nearest_k
    p = nearest_k(params["params_by_k"], k)
    return M.baseline(pre, sub, p["T_pre_F1tuned"], p["T_post_F1tuned"])


def fig_B_D(source):
    params = json.loads((C.TABLES / f"selected_parameters_{source}.json").read_text())
    z = np.load(C.DATA / "reference" / "s2_reference_2025.npz")
    dom, refm = z["domain"], z["ref"]
    pre, post, dates, _ = load_year(source, 2025)
    # ---- Figure B: zoom on the east-bank erosion hotspot; tuned baseline vs SAGE A+G
    box = (14.0, 20.0, 1.5, 10.5)
    cases = [((0,), "k=1: first scene"), ((0, 1, 2), "k=3: first three"), (tuple(range(8)), "k=8: all Nov–Jan")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 11.5), dpi=200)
    for j, (comb, title) in enumerate(cases):
        base, sage, lab, ref, ds = maps_for(source, 2025, comb, params)
        tb = tuned_baseline(pre, post[list(comb)], params, len(comb))
        span = ds[0] + (f" … {ds[-1]}" if len(ds) > 1 else "")
        _overlay(axes[0, j], z["rgb_post"], tb, ref, dom, refm, box, f"Baseline (F1-tuned T)\n{title} ({span})")
        _overlay(axes[1, j], z["rgb_post"], sage, ref, dom, refm, box, f"{lab}\n{title}")
    axes[0, 0].set_ylabel("km"); axes[1, 0].set_ylabel("km")
    fig.legend(handles=LEG + [Patch(edgecolor="cyan", facecolor="none", label="Sentinel-2 reference erosion outline")],
               loc="lower center", ncol=5, fontsize=10, frameon=False)
    fig.suptitle("Test monsoon 2025 — east-bank erosion hotspot (background: Sentinel-2 Feb–Mar 2026)", fontsize=12, color=NAVY)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(C.FIGS / "figure_B_maps.png", bbox_inches="tight")
    plt.close(fig)
    # ---- Figure D: one anomalous scene (31 Jan 2026) — why agreement matters
    i_bad = dates.index("2026-01-31")
    i_prev = dates.index("2026-01-19")
    pair = (i_prev, i_bad)
    boxw = (2.5, 9.0, 0.0, 11.0)
    fig, axes = plt.subplots(1, 4, figsize=(18, 7.2), dpi=200)
    sar, e = _crop(post[i_bad], None, boxw)
    axes[0].imshow(sar, vmin=-22, vmax=-2, cmap="gray", extent=e)
    axes[0].set_title("Sentinel-1 VV, 31 Jan 2026 (dB):\ndark field-shaped patches on the west floodplain", fontsize=10, color=NAVY)
    tb1 = tuned_baseline(pre, post[[i_bad]], params, 1)
    tb2 = tuned_baseline(pre, post[list(pair)], params, 2)
    _, sage2, lab2, ref, _ = maps_for(source, 2025, pair, params)
    def fp_ha(pred):
        return float(((pred == 1) & (ref == 0) & dom).sum() * 0.01)
    _overlay(axes[1], z["rgb_post"], tb1, ref, dom, refm, boxw, f"Baseline, this scene alone\nfalse erosion {fp_ha(tb1):.0f} ha (whole strip)")
    _overlay(axes[2], z["rgb_post"], tb2, ref, dom, refm, boxw, f"Baseline, 19 Jan + 31 Jan\nfalse erosion {fp_ha(tb2):.0f} ha")
    _overlay(axes[3], z["rgb_post"], sage2, ref, dom, refm, boxw, f"SAGE A+G, 19 Jan + 31 Jan\nfalse erosion {fp_ha(sage2):.1f} ha (grey = UNCERTAIN)")
    axes[0].set_ylabel("km")
    fig.legend(handles=LEG, loc="lower center", ncol=4, fontsize=10, frameon=False)
    fig.suptitle("Why temporal agreement matters: a single anomalous acquisition can create large false erosion (west floodplain, 2025 test)",
                 fontsize=12, color=NAVY)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(C.FIGS / "figure_D_errors.png", bbox_inches="tight")
    plt.close(fig)


def fig_C_poster(source):
    """Simplified Figure C for the poster (5 methods, 4 panels)."""
    df = pd.read_csv(C.TABLES / f"experiment_A_summary_{source}.csv")
    d = df[df.year == 2025]
    keep = ["BASE_published", "BASE_F1tuned", "BASE_calibrated", "A_unanimous", "AG_agree+gate"]
    panels = [("f1_mean", "f1_sd", "F1 on decided pixels"), ("f1_abst_nonero_mean", "f1_abst_nonero_sd", "F1, UNCERTAIN counted as non-erosion"),
              ("false_erosion_ha_mean", None, "False erosion area (ha, log)"), ("coverage_mean", None, "Decision coverage")]
    fig, axes = plt.subplots(1, 4, figsize=(20, 5.4), dpi=200)
    for ax, (col, sd, title) in zip(axes, panels):
        for m in keep:
            lab, colr, ls, mk = METHOD_STYLE[m]
            dm = d[d.method == m].sort_values("k")
            lw = 1.4 if m == "BASE_calibrated" else 2.6
            ax.plot(dm.k, dm[col], ls=ls, color=colr, marker=mk, lw=lw, ms=8, label=lab, alpha=0.6 if m == "BASE_calibrated" else 1)
            if sd and dm[sd].notna().any():
                ax.fill_between(dm.k, dm[col] - dm[sd].fillna(0), dm[col] + dm[sd].fillna(0), color=colr, alpha=0.10)
        ax.set_title(title, loc="left", fontsize=13, color=NAVY)
        ax.set_xticks(C.K_LIST)
        ax.set_xlabel("post-monsoon scenes (k)")
        ax.grid(alpha=0.3)
        if col.startswith("false"):
            ax.set_yscale("log")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=5, fontsize=11.5, frameon=False, bbox_to_anchor=(0.5, 1.07))
    fig.tight_layout()
    fig.savefig(C.FIGS / "figure_C_poster.png", bbox_inches="tight")
    plt.close(fig)


def fig_E(source):
    df = pd.read_csv(C.TABLES / f"experiment_B_chronological_{source}.csv")
    d = df[df.year == 2025]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), dpi=200, sharey=True)
    for ax, refname, title in ((axes[0], "cumulative_FebMar_next_year", "vs cumulative reference (Feb–Mar 2026)"),
                               (axes[1], "asof_mid_December", "vs as-of mid-December reference")):
        dd = d[d.reference == refname]
        for m in ("BASE_published", "BASE_F1tuned", "G_gated", "AG_agree+gate"):
            lab, colr, ls, mk = METHOD_STYLE[m]
            dm = dd[dd.method == m].sort_values("k")
            if dm.empty:
                continue
            ax.plot(dm.map_available_date, dm.f1, ls=ls, color=colr, marker=mk, lw=2.2, ms=8, label=lab + " (decided px)")
            if m in ("AG_agree+gate", "G_gated") and "f1_abst_nonero" in dm:
                ax.plot(dm.map_available_date, dm.f1_abst_nonero, ls="--", color=colr, marker=mk, lw=1.4, ms=6, alpha=0.75,
                        label=lab + " (UNCERTAIN = non-erosion)")
        ax.set_title(title, loc="left", color=NAVY)
        ax.set_xlabel("date the map could be produced (k = 1, 2, 3)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("F1 (decided px)")
    axes[0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(C.FIGS / "figure_E_chronological.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["gee", "pc"], required=True)
    a = ap.parse_args()
    fig_C(a.source)
    fig_C_poster(a.source)
    fig_B_D(a.source)
    fig_E(a.source)
    print("figures written")
