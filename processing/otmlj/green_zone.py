from dataclasses import dataclass
from area import area as geo_json_area
from shapely import Polygon, Point

from otmlj.avtobusi import BusStopWithStatistics
from otmlj.common import LatitudeLongitude


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class GreenZone:
    polygon_bounds: list[LatitudeLongitude]
    area_in_square_metres: float
    total_arrivals_per_day_inside_zone: int

    def serialize(self) -> dict:
        return {
            "polygon_bounds": [
                polygon.serialize()
                for polygon in self.polygon_bounds
            ],
            "area_in_square_metres": self.area_in_square_metres,
            "total_arrivals_per_day_inside_zone": self.total_arrivals_per_day_inside_zone
        }


def parse_green_zone_GeoJSON_polygon(
    raw_geojson_data: dict,
    all_bus_stops: list[BusStopWithStatistics]
) -> GreenZone:
    if "type" not in raw_geojson_data:
        raise RuntimeError("Invalid GeoJSON data: field type missing")

    if raw_geojson_data["type"] != "FeatureCollection":
        raise RuntimeError("Invalid GeoJSON data: not a FeatureCollection")


    features = raw_geojson_data["features"]
    if len(features) > 1:
        raise RuntimeError("Unexpected green zone format: expected only one feature")

    feature_geometry = features[0]["geometry"]

    zone_area = geo_json_area(feature_geometry)

    feature_coordinates = feature_geometry["coordinates"][0]

    if not isinstance(feature_coordinates, list):
        raise RuntimeError(
            "Invalid GeoJSON data: features[0].geometry.coordinates should be a list"
        )


    zone_polygon_bounds: list[LatitudeLongitude] = []

    for coordinate_pair in feature_coordinates:
        if len(coordinate_pair) != 2:
            raise RuntimeError("Invalid GeoJSON data: expected lat,lng pairs")

        longitude, latitude = coordinate_pair

        latitude = float(latitude)
        longitude = float(longitude)

        zone_polygon_bounds.append(LatitudeLongitude(
            latitude=latitude,
            longitude=longitude
        ))


    # Precalculate how many arrivals happen per day inside the proposed zone
    total_arrivals_per_day_inside_zone: int = 0

    zone_polygon = Polygon([
        (point.latitude, point.longitude)
        for point in zone_polygon_bounds
    ])

    for bus_stop in all_bus_stops:
        bus_point = Point(bus_stop.location.latitude, bus_stop.location.longitude)

        if zone_polygon.contains(bus_point):
            total_arrivals_to_stop: int = sum(bus_stop.arrivals_per_hour.arrivals)
            total_arrivals_per_day_inside_zone += total_arrivals_to_stop


    return GreenZone(
        polygon_bounds=zone_polygon_bounds,
        area_in_square_metres=zone_area,
        total_arrivals_per_day_inside_zone=total_arrivals_per_day_inside_zone
    )
