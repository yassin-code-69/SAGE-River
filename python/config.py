"""Central configuration for SAGE-River. Every experiment reads parameters from here so runs are reproducible.

All dates are inclusive start / exclusive end (Earth Engine convention) unless noted.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Study reach. "kurigram" (default) = the primary reach used to develop the method. Any other reach (set the
# environment variable SAGE_REACH, e.g. "sirajganj") gets its own data/ and outputs/ trees so that an
# independent evaluation never mixes with — or overwrites — the development reach.
REACH = os.environ.get("SAGE_REACH", "kurigram")
if REACH == "kurigram":
    DATA = ROOT / "data"
    OUT = ROOT / "outputs"
else:
    DATA = ROOT / "data" / "reaches" / REACH
    OUT = ROOT / "outputs" / "reaches" / REACH
CACHE = DATA / "cache"
TABLES = OUT / "tables"
FIGS = OUT / "figures"
MAPS = OUT / "maps"
REPORTS = OUT / "reports"
for p in (CACHE, TABLES, FIGS, MAPS, REPORTS, DATA / "aoi", DATA / "metadata", DATA / "reference"):
    p.mkdir(parents=True, exist_ok=True)

# Working projection: UTM 45N covers the whole Jamuna in Bangladesh (88-90E? Jamuna lies at ~89.5-89.9E).
WORK_CRS = "EPSG:32645"
PIXEL = 10.0  # metres, native Sentinel-1 GRD / Sentinel-2 10 m grid

# ---------------------------------------------------------------------------
# Baseline (Freihardt & Frey 2023, released code Zenodo 7253121) parameters
# ---------------------------------------------------------------------------
FF = {
    "collection": "COPERNICUS/S1_GRD",
    "instrumentMode": "IW",
    "resolution_meters": 10,
    "polarisation": "VV",
    "pass": "ASCENDING",
    "angle_min": 30.0,       # code lines 218-230: angle.gt(30)
    "angle_max": 45.0,       # angle.lt(45)
    "kernel_code": "circle_r7",   # code: ee.Kernel.circle({radius: 7, normalize: true}) applied in linear units
    "kernel_paper": "square_7x7",  # paper text: "7 x 7 boxcar"
    "T_6mo": -13.2,          # paper Sect. 2.5 / code line 1203
    "T_1mo": -12.7,          # paper Sect. 2.5 / code line 1208
}

# Relative orbit used for all experiments (ascending, the F&F look direction). Verified in inventory.
REL_ORBIT = 114

# ---------------------------------------------------------------------------
# Temporal design (validation monsoon 2024, test monsoon 2025)
# ---------------------------------------------------------------------------
YEARS = {
    2024: {  # VALIDATION / calibration year — the only year used to choose thresholds, m and delta
        "role": "validation",
        "pre": ("2023-11-01", "2024-05-01"),     # F&F 6-month dry-season composite before monsoon 2024
        "post_pool": ("2024-11-01", "2025-02-01"),  # Nov-Jan post-monsoon pool
        "s2_pre": ("2024-02-01", "2024-04-01"),  # Feb-Mar 2024 optical reference
        "s2_post": ("2025-02-01", "2025-04-01"),  # Feb-Mar 2025 optical reference
    },
    2025: {  # TEST year — never used for tuning
        "role": "test",
        "pre": ("2024-11-01", "2025-05-01"),
        "post_pool": ("2025-11-01", "2026-02-01"),
        "s2_pre": ("2025-02-01", "2025-04-01"),
        "s2_post": ("2026-02-01", "2026-04-01"),
    },
}

# Scene budgets for Experiment A (controlled, exhaustive combinations of the pool)
K_LIST = [1, 2, 3, 6, 8]
# Experiment B (chronological first-k after 1 November)
K_CHRONO = [1, 2, 3]

# SAGE-G candidate margins (dB) — chosen on 2024 only
DELTAS = [0.0, 0.5, 1.0, 1.5, 2.0]
# Pre-registered selection rule for delta/m (fixed BEFORE looking at 2025):
#   maximise F1 on decided pixels of the 2024 validation year subject to decision coverage >= COVERAGE_MIN
COVERAGE_MIN = 0.90

RANDOM_SEED = 20251108  # only used if a combination set has to be subsampled (documented)
