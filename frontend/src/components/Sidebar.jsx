import React, { useState } from 'react';
import axios from 'axios';
import { cellToBoundary } from 'h3-js';

const mockAnomalies = [
  {
    id: 'ANM-9921',
    type: 'OIL_DUMP',
    confidence: 0.94,
    coordinates: [65.0, 15.0], // Arabian Sea (Lon, Lat) matching backend mock
    timestamp: '2026-09-05T22:14:00Z',
    description: 'Dark fleet suspected. AIS gap of 4 hours.',
  }
];

const Sidebar = ({ activeAnomaly, setActiveAnomaly, setMapData, apiResponse, setApiResponse }) => {
  const [isExecuting, setIsExecuting] = useState(false);

  const handleActivate = async (anm) => {
    setActiveAnomaly(anm);
    setIsExecuting(true);
    
    try {
      const res = await axios.post('http://localhost:8000/api/v1/triage', {
        chip_id: anm.id,
        center_lat: anm.coordinates[1],
        center_lon: anm.coordinates[0]
      });
      
      const data = res.data;
      setApiResponse(data);

      // 1. Decode the Hexagons
      const features = Object.keys(data.h3_origin_hexagons).map(hexId => {
        const boundary = cellToBoundary(hexId, true);
        return {
          type: 'Feature',
          properties: { layer: 'h3_drift', intensity: data.h3_origin_hexagons[hexId] },
          geometry: { type: 'Polygon', coordinates: [boundary] }
        };
      });

      // 2. Add Incident Location (The Oil Slick)
      features.push({
        type: 'Feature',
        properties: { layer: 'incident' },
        geometry: { type: 'Point', coordinates: [anm.coordinates[0], anm.coordinates[1]] }
      });

      // 3. Add the AIS Track (Yellow dashed line)
      if (data.top_suspects[0].historical_path) {
        features.push({
          type: 'Feature',
          properties: { layer: 'ais_track' },
          geometry: { type: 'LineString', coordinates: data.top_suspects[0].historical_path }
        });

        // 4. Add Current Ship Location (End of the track)
        const pathLength = data.top_suspects[0].historical_path.length;
        features.push({
          type: 'Feature',
          properties: { layer: 'ship' },
          geometry: { type: 'Point', coordinates: data.top_suspects[0].historical_path[pathLength - 1] }
        });
      }

      // Push everything to the map at once
      setMapData({
        type: 'FeatureCollection',
        features: features
      });

    } catch (err) {
      console.error("Pipeline Failed. Ensure Uvicorn is running.", err);
    }
    setIsExecuting(false);
  };

  const handleReset = () => {
    setActiveAnomaly(null);
    setApiResponse(null);
    setMapData({ type: 'FeatureCollection', features: [] });
  };

  return (
    <div className="w-[30%] h-full bg-slate-900 border-l border-slate-800 flex flex-col overflow-y-auto">
      <div className="p-4 border-b border-slate-800 sticky top-0 bg-slate-900 z-10">
        <h2 className="text-lg font-bold text-slate-100 flex items-center justify-between uppercase">
          {activeAnomaly ? 'Tactical Intercept Dossier' : 'Active Anomalies Feed'}
          {activeAnomaly && (
            <button 
              onClick={handleReset}
              className="text-xs text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 px-2 py-1 rounded transition-colors"
            >
              ◄ RESET COMMAND
            </button>
          )}
        </h2>
      </div>

      <div className="p-4 flex-1">
        {!activeAnomaly ? (
          // FEED STATE
          <div className="flex flex-col gap-4">
            {mockAnomalies.map((anm) => (
              <div 
                key={anm.id}
                onClick={() => handleActivate(anm)}
                className="bg-slate-950 border border-slate-800 p-4 rounded cursor-pointer hover:border-radar-blue transition-all group"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-alert-red font-mono text-sm font-bold">{anm.id}</span>
                  <span className="text-neon-green font-mono text-xs">{anm.timestamp.substring(11, 16)} Z</span>
                </div>
                <h3 className="text-white font-semibold mb-1">{anm.type.replace('_', ' ')}</h3>
                <p className="text-slate-400 text-sm mb-3">{anm.description}</p>
                <div className="flex justify-between items-center text-xs text-slate-500">
                  <span>LAT/LON: {anm.coordinates[1].toFixed(2)}, {anm.coordinates[0].toFixed(2)}</span>
                  <span className="group-hover:text-radar-blue transition-colors">ACTIVATE &rarr;</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          // INTERCEPT STATE
          <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-right-4 duration-300">
            <div className="bg-slate-950 border border-slate-800 rounded p-4">
              <h3 className="text-radar-blue font-mono text-xs uppercase mb-1">Target ID</h3>
              <p className="text-xl font-bold">{activeAnomaly.id}</p>
            </div>
            
            {isExecuting || !apiResponse ? (
              <div className="bg-slate-900 border border-radar-blue p-8 rounded text-center animate-pulse">
                <p className="text-radar-blue font-mono text-sm tracking-widest">EXECUTING EULER-MARUYAMA SDE...</p>
              </div>
            ) : (
              <>
                <div className="bg-slate-950 border border-alert-red/50 rounded p-4">
                  <h3 className="text-alert-red font-mono text-xs uppercase mb-4 font-bold">Attribution Data: Prime Suspect</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="block text-slate-500 text-xs">Vessel Name</span>
                      <span className="text-white font-mono font-bold text-sm">{apiResponse.top_suspects[0].vessel_name}</span>
                    </div>
                    <div>
                      <span className="block text-slate-500 text-xs">Vessel MMSI</span>
                      <span className="text-white font-mono">{apiResponse.top_suspects[0].mmsi}</span>
                    </div>
                    <div>
                      <span className="block text-slate-500 text-xs">Kinematic Match (SDE)</span>
                      <span className="text-neon-green font-mono">{(apiResponse.top_suspects[0].kinematic_guilt_scores.phi_align * 100).toFixed(1)}%</span>
                    </div>
                    <div>
                      <span className="block text-slate-500 text-xs">Evasion Tactics</span>
                      <span className="text-alert-red text-xs">Magic Pipe Flagged</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded p-4">
                  <h3 className="text-radar-blue font-mono text-xs uppercase mb-3">Mathematical Proof</h3>
                  <p className="text-slate-400 text-sm font-mono leading-relaxed bg-slate-900 p-3 rounded border border-slate-800">
                    dX_t = a(X_t, t)dt + b(X_t, t)dW_t<br/><br/>
                    Euler-Maruyama Inverse Lagrangian Drift Engine confirms origin trajectory with {apiResponse.top_suspects[0].kinematic_guilt_scores.phi_align * 100}% alignment against historical IMM Kalman tracking data.
                  </p>
                </div>
              </>
            )}

            <button 
              disabled={isExecuting}
              className={`w-full py-3 rounded font-bold tracking-widest transition-colors ${
                isExecuting 
                ? 'bg-slate-800 text-slate-600' 
                : 'bg-alert-red/20 text-alert-red border border-alert-red/50 hover:bg-alert-red/30'
              }`}
            >
              {isExecuting ? 'PROCESSING...' : 'SCRAMBLE INTERCEPT'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;

// import React, { useState } from 'react';
// import axios from 'axios';
// import { cellToBoundary } from 'h3-js';

// const mockAnomalies = [
//   {
//     id: 'ANM-9921',
//     type: 'OIL_DUMP',
//     confidence: 0.94,
//     coordinates: [65.0, 15.0], // Arabian Sea (Lon, Lat) matching backend mock
//     timestamp: '2026-09-05T22:14:00Z',
//     description: 'Dark fleet suspected. AIS gap of 4 hours.',
//   }
// ];

// const Sidebar = ({ activeAnomaly, setActiveAnomaly, setMapData, apiResponse, setApiResponse }) => {
//   const [isExecuting, setIsExecuting] = useState(false);

//   const handleActivate = async (anm) => {
//     setActiveAnomaly(anm);
//     setIsExecuting(true);
    
//     try {
//       // 1. Hit the local Python backend
//       const res = await axios.post('http://localhost:8000/api/v1/triage', {
//         chip_id: anm.id,
//         center_lat: anm.coordinates[1], // API wants Latitude
//         center_lon: anm.coordinates[0]  // API wants Longitude
//       });
      
//       const data = res.data;
//       setApiResponse(data);

//       // 2. Decode the Hexagons back into GeoJSON Map Polygons
//       const h3Features = Object.keys(data.h3_origin_hexagons).map(hexId => {
//         const boundary = cellToBoundary(hexId, true); // true = [lon, lat] format
//         return {
//           type: 'Feature',
//           properties: { layer: 'h3_drift', intensity: data.h3_origin_hexagons[hexId] },
//           geometry: { type: 'Polygon', coordinates: [boundary] }
//         };
//       });

//       setMapData({
//         type: 'FeatureCollection',
//         features: [...h3Features]
//       });

//     } catch (err) {
//       console.error("Pipeline Failed. Ensure Uvicorn is running.", err);
//     }
//     setIsExecuting(false);
//   };

//   const handleReset = () => {
//     setActiveAnomaly(null);
//     setApiResponse(null);
//   };

//   return (
//     <div className="w-[30%] h-full bg-slate-900 border-l border-slate-800 flex flex-col overflow-y-auto">
//       <div className="p-4 border-b border-slate-800 sticky top-0 bg-slate-900 z-10">
//         <h2 className="text-lg font-bold text-slate-100 flex items-center justify-between uppercase">
//           {activeAnomaly ? 'Tactical Intercept Dossier' : 'Active Anomalies Feed'}
//           {activeAnomaly && (
//             <button 
//               onClick={handleReset}
//               className="text-xs text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 px-2 py-1 rounded transition-colors"
//             >
//               ◄ RESET COMMAND
//             </button>
//           )}
//         </h2>
//       </div>

//       <div className="p-4 flex-1">
//         {!activeAnomaly ? (
//           // FEED STATE
//           <div className="flex flex-col gap-4">
//             {mockAnomalies.map((anm) => (
//               <div 
//                 key={anm.id}
//                 onClick={() => handleActivate(anm)}
//                 className="bg-slate-950 border border-slate-800 p-4 rounded cursor-pointer hover:border-radar-blue transition-all group"
//               >
//                 <div className="flex justify-between items-start mb-2">
//                   <span className="text-alert-red font-mono text-sm font-bold">{anm.id}</span>
//                   <span className="text-neon-green font-mono text-xs">{anm.timestamp.substring(11, 16)} Z</span>
//                 </div>
//                 <h3 className="text-white font-semibold mb-1">{anm.type.replace('_', ' ')}</h3>
//                 <p className="text-slate-400 text-sm mb-3">{anm.description}</p>
//                 <div className="flex justify-between items-center text-xs text-slate-500">
//                   <span>LAT/LON: {anm.coordinates[1].toFixed(2)}, {anm.coordinates[0].toFixed(2)}</span>
//                   <span className="group-hover:text-radar-blue transition-colors">ACTIVATE &rarr;</span>
//                 </div>
//               </div>
//             ))}
//           </div>
//         ) : (
//           // INTERCEPT STATE
//           <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-right-4 duration-300">
//             <div className="bg-slate-950 border border-slate-800 rounded p-4">
//               <h3 className="text-radar-blue font-mono text-xs uppercase mb-1">Target ID</h3>
//               <p className="text-xl font-bold">{activeAnomaly.id}</p>
//             </div>
            
//             {isExecuting || !apiResponse ? (
//               <div className="bg-slate-900 border border-radar-blue p-8 rounded text-center animate-pulse">
//                 <p className="text-radar-blue font-mono text-sm tracking-widest">EXECUTING EULER-MARUYAMA SDE...</p>
//               </div>
//             ) : (
//               <>
//                 <div className="bg-slate-950 border border-alert-red/50 rounded p-4">
//                   <h3 className="text-alert-red font-mono text-xs uppercase mb-4 font-bold">Attribution Data: Prime Suspect</h3>
//                   <div className="grid grid-cols-2 gap-4">
//                     <div>
//                       <span className="block text-slate-500 text-xs">Vessel Name</span>
//                       <span className="text-white font-mono font-bold text-sm">{apiResponse.top_suspects[0].vessel_name}</span>
//                     </div>
//                     <div>
//                       <span className="block text-slate-500 text-xs">Vessel MMSI</span>
//                       <span className="text-white font-mono">{apiResponse.top_suspects[0].mmsi}</span>
//                     </div>
//                     <div>
//                       <span className="block text-slate-500 text-xs">Kinematic Match (SDE)</span>
//                       <span className="text-neon-green font-mono">{(apiResponse.top_suspects[0].kinematic_guilt_scores.phi_align * 100).toFixed(1)}%</span>
//                     </div>
//                     <div>
//                       <span className="block text-slate-500 text-xs">Evasion Tactics</span>
//                       <span className="text-alert-red text-xs">Magic Pipe Flagged</span>
//                     </div>
//                   </div>
//                 </div>

//                 <div className="bg-slate-950 border border-slate-800 rounded p-4">
//                   <h3 className="text-radar-blue font-mono text-xs uppercase mb-3">Mathematical Proof</h3>
//                   <p className="text-slate-400 text-sm font-mono leading-relaxed bg-slate-900 p-3 rounded border border-slate-800">
//                     dX_t = a(X_t, t)dt + b(X_t, t)dW_t<br/><br/>
//                     Euler-Maruyama Inverse Lagrangian Drift Engine confirms origin trajectory with {apiResponse.top_suspects[0].kinematic_guilt_scores.phi_align * 100}% alignment against historical IMM Kalman tracking data.
//                   </p>
//                 </div>
//               </>
//             )}

//             <button 
//               disabled={isExecuting}
//               className={`w-full py-3 rounded font-bold tracking-widest transition-colors ${
//                 isExecuting 
//                 ? 'bg-slate-800 text-slate-600' 
//                 : 'bg-alert-red/20 text-alert-red border border-alert-red/50 hover:bg-alert-red/30'
//               }`}
//             >
//               {isExecuting ? 'PROCESSING...' : 'SCRAMBLE INTERCEPT'}
//             </button>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default Sidebar;

// // import React from 'react';

// // const mockAnomalies = [
// //   {
// //     id: 'ANM-9921',
// //     type: 'OIL_DUMP',
// //     confidence: 0.94,
// //     coordinates: [72.6050, 18.7510], // Arabian Sea
// //     timestamp: '2026-09-05T22:14:00Z',
// //     vessel_mmsi: '412000000',
// //     description: 'Dark fleet suspected. AIS gap of 4 hours.',
// //   },
// //   {
// //     id: 'ANM-8834',
// //     type: 'ILLEGAL_FISHING',
// //     confidence: 0.88,
// //     coordinates: [75.0, 15.0], 
// //     timestamp: '2026-09-05T21:05:00Z',
// //     vessel_mmsi: 'UNKNOWN',
// //     description: 'Multiple vessels congregating in EEZ.',
// //   }
// // ];

// // const Sidebar = ({ activeAnomaly, setActiveAnomaly }) => {
// //   return (
// //     <div className="w-[30%] h-full bg-slate-900 border-l border-slate-800 flex flex-col overflow-y-auto">
// //       {/* Header */}
// //       <div className="p-4 border-b border-slate-800 sticky top-0 bg-slate-900 z-10">
// //         <h2 className="text-lg font-bold text-slate-100 flex items-center justify-between uppercase">
// //           {activeAnomaly ? 'Tactical Intercept Dossier' : 'Active Anomalies Feed'}
// //           {activeAnomaly && (
// //             <button 
// //               onClick={() => setActiveAnomaly(null)}
// //               className="text-xs text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 px-2 py-1 rounded transition-colors"
// //             >
// //               BACK TO FEED
// //             </button>
// //           )}
// //         </h2>
// //       </div>

// //       <div className="p-4 flex-1">
// //         {!activeAnomaly ? (
// //           // State 1: Feed
// //           <div className="flex flex-col gap-4">
// //             {mockAnomalies.map((anm) => (
// //               <div 
// //                 key={anm.id}
// //                 onClick={() => setActiveAnomaly(anm)}
// //                 className="bg-slate-950 border border-slate-800 p-4 rounded cursor-pointer hover:border-radar-blue transition-all group"
// //               >
// //                 <div className="flex justify-between items-start mb-2">
// //                   <span className="text-alert-red font-mono text-sm font-bold">{anm.id}</span>
// //                   <span className="text-neon-green font-mono text-xs">{anm.timestamp.substring(11, 16)} Z</span>
// //                 </div>
// //                 <h3 className="text-white font-semibold mb-1">{anm.type.replace('_', ' ')}</h3>
// //                 <p className="text-slate-400 text-sm mb-3">{anm.description}</p>
// //                 <div className="flex justify-between items-center text-xs text-slate-500">
// //                   <span>LAT/LON: {anm.coordinates[1].toFixed(2)}, {anm.coordinates[0].toFixed(2)}</span>
// //                   <span className="group-hover:text-radar-blue transition-colors">ACTIVATE &rarr;</span>
// //                 </div>
// //               </div>
// //             ))}
// //           </div>
// //         ) : (
// //           // State 2: Intercept
// //           <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-right-4 duration-300">
// //             <div className="bg-slate-950 border border-slate-800 rounded p-4">
// //               <h3 className="text-radar-blue font-mono text-xs uppercase mb-1">Target ID</h3>
// //               <p className="text-xl font-bold">{activeAnomaly.id}</p>
// //             </div>
            
// //             <div className="bg-slate-950 border border-slate-800 rounded p-4">
// //               <h3 className="text-radar-blue font-mono text-xs uppercase mb-4">Attribution Data</h3>
// //               <div className="grid grid-cols-2 gap-4">
// //                 <div>
// //                   <span className="block text-slate-500 text-xs">Vessel MMSI</span>
// //                   <span className="text-white font-mono">{activeAnomaly.vessel_mmsi}</span>
// //                 </div>
// //                 <div>
// //                   <span className="block text-slate-500 text-xs">Confidence</span>
// //                   <span className="text-neon-green font-mono">{(activeAnomaly.confidence * 100).toFixed(1)}%</span>
// //                 </div>
// //                 <div>
// //                   <span className="block text-slate-500 text-xs">Evasion Tactics</span>
// //                   <span className="text-alert-red text-sm">AIS Spoofing / Gaps</span>
// //                 </div>
// //                 <div>
// //                   <span className="block text-slate-500 text-xs">Time of Event</span>
// //                   <span className="text-white text-sm">{activeAnomaly.timestamp}</span>
// //                 </div>
// //               </div>
// //             </div>

// //             <div className="bg-slate-950 border border-slate-800 rounded p-4">
// //               <h3 className="text-radar-blue font-mono text-xs uppercase mb-3">Mathematical Proof</h3>
// //               <p className="text-slate-400 text-sm font-mono leading-relaxed bg-slate-900 p-3 rounded border border-slate-800">
// //                 dX_t = a(X_t, t)dt + b(X_t, t)dW_t<br/><br/>
// //                 Euler-Maruyama Inverse Lagrangian Drift Engine confirms origin trajectory with 94% overlap against historical H3 grid cells.
// //               </p>
// //             </div>

// //             <button className="w-full bg-alert-red/20 text-alert-red border border-alert-red/50 hover:bg-alert-red/30 py-3 rounded font-bold tracking-widest transition-colors">
// //               SCRAMBLE INTERCEPT
// //             </button>
// //           </div>
// //         )}
// //       </div>
// //     </div>
// //   );
// // };

// // export default Sidebar;
