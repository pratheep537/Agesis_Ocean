export default function Dossier({ onReset }) {
  return (
    <div className="space-y-6 animate-fade-in w-full">
      <button 
        onClick={onReset}
        className="text-blue-500 hover:text-blue-400 text-sm font-mono mb-4 flex items-center gap-2"
      >
        ◄ RESET GLOBAL VIEW
      </button>

      <h2 className="text-lg font-bold text-red-500 border-b border-red-900/50 pb-2">TACTICAL INTERCEPT DOSSIER</h2>
      
      <div className="space-y-4 font-mono text-sm">
        <div className="p-4 bg-gray-900 rounded border border-gray-800">
          <p className="text-gray-400 mb-1">Vessel Identification</p>
          <p className="text-white text-base">MT_ARABIAN_STAR (MMSI: 419000789)</p>
          <p className="text-yellow-500 text-xs mt-2">► EVASION: AIS Transponder Disabled (5h gap)</p>
        </div>

        <div className="p-4 bg-gray-900 rounded border border-gray-800">
          <p className="text-gray-400 mb-2">Mathematical Attribution</p>
          <ul className="space-y-2 text-gray-300">
            <li className="flex justify-between"><span>Physics Engine:</span> <span>Euler-Maruyama</span></li>
            <li className="flex justify-between"><span>Spatial Hash:</span> <span>H3 (Res 8)</span></li>
            <li className="flex justify-between text-green-400 mt-2 pt-2 border-t border-gray-800">
              <span>Confidence:</span> <span>98.4%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}