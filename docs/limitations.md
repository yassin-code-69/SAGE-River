# Limitations (state these honestly on the poster and in Q&A)
*Updated 11 Nov 2026 for GEE σ⁰ as the primary source and for SAGE-River v2.*

1. **Few reaches and years.**
   - Development reach: Kurigram (Jamuna upstream of Chilmari); validation monsoon 2024, test monsoon 2025.
   - Independent reach: Sirajganj–Kazipur (2024 and 2025).
   - Two reaches of one braided river are not evidence of generality for other rivers, protected banks or years.
2. **Reference is optical, not field truth.**
   - Sentinel-2 NDVI/MNDWI classes have errors: mixed pixels, crop calendar, residual haze, wet vs dry sand.
   - The blind point checks were done by the AI analyst and must be spot-checked by the team.
3. **Reach selection used optical change.** Both reaches were chosen because Sentinel-2 showed visible outer-bank loss, which is needed to have erosion to evaluate. SAR results were not used for selection.
4. **SAR source.**
   - GEE COPERNICUS/S1_GRD σ⁰ is primary. Observed incidence angles over Kurigram were 36.4–38.1°, inside the 30–45° mask.
   - The Planetary Computer RTC γ⁰ runs are an *adapted* cross-check only. RTC is terrain-flattened γ⁰ (≈ 1 dB above σ⁰ at these angles), has no angle band and has archive gaps. It is not an exact reproduction of the GEE σ⁰ workflow.
5. **Overlapping subsets.** Experiment A uses all combinations of the same 8 scenes. SD and range describe subset variability, not independent confidence intervals.
6. **Temporal mismatch.** The Feb–Mar reference is cumulative, so early maps cannot contain later erosion. The as-of-mid-December reference only partly fixes this.
7. **Classifier simplicity.** A single VV threshold rule; no VH, no texture, no learned pixel classifier.
8. **Abstention is not probability.** The ±δ band is a selective-decision rule, not calibrated uncertainty. The v2 review ranking is a logistic score used only for ordering.
9. **Outer-bank domain is heuristic.** Row-wise channel edges plus a 1.5 km strip; char (island) erosion is excluded by design.
10. **Not forecasting, not a PINN, no hydraulics.**
11. **Coverage did not fully transfer.** The ≥ 90 % coverage rule set on 2024 gave 88–91 % for v1 A+G in 2025.
12. **Fairness control added after run 1.** The F1-tuned baseline was added after inspecting only 2024 tables. Run 1 is archived.
13. **Anomalous-scene interpretation unverified.** The 31 Jan 2026 dark fields are consistent with temporary flooding (three independent sources) but were not field-verified.
14. **The v2 reviewer is simulated as an oracle.** The review simulation assumes the analyst labels every reviewed pixel correctly. Real analysts make errors and need imagery, so the "v2 + review" F1 values are upper bounds. They are not comparable to no-review baselines.
15. **Review burden.**
    - REVIEW covers 184–1218 ha, against 12–60 ha of reference erosion.
    - A 20 % budget means inspecting 37–244 ha, about 3–23 ha per ha recovered.
16. **The independent primary test is weak.**
    - Sirajganj 2025 has only 12.2 ha of reference erosion.
    - The erosion-point check agreed for 10/15 decidable points (67 %); 15 of 30 points were undecidable.
    - Criterion (a) passed at k = 2, 3, 6 by tiny margins and failed at k = 8.
17. **Kurigram 2025 v2 results are exploratory.** The v2 idea was formed after inspecting them, so they are not held-out evidence.
18. **v2 adds no automatic accuracy.**
    - The high-confidence class equals v1 and is below the tuned baseline in every reach × k cell.
    - Single-scene maps remain unreliable (31 Jan: 104 ha false erosion in v2 HC).
    - Random review of v1 UNCERTAIN pixels nearly matched v2 at ≥ 20 % effort in Sirajganj 2024.
