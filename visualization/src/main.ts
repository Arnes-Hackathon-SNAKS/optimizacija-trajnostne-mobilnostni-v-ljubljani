import "./style.scss";
import { HeatLayer, heatLayer } from "./vendor/Leaflet.heat/HeatLayer.js";
import leaflet, { type MapOptions, TileLayerOptions } from "leaflet";
import "leaflet/dist/leaflet.css";
import { VisualizationData } from "./data.ts";


const LEAFLET_MAP_ELEMENT_ID: string = "leaflet-map";
const MAP_CONTROLS_ELEMENT_IDS = {
    busStationPositionsToggle: "control_bus_station-positions",
    busStationPositionsHeatmapToggle: "control_bus_station-heatmap",
    busArrivalHeatmapToggle: "control_bus_arrival-heatmap",
    bikeLanesToggle: "control_bike_lanes",
    existingParkAndRide: "control_existing-par",
    proposedParkAndRide: "control_proposed-par",
    greenZone: "control_green-zone"
};

const VISUALIZATION_JSON_FILE_PATH: string = "otmlj-data_2024-05-13_20-01-16.json";


function getRequiredElementById<E extends HTMLElement>(
  elementId: string
): E {
    const element = document.getElementById(elementId);
    if (element == null) {
        throw new Error(`Element with id ${elementId} not found`);
    }

    return <E> element;
}


async function loadJSONFileFromUrl(url: string): Promise<Record<string, any>> {
    return fetch(url)
      .then(response => response.json());
}

async function loadVisualizationData(): Promise<VisualizationData> {
    return <VisualizationData> await loadJSONFileFromUrl(VISUALIZATION_JSON_FILE_PATH);
}


type MapState = {
    map: leaflet.Map,
    tiles: leaflet.TileLayer,
    layerGroups: {
        busStationPositions: leaflet.LayerGroup,
        busStationPositionsHeatmap: leaflet.LayerGroup,
        dailyBusStopsHeatmap: leaflet.LayerGroup,
        bikeLaneRoutes: leaflet.LayerGroup,
        existingParkAndRideLocations: leaflet.LayerGroup,
        proposedParkAndRideLocations: leaflet.LayerGroup,
        proposedGreenZone: leaflet.LayerGroup,
    },
    heatmaps: {
        busStationPositions: typeof HeatLayer,
        busDailyStops: typeof HeatLayer,
    }
};


const busIcon = leaflet.icon({
    iconUrl: "icons/bus-front_alt.svg",
    iconSize: [16, 16],
    popupAnchor: [0, -16],
    className: "map-bus-icon"
});

const parkAndRideBlueIcon = leaflet.icon({
    iconUrl: "icons/p-and-r_blue_v1.svg",
    iconSize: [32, 16],
    popupAnchor: [0, -16],
    className: "map-p-plus-r-icon"
});

const parkAndRideGreenIcon = leaflet.icon({
    iconUrl: "icons/p-and-r_green_v1.svg",
    iconSize: [32, 16],
    popupAnchor: [0, -16],
    className: "map-p-plus-r-icon"
});



async function setUpMap(
  mapDOMElement: HTMLElement,
  visualizationData: VisualizationData,
): Promise<MapState> {
    /*
     * Precalculate some data
     */
    let maximumArrivalsPerDay: number = 0;
    for (const busStop of visualizationData.bus.stops_with_arrivals) {
        let totalArrivalsPerDay = 0;
        for (const arrivalPerHour of busStop.arrivals_per_hour) {
            totalArrivalsPerDay += arrivalPerHour;
        }

        if (totalArrivalsPerDay > maximumArrivalsPerDay) {
            maximumArrivalsPerDay = totalArrivalsPerDay;
        }
    }

    console.log("Maximum arrivals per day: " + maximumArrivalsPerDay);



    /*
     * Set up leaflet map
     */
    const mapOptions: MapOptions = {
        minZoom: 12,
        zoom: 12.5,
        maxZoom: 20,
        zoomDelta: 0.5,
        zoomSnap: 0.5,
        center: [46.0496302,14.5082294],
        // maxBounds: [
        //     [46.1119247,14.3496721],
        //     [45.9763077,14.7196471]
        // ],
        maxBounds: [
            [46.18656505801903,14.203550599655188],
            [45.8912566052835,14.804051448498598]
        ],
        wheelPxPerZoomLevel: 140,
    };
    const leafletMap = leaflet.map(mapDOMElement, mapOptions);


    const tileLayerOptions: TileLayerOptions = {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    };
    const tileLayer = leaflet.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", tileLayerOptions);
    tileLayer.addTo(leafletMap);


    // Set up layer groups.
    const busStationPositionsLayerGroup = leaflet.layerGroup();
    const busStationPositionHeatmapLayerGroup = leaflet.layerGroup();
    const busDailyStopsHeatmapLayerGroup = leaflet.layerGroup();
    const bikeLaneRoutesLayerGroup = leaflet.layerGroup();
    const existingParkAndRideLocationsLayerGroup = leaflet.layerGroup();
    const proposedParkAndRideLocationsLayerGroup = leaflet.layerGroup();
    const proposedGreenZoneLayerGroup = leaflet.layerGroup();



    /*
     * Prepare heat maps
     */

    const heatmapStops = {
        0.25: "rgb(255,28,62)",
        0.50: "rgb(250,180,28)",
        0.65: "#aad27a",
        0.80: "#21ce29",
    };

    const busStationPositionHeatmap = heatLayer(
      [],
      {
          radius: 36,
          minOpacity: 0.2,
          blur: 22,
          // max: 1.0,
          gradient: heatmapStops
      }
    );
    busStationPositionHeatmap.addTo(busStationPositionHeatmapLayerGroup);



    const dailyBusesHeatmapStops = {
        0.15: "rgb(255,28,62)",
        0.30: "rgb(250,180,28)",
        0.55: "#aad27a",
        0.70: "#21ce29",
    };

    const busStationDailyStopsHeatmap = heatLayer(
      [],
      {
          radius: 36,
          minOpacity: 0.2,
          blur: 22,
          // max: 1.0,
          gradient: dailyBusesHeatmapStops
      }
    );

    busStationDailyStopsHeatmap.addTo(busDailyStopsHeatmapLayerGroup);




    /*
     * Bus station positions location (+ daily stops) heatmap
     */

    for (const busStop of visualizationData.bus.stops_with_arrivals) {
        const busStationMarker = leaflet.marker(
          busStop.location,
          {
              icon: busIcon
          }
        );

        let totalArrivalsPerDay = 0;
        for (const arrivalPerHour of busStop.arrivals_per_hour) {
            totalArrivalsPerDay += arrivalPerHour;
        }

        // console.log(`Station ${busStop.name} has ${totalArrivalsPerDay} daily arrivals (${totalArrivalsPerDay / maximumArrivalsPerDay}).`);


        busStationPositionHeatmap.addLatLng(
          [busStop.location[0], busStop.location[1], 1]
        );
        busStationDailyStopsHeatmap.addLatLng(
          [busStop.location[0], busStop.location[1], totalArrivalsPerDay / maximumArrivalsPerDay]
        );

        busStationMarker.bindPopup(
`
<div class="bus-station-marker">
    <div class="bus-station-marker_top">
        ${busStop.code}
    </div>
    <div class="bus-station-marker_main">
        Postaja <b>${busStop.name}</b>
    </div>
    <div class="bus-station-marker_daily-count">
        ${totalArrivalsPerDay} avtobusov na dan
    </div>
</div>
`
        );

        busStationMarker.addTo(busStationPositionsLayerGroup);
    }



    /*
     * Bike lanes
     */

    for (const bikeLane of visualizationData.bike.bike_lanes) {
        const bikeLanePolyLine = leaflet.polyline(
          bikeLane.line_points,
          {
              color: "#494652",
              opacity: 0.8,
          }
        );

        bikeLanePolyLine.addTo(bikeLaneRoutesLayerGroup);
    }




    /*
     * Proposed green zone
     */

    const greenZonePolygon = leaflet.polygon(
      visualizationData.green_zone.green_zone.polygon_bounds,
      {
          color: "#af52a7",
          opacity: 0.7,
          fillColor: "#bb3ed7",
          fillOpacity: 0.25,
      }
    );

    const greenZoneSquareKilometres = (visualizationData.green_zone.green_zone.area_in_square_metres / 1000000)
        .toFixed(2);

    greenZonePolygon.bindPopup(
`
<div class="green-zone-marker">
    <div class="green-zone-marker_title">
        Predlagan zeleni krog
    </div>
    <div class="green-zone-marker_area">
        Površina: ${greenZoneSquareKilometres} km<sup>2</sup>
    </div>
</div>
`,
      {
          maxWidth: 600
      }
    );

    greenZonePolygon.addTo(proposedGreenZoneLayerGroup);




    /*
     * Park and ride locations (existing and proposed)
     */

    for (const existingPPlusR of visualizationData.p_plus_r.existing) {
        const locationMarker = leaflet.marker(
          existingPPlusR.location,
          {
              icon: parkAndRideBlueIcon
          }
        );

        let nameWithoutPPlusRSuffix = existingPPlusR.name.replace("P+R", "");
        nameWithoutPPlusRSuffix = nameWithoutPPlusRSuffix.trim();

        locationMarker.bindPopup(
`
<div class="par-marker par-marker__existing">
    <div class="par-marker_type">
        obstoječi P+R
    </div>
    <div class="par-marker_name">
        ${nameWithoutPPlusRSuffix}
    </div>
</div>
`
        );

        locationMarker.addTo(existingParkAndRideLocationsLayerGroup);
    }

    for (const proposedPPlusR of visualizationData.p_plus_r.proposed) {
        const locationMarker = leaflet.marker(
          proposedPPlusR.location,
          {
              icon: parkAndRideGreenIcon
          }
        );

        locationMarker.bindPopup(
          `
<div class="par-marker par-marker__proposed">
    <div class="par-marker_type">
        predlog za novi P+R
    </div>
    <div class="par-marker_name">
        ${proposedPPlusR.name}
    </div>
</div>
`
        );

        locationMarker.addTo(proposedParkAndRideLocationsLayerGroup);

    }



    return {
        map: leafletMap,
        tiles: tileLayer,
        layerGroups: {
            busStationPositions: busStationPositionsLayerGroup,
            busStationPositionsHeatmap: busStationPositionHeatmapLayerGroup,
            dailyBusStopsHeatmap: busDailyStopsHeatmapLayerGroup,
            bikeLaneRoutes: bikeLaneRoutesLayerGroup,
            existingParkAndRideLocations: existingParkAndRideLocationsLayerGroup,
            proposedParkAndRideLocations: proposedParkAndRideLocationsLayerGroup,
            proposedGreenZone: proposedGreenZoneLayerGroup
        },
        heatmaps: {
            busStationPositions: busStationPositionHeatmap,
            busDailyStops: busStationDailyStopsHeatmap,
        }
    }
}


async function setUpInteractivity(
  mapState: MapState
) {
    const busStationPositionsCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.busStationPositionsToggle);

    const busStationPositionHeatmapCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.busStationPositionsHeatmapToggle);

    const busArrivalHeatmapCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.busArrivalHeatmapToggle);

    const bikeLanesCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.bikeLanesToggle);

    const existingParkAndRideCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.existingParkAndRide);

    const proposedParkAndRideCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.proposedParkAndRide);

    const greenZoneCheckboxElement =
      getRequiredElementById<HTMLInputElement>(MAP_CONTROLS_ELEMENT_IDS.greenZone);


    // Set up default values.
    busStationPositionsCheckboxElement.checked = false;
    busStationPositionHeatmapCheckboxElement.checked = false;
    busArrivalHeatmapCheckboxElement.checked = true;
    bikeLanesCheckboxElement.checked = false;
    existingParkAndRideCheckboxElement.checked = true;
    proposedParkAndRideCheckboxElement.checked = true;
    greenZoneCheckboxElement.checked = true;


    function setUpElementForInteractiveLayerGroupToggle(
      toggleElement: HTMLInputElement,
      layerGroupToControl: leaflet.LayerGroup
    ) {
        function applyVisibilityToGroupLayer(value: boolean) {
            if (value) {
                if (!mapState.map.hasLayer(layerGroupToControl)) {
                    layerGroupToControl.addTo(mapState.map);
                }
            } else {
                if (mapState.map.hasLayer(layerGroupToControl)) {
                    layerGroupToControl.removeFrom(mapState.map);
                }
            }
        }

        toggleElement.addEventListener("click", () => {
            applyVisibilityToGroupLayer(toggleElement.checked);
        });

        applyVisibilityToGroupLayer(toggleElement.checked);
    }


    setUpElementForInteractiveLayerGroupToggle(
      busStationPositionsCheckboxElement,
      mapState.layerGroups.busStationPositions
    );

    setUpElementForInteractiveLayerGroupToggle(
      busStationPositionHeatmapCheckboxElement,
      mapState.layerGroups.busStationPositionsHeatmap,
    );

    setUpElementForInteractiveLayerGroupToggle(
      busArrivalHeatmapCheckboxElement,
      mapState.layerGroups.dailyBusStopsHeatmap
    );

    setUpElementForInteractiveLayerGroupToggle(
      bikeLanesCheckboxElement,
      mapState.layerGroups.bikeLaneRoutes
    );

    setUpElementForInteractiveLayerGroupToggle(
      existingParkAndRideCheckboxElement,
      mapState.layerGroups.existingParkAndRideLocations
    );

    setUpElementForInteractiveLayerGroupToggle(
      proposedParkAndRideCheckboxElement,
      mapState.layerGroups.proposedParkAndRideLocations
    );

    setUpElementForInteractiveLayerGroupToggle(
      greenZoneCheckboxElement,
      mapState.layerGroups.proposedGreenZone
    );
}


async function main() {
    const mapSurfaceElement = getRequiredElementById(LEAFLET_MAP_ELEMENT_ID);

    const visualizationData = await loadVisualizationData();
    console.log("Visualization data loaded.");

    const mapState = await setUpMap(
      mapSurfaceElement,
      visualizationData
    );
    console.log("Map set up.");

    await setUpInteractivity(mapState);
    console.log("Interactivity set up.");
}


document.addEventListener("DOMContentLoaded", () => {
    main();
})