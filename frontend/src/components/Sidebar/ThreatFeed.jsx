export default function ThreatFeed({ onIntercept }) {
  return (
    <div className="space-y-6 w-full">
      <h2 className="text-sm font-bold text-gray-400 tracking-widest border-b border-gray-800 pb-2">ACTIVE ANOMALIES</h2>
      <div 
        onClick={onIntercept}
        className="p-4 bg-gray-900 border border-gray-800 hover:border-blue-500 hover:bg-blue-950/20 cursor-pointer transition-all rounded"
      >
        <div className="flex justify-between items-start mb-2">
          <span className="text-red-500 font-bold text-sm bg-red-950/50 px-2 py-1 rounded border border-red-900">PROBABLE SPILL</span>
          <span className="text-xs text-gray-500 font-mono">18.75°N, 72.60°E</span>
        </div>
        <p className="text-gray-300 font-mono text-sm mt-3">Target: UNKNOWN_DARK_FLEET</p>
        <p className="text-gray-500 text-xs mt-1 italic">Click to initiate tactical zoom...</p>
      </div>
    </div>
  );
}