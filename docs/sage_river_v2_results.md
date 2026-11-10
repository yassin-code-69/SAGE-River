# SAGE-River v2 — results and updated conclusion
*Written 11 Nov 2026. Every number comes from the CSV files named in each section. The design was pre-registered in `docs/sage_river_v2_design.md`, with checksums and freeze times in `docs/sage_river_v2_design.md5`. SAR source: GEE COPERNICUS/S1_GRD σ⁰ (primary), unless stated otherwise.*

## 1. What was evaluated, and with what status
| Evaluation | Parameters from | Status | Reference erosion |
|---|---|---|---|
| Kurigram 2025 | Kurigram 2024 | **EXPLORATORY**: the v2 idea came from looking at these v1 results | 58.8 ha |
| Sirajganj–Kazipur 2025 | Sirajganj 2024 (same frozen procedure) | **INDEPENDENT, pre-registered primary test**: new reach; code frozen 03:12:45 before any Sirajganj SAR was processed | 12.2 ha |
| Sirajganj–Kazipur 2024 | Kurigram 2024 (unchanged) | **INDEPENDENT TRANSFER**: addendum written 03:30:51, before any Sirajganj SAR result | 59.9 ha |
| Sirajganj–Kazipur 2025 | Kurigram 2024 (unchanged) | **INDEPENDENT TRANSFER** (addendum) | 12.2 ha |

**Reference quality (Sirajganj 2025).** A blind visual point check agreed for 10/15 = 67 % of erosion points and 27/29 = 93 % of non-erosion points (`outputs/reaches/sirajganj/tables/reference_point_agreement_2025.csv`). With only 12.2 ha of erosion and moderate erosion-label agreement, this test is weak. That weakness is why the transfer evaluation on 2024 (59.9 ha) was added before any results were seen.

## 2. Root-cause audit of the 31 Jan 2026 scene (summary)
Full report: `outputs/reports/root_cause_audit_20260131.md`.

**No implementation error was found.** The following checks were all clean:
- NoData values;
- alignment (FFT shift 0/0 px);
- scene-wide radiometry;
- mosaicking;
- thresholds.

**Cause.** The false erosion comes from **temporarily inundated fields** on the west floodplain. Three independent sources show them dark or wet:
- GEE σ⁰: −15.0 dB, against −8.2 dB on control fields;
- the R150 descending scene: −13.1 dB;
- Sentinel-2: 88–99 % MNDWI > 0 between 28 Jan and 12 Feb.

**The scene was kept in every experiment.** On GEE σ⁰ it produces:

| Map | False erosion |
|---|---|
| 31 Jan alone, published thresholds | 265 ha |
| 31 Jan alone, tuned thresholds | 160 ha |
| v1 A+G, 2-scene subsets containing it | 1.6 ha (tuned baseline: 12.1 ha) |
| v2 HIGH-CONFIDENCE, 31 Jan alone (k = 1) | **104 ha** |

Bank connectivity therefore removes only part of this error in a single-scene map. Some flooded fields connect to the channel through candidate pixels. Temporal agreement (k ≥ 2) is what suppresses it.

## 3. Ablation — full-area F1 (UNCERTAIN/REVIEW counted as non-erosion unless reviewed)
Source: `outputs/tables/v2_ablation_all_reaches.csv`. Values are means over all C(8,k) subsets. Each cell gives **F1 / false erosion (ha)**.

| Step | Kurigram 2025 (expl.) k=3 | k=8 | Sirajganj 2025 (indep.) k=3 | k=8 | Sirajganj 2024 (transfer) k=3 | k=8 |
|---|---|---|---|---|---|---|
| Published σ⁰ thresholds | 0.71 / 24.1 | 0.82 / 7.5 | 0.48 / 7.1 | 0.51 / 4.7 | 0.70 / 10.9 | 0.72 / 8.8 |
| Adapted baseline, F1-tuned T | 0.79 / 6.0 | 0.82 / 7.1 | 0.46 / 8.8 | 0.52 / 3.8 | 0.68 / 7.0 | 0.73 / 6.1 |
| + agreement (unanimous) | 0.71 / 19.8 | 0.79 / 1.5 | 0.39 / 5.1 | 0.37 / 1.1 | 0.68 / 2.0 | 0.64 / 0.4 |
| + gating (G) | 0.59 / 46.3 | 0.74 / 15.7 | 0.32 / 1.5 | 0.31 / 1.1 | 0.69 / 3.2 | 0.71 / 1.3 |
| SAGE-River v1 (A+G) | 0.66 / 0.49 | 0.77 / 1.22 | 0.33 / 1.63 | 0.15 / 0.47 | 0.54 / 0.16 | 0.64 / 0.27 |
| **v2, no review (HC only)** | 0.66 / 0.49 | 0.77 / 1.22 | 0.33 / 1.37 | 0.15 / 0.47 | 0.54 / 0.16 | 0.64 / 0.27 |
| v2 + 10 % prioritized review | 0.87 | 0.89 | 0.83 | 0.97 | 0.76 | 0.79 |
| v2 + 20 % prioritized review | 0.92 | 0.92 | 0.85 | 0.97 | 0.82 | 0.83 |
| v2 + 20 % **random** review | 0.74 | 0.81 | 0.52 | 0.53 | 0.67 | 0.73 |

**Single scene (k = 1).** v2 HC versus the tuned baseline, as mean F1 / false erosion:

| Evaluation | v2 HC | Tuned baseline |
|---|---|---|
| Kurigram | 0.64 / 37.3 ha | 0.70 / 24.3 ha |
| Sirajganj 2025 | 0.30 / 4.4 ha | 0.45 / 9.3 ha |
| Sirajganj 2024 transfer | 0.67 / 5.6 ha | 0.64 / 7.8 ha |

Source: `v2_hc_only_metrics_*.csv`, `experiment_A_summary_*.csv`.

## 4. Prioritized vs random review
- **Sources:** `v2_review_summary_*.csv`.
- **Review effort** is a fraction of the REVIEW area. Each cell gives the ha of reference erosion recovered.
- **"Random"** is the mean of 500 random patch orders; "p95" is their 95th percentile.
- **"v1-U random"** is random review of v1 UNCERTAIN pixels with the same ha budget.

| Evaluation (k) | REVIEW area / erosion inside | 5 %: v2 / random / p95 / v1-U | 10 % | 20 % |
|---|---|---|---|---|
| Kurigram 2025, k=3 (expl.) | 758 ha / 25.0 ha | 12.3 / 2.3 / 10.3 / 2.2 | 16.3 / 3.4 / 11.8 / 4.0 | 21.3 / 5.5 / 16.1 / 7.8 |
| Kurigram 2025, k=8 (expl.) | 793 ha / 16.7 ha | 8.8 / 1.6 / 5.5 / 1.4 | 10.8 / 2.2 / 7.0 / 2.6 | 13.6 / 3.7 / 9.6 / 4.9 |
| Sirajganj 2025, k=3 (indep.) | 441 ha / 7.3 ha | 6.0 / 1.1 / 5.2 / 0.4 | 6.9 / 1.4 / 6.3 / 0.8 | 7.2 / 2.1 / 7.2 / 1.5 |
| Sirajganj 2025, k=8 (indep.) | 1218 ha / 10.8 ha | 10.8 / 3.4 / 10.8 / 1.1 | 10.8 / 3.6 / 10.8 / 2.0 | 10.8 / 3.6 / 10.8 / 3.8 |
| Sirajganj 2024, k=3 (transfer) | 430 ha / 33.9 ha | 9.9 / 2.8 / 9.2 / 4.0 | 14.8 / 4.7 / 13.1 / 8.2 | 19.7 / 8.0 / 18.2 / **16.8** |
| Sirajganj 2024, k=8 (transfer) | 397 ha / 27.4 ha | 9.1 / 2.4 / 7.3 / 3.6 | 11.1 / 3.6 / 10.8 / 7.1 | 14.9 / 6.2 / 13.5 / **15.2** |

**PC RTC γ⁰ cross-source check (Kurigram 2025, 20 %)** gives the same picture:

| k | v2 prioritized | Random | p95 | v1-U |
|---|---|---|---|---|
| 3 | 21.7 ha | 5.5 ha | 14.9 ha | 7.5 ha |
| 8 | 13.9 ha | 3.5 ha | 8.9 ha | 5.1 ha |

## 5. Pre-registered success criteria
Source: `outputs/tables/v2_preregistered_criteria.csv`. The criteria are:
- **(a)** prioritized review beats the random mean and the 95th percentile at a 20 % budget;
- **(b)** HC false erosion is not higher than v1's.

| Evaluation | k = 2 | k = 3 | k = 6 | k = 8 |
|---|---|---|---|---|
| Kurigram 2025 (exploratory) | a ✓ b ✓ | a ✓ b ✓ | a ✓ b ✓ | a ✓ b ✓ |
| **Sirajganj 2025, local (primary independent)** | a ✓ (8.90 vs p95 8.82) b ✓ | a ✓ (7.22 vs 7.17) b ✓ | a ✓ (10.58 vs 10.56) b ✓ | **a ✗** (10.82 = p95 10.82) b ✓ |
| Sirajganj 2024, transfer | a ✓ b ✓ | a ✓ b ✓ | a ✓ b ✓ | a ✓ b ✓ |
| Sirajganj 2025, transfer | a ✓ b ✓ | a ✓ (9.57 vs 9.50) b ✓ | a ✓ b ✓ | a ✓ (8.82 vs 8.80) b ✓ |

On the primary independent test, criterion (a) holds for k = 2, 3, 6 by very small margins and **fails for k = 8**. At k = 8 the 95th percentile of random review already reaches the maximum possible (10.82 ha), because nearly all erosion sits in a few large patches that random review often picks. Criterion (b) holds everywhere: HC false erosion equals or is slightly below v1's.

## 6. What v2 does *not* show (stated plainly)
1. **No automatic accuracy gain.** Without review, v2 HC has the same full-area F1 as v1 (identical or within 0.01). It is below the F1-tuned baseline in all 16 reach × k cells (k = 2, 3, 6, 8 in four evaluations). On the independent Sirajganj 2025 test, all automatic methods are weak (tuned baseline 0.43–0.52). v1 and v2 HC are much worse there (0.12–0.33), because they abstain on or exclude almost all of the 12 ha of erosion. The original finding stands: **uncertainty-based abstention buys precision at a large cost in recall and coverage.**
2. **The reviewer is simulated as an oracle.** Every reviewed pixel is judged correctly, which no human analyst does. The "v2 + review" F1 values include that human work. They are not comparable to the no-review baselines and are reported only to show the effort/benefit curve.
3. **Review burden is large.** REVIEW covers 184–1218 ha, against 12–60 ha of reference erosion. At 20 % effort an analyst inspects 37–244 ha, i.e. roughly 3–23 ha inspected per ha of erosion recovered.
4. **The advantage over simply reviewing v1's UNCERTAIN pixels is not uniform.** In Kurigram and in both Sirajganj 2025 evaluations, v2 prioritized review recovers 2.3–4.9 times more than v1-U random review at 20 % effort, and more at 5 %. In the Sirajganj 2024 transfer the gap closes by 20 % effort (k = 3: 19.7 vs 16.8 ha; k = 8: 14.9 vs 15.2 ha, where v1-U is slightly higher). v2's ranking helps most at small budgets (5–10 %).
5. **Single-scene maps remain unreliable.** At k = 1, bank connectivity does not remove the inundated-field error (104 ha on 31 Jan).
6. **What the ranking model learned.** Its standardized coefficients favour patches that were clearly vegetated before (pre margin +2.04), dark in many scenes (vote fraction +1.76), close to the bank (distance −1.67) and small (log area −1.25). Change magnitude has almost no weight (+0.04). It was trained on Kurigram 2024 only (6292 patches). It transferred to Sirajganj, but two reaches of one river are not evidence of generality.

## 7. Updated research conclusion
- **Scene budget (v1 question, GEE σ⁰, Kurigram 2025).**
  - With the published thresholds, false erosion fell from 74 ha (1 scene) to 24 ha (3 scenes) and 7.5–8.7 ha (6–8 scenes); F1 rose from 0.56 to 0.71 and then 0.81–0.82.
  - A 2024-tuned baseline reached 0.70 (k = 1), 0.79 (k = 3) and 0.82 (k = 8).
- **Agreement + abstention (v1).** False erosion fell below 3 ha and F1 on decided pixels reached 0.85–0.90. But 9–12 % of the domain was abstained, holding 14–21 ha of real erosion. With abstentions counted as misses, v1 did not beat the tuned baseline. This held on the independent reach as well.
- **Triage + prioritized review (v2).**
  - Bank-connectivity triage plus a ranking learned on 2024 directs a limited review to the right patches. On every evaluation, reviewing the top 5–10 % of the REVIEW area recovered far more erosion than the random-review mean.
  - The pre-registered criteria were met in 15 of 16 reach × k cells. The exception is k = 8 on the primary independent test, and several independent margins are very small.
  - This is a **workflow result** (where to spend analyst time), not a better automatic classifier.
- **Defensible claim.** To our knowledge, this is the first erosion-map study to report scene-budget accuracy, abstention cost and the benefit of review prioritization together, with a pre-registered independent-reach test. The improvement is real but modest and depends on human review. Automatic accuracy did not improve.
