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

### 2.1 Two SAR data sources (both documented, never mixed in one experiment)
| Source | Tag | Status | Notes |
|---|---|---|---|
| Google Earth Engine `COPERNICUS/S1_GRD` σ⁰ (ellipsoid-corrected, GRD), per-image angle mask, circle(r=7) filter in each image's native grid, then per-day mosaic | `gee` | **Primary** (the baseline's own data). Run on 11 Nov 2026 after the Earth Engine API was enabled. Complete scene pools: 2024 pre 14 / post 8; 2025 pre 16 / post 8 | closest available reproduction of the released code. Remaining differences: an explicit relative-orbit filter (no data effect) and the per-day mosaic |
| Microsoft Planetary Computer `sentinel-1-rtc` γ⁰ (terrain-flattened) | `pc` | **Adapted cross-check only**, NOT a reproduction of the GEE σ⁰ workflow | no angle band (angle mask not applied); γ⁰ ≈ σ⁰ + ~1 dB on flat ground, so published thresholds do not transfer; archive gaps (2024 post pool 6 of 8, pre 11–12 of 14–16) |

Thresholds tuned on 2024 erosion F1 with GEE σ⁰ (T_pre = −13.15 / −12.65 dB, T_post = −13.25 / −12.7 dB for k = 3 / 6–8) are close to the published −13.2 / −12.7 dB. This independently supports the σ⁰ reproduction.

## 3. SAGE-River
- **S (season matching)**: dry-season composites before and after the monsoon; identical for all methods (common control, not a contribution).
- **A (agreement)**: each post scene votes sand/water if VV < T_scene; erosion requires ≥ m votes of k. Majority m = ⌊k/2⌋+1, unanimous m = k. For k = 1 no agreement is possible.
- **G (confidence gating)**: values within ±δ dB of a threshold are "unsure". Three-valued logic: erosion = VEG_pre ∧ SAND_post; decided non-erosion when either term is confidently false, decided erosion when both are confidently true, otherwise UNCERTAIN. Gating is a **selective decision (abstention) rule**, not a calibrated probability.
- **A+G**: per-scene votes with the ±δ band; post term true if #SAND ≥ m, false if #SAND + #UNSURE < m, else uncertain.

### 3.1 SAGE-River v2 — triage + prioritized review (pre-registered; `docs/sage_river_v2_design.md`)
- **Map-date geometry from SAR only:**
  - the channel = pre composite < T_pre, components ≥ 1 km²;
  - a 3-px bank buffer and a distance transform.
- **Candidates:**
  - pre_comp > T_pre − δ with at least one "possible" vote;
  - plus all v1 confident pixels;
  - grouped into 8-connected patches.
- **Classes:**
  - HIGH-CONFIDENCE = v1 confident pixels in bank-touching patches;
  - REVIEW = other candidates in patches within D_review = 100 m of the bank;
  - LIKELY STABLE = the rest.
- **Ranking:** logistic regression on 7 map-date patch features, trained on the validation year only. The later Sentinel-2 reference is never an input.
- **Evaluation:**
  - simulated oracle review at fixed area budgets;
  - compared with 500 random orders and with random review of v1 UNCERTAIN pixels.
- **Results:** `docs/sage_river_v2_results.md`.

## 4. Where AI/ML is (and is not) used
- No neural network, no PINN, no forecasting model.
- Data-driven components:
  - supervised threshold calibration on a held-out validation year (Youden-optimal class separation);
  - validation-based model selection (m, δ) under a coverage constraint;
  - selective classification / abstention;
  - in v2, a learned patch-ranking model (logistic regression) that prioritizes human review.
- Honest description: an *intelligent geospatial reliability-evaluation framework* built on rule-based SAR classification.
