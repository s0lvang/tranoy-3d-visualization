from dataclasses import dataclass


@dataclass
class Config:
    viewpoint: tuple[float, float]
    house_polygon: list[tuple[float, float]]
    center_xyz: tuple[float, float, float]
    house_base_elevation: float
    house_height: float
    eye_height: float = 1.6
    analysis_radius: float = 50
    azimuth_step: float = 0.5
    dtm_resolution: float = 1.0
    koordsys: int = 25833


def tranoy_example() -> Config:
    easting = 527304.36 
    northing = 7563388.55 

    easting = 527304.36 
    northing = 7563388.55 

    house_px = [
    (294, 302),
    (328, 275),
    (437, 408),
    (408, 429),
    (396, 413),
    (368, 435),
    (299, 348),
    (318, 332),
    ]

    # Image dimensions:
    img_w, img_h = 723, 732
    dpi = 1
    scale = 0.155  # 500 / dpi * 25.4  # mm to meters, or derive from grid spacing
    # simpler: if grid spacing of 100 units = N pixels, then meters_per_pixel = (100 * 0.5) / N
    center_xyz = ( 527338.39, 7563433.25 , 21.0 + 5.5 / 2)
    house_polygon = [
    (easting + px * scale, northing + (img_h - py) * scale)
    for px, py in house_px
    ]

    return Config(
        viewpoint=(easting, northing),
        house_polygon=house_polygon,
        center_xyz=center_xyz,
        house_base_elevation=21.0,
        house_height=5.5,
    )
