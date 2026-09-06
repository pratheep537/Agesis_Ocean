import React, { useState } from 'react';
import CommandBar from './components/CommandBar';
import GlobeMap from './components/Map/GlobeMap';
import Sidebar from './components/Sidebar';

export default function App() {
  const [activeAnomaly, setActiveAnomaly] = useState(null);
  
  // Empty GeoJSON container for the live H3 polygons
  const [mapData, setMapData] = useState({ type: 'FeatureCollection', features: [] });
  const [apiResponse, setApiResponse] = useState(null);

  return (
    <div className="w-screen h-screen flex flex-col bg-slate-950 text-white font-sans overflow-hidden">
      <CommandBar />
      <div className="flex-1 flex overflow-hidden">
        <div className="w-[70%] h-full relative">
          {/* Inject dynamic API data into the map */}
          <GlobeMap activeTarget={activeAnomaly} geoData={mapData} />
        </div>
        <Sidebar 
          activeAnomaly={activeAnomaly} 
          setActiveAnomaly={setActiveAnomaly}
          setMapData={setMapData}
          apiResponse={apiResponse}
          setApiResponse={setApiResponse}
        />
      </div>
    </div>
  );
}


// import React, { useState } from 'react';
// import CommandBar from './components/CommandBar';
// import GlobeMap from './components/Map/GlobeMap';
// import Sidebar from './components/Sidebar';

// function App() {
//   const [activeAnomaly, setActiveAnomaly] = useState(null);

//   return (
//     <div className="w-screen h-screen flex flex-col bg-slate-950 text-white font-sans overflow-hidden">
//       <CommandBar />
//       <div className="flex-1 flex overflow-hidden">
//         <div className="w-[70%] h-full relative">
//           <GlobeMap activeTarget={activeAnomaly} />
//         </div>
//         <Sidebar activeAnomaly={activeAnomaly} setActiveAnomaly={setActiveAnomaly} />
//       </div>
//     </div>
//   );
// }

// export default App;