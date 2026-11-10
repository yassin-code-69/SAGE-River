# Root-cause audit — the 31 January 2026 Sentinel-1 scene (Kurigram reach)

**Question.** Why did a single post-monsoon scene (S1A, relative orbit 114 ascending, 31 Jan 2026 12:05 UTC) produce about 150 ha of false erosion with the published thresholds and about 197 ha with the 2024-tuned thresholds? The other seven scenes produced 2–23 ha each.

*These figures are from the Planetary Computer RTC γ⁰ run, where the audit started. On the primary GEE σ⁰ stack, the same scene alone gives 265 ha (published thresholds) and 160 ha (tuned thresholds); the other seven scenes give 2–10 ha each with the tuned thresholds (`experiment_A_all_subsets_gee.csv`).*

**Conclusion.** No implementation error was found. The false erosion comes from **temporarily inundated agricultural fields** on the west floodplain:
- they are dark in independent radar processing chains and in a second viewing geometry;
- Sentinel-2 shows them as open water from about 28 January to 12 February 2026.

The scene is **not** excluded from any experiment. It is a real example of the confounder the project is about: temporary water mistaken for permanent riverbank loss.

All numbers come from `outputs/tables/audit_20260131_*.csv` and `audit_20260131_morphology.json`. The figure is `outputs/figures/supp_audit_20260131.png`. The script is `python/audit_scene_20260131.py`.

## 1. Implementation checks (performed first)
| Check | Result | Verdict |
|---|---|---|
| Metadata of all 8 post scenes | Same platform (S1A), same relative orbit (114), same product family. PC STAC lists no differing processing fields. | no anomaly |
| NoData / invalid values (unfiltered RTC, AOI) | Valid fraction 1.000; 0 zero and 0 negative values; median −10.34 dB (vs −10.13 dB on 19 Jan) | no anomaly |
| Raster alignment | FFT phase-correlation shift vs 19 Jan = 0 rows / 0 columns for all 8 scenes | no misregistration |
| Scene-wide radiometry | Stable-vegetation median −7.28 dB (other dates −7.6 to −8.1); settlement median 0.90 dB (0.60–0.87); water median −19.0 dB (−18.9 to −20.2) | no global offset |
| Mosaicking / masks | One RTC item covers the AOI on that date (no slice seam); the same per-scene filter is used for every scene | no anomaly |
| Thresholds | Identical for all scenes. Only the *fraction* of S2-vegetated domain pixels below −12.7 dB differs: 4.7 % on 31 Jan vs 0.02–0.21 % on the other dates | localized, not a threshold bug |

## 2. Morphology of the false erosion
- 149.9 ha in 115 connected patches (26 of them ≥ 1 ha; largest 40.3 ha).
- 98.9 % on the west floodplain.
- Median distance to the main channel complex: 584 m.
- The patches are field-shaped, not bank-shaped.

## 3. Independent corroboration
| Evidence | Anomaly patches | Control fields |
|---|---|---|
| PC RTC γ⁰, 31 Jan (unfiltered) | −14.6 dB | −7.8 dB |
| PC RTC γ⁰, 19 Jan (unfiltered) | −9.9 dB | −8.1 dB |
| **GEE COPERNICUS/S1_GRD σ⁰, 31 Jan** (independent processing) | **−15.0 dB** | −8.2 dB |
| GEE σ⁰, 19 Jan | −10.6 dB | −8.4 dB |
| **PC RTC R150 descending, 2 Feb** (other geometry, +2 days) | **−13.1 dB** | −7.4 dB |
| Sentinel-2, 23 Jan | NDVI 0.09, MNDWI −0.09; 42 % MNDWI > 0 | NDVI 0.40; 2 % |
| Sentinel-2, 28 Jan | NDVI 0.11, MNDWI +0.32; **88 % water** | NDVI 0.48; 4 % |
| Sentinel-2, 7 Feb | NDVI 0.17, MNDWI +0.36; **99 % water** | NDVI 0.52; 10 % |
| Sentinel-2, 12 Feb | NDVI 0.24, MNDWI +0.32; 99 % water | NDVI 0.46; 12 % |

**Interpretation.** The fields were flooded from late January to mid-February 2026, and NDVI then rose as the crop grew. This is consistent with irrigation or puddling for dry-season (boro) rice, but **it has not been verified in the field**. By the Feb–Mar composite the fields count as vegetated, so the reference labels them non-erosion. The SAR rule saw "vegetated before, water after" and therefore flagged erosion.

## 4. Consequences
1. No bug fix was needed. The v1 results stand unchanged.
2. Temporal agreement already suppresses this mechanism when k ≥ 2. A single-scene map cannot.
3. SAGE-River v2 adds a map-date, SAR-only bank-connectivity test, motivated by the 584 m median distance of these patches from the channel.
   - **Measured afterwards (GEE σ⁰, `v2_hc_only_metrics_gee.csv`), the test only partly works.** The single-scene (k = 1) v2 HIGH-CONFIDENCE map for 31 Jan still contains **104 ha** of false erosion. That is less than v1 gating alone (234 ha) and the tuned baseline (160 ha), but far from zero, because some flooded fields connect to the channel through candidate pixels.
   - With k ≥ 2, temporal agreement removes the error: 2-scene subsets containing 31 Jan give 1.1 ha (v2 HC) and 1.6 ha (v1).
   - *Correction note, 11 Nov 2026: an earlier version of this item claimed v2 places the fields outside HIGH-CONFIDENCE; that claim had not been checked and is withdrawn.*
4. The scene is kept in every subset, so no difficult data were removed to improve accuracy.
