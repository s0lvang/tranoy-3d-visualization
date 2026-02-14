from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from rasterio.transform import Affine


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
    viewpoint_xyz: tuple[float, float, float],
) -> None:
    pl = pv.Plotter()
    pl.add_mesh(terrain_mesh, scalars=terrain_mesh.points[:, 2], cmap="terrain", show_scalar_bar=True)
    if house_mesh is not None:
        pl.add_mesh(house_mesh, color="tan", opacity=0.9)
    vx, vy, vz = viewpoint_xyz
    pl.add_mesh(pv.Sphere(radius=2, center=(vx, vy, vz)), color="red")
    pl.add_axes()
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
