# SAGE-River — Final Completion and Limitation Report
Generated 11 Nov 2026 (~02:15 BST). Event: IEEE BUBT Academic Research Showcase, 13–14 Nov 2026.

## 1. What was done (all executed, not just scripted)
1. **Environment:** `.venv` (Python 3.14; the 3.11 launcher entry points to a missing executable), pinned `requirements.txt`. Self-tests for metrics and decision rules pass.
2. **Earth Engine:** browser login completed by the user (credentials saved). **No Cloud project ID was provided**, so `ee.Initialize` could not run. GEE scripts (`gee/01–07`) are built for the final AOI and pass a JavaScript syntax check, but were **not executed in Earth Engine**.
3. **Study area:** Sentinel-2 reconnaissance of Kurigram and Sirajganj boxes (30 m). The Bogura box crashed on a console-encoding error after Sirajganj and was not rerun. Final AOI is a 12 km Jamuna reach upstream of Chilmari, Kurigram: UTM45N 764–790 E, 2836–2848 N; 89.6289–89.8902 °E, 25.6131–25.7262 °N (`data/aoi/aoi.geojson`, `outputs/figures/figure_0_study_area.png`).
4. **Scene inventory:** ASF and Planetary Computer catalogues for the exact AOI (`outputs/tables/sentinel1_*.csv`, Figure A). Phase 0 counts were confirmed (`docs/phase0_audit.md`).
5. **SAR data:** Planetary Computer `sentinel-1-rtc` γ⁰ VV, R114 ascending. Linear values were filtered with circle r=7 then converted to dB; a square 7×7 run was added for sensitivity. Scene pools:

   | Year | Pre composite | Post pool |
   |---|---|---|
   | 2024 | 11 scenes | 6 scenes |
   | 2025 | 12 scenes | 8 scenes |

   Product IDs are listed in `data/cache/s1_pc_*.json`.
6. **Reference:** Sentinel-2 L2A with the SCL cloud mask, Feb–Mar composites, and an as-of Nov–Dec composite. Reference erosion is 58.8 ha in 2025 and 59.8 ha in 2024. AOI clear-observation quality is in `s2_reference_quality.csv`.
7. **Reference point check:** 120 stratified points, interpreted blind to stratum. Agreement was 36/39 = 92 % for the erosion stratum and 47/47 = 100 % for non-erosion near the bank. Interpretation was by the AI analyst; the team still needs to spot-check.
8. **Experiments:**
   - Calibration and selection on 2024 only.
   - Parameters frozen at 01:59:39 (JSON), then the 2025 test.
   - Experiment A: all 121 subsets. Experiment B: first 1–3 scenes after 1 November.
   - A fairness-control baseline (F1-tuned) was added after inspecting only the 2024 tables. Run 1 without it is archived in `outputs/reports/run1_without_F1tuned_baseline/`.
   - Post-hoc δ trade-off on 2025 is labelled as not used for selection.
9. **Figures:** 0, A, B, C (full and poster versions), D (anomalous scene), E (chronological), F (trade-off), plus supplementary reference QA figures.
10. **Poster:** `poster/poster_editable.pptx`
    - 48×36 in, 31 text boxes, 2 native charts, 2 native tables, 7 images.
    - `poster/poster_final.pdf`, exported by PowerPoint; images embedded at ~200 ppi.
    - `poster/poster_content_en.md` and `poster/references.bib`. Titles were checked against Crossref.
11. **Presentation:** 30-second and 2-minute English pitch, Bangla guide, judges' Q&A (general and results), figure explanations, team roles.
12. **Final audit:** `outputs/reports/final_audit.md`. All checks pass:
    - file existence and subset counts;
    - metric ranges and count consistency;
    - 5 recomputed rows;
    - freeze order;
    - claim scan with negations allowed.

## 2. Key verified results (2025 test)
- **How many scenes are enough:** with the published rule, F1 is 0.70 (k=1), 0.77 (k=3) and 0.77 (k=8). False erosion is 22 ha at k=1 and 2 ha at k=3. Single scenes range from F1 0.30 to 0.77.
- **Tuned baseline:** F1 0.67 (k=1) rising to 0.80 (k=8).
- **SAGE A+G:**
  - F1 on decided pixels 0.86–0.90; false erosion ≤ 2.4 ha.
  - Coverage 87–91 %; 13.7–21.2 ha of the 58.8 ha reference erosion was abstained.
  - With UNCERTAIN counted as non-erosion, F1 is 0.66–0.77, which is not consistently better than the tuned baseline.
- **Anomalous scene (31 Jan 2026):** 197 ha of false erosion alone (tuned baseline). In 2-scene maps that include it, false erosion is 36 ha on average for the baseline and about 1 ha for A+G.
- **Class-separability (Youden) thresholds:** F1 0.35–0.42. Threshold choice dominates the result.
- **Filter:** the paper's square 7×7 changed F1 by −0.02 to +0.08. The ranking of methods did not change.

## 3. Status table
| Component | Status | Evidence |
|---|---|---|
| Literature Review | Completed with limitations | `docs/literature_review.md` (F&F and Shampa read in full text; others abstract-level; IEEE Xplore/Scopus not searched) |
| Research Gap | Completed and verified | `docs/research_gap.md`; cautious "to our knowledge" wording |
| GEE Authentication | Partially completed | Login done; **project ID missing**, so `ee.Initialize` not run; scripts ready in `gee/` |
| Final Study Area | Completed and verified | `data/aoi/aoi.geojson`, Figure 0, recon maps |
| Scene Inventory | Completed with limitations | ASF and PC inventory for the AOI; **GEE inventory not run** |
| Baseline | Completed with limitations | Released-code rule reproduced in Python on PC RTC γ⁰ (not GEE σ⁰; no angle mask); published, calibrated and F1-tuned variants |
| Independent Reference | Completed with limitations | S2 L2A reference; 120-point visual check (92 %/100 %) by the AI analyst; team spot-check pending |
| SAGE-River | Completed and verified | `python/sage_methods.py` (self-tests); `gee/06_sage_river.js` (syntax only) |
| Experiment A | Completed and verified | `experiment_A_*_pc.csv`; audit recomputation passed |
| Experiment B | Completed with limitations | `experiment_B_chronological_pc.csv`; 2024 lacks the 1 Nov scene in PC |
| Evaluation | Completed and verified | P/R/F1/IoU, coverage, false/missed/abstained ha, full-coverage F1 |
| Poster PPTX | Completed with limitations | `poster/poster_editable.pptx`; team names, e-mail and supervisor are placeholders |
| Poster PDF | Completed with limitations | `poster/poster_final.pdf`; ~200 ppi images; organiser size not confirmed (official template is A1 portrait) |
| Presentation | Completed and verified | `presentation/*.md` |

## 4. What remains (human actions)
1. **Earth Engine σ⁰ re-run (optional but recommended).** Provide a Cloud project ID, then from `python/`:
   ```
   ..\.venv\Scripts\python.exe gee_auth_check.py --project <ID>
   ..\.venv\Scripts\python.exe s1_stack.py --source gee --year 2024
   ..\.venv\Scripts\python.exe s1_stack.py --source gee --year 2025
   ..\.venv\Scripts\python.exe scene_analysis.py --gee
   ..\.venv\Scripts\python.exe experiment_runner.py --source gee
   ```
2. Spot-check at least 20 validation points (`data/reference/validation_points_2025.csv`, column `team_check`; chips are in `outputs/reports/validation_chips_2025_*.png`).
3. Fill in team names, department, university, e-mail and poster ID in the PPTX. Confirm the poster size with the organisers: the official template is A1 portrait (23.4×33.1 in), and our poster is 48×36 in landscape.
4. Re-export the PDF after editing (`poster/export_pdf.ps1`) and check it at 100 % zoom before printing.

## 5. What cannot be claimed
- SAGE-River is better than the baseline in every respect.
- Field-validated accuracy.
- Any forecast or future-erosion skill.
- A PINN or physics model.
- Earth Engine σ⁰ results.
- Generalisation beyond one reach and one test monsoon.
- That the 31 Jan dark patches are flooded paddies (not field-verified).
