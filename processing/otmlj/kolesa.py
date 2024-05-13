import json
from dataclasses import dataclass

from otmlj.common import LatitudeLongitude


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class BikeLaneMultiLine:
    # Coordinate order: latitude, then longitude.
    line_points: list[LatitudeLongitude]

    def serialize_as_dict(self) -> dict:
        return {
            "line_points": [
                point.serialize()
                for point in self.line_points
            ]
        }



def parse_bike_lanes_from_WGS84_GeoJSON(
    raw_json_data: str
) -> tuple[list[BikeLaneMultiLine], float]:
    """
    :return: list containing all bike lanes, and the sum of their lengths in metres
    """

    json_data: dict = json.loads(raw_json_data)

    if json_data["type"] != "FeatureCollection":
        raise RuntimeError("Expected the GeoJSON to be of type FeatureCollection.")

    features: dict = json_data["features"]


    parsed_bike_lanes: list[BikeLaneMultiLine] = []
    total_length_in_metres: float = 0

    for raw_feature in features:
        if raw_feature["type"] != "Feature":
            raise RuntimeError("Expected the feature to be of type Feature.")

        raw_geometry = raw_feature["geometry"]

        if raw_geometry["type"] == "LineString":
            raw_coordinates_lat_lng: list[LatitudeLongitude] = []
            for raw_coordinate_pair in raw_geometry["coordinates"]:
                longitude, latitude = list(raw_coordinate_pair)
                raw_coordinates_lat_lng.append(
                    LatitudeLongitude(
                        latitude=float(latitude),
                        longitude=float(longitude)
                    )
                )

            bike_lane_segment = BikeLaneMultiLine(line_points=raw_coordinates_lat_lng)
            parsed_bike_lanes.append(bike_lane_segment)
        elif raw_geometry["type"] == "MultiLineString":
            for line_coordinate_list in raw_geometry["coordinates"]:
                raw_coordinates_lat_lng: list[LatitudeLongitude] = []
                for raw_coordinate_pair in line_coordinate_list:
                    longitude, latitude = list(raw_coordinate_pair)
                    raw_coordinates_lat_lng.append(
                        LatitudeLongitude(
                            latitude=float(latitude),
                            longitude=float(longitude)
                        )
                    )

                bike_lane_segment = BikeLaneMultiLine(line_points=raw_coordinates_lat_lng)
                parsed_bike_lanes.append(bike_lane_segment)
        else:
            raise RuntimeError("Expected geometry type LineString or MultiLineString.")


        shape_length_in_metres = float(raw_feature["properties"]["SHAPE_Leng"])
        total_length_in_metres += shape_length_in_metres


    return parsed_bike_lanes, total_length_in_metres
