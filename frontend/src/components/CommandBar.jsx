import React from 'react';

const CommandBar = () => {
  return (
    <div className="h-[60px] w-full bg-slate-950 border-b border-slate-800 flex items-center justify-between px-6 shrink-0 relative z-10">
      <div className="flex items-center gap-4">
        {/* Radar Icon / Logo */}
        <div className="w-8 h-8 rounded-full border border-radar-blue flex items-center justify-center">
          <div className="w-2 h-2 rounded-full bg-radar-blue animate-ping"></div>
        </div>
        <h1 className="text-xl font-bold tracking-widest text-slate-100 uppercase">
          Aegis<span className="text-radar-blue">-Ocean</span>
        </h1>
        <span className="ml-4 px-2 py-0.5 text-[10px] uppercase tracking-wider border border-slate-700 text-slate-400 rounded">
          IPMDA Command
        </span>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded">
          <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse"></div>
          <span className="text-neon-green text-xs font-mono tracking-wider">UPLINK SECURE</span>
        </div>
        <div className="text-slate-500 font-mono text-xs hidden md:block">
          {new Date().toISOString().split('T')[0]} T {new Date().toISOString().split('T')[1].substring(0, 8)} Z
        </div>
      </div>
    </div>
  );
};

export default CommandBar;