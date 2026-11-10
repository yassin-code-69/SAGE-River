# SAGE-River — Final Completion and Limitation Report
Updated 11 Nov 2026 ~04:20 BST (supersedes the 02:15 version). Event: IEEE BUBT Academic Research Showcase, 13–14 Nov 2026.

## 1. What was done (all executed, not just scripted)
1. **Environment.** `.venv` (Python 3.14) with pinned `requirements.txt`. Self-tests for metrics and decision rules pass.
2. **Earth Engine.** Project `fleet-surface-473722-b9`. **GEE COPERNICUS/S1_GRD σ⁰ is the primary SAR source** (tag `gee`).
   - Per-image processing: angle mask 30–45° → circle r = 7 filter in linear units → dB, then a per-day mosaic. Observed angles over the AOI were 36.4–38.1°.
   - Scene pools:

     | Year | Pre composite | Post pool |
     |---|---|---|
     | 2024 | 14 scenes | 8 scenes |
     | 2025 | 16 scenes | 8 scenes |

   - Planetary Computer RTC γ⁰ (tag `pc`) is kept as an *adapted* cross-check. It is not an exact reproduction of GEE σ⁰ (see `docs/methodology.md` §2.1).
3. **Study area.**
   - Development reach: Kurigram, 26 × 12 km, 12 km of the Jamuna upstream of Chilmari (`data/aoi/aoi.geojson`).
   - Independent reach for v2: Sirajganj–Kazipur, 28 × 12 km, 89.569–89.847 °E, 24.644–24.748 °N (`data/reaches/sirajganj/`).
4. **Scene inventory.** GEE, ASF and PC catalogues (`outputs/tables/sentinel1_*.csv`, Figure A). R114 ascending gives 2–3 scenes per November.
5. **Reference.** Sentinel-2 L2A with the SCL mask, Feb–Mar composites, channel-connected, in a 1.5 km outer-bank strip.

   | Reach / year | Reference erosion | Blind point check (erosion / non-erosion) |
   |---|---|---|
   | Kurigram 2025 | 58.8 ha | 36/39 = 92 % / 47/47 = 100 % |
   | Kurigram 2024 | 59.8 ha | – |
   | Sirajganj 2025 | 12.2 ha | 10/15 = 67 % (15 undecidable) / 27/29 = 93 % |
   | Sirajganj 2024 | 59.9 ha | – |

   The points were interpreted by the AI analyst; the team still needs to spot-check them.
6. **v1 experiments (Kurigram, GEE).**
   - Calibration and selection on 2024 only; frozen JSON; then the 2025 test.
   - Experiment A: all 121 subsets. Experiment B: first 1–3 scenes after 1 Nov.
   - F1-tuned fairness-control baseline included.
7. **Root-cause audit of the 31 Jan 2026 scene** (`outputs/reports/root_cause_audit_20260131.md`).
   - **No implementation error.** NoData, alignment, radiometry, mosaics and thresholds were all checked.
   - **Cause:** temporarily inundated fields, confirmed by three independent sources.
   - **The scene is kept** in every experiment.
   - One earlier claim in that report was corrected after measurement: v2 bank connectivity does *not* remove this error at k = 1.
8. **SAGE-River v2** (quality-aware triage + prioritized review).
   - Pre-registered: design 02:58, code freeze 03:12:45, transfer addendum 03:30:51.
   - md5 checksums in `docs/sage_river_v2_design.md5`; the final audit re-verified them as unchanged.
   - Evaluated on four reach/years (see §2.3).
   - Results and conclusion: `docs/sage_river_v2_results.md`.
9. **Figures.**
   - 0, A, B, C, D, E, F (v1);
   - G (v2 ablation), H (prioritized vs random review), I (three-class map, Kurigram and Sirajganj);
   - supplementary audit and reference-QA figures.
   - PC-based versions are archived in `outputs/figures/pc_rtc/`.
10. **Poster.** `poster/poster_editable.pptx` and `poster/poster_final.pdf`.
    - 48 × 48 in; native text, 2 native charts, 3 native tables.
    - Rebuilt from the GEE results with v2 (section 10 table read from `v2_preregistered_criteria.csv`).
    - The v1/PC version is archived in `poster/archive_v1_pc/`.
11. **Presentation.** Pitches (EN/BN), judges' Q&A (general and results, including v2 and the root cause), figure explanations, team roles.
12. **Final audit.** `outputs/reports/final_audit.md` (`--source gee`) shows 64 PASS and 0 FAIL. It now also checks:
    - the v2 frozen-file checksums;
    - that the Sirajganj SAR was created after the code freeze;
    - recomputation of the criteria flags.

## 2. Key verified results
### 2.1 Scene budget (Kurigram 2025, GEE σ⁰, means over all C(8,k) subsets)
| Method | k = 1 | k = 3 | k = 8 |
|---|---|---|---|
| Published thresholds, F1 | 0.56 | 0.71 | 0.82 |
| Published thresholds, false erosion | 74 ha | 24 ha | 7.5 ha |
| 2024-tuned baseline, F1 | 0.70 | 0.79 | 0.82 |

The tuned thresholds came out close to the published ones. Class-separability (Youden) thresholds were poor (F1 0.35–0.46).

### 2.2 Agreement + abstention (v1, A+G)
- **Decided pixels:** F1 0.85–0.90, false erosion < 3 ha.
- **Cost:** coverage 88–91 %; 14–21 ha of the 58.8 ha reference erosion was abstained.
- **Counting UNCERTAIN as non-erosion:** F1 0.66–0.77, never above the tuned baseline (0.76–0.82). This held on Sirajganj too.
- **31 Jan scene:**
  - alone, tuned baseline: 160 ha of false erosion;
  - 2-scene subsets containing it: tuned baseline 12.1 ha, A+G 1.6 ha.

### 2.3 v2 triage + prioritized review (`docs/sage_river_v2_results.md`)
- **No automatic gain.** v2 high-confidence F1 equals v1 and is below the tuned baseline in all 16 reach × k cells.
- **Prioritized vs random review at 20 % effort.**

  | Evaluation | Recovered (v2 prioritized) | Random mean |
  |---|---|---|
  | Kurigram 2025, k = 3 (exploratory) | 21.3 ha | 5.5 ha |
  | Sirajganj 2025, k = 3 (independent) | 7.2 ha | 2.1 ha |
  | Sirajganj 2024 transfer, k = 3 | 19.7 ha | 8.0 ha |

- **Pre-registered criteria:**
  - Kurigram (exploratory): 4/4 cells met.
  - Independent evaluations: 11/12 met. The failure is the primary local test at k = 8, where prioritized equals the random 95th percentile.
  - Several independent margins are very small.
- **Caveats:**
  - The reviewer is a simulated oracle.
  - REVIEW covers 184–1218 ha.
  - In the Sirajganj 2024 transfer, randomly reviewing v1's UNCERTAIN pixels was about as good at 20 % effort (k = 8: 15.2 vs 14.9 ha).
- **Single-scene maps remain unreliable.** At k = 1 on 31 Jan, v2 high-confidence still contains 104 ha of false erosion.

## 3. Status table
| Component | Status | Evidence |
|---|---|---|
| Literature review | Completed with limitations | `docs/literature_review.md` (F&F and Shampa full text; others abstract-level) |
| Research gap | Completed and verified | `docs/research_gap.md`; cautious "to our knowledge" wording |
| GEE authentication | Completed and verified | project initialised; `*_gee.*` outputs |
| Study areas | Completed and verified | Kurigram `data/aoi/`; Sirajganj `data/reaches/sirajganj/aoi/` |
| Scene inventory | Completed and verified | GEE, ASF and PC (`sentinel1_*.csv`) |
| Baseline (GEE σ⁰) | Completed and verified | published, calibrated, F1-tuned |
| Root-cause audit | Completed and verified | `root_cause_audit_20260131.md`; interpretation (boro-rice flooding) not field-verified |
| Independent reference | Completed with limitations | S2 optical reference; AI point check; Sirajganj 2025 is weak (12 ha, 67 %) |
| SAGE-River v1 | Completed and verified | `sage_methods.py`, `experiment_A/B_*_gee.csv` |
| SAGE-River v2 | Completed and verified (modest, review-dependent gain) | `sage_v2.py`, `transfer_eval.py`, `v2_*` tables, criteria CSV |
| Independent evaluation | Completed with limitations | one independent reach, two years; the primary test is weak |
| Poster PPTX / PDF | Completed with limitations | 48 × 48 in; other team members, department and university are placeholders |
| Presentation | Completed and verified | `presentation/*.md` |

## 4. What remains (human actions)
1. Spot-check at least 20 validation points per reach:
   - `data/reference/validation_points_2025.csv`;
   - `data/reaches/sirajganj/reference/validation_points_2025.csv`;
   - use the column `team_check`.
2. Fill in the placeholders in the PPTX (team members, department, university). Then re-export with `poster/export_pdf.ps1` and check the PDF at 100 % zoom.
3. Optional: rehearse the "no automatic gain / oracle review" answers in `presentation/judges_qa_results.md`.

## 5. What cannot be claimed
- That SAGE-River (v1 or v2) is a better automatic classifier than a tuned baseline.
- That review gains hold for a real (non-oracle) analyst.
- Field-validated accuracy.
- Generalisation beyond two reaches of one river.
- Any forecasting skill, a PINN or a physics model.
- That the 31 Jan dark patches are flooded paddies (consistent with that, but not field-verified).
- That the Kurigram 2025 v2 numbers are held-out evidence (they are exploratory).
