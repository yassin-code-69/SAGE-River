"""Public (no-login) access to Sentinel-1 RTC and Sentinel-2 L2A via Microsoft Planetary Computer STAC.

Used for (i) study-area reconnaissance, (ii) independent cross-check of the scene inventory, and
(iii) as the fallback SAR source if Earth Engine authentication is unavailable.
Reads only small windows of cloud-optimised GeoTIFFs onto a common UTM grid.
"""
import time

import numpy as np
import planetary_computer as pc
import rasterio
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.transform import from_origin

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def client():
    return Client.open(STAC_URL, modifier=pc.sign_inplace)


def search(collection, bbox_ll, start, end, query=None, max_items=500):
    for attempt in range(4):
        try:
            s = client().search(collections=[collection], bbox=bbox_ll, datetime=f"{start}/{end}",
                                query=query or {}, max_items=max_items)
            return list(s.items())
        except Exception as e:  # transient API errors
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))


class Grid:
    """A north-up grid in WORK_CRS defined by bounds (xmin, ymin, xmax, ymax) and pixel size."""

    def __init__(self, crs, bounds, res):
        self.crs = crs
        xmin, ymin, xmax, ymax = bounds
        self.res = res
        self.width = int(round((xmax - xmin) / res))
        self.height = int(round((ymax - ymin) / res))
        self.transform = from_origin(xmin, ymax, res, res)
        self.bounds = (xmin, ymax - self.height * res, xmin + self.width * res, ymax)

    def to_dict(self):
        return {"crs": self.crs, "bounds": self.bounds, "res": self.res, "width": self.width, "height": self.height}


def read_to_grid(href, grid, resampling=Resampling.bilinear, nodata=None, dtype="float32", overview_level=None):
    """Reproject a (remote) raster asset onto `grid`; returns a 2-D array with NaN for missing data.

    overview_level: read a COG overview (0 = first, 2x coarser) — used only for coarse reconnaissance.
    """
    for attempt in range(4):
        try:
            kw = {} if overview_level is None else {"overview_level": overview_level}
            with rasterio.open(href, **kw) as src:
                nd = src.nodata if nodata is None else nodata
                with WarpedVRT(src, crs=grid.crs, transform=grid.transform, width=grid.width, height=grid.height,
                               resampling=resampling, src_nodata=nd, nodata=nd if nd is not None else 0) as vrt:
                    arr = vrt.read(1, out_dtype=dtype)
                    valid = vrt.read_masks(1) > 0
            arr = arr.astype("float32")
            arr[~valid] = np.nan
            return arr
        except Exception:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
