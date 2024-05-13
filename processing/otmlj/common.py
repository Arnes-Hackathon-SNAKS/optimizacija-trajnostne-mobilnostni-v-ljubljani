from dataclasses import dataclass


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class LatitudeLongitude:
    latitude: float
    longitude: float

    def serialize(self) -> tuple[float, float]:
        return self.latitude, self.longitude
