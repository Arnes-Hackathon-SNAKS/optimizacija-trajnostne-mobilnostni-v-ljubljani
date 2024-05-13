from dataclasses import dataclass

from otmlj.common import LatitudeLongitude


@dataclass(init=True, repr=True, eq=True, frozen=True, slots=True)
class PPlusR:
    name: str
    location: LatitudeLongitude

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "location": self.location.serialize()
        }


EXISTING_P_PLUS_R_STATIONS: list[PPlusR] = [
    PPlusR(
        name="Stožice P+R",
        location=LatitudeLongitude(
            latitude=46.08193178070523,
            longitude=14.523173128250244
        )
    ),
    PPlusR(
        name="Dolgi most P+R",
        location=LatitudeLongitude(
            latitude=46.03644878723429,
            longitude=14.462492465882027
        )
    ),
    PPlusR(
        name="Fužine P+R",
        location=LatitudeLongitude(
            latitude=46.05216289561236,
            longitude=14.566035647181735
        )
    ),
    PPlusR(
        name="Ig-Banija P+R",
        location=LatitudeLongitude(
            latitude=45.95925901901162,
            longitude=14.527172648350264
        )
    ),
    PPlusR(
        name="P+R Središče Škofljica",
        location=LatitudeLongitude(
            latitude=45.984549611816824,
            longitude=14.573045134208522
        )
    ),
    PPlusR(
        name="Ježica P+R",
        location=LatitudeLongitude(
            latitude=46.098260477233154,
            longitude=14.514537553143578
        )
    ),
    PPlusR(
        name="Barje P+R",
        location=LatitudeLongitude(
            latitude=46.026998079960904,
            longitude=14.500014207251574
        )
    ),
    PPlusR(
        name="Sinja Gorica (Vrhnika) P+R",
        location=LatitudeLongitude(
            latitude=45.977638600736874,
            longitude=14.308792472252293
        )
    ),
    PPlusR(
        name="Stanežiče P+R",
        location=LatitudeLongitude(
            latitude=46.10754761732814,
            longitude=14.449335612789403
        )
    ),
    PPlusR(
        name="Grosuplje P+R",
        location=LatitudeLongitude(
            latitude=45.95723414853831,
            longitude=14.652393760311602
        )
    ),
]


PROPOSED_NEW_P_PLUS_R_STATIONS: list[PPlusR] = [
    PPlusR(
        name="Šmartno P+R",
        location=LatitudeLongitude(
            latitude=46.126144,
            longitude=14.485276
        )
    ),
    PPlusR(
        name="Črnuče P+R",
        location=LatitudeLongitude(
            latitude=46.104248,
            longitude=14.545969
        )
    ),
    PPlusR(
        name="Trzin P+R",
        location=LatitudeLongitude(
            latitude=46.119323,
            longitude=14.551727
        )
    ),
    PPlusR(
        name="Brinje P+R",
        location=LatitudeLongitude(
            latitude=46.090573,
            longitude=14.597373
        )
    ),
    PPlusR(
        name="Brezovica pri Ljubljani P+R",
        location=LatitudeLongitude(
            latitude=46.025983,
            longitude=14.430386
        )
    ),
]