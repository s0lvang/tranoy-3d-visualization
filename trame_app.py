import asyncio
import sys

from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3, vtk

import pyvista as pv
from pyvista.trame.ui import plotter_ui

from config import Config, tranoy_example
from dtm import fetch_dtm_raster, fetch_point_elevation
from osm import fetch_osm_buildings, fetch_osm_roads
from viz import (
    build_house_mesh,
    build_osm_buildings_mesh,
    build_osm_roads_mesh,
    build_terrain_mesh,
)

def _ensure_event_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_ensure_event_loop()


def create_plotter(cfg: Config):
    bbox_data = _bbox_from_config(cfg)
    
    dtm, transform = fetch_dtm_raster(bbox_data, cfg.dtm_resolution)
    [viewpoint_terrain_z] = fetch_point_elevation([cfg.viewpoint], cfg.koordsys)
    eye_z = viewpoint_terrain_z + cfg.eye_height
    viewpoint_xyz = (cfg.viewpoint[0], cfg.viewpoint[1], eye_z)
    
    terrain_mesh = build_terrain_mesh(dtm, transform)
    terrain_poly = terrain_mesh.extract_surface().triangulate().decimate(0.5)
    house_mesh = build_house_mesh(
        cfg.house_polygon, cfg.house_base_elevation, cfg.house_height
    )
    buildings = fetch_osm_buildings(bbox_data)
    roads = fetch_osm_roads(bbox_data)
    osm_buildings_mesh = build_osm_buildings_mesh(buildings, dtm, transform)
    osm_roads_mesh = build_osm_roads_mesh(roads, dtm, transform)
    
    pl = pv.Plotter()
    pl.add_mesh(
        terrain_poly,
        scalars=terrain_poly.points[:, 2],
        cmap="terrain",
        show_scalar_bar=True,
        name="terrain"
    )
    if osm_buildings_mesh is not None:
        pl.add_mesh(osm_buildings_mesh, color="gray", opacity=0.8, name="osm_buildings")
    if osm_roads_mesh is not None:
        pl.add_mesh(osm_roads_mesh, color="darkgray", name="osm_roads")
    if house_mesh is not None:
        pl.add_mesh(house_mesh, color="tan", opacity=0.9, name="house")
    
    vx, vy, vz = cfg.center_xyz
    pl.add_mesh(pv.Sphere(radius=2, center=(vx, vy, vz)), color="red", name="viewpoint")
    pl.add_axes()
    pl.camera.position = (vx + 100, vy, vz + 100)
    pl.camera.focal_point = (vx, vy, vz)
    pl.camera.up = (0, 0, 1)
    pl.enable_terrain_style(mouse_wheel_zooms=True, shift_pans=True)
    
    return pl


def _bbox_from_config(cfg: Config) -> tuple[float, float, float, float]:
    vx, vy = cfg.viewpoint
    r = cfg.analysis_radius
    xs = [vx] + [p[0] for p in cfg.house_polygon]
    ys = [vy] + [p[1] for p in cfg.house_polygon]
    xmin = min(xs) - r
    xmax = max(xs) + r
    ymin = min(ys) - r
    ymax = max(ys) + r
    return (xmin, ymin, xmax, ymax)


def main():
    server = get_server(client_type="vue3")
    state, ctrl = server.state, server.controller
    
    cfg = tranoy_example()
    
    state.trame__title = "Tranøy Map 3D Viewer"
    
    print("Loading terrain data...")
    pl = create_plotter(cfg)
    
    with SinglePageLayout(server) as layout:
        layout.title.set_text("Tranøy Map 3D Viewer")
        
        with layout.toolbar:
            vuetify3.VSpacer()
            vuetify3.VBtn("Reset Camera", click=ctrl.view_reset_camera)
        
        with layout.content:
            with vuetify3.VContainer(fluid=True, classes="pa-0 fill-height"):
                view = plotter_ui(pl)
                ctrl.view_reset_camera = view.reset_camera
    
    server.start(
        port=7860,
        host="0.0.0.0",
        open_browser=False,
    )


if __name__ == "__main__":
    main()
