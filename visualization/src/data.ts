export type LatitudeLongitude = [
  number,
  number
];


export type ArrivalsPerHour = number[];

export type BusStopWithArrivalsPerHour = {
    id: string,
    code: number,
    name: string,
    location: LatitudeLongitude,
    arrivals_per_hour: ArrivalsPerHour,
};


export type BikeLane = {
    line_points: LatitudeLongitude[]
};

export type PPlusR = {
    name: string,
    location: LatitudeLongitude
};

export type GreenZone = {
    polygon_bounds: LatitudeLongitude[],
    area_in_square_metres: number,
};


export type VisualizationData = {
    bus: {
        stops_with_arrivals: BusStopWithArrivalsPerHour[],
    },
    bike: {
        bike_lanes: BikeLane[],
        total_length_in_metres: number,
    },
    p_plus_r: {
        existing: PPlusR[],
        proposed: PPlusR[],
    },
    green_zone: {
        green_zone: GreenZone
    }
};
