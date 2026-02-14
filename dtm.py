import json
from typing import Any

import numpy as np
import rasterio
import requests
from rasterio.transform import from_bounds

DTM_IMAGE_SERVER = "https://hoydedata.no/arcgis/rest/services/DTM/ImageServer/exportImage"
POINT_API = "https://ws.geonorge.no/hoydedata/v1/punkt"


def fetch_dtm_raster(
    bbox: tuple[float, float, float, float],
    resolution: float,
) -> tuple[np.ndarray, Any]:
    xmin, ymin, xmax, ymax = bbox
    width = int((xmax - xmin) / resolution)
    height = int((ymax - ymin) / resolution)
    width = max(1, min(width, 15000))
    height = max(1, min(height, 15000))

    params = {
        "bbox": f"{xmin},{ymin},{xmax},{ymax}",
        "bboxSR": 25833,
        "imageSR": 25833,
        "size": f"{width},{height}",
        "format": "tiff",
        "pixelType": "F32",
        "f": "image",
        "adjustAspectRatio": "false",
    }
    r = requests.get(DTM_IMAGE_SERVER, params=params, timeout=120)
    r.raise_for_status()

    with rasterio.MemoryFile(r.content) as mem:
        with mem.open() as src:
            data = src.read()
            transform = src.transform

    if data.ndim == 3:
        data = data[0]
    return data, transform


def fetch_point_elevation(
    points: list[tuple[float, float]],
    koordsys: int = 25833,
) -> list[float]:
    result: list[float] = []
    for i in range(0, len(points), 50):
        batch = points[i : i + 50]
        punkter = [[float(x), float(y)] for x, y in batch]
        params = {"koordsys": koordsys, "punkter": json.dumps(punkter)}
        r = requests.get(POINT_API, params=params, timeout=30)
        r.raise_for_status()
        js = r.json()
        for p in js["punkter"]:
            result.append(p["z"])
    return result
