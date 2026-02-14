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
    return Config(
        viewpoint=(easting, northing),
        house_polygon=[
            (easting + 30.0, northing + 25.0),
            (easting + 37.5, northing + 25.0),
            (easting + 38.5, northing + 27.5),
            (easting + 44.0, northing + 36.0),
            (easting + 42.0, northing + 37.0),
            (easting + 32.5, northing + 38.5),
            (easting + 31.0, northing + 37.0),
            (easting + 30.0, northing + 30.0),
        ],
        house_base_elevation=22.5,
        house_height=6.0,
    )
