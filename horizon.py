import math
from typing import Any

import numpy as np
import scipy.ndimage
from shapely.geometry import LineString, Polygon


def _sample_terrain(
    dtm: np.ndarray,
    transform: Any,
    x: float,
    y: float,
) -> float:
    col, row = ~transform * (x, y)
    if row < -0.5 or row >= dtm.shape[0] - 0.5 or col < -0.5 or col >= dtm.shape[1] - 0.5:
        return np.nan
    return float(scipy.ndimage.map_coordinates(dtm, [[row], [col]], order=1, mode="constant", cval=np.nan)[0])


def _ray_intersects_house(
    viewpoint_x: float,
    viewpoint_y: float,
    azimuth_deg: float,
    house_poly: Polygon,
) -> float | None:
    azimuth_rad = math.radians(azimuth_deg)
    dx = math.sin(azimuth_rad)
    dy = math.cos(azimuth_rad)
    far_x = viewpoint_x + 100000 * dx
    far_y = viewpoint_y + 100000 * dy
    ray = LineString([(viewpoint_x, viewpoint_y), (far_x, far_y)])
    inter = house_poly.exterior.intersection(ray)
    if inter.is_empty:
        return None
    pts = []
    if hasattr(inter, "geoms"):
        for g in inter.geoms:
            pts.append((g.x, g.y))
    elif hasattr(inter, "coords"):
        pts = list(inter.coords)
    else:
        pts = [(inter.x, inter.y)]
    if not pts:
        return None
    closest = min(pts, key=lambda p: (p[0] - viewpoint_x) ** 2 + (p[1] - viewpoint_y) ** 2)
    return math.sqrt((closest[0] - viewpoint_x) ** 2 + (closest[1] - viewpoint_y) ** 2)


def compute_horizon_profile(
    dtm: np.ndarray,
    transform: Any,
    viewpoint_xyz: tuple[float, float, float],
    azimuth_step: float,
    max_distance: float,
    house_polygon: list[tuple[float, float]] | None = None,
    house_base: float | None = None,
    house_height: float | None = None,
    sample_step: float = 1.0,
) -> np.ndarray:
    vx, vy, vz = viewpoint_xyz
    house_poly = Polygon(house_polygon) if house_polygon and house_base is not None and house_height is not None else None
    house_top = (house_base or 0) + (house_height or 0) if house_poly else None

    azimuths = np.arange(0, 360, azimuth_step)
    result = np.zeros((len(azimuths), 2))
    result[:, 0] = azimuths

    for i, az in enumerate(azimuths):
        max_angle = -90.0
        az_rad = math.radians(az)
        dx = math.sin(az_rad)
        dy = math.cos(az_rad)

        if house_poly is not None and house_top is not None:
            dist_to_house = _ray_intersects_house(vx, vy, az, house_poly)
            if dist_to_house is not None and dist_to_house < max_distance:
                dz = house_top - vz
                angle = math.degrees(math.atan2(dz, dist_to_house))
                max_angle = max(max_angle, angle)

        d = sample_step
        while d <= max_distance:
            x = vx + d * dx
            y = vy + d * dy
            z = _sample_terrain(dtm, transform, x, y)
            if not np.isnan(z):
                angle = math.degrees(math.atan2(z - vz, d))
                max_angle = max(max_angle, angle)
            d += sample_step

        result[i, 1] = max_angle

    return result


def compute_obstruction(
    profile_without: np.ndarray,
    profile_with: np.ndarray,
    azimuth_step_deg: float,
) -> dict[str, Any]:
    delta = np.maximum(0, profile_with[:, 1] - profile_without[:, 1])
    solid_angle = (np.pi / 180) ** 2 * np.sum(delta) * azimuth_step_deg
    return {
        "delta_per_azimuth": delta,
        "max_delta_deg": float(np.max(delta)),
        "mean_delta_deg": float(np.mean(delta)),
        "blocked_solid_angle_sr": float(solid_angle),
    }
