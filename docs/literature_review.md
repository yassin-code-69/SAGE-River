# Verified Literature Review — SAGE-River

**Verification status legend**
- **VERIFIED-FULLTEXT**: checked against the publisher PDF/full text (page/section/table given).
- **VERIFIED-ABSTRACT**: only the publisher-deposited abstract/metadata (Crossref, DOAJ, OpenAlex) could be read; full text was blocked (HTTP 403) during verification on 11 Nov 2026. Do not quote internal numbers from these papers.
- **UNVERIFIED**: claim seen only in secondary snippets — not used on the poster.

All DOIs below were checked to resolve (HTTP 302 to publisher) on 11 Nov 2026.

---

## 1. Freihardt & Frey (2023) — primary baseline  *(VERIFIED-FULLTEXT + code)*

Freihardt, J. & Frey, O. (2023). Assessing riverbank erosion in Bangladesh using time series of Sentinel-1 radar imagery in the Google Earth Engine. *Natural Hazards and Earth System Sciences*, 23, 751–770. https://doi.org/10.5194/nhess-23-751-2023 (CC BY 4.0). Local copy: `references/freihardt_frey_2023/`.

Code: Freihardt & Frey (2022), *Code to develop algorithm for riverbank erosion assessment in the Google Earth Engine*, Zenodo, https://doi.org/10.5281/zenodo.7253121 (CC-BY-4.0; single JS file, 1,381 lines, md5 4965759680c5a2c16b3179669f6ce22a — checksum re-verified locally). Local copy: `references/zenodo_7253121/`.

| Item | Finding (location) |
|---|---|
| Problem | Detect historical riverbank erosion (vegetated land and settlements lost during a monsoon) on the Jamuna with free SAR data in GEE. |
| Area | Jamuna River, >200 km N–S (Sect. 2.6); outer banks; erosion on sandbanks/islands not discussed (Sect. 3.3). |
| Data | `COPERNICUS/S1_GRD`, IW, 10 m, **VV only** ("VH is available only from 2017 on", Sect. 2.2); ascending pass for land cover/erosion (code l. 239, 1214–1219); relative orbits 114 (asc) and 150 (desc), 12-day revisit (p. 753). Incidence angle 30–45° applied as a **per-pixel mask** in code (l. 218–230). |
| Method | Temporal **mean of speckle-filtered dB images**; thresholds from class statistics of 10 reference patches per class: T = ½[(μᵢ+nσᵢ)+(μⱼ−nσⱼ)] (Sect. 2.3). Erosion = pre composite > T **and** post composite < T (Sect. 2.5; code l. 1222–1226). No morphology / minimum mapping unit / water mask. |
| Thresholds | **−13.2 dB** (6-month window), **−12.7 dB** (1-month window), both with the "7×7" filter (Sect. 2.5; Tables B1/B2; code l. 1203, 1208). |
| Filter discrepancy | Paper text: "7 × 7 boxcar". Released code: `ee.Kernel.circle({radius: 7, normalize: true})` (l. 158–167) — a ~15-px-diameter disc (~150 m), not a 7×7 square. Our baseline follows the **released code**; the square 7×7 is run as a sensitivity check. |
| Windows | Dry season Nov–Apr; post-monsoon composite of year Y reused as pre composite of Y+1; 2019 case uses **November only** "to simulate the case where the erosion detection has to be performed already in December" (Sect. 2.5; code l. 1206). |
| Sampling-duration test | 2 weeks … 7 months from 1 Nov 2018; measured **mean and σ of backscatter in patches** (Figs 4, A3) — **not erosion-map accuracy** (Sect. 2.3, 3.1). |
| Validation | Land-cover only: Sentinel-2 L1C NDVI 0.1 two-class reference at one site; overall accuracy 87.5 % (November, 3-yr mean) and 90.6 % (March) (Table 2). Erosion map checked **visually** only (Sect. 3.3, Fig. 8). "validation based on groundtruth data was not possible" (Sect. 3.4). |
| m-of-k | Only for settlement / persistent-scatterer detection: σ⁰ > −4 dB in ≥ 0.65K images (Sect. 2.4) — **not used for erosion**. |
| Uncertainty | No uncertain/abstention class. |
| Limitations stated | single case study, transferability unclear; SAR only; no phase; trees vs fields poorly separable; cloud-mask errors in optical check (Sects 3.1, 3.4, 4). |
| Relevance | Our reproduced baseline; our study adds **erosion-map-level** accuracy vs scene count against an independent S2 reference, plus agreement and abstention rules. |

## 2. Shampa et al. (2025) *(VERIFIED-FULLTEXT)*
Shampa, Muktadir, H. M., Nejhum, I. J., Hussain, M. M., Bhowmik, A., Ananto, N. I., Aungon, F. A., Biswas, S., Islam, M. M. (2025) (author list checked against Crossref). A riverbank erosion early warning system (EWS-RE) for braided river: a case of the Brahmaputra–Jamuna. *Frontiers in Earth Science*, 13, 1570577. https://doi.org/10.3389/feart.2025.1570577
- Problem: physics-based **early warning / forecasting** for a braided river.
- Data/method: Landsat band-ratio bathymetry + cross-sections, Delft3D 2-D model, GloFAS seasonal forecasts, BWDB records; **no Sentinel-1 / SAR**.
- Evaluation: hydraulics NSE 0.608–0.971 (Table 4); 2019 spatial erosion OA 88 %, κ 73.3 % (Table 5); 2023 field test OA 70 % (Table 6).
- Limitations: 2-D model misses 3-D flow, no geotechnical failure, sparse validation.
- Relevance: forecasting (different task); complementary to our historical-detection reliability study.

## 3. Aishi & Fahim (2024) *(VERIFIED-ABSTRACT)*
Aishi, A. F. & Fahim, A. K. F. (2024). Analyzing the association between the hydrodynamics and bank erosion along the Padma River: 2020 monsoon floods. *Geomatics, Natural Hazards and Risk*, 15(1), 2399668. https://doi.org/10.1080/19475705.2024.2399668
- Padma River, 2020 monsoon; Sentinel-1 + Sentinel-2 erosion mapping; 1-D hydraulic model; MLR/RF/ANN/SVM; ANN best; flow area, stream power, shear stress most influential (abstract).
- Internal metrics, reach and limitations **not verified** (full text blocked) → not quoted.
- Relevance: SAR used during a monsoon on a Bangladeshi river; hydraulics+ML, not scene-count reliability.

## 4. Langhorst & Pavelsky (2023) *(VERIFIED-ABSTRACT)*
Langhorst, T. & Pavelsky, T. (2023). Global observations of riverbank erosion and accretion from Landsat imagery. *JGR: Earth Surface*, 128(2), e2022JF006774. https://doi.org/10.1029/2022JF006774
- Global Landsat-based bank erosion/accretion for >370,000 km of rivers; uncertainty by propagating water-classification errors; vs 25 independent estimates NMAE 42 %, bias 5.8 % (abstract).
- A snippet claiming "areas with fewer images have higher classification errors" is **UNVERIFIED** — not cited.

## 5. CEGIS operational prediction *(VERIFIED — official PDF)*
CEGIS (2026). *Prediction of Riverbank Erosion 2026 (Jamuna, Ganges and Padma Rivers)*, summary report, 19 May 2026. https://www.cegisbd.com/news/3011 (old `web.cegisbd.com/EventData?Evntid=72` no longer resolves). Local copy `references/cegis/`.
- 2025 monitored erosion (Table 2): Jamuna 348 ha land in total; by district Kurigram 149 ha (40 ha settlement), Jamalpur 49, Sirajganj 49, Gaibandha 39, Tangail 26, Bogura 23, Manikganj 11, Pabna 2.
- Landsat 30 m: small (1–50 m) erosion not predicted; graded 30/50/70 % probability lines.
- Relevance: official context; motivates a 10 m SAR reliability study. We do **not** claim to replace CEGIS.

## 6. Related techniques (component precedents)

| Work | DOI / URL | Overlap with SAGE-River | Status |
|---|---|---|---|
| Peña-Luque et al. 2021, *Remote Sens.* 13:3279 | 10.3390/rs13163279 | S1/S2 water detection vs aggregation window (5–30 d); radar F1 0.72→0.80 | VERIFIED-ABSTRACT |
| NASA LANCE MODIS NRT flood product (MCDWD) User Guide Rev D, 2024 | earthdata.nasa.gov (PDF in `references/other/`) | Operational **m-of-k** rule (detections required grows with observations) — optical | VERIFIED-FULLTEXT |
| Reiche et al. 2021 (RADD), *Environ. Res. Lett.* 16:024005 | 10.1088/1748-9326/abd0a8 | Multi-scene S1 confirmation with confidence tiers (forest) | VERIFIED-ABSTRACT |
| Canty et al. 2020, *Remote Sens.* 12:46 | 10.3390/rs12010046 | Sequential S1 omnibus change detection in GEE | VERIFIED-ABSTRACT |
| Krullikowski et al. 2023, *IEEE JSTARS* 16:6917; GFM PDD v4.0 (2025) | 10.1109/JSTARS.2023.3292350 | Ensemble flood mapping, likelihood/exclusion layers | VERIFIED-ABSTRACT / PDF |
| Li, Matgen & Chini 2026, "Quantifying and Communicating Uncertainty in SAR-Based Flood Mapping via Density-Aware Neural Networks and Conformal Risk Control", *IEEE TGRS* 64:4202520 | 10.1109/TGRS.2026.3661208 | Conformal risk control / abstention for SAR flood mapping | VERIFIED-ABSTRACT (title via Crossref) |
| Giustarini et al. 2016, *IEEE TGRS* 54:6958 | 10.1109/TGRS.2016.2592951 | Per-pixel probabilistic SAR flood maps | VERIFIED-ABSTRACT |
| Martinis et al. 2015, *ISPRS J.* 104:203; Twele et al. 2016, *IJRS* 37:2990 | 10.1016/j.isprsjprs.2014.07.014; 10.1080/01431161.2016.1192304 | Fuzzy-logic band around SAR threshold | VERIFIED-ABSTRACT |
| Zhao et al. 2021, *RSE* 265:112668 | 10.1016/j.rse.2021.112668 | S1 exclusion maps (incl. sand) | VERIFIED-ABSTRACT |
| Condessa et al. 2016, *IEEE JSTARS* 9:2321 | 10.1109/JSTARS.2015.2510032 | Classification with reject option | VERIFIED-ABSTRACT |
| Valsangkar et al. 2024, *JAG* 134:104146 | 10.1016/j.jag.2024.104146 | Lower Jamuna S1/S2 waterlines with uncertainty | VERIFIED-ABSTRACT |
| Rossi et al. 2023, *Remote Sens.* 15:3622 | 10.3390/rs15143622 | Dense S1 time series for bank erosion (Tagliamento) | VERIFIED-ABSTRACT |

48 works citing Freihardt & Frey (OpenAlex) were screened by title/abstract: none reported scene-count, agreement or abstention analysis of erosion maps. IEEE Xplore/Scopus full texts could not be searched → use "to our knowledge".

## 7. Satellite facts (official sources)
- Sentinel-1B anomaly 23 Dec 2021; end of mission announced 3 Aug 2022 (ESA).
- Sentinel-1C launched 5 Dec 2024; user data from 26 Mar 2025 (CDSE notice).
- Sentinel-1D launched 4 Nov 2025; user data from 17 Apr 2026; Sentinel-1A operations ended 29 Jun 2026 (ESA "Time to say goodbye to Sentinel-1A").
- Over our AOI, see `outputs/tables/sentinel1_acquisitions.csv` for what was actually acquired (local inventory supersedes global statements).
