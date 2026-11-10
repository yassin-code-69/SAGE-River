# Methodology

## 1. Workflow
```
Sentinel-1 GRD (VV, IW, R114 ascending)          Sentinel-2 L2A (independent optical sensor)
        │ angle 30–45° mask (GEE source)                 │ SCL cloud mask, median Feb–Mar
        │ linear → circle(r=7) mean → dB                 │ NDVI / MNDWI classes
        ▼                                                ▼
 pre composite (Nov–Apr mean)                   reference erosion (veg → sand/water,
 post pool (8 scenes, Nov–Jan)                  channel-connected, outer-bank strip)
        │                                                │
        ├─ BASELINE  pre > T_pre AND mean(post_k) < T_post         │
        ├─ A         pre > T_pre AND ≥ m of k scenes < T_scene     │
        ├─ G         ±δ abstention band (UNCERTAIN)                │
        └─ A+G       per-scene ±δ votes + m-of-k + Kleene AND      │
                              ▼                                    ▼
             metrics on decided pixels + coverage  ◄───────────────┘
```

## 2. Baseline reproduction (Freihardt & Frey 2023; released code)
| Step | Released code | This study | Change? |
|---|---|---|---|
| Collection | COPERNICUS/S1_GRD, IW, 10 m | same (GEE source) / PC sentinel-1-rtc (fallback) | fallback documented |
| Polarisation | VV | VV | — |
| Pass / orbit | ASCENDING (no relative-orbit filter) | ASCENDING, relative orbit 114 (the only ascending orbit over the AOI — verified) | explicit filter, same data |
| Incidence angle | per-pixel mask 30°<θ<45° | same (GEE). PC RTC has no angle band → not applied | fallback limitation |
| Same-day slices | `mean()` of all images | slices of the same pass/day mosaicked first, so each acquisition counts once | yes, documented |
| Speckle filter | linear → `ee.Kernel.circle(radius 7, normalize)` → dB | identical (GEE) / identical kernel in NumPy (PC) | — |
| Paper text filter | "7×7 boxcar" | evaluated separately as sensitivity (`--filter square7`) | reported separately |
| Composite | temporal mean of filtered dB images | same | — |
| Windows | pre = Nov–Apr; post = Nov–Apr (6 mo) or Nov (1 mo) | pre = Nov–Apr; post = first k of Nov–Jan pool | k-scene windows are our experiment |
| Thresholds | −13.2 dB (6 mo), −12.7 dB (1 mo), from 2018 patches | published values reported + 2024-calibrated values | calibration documented |
| Erosion rule | pre > T AND post < T | same | — |
| Post-processing | none | none | — |

## 3. SAGE-River
- **S (season matching)**: dry-season composites before and after the monsoon; identical for all methods (common control, not a contribution).
- **A (agreement)**: each post scene votes sand/water if VV < T_scene; erosion requires ≥ m votes of k. Majority m = ⌊k/2⌋+1, unanimous m = k. For k = 1 no agreement is possible.
- **G (confidence gating)**: values within ±δ dB of a threshold are "unsure". Three-valued logic: erosion = VEG_pre ∧ SAND_post; decided non-erosion when either term is confidently false, decided erosion when both are confidently true, otherwise UNCERTAIN. Gating is a **selective decision (abstention) rule**, not a calibrated probability.
- **A+G**: per-scene votes with the ±δ band; post term true if #SAND ≥ m, false if #SAND + #UNSURE < m, else uncertain.

## 4. Where AI/ML is (and is not) used
- No neural network, no PINN, no forecasting model.
- Data-driven components: supervised threshold calibration on a held-out validation year (Youden-optimal class separation), validation-based model selection (m, δ) under a coverage constraint, and selective classification / abstention.
- Honest description: an *intelligent geospatial reliability-evaluation framework* built on rule-based SAR classification.
