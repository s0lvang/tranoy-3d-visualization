from dataclasses import dataclass


@dataclass
class Config:
    viewpoint: tuple[float, float]
    house_polygon: list[tuple[float, float]]
    house_base_elevation: float
    house_height: float
    eye_height: float = 1.6
    analysis_radius: float = 200
    azimuth_step: float = 0.5
    dtm_resolution: float = 1.0
    koordsys: int = 25833


def tranoy_example() -> Config:
    easting = 527304.36 
    northing = 7563388.55 
    house_px= [
    (291, 302),
    (329, 272),
    (436, 407),
    (410, 429),
    (395, 414),
    (369, 433),
    (304, 358),
    (310, 355),
    (304, 345),
    (316, 331),
    ]
    dpi = 1
    scale = 0.155  # 500 / dpi * 25.4  # mm to meters, or derive from grid spacing
    # simpler: if grid spacing of 100 units = N pixels, then meters_per_pixel = (100 * 0.5) / N
    img_h = 732

    house_polygon = [
    (easting + px * scale, northing + (img_h - py) * scale)
    for px, py in house_px
    ]

    return Config(
        viewpoint=(easting, northing),
        house_polygon=house_polygon,
        house_base_elevation=21.0,
        house_height=5.5,
    )
