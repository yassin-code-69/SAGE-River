# Judges' Q&A — results-specific answers
*Updated 11 Nov 2026. Primary SAR source is GEE COPERNICUS/S1_GRD σ⁰.*

**Sources:**
- `outputs/tables/experiment_A_summary_gee.csv`, `experiment_A_all_subsets_gee.csv`, `experiment_B_chronological_gee.csv`, `selected_parameters_gee.json`;
- `v2_preregistered_criteria.csv`, `v2_ablation_all_reaches.csv`, `v2_review_summary_*.csv`;
- `audit_20260131_*.csv`;
- the Sirajganj tables in `outputs/reaches/sirajganj/tables/`.

## Scene budget and v1
**Q: So how many scenes are enough?**
For a usable map, 2–3. With the published thresholds on Kurigram 2025:

| Scenes (k) | Mean F1 | False erosion |
|---|---|---|
| 1 | 0.56 | 74 ha |
| 3 | 0.71 | 24 ha |
| 8 | 0.82 | 7.5 ha |

The 2024-tuned baseline reached 0.70, 0.79 and 0.82. Single scenes are risky: depending on the date, the tuned baseline's F1 ranged from 0.30 to 0.80.

**Q: Did SAGE-River v1 beat the baseline?**
- **On decided pixels: yes.** F1 0.85–0.90 with less than 3 ha of false erosion.
- **But it abstains.** Coverage was 88–91 %, and 14–21 ha of the 58.8 ha of real erosion fell into UNCERTAIN, mostly at bank edges.
- **Counting UNCERTAIN as "no erosion":** F1 is 0.66–0.77, never above the tuned baseline (0.76–0.82). The same held on the independent Sirajganj reach.
- So v1 is a reliability tool, not a better detector.

**Q: Why are the published thresholds now so close to your tuned ones?**
Because we now use the same data type as the paper (Earth Engine σ⁰). The 2024-tuned thresholds came out at −13.15 / −13.25 dB for k = 3 and −12.65 / −12.7 dB for k ≥ 6, against the published −13.2 / −12.7 dB. Earlier Planetary Computer γ⁰ runs needed thresholds about 1 dB higher. That is why they are only an adapted cross-check.

**Q: Why is "Baseline (calibrated)" so bad?**
Its thresholds separate vegetation from sand/water over the whole reach (Youden's J). That is a different objective from detecting bank loss, and it gives F1 0.35–0.46 with more than 100 ha of false erosion. Threshold choice matters more than anything else, which is why the F1-tuned baseline is our fair control.

## The bad scene (31 Jan 2026)
**Q: Was the bad scene a bug in your code?**
No. We audited it before changing any algorithm.
- **Implementation checks, all clean:**
  - NoData: none;
  - alignment: phase-correlation shift 0 px;
  - scene-wide radiometry: normal;
  - mosaicking: one item;
  - thresholds: identical to the other scenes.
- **What the dark patches are:** temporarily inundated fields, a median 584 m from the channel. Three independent sources agree:
  - GEE σ⁰: −15.0 dB, against −8.2 dB on control fields;
  - the R150 descending scene two days later is also dark;
  - Sentinel-2 shows 88–99 % open water from 28 Jan to 12 Feb.
- This fits flooding for boro rice, but it is not field-verified. We kept the scene in every experiment.

**Q: What did the bad scene do to the maps?**

| Map | False erosion |
|---|---|
| Alone, published thresholds | 265 ha |
| Alone, tuned thresholds | 160 ha |
| 2-scene maps containing it, tuned baseline | 12.1 ha |
| 2-scene maps containing it, A+G | 1.6 ha |

Temporal agreement is what protects you. A single-scene map cannot, and v2 does not fix that either: its single-scene high-confidence map still has 104 ha of false erosion.

## SAGE-River v2
**Q: What is v2?**
- **Three classes:**
  - HIGH-CONFIDENCE erosion: v1 confident pixels in patches touching the SAR-derived bank;
  - POSSIBLE EROSION — REVIEW: candidates within 100 m of the bank;
  - LIKELY STABLE.
- **Ranking:** REVIEW patches are ranked by a logistic model trained on 2024. It uses only map-date SAR features: change magnitude, vote fraction, pre margin, distance to the bank, area, bank contact and v1 fraction. The later Sentinel-2 reference is never an input.

**Q: Is v2 more accurate than the baseline?**
Not automatically. Its high-confidence class has the same F1 as v1 and is below the tuned baseline in every reach and scene budget. v2's value is in **where to send a limited review**.

**Q: Show me the review result.**
At 20 % review effort, k = 3:

| Evaluation | v2 prioritized | Random review (mean) |
|---|---|---|
| Kurigram 2025 (exploratory) | 21.3 ha | 5.5 ha |
| Sirajganj 2025 (independent) | 7.2 ha | 2.1 ha |
| Sirajganj 2024 (Kurigram parameters) | 19.7 ha | 8.0 ha |

Across the 12 independent tests, both pre-registered criteria were met in 11. The failure is the primary local test at k = 8, where prioritized equals the random 95th percentile (10.82 ha). Several margins are tiny.

**Q: Isn't 0.92 F1 after review cheating?**
It would be if we compared it with no-review baselines, and we don't. The simulated reviewer is an *oracle* that labels every reviewed pixel correctly, so the numbers are an upper bound. They measure how well the ranking directs effort, not map accuracy. We report effort in hectares: a 20 % budget is 37–244 ha of inspection.

**Q: Couldn't you just review v1's UNCERTAIN pixels?**
We tested exactly that (random order, same hectares):
- In Kurigram and Sirajganj 2025, v2 recovers 2.3–4.9 times more.
- In the Sirajganj 2024 transfer, the gap closes by 20 % effort (k = 3: 19.7 vs 16.8 ha; k = 8: 14.9 vs 15.2 ha, slightly in v1's favour).
- v2's ranking helps most at small budgets (5–10 %).

**Q: Did you tune v2 on the test data?**
No.
- **Frozen in advance:** the design was written at 02:58 and the code frozen at 03:12:45, with md5 checksums. The transfer addendum was written at 03:30:51.
- **Independent data:** the Sirajganj SAR was downloaded at 03:36–03:40, after the freeze. Our final audit re-verifies the checksums and this order.
- **Exploratory part:** the v2 idea came from inspecting Kurigram 2025. That is why we label Kurigram 2025 v2 results "exploratory" and use Sirajganj as the independent test.

**Q: How good is the Sirajganj reference?**
Weak, and we say so.
- **Size:** only 12.2 ha of erosion in 2025.
- **Point check:** 10/15 = 67 % of decidable erosion points agreed (15 of 30 were undecidable); non-erosion agreed 27/29 = 93 %.
- **Response:** before seeing any results, we added a transfer test on Sirajganj 2024 (59.9 ha) using Kurigram parameters.

## Other checks
**Q: Early mapping — when can you publish a map?**
Maps possible on 8 Nov, 20 Nov and 2 Dec 2025 reached F1 0.73, 0.76 and 0.79 (tuned baseline). Against an "as-of mid-December" reference they reached 0.75–0.82.

**Q: How good is your reference (Kurigram)?**
On 120 stratified points, interpreted blind to the label:
- 36/39 decidable erosion points were truly eroded (92 %);
- 47/47 near-bank non-erosion points were correct (100 %).

The points were interpreted by the AI analyst; the team must spot-check at least 20.

**Q: Does the filter matter (circle vs 7×7)?**
In the Planetary Computer cross-check, the paper's 7×7 square changed F1 by −0.02 to +0.08 and did not change the ranking of the rules. The primary GEE runs use the released code's radius-7 circle.
