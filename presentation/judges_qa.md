# Judges' Technical Q&A — SAGE-River

> Numbers quoted here come from files in `outputs/tables/`. Section R (results) is generated from the final runs — re-read it before the event.

### 1. What exactly is your research problem?
When an erosion map must be made soon after the monsoon, only a few comparable Sentinel-1 scenes exist (2–3 in November for one look direction over our reach). We measure how the reliability of the published Sentinel-1 erosion-mapping rule changes with the number of scenes, and test two safeguards — temporal agreement and confidence-based abstention.

### 2. Why is this important in Bangladesh?
The Jamuna erodes hundreds of hectares every year (CEGIS monitored ~348 ha in 2025). Post-monsoon maps of lost land support relief, planning and protection works before the next monsoon. A map that shows false erosion wastes attention; one that hides erosion is dangerous — so reliability matters.

### 3. What did Freihardt & Frey already do?
They built the Sentinel-1/GEE workflow: VV ascending, speckle filter, temporal mean, threshold −13.2/−12.7 dB, erosion = vegetation before and sand/water after. They studied window length and filters through backscatter statistics, validated land cover (≈88–91 % overall accuracy) and showed erosion can be mapped about one month after the monsoon. They did not quantify erosion-map accuracy versus number of scenes and used no agreement or abstention rule for erosion.

### 4. What is your research gap?
An erosion-map-level, scene-count reliability evaluation of that workflow against an independent optical reference, with agreement and abstention rules and decision-coverage reporting. To our knowledge this combination has not been reported in the reviewed literature; each component exists separately in other domains (flood mapping, deforestation alerts).

### 5. What is different about SAGE-River?
S = season-matched comparison (already in the baseline — common control). A = a pixel is eroded only if ≥ m of k post-monsoon scenes agree. G = pixels too close to the threshold are labelled UNCERTAIN instead of forced into a class. We always report how many pixels were decided.

### 6. Why is Sentinel-1 useful?
C-band radar sees through clouds and works day/night; water and smooth sand give low backscatter, vegetation and settlements higher backscatter. It is free, 10 m, and available in Google Earth Engine.

### 7. Why are observations sparse if radar sees through clouds?
Not because of clouds. Over our reach only two relative orbits exist (R114 ascending, R150 descending), each every 12 days. The baseline uses one look direction to keep geometry consistent, so a 1-month window has only 2–3 scenes. Sentinel-1B added almost nothing here (a handful of scenes in 2019–2020), so its failure is not the reason.

### 8. How do you distinguish temporary flooding from permanent erosion?
(1) Season matching: dry-season composites before and after the monsoon, not peak-flood images. (2) Agreement: one wet scene is not enough; several scenes must agree. (3) Reference: the optical label requires the land to still be sand/water in the next Feb–Mar and to be connected to the river channel.

### 9. What is your independent reference?
Sentinel-2 L2A surface reflectance (a different sensor): vegetated in Feb–Mar before the monsoon (NDVI ≥ 0.30) and water (MNDWI ≥ 0) or bare sand (NDVI < 0.20) in the next Feb–Mar, connected to the channel, inside a 1.5 km outer-bank strip. Points were visually checked.

### 10. Is the Sentinel-2 reference field ground truth?
No. It is an independent optical-sensor reference with its own errors (mixed pixels, crop calendar, cloud residue). We call results "agreement with an independent optical reference".

### 11. How do you prevent data leakage?
All thresholds, m and δ were chosen on the 2024 monsoon and frozen (timestamped JSON) before the 2025 test was computed; the 2025 reference was never used for tuning. Early maps use no future scenes. All methods use the same scenes, preprocessing, reference and evaluation domain. We do not split adjacent pixels into train/test.

### 12. How do you measure uncertainty?
We do not estimate a calibrated probability. G is a decision-abstention rule: a pixel within ±δ dB of the threshold is UNCERTAIN. We report precision/recall on decided pixels together with decision coverage and the reference erosion area that fell into abstention.

### 13. What if SAGE-River does not outperform the baseline?
Then that is our finding, reported honestly. A reliability study is valuable when it shows a safeguard does *not* help, or when it buys precision only by losing recall or coverage.

### 14. What are your limitations?
One reach, one test monsoon; optical reference not field truth; threshold-based classifier; ascending orbit only; overlapping scene subsets are not independent samples; the later reference includes erosion after early map dates; Planetary-Computer γ⁰ data used if Earth Engine σ⁰ was not available (see final report).

### 15. Can CEGIS or BWDB use this?
Not as a replacement for their operational systems. The evaluation protocol (scene-count check + agreement + abstention with coverage) could be added to any SAR-based post-monsoon mapping to flag where a quick map is unreliable — after testing on more reaches and years.

### 16. Is this a PINN / do you predict future erosion?
No. No neural network and no physics model. We map past erosion and evaluate its reliability; we do not forecast.

### 17. Where is the AI / intelligent computing?
Data-driven threshold calibration on a held-out year, validation-based model selection under a coverage constraint, and selective classification (abstention) — an intelligent geospatial reliability-evaluation framework. We deliberately did not add deep learning without labelled training data.

## R. Results-specific answers
(see `presentation/judges_qa_results.md`, generated after the final runs)
