# Phase 0 Audit — verification of preliminary claims (re-checked 11 Nov 2026 on the FINAL AOI)

Final AOI: 89.6289–89.8902 °E, 25.6131–25.7262 °N (UTM 45N 764–790 km E, 2836–2848 km N), see `data/aoi/aoi.geojson`.
Catalogues queried for this exact AOI: ASF search API (GRD_HD, IW) and Microsoft Planetary Computer `sentinel-1-rtc`.
Google Earth Engine: user login completed, but no Cloud project ID was available during execution → GEE inventory **not** run (scripts ready in `gee/`).

| Phase 0 claim | Status on final AOI | Evidence |
|---|---|---|
| Two relative orbits: R114 ascending, R150 descending | **Confirmed** (ASF: only 114 ASC and 150 DSC) | `outputs/tables/sentinel1_counts_by_year_orbit.csv` |
| R114 from 2017, R150 from Oct 2014 | **Confirmed in ASF.** PC RTC additionally lists sparse R114 items in 2014–2016 that ASF footprints do not place over the AOI (35 PC-only keys) | `sentinel1_source_comparison.csv` |
| ~12-day interval per orbit | **Confirmed**: R114 ASF gaps 12 d (281×), 24 d (6×), 6–7 d (5×, S1B 2020 / S1A–S1D overlap 2026) | inventory analysis |
| Sentinel-1B contributed very few scenes | **Confirmed**: 4 S1B acquisitions over the AOI (2019-07-25, 2020-05-22, 2020-07-19, 2020-07-21) | ASF |
| S1A last local scene 26 Jun 2026; S1D from Jul 2026 | **Confirmed**: S1A last 2026-06-26, S1D first 2026-07-01 (same orbits); no Sentinel-1C over the AOI | ASF |
| November only: 2–3 R114 scenes | **Confirmed** 2017/18–2025/26: 2 or 3 | `sentinel1_window_counts.csv` |
| Nov–Dec 5–6; Nov–Jan 7–8; Nov–Apr 14–16 | **Confirmed** (ASF) | same |
| 2025/26 pool = 8 dates (8 Nov … 31 Jan) | **Confirmed in ASF and PC** with product IDs | `data/cache/s1_pc_2025.json` |
| 2024/25 pre composite ≈ 16 scenes | **ASF: 16; PC RTC: 12** (4 not processed in PC RTC) | comparison table |
| 2024/25 post pool (validation) = 8 | **ASF: 8; PC RTC: 6** (missing 2024-11-01, 2024-12-31) | comparison table |
| Kurigram first candidate | **Selected after S2 inspection** (outer-bank loss ~60 ha in 30 m recon); Sirajganj (Kazipur) alternative showed mostly protected west bank | `outputs/maps/recon_*.png` |
| CEGIS 2025 district erosion figures | **Confirmed in CEGIS PDF Table 2** (Kurigram 149 ha / 40 ha settlement, …) | `references/cegis/` |
| F&F circle(r=7) vs 7×7 boxcar discrepancy | **Confirmed in code lines 158–167** (`ee.Kernel.circle({radius: 7})`) | `references/zenodo_7253121/` |
| F&F thresholds −13.2 / −12.7 dB | **Confirmed** paper Sect. 2.5 and code l. 1203/1208 | same |

## Consequences for the experiment
- Because GEE could not be initialised (no project ID), the SAR source is PC `sentinel-1-rtc` (γ⁰ RTC). The published σ⁰ thresholds are therefore only indicative; the calibrated baseline is the primary comparison.
- With PC RTC the 2024 validation pool has 6 scenes, so k = 8 cannot be calibrated on 2024: for k = 8 the k = 6 calibration is used (documented fallback `nearest_k`).
- Re-running with `--source gee` (complete archive, σ⁰, angle mask) is the first action once a project ID is provided.
