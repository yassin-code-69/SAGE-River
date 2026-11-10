# Judges' Q&A — results-specific answers (2025 test monsoon, parameters frozen on 2024)

Sources: `outputs/tables/experiment_A_summary_pc.csv`, `experiment_B_chronological_pc.csv`, `experiment_A_all_subsets_pc.csv`, `selected_parameters_pc.json`, `reference_point_agreement_2025.csv`, `filter_sensitivity_2025_circle7_vs_square7.csv`.

**Q: So how many scenes are enough?**
With the published rule, 2–3 scenes. Mean F1 went from 0.70 (1 scene) to 0.77 (3 scenes) and then stayed at 0.77 up to 8 scenes; false erosion fell from 22 ha to 2 ha. Single-scene maps were unreliable: their F1 ranged from 0.30 to 0.77 depending on which scene you happened to use. The 2024-tuned baseline kept improving slowly (0.67 → 0.80 from 1 to 8 scenes).

**Q: Did SAGE-River beat the baseline?**
On the pixels it decides — yes: F1 0.86–0.90, precision 0.94–0.98, false erosion ≤ 2.4 ha, versus 0.73–0.80 for the best baseline. But it leaves 9–13 % of the outer-bank strip UNCERTAIN, and 23–36 % of the true erosion area lies in those uncertain pixels (mostly bank edges). If we count UNCERTAIN as "no erosion", SAGE scores 0.66–0.77 — not consistently better than the tuned baseline (0.73–0.80). So it is a *reliability* tool: what it says is very trustworthy, and it tells you where to look again; it does not find more erosion.

**Q: Then what is the value of agreement?**
Robustness to a bad scene. On 31 January 2026 one acquisition showed dark, field-shaped patches on the west floodplain (consistent with temporarily flooded or irrigated fields — not field-verified). Used alone, the tuned baseline mapped 197 ha of false erosion from it (150 ha with the published thresholds). In 2-scene maps containing that date, the tuned baseline still had 36 ha of false erosion on average, while SAGE A+G stayed at about 1 ha.

**Q: Why is "Baseline (calibrated)" so bad?**
Its thresholds were chosen to separate vegetation from sand/water over the whole reach (Youden's J). That is not the same objective as detecting the vegetated→sand change on the bank, and it gave F1 0.35–0.42 with > 100 ha false erosion. It shows that threshold choice matters more than anything else. That is why we added a fair control: a baseline whose thresholds were tuned on 2024 erosion F1, just like SAGE's m and δ.

**Q: You used γ⁰ RTC data but published σ⁰ thresholds — is that valid?**
The published thresholds (−13.2/−12.7 dB) were derived for Earth Engine σ⁰. γ⁰ is roughly 1 dB higher on flat ground, so we treat them as indicative only. Interestingly, the thresholds tuned on 2024 (−11.5 dB pre; −12.2 to −11.4 dB post) are close to the published values plus ~1 dB. Earth Engine σ⁰ re-runs are scripted and pending a project ID.

**Q: Early mapping — when can you publish a map?**
Maps possible on 8 Nov, 20 Nov and 2 Dec 2025 reached F1 0.73, 0.75 and 0.78 (tuned baseline). 95 % of the reference erosion was already visible in optical images by mid-December, so late-season erosion did not distort the comparison much.

**Q: How good is your reference?**
On 120 stratified points interpreted visually (blind to the automatic label): 36 of 39 decidable reference-erosion points were truly eroded (92 %), and 47 of 47 non-erosion points near the bank were not eroded (100 %). The points were interpreted by the AI analyst. The team must spot-check at least 20 before presenting.

**Q: Does the filter matter (circle vs 7×7)?**
The paper text says "7×7 boxcar", but the released code uses a radius-7 circle. Using the paper's 7×7 square changed F1 by −0.02 to +0.08 depending on the rule (mostly a small gain). The ranking of the rules did not change.

**Q: Did the 2024 settings transfer to 2025?**
Mostly yes. The one exception is coverage: m and δ were chosen to keep ≥ 90 % coverage in 2024, but coverage fell to 87–88 % in 2025 for k ≥ 3. That is exactly why coverage must be reported with every result.
