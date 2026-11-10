"""Assemble standalone GEE Code Editor scripts: header (with the final AOI bbox) + body.

Run after select_aoi.py:  python build_gee_scripts.py
Writes gee/01_scene_inventory.js ... gee/07_validation.js
"""
import re

import config as C
from aoi import load_aoi_ll

GEE = C.ROOT / "gee"


def main():
    lon0, lat0, lon1, lat1 = load_aoi_ll(bbox=True)
    header = (GEE / "00_common_header.js").read_text(encoding="utf-8")
    header = re.sub(r"/\*AOI_BBOX\*/.*?/\*END_AOI_BBOX\*/",
                    f"/*AOI_BBOX*/[{lon0:.5f}, {lat0:.5f}, {lon1:.5f}, {lat1:.5f}]/*END_AOI_BBOX*/", header)
    (GEE / "00_common_header.js").write_text(header, encoding="utf-8")
    for body in sorted((GEE / "src").glob("*.body.js")):
        name = body.name.replace(".body.js", ".js")
        (GEE / name).write_text(header + "\n" + body.read_text(encoding="utf-8"), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
