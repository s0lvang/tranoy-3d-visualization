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
    easting =  527372.01
    northing = 7563449.49
    return Config(
        viewpoint=(easting, northing),
        house_polygon=[
            (easting + 50, northing - 30),
            (easting + 50, northing - 50),
            (easting + 30, northing - 50),
            (easting + 30, northing - 30),
        ],
        house_base_elevation=10.0,
        house_height=6.0,
    )
