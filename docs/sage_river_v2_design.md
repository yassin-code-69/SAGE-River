# SAGE-River v2 — Quality-Aware, Erosion-Sensitive Mapping with Prioritized Review
**Pre-registered design. Written 11 Nov 2026 ~02:55 BST, BEFORE any SAR data of the independent reach were downloaded or inspected.**

## 0. Why v2 (what v1 got wrong)
Results of v1 (Kurigram, 2025 test):
- High precision on decided pixels.
- 23–36 % of the reference erosion fell into UNCERTAIN, mostly at bank edges.
- Full-area F1 was not consistently better than a tuned baseline.

Root-cause audit of the 31 Jan 2026 scene (`outputs/reports/root_cause_audit_20260131.md`) found no implementation error. The dark patches are inundated fields; the evidence:
- they are field-shaped and off-channel (median 295 m from the channel);
- they appear in GEE σ⁰ and in the R150 descending scene;
- Sentinel-2 shows MNDWI > 0 on 28 Jan–12 Feb.

Two error mechanisms follow:
1. **Temporary off-channel water** creates false erosion.
2. **Bank-edge pixels** near the threshold are real erosion but get abstained.

v2 addresses both, using **only information available at the mapping date** (SAR pre composite and the k post scenes).

## 1. Inputs
- SAR pre composite and post scenes of the subset.
- Parameters frozen by the v1 calibration on the reach's validation year (`selected_parameters_<tag>.json`):
  - T_pre;
  - T_scene;
  - m-rule;
  - δ_AG for k ≥ 2, or δ_G for k = 1.

  δ below means δ_AG, or δ_G when k = 1.

## 2. Map-date geometry from SAR only
- **SAR pre-event channel:** pixels with pre_comp < T_pre, 8-connected. Keep components ≥ 1 km² (the main channel complex).
- **Bank buffer:** the SAR channel dilated by 3 px (30 m).
- **dist_bank:** Euclidean distance (m) from the SAR channel.
- The later Sentinel-2 reference is never used here.

## 3. Pixel evidence
| Quantity | Definition |
|---|---|
| votes_conf | # post scenes < T_scene − δ |
| votes_poss | # post scenes < T_scene + δ |
| vote_frac | votes_conf / k |
| Δ (change magnitude) | pre_comp − mean(post) in dB |
| pre_margin | pre_comp − T_pre |
| v1_conf | v1 A+G confident erosion (identical to v1) |

## 4. Three-class decision
- **candidate:** pre_comp > T_pre − δ AND votes_poss ≥ 1, plus all v1_conf pixels.
- **patches:** 8-connected components of the candidate mask.
- **HIGH-CONFIDENCE EROSION:** v1_conf pixels whose patch touches the bank buffer.
- **POSSIBLE EROSION — REVIEW:** candidate pixels that are not HC, in patches whose min dist_bank ≤ D_review. This includes v1_conf pixels in off-bank patches within D_review.
- **LIKELY STABLE:** everything else, including off-bank patches beyond D_review ("likely temporary inundation or noise").

**D_review** is chosen on the validation year. It is the smallest value in {100, 200, 300, 500, 750, 1000} m for which ≥ 90 % of validation-year reference-erosion candidate pixels (non-HC) lie in patches with min dist_bank ≤ D_review.

## 5. Prioritized review (ranking)
- **Unit:** REVIEW patches.
- **Features**, all from map-date SAR:
  1. mean Δ;
  2. mean vote_frac;
  3. mean pre_margin;
  4. min dist_bank;
  5. log10(area ha);
  6. touches bank buffer (0/1);
  7. fraction of v1_conf pixels.
- **Model:** logistic regression (scikit-learn; standardized features, C = 1.0, class_weight = "balanced", max_iter = 1000).
- **Target:** patch reference-eroded fraction ≥ 0.5.
- **Training data:** pooled over all validation-year subsets (k ∈ K_LIST available in that year). Training uses the validation year only.
- **Priority:** predicted probability, descending; ties broken by area.

## 6. Review simulation (evaluation only)
- **Budget b:** reviewed area as a fraction of the REVIEW area ∈ {0, 5, 10, 20, 30, 50, 100} %, also reported in ha.
- **Oracle reviewer:** inside reviewed patches, reference-erosion pixels are recovered and all other pixels are rejected (no false positives). This is a *simulation of a human analyst*; it is not a claim about human accuracy.
- **Metrics at each b:**
  - recovered erosion (ha);
  - missed erosion (ha) = reference erosion not in HC ∪ reviewed;
  - false erosion (ha) = HC false positives;
  - review effort (ha);
  - decision coverage = (HC + STABLE) / domain;
  - F1 with HC ∪ recovered treated as erosion.
- **Random review:** 500 random patch orders (seed 20251108); mean and 5–95 % band at the same area budgets.
- **v1 comparison:** v1 UNCERTAIN patches reviewed in random order at the same ha budgets.

## 7. Evaluation protocol
| Reach / year | Role |
|---|---|
| Kurigram 2024 | calibration (thresholds, m, δ, D_review, ranking model) |
| **Kurigram 2025** | **EXPLORATORY** — the v2 idea was formed after seeing these results; not held-out evidence |
| Sirajganj–Kazipur 2024 | calibration for that reach with the identical frozen procedure |
| **Sirajganj–Kazipur 2025** | **INDEPENDENT TEST** — never inspected before this design was fixed |

- **Sirajganj reach:** 89.569–89.847 °E, 24.644–24.748 °N (UTM45N 760–788 E, 2728–2740 N).
- **Secondary check:** the Kurigram-trained ranking model transferred unchanged to Sirajganj 2025.
- **SAR source:** Earth Engine COPERNICUS/S1_GRD σ⁰ if available for both reaches (pre-stated primary source). Otherwise Planetary Computer RTC γ⁰, an *adapted* baseline and not an exact reproduction of the GEE σ⁰ workflow.

## 8. Success criteria (stated in advance)
v2 counts as an improvement on the independent test only if both hold:
- **(a)** at a 20 % review budget, prioritized review recovers more reference erosion than the random-review mean, outside the 5–95 % random band;
- **(b)** HC false erosion is not higher than v1's.

Otherwise the result is reported as negative or inconclusive.

## 9. Addendum — written 11 Nov 2026 ~03:33, BEFORE any Sirajganj SAR result was produced or inspected
The Sirajganj–Kazipur 2025 optical reference contains only **12.2 ha** of erosion, and the blind visual point check gave 10/15 = 67 % agreement for the erosion stratum (27/29 = 93 % for non-erosion). This makes a single 2025 test weak.

We therefore add a second, fully independent **transfer evaluation**:
- **Parameters:** every parameter frozen on **Kurigram 2024** (v1 thresholds, m, δ; v2 D_review and ranking model) is applied **unchanged** to Sirajganj **2024 (59.9 ha reference erosion)** and **2025**.
- **Independence:** no Sirajganj data are used for any choice in this evaluation.
- **Metrics:** the same as above.

The pre-registered local protocol (calibrate on Sirajganj 2024, test on Sirajganj 2025) is still reported as specified.
