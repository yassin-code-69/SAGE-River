# Research Gap and Contribution Statement

## What is already established (do not claim)
- Sentinel-1 SAR + GEE threshold mapping of historical Jamuna erosion (Freihardt & Frey 2023).
- That erosion can be mapped ~1 month after the monsoon (ibid., abstract) — **not our finding**.
- Effects of sampling duration and speckle filtering on **backscatter statistics** (ibid., Sect. 3.1).
- Season-matched dry-season comparison (ibid.) — used here as a **common control**, not a contribution.
- Temporal aggregation windows for SAR water mapping (Peña-Luque et al. 2021); m-of-k confirmation rules in operational flood (NASA MCDWD) and SAR deforestation alerts (RADD, Reiche et al. 2021); uncertainty/exclusion layers and abstention in SAR flood mapping (GFM / Krullikowski et al. 2023; Li, Matgen & Chini 2026; DLR fuzzy logic).
- Physics/hydraulic erosion forecasting for the Jamuna (Shampa et al. 2025) and operational prediction (CEGIS).

## Gap (as found in the reviewed literature)
Freihardt & Frey validated land cover (overall accuracy 87.5–90.6 %) and inspected erosion maps visually; they did not quantify **erosion-map-level** accuracy as a function of the **number of scenes**, nor test agreement or abstention rules for erosion. Component techniques exist in other domains, but we did not identify a study that evaluates them together for SAR riverbank-erosion maps against an independent optical reference with decision-coverage reporting.

## Contribution statement (poster wording)
> We extend the Sentinel-1/GEE erosion workflow of Freihardt & Frey (2023) with a reliability evaluation:
> (i) how erosion-map accuracy changes with the number of post-monsoon scenes (exhaustive scene-budget subsets and chronological first-k maps),
> (ii) an m-of-k temporal-agreement rule adapted from operational products, and
> (iii) a threshold-margin abstention band reported as precision/recall versus decision coverage,
> evaluated against an independent Sentinel-2 reference on a Jamuna reach.
> To our knowledge, this specific combination of evaluations has not been identified in the reviewed literature.

## Words we avoid
"first", "novel framework", "uncertainty quantification" (a margin band is not a calibrated probability), "ground truth" (Sentinel-2 is an independent optical reference), "prediction/forecast", "PINN".
