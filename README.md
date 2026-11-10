# SAGE-River — Season-matched, Agreement-Gated Erosion Mapping (v1) with Quality-Aware Triage and Prioritized Review (v2)

**How Many Sentinel-1 Scenes Are Enough? Scene-Count Sensitivity, Agreement-Gated Reliability and Prioritized Review of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh**

IEEE BUBT Academic Research Showcase 2026 · Track 1 (Intelligent Computing, AI & Data Technologies)

The project does historical post-monsoon erosion detection and checks how reliable it is. It is **not** forecasting and **not** a PINN.

Baseline: Freihardt & Frey (2023), NHESS 23:751–770, doi:10.5194/nhess-23-751-2023; code doi:10.5281/zenodo.7253121.

**Results in one place:**
- `outputs/reports/final_project_report.md` (status);
- `docs/sage_river_v2_results.md` (v2 and the updated conclusion);
- `outputs/reports/root_cause_audit_20260131.md` (the bad-scene audit).

## Quick start (Windows PowerShell)
```powershell
cd "d:\Program Work\Project in Vibe Coding\BUBT_PP_P\SAGE-River"
python -m venv .venv                      # Python 3.14
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd python
..\.venv\Scripts\python.exe metrics.py          # self-test
..\.venv\Scripts\python.exe sage_methods.py     # self-test
```

### Google Earth Engine (primary SAR source = COPERNICUS/S1_GRD σ⁰)
```powershell
..\.venv\Scripts\python.exe gee_auth_check.py --auth                 # browser login (once; token stays in your user profile, not in the repo)
..\.venv\Scripts\python.exe gee_auth_check.py --project <CLOUD_PROJECT_ID>
```
The project ID is stored in `data/metadata/gee_project.json`. Without Earth Engine, the pipeline can use Microsoft Planetary Computer `sentinel-1-rtc` γ⁰ instead (`--source pc`, no login). That is an *adapted* cross-check, not a reproduction of the σ⁰ workflow.

## Full reproduction — development reach (Kurigram), from `python/`
| Step | Command | Output |
|---|---|---|
| 1 Reconnaissance | `study_area_scan.py` | `outputs/maps/recon_*.png` |
| 2 Freeze AOI | `select_aoi.py <box> <xmin> <ymin> <xmax> <ymax> "<name>" "<why>"` (UTM45N km) | `data/aoi/`, `figure_0_study_area.png` |
| 3 GEE scripts | `build_gee_scripts.py` | `gee/01..07_*.js` |
| 4 Scene inventory | `scene_analysis.py --gee` | `outputs/tables/sentinel1_*.csv`, Figure A |
| 5 SAR stacks | `s1_stack.py --source gee --year 2024` and `--year 2025` | `data/cache/s1_gee_<year>.npz/.json` |
| 6 Reference | `reference_validation.py 2024 2025` | `data/reference/s2_reference_<year>.npz/.json` |
| 7 Point check | `validation_points.py sample 2025` → label → `validation_points.py score 2025` | `reference_point_agreement_2025.csv` |
| 8 v1 experiments | `experiment_runner.py --source gee` | `experiment_A_*_gee`, `experiment_B_*_gee`, `selected_parameters_gee.json` |
| 9 Bad-scene audit | `audit_scene_20260131.py` | `audit_20260131_*.csv/json`, `supp_audit_20260131.png` |
| 10 v2 (triage + review) | `sage_v2.py --tag gee` | `v2_calibration_gee.json`, `v2_review_*_gee.csv`, `v2_hc_only_metrics_gee.csv` |
| 11 Figures | `generate_figures.py --source gee` | Figures B–F |
| 12 Poster | `build_poster.py --source gee`, then `..\poster\export_pdf.ps1` | `poster/poster_editable.pptx`, `poster/poster_final.pdf` |
| 13 Audit | `final_audit.py --source gee` | `outputs/reports/final_audit.md` |

## Independent reach (Sirajganj–Kazipur)
Set `SAGE_REACH`, and `config.py` redirects all data and outputs to `data/reaches/<reach>/` and `outputs/reaches/<reach>/`:
```powershell
$env:SAGE_REACH = "sirajganj"
..\.venv\Scripts\python.exe s1_stack.py --source gee --year 2024; ..\.venv\Scripts\python.exe s1_stack.py --source gee --year 2025
..\.venv\Scripts\python.exe reference_validation.py 2024 2025
..\.venv\Scripts\python.exe experiment_runner.py --source gee     # local calibration on Sirajganj 2024, test 2025
..\.venv\Scripts\python.exe sage_v2.py --tag gee
..\.venv\Scripts\python.exe transfer_eval.py                      # Kurigram-2024 parameters applied unchanged
Remove-Item Env:SAGE_REACH
..\.venv\Scripts\python.exe v2_criteria.py                        # pre-registered criteria, all evaluations
..\.venv\Scripts\python.exe v2_report.py tables; ..\.venv\Scripts\python.exe v2_report.py charts; ..\.venv\Scripts\python.exe v2_report.py map
```
- The Sirajganj AOI, GEE project file and validation points live in `data/reaches/sirajganj/`.
- Do **not** run `build_gee_scripts.py` with `SAGE_REACH` set, because it would overwrite the shared `gee/` folder.

## Pre-registration (v2)
- The design is in `docs/sage_river_v2_design.md`. Checksums and freeze times are in `docs/sage_river_v2_design.md5`.
- `final_audit.py --source gee` re-checks that:
  - the frozen files are unchanged;
  - the Sirajganj SAR stacks were created after the code freeze.
- Kurigram 2025 v2 results are **exploratory**. The Sirajganj evaluations are the independent tests.

## Folder map
| Folder | Contents |
|---|---|
| `docs/` | research documents (including v2 design and results) |
| `gee/` | Code Editor scripts |
| `python/` | pipeline |
| `data/` | AOI, metadata, reference; `reaches/` for the independent reach (the cache is not versioned) |
| `outputs/` | tables, figures, maps, reports; `reaches/` for the independent reach |
| `poster/` | poster files (`archive_v1_pc/` holds the earlier version) |
| `presentation/` | pitches, Q&A, figure explanations, team roles |
| `references/` | primary sources with checksums |

## Integrity rules (enforced in code)
- **Data split:** 2024 is used for validation (all tuning); 2025 is the test (frozen, timestamped parameters).
- **Same inputs for every method:** scenes, preprocessing and reference.
- **Exhaustive scene subsets:** they overlap, so SD reflects subset variability.
- **Reporting:** abstentions are always reported with coverage. v2 review effort is always reported in ha. The simulated reviewer is an oracle, i.e. an upper bound.
- **Reference:** Sentinel-2 is an independent optical reference, not ground truth.
