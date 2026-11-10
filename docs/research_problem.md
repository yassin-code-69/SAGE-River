# Research Problem

## Real-world problem
Riverbank erosion on the Jamuna (Brahmaputra) destroys farmland and homesteads every monsoon; CEGIS monitored ~348 ha of Jamuna bank erosion in 2025 alone (CEGIS 2026, Table 2). Post-monsoon maps of *where land was lost* help agencies and communities prepare before the next monsoon.

Sentinel-1 C-band SAR images the surface through clouds, so radar is attractive for the cloudy monsoon/post-monsoon period. Freihardt & Frey (2023) showed that a simple Sentinel-1 threshold rule in Google Earth Engine can map historical erosion on the Jamuna and that erosion "can be determined already 1 month after the end of the monsoon".

## Why observations are limited (verified locally, not assumed)
- Radar is **not** limited by clouds. The limitation is **acquisition geometry and time**: over our reach only two relative orbits exist (R114 ascending, R150 descending), each imaged every **12 days** (see `outputs/tables/sentinel1_acquisitions.csv`).
- The published workflow uses a **single look direction** (ascending) to keep geometry consistent. A one-month early-mapping window therefore contains only **2–3 comparable scenes**.
- Sentinel-1B contributed almost nothing over this area (2019–2020 only, a handful of scenes) — its 2021 failure is **not** the cause of local sparsity.

## Scientific problem
With only a few scenes, speckle, wet-sand/water ambiguity and lingering floodwater can push pixels across the vegetation/sand threshold, creating **false erosion**, while missing real erosion. The published study varied window length but evaluated only backscatter statistics of reference patches and validated *land cover*, not the *erosion map*.

## Research questions
- **RQ1** How do Precision, Recall, F1 and IoU of the erosion map change as the number of post-monsoon Sentinel-1 scenes decreases (k = 1, 2, 3, 6, 8)?
- **RQ2** Does m-of-k temporal agreement reduce false erosion, and at what recall cost?
- **RQ3** Does a threshold-margin abstention band (UNCERTAIN class) raise precision on decided pixels, and how much decision coverage is lost?
- **RQ4** What is the trade-off between map timeliness (first 1–3 acquisitions after 1 November) and agreement with a later independent reference?

## Scope (explicit)
Historical post-monsoon erosion detection and its reliability. NOT forecasting, NOT a PINN, NOT hydrodynamic or geotechnical modelling, NOT a replacement for CEGIS/BWDB systems.
