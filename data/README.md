# data/

| Path | Content | Provenance |
|---|---|---|
| `aoi/aoi.geojson`, `aoi/grid.json` | Final study AOI (WGS84 polygon + UTM45N bounds, rationale) and the 10 m analysis grid | `python/select_aoi.py` |
| `metadata/phase0_asf/` | Phase 0 ASF catalogue CSVs for five candidate points (11 Nov 2026, 00:07) | ASF search API, public |
| `metadata/phase0_earthsearch_s2/` | Phase 0 Element84 Earth Search S2 tile-level cloud summaries | public STAC |
| `metadata/gee_project.json` | (only if provided) Earth Engine Cloud project ID — **not** committed (`.gitignore`) | user |
| `reference/s2_reference_<year>.npz/.json` | Sentinel-2 reference layers (classes, reference label, domain, RGB) and metadata (item IDs, thresholds, counts) | `python/reference_validation.py` |
| `reference/validation_points_<year>.csv` | Stratified points with automatic and visual labels; `team_check` column for the team | `python/validation_points.py` |
| `cache/` (not versioned) | Downloaded SAR stacks `s1_<source>_<year>[_filter].npz` + JSON with product IDs; S2 composites per window; reconnaissance composites | `python/s1_stack.py`, `reference_validation.py`, `study_area_scan.py` |

No raw scenes are stored — only small AOI windows (10 m) read from cloud-optimised GeoTIFFs. Everything can be regenerated with the commands in the main README.
