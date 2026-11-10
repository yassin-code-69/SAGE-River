# SAGE-River — Season-matched, Agreement-Gated Erosion Mapping

**How Many Sentinel-1 Scenes Are Enough? Scene-Count Sensitivity and Agreement-Gated Reliability of Post-Monsoon Riverbank Erosion Maps — Jamuna River, Bangladesh**
IEEE BUBT Academic Research Showcase 2026 · Track 1 (Intelligent Computing, AI & Data Technologies)

Historical post-monsoon erosion detection and its reliability — **not** forecasting, **not** a PINN.
Baseline: Freihardt & Frey (2023), NHESS 23:751–770, doi:10.5194/nhess-23-751-2023; code doi:10.5281/zenodo.7253121.

## Quick start (Windows PowerShell)
```powershell
cd "d:\Program Work\Project in Vibe Coding\BUBT_PP_P\SAGE-River"
python -m venv .venv                      # Python 3.14 (3.11 launcher entry exists but its executable is missing)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd python
..\.venv\Scripts\python.exe metrics.py          # self-test
..\.venv\Scripts\python.exe sage_methods.py     # self-test
```

### Optional: Google Earth Engine (preferred SAR source = COPERNICUS/S1_GRD σ⁰)
```powershell
..\.venv\Scripts\python.exe gee_auth_check.py --auth                 # browser login (once)
..\.venv\Scripts\python.exe gee_auth_check.py --project <CLOUD_PROJECT_ID>
```
Without Earth Engine the pipeline uses the public Microsoft Planetary Computer (`sentinel-1-rtc` γ⁰, `sentinel-2-l2a`), no login.

## Full reproduction (from `python/`)
| Step | Command | Output |
|---|---|---|
| 1 Reconnaissance | `study_area_scan.py` | `outputs/maps/recon_*.png` |
| 2 Freeze AOI | `select_aoi.py <box> <xmin> <ymin> <xmax> <ymax> "<name>" "<why>"` (UTM45N km; exact call in `data/aoi/aoi.geojson` properties) | `data/aoi/`, `figure_0_study_area.png` |
| 3 GEE scripts | `build_gee_scripts.py` | `gee/01..07_*.js` (paste into code.earthengine.google.com) |
| 4 Scene inventory | `scene_analysis.py [--gee]` | `outputs/tables/sentinel1_*.csv`, `figure_A_scene_availability.png` |
| 5 SAR stacks | `s1_stack.py --source pc --year 2024` and `--year 2025` (or `--source gee`) | `data/cache/s1_<src>_<year>.npz/.json` |
| 6 Reference | `reference_validation.py 2024 2025` | `data/reference/s2_reference_<year>.npz/.json` |
| 7 Point check | `validation_points.py sample 2025` → label → `validation_points.py score 2025` | `reference_point_agreement_2025.csv` |
| 8 Experiments | `experiment_runner.py --source pc` | `experiment_A_*`, `experiment_B_*`, `selected_parameters_*.json` |
| 9 Figures | `generate_figures.py --source pc` | `figure_B/C/D/E_*.png` |
| 10 Poster | `build_poster.py --source pc` then `export_pdf.ps1` | `poster/poster_editable.pptx`, `poster/poster_final.pdf` |
| 11 Audit | `final_audit.py --source pc` | `outputs/reports/final_audit.md` |

## Folder map
`docs/` research documents · `gee/` Code Editor scripts · `python/` pipeline · `data/` AOI, metadata, reference (cache is not versioned) · `outputs/` tables, figures, maps, reports · `poster/` · `presentation/` · `references/` primary sources with checksums.

## Integrity rules (enforced in code)
2024 = validation (all tuning), 2025 = test (frozen parameters, timestamped). Same scenes/preprocessing/reference for every method. Exhaustive scene subsets (overlapping → SD is subset variability). Abstentions always reported with coverage. Sentinel-2 is an independent optical reference, not ground truth.

See `outputs/reports/final_project_report.md` for what was completed, verified and what remains.
