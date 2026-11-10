"""Build the editable 48 x 36 in landscape poster (PPTX) from REAL outputs.

Numbers are read from outputs/tables/*.csv; interpretive sentences are read from poster/findings.json, which is
written only after the results were inspected. Missing inputs are shown as an explicit "pending" label.
Usage: python build_poster.py --source pc|gee
"""
import argparse
import json

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
BODY = 23
SMALL = 19

M_LABEL = {"BASE_published": "Baseline (published T)", "BASE_calibrated": "Baseline (calibrated T)",
           "BASE_F1tuned": "Baseline (F1-tuned T)",
           "A_majority": "A: majority", "A_unanimous": "A: unanimous", "G_gated": "G: gating",
           "AG_agree+gate": "SAGE-River A+G"}


def f2(v, nd=2):
    return "–" if v is None or (isinstance(v, float) and pd.isna(v)) else f"{v:.{nd}f}"


def load(source):
    R = {"source": source}
    t = C.TABLES
    R["wc"] = pd.read_csv(t / "sentinel1_window_counts.csv")
    R["acq"] = pd.read_csv(t / "sentinel1_acquisitions.csv")
    R["A"] = pd.read_csv(t / f"experiment_A_summary_{source}.csv")
    R["B"] = pd.read_csv(t / f"experiment_B_chronological_{source}.csv")
    R["sel"] = json.loads((t / f"selected_parameters_{source}.json").read_text())
    R["cal"] = pd.read_csv(t / f"calibration_thresholds_2024_{source}.csv")
    fj = POSTER / "findings.json"
    R["F"] = json.loads(fj.read_text(encoding="utf-8")) if fj.exists() else None
    pa = t / "reference_point_agreement_2025.csv"
    R["pts"] = pd.read_csv(pa) if pa.exists() else None
    rq = t / "s2_reference_quality.csv"
    R["rq"] = pd.read_csv(rq) if rq.exists() else None
    return R


def header(s, R):
    rect(s, 0, 0, 48, 4.7, fill=NAVY)
    rect(s, 0, 4.7, 48, 0.12, fill=TEAL)
    if (ASSETS / "Picture_31.png").exists():
        picture(s, ASSETS / "Picture_31.png", 0.55, 0.6, h=3.3)
    if (ASSETS / "Picture_30.png").exists():  # official event logo (from the organiser's template); white card behind it
        rect(s, 42.75, 0.55, 4.7, 3.5, fill=WHITE)
        picture(s, ASSETS / "Picture_30.png", 42.85, 0.0, h=4.6)
    text(s, 4.3, 0.3, 38.2, 0.6, [[("IEEE BUBT ACADEMIC RESEARCH SHOWCASE 2026  ·  TRACK 1: INTELLIGENT COMPUTING, AI & DATA TECHNOLOGIES",
                                     {"color": RGBColor(0x7F, 0xD8, 0xD8), "bold": True})]], size=22)
    text(s, 4.3, 0.85, 38.2, 1.4, [[("How Many Sentinel-1 Scenes Are Enough?", {"color": WHITE, "bold": True})]], size=78)
    text(s, 4.3, 2.25, 38.2, 1.2, [[("Scene-Count Sensitivity and Agreement-Gated Reliability of Post-Monsoon Riverbank Erosion Maps — "
                                     "Jamuna River, Bangladesh", {"color": WHITE})]], size=36)
    text(s, 4.3, 3.6, 38.2, 0.8, [[("[Team member names]  ·  Department of CSE, [University]  ·  [Corresponding e-mail]",
                                    {"color": RGBColor(0xDD, 0xE6, 0xF0)})]], size=26)


def ribbon(s, R):
    rect(s, 0.5, 5.05, 47.0, 1.05, fill=CYAN_LIGHT, line=TEAL, line_w=2)
    msg = R["F"]["takeaway"] if R["F"] else "Key message pending verified results"
    text(s, 0.8, 5.1, 46.4, 0.95, [[("KEY MESSAGE  ", {"bold": True, "color": TEAL}), (msg, {"bold": True, "color": NAVY})]],
         size=27, anchor=MSO_ANCHOR.MIDDLE)


def col1(s, R, x=0.5, w=13.2):
    F = R["F"]
    y = 6.35
    cx, cy, cw = section(s, x, y, w, 6.55, "01", "Abstract")
    text(s, cx, cy, cw, 5.4, F["abstract"] if F else "Abstract pending verified results.", size=20.5, line_spacing=1.06)
    y = 13.15
    cx, cy, cw = section(s, x, y, w, 5.75, "02", "Real-world problem")
    wc = R["wc"]
    w0 = wc[(wc.source == ("GEE" if R["source"] == "gee" else "ASF")) & wc.season.isin([f"{a}/{a + 1}" for a in range(2017, 2026)])]
    nov_rng = f"{int(w0['Nov'].min())}–{int(w0['Nov'].max())}" if len(w0) else "?"
    bullets(s, cx, cy, cw, 4.6, [
        "The Jamuna erodes farmland and homesteads every monsoon — CEGIS monitored ~348 ha of Jamuna bank erosion in 2025.",
        "Post-monsoon maps of lost land help agencies prepare before the next monsoon.",
        [("Radar sees through clouds, but a quick map has few comparable scenes: ", {"size": 21}),
         (f"only {nov_rng} ascending Sentinel-1 scenes per November (2017–2025) over our reach.", {"bold": True, "color": ORANGE, "size": 21})],
        "Speckle, wet sand, flooded fields and lingering floodwater can create false erosion — or hide real erosion.",
    ], size=22)
    y = 19.15
    cx, cy, cw = section(s, x, y, w, 9.15, "03", "Existing research → gap")
    rows = [["Study", "What it did", "Missing for our question"],
            ["Freihardt & Frey 2023 (NHESS)", "Sentinel-1 + GEE threshold erosion maps, Jamuna; window & filter effects on backscatter; land-cover OA 87.5–90.6 %",
             "Erosion-map accuracy vs scene count; erosion checked visually only"],
            ["Shampa et al. 2025 (Front. Earth Sci.)", "Delft3D erosion early warning, Brahmaputra–Jamuna", "Forecasting task; no SAR"],
            ["CEGIS (annual report)", "Operational erosion prediction from Landsat", "30 m; not a SAR reliability test"],
            ["MCDWD · RADD · GFM · Li et al. 2026", "m-of-k confirmation / abstention in flood & forest products", "Not tested for riverbank erosion maps"]]
    table(s, cx, cy, cw, 5.9, rows, col_w=[3.2, 5.35, 3.95], font_size=16.5)
    text(s, cx, cy + 6.2, cw, 1.8, [[("Gap: ", {"bold": True, "color": TEAL}),
                                     ("to our knowledge, no reviewed study measured erosion-map accuracy across Sentinel-1 scene budgets "
                                      "with agreement + abstention + coverage reporting, against an independent optical reference.", {})]], size=20)
    y = 28.55
    cx, cy, cw = section(s, x, y, w, 5.2, "04", "Research questions")
    bullets(s, cx, cy, cw, 4.1, [
        [("RQ1 ", {"bold": True, "color": NAVY, "size": 20}), ("How do Precision, Recall, F1, IoU change as scenes decrease (k = 8 → 1)?", {"size": 20})],
        [("RQ2 ", {"bold": True, "color": NAVY, "size": 20}), ("Does m-of-k agreement cut false erosion, and at what recall cost?", {"size": 20})],
        [("RQ3 ", {"bold": True, "color": NAVY, "size": 20}), ("Does abstaining near the threshold raise precision — and how much coverage is lost?", {"size": 20})],
        [("RQ4 ", {"bold": True, "color": NAVY, "size": 20}), ("Timeliness vs reliability of maps from the first 1–3 scenes after 1 Nov.", {"size": 20})],
    ], size=20, bullet="")


def col2(s, R, x=14.15, w=14.8):
    y = 6.35
    cx, cy, cw = section(s, x, y, w, 6.4, "05", "Study area & data")
    fw, fh = fit_picture(s, C.FIGS / "figure_0_study_area.png", cx, cy, cw * 0.60, 5.2, align="left")
    p = aoi_props()
    src = ("Sentinel-1 GRD σ⁰ (Google Earth Engine)" if R["source"] == "gee" else "Sentinel-1 RTC γ⁰ (Microsoft Planetary Computer)")
    bullets(s, cx + fw + 0.2, cy, cw - fw - 0.2, 5.2, [
        f"{p['height_km']:.0f} km Jamuna reach upstream of Chilmari, Kurigram (AOI {p['width_km']:.0f} × {p['height_km']:.0f} km, "
        f"{p['centre_lat']:.2f}°N {p['centre_lon']:.2f}°E)",
        f"SAR: {src}; VV, IW, orbit 114 ascending, 10 m",
        "Reference: Sentinel-2 L2A — independent optical sensor",
        "Validation monsoon 2024 · test monsoon 2025",
    ], size=16.5)
    y = 12.95
    cx, cy, cw = section(s, x, y, w, 7.05, "06", "Sentinel-1 scene availability (Fig. A)")
    fw, fh = fit_picture(s, C.FIGS / "figure_A_scene_availability.png", cx, cy, cw, 5.2)
    caption(s, cx, cy + fh + 0.05, cw, "Unique acquisitions over the AOI (ASF catalogue; cross-checked with Planetary Computer). "
            "Few scenes = orbit geometry and time window, not clouds. S1B added only 4 scenes; S1D replaced S1A in July 2026.", size=14.5)
    y = 20.25
    cx, cy, cw = section(s, x, y, w, 7.75, "07", "Baseline & SAGE-River")
    flow(s, cx, cy, cw)
    y = 28.25
    cx, cy, cw = section(s, x, y, w, 5.5, "08", "Experimental design & integrity")
    bullets(s, cx, cy, cw, 4.4, [
        "All tuning on 2024 only (thresholds; m, δ by F1 with coverage ≥ 90 %), frozen with a timestamp, then one test on 2025",
        "Fairness control: a baseline with thresholds tuned on the same 2024 erosion F1 (BASE F1-tuned)",
        "Exp. A: all C(8,k) subsets of the Nov–Jan pool, k = 1, 2, 3, 6, 8 (121 maps per rule)",
        "Exp. B: first 1, 2, 3 scenes after 1 Nov — no future scenes; same reference & domain for all rules",
    ], size=18)


def flow(s, x, y, w):
    def box(bx, by, bw, bh, t, fill=LIGHT, col=NAVY, size=16, bold=True, line=NAVY):
        sh = rect(s, bx, by, bw, bh, fill=fill, line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_w=1.75)
        tf = sh.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.06)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        parts = t.split("\n")
        for i, line_t in enumerate(parts):
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
        ln = c.line._get_or_add_ln()
        from lxml import etree
        from pptx.oxml.ns import qn
        tail = etree.SubElement(ln, qn("a:tailEnd"))
        tail.set("type", "triangle")
        return c

    bw = (w - 0.6) / 3
    box(x, y, bw, 1.1, "Sentinel-1 VV · R114 asc\ncircle r=7 filter (linear) → dB")
    box(x + bw + 0.3, y, bw, 1.1, "Pre composite\nmean Nov–Apr (dry season)")
    box(x + 2 * (bw + 0.3), y, bw, 1.1, "Post scenes\nk of 8 (Nov–Jan)")
    arrow(x + bw, y + 0.55, x + bw + 0.3, y + 0.55)
    arrow(x + 2 * bw + 0.3, y + 0.55, x + 2 * bw + 0.6, y + 0.55)
    yy = y + 1.45
    rw = (w - 0.45) / 4
    rules = [("BASELINE\n(F&F 2023)", "pre > T_pre AND\nmean(post) < T_post", LIGHT, NAVY),
             ("A: AGREEMENT", "≥ m of k scenes\nbelow T_scene", CYAN_LIGHT, NAVY),
             ("G: GATING", "|value − T| ≤ δ dB\n→ UNCERTAIN", CYAN_LIGHT, NAVY),
             ("SAGE A+G", "per-scene ±δ votes\n+ m-of-k", RGBColor(0xFD, 0xEB, 0xDF), ORANGE)]
    for i, (t1, t2, fill, col) in enumerate(rules):
        box(x + i * (rw + 0.15), yy, rw, 1.55, f"{t1}\n{t2}", fill=fill, col=col, size=16, line=col)
    for i in range(4):
        arrow(x + w / 2, y + 1.1, x + i * (rw + 0.15) + rw / 2, yy)
    yy2 = yy + 1.9
    box(x, yy2, w, 0.95, "Output per pixel:  EROSION  ·  NON-EROSION  ·  UNCERTAIN (abstained, always counted in coverage)",
        fill=WHITE, size=16)
    yy3 = yy2 + 1.25
    box(x, yy3, w * 0.48, 1.1, "Sentinel-2 reference\nveg (NDVI ≥ 0.30) → sand/water; channel-connected", fill=LIGHT, size=15)
    box(x + w * 0.52, yy3, w * 0.48, 1.1, "Score on outer-bank strip (1.5 km)\nP, R, F1, IoU on decided px + coverage", fill=LIGHT, size=15)
    text(s, x, yy3 + 1.2, w, 0.7, [[("S (season matching) is part of the baseline — a common control, not claimed as new. "
                                     "Gating is an abstention rule, not a calibrated probability.", {"italic": True, "color": GREY})]], size=14)


def col3(s, R, x=29.4, w=18.1):
    A = R["A"]
    d = A[A.year == 2025]
    F = R["F"]
    y = 6.35
    cx, cy, cw = section(s, x, y, w, 11.75, "09", "Results — test monsoon 2025 (parameters frozen on 2024)")
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
    line_chart(s, cx, cy, chw, 5.3, [str(k) for k in ks], series("f1_mean"), title="F1 on decided pixels (mean of all subsets)",
               y_title="F1", colors=colors, font_size=15, y_max=1.0)
    line_chart(s, cx + chw + 0.3, cy, chw, 5.3, [str(k) for k in ks], series("f1_abst_nonero_mean"),
               title="F1 with UNCERTAIN counted as non-erosion", y_title="F1", colors=colors, font_size=15, y_max=1.0)
    yt = cy + 5.45
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
    table(s, cx, yt, cw, 0.33 * len(rows), rows, col_w=[0.5, 4.15, 1.5, 1.35, 1.1, 1.65, 1.1, 1.5, 1.4, 1.55, 1.6], font_size=14.5)
    caption(s, cx, yt + 0.33 * len(rows) + 0.08, cw,
            "Means over all C(8,k) subsets (overlapping, not independent). Reference erosion = 58.8 ha. Precision/recall on decided pixels; "
            "'F1 (U = non)' counts UNCERTAIN as non-erosion. Source: outputs/tables/experiment_A_summary_" + R["source"] + ".csv", size=13.5)
    y = 18.3
    cx, cy, cw = section(s, x, y, w, 10.05, "10", "Maps: scene budget, a bad scene, and early maps")
    bw, bh = fit_picture(s, C.FIGS / "figure_B_maps.png", cx, cy, cw * 0.50, 8.85, align="left")
    rx, rw = cx + bw + 0.25, cw - bw - 0.25
    dw, dh = fit_picture(s, C.FIGS / "figure_D_errors.png", rx, cy, rw, 3.6, align="left")
    ew, eh = fit_picture(s, C.FIGS / "figure_E_chronological.png", rx, cy + dh + 0.15, rw, 3.0, align="left")
    eb = F["exp_b"] if F else "Experiment B summary pending."
    text(s, rx, cy + dh + eh + 0.25, rw, 8.85 - dh - eh - 0.25, [[("Early maps (Exp. B): ", {"bold": True, "color": NAVY}), (eb, {})]], size=14.5)
    y = 28.55
    cx, cy, cw = section(s, x, y, w, 5.2, "11", "Key findings · contributions · limitations")
    third = (cw - 0.4) / 3
    callout(s, cx, cy, third, 4.05, "Findings", F["findings"] if F else ["pending"], size=13.5)
    callout(s, cx + third + 0.2, cy, third, 4.05, "Contributions", F["contributions"] if F else ["pending"], size=13.5)
    callout(s, cx + 2 * (third + 0.2), cy, third, 4.05, "Limitations", F["limitations"] if F else ["pending"],
            fill=RGBColor(0xFD, 0xF2, 0xEA), size=13.5)


def footer(s, R):
    rect(s, 0, 33.95, 48, 2.05, fill=LIGHT)
    rect(s, 0, 33.95, 48, 0.06, fill=TEAL)
    refs = ("[1] Freihardt & Frey (2023) NHESS 23:751–770, doi:10.5194/nhess-23-751-2023 · [2] Freihardt & Frey (2022) code, doi:10.5281/zenodo.7253121 · "
            "[3] Shampa et al. (2025) Front. Earth Sci. 13:1570577, doi:10.3389/feart.2025.1570577 · [4] Aishi & Fahim (2024) GNHR 15:2399668, "
            "doi:10.1080/19475705.2024.2399668 · [5] Langhorst & Pavelsky (2023) JGR-ES 128:e2022JF006774 · [6] CEGIS (2026) Prediction of Riverbank "
            "Erosion 2026, cegisbd.com/news/3011 · [7] Reiche et al. (2021) ERL 16:024005 · [8] Krullikowski et al. (2023) IEEE JSTARS 16:6917 · "
            "[9] Li, Matgen & Chini (2026) IEEE TGRS 64:4202520 · [10] Peña-Luque et al. (2021) Remote Sens. 13:3279 · Data: Copernicus Sentinel-1/2 "
            "(ESA), Microsoft Planetary Computer, ASF.")
    text(s, 0.5, 34.05, 39.5, 1.85, [[("REFERENCES  ", {"bold": True, "color": NAVY}), (refs, {"color": DARK})]], size=13.5, line_spacing=1.0)
    text(s, 40.2, 34.1, 7.3, 1.8, [[("Code, data & CSVs: SAGE-River/ (README)", {"bold": True, "color": NAVY})],
                                   [("Corresponding author: [name, e-mail]", {})],
                                   [("Sentinel-2 is an optical reference, not field ground truth.", {"italic": True, "color": GREY})]], size=14)


def write_markdown(R):
    """Poster text in Markdown (same sources as the PPTX)."""
    F = R["F"] or {}
    A = R["A"]
    d = A[A.year == 2025]
    p = aoi_props()
    L = ["# How Many Sentinel-1 Scenes Are Enough?",
         "## Scene-Count Sensitivity and Agreement-Gated Reliability of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh",
         "[Team member names] · Department of CSE, [University] · [Corresponding e-mail] — IEEE BUBT Academic Research Showcase 2026, Track 1", "",
         f"**Key message:** {F.get('takeaway', 'pending')}", "", "### Abstract", F.get("abstract", "pending"), "",
         "### Real-world problem",
         "- The Jamuna erodes farmland and homesteads every monsoon — CEGIS monitored ~348 ha of Jamuna bank erosion in 2025.",
         "- Post-monsoon maps of lost land help agencies prepare before the next monsoon.",
         "- Sentinel-1 radar sees through clouds, but a quick map can use only a few comparable scenes (2–3 ascending scenes in November over our reach).", "",
         "### Existing research → gap",
         "- Freihardt & Frey 2023: Sentinel-1/GEE threshold erosion mapping on the Jamuna; window/filter effects on backscatter; land-cover OA 87.5–90.6 %; erosion checked visually.",
         "- Shampa et al. 2025: Delft3D early warning (forecasting, no SAR). CEGIS: operational Landsat prediction.",
         "- m-of-k confirmation and abstention exist in flood/forest SAR products (MCDWD, RADD, GFM, Li et al. 2026).",
         "- **Gap:** to our knowledge, no reviewed study measured erosion-map accuracy across Sentinel-1 scene budgets with agreement + abstention + coverage against an independent optical reference.", "",
         "### Research questions", "RQ1 scene count vs P/R/F1/IoU · RQ2 agreement vs false erosion · RQ3 abstention vs coverage · RQ4 timeliness vs reliability", "",
         "### Study area & data",
         f"{p['name']}; AOI {p['width_km']:.0f} × {p['height_km']:.0f} km, centre {p['centre_lat']:.3f}°N {p['centre_lon']:.3f}°E. "
         f"SAR source: {'GEE S1_GRD σ⁰' if R['source'] == 'gee' else 'Planetary Computer sentinel-1-rtc γ⁰'} VV, R114 ascending. Reference: Sentinel-2 L2A.", "",
         "### Results (test monsoon 2025, frozen parameters; mean over all C(8,k) subsets)", "",
         "| k | Method | Precision | Recall | F1 | IoU | Coverage | False ha | Missed ha |", "|---|---|---|---|---|---|---|---|---|"]
    for k in (1, 2, 3, 6, 8):
        for m in ["BASE_published", "BASE_calibrated", "BASE_F1tuned", "A_majority", "A_unanimous", "G_gated", "AG_agree+gate"]:
            r = d[(d.method == m) & (d.k == k)]
            if r.empty:
                continue
            r = r.iloc[0]
            L.append(f"| {k} | {M_LABEL[m]} | {f2(r.precision_mean)} | {f2(r.recall_mean)} | {f2(r.f1_mean)} | {f2(r.iou_mean)} | "
                     f"{100 * r.coverage_mean:.0f}% | {f2(r.false_erosion_ha_mean, 1)} | {f2(r.missed_erosion_ha_mean, 1)} |")
    L += ["", f"**Early maps (Exp. B):** {F.get('exp_b', 'pending')}", "", "### Key findings"] + [f"- {x}" for x in F.get("findings", [])]
    L += ["", "### Contributions"] + [f"- {x}" for x in F.get("contributions", [])]
    L += ["", "### Limitations"] + [f"- {x}" for x in F.get("limitations", [])]
    L += ["", "Sentinel-2 is an independent optical reference, not field ground truth. Historical erosion mapping — not forecasting, not a PINN."]
    (POSTER / "poster_content_en.md").write_text("\n".join(L), encoding="utf-8")


def main(source):
    R = load(source)
    write_markdown(R)
    p, s = new_poster()
    header(s, R)
    ribbon(s, R)
    col1(s, R)
    col2(s, R)
    col3(s, R)
    footer(s, R)
    out = POSTER / "poster_editable.pptx"
    p.save(out)
    print("saved", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["gee", "pc"], required=True)
    main(ap.parse_args().source)
