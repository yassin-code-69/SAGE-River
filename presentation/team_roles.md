# Team Roles and Responsibilities

Replace `Member A–D` with real names. **Every member must be able to explain the whole workflow** (problem → data → baseline → SAGE-River → validation → results → limitations) in two minutes.

| Role | Owner | Must be able to explain | Evidence to point at on the poster |
|---|---|---|---|
| Satellite data & study area | Member A | Why Sentinel-1 (radar, all-weather); why only 2–3 scenes in November (12-day revisit, one look direction); how the reach was chosen | Figure A, study-area map, `sentinel1_acquisitions.csv` |
| Baseline & SAGE-River code | Member B | Freihardt & Frey rule (pre > T, post < T); circle(r=7) vs 7×7 filter; agreement (m-of-k) and gating (±δ, UNCERTAIN) | Method panel, `python/sage_methods.py` |
| Validation & metrics | Member C | Sentinel-2 reference (NDVI/MNDWI, channel connectivity, outer-bank strip); why it is *not* ground truth; precision/recall/F1/IoU/coverage; 2024 tuning vs 2025 test | Figures B, C, D; `experiment_A_summary_*.csv` |
| Poster, pitch & Q&A lead | Member D | 30-s pitch, 2-min pitch, limitations; what we do **not** claim | Poster, `judges_qa.md` |

## Rehearsal checklist (13 Nov morning)
- [ ] Each member gives the 30-second pitch without notes.
- [ ] Each member answers 5 random questions from `judges_qa.md`.
- [ ] Each member can point to where a number on the poster comes from (CSV file name).
- [ ] Spot-check ≥ 20 validation points in `data/reference/validation_points_2025.csv` (column `team_check`).
- [ ] Fill in names, department, contact e-mail on the poster (placeholders in brackets).
