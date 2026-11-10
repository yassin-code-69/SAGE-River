# Limitations (state these honestly on the poster and in Q&A)

1. **One reach, one test monsoon.** 12 km of the Jamuna upstream of Chilmari (Kurigram), test monsoon 2025, validation monsoon 2024. Results may not transfer to other reaches, protected banks or years.
2. **Reference is optical, not field truth.** Sentinel-2 NDVI/MNDWI classes have errors (mixed pixels at 10–20 m, crop calendar, residual cloud/haze, wet vs dry sand). Visual point checks were done by the AI analyst and must be spot-checked by the team.
3. **Reach selection used optical change.** The AOI was chosen because Sentinel-2 showed visible 2025 outer-bank loss (required to have erosion to evaluate). SAR results were not used for selection, but the reach is not a random sample.
4. **SAR source.** Earth Engine σ⁰ could not be used (no Cloud project ID during execution); Planetary Computer RTC γ⁰ was used instead. γ⁰ is ≈ 1 dB higher than σ⁰ on flat ground at 30–45°, so the published thresholds (−13.2/−12.7 dB, σ⁰) are not directly applicable — the 2024-calibrated thresholds are the primary baseline. The incidence-angle mask (30–45°) could not be applied because RTC has no angle band (the AOI lies well inside that range for R114 — to be confirmed with GEE).
5. **Archive gaps in the fallback source.** PC RTC lacks 4 of 16 (2025 pre), 3 of 14 (2024 pre) and 2 of 8 (2024 post) ASF acquisitions; the 2024 calibration therefore covers k ≤ 6 and k = 8 uses the k = 6 parameters.
6. **Overlapping subsets.** Experiment A uses all combinations of the same 8 scenes; SD/range describe subset variability, not independent confidence intervals.
7. **Temporal mismatch.** The Feb–Mar reference is cumulative; early maps (8 Nov–2 Dec) cannot contain later falling-stage erosion. The as-of-mid-December reference only partially fixes this (Nov–Dec optical composites contain residual water).
8. **Classifier simplicity.** One VV threshold separates vegetation from sand/water; trees vs fields, settlements and wet fields are not separated; no VH, no texture, no learning-based classifier.
9. **Abstention is not probability.** The ±δ band is a selective-decision rule; it is not calibrated uncertainty.
10. **Outer-bank domain is heuristic.** Row-wise westmost/eastmost channel edges + 1.5 km strip; char (island) erosion is excluded by design.
11. **Not forecasting, not a PINN, no hydraulics.** The work maps past erosion and evaluates map reliability only.
12. **Coverage did not fully transfer.** m and δ were selected on 2024 with a ≥ 90 % coverage rule; on 2025 SAGE A+G coverage was 87–88 % for k ≥ 3.
13. **Fairness control added after run 1.** The F1-tuned baseline was added after inspecting only 2024 tables (run 1 archived in `outputs/reports/run1_without_F1tuned_baseline/`); all other rules are deterministic and identical across runs.
14. **Anomalous-scene interpretation unverified.** The dark field-shaped patches on 31 Jan 2026 are consistent with temporarily flooded/irrigated fields, but this was not field-verified.
