# Experiment Design

## Periods (temporal hold-out)
| Role | Monsoon | SAR pre composite | SAR post-monsoon pool | S2 reference (pre → post) |
|---|---|---|---|---|
| Validation (all tuning) | 2024 | 1 Nov 2023 – 30 Apr 2024 | 1 Nov 2024 – 31 Jan 2025 | Feb–Mar 2024 → Feb–Mar 2025 |
| Test (frozen parameters) | 2025 | 1 Nov 2024 – 30 Apr 2025 | 1 Nov 2025 – 31 Jan 2026 | Feb–Mar 2025 → Feb–Mar 2026 |

Notes: the 2024 post window and the 2025 pre window overlap in time (Nov 2024–Jan 2025), and the Feb–Mar 2025 optical composite is the "post" of 2024 and the "pre" of 2025. This is a mild dependence, not label leakage: the 2025 reference labels (2025→2026 change) are never seen during tuning.

## Update 11 Nov 2026 ~03:20
- **GEE σ⁰ is the primary source.** Earth Engine became available, so `--source gee` was run for Kurigram; per the pre-stated rule it is now primary. The PC γ⁰ runs are kept as an adapted cross-check.
- **SAGE-River v2** (quality-aware, erosion-sensitive mapping with prioritized review) was pre-registered in `docs/sage_river_v2_design.md`. Checksums and freeze times are in `docs/sage_river_v2_design.md5`.
- **Result status:**
  - Kurigram 2025 v2 results are **exploratory**, because the v2 idea came from inspecting them.
  - Sirajganj–Kazipur 2025 is the **independent test**: new reach; v2 design and code frozen before its SAR data were processed.

- **v2 results:** `docs/sage_river_v2_results.md`. The pre-registered criteria are in `outputs/tables/v2_preregistered_criteria.csv`:
  - met in 11 of 12 independent tests;
  - failed for Sirajganj 2025 at k = 8;
  - no automatic accuracy gain over the tuned baseline.

## Data source switch
`s1_stack.py --source gee` (COPERNICUS/S1_GRD σ⁰, the baseline's own data) is preferred. If Earth Engine is not authorised, `--source pc` uses Planetary Computer `sentinel-1-rtc` (γ⁰ terrain-flattened, no angle band). The source is stored in every output file name and in the CSV `source` column. Published dB thresholds are defined for GEE σ⁰ and are reported for reference only when the source is `pc`.

## Methods compared (same scenes, same preprocessing, same reference, same evaluation domain)
| ID | Rule | Abstains? |
|---|---|---|
| BASE_published | F&F: pre_mean > −13.2 dB AND post_mean(k) < −12.7 dB | no |
| BASE_calibrated | same rule, thresholds calibrated on 2024 by class separability (T_pre; T_post(k)) | no |
| BASE_F1tuned | same rule, (T_pre, T_post) chosen on 2024 to maximise erosion F1 (grid ±2 dB / ±3 dB, 0.5 dB steps) — **fairness control**: gives the baseline the same erosion-label tuning advantage that SAGE's m and δ receive (added after inspecting only 2024 tables; run 1 without it archived in `outputs/reports/run1_without_F1tuned_baseline/`) | no |
| A_majority | pre_mean > T_pre AND #{scenes < T_scene} ≥ ⌊k/2⌋+1 | no (k ≥ 2) |
| A_unanimous | … ≥ k | no (k ≥ 3) |
| G_gated | BASE_calibrated with ±δ abstention band on pre_mean and post_mean (Kleene AND) | yes |
| AG_agree+gate | per-scene votes with ±δ band, m-of-k, Kleene AND with pre | yes |

## Calibration (2024 only) — documented procedure
1. Pixels whose S2 class (Feb–Mar) is VEG vs WATER/SAND are used as class samples (whole AOI).
2. T_pre: threshold on the SAR pre composite maximising Youden's J (TPR−FPR) between VEG and WATER/SAND (S2 Feb–Mar 2024).
3. T_post(k): same on k-scene composites of the 2024 post pool (all combinations pooled; 60,000 random pixels per class, seed 20251108) vs S2 Feb–Mar 2025 classes. T_scene = T_post(1) is used for per-scene votes.
4. m and δ: for each k, grid δ ∈ {0, 0.5, 1.0, 1.5, 2.0} dB and m ∈ {majority, unanimous}; choose maximum mean F1 on decided pixels subject to mean decision coverage ≥ 0.90 (rule fixed in `config.py` before any 2025 run).
5. Frozen to `outputs/tables/selected_parameters_<source>.json` with a timestamp before 2025 metrics are computed.

## Experiment A — controlled scene budget (RQ1–RQ3)
Pool = all R114-ascending acquisitions 1 Nov – 31 Jan (verified: 8 per season). For k ∈ {1, 2, 3, 6, 8} **all** C(8,k) combinations are evaluated (8, 28, 56, 28, 1 = 121 subsets). Overlapping subsets are not independent replicates: the reported SD/range is subset variability, not a confidence interval.

## Experiment B — chronological early mapping (RQ4)
First 1, 2, 3 acquisitions after 1 November; the map date is the last acquisition used. Scored against (a) the cumulative Feb–Mar reference and (b) an "as-of mid-December" reference = cumulative erosion pixels already sand/water in the S2 10 Nov–15 Dec composite (erosion not yet visible by mid-December is excluded from (b) rather than counted as an early-map error).

## Metrics
Precision, Recall, F1, IoU on decided pixels; decision coverage; uncertain %; false-erosion area (ha); missed-erosion area (ha); abstained reference-erosion area (ha); all-pixel recall (abstained erosion counted as missed). 10 m pixel = 0.01 ha. Overall accuracy is not used.
