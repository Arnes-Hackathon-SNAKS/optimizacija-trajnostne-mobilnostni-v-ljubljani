import "./style.scss";
import { heatLayer } from "./vendor/Leaflet.heat/HeatLayer.js";
import leaflet, { type MapOptions, TileLayerOptions } from "leaflet";
import "leaflet/dist/leaflet.css";
// import JSZip from "jszip";
// import { open as shapefileOpen } from "shapefile";


// async function downloadBinaryFile(
//   url: string
// ): Promise<Blob> {
//     return fetch(url)
//       .then(response => response.blob());
// }

async function downloadJsonFile(
  url: string
): Promise<Record<string, any>> {
    return fetch(url)
      .then(response => response.json());
}

/*
async function extractAhpAndDbf(
  blob: Blob,
  collectionName: string,
): Promise<[ArrayBuffer, ArrayBuffer]> {
    const zipFile = await JSZip.loadAsync(blob);


    const shpFile = zipFile.file(collectionName + ".shp");
    if (shpFile == null) {
        throw new Error("File does not contain " + collectionName + ".shp");
    }

    const shpFileContents = await shpFile.async("arraybuffer");


    const dbfFile = zipFile.file(collectionName + ".dbf");
    if (dbfFile == null) {
        throw new Error("File does not contain " + collectionName + ".dbf");
    }

    const dbfFileContents = await dbfFile.async("arraybuffer");


    return [shpFileContents, dbfFileContents];
}
*/

async function main() {
    console.log("Starting.");

    const mapDivElement = document.getElementById("leaflet-map");
    if (mapDivElement == null) {
        throw new Error("Unable to find leaflet-map element.");
    }


    const individualStationsCheckbox = <HTMLInputElement | null> document.getElementById("control_individual-stations");
    if (individualStationsCheckbox == null) {
        throw new Error("Unable to find control_individual-stations element.");
    }

    const heatmapCheckbox = <HTMLInputElement | null> document.getElementById("control_heatmap");
    if (heatmapCheckbox == null) {
        throw new Error("Unable to find control_heatmap element.");
    }

    // const lppData = await downloadBinaryFile("/mollpp.zip");
    // const [lppShp, lppDbf] = await extractAhpAndDbf(lppData, "MOL_LPP");
    // console.log(lppShp, lppDbf);

    // const parsedLppData = await shapefileOpen(lppShp, lppDbf, { encoding: "utf8" });
    // console.log(parsedLppData);

    // const rawShapeFile = (await Shapefile.load(lppData))["MOL_LPP"];
    // console.log(rawShapeFile);
    //
    // const shapes = rawShapeFile.parse("shp");
    // console.log(shapes);
    //
    // const attributes = rawShapeFile.parse("dbf", { properties: true });
    // console.log(attributes);

    const lppData = await downloadJsonFile("/mollpp_wgs84.json");
    console.log(lppData);


    const busIcon = leaflet.icon({
        iconUrl: "/icons/bus-front_alt.svg",
        iconSize: [16, 16],
        popupAnchor: [0, -16],
        className: "map-bus-icon"
    });


    const mapOptions: MapOptions = {
        minZoom: 12.5,
        zoom: 13,
        maxZoom: 19,
        zoomDelta: 0.5,
        zoomSnap: 0.5,
        center: [46.0496302,14.5082294],
        maxBounds: [
          [46.1119247,14.3496721],
          [45.9763077,14.7196471]
        ],
        wheelPxPerZoomLevel: 140,
    };
    const leafletMap = leaflet.map(mapDivElement, mapOptions);


    const tileLayerOptions: TileLayerOptions = {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    };
    const tileLayer = leaflet.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", tileLayerOptions);
    tileLayer.addTo(leafletMap);


    const heatMapLayerGroup = leaflet.layerGroup();
    // heatMapLayerGroup.addTo(leafletMap);

    const heatMapLayer = heatLayer(
      [],
      {
          radius: 50,
          minOpacity: 0.15,
          blur: 12,
          max: 1.0
      }
    );
    heatMapLayer.addTo(heatMapLayerGroup);



    const stationsLayerGroup = leaflet.layerGroup();
    stationsLayerGroup.addTo(leafletMap);

    const lppStations: Record<string, any>[] = lppData["features"];
    for (const rawStationData of lppStations) {
        const rawStationCoordinates: any[] = rawStationData["geometry"]["coordinates"];

        const stationLng = parseFloat(rawStationCoordinates[0]);
        const stationLat = parseFloat(rawStationCoordinates[1]);

        const stationName = String(rawStationData["properties"]["Title"]);


        console.log(`Station ${stationName}: ${stationLat}, ${stationLng}`);

        const stationMarker = leaflet.marker(
          [stationLat, stationLng],
          {
              icon: busIcon
          }
        );

        heatMapLayer.addLatLng(
          [stationLat, stationLng, 1]
        );

        stationMarker.bindPopup(`Postaja <b>${stationName}</b>`);

        stationMarker.addTo(stationsLayerGroup);
    }


    individualStationsCheckbox.checked = true;
    heatmapCheckbox.checked = false;


    individualStationsCheckbox.addEventListener("click", () => {
        if (individualStationsCheckbox.checked) {
            leafletMap.addLayer(stationsLayerGroup);
        } else {
            leafletMap.removeLayer(stationsLayerGroup);
        }
    });

    heatmapCheckbox.addEventListener("click", () => {
        if (heatmapCheckbox.checked) {
            leafletMap.addLayer(heatMapLayerGroup);
        } else {
            leafletMap.removeLayer(heatMapLayerGroup);
        }
    });

    /*
    while (true) {
        const nextLocation = await parsedLppData.read();
        if (nextLocation.done) {
            console.log("All locations parsed.");
            break;
        }

        console.log(nextLocation);

        const stationCoordinates = (nextLocation.value.geometry as Record<string, any>)["coordinates"] as number[];
        const stationName = (nextLocation.value.properties as Record<string, any>)["Title"] as string;


        // const stationLat = parseFloat(stationCoordinates[0] as any) / 10000;
        // const stationLng = parseFloat(stationCoordinates[1] as any) / 10000;

        console.log(`Station ${stationName}: ${stationCoordinates}`);

        // const stationMarker = leaflet.marker(
        //   [stationLat, stationLng],
        //   {
        //
        //   }
        // );
        //
        // stationMarker.bindPopup(`Postaja: ${stationName}`);
        //
        // stationMarker.addTo(leafletMap);
    }
    */
}


document.addEventListener("DOMContentLoaded", () => {
    main();
})