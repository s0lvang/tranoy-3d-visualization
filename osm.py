import re
from typing import Any

import pyproj
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
WGS84 = pyproj.CRS.from_epsg(4326)
UTM33 = pyproj.CRS.from_epsg(25833)
WGS84_TO_UTM = pyproj.Transformer.from_crs(WGS84, UTM33, always_xy=True)
UTM_TO_WGS84 = pyproj.Transformer.from_crs(UTM33, WGS84, always_xy=True)


def _bbox_25833_to_wgs84(bbox: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    xmin, ymin, xmax, ymax = bbox
    sw_lon, sw_lat = UTM_TO_WGS84.transform(xmin, ymin)
    ne_lon, ne_lat = UTM_TO_WGS84.transform(xmax, ymax)
    return (sw_lat, sw_lon, ne_lat, ne_lon)


def _parse_height(tags: dict[str, Any]) -> float:
    if "height" in tags:
        m = re.match(r"^([\d.]+)\s*m?$", str(tags["height"]).strip().lower())
        if m:
            return float(m.group(1))
    if "building:levels" in tags:
        try:
            return float(tags["building:levels"]) * 3.0
        except (ValueError, TypeError):
            pass
    return 5.0


def _lonlat_to_utm(geom: list[dict]) -> list[tuple[float, float]]:
    return [WGS84_TO_UTM.transform(p["lon"], p["lat"])[:2] for p in geom]


def fetch_osm_buildings(bbox_25833: tuple[float, float, float, float]) -> list[dict]:
    south, west, north, east = _bbox_25833_to_wgs84(bbox_25833)
    query = f"""
    [out:json][timeout:60];
    (
      way["building"]({south},{west},{north},{east});
    );
    out geom;
    """
    r = requests.post(OVERPASS_URL, data={"data": query}, timeout=90)
    r.raise_for_status()
    data = r.json()
    result = []
    for el in data.get("elements", []):
        if el.get("type") != "way":
            continue
        geom = el.get("geometry")
        if not geom or len(geom) < 3:
            continue
        coords = _lonlat_to_utm(geom)
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        tags = el.get("tags", {})
        result.append({"polygon": coords, "height": _parse_height(tags)})
    return result


def fetch_osm_roads(bbox_25833: tuple[float, float, float, float]) -> list[dict]:
    south, west, north, east = _bbox_25833_to_wgs84(bbox_25833)
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"]({south},{west},{north},{east});
    );
    out geom;
    """
    r = requests.post(OVERPASS_URL, data={"data": query}, timeout=90)
    r.raise_for_status()
    data = r.json()
    result = []
    for el in data.get("elements", []):
        if el.get("type") != "way":
            continue
        geom = el.get("geometry")
        if not geom or len(geom) < 2:
            continue
        coords = _lonlat_to_utm(geom)
        tags = el.get("tags", {})
        result.append({"coords": coords, "highway": tags.get("highway", "unknown")})
    return result
