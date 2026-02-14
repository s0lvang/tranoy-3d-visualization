from config import Config, tranoy_example
from dtm import fetch_dtm_raster, fetch_point_elevation
from horizon import compute_horizon_profile, compute_obstruction
from osm import fetch_osm_buildings, fetch_osm_roads
from viz import (
    build_house_mesh,
    build_osm_buildings_mesh,
    build_osm_roads_mesh,
    build_terrain_mesh,
    plot_horizon_profiles,
    show_3d_scene,
)


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


def run(cfg: Config | None = None) -> None:
    cfg = cfg or tranoy_example()
    bbox = _bbox_from_config(cfg)

    dtm, transform = fetch_dtm_raster(bbox, cfg.dtm_resolution)
    [viewpoint_terrain_z] = fetch_point_elevation([cfg.viewpoint], cfg.koordsys)
    eye_z = viewpoint_terrain_z + cfg.eye_height
    viewpoint_xyz = (cfg.viewpoint[0], cfg.viewpoint[1], eye_z)

    profile_without = compute_horizon_profile(
        dtm, transform, viewpoint_xyz, cfg.azimuth_step, cfg.analysis_radius
    )
    profile_with = compute_horizon_profile(
        dtm,
        transform,
        viewpoint_xyz,
        cfg.azimuth_step,
        cfg.analysis_radius,
        house_polygon=cfg.house_polygon,
        house_base=cfg.house_base_elevation,
        house_height=cfg.house_height,
    )

    obst = compute_obstruction(profile_without, profile_with, cfg.azimuth_step)
    print(f"Max horizon angle increase: {obst['max_delta_deg']:.2f}°")
    print(f"Mean horizon angle increase: {obst['mean_delta_deg']:.2f}°")
    print(f"Approximate blocked solid angle: {obst['blocked_solid_angle_sr']:.6f} sr")

    terrain_mesh = build_terrain_mesh(dtm, transform)
    house_mesh = build_house_mesh(
        cfg.house_polygon, cfg.house_base_elevation, cfg.house_height
    )
    buildings = fetch_osm_buildings(bbox)
    roads = fetch_osm_roads(bbox)
    osm_buildings_mesh = build_osm_buildings_mesh(buildings, dtm, transform)
    osm_roads_mesh = build_osm_roads_mesh(roads, dtm, transform)

    show_3d_scene(
        terrain_mesh,
        house_mesh,
        viewpoint_xyz,
        osm_buildings_mesh=osm_buildings_mesh,
        osm_roads_mesh=osm_roads_mesh,
    )
    plot_horizon_profiles(profile_without, profile_with)


if __name__ == "__main__":
    run()
