from dataclasses import dataclass
from typing import Optional

from otmlj.common import LatitudeLongitude


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class TimeOfDay:
    """
    Some hour and minute of a day.
    """

    hour: int
    minute: int

    @classmethod
    def from_colon_separated_hms(cls, raw_colon_separated_hms: str):
        hour, minute, _ = raw_colon_separated_hms.split(":", maxsplit=3)
        hour = int(hour) - 1
        minute = int(minute)

        if hour < 0 or hour > 23:
            raise RuntimeError("Invalid H:M:S string.")
        if minute < 0 or minute > 60:
            raise RuntimeError("Invalid H:M:S string.")

        return TimeOfDay(hour, minute)

    def serialize(self) -> tuple[int, int]:
        return self.hour, self.minute


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class BusStop:
    id: str
    code: int
    name: str
    location: LatitudeLongitude

    def serialize_as_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "location": self.location.serialize()
        }


def parse_bus_stops_from_raw_csv_data(
    raw_csv_data: str
) -> list[BusStop]:
    # Extract lines, with the first one containing column names
    # and subsequent ones containing data.

    lines = raw_csv_data.splitlines(keepends=False)


    column_names = lines[0].split(",")

    def get_column_index_by_name(name: str) -> Optional[int]:
        for index, column_name in enumerate(column_names):
            if column_name == name:
                return index

        return None

    data_rows: list[list[str]] = []
    for unparsed_data_line in lines[1:]:
        data_row = unparsed_data_line.split(",")

        if len(data_row) != len(column_names):
            raise RuntimeError(f"data does not have all the columns: {data_row}")

        data_rows.append(data_row)


    # Parse actual `BusStop`s out of raw data lines.
    parsed_stops: list[BusStop] = []

    stop_id_column_index = get_column_index_by_name("stop_id")
    stop_code_column_index = get_column_index_by_name("stop_code")
    stop_name_column_index = get_column_index_by_name("stop_name")
    stop_lat_column_index = get_column_index_by_name("stop_lat")
    stop_lon_column_index = get_column_index_by_name("stop_lon")

    if None in [
        stop_id_column_index, stop_code_column_index, stop_name_column_index,
        stop_lat_column_index, stop_lon_column_index
    ]:
        raise RuntimeError(
            "Invalid input data: expected stop_id, stop_code, \
            stop_name, stop_lat and stop_lon columns."
        )

    for split_data_line in data_rows:
        bus_stop_id = str(split_data_line[stop_id_column_index])
        bus_stop_code = int(split_data_line[stop_code_column_index])
        bus_stop_name = str(split_data_line[stop_name_column_index])
        bus_stop_lat = float(split_data_line[stop_lat_column_index])
        bus_stop_lon = float(split_data_line[stop_lon_column_index])

        bus_stop = BusStop(
            id=bus_stop_id,
            code=bus_stop_code,
            name=bus_stop_name,
            location=LatitudeLongitude(
                latitude=bus_stop_lat,
                longitude=bus_stop_lon
            )
        )

        parsed_stops.append(bus_stop)

    return parsed_stops



@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class BusArrival:
    trip_id: str
    arrival_time: TimeOfDay
    departure_time: TimeOfDay
    stop_id: str
    stop_sequence: int

    def serialize(self) -> dict:
        return {
            "trip_id": self.trip_id,
            "arrival_time": self.arrival_time.serialize(),
            "departure_time": self.departure_time.serialize(),
            "stop_id": self.stop_id,
            "stop_sequence": self.stop_sequence
        }

    def serialize_bare(self) -> tuple[int, int]:
        return self.arrival_time.serialize()


def parse_daily_bus_stop_entries_from_raw_csv_data(
    raw_csv_data: str
) -> list[BusArrival]:
    # Extract lines, with the first one containing column names
    # and subsequent ones containing data.
    lines = raw_csv_data.splitlines(keepends=False)


    column_names = lines[0].split(",")

    def get_column_index_by_name(name: str) -> Optional[int]:
        for index, column_name in enumerate(column_names):
            if column_name == name:
                return index

        return None


    data_rows: list[list[str]] = []
    for unparsed_data_line in lines[1:]:
        data_row = unparsed_data_line.split(",")

        if len(data_row) != len(column_names):
            raise RuntimeError(f"data does not have all the columns: {data_row}")

        data_rows.append(data_row)



    parsed_stop_times: list[BusArrival] = []

    trip_id_column_index = get_column_index_by_name("trip_id")
    arrival_time_column_index = get_column_index_by_name("arrival_time")
    departure_time_column_index = get_column_index_by_name("departure_time")
    stop_id_column_index = get_column_index_by_name("stop_id")
    stop_sequence_column_index = get_column_index_by_name("stop_sequence")

    if None in [
        trip_id_column_index, arrival_time_column_index, departure_time_column_index,
        stop_id_column_index, stop_sequence_column_index
    ]:
        raise RuntimeError(
            "Invalid input data: expected trip_id, arrival_time, \
            departure_time, stop_id and stop_sequence columns."
        )


    for split_data_line in data_rows:
        trip_id = str(split_data_line[trip_id_column_index])

        # This ignores trips that are not on 2024-05-08.
        if "ddfb999e-c766-48e1-a5c5-e97e5b09e19c" not in trip_id:
            continue

        arrival_time_raw = str(split_data_line[arrival_time_column_index])
        departure_time_raw = str(split_data_line[departure_time_column_index])
        stop_id = str(split_data_line[stop_id_column_index])
        stop_sequence = int(split_data_line[stop_sequence_column_index])

        arrival_time = TimeOfDay.from_colon_separated_hms(arrival_time_raw)
        departure_time = TimeOfDay.from_colon_separated_hms(departure_time_raw)


        daily_stop_entry = BusArrival(
            trip_id=trip_id,
            arrival_time=arrival_time,
            departure_time=departure_time,
            stop_id=stop_id,
            stop_sequence=stop_sequence,
        )

        parsed_stop_times.append(daily_stop_entry)


    return parsed_stop_times


class ArrivalsPerHourOfDay:
    # Length is 24, first item represents arrivals
    # between 00:00 and 00:59 in the morning, and so on.
    arrivals: list[int]

    def __init__(self):
        self.arrivals = [0 for _ in range(24)]

    def increment_by_one(self, time_of_day: TimeOfDay):
        self.arrivals[time_of_day.hour - 1] += 1

    def serialize(self) -> list[int]:
        return self.arrivals


@dataclass(init=True, repr=True, eq=True, frozen=False, slots=True)
class BusStopWithStatistics:
    id: str
    code: int
    name: str
    location: LatitudeLongitude
    arrivals_per_hour: ArrivalsPerHourOfDay

    def serialize_as_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "location": self.location.serialize(),
            "arrivals_per_hour": self.arrivals_per_hour.serialize()
        }



def merge_arrivals_into_corresponding_bus_stops(
    bus_stops: list[BusStop],
    arrivals: list[BusArrival]
) -> list[BusStopWithStatistics]:
    bus_stops_by_id: dict[str, BusStopWithStatistics] = {
        stop.id: BusStopWithStatistics(
            id=stop.id,
            code=stop.code,
            name=stop.name,
            location=stop.location,
            arrivals_per_hour=ArrivalsPerHourOfDay()
        )
        for stop in bus_stops
    }

    for arrival in arrivals:
        corresponding_bus_stop = bus_stops_by_id[arrival.stop_id]
        corresponding_bus_stop.arrivals_per_hour.increment_by_one(arrival.arrival_time)

    return [
        stop_with_arrival
        for stop_with_arrival in bus_stops_by_id.values()
    ]
