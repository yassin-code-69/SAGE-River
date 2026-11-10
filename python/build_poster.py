"""Build the editable 48 x 48 in (4 ft x 4 ft) poster (PPTX) from REAL outputs.

Numbers are read from outputs/tables/*.csv; interpretive sentences come from poster/findings.json (written by hand
after the results were inspected). Missing inputs are shown as explicit placeholders, never invented.
Usage: python build_poster.py --source gee|pc [--figdir outputs/figures]
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import config as C
from aoi import aoi_props
from poster_lib import (CYAN_LIGHT, DARK, GREY, LIGHT, NAVY, ORANGE, TEAL, WHITE, RGBColor, bullets, callout, caption,
                        fit_picture, line_chart, new_poster, picture, rect, section, table, text)

POSTER = C.ROOT / "poster"
ASSETS = POSTER / "template_assets"
W_IN, H_IN = 48, 48
AUTHOR_LINE = "Yassin Bhuyan Alindo  [+ team members]  ·  Department of CSE, [University]  ·  alindobhuyan60@gmail.com"
CORRESPONDING = "Corresponding author: Yassin Bhuyan Alindo · alindobhuyan60@gmail.com"

M_LABEL = {"BASE_published": "Baseline (published T)", "BASE_calibrated": "Baseline (calibrated T)",
           "BASE_F1tuned": "Baseline (F1-tuned T)", "A_majority": "A: majority", "A_unanimous": "A: unanimous",
           "G_gated": "G: gating", "AG_agree+gate": "SAGE-River A+G"}
COL_X = (0.5, 14.15, 29.4)
COL_W = (13.2, 14.8, 18.1)
TOP = 7.05
GAP = 0.3


def f2(v, nd=2):
    return "–" if v is None or (isinstance(v, float) and pd.isna(v)) else f"{v:.{nd}f}"


def load(source):
    R = {"source": source}
    t = C.TABLES
    R["wc"] = pd.read_csv(t / "sentinel1_window_counts.csv")
    R["A"] = pd.read_csv(t / f"experiment_A_summary_{source}.csv")
    R["B"] = pd.read_csv(t / f"experiment_B_chronological_{source}.csv")
    R["sel"] = json.loads((t / f"selected_parameters_{source}.json").read_text())
    fj = POSTER / "findings.json"
    R["F"] = json.loads(fj.read_text(encoding="utf-8")) if fj.exists() else None
    pa = t / "reference_point_agreement_2025.csv"
    R["pts"] = pd.read_csv(pa) if pa.exists() else None
    sp = C.ROOT / "outputs" / "reaches" / "sirajganj" / "tables" / "reference_point_agreement_2025.csv"
    R["pts_sir"] = pd.read_csv(sp) if sp.exists() else None
    cr = C.ROOT / "outputs" / "tables" / "v2_preregistered_criteria.csv"
    R["crit"] = pd.read_csv(cr) if (cr.exists() and source == "gee") else None
    return R


def stack(col_heights):
    """Section y positions for the given heights, starting at TOP with GAP spacing."""
    ys, y = [], TOP
    for h in col_heights:
        ys.append(y)
        y += h + GAP
    return ys


def header(s, R):
    rect(s, 0, 0, W_IN, 5.3, fill=NAVY)
    rect(s, 0, 5.3, W_IN, 0.14, fill=TEAL)
    if (ASSETS / "Picture_31.png").exists():
        picture(s, ASSETS / "Picture_31.png", 0.6, 0.75, h=3.8)
    if (ASSETS / "Picture_30.png").exists():  # official event logo from the organiser's template, on a white card
        rect(s, 42.3, 0.6, 5.2, 4.1, fill=WHITE)
        picture(s, ASSETS / "Picture_30.png", 42.4, -0.05, h=5.3)
    text(s, 4.9, 0.35, 37.2, 0.7, [[("IEEE BUBT ACADEMIC RESEARCH SHOWCASE 2026  ·  13–14 NOVEMBER  ·  TRACK 1: INTELLIGENT COMPUTING, AI & DATA TECHNOLOGIES",
                                     {"color": RGBColor(0x7F, 0xD8, 0xD8), "bold": True})]], size=23)
    text(s, 4.9, 1.0, 37.2, 1.55, [[("How Many Sentinel-1 Scenes Are Enough?", {"color": WHITE, "bold": True})]], size=86)
    text(s, 4.9, 2.55, 37.2, 1.4, [[("Scene-Count Sensitivity, Agreement-Gated Reliability and Prioritized Review of Post-Monsoon "
                                     "Riverbank Erosion Maps — Jamuna River, Bangladesh", {"color": WHITE})]], size=35)
    text(s, 4.9, 4.2, 37.2, 0.9, [[(AUTHOR_LINE, {"color": RGBColor(0xDD, 0xE6, 0xF0)})]], size=27)


def ribbon(s, R):
    rect(s, 0.5, 5.7, 47.0, 1.1, fill=CYAN_LIGHT, line=TEAL, line_w=2.5)
    msg = R["F"]["takeaway"] if R["F"] else "Key message pending verified results"
    text(s, 0.8, 5.72, 46.4, 1.06, [[("KEY MESSAGE  ", {"bold": True, "color": TEAL}), (msg, {"bold": True, "color": NAVY})]],
         size=28, anchor=MSO_ANCHOR.MIDDLE)


def col1(s, R):
    x, w = COL_X[0], COL_W[0]
    F = R["F"]
    hs = [8.3, 6.5, 10.9, 5.5, 6.6]
    ys = stack(hs)
    cx, cy, cw = section(s, x, ys[0], w, hs[0], "01", "Abstract")
    text(s, cx, cy, cw, hs[0] - 1.2, F["abstract"] if F else "Abstract pending verified results.", size=24.5, line_spacing=1.07)
    cx, cy, cw = section(s, x, ys[1], w, hs[1], "02", "Real-world problem")
    wc = R["wc"]
    src = "GEE" if (R["source"] == "gee" and "GEE" in set(wc.source)) else "ASF"
    w0 = wc[(wc.source == src) & wc.season.isin([f"{a}/{a + 1}" for a in range(2017, 2026)])]
    nov_rng = f"{int(w0['Nov'].min())}–{int(w0['Nov'].max())}" if len(w0) else "?"
    bullets(s, cx, cy, cw, hs[1] - 1.1, [
        "The Jamuna erodes farmland and homesteads every monsoon — CEGIS monitored ~348 ha of Jamuna bank erosion in 2025.",
        "Post-monsoon maps of lost land help agencies prepare before the next monsoon.",
        [("Radar sees through clouds, but a quick map has few comparable scenes: ", {"size": 25}),
         (f"only {nov_rng} ascending Sentinel-1 scenes per November (2017–2025) over our reach.", {"bold": True, "color": ORANGE, "size": 25})],
        "Speckle, wet sand, flooded fields and lingering floodwater can create false erosion — or hide real erosion.",
    ], size=25)
    cx, cy, cw = section(s, x, ys[2], w, hs[2], "03", "Existing research → gap")
    rows = [["Study", "What it did", "Missing for our question"],
            ["Freihardt & Frey 2023 (NHESS)", "Sentinel-1 + GEE threshold erosion maps, Jamuna; window & filter effects on backscatter; land-cover OA 87.5–90.6 %",
             "Erosion-map accuracy vs scene count; erosion checked visually only"],
            ["Shampa et al. 2025 (Front. Earth Sci.)", "Delft3D erosion early warning, Brahmaputra–Jamuna", "Forecasting task; no SAR"],
            ["CEGIS (annual report)", "Operational erosion prediction from Landsat", "30 m; not a SAR reliability test"],
            ["MCDWD · RADD · GFM · Li et al. 2026", "m-of-k confirmation / abstention in flood & forest products", "Not tested for riverbank erosion maps"]]
    table(s, cx, cy, cw, 7.3, rows, col_w=[3.2, 5.35, 3.95], font_size=20)
    text(s, cx, cy + 7.6, cw, 2.2, [[("Gap: ", {"bold": True, "color": TEAL}),
                                      ("to our knowledge, no reviewed study measured erosion-map accuracy across Sentinel-1 scene budgets "
                                       "with agreement + abstention + coverage reporting, against an independent optical reference.", {})]], size=23)
    cx, cy, cw = section(s, x, ys[3], w, hs[3], "04", "Research questions")
    bullets(s, cx, cy, cw, hs[3] - 1.1, [
        [("RQ1 ", {"bold": True, "color": NAVY, "size": 21.5}), ("How do Precision, Recall, F1, IoU change as scenes decrease (k = 8 → 1)?", {"size": 21.5})],
        [("RQ2 ", {"bold": True, "color": NAVY, "size": 21.5}), ("Does m-of-k agreement cut false erosion, and at what recall cost?", {"size": 21.5})],
        [("RQ3 ", {"bold": True, "color": NAVY, "size": 21.5}), ("Does abstaining near the threshold raise precision — and how much coverage is lost?", {"size": 21.5})],
        [("RQ4 ", {"bold": True, "color": NAVY, "size": 21.5}), ("Timeliness vs reliability of maps from the first 1–3 scenes after 1 Nov.", {"size": 21.5})],
        [("RQ5 ", {"bold": True, "color": ORANGE, "size": 21.5}), ("Can map-date SAR evidence rank possible-erosion patches so a limited review recovers more "
                                                                     "erosion than random review — on an independent reach?", {"size": 21.5})],
    ], size=21.5, bullet="")
    cx, cy, cw = section(s, x, ys[4], w, hs[4], "05", "Independent reference & check")
    pts = R["pts"]
    if pts is not None:
        e = pts[pts.stratum == "ref_erosion"].iloc[0]
        n = pts[pts.stratum == "ref_nonerosion_near_bank"].iloc[0]
        chk = (f"Visual check of {int(pts.n_points.sum())} stratified points (blind to label): {int(e.visual_eroded)}/{int(e.n_visual_decided)} "
               f"reference-erosion points truly eroded ({100 * e.agreement_with_auto_label:.0f} %); {int(n.visual_not_eroded)}/{int(n.n_visual_decided)} "
               f"near-bank non-erosion points correct ({100 * n.agreement_with_auto_label:.0f} %). AI-interpreted; team spot-check pending.")
    else:
        chk = "Point check pending."
    bullets(s, cx, cy, cw, hs[4] - 1.1, [
        "Sentinel-2 L2A (different sensor): vegetated (NDVI ≥ 0.30) in Feb–Mar before → water (MNDWI ≥ 0) or bare sand (NDVI < 0.20) in the next Feb–Mar, connected to the channel, in a 1.5 km outer-bank strip.",
        chk,
        sir_chk(R),
    ], size=21)


def sir_chk(R):
    q = R.get("pts_sir")
    if q is None:
        return "An optical reference — NOT field ground truth."
    e = q[q.stratum == "ref_erosion"].iloc[0]
    n = q[q.stratum == "ref_nonerosion_near_bank"].iloc[0]
    return (f"Independent reach (Sirajganj, 2025): {int(e.visual_eroded)}/{int(e.n_visual_decided)} erosion points "
            f"({100 * e.agreement_with_auto_label:.0f} %; {int(e.visual_cannot_tell)} undecidable), {int(n.visual_not_eroded)}/{int(n.n_visual_decided)} "
            f"non-erosion ({100 * n.agreement_with_auto_label:.0f} %). An optical reference — NOT field ground truth.")


def flow(s, x, y, w):
    def box(bx, by, bw, bh, t, fill=LIGHT, col=NAVY, size=18, bold=True, line=NAVY):
        sh = rect(s, bx, by, bw, bh, fill=fill, line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_w=1.75)
        tf = sh.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.06)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        for i, line_t in enumerate(t.split("\n")):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = PP_ALIGN.CENTER
            r = para.add_run()
            r.text = line_t
            r.font.size = Pt(size if i == 0 else size - 2)
            r.font.bold = bold if i == 0 else False
            r.font.color.rgb = col
            r.font.name = "Calibri"
        return sh

    def arrow(x1, y1, x2, y2):
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        c.line.color.rgb = GREY
        c.line.width = Pt(2.5)
        from lxml import etree
        from pptx.oxml.ns import qn
        etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd")).set("type", "triangle")
        return c

    bw = (w - 0.6) / 3
    box(x, y, bw, 1.35, "Sentinel-1 VV · R114 asc\nangle 30–45° · circle r=7 (linear) → dB")
    box(x + bw + 0.3, y, bw, 1.35, "Pre composite\nmean Nov–Apr (dry season)")
    box(x + 2 * (bw + 0.3), y, bw, 1.35, "Post scenes\nk of 8 (Nov–Jan)")
    arrow(x + bw, y + 0.67, x + bw + 0.3, y + 0.67)
    arrow(x + 2 * bw + 0.3, y + 0.67, x + 2 * bw + 0.6, y + 0.67)
    yy = y + 1.8
    rw = (w - 0.45) / 4
    rules = [("BASELINE\n(F&F 2023)", "pre > T_pre AND\nmean(post) < T_post", LIGHT, NAVY),
             ("A: AGREEMENT", "≥ m of k scenes\nbelow T_scene", CYAN_LIGHT, NAVY),
             ("G: GATING", "|value − T| ≤ δ dB\n→ UNCERTAIN", CYAN_LIGHT, NAVY),
             ("SAGE A+G", "per-scene ±δ votes\n+ m-of-k", RGBColor(0xFD, 0xEB, 0xDF), ORANGE)]
    for i, (t1, t2, fill, col) in enumerate(rules):
        box(x + i * (rw + 0.15), yy, rw, 1.9, f"{t1}\n{t2}", fill=fill, col=col, size=18, line=col)
    for i in range(4):
        arrow(x + w / 2, y + 1.35, x + i * (rw + 0.15) + rw / 2, yy)
    yy2 = yy + 2.25
    box(x, yy2, w, 1.05, "v1 output:  EROSION · NON-EROSION · UNCERTAIN (abstained, counted in coverage)" + chr(10) +
        "v2 triage:  HIGH-CONFIDENCE (v1 + bank-connected) · REVIEW (ranked) · LIKELY STABLE", fill=WHITE, size=17)
    yy3 = yy2 + 1.4
    box(x, yy3, w * 0.48, 1.3, "Sentinel-2 reference\nveg → sand/water, channel-connected", fill=LIGHT, size=17)
    box(x + w * 0.52, yy3, w * 0.48, 1.3, "Score on outer-bank strip\nP, R, F1, IoU on decided px + coverage", fill=LIGHT, size=17)
    text(s, x, yy3 + 1.45, w, 0.9, [[("S (season matching) is part of the baseline — a common control, not claimed as new. "
                                      "Gating is an abstention rule, not a calibrated probability.", {"italic": True, "color": GREY})]], size=16)


def col2(s, R, figdir):
    x, w = COL_X[1], COL_W[1]
    hs = [7.4, 7.3, 9.6, 5.0, 8.0]
    ys = stack(hs)
    cx, cy, cw = section(s, x, ys[0], w, hs[0], "06", "Study area & data")
    fw, fh = fit_picture(s, C.FIGS / "figure_0_study_area.png", cx, cy, cw * 0.64, hs[0] - 1.2, align="left")
    p = aoi_props()
    src = ("Sentinel-1 GRD σ⁰ (Google Earth Engine COPERNICUS/S1_GRD)" if R["source"] == "gee"
           else "Sentinel-1 RTC γ⁰ (Microsoft Planetary Computer)")
    bullets(s, cx + fw + 0.2, cy, cw - fw - 0.2, hs[0] - 1.2, [
        f"{p['height_km']:.0f} km Jamuna reach upstream of Chilmari, Kurigram — AOI {p['width_km']:.0f} × {p['height_km']:.0f} km, "
        f"{p['centre_lat']:.2f}°N {p['centre_lon']:.2f}°E",
        f"SAR: {src}; VV, IW, orbit 114 ascending, 10 m",
        "Reference: Sentinel-2 L2A",
        "Validation monsoon 2024 · test monsoon 2025",
        "Independent reach (pre-registered): Sirajganj–Kazipur, 28 × 12 km, 24.70°N 89.71°E",
    ], size=17)
    cx, cy, cw = section(s, x, ys[1], w, hs[1], "07", "Sentinel-1 scene availability (Fig. A)")
    fw, fh = fit_picture(s, C.FIGS / "figure_A_scene_availability.png", cx, cy, cw, hs[1] - 2.2)
    inv = "Google Earth Engine inventory, cross-checked with ASF and Planetary Computer" if R["source"] == "gee" \
        else "ASF catalogue, cross-checked with Planetary Computer"
    caption(s, cx, cy + fh + 0.08, cw, f"Unique acquisitions over the AOI ({inv}). Few scenes = orbit geometry and time window, "
            "not clouds. Sentinel-1B added only 4 scenes; Sentinel-1D replaced 1A in July 2026.", size=16)
    cx, cy, cw = section(s, x, ys[2], w, hs[2], "08", "Baseline & SAGE-River")
    flow(s, cx, cy, cw)
    cx, cy, cw = section(s, x, ys[3], w, hs[3], "09", "Experimental design & integrity")
    bullets(s, cx, cy, cw, hs[3] - 1.1, [
        "All tuning on 2024 only (thresholds; m and δ by F1 with coverage ≥ 90 %), frozen with a timestamp, then ONE test on 2025",
        "Fairness control: a baseline whose thresholds are tuned on the same 2024 erosion F1",
        "Exp. A: all C(8,k) subsets of the Nov–Jan pool, k = 1, 2, 3, 6, 8 (121 maps per rule)",
        "Exp. B: first 1, 2, 3 scenes after 1 Nov — no future scenes; same reference & domain for every rule",
        "v2 design + code frozen (md5, timestamps) before any Sirajganj SAR was processed; Kurigram 2025 v2 = exploratory",
    ], size=19.5)
    v2fig = Path(figdir) / "figure_H_poster.png"
    if v2fig.exists():
        cx, cy, cw = section(s, x, ys[4], w, hs[4], "10", "SAGE-River v2: triage + prioritized review")
        fw, fh = fit_picture(s, v2fig, cx, cy, cw, hs[4] - 4.0)
        caption(s, cx, cy + fh + 0.03, cw, "REVIEW = possible erosion within 100 m of the SAR bank, ranked by a 2024-trained logistic model on "
                "map-date SAR features only. Review = simulated oracle analyst (upper bound). Random = 500 orders.", size=13.5)
        v2_table(s, R, cx, cy + fh + 0.62, cw)
    else:
        cx, cy, cw = section(s, x, ys[4], w, hs[4], "10", "Abstention trade-off (Fig. F)")
        fit_picture(s, Path(figdir) / "figure_F_tradeoff.png", cx, cy, cw, hs[4] - 1.15)


def v2_table(s, R, x, y, w):
    c = R.get("crit")
    if c is None:
        return
    role = {"Kurigram 2025": "exploratory", "Sirajganj 2025 (local calibration)": "INDEPENDENT",
            "Sirajganj 2024 (Kurigram parameters)": "transfer", "Sirajganj 2025 (Kurigram parameters)": "transfer"}
    name = {"Kurigram 2025": "Kurigram 2025", "Sirajganj 2025 (local calibration)": "Sirajganj 2025 (local T)",
            "Sirajganj 2024 (Kurigram parameters)": "Sirajganj 2024 (Kurigram T)", "Sirajganj 2025 (Kurigram parameters)": "Sirajganj 2025 (Kurigram T)"}
    rows = [["k = 3", "Status", "Tuned F1", "v2 HC F1", "Recovered @ 20 %: v2 / random / v1-U", "Both criteria met"]]
    for ev in role:
        d = c[c.evaluation == ev]
        if d.empty:
            continue
        r = d[d.k == 3].iloc[0]
        met = " ".join(f"k{int(k)}{'✓' if b else '✗'}" for k, b in zip(d.k, d.both_met))
        rows.append([name[ev], role[ev], f2(r.f1_tuned_baseline), f2(r.f1_v2_no_review),
                     f"{r.recovered_prioritized_ha:.1f} / {r.recovered_random_mean_ha:.1f} / {r.recovered_v1_uncertain_random_ha:.1f} ha",
                     met])
    cw0 = [3.3, 1.75, 1.25, 1.3, 3.75, 3.45]
    table(s, x, y, w, 0.36 * len(rows), rows, col_w=[v * w / sum(cw0) for v in cw0], font_size=14.5)
    caption(s, x, y + 0.36 * len(rows) + 0.05, w, "Criteria (pre-registered): (a) prioritized > random mean and 95th percentile at 20 %; "
            "(b) HC false erosion ≤ v1. HC F1 = full-area, no review. v1-U = random review of v1 UNCERTAIN, same ha. Source: outputs/tables/v2_preregistered_criteria.csv", size=12.5)


def col3(s, R, figdir):
    x, w = COL_X[2], COL_W[2]
    A = R["A"]
    d = A[A.year == 2025]
    F = R["F"]
    hs = [14.2, 9.0, 8.5, 6.1]
    ys = stack(hs)
    cx, cy, cw = section(s, x, ys[0], w, hs[0], "11", "Results — test monsoon 2025 (parameters frozen on 2024)")
    ks = [1, 2, 3, 6, 8]
    methods = ["BASE_published", "BASE_F1tuned", "BASE_calibrated", "A_unanimous", "AG_agree+gate"]
    colors = [RGBColor(0x7F, 0x8C, 0x8D), RGBColor(0xA0, 0x52, 0x2D), NAVY, RGBColor(0x8E, 0x44, 0xAD), ORANGE]

    def series(col):
        out = []
        for m in methods:
            dm = d[d.method == m].set_index("k")
            out.append((M_LABEL[m], [dm[col].get(k) if k in dm.index else None for k in ks]))
        return out

    chw = (cw - 0.3) / 2
    line_chart(s, cx, cy, chw, 6.3, [str(k) for k in ks], series("f1_mean"), title="F1 on decided pixels (mean of all subsets)",
               y_title="F1", colors=colors, font_size=17, y_max=1.0)
    line_chart(s, cx + chw + 0.3, cy, chw, 6.3, [str(k) for k in ks], series("f1_abst_nonero_mean"),
               title="F1 with UNCERTAIN counted as non-erosion", y_title="F1", colors=colors, font_size=17, y_max=1.0)
    yt = cy + 6.5
    rows = [["k", "Rule", "Precision", "Recall", "F1", "F1 (U = non)", "IoU", "Coverage", "False ha", "Missed ha", "Abstained ha"]]
    for k in (1, 3, 8):
        for m in methods:
            r = d[(d.method == m) & (d.k == k)]
            if r.empty:
                continue
            r = r.iloc[0]
            rows.append([str(k), M_LABEL[m], f2(r.precision_mean), f2(r.recall_mean), f2(r.f1_mean), f2(r.f1_abst_nonero_mean),
                         f2(r.iou_mean), f"{100 * r.coverage_mean:.0f}%", f2(r.false_erosion_ha_mean, 1), f2(r.missed_erosion_ha_mean, 1),
                         f2(r.abstained_erosion_ha_mean, 1)])
    rh = 0.4
    table(s, cx, yt, cw, rh * len(rows), rows, col_w=[0.5, 4.15, 1.5, 1.35, 1.1, 1.65, 1.1, 1.5, 1.4, 1.55, 1.6], font_size=16.5)
    ref_ha = d["reference_erosion_ha"].dropna().iloc[0]
    caption(s, cx, yt + rh * len(rows) + 0.1, cw,
            f"Means over all C(8,k) subsets (overlapping, not independent). Reference erosion = {ref_ha:.1f} ha. Precision/recall on decided pixels; "
            f"'F1 (U = non)' counts UNCERTAIN as non-erosion. Source: outputs/tables/experiment_A_summary_{R['source']}.csv", size=15)
    cx, cy, cw = section(s, x, ys[1], w, hs[1], "12", "Maps (east-bank hotspot) and early maps")
    avail = hs[1] - 1.2
    bw, bh = fit_picture(s, Path(figdir) / "figure_B_maps.png", cx, cy, cw * 0.55, avail, align="left")
    rx, rw = cx + bw + 0.25, cw - bw - 0.25
    imap = Path(figdir) / "figure_I_three_class_map.png"
    ew, eh = fit_picture(s, imap if imap.exists() else Path(figdir) / "figure_E_chronological.png", rx, cy, rw, 4.2, align="left")
    eb = F["exp_b"] if F else "Experiment B summary pending."
    text(s, rx, cy + eh + 0.2, rw, avail - eh - 0.2, [[("Early maps (Exp. B): ", {"bold": True, "color": NAVY}), (eb, {})]], size=17.5)
    cx, cy, cw = section(s, x, ys[2], w, hs[2], "13", "A bad scene, audited: inundated fields — not a processing bug")
    fw, fh = fit_picture(s, Path(figdir) / "figure_D_errors.png", cx, cy, cw, hs[2] - 2.3)
    rc = F.get("root_cause", "") if F else ""
    if rc:
        caption(s, cx, cy + fh + 0.05, cw, rc, size=14.5)
    cx, cy, cw = section(s, x, ys[3], w, hs[3], "14", "Key findings · contributions · limitations")
    third = (cw - 0.4) / 3
    ch = hs[3] - 1.15
    callout(s, cx, cy, third, ch, "Findings", F["findings"] if F else ["pending"], size=15.5)
    callout(s, cx + third + 0.2, cy, third, ch, "Contributions", F["contributions"] if F else ["pending"], size=15.5)
    callout(s, cx + 2 * (third + 0.2), cy, third, ch, "Limitations", F["limitations"] if F else ["pending"],
            fill=RGBColor(0xFD, 0xF2, 0xEA), size=15.5)


def footer(s, R):
    y0 = 46.05
    rect(s, 0, y0, W_IN, H_IN - y0, fill=LIGHT)
    rect(s, 0, y0, W_IN, 0.07, fill=TEAL)
    data = "Copernicus Sentinel-1/2 (ESA) via " + ("Google Earth Engine, " if R["source"] == "gee" else "") + "Microsoft Planetary Computer, ASF."
    refs = ("[1] Freihardt & Frey (2023) NHESS 23:751–770, doi:10.5194/nhess-23-751-2023 · [2] Freihardt & Frey (2022) code, doi:10.5281/zenodo.7253121 · "
            "[3] Shampa et al. (2025) Front. Earth Sci. 13:1570577, doi:10.3389/feart.2025.1570577 · [4] Aishi & Fahim (2024) GNHR 15:2399668, "
            "doi:10.1080/19475705.2024.2399668 · [5] Langhorst & Pavelsky (2023) JGR-ES 128:e2022JF006774 · [6] CEGIS (2026) Prediction of Riverbank "
            "Erosion 2026, cegisbd.com/news/3011 · [7] Reiche et al. (2021) ERL 16:024005 · [8] Krullikowski et al. (2023) IEEE JSTARS 16:6917 · "
            "[9] Li, Matgen & Chini (2026) IEEE TGRS 64:4202520 · [10] Peña-Luque et al. (2021) Remote Sens. 13:3279 · Data: " + data)
    text(s, 0.5, y0 + 0.12, 38.6, 1.8, [[("REFERENCES  ", {"bold": True, "color": NAVY}), (refs, {"color": DARK})]], size=15, line_spacing=1.0)
    text(s, 39.4, y0 + 0.12, 8.1, 1.8, [[(CORRESPONDING, {"bold": True, "color": NAVY})],
                                        [("Code, data & CSVs: SAGE-River/ (README)", {})],
                                        [("Sentinel-2 is an optical reference, not field ground truth.", {"italic": True, "color": GREY})]], size=15)


def write_markdown(R):
    """Poster text in Markdown (same sources as the PPTX)."""
    F = R["F"] or {}
    d = R["A"][R["A"].year == 2025]
    p = aoi_props()
    L = ["# How Many Sentinel-1 Scenes Are Enough?",
         "## Scene-Count Sensitivity, Agreement-Gated Reliability and Prioritized Review of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh",
         AUTHOR_LINE + " — IEEE BUBT Academic Research Showcase 2026, Track 1 (poster 48 × 48 in)", "",
         f"**Key message:** {F.get('takeaway', 'pending')}", "", "### Abstract", F.get("abstract", "pending"), "",
         "### Real-world problem",
         "- The Jamuna erodes farmland and homesteads every monsoon — CEGIS monitored ~348 ha of Jamuna bank erosion in 2025.",
         "- Post-monsoon maps of lost land help agencies prepare before the next monsoon.",
         "- Radar sees through clouds, but a quick map has few comparable scenes (2–3 ascending scenes per November over our reach).", "",
         "### Existing research → gap",
         "- Freihardt & Frey 2023: Sentinel-1/GEE threshold erosion mapping on the Jamuna; window/filter effects on backscatter; land-cover OA 87.5–90.6 %; erosion checked visually.",
         "- Shampa et al. 2025: Delft3D early warning (forecasting, no SAR). CEGIS: operational Landsat prediction.",
         "- m-of-k confirmation and abstention exist in flood/forest SAR products (MCDWD, RADD, GFM, Li et al. 2026).",
         "- **Gap:** to our knowledge, no reviewed study measured erosion-map accuracy across Sentinel-1 scene budgets with agreement + abstention + coverage against an independent optical reference.", "",
         "### Research questions", "RQ1 scene count vs P/R/F1/IoU · RQ2 agreement vs false erosion · RQ3 abstention vs coverage · RQ4 timeliness vs reliability · "
         "RQ5 can map-date SAR evidence rank possible-erosion patches so a limited review recovers more erosion than random review, on an independent reach?", "",
         "### Study area & data",
         f"{p['name']}; AOI {p['width_km']:.0f} × {p['height_km']:.0f} km, centre {p['centre_lat']:.3f}°N {p['centre_lon']:.3f}°E. "
         f"SAR source: {'GEE COPERNICUS/S1_GRD σ⁰' if R['source'] == 'gee' else 'Planetary Computer sentinel-1-rtc γ⁰'} VV, R114 ascending. Reference: Sentinel-2 L2A.", "",
         "### Results (test monsoon 2025, frozen parameters; mean over all C(8,k) subsets)", "",
         "| k | Rule | Precision | Recall | F1 | F1 (U = non) | IoU | Coverage | False ha | Missed ha | Abstained ha |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in (1, 2, 3, 6, 8):
        for m in ["BASE_published", "BASE_calibrated", "BASE_F1tuned", "A_majority", "A_unanimous", "G_gated", "AG_agree+gate"]:
            r = d[(d.method == m) & (d.k == k)]
            if r.empty:
                continue
            r = r.iloc[0]
            L.append(f"| {k} | {M_LABEL[m]} | {f2(r.precision_mean)} | {f2(r.recall_mean)} | {f2(r.f1_mean)} | {f2(r.f1_abst_nonero_mean)} | "
                     f"{f2(r.iou_mean)} | {100 * r.coverage_mean:.0f}% | {f2(r.false_erosion_ha_mean, 1)} | {f2(r.missed_erosion_ha_mean, 1)} | "
                     f"{f2(r.abstained_erosion_ha_mean, 1)} |")
    L += ["", f"**Early maps (Exp. B):** {F.get('exp_b', 'pending')}", ""]
    if F.get("root_cause"):
        L += ["### A bad scene, audited (31 Jan 2026)", F["root_cause"], ""]
    c = R.get("crit")
    if c is not None:
        L += ["### SAGE-River v2: triage + prioritized review (20 % review effort, simulated oracle reviewer)", "",
              "| Evaluation | Role | k | Tuned F1 | v2 HC F1 | Recovered v2 / random / v1-U (ha) | Random p95 (ha) | (a) | (b) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for _, r in c.iterrows():
            L.append(f"| {r.evaluation} | {r.role} | {int(r.k)} | {f2(r.f1_tuned_baseline)} | {f2(r.f1_v2_no_review)} | "
                     f"{r.recovered_prioritized_ha:.2f} / {r.recovered_random_mean_ha:.2f} / {r.recovered_v1_uncertain_random_ha:.2f} | "
                     f"{r.random_p95_ha:.2f} | {'met' if r.crit_a_met else 'NOT met'} | {'met' if r.crit_b_met else 'NOT met'} |")
        L += ["", "Source: outputs/tables/v2_preregistered_criteria.csv. Details: docs/sage_river_v2_results.md", ""]
    L += ["### Key findings"] + [f"- {x}" for x in F.get("findings", [])]
    L += ["", "### Contributions"] + [f"- {x}" for x in F.get("contributions", [])]
    L += ["", "### Limitations"] + [f"- {x}" for x in F.get("limitations", [])]
    L += ["", CORRESPONDING, "", "Sentinel-2 is an independent optical reference, not field ground truth. Historical erosion mapping — not forecasting, not a PINN."]
    (POSTER / "poster_content_en.md").write_text("\n".join(L), encoding="utf-8")


def main(source, figdir):
    R = load(source)
    write_markdown(R)
    p, s = new_poster(W_IN, H_IN)
    header(s, R)
    ribbon(s, R)
    col1(s, R)
    col2(s, R, figdir)
    col3(s, R, figdir)
    footer(s, R)
    out = POSTER / "poster_editable.pptx"
    p.save(out)
    print("saved", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["gee", "pc"], required=True)
    ap.add_argument("--figdir", default=str(C.FIGS))
    a = ap.parse_args()
    main(a.source, a.figdir)
