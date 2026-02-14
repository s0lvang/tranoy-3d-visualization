from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from rasterio.transform import Affine

from horizon import sample_terrain


def build_terrain_mesh(dtm: np.ndarray, transform: Any) -> pv.StructuredGrid:
    rows, cols = dtm.shape
    col_idx = np.arange(cols, dtype=np.float64)
    row_idx = np.arange(rows, dtype=np.float64)
    col_mesh, row_mesh = np.meshgrid(col_idx, row_idx, indexing="xy")
    if isinstance(transform, Affine):
        xx = transform.c + transform.a * col_mesh + transform.b * row_mesh
        yy = transform.f + transform.d * col_mesh + transform.e * row_mesh
    else:
        xx, yy = transform * (col_mesh, row_mesh)
    zz = np.where(np.isnan(dtm), 0.0, dtm).astype(np.float64)
    return pv.StructuredGrid(xx, yy, zz)


def build_osm_buildings_mesh(
    buildings: list[dict],
    dtm: np.ndarray,
    transform: Any,
) -> pv.PolyData | None:
    if not buildings:
        return None
    meshes = []
    for b in buildings:
        poly = b["polygon"]
        if len(poly) < 3:
            continue
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        base_z = sample_terrain(dtm, transform, cx, cy)
        if np.isnan(base_z):
            base_z = 0.0
        mesh = build_house_mesh(poly, base_z, b["height"])
        meshes.append(mesh)
    return pv.merge(meshes) if meshes else None


def build_osm_roads_mesh(
    roads: list[dict],
    dtm: np.ndarray,
    transform: Any,
    tube_radius: float = 1.0,
    height_offset: float = 0.5,
) -> pv.PolyData | None:
    if not roads:
        return None
    meshes = []
    for r in roads:
        coords = r["coords"]
        if len(coords) < 2:
            continue
        pts = []
        for x, y in coords:
            z = sample_terrain(dtm, transform, x, y)
            z = height_offset if np.isnan(z) else z + height_offset
            pts.append([x, y, z])
        arr = np.array(pts, dtype=np.float64)
        line = pv.lines_from_points(arr)
        tube = line.tube(radius=tube_radius)
        meshes.append(tube)
    return pv.merge(meshes) if meshes else None


def build_house_mesh(
    polygon: list[tuple[float, float]],
    base_elevation: float,
    height: float,
) -> pv.PolyData:
    pts = np.array([[x, y, base_elevation] for x, y in polygon], dtype=np.float64)
    n = len(pts)
    faces = np.concatenate([[n], np.arange(n)])
    face = pv.PolyData(pts, faces)
    extruded = face.extrude((0, 0, height), capping=True)
    return extruded


def show_3d_scene(
    terrain_mesh: pv.StructuredGrid,
    house_mesh: pv.PolyData | None,
    center_xyz: tuple[float, float, float],
    osm_buildings_mesh: pv.PolyData | None = None,
    osm_roads_mesh: pv.PolyData | None = None,
) -> None:
    pl = pv.Plotter()
    pl.add_mesh(terrain_mesh, scalars=terrain_mesh.points[:, 2], cmap="terrain", show_scalar_bar=True)
    if osm_buildings_mesh is not None:
        pl.add_mesh(osm_buildings_mesh, color="gray", opacity=0.8)
    if osm_roads_mesh is not None:
        pl.add_mesh(osm_roads_mesh, color="darkgray")
    if house_mesh is not None:
        pl.add_mesh(house_mesh, color="tan", opacity=0.9)
    vx, vy, vz = center_xyz
    pl.add_mesh(pv.Sphere(radius=2, center=(vx, vy, vz)), color="red")
    pl.add_axes()
    pl.enable_terrain_style()
    pl.camera.position = (vx + 100, vy, vz + 100)
    pl.camera.focal_point = (vx, vy, vz)
    pl.camera.up = (0, 0, 1)
    pl.show()


def plot_horizon_profiles(
    profile_without: np.ndarray,
    profile_with: np.ndarray,
) -> None:
    azimuths = np.radians(profile_without[:, 0])
    elev_without = profile_without[:, 1]
    elev_with = profile_with[:, 1]
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.plot(azimuths, elev_without, label="Terrain only", color="green", linewidth=1)
    ax.plot(azimuths, elev_with, label="With house", color="brown", linewidth=1)
    delta = np.maximum(0, elev_with - elev_without)
    ax.fill_between(azimuths, elev_without, elev_with, where=delta > 0, alpha=0.3, color="brown")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.legend(loc="upper right")
    ax.set_title("Horizon profile (elevation angle vs azimuth)")
    plt.tight_layout()
    plt.show()
