import json
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from otmlj.avtobusi import parse_daily_bus_stop_entries_from_raw_csv_data, parse_bus_stops_from_raw_csv_data, BusStop, \
    BusArrival, BusStopWithStatistics, merge_arrivals_into_corresponding_bus_stops
from otmlj.green_zone import GreenZone, parse_green_zone_GeoJSON_polygon
from otmlj.kolesa import parse_bike_lanes_from_WGS84_GeoJSON, BikeLaneMultiLine
from otmlj.p_plus_r import PPlusR, EXISTING_P_PLUS_R_STATIONS, PROPOSED_NEW_P_PLUS_R_STATIONS

SCRIPT_DIRECTORY_PATH: Path = Path(__file__).parent
RAW_DATA_DIRECTORY_PATH: Path = SCRIPT_DIRECTORY_PATH / "raw-data"
OUTPUT_DATA_DIRECTORY_PATH: Path = SCRIPT_DIRECTORY_PATH / "output-data"

LPP_BUS_FEED_DATA_ZIP_PATH: Path = RAW_DATA_DIRECTORY_PATH / "lpp-avtobus" / "LPP_2024-05-09_feed.zip"
BIKE_LANES_DATA_ZIP_PATH: Path = RAW_DATA_DIRECTORY_PATH / "lj-kolesarji" / "MOL_KolesarskePoti_wgs84.json"
GREEN_ZONE_GEOJSON_POLYGON_PATH: Path = RAW_DATA_DIRECTORY_PATH / "green-zone" / "green-zone-polygon.json"


if not OUTPUT_DATA_DIRECTORY_PATH.is_dir():
    OUTPUT_DATA_DIRECTORY_PATH.mkdir(parents=True)

if not LPP_BUS_FEED_DATA_ZIP_PATH.exists():
    raise RuntimeError(f"Missing data file: {LPP_BUS_FEED_DATA_ZIP_PATH}")
if not BIKE_LANES_DATA_ZIP_PATH.exists():
    raise RuntimeError(f"Missing data file: {BIKE_LANES_DATA_ZIP_PATH}")


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class BusVisualizationData:
    stops_with_arrivals: list[BusStopWithStatistics]

    def serialize(self) -> dict:
        return {
            "stops_with_arrivals": [
                stop.serialize_as_dict()
                for stop in self.stops_with_arrivals
            ],
        }


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class BikeVisualizationData:
    bike_lanes: list[BikeLaneMultiLine]
    total_length_in_metres: float

    def serialize(self) -> dict:
        return {
            "bike_lanes": [
                lane.serialize_as_dict()
                for lane in self.bike_lanes
            ],
            "total_length_in_metres": self.total_length_in_metres
        }


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class PPlusRVisualizationData:
    existing: list[PPlusR]
    proposed: list[PPlusR]

    def serialize(self) -> dict:
        return {
            "existing": [
                existing.serialize()
                for existing in self.existing
            ],
            "proposed": [
                proposed.serialize()
                for proposed in self.proposed
            ]
        }


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class GreenZoneVisualizationData:
    green_zone: GreenZone

    def serialize(self) -> dict:
        return {
            "green_zone": self.green_zone.serialize()
        }



@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class VisualizationData:
    bus: BusVisualizationData
    bike: BikeVisualizationData
    p_plus_r: PPlusRVisualizationData
    green_zone: GreenZoneVisualizationData

    def serialize_as_dict(self) -> dict:
        return {
            "bus": self.bus.serialize(),
            "bike": self.bike.serialize(),
            "p_plus_r": self.p_plus_r.serialize(),
            "green_zone": self.green_zone.serialize()
        }




def process_bus_data() -> tuple[list[BusStop], list[BusArrival]]:
    zip_data = zipfile.ZipFile(LPP_BUS_FEED_DATA_ZIP_PATH, mode="r")


    raw_stops_csv_data = zip_data.open("stops.txt", mode="r").read().decode("utf8")
    stops = parse_bus_stops_from_raw_csv_data(raw_stops_csv_data)

    raw_stop_times_data = zip_data.open("stop_times.txt").read().decode("utf8")
    daily_stop_entries = parse_daily_bus_stop_entries_from_raw_csv_data(raw_stop_times_data)


    # print("\n".join([str(s) for s in stops[:50]]))
    # print(len(stops))
    #
    # print("\n".join([str(s) for s in daily_stop_entries[:50]]))
    # print(len(daily_stop_entries))

    return stops, daily_stop_entries


def process_bike_data() -> tuple[list[BikeLaneMultiLine], float]:
    with BIKE_LANES_DATA_ZIP_PATH.open("r", encoding="utf8") as bike_lane_file:
        bike_lane_data = bike_lane_file.read()

    (bike_lanes, total_lane_length_metres) = parse_bike_lanes_from_WGS84_GeoJSON(bike_lane_data)

    # print("\n".join([str(line_segment) for line_segment in bike_lanes[:50]]))
    # print(len(bike_lanes))
    #
    # print(f"Total bike lane length: {round(total_lane_length_metres, 1)} metres")

    return bike_lanes, total_lane_length_metres


def process_green_zone() -> GreenZone:
    with GREEN_ZONE_GEOJSON_POLYGON_PATH.open("r", encoding="utf8") as green_zone_file:
        geojson_string = green_zone_file.read()

    geojson_data = json.loads(geojson_string)

    return parse_green_zone_GeoJSON_polygon(geojson_data)



def export_processed_data_to_file_for_visualization(
    bus_stops_with_arrivals: list[BusStopWithStatistics],
    bike_lanes: list[BikeLaneMultiLine],
    total_bike_lane_length_metres: float,
    green_zone: GreenZone
):
    full_data_structure = VisualizationData(
        bus=BusVisualizationData(
            stops_with_arrivals=bus_stops_with_arrivals,
        ),
        bike=BikeVisualizationData(
            bike_lanes=bike_lanes,
            total_length_in_metres=total_bike_lane_length_metres,
        ),
        p_plus_r=PPlusRVisualizationData(
            existing=EXISTING_P_PLUS_R_STATIONS,
            proposed=PROPOSED_NEW_P_PLUS_R_STATIONS
        ),
        green_zone=GreenZoneVisualizationData(
            green_zone=green_zone
        )
    )

    formatted_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file_path = OUTPUT_DATA_DIRECTORY_PATH / f"otmlj-data_{formatted_datetime}.json"

    with output_file_path.open("w", encoding="utf8") as output_file:
        json.dump(
            full_data_structure.serialize_as_dict(),
            output_file,
            indent=2,
            ensure_ascii=False
        )


def main():
    time_bus_data_start = time.time()
    bus_stops, bus_daily_timed_stops = process_bus_data()

    time_bus_arrival_merge_start = time.time()
    bus_stops_with_arrivals = merge_arrivals_into_corresponding_bus_stops(bus_stops, bus_daily_timed_stops)

    time_bike_data_start = time.time()
    bike_lanes, total_bike_lane_length_metres = process_bike_data()

    time_green_zone_start = time.time()
    green_zone = process_green_zone()

    time_export_start = time.time()
    export_processed_data_to_file_for_visualization(
        bus_stops_with_arrivals,
        bike_lanes,
        total_bike_lane_length_metres,
        green_zone
    )

    time_finished = time.time()


    print("Finished!")
    print(
        "Timings:\n"
        "  Bus\n"
        f"    data loading took {round(time_bus_arrival_merge_start - time_bus_data_start, 1)} seconds\n"
        f"    processing took {round(time_bike_data_start - time_bus_arrival_merge_start, 1)} seconds\n"
        "  Green Zone\n"
        f"    processing took {round(time_export_start - time_green_zone_start, 1)} seconds"
        "  Bike\n"
        f"    data loading took {round(time_green_zone_start - time_bike_data_start, 1)} seconds\n"
        "  Export\n"
        f"    exporting took {round(time_finished - time_export_start, 1)} seconds\n"
        "\n"
        f"Total time: {round(time_finished - time_bus_data_start, 1)} seconds"
    )



if __name__ == '__main__':
    main()
