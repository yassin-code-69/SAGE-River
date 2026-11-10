# How Many Sentinel-1 Scenes Are Enough?
## Scene-Count Sensitivity, Agreement-Gated Reliability and Prioritized Review of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh
Yassin Bhuyan Alindo  [+ team members]  ·  Department of CSE, [University]  ·  alindobhuyan60@gmail.com — IEEE BUBT Academic Research Showcase 2026, Track 1 (poster 48 × 48 in)

**Key message:** 2–3 Sentinel-1 scenes give usable erosion maps. Abstention removes false alarms but hides real erosion; triage + prioritized review recovers most of it with 10–20 % review effort. There is no automatic accuracy gain.

### Abstract
Sentinel-1 radar maps riverbank erosion through clouds, but a quick post-monsoon map has few comparable scenes: only 2–3 ascending scenes each November over our 12-km Jamuna reach (Kurigram). We reproduced the Freihardt & Frey (2023) threshold rule on Earth Engine σ⁰ and scored every subset of 1–8 post-monsoon scenes (121 maps per rule) against an independent Sentinel-2 reference, tuning on 2024 only. With the published thresholds, false erosion fell from 74 ha (1 scene) to 24 ha (3 scenes), and F1 rose from 0.56 to 0.71, reaching 0.82 with 8 scenes. Agreement + abstention (v1) cut false erosion below 3 ha. However, it abstained on 9–12 % of pixels holding 14–21 ha of real erosion, so it did not beat a tuned baseline. A pre-registered v2 sorts pixels into high-confidence / review / stable and ranks review patches using map-date SAR only. On an independent reach (Sirajganj–Kazipur), prioritized review beat random review in 11 of 12 pre-registered tests, often by small margins. v2 adds no automatic accuracy gain.

### Real-world problem
- The Jamuna erodes farmland and homesteads every monsoon — CEGIS monitored ~348 ha of Jamuna bank erosion in 2025.
- Post-monsoon maps of lost land help agencies prepare before the next monsoon.
- Radar sees through clouds, but a quick map has few comparable scenes (2–3 ascending scenes per November over our reach).

### Existing research → gap
- Freihardt & Frey 2023: Sentinel-1/GEE threshold erosion mapping on the Jamuna; window/filter effects on backscatter; land-cover OA 87.5–90.6 %; erosion checked visually.
- Shampa et al. 2025: Delft3D early warning (forecasting, no SAR). CEGIS: operational Landsat prediction.
- m-of-k confirmation and abstention exist in flood/forest SAR products (MCDWD, RADD, GFM, Li et al. 2026).
- **Gap:** to our knowledge, no reviewed study measured erosion-map accuracy across Sentinel-1 scene budgets with agreement + abstention + coverage against an independent optical reference.

### Research questions
RQ1 scene count vs P/R/F1/IoU · RQ2 agreement vs false erosion · RQ3 abstention vs coverage · RQ4 timeliness vs reliability · RQ5 can map-date SAR evidence rank possible-erosion patches so a limited review recovers more erosion than random review, on an independent reach?

### Study area & data
Jamuna (Brahmaputra) reach upstream of Chilmari, Kurigram district (12 km); AOI 26 × 12 km, centre 25.670°N 89.760°E. SAR source: GEE COPERNICUS/S1_GRD σ⁰ VV, R114 ascending. Reference: Sentinel-2 L2A.

### Results (test monsoon 2025, frozen parameters; mean over all C(8,k) subsets)

| k | Rule | Precision | Recall | F1 | F1 (U = non) | IoU | Coverage | False ha | Missed ha | Abstained ha |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Baseline (published T) | 0.46 | 0.77 | 0.56 | 0.56 | 0.40 | 100% | 74.4 | 13.7 | 0.0 |
| 1 | Baseline (calibrated T) | 0.23 | 0.78 | 0.35 | 0.35 | 0.21 | 100% | 172.5 | 12.8 | 0.0 |
| 1 | Baseline (F1-tuned T) | 0.80 | 0.67 | 0.70 | 0.70 | 0.56 | 100% | 24.3 | 19.7 | 0.0 |
| 1 | G: gating | 0.39 | 0.81 | 0.51 | 0.49 | 0.35 | 93% | 83.3 | 9.8 | 6.6 |
| 2 | Baseline (published T) | 0.57 | 0.77 | 0.64 | 0.64 | 0.48 | 100% | 46.0 | 13.5 | 0.0 |
| 2 | Baseline (calibrated T) | 0.26 | 0.79 | 0.38 | 0.38 | 0.24 | 100% | 149.2 | 12.4 | 0.0 |
| 2 | Baseline (F1-tuned T) | 0.89 | 0.67 | 0.76 | 0.76 | 0.62 | 100% | 5.2 | 19.4 | 0.0 |
| 2 | A: majority | 0.49 | 0.74 | 0.59 | 0.59 | 0.42 | 100% | 50.0 | 15.0 | 0.0 |
| 2 | G: gating | 0.47 | 0.82 | 0.59 | 0.56 | 0.43 | 93% | 58.4 | 9.4 | 6.7 |
| 2 | SAGE-River A+G | 0.93 | 0.79 | 0.85 | 0.73 | 0.75 | 91% | 2.8 | 9.3 | 14.2 |
| 3 | Baseline (published T) | 0.67 | 0.77 | 0.71 | 0.71 | 0.56 | 100% | 24.1 | 13.3 | 0.0 |
| 3 | Baseline (calibrated T) | 0.25 | 0.80 | 0.38 | 0.38 | 0.24 | 100% | 149.0 | 11.9 | 0.0 |
| 3 | Baseline (F1-tuned T) | 0.88 | 0.72 | 0.79 | 0.79 | 0.66 | 100% | 6.0 | 16.2 | 0.0 |
| 3 | A: majority | 0.30 | 0.79 | 0.44 | 0.44 | 0.28 | 100% | 110.5 | 12.4 | 0.0 |
| 3 | A: unanimous | 0.71 | 0.72 | 0.71 | 0.71 | 0.55 | 100% | 19.8 | 16.3 | 0.0 |
| 3 | G: gating | 0.50 | 0.83 | 0.62 | 0.59 | 0.45 | 91% | 46.3 | 8.9 | 6.8 |
| 3 | SAGE-River A+G | 0.98 | 0.77 | 0.87 | 0.66 | 0.76 | 89% | 0.5 | 8.6 | 21.0 |
| 6 | Baseline (published T) | 0.84 | 0.78 | 0.81 | 0.81 | 0.68 | 100% | 8.7 | 13.2 | 0.0 |
| 6 | Baseline (calibrated T) | 0.29 | 0.80 | 0.42 | 0.42 | 0.27 | 100% | 117.4 | 11.6 | 0.0 |
| 6 | Baseline (F1-tuned T) | 0.85 | 0.77 | 0.81 | 0.81 | 0.68 | 100% | 8.2 | 13.5 | 0.0 |
| 6 | A: majority | 0.48 | 0.78 | 0.59 | 0.59 | 0.42 | 100% | 51.4 | 12.9 | 0.0 |
| 6 | A: unanimous | 0.94 | 0.69 | 0.79 | 0.79 | 0.66 | 100% | 2.7 | 18.5 | 0.0 |
| 6 | G: gating | 0.67 | 0.84 | 0.74 | 0.70 | 0.59 | 91% | 21.9 | 8.5 | 6.8 |
| 6 | SAGE-River A+G | 0.96 | 0.83 | 0.89 | 0.76 | 0.81 | 89% | 1.4 | 7.5 | 14.2 |
| 8 | Baseline (published T) | 0.86 | 0.78 | 0.82 | 0.82 | 0.69 | 100% | 7.5 | 13.1 | 0.0 |
| 8 | Baseline (calibrated T) | 0.32 | 0.81 | 0.46 | 0.46 | 0.30 | 100% | 100.2 | 11.5 | 0.0 |
| 8 | Baseline (F1-tuned T) | 0.86 | 0.77 | 0.82 | 0.82 | 0.69 | 100% | 7.1 | 13.5 | 0.0 |
| 8 | A: majority | 0.47 | 0.78 | 0.59 | 0.59 | 0.42 | 100% | 51.9 | 12.6 | 0.0 |
| 8 | A: unanimous | 0.96 | 0.67 | 0.79 | 0.79 | 0.66 | 100% | 1.5 | 19.3 | 0.0 |
| 8 | G: gating | 0.73 | 0.83 | 0.78 | 0.74 | 0.64 | 91% | 15.7 | 8.6 | 6.7 |
| 8 | SAGE-River A+G | 0.97 | 0.83 | 0.90 | 0.77 | 0.81 | 88% | 1.2 | 7.4 | 13.9 |

**Early maps (Exp. B):** maps possible on 8 Nov, 20 Nov and 2 Dec 2025 reached F1 0.73, 0.76 and 0.79 (tuned baseline, full coverage). A+G reached 0.82–0.84 on decided pixels, but only 0.66–0.70 with UNCERTAIN counted as non-erosion. Against an 'as-of mid-December' reference, the tuned baseline scored 0.75–0.82.

### A bad scene, audited (31 Jan 2026)
Root-cause audit: no processing error. NoData, alignment (0-px shift), radiometry, mosaics and thresholds were all checked. The dark 31 Jan 2026 patches are temporarily inundated fields, a median 584 m from the channel. Evidence: GEE σ⁰ −15.0 dB vs −8.2 dB on control fields; also dark in the R150 descending scene; Sentinel-2 shows 88–99 % water from 28 Jan to 12 Feb. The scene was kept in every experiment. Alone it gives 160 ha of false erosion (tuned T); 2-scene A+G maps that contain it average 1.6 ha.

### SAGE-River v2: triage + prioritized review (20 % review effort, simulated oracle reviewer)

| Evaluation | Role | k | Tuned F1 | v2 HC F1 | Recovered v2 / random / v1-U (ha) | Random p95 (ha) | (a) | (b) |
|---|---|---|---|---|---|---|---|---|
| Kurigram 2025 | EXPLORATORY | 2 | 0.76 | 0.74 | 14.76 / 4.20 / 3.28 | 10.37 | met | met |
| Kurigram 2025 | EXPLORATORY | 3 | 0.79 | 0.66 | 21.31 / 5.51 / 7.78 | 16.12 | met | met |
| Kurigram 2025 | EXPLORATORY | 6 | 0.81 | 0.76 | 14.16 / 3.77 / 4.85 | 9.79 | met | met |
| Kurigram 2025 | EXPLORATORY | 8 | 0.82 | 0.77 | 13.62 / 3.65 / 4.93 | 9.57 | met | met |
| Sirajganj 2025 (local calibration) | INDEPENDENT (pre-registered primary) | 2 | 0.43 | 0.12 | 8.90 / 2.56 / 2.29 | 8.82 | met | met |
| Sirajganj 2025 (local calibration) | INDEPENDENT (pre-registered primary) | 3 | 0.46 | 0.33 | 7.22 / 2.09 / 1.48 | 7.17 | met | met |
| Sirajganj 2025 (local calibration) | INDEPENDENT (pre-registered primary) | 6 | 0.49 | 0.14 | 10.58 / 3.06 / 3.56 | 10.56 | met | met |
| Sirajganj 2025 (local calibration) | INDEPENDENT (pre-registered primary) | 8 | 0.52 | 0.15 | 10.82 / 3.55 / 3.84 | 10.82 | NOT met | met |
| Sirajganj 2024 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 2 | 0.65 | 0.61 | 13.43 / 5.57 / 6.93 | 11.69 | met | met |
| Sirajganj 2024 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 3 | 0.68 | 0.54 | 19.67 / 8.01 / 16.83 | 18.20 | met | met |
| Sirajganj 2024 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 6 | 0.72 | 0.63 | 14.38 / 6.02 / 13.09 | 13.48 | met | met |
| Sirajganj 2024 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 8 | 0.73 | 0.64 | 14.88 / 6.23 / 15.24 | 13.50 | met | met |
| Sirajganj 2025 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 2 | 0.51 | 0.26 | 6.84 / 1.73 / 1.66 | 6.34 | met | met |
| Sirajganj 2025 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 3 | 0.53 | 0.10 | 9.57 / 2.74 / 3.95 | 9.50 | met | met |
| Sirajganj 2025 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 6 | 0.54 | 0.30 | 8.49 / 2.66 / 3.30 | 8.43 | met | met |
| Sirajganj 2025 (Kurigram parameters) | INDEPENDENT TRANSFER (addendum) | 8 | 0.55 | 0.30 | 8.82 / 2.79 / 3.86 | 8.80 | met | met |

Source: outputs/tables/v2_preregistered_criteria.csv. Details: docs/sage_river_v2_results.md

### Key findings
- Scene budget: published-rule false erosion 74 → 24 → 7.5 ha (k = 1 → 3 → 8); tuned-baseline F1 0.70 → 0.79 → 0.82.
- v1 A+G: decided-pixel F1 0.85–0.90 with < 3 ha false erosion, but 14–21 ha of real erosion was abstained. Counting UNCERTAIN as non-erosion, it was no better than the tuned baseline (Kurigram and Sirajganj).
- v2 at 20 % review (Kurigram k = 3, exploratory): 21.3 ha recovered vs 5.5 ha for random review. Independent Sirajganj: both criteria met in 11/12 tests; failed at k = 8 (local 2025).
- No automatic gain: v2 high-confidence F1 = v1, below the tuned baseline in every test. Single-scene maps still fail (31 Jan: 104 ha false).

### Contributions
- Erosion-map scene-budget benchmark (121 subsets × 7 rules) of the published Sentinel-1/GEE method against an independent Sentinel-2 reference.
- Abstention reported with coverage and abstained-erosion area — no hidden pixels.
- Three-class triage + map-date review ranking, pre-registered (md5 + timestamps) and tested on an independent reach.
- Root-cause audit of a failing scene (inundated fields, three independent sources); open pipeline with all CSVs.

### Limitations
- Sentinel-2 is an optical reference, not field truth. Sirajganj 2025 has only 12 ha of erosion, with 67 % agreement on erosion points.
- The reviewer is simulated as an oracle, and the REVIEW class covers 184–1218 ha. In Sirajganj 2024, randomly reviewing v1 UNCERTAIN pixels was almost as good at 20 % effort.
- Kurigram 2025 v2 numbers are exploratory. Only two reaches of one river were tested, and overlapping subsets are not independent samples.
- Historical mapping only — no forecasting, no PINN.

Corresponding author: Yassin Bhuyan Alindo · alindobhuyan60@gmail.com

Sentinel-2 is an independent optical reference, not field ground truth. Historical erosion mapping — not forecasting, not a PINN.