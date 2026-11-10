"""Earth Engine authentication + connectivity check for SAGE-River.

Usage (from the SAGE-River folder):
    .venv\\Scripts\\python.exe python\\gee_auth_check.py --auth            # opens browser login (localhost flow)
    .venv\\Scripts\\python.exe python\\gee_auth_check.py --project MY_ID   # test initialisation with a Cloud project

Never prints or stores tokens. Credentials are written by the earthengine-api to
%USERPROFILE%\\.config\\earthengine\\credentials (outside the repository).
"""
import argparse
import json
import sys
from pathlib import Path

import ee

CRED = Path.home() / ".config" / "earthengine" / "credentials"
PROJECT_FILE = Path(__file__).resolve().parents[1] / "data" / "metadata" / "gee_project.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auth", action="store_true", help="run browser-based localhost authentication")
    ap.add_argument("--project", default=None, help="Google Cloud project ID registered for Earth Engine")
    a = ap.parse_args()

    if a.auth:
        ee.Authenticate(auth_mode="localhost", force=False)
    print("credentials file present:", CRED.exists())
    if not CRED.exists():
        sys.exit(2)

    project = a.project
    if project is None and PROJECT_FILE.exists():
        project = json.loads(PROJECT_FILE.read_text())["project"]
    if project is None:
        try:
            project = json.loads(CRED.read_text()).get("project")
        except Exception:
            project = None
    print("project:", project)
    ee.Initialize(project=project)
    n = ee.ImageCollection("COPERNICUS/S1_GRD").filterDate("2025-11-01", "2025-11-30") \
        .filterBounds(ee.Geometry.Point(89.69, 25.50)).size().getInfo()
    print("EE OK — S1_GRD images over Kurigram test point, Nov 2025:", n)
    if project:
        PROJECT_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROJECT_FILE.write_text(json.dumps({"project": project}))


if __name__ == "__main__":
    main()
