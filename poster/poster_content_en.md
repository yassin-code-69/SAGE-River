# How Many Sentinel-1 Scenes Are Enough?
## Scene-Count Sensitivity and Agreement-Gated Reliability of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh
[Team member names] · Department of CSE, [University] · [Corresponding e-mail] — IEEE BUBT Academic Research Showcase 2026, Track 1

**Key message:** 2–3 Sentinel-1 scenes already give stable erosion maps; agreement + abstention removes almost all false erosion and survives a bad scene — but abstains on ~12 % of the bank strip, where 23–36 % of the true erosion lies.

### Abstract
Sentinel-1 radar maps riverbank erosion through clouds, but a quick post-monsoon map has few comparable scenes: over our 12-km Jamuna reach (Kurigram) only 2–3 ascending scenes each November. We reproduced the Freihardt & Frey (2023) threshold rule and scored every subset of 1–8 post-monsoon scenes (121 maps per method) for the 2025 monsoon against an independent Sentinel-2 reference (58.8 ha of outer-bank erosion), with all thresholds and rules tuned on 2024 only. For the best baselines, mean F1 rose from 0.67–0.70 with one scene to 0.77–0.80 with 3–8 scenes, and false erosion dropped sharply after 2–3 scenes. Adding m-of-k agreement and a ±δ abstention band (SAGE-River) raised F1 on decided pixels to 0.86–0.90 with ≤ 2.4 ha false erosion and resisted an anomalous scene, but left 9–13 % of pixels UNCERTAIN, containing 23–36 % of the true erosion; counting those as non-erosion, it did not consistently beat the tuned baseline. Reliability gains carry a coverage cost that must be reported.

### Real-world problem
- The Jamuna erodes farmland and homesteads every monsoon — CEGIS monitored ~348 ha of Jamuna bank erosion in 2025.
- Post-monsoon maps of lost land help agencies prepare before the next monsoon.
- Sentinel-1 radar sees through clouds, but a quick map can use only a few comparable scenes (2–3 ascending scenes in November over our reach).

### Existing research → gap
- Freihardt & Frey 2023: Sentinel-1/GEE threshold erosion mapping on the Jamuna; window/filter effects on backscatter; land-cover OA 87.5–90.6 %; erosion checked visually.
- Shampa et al. 2025: Delft3D early warning (forecasting, no SAR). CEGIS: operational Landsat prediction.
- m-of-k confirmation and abstention exist in flood/forest SAR products (MCDWD, RADD, GFM, Li et al. 2026).
- **Gap:** to our knowledge, no reviewed study measured erosion-map accuracy across Sentinel-1 scene budgets with agreement + abstention + coverage against an independent optical reference.

### Research questions
RQ1 scene count vs P/R/F1/IoU · RQ2 agreement vs false erosion · RQ3 abstention vs coverage · RQ4 timeliness vs reliability

### Study area & data
Jamuna (Brahmaputra) reach upstream of Chilmari, Kurigram district (12 km); AOI 26 × 12 km, centre 25.670°N 89.760°E. SAR source: Planetary Computer sentinel-1-rtc γ⁰ VV, R114 ascending. Reference: Sentinel-2 L2A.

### Results (test monsoon 2025, frozen parameters; mean over all C(8,k) subsets)

| k | Method | Precision | Recall | F1 | IoU | Coverage | False ha | Missed ha |
|---|---|---|---|---|---|---|---|---|
| 1 | Baseline (published T) | 0.81 | 0.64 | 0.70 | 0.55 | 100% | 22.5 | 21.0 |
| 1 | Baseline (calibrated T) | 0.23 | 0.78 | 0.35 | 0.21 | 100% | 172.7 | 12.8 |
| 1 | Baseline (F1-tuned T) | 0.72 | 0.68 | 0.67 | 0.53 | 100% | 34.1 | 18.8 |
| 1 | G: gating | 0.41 | 0.81 | 0.53 | 0.37 | 92% | 73.7 | 10.0 |
| 2 | Baseline (published T) | 0.92 | 0.64 | 0.76 | 0.61 | 100% | 3.6 | 21.0 |
| 2 | Baseline (calibrated T) | 0.24 | 0.79 | 0.37 | 0.23 | 100% | 159.8 | 12.1 |
| 2 | Baseline (F1-tuned T) | 0.79 | 0.69 | 0.73 | 0.58 | 100% | 13.6 | 18.3 |
| 2 | A: majority | 0.49 | 0.74 | 0.58 | 0.42 | 100% | 51.2 | 15.0 |
| 2 | G: gating | 0.48 | 0.82 | 0.60 | 0.43 | 91% | 52.6 | 9.3 |
| 2 | SAGE-River A+G | 0.94 | 0.79 | 0.86 | 0.75 | 91% | 2.4 | 9.4 |
| 3 | Baseline (published T) | 0.95 | 0.64 | 0.77 | 0.62 | 100% | 1.9 | 21.0 |
| 3 | Baseline (calibrated T) | 0.23 | 0.80 | 0.36 | 0.22 | 100% | 162.1 | 11.6 |
| 3 | Baseline (F1-tuned T) | 0.88 | 0.70 | 0.78 | 0.64 | 100% | 5.7 | 17.7 |
| 3 | A: majority | 0.30 | 0.79 | 0.43 | 0.28 | 100% | 112.4 | 12.3 |
| 3 | A: unanimous | 0.70 | 0.72 | 0.70 | 0.55 | 100% | 20.6 | 16.4 |
| 3 | G: gating | 0.52 | 0.83 | 0.63 | 0.47 | 90% | 43.0 | 8.8 |
| 3 | SAGE-River A+G | 0.98 | 0.78 | 0.87 | 0.77 | 88% | 0.5 | 8.4 |
| 6 | Baseline (published T) | 0.96 | 0.64 | 0.77 | 0.62 | 100% | 1.7 | 21.0 |
| 6 | Baseline (calibrated T) | 0.26 | 0.81 | 0.40 | 0.25 | 100% | 134.8 | 11.2 |
| 6 | Baseline (F1-tuned T) | 0.84 | 0.75 | 0.79 | 0.66 | 100% | 8.8 | 14.5 |
| 6 | A: majority | 0.47 | 0.78 | 0.58 | 0.41 | 100% | 53.9 | 12.8 |
| 6 | A: unanimous | 0.94 | 0.68 | 0.79 | 0.65 | 100% | 2.8 | 18.7 |
| 6 | G: gating | 0.67 | 0.84 | 0.74 | 0.59 | 89% | 23.1 | 8.5 |
| 6 | SAGE-River A+G | 0.97 | 0.83 | 0.89 | 0.81 | 87% | 1.3 | 7.7 |
| 8 | Baseline (published T) | 0.96 | 0.64 | 0.77 | 0.62 | 100% | 1.7 | 21.1 |
| 8 | Baseline (calibrated T) | 0.28 | 0.81 | 0.42 | 0.27 | 100% | 119.8 | 11.1 |
| 8 | Baseline (F1-tuned T) | 0.86 | 0.75 | 0.80 | 0.67 | 100% | 7.5 | 14.5 |
| 8 | A: majority | 0.46 | 0.78 | 0.58 | 0.41 | 100% | 54.8 | 12.7 |
| 8 | A: unanimous | 0.96 | 0.67 | 0.79 | 0.65 | 100% | 1.5 | 19.6 |
| 8 | G: gating | 0.73 | 0.84 | 0.78 | 0.64 | 89% | 16.5 | 8.4 |
| 8 | SAGE-River A+G | 0.97 | 0.83 | 0.90 | 0.81 | 87% | 1.2 | 7.6 |

**Early maps (Exp. B):** maps possible on 8 Nov, 20 Nov and 2 Dec 2025 reached F1 0.73, 0.75 and 0.78 (tuned baseline, full coverage). A+G reached 0.83–0.85 on decided pixels but only 0.66–0.72 with UNCERTAIN counted as non-erosion. 95 % of the reference erosion was already visible by mid-December, so later erosion barely affected early maps.

### Key findings
- More scenes → fewer false alarms: published-rule false erosion fell from 22 ha (1 scene) to 2 ha (3 scenes); F1 plateaued (0.77) after 3 scenes.
- SAGE A+G: decided-pixel F1 0.86–0.90, ≤ 2.4 ha false erosion — but 9–13 % abstained, holding 23–36 % of true erosion.
- UNCERTAIN counted as non-erosion: A+G 0.66–0.77 vs tuned baseline 0.73–0.80 → no consistent full-coverage gain (only k=2: 0.74 vs 0.73).
- One anomalous scene (31 Jan) gave 197 ha false erosion with the tuned baseline (150 ha published); 2-scene A+G maps containing it stayed at ~1 ha.

### Contributions
- Erosion-map-level scene-budget benchmark (121 scene subsets, up to 7 decision rules) of the published Sentinel-1/GEE method against an independent Sentinel-2 reference.
- Agreement + abstention rules reported with coverage and abstained-erosion area — no hidden pixels.
- Threshold choice dominates: class-separability thresholds gave F1 0.35–0.42; erosion-tuned or published ones 0.67–0.80.
- Open, reproducible pipeline (Python + GEE scripts, CSVs, frozen parameters).

### Limitations
- One 12-km reach and one test monsoon; Sentinel-2 is an optical reference, not field truth (visual point check: 92 % / 100 % agreement, AI-interpreted, team spot-check pending).
- SAR from Planetary Computer RTC γ⁰ (Earth Engine σ⁰ not run: no project ID); 2024 pool had 6 of 8 scenes.
- Coverage target (≥ 90 %, set on 2024) fell to 87–88 % in 2025 for k ≥ 3; overlapping subsets are not independent samples.
- Historical mapping only — no forecasting, no PINN.

Sentinel-2 is an independent optical reference, not field ground truth. Historical erosion mapping — not forecasting, not a PINN.