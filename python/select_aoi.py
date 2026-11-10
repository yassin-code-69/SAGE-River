"""Freeze the study AOI (after visual inspection of the reconnaissance maps) and draw Figure 0.

Usage: python select_aoi.py <box> <xmin_km> <ymin_km> <xmax_km> <ymax_km> "<name>" "<rationale>"
  coordinates in UTM 45N kilometres (as read from outputs/maps/recon_<box>.png grid lines)
Writes data/aoi/aoi.geojson, data/aoi/grid.json, outputs/figures/figure_0_study_area.png
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from pyproj import Transformer

import config as C
from aoi import save_aoi


def main():
    box, x0, y0, x1, y1, name, why = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6], sys.argv[7]
    b = (x0 * 1000, y0 * 1000, x1 * 1000, y1 * 1000)
    tr = Transformer.from_crs(C.WORK_CRS, "EPSG:4326", always_xy=True)
    c_lon, c_lat = tr.transform((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    grid = save_aoi(name, b, why, extra={"recon_box": box, "centre_lon": round(c_lon, 5), "centre_lat": round(c_lat, 5)})
    print("AOI saved", grid.to_dict(), "centre", c_lon, c_lat)
    # Figure 0: context (recon composite) + AOI rectangle
    fig, axes = plt.subplots(1, 2, figsize=(14, 9), dpi=200, gridspec_kw={"width_ratios": [1, 1.25]})
    for ax, year in zip(axes, (2025, 2026)):
        z = np.load(C.CACHE / "recon" / f"recon_{box}_{year}.npz")
        m = json.loads((C.CACHE / "recon" / f"recon_{box}_{year}.json").read_text())
        xmin, ymin, xmax, ymax = m["grid"]["bounds"]
        if ax is axes[0]:
            ax.imshow(np.nan_to_num(np.clip(z["rgb"] / 0.25, 0, 1), nan=1), extent=(xmin / 1000, xmax / 1000, ymin / 1000, ymax / 1000))
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="yellow", lw=2.5))
            ax.set_title(f"Context: Sentinel-2 Feb–Mar {year}, {box} (UTM 45N km)", fontsize=10)
        else:
            ax.imshow(np.nan_to_num(np.clip(z["rgb"] / 0.25, 0, 1), nan=1), extent=(xmin / 1000, xmax / 1000, ymin / 1000, ymax / 1000))
            ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
            ax.set_title(f"Study reach: {name}\nSentinel-2 Feb–Mar {year} (after the 2025 monsoon)", fontsize=10)
    lonlat = [tr.transform(x * 1000, y * 1000) for x, y in ((x0, y0), (x1, y1))]
    fig.text(0.5, 0.01, f"AOI {x1 - x0:.1f} km × {y1 - y0:.1f} km; corners {lonlat[0][0]:.4f}E {lonlat[0][1]:.4f}N – "
             f"{lonlat[1][0]:.4f}E {lonlat[1][1]:.4f}N; analysis grid EPSG:32645, 10 m", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(C.FIGS / "figure_0_study_area.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
