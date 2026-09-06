import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'pk.eyJ1IjoicHJhdGhlZSIsImEiOiJjbXRvbWlwNjkwbG5sMndxdTduNDRubjc2In0.143URl9pUqfKQ0smSzePew'; 

export default function GlobeMap({ activeTarget, geoData }) {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (map.current) return; 

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11', // STRICT DARK MODE
      projection: 'globe', 
      zoom: 1.5,
      center: [72.6050, 18.7510],
    });

    map.current.on('style.load', () => {
      setTimeout(() => { map.current.resize(); }, 200);

      // Deep space atmosphere
      map.current.setFog({
        'color': 'rgb(15, 23, 42)',
        'high-color': 'rgb(16, 185, 129)',
        'horizon-blend': 0.2,
        'space-color': 'rgb(0, 0, 0)',
        'star-intensity': 0.8
      });

      map.current.addSource('aegis-data', { 
        type: 'geojson', 
        data: { type: 'FeatureCollection', features: [] } 
      });

      // 1. Hexagon Fill (Tactical Cyan)
      map.current.addLayer({
        'id': 'h3-fill',
        'type': 'fill',
        'source': 'aegis-data',
        'filter': ['==', 'layer', 'h3_drift'],
        'paint': { 'fill-color': '#38bdf8', 'fill-opacity': 0.25 }
      });

      // 2. Hexagon Outline (Glowing borders)
      map.current.addLayer({
        'id': 'h3-outline',
        'type': 'line',
        'source': 'aegis-data',
        'filter': ['==', 'layer', 'h3_drift'],
        'paint': { 'line-color': '#0284c7', 'line-width': 2 }
      });

      // 3. AIS Track (Yellow dashed line)
      map.current.addLayer({
        'id': 'ais-track',
        'type': 'line',
        'source': 'aegis-data',
        'filter': ['==', 'layer', 'ais_track'],
        'paint': { 'line-color': '#eab308', 'line-width': 3, 'line-dasharray': [2, 2] }
      });

      // 4. Incident Marker (Red Dot for Spill)
      map.current.addLayer({
        'id': 'incident-marker',
        'type': 'circle',
        'source': 'aegis-data',
        'filter': ['==', 'layer', 'incident'],
        'paint': { 'circle-color': '#ef4444', 'circle-radius': 7, 'circle-stroke-width': 2, 'circle-stroke-color': '#1e293b' }
      });

      // 5. Ship Marker (Green Dot for Suspect Vessel)
      map.current.addLayer({
        'id': 'ship-marker',
        'type': 'circle',
        'source': 'aegis-data',
        'filter': ['==', 'layer', 'ship'],
        'paint': { 'circle-color': '#10b981', 'circle-radius': 7, 'circle-stroke-width': 2, 'circle-stroke-color': '#1e293b' }
      });
    });
  }, []);

  useEffect(() => {
    if (!map.current || !map.current.getSource('aegis-data')) return;
    if (geoData && geoData.features.length > 0) {
      map.current.getSource('aegis-data').setData(geoData);
    }
  }, [geoData]);

  useEffect(() => {
    if (!map.current) return;
    
    if (activeTarget) {
      map.current.flyTo({ 
        center: activeTarget.coordinates, 
        zoom: 10, 
        pitch: 45, 
        bearing: -10, 
        duration: 4000, 
        essential: true 
      });
    } else {
      map.current.flyTo({ center: [72.6050, 18.7510], zoom: 1.5, pitch: 0, bearing: 0, duration: 3000 });
      if (map.current.getSource('aegis-data')) {
        map.current.getSource('aegis-data').setData({ type: 'FeatureCollection', features: [] });
      }
    }
  }, [activeTarget]);

  return <div ref={mapContainer} className="w-full h-full absolute inset-0 bg-[#020409]" />;
}

// import { useEffect, useRef } from 'react';
// import mapboxgl from 'mapbox-gl';
// import 'mapbox-gl/dist/mapbox-gl.css';

// mapboxgl.accessToken = 'pk.eyJ1IjoicHJhdGhlZSIsImEiOiJjbXRvbWlwNjkwbG5sMndxdTduNDRubjc2In0.143URl9pUqfKQ0smSzePew'; 

// export default function GlobeMap({ activeTarget, geoData }) {
//   const mapContainer = useRef(null);
//   const map = useRef(null);

//   // Initialize Map
//   useEffect(() => {
//     if (map.current) return; 

//     map.current = new mapboxgl.Map({
//       container: mapContainer.current,
//       style: 'mapbox://styles/mapbox/dark-v11',
//       projection: 'globe', 
//       zoom: 1.5,
//       center: [72.6050, 18.7510],
//     });

//     map.current.on('style.load', () => {
//       setTimeout(() => { map.current.resize(); }, 200);

//       map.current.setFog({
//         'color': 'rgb(4, 11, 22)',
//         'high-color': 'rgb(0, 225, 255)',
//         'horizon-blend': 0.1,
//         'space-color': 'rgb(2, 4, 9)',
//         'star-intensity': 0.9
//       });

//       // Start with an empty GeoJSON source
//       map.current.addSource('aegis-data', { 
//         type: 'geojson', 
//         data: { type: 'FeatureCollection', features: [] } 
//       });

//       map.current.addLayer({
//         'id': 'h3-hexagons',
//         'type': 'fill-extrusion',
//         'source': 'aegis-data',
//         'filter': ['==', 'layer', 'h3_drift'],
//         'paint': { 
//           'fill-extrusion-color': '#00FF66', 
//           'fill-extrusion-height': 5000, 
//           'fill-extrusion-opacity': 0.7 
//         }
//       });
//     });
//   }, []);

//   // Watch for new API data and paint the map
//   useEffect(() => {
//     if (!map.current || !map.current.getSource('aegis-data')) return;
//     if (geoData && geoData.features.length > 0) {
//       map.current.getSource('aegis-data').setData(geoData);
//     }
//   }, [geoData]);

//   // Handle Camera FlyTo Animation
//   useEffect(() => {
//     if (!map.current) return;
    
//     if (activeTarget) {
//       // Fly to anomaly coordinates
//       map.current.flyTo({ 
//         center: activeTarget.coordinates, 
//         zoom: 7, 
//         pitch: 60, 
//         bearing: -20, 
//         duration: 4000, 
//         essential: true 
//       });
//     } else {
//       map.current.flyTo({ center: [72.6050, 18.7510], zoom: 1.5, pitch: 0, bearing: 0, duration: 3000 });
//       // Clear the map if reset
//       if (map.current.getSource('aegis-data')) {
//         map.current.getSource('aegis-data').setData({ type: 'FeatureCollection', features: [] });
//       }
//     }
//   }, [activeTarget]);

//   return <div ref={mapContainer} className="w-full h-full absolute inset-0 bg-[#020409]" />;
// }


// // import { useEffect, useRef } from 'react';
// // import mapboxgl from 'mapbox-gl';
// // import 'mapbox-gl/dist/mapbox-gl.css';

// // // Your verified token
// // mapboxgl.accessToken = 'pk.eyJ1IjoicHJhdGhlZSIsImEiOiJjbXRvbWlwNjkwbG5sMndxdTduNDRubjc2In0.143URl9pUqfKQ0smSzePew'; 

// // const mockAegisData = {
// //   "type": "FeatureCollection",
// //   "features": [
// //     {
// //       "type": "Feature",
// //       "properties": { "layer": "sar_slick", "color": "#FF0033" },
// //       "geometry": { "type": "Polygon", "coordinates": [[[72.600, 18.746], [72.610, 18.749], [72.613, 18.757], [72.603, 18.755], [72.600, 18.746]]] }
// //     },
// //     {
// //       "type": "Feature",
// //       "properties": { "layer": "h3_drift", "probability": 98.4 },
// //       "geometry": { "type": "Polygon", "coordinates": [[[72.610, 18.750], [72.620, 18.755], [72.630, 18.750], [72.630, 18.740], [72.620, 18.735], [72.610, 18.740], [72.610, 18.750]]] }
// //     },
// //     {
// //       "type": "Feature",
// //       "properties": { "layer": "suspect_vessel", "mmsi": "419000789" },
// //       "geometry": { "type": "LineString", "coordinates": [[72.350, 18.300], [72.415, 18.560], [72.480, 18.820]] }
// //     }
// //   ]
// // };

// // export default function GlobeMap({ activeTarget }) {
// //   const mapContainer = useRef(null);
// //   const map = useRef(null);

// //   // Initialize Map
// //   useEffect(() => {
// //     if (map.current) return; 

// //     map.current = new mapboxgl.Map({
// //       container: mapContainer.current,
// //       accessToken: mapboxgl.accessToken,
// //       style: 'mapbox://styles/mapbox/dark-v11',
// //       projection: 'globe', 
// //       zoom: 1.5,
// //       center: [72.6050, 18.7510],
// //     });

// //     map.current.on('style.load', () => {
// //       // Add a delayed resize trigger to force the canvas to calculate its bounds
// //       setTimeout(() => { map.current.resize(); }, 200);

// //       map.current.setFog({
// //         'color': 'rgb(4, 11, 22)',
// //         'high-color': 'rgb(0, 225, 255)',
// //         'horizon-blend': 0.1,
// //         'space-color': 'rgb(2, 4, 9)',
// //         'star-intensity': 0.9
// //       });

// //       map.current.addSource('aegis-data', { type: 'geojson', data: mockAegisData });

// //       map.current.addLayer({
// //         'id': 'h3-hexagons',
// //         'type': 'fill-extrusion',
// //         'source': 'aegis-data',
// //         'filter': ['==', 'layer', 'h3_drift'],
// //         'paint': { 'fill-extrusion-color': '#00FF66', 'fill-extrusion-height': 5000, 'fill-extrusion-opacity': 0.7 }
// //       });

// //       map.current.addLayer({
// //         'id': 'dark-vessel-track',
// //         'type': 'line',
// //         'source': 'aegis-data',
// //         'filter': ['==', 'layer', 'suspect_vessel'],
// //         'paint': { 'line-color': '#FFFF00', 'line-width': 4, 'line-dasharray': [2, 2] }
// //       });

// //       map.current.addLayer({
// //         'id': 'oil-slick',
// //         'type': 'fill',
// //         'source': 'aegis-data',
// //         'filter': ['==', 'layer', 'sar_slick'],
// //         'paint': { 'fill-color': '#FF0033', 'fill-opacity': 0.8 }
// //       });
// //     });
// //   }, []);

// //   // Handle Camera FlyTo Animation
// //   useEffect(() => {
// //     if (!map.current) return;
    
// //     if (activeTarget) {
// //       map.current.flyTo({ center: [72.6050, 18.7510], zoom: 10, pitch: 60, bearing: -20, duration: 4000, essential: true });
// //     } else {
// //       map.current.flyTo({ center: [72.6050, 18.7510], zoom: 1.5, pitch: 0, bearing: 0, duration: 3000 });
// //     }
// //   }, [activeTarget]);

// //   return <div ref={mapContainer} className="w-full h-full absolute inset-0 bg-[#020409]" />;
// // }