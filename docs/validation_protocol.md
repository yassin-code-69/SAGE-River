# Validation Protocol — Independent Sentinel-2 Reference

**The reference is an independent optical-sensor reference derived from Sentinel-2 L2A surface reflectance. It is NOT field ground truth.**

## 1. Data
- Sentinel-2 L2A (ESA Sen2Cor surface reflectance), the same product as `COPERNICUS/S2_SR_HARMONIZED`, accessed through the Planetary Computer STAC (public). Processing-baseline ≥ 04.00 offset (−1000 DN) is removed, i.e. values are harmonised.
- Cloud handling: Scene Classification Layer (SCL) classes 0, 1, 3, 8, 9, 10 masked (no data, saturated, cloud shadow, medium/high cloud, cirrus). Cloud Score+ is used in the GEE version of the script (`gee/05_sentinel2_reference.js`); the Python run uses SCL because it does not require login. The per-pixel number of clear dates (`nobs`) is stored; < 3 clear dates → reference UNCERTAIN.
- AOI-level clear-observation statistics are written to `outputs/tables/s2_reference_quality.csv` (not tile-level cloud percentages).

## 2. Composites and classes
Median of clear observations, Feb–Mar of each year (driest, least-cloudy months; same season every year so crop calendar and water stage are matched). Classes: VEG (NDVI ≥ 0.30, not water), WATER (MNDWI ≥ 0), SAND/BARE (NDVI < 0.20, not water), AMBIGUOUS (otherwise).
Thresholds were fixed a priori from typical dry-season values and are **checked**, not tuned, against visual interpretation of stratified points (section 5). NDVI 0.1 (used by Freihardt & Frey for L1C TOA) is **not** assumed.

## 3. Reference erosion label
erosion = VEG(Feb–Mar Y) AND WATER|SAND(Feb–Mar Y+1) AND the new sand/water patch is connected (8-neighbour) to the post-monsoon channel complex (sand/water components touching the largest water body).
Vegetation→bare patches **not connected** to the channel (harvested/fallow fields, ponds) are labelled UNCERTAIN and excluded, because they are not riverbank erosion but would otherwise be counted as reference erosion.

## 4. Evaluation domain (outer banks only)
For each image row, the westmost and eastmost pixels of the Feb–Mar(Y) channel complex define the outer bank lines; the domain is the 1.5 km strip outside each line (floodplain side). In-channel chars/sandbars are excluded, following the published baseline's outer-bank focus. Pixels with reference UNCERTAIN are excluded from scoring for every method alike; their area is reported.

## 5. Point-based check of the reference (stratified)
- Sample: stratified random points inside the evaluation domain (strata: reference erosion, reference non-erosion near the bank line, reference uncertain), seed 20251108.
- Interpretation: true-colour Sentinel-2 chips (Feb–Mar Y and Feb–Mar Y+1, 600 m × 600 m) inspected visually; label one of {eroded (vegetated/settled land → sand or water), not eroded, cannot tell}.
- Interpreter: the AI analyst (Claude) performed the first-pass visual labelling; **the team must spot-check at least 20 points before presenting** (sheet `data/reference/validation_points_<year>.csv` has an empty `team_check` column).
- Reported: agreement between automatic reference labels and visual labels per stratum. If agreement on the erosion stratum is poor, map accuracy is reported only as *agreement with the optical reference*, not as validated accuracy.

## 6. Temporal target
The Feb–Mar(Y+1) reference represents cumulative change after the monsoon. An early SAR map (e.g. 8 Nov) cannot see erosion that happens later in the falling stage. Experiment B therefore also scores against an "as-of mid-December" subset (reference erosion already sand/water in the 10 Nov–15 Dec S2 composite).
