import { useState, useEffect } from 'react';

export default function LiveMonitor() {
  const [stats, setStats] = useState({ vram: 0, gpu: 0, ram: 0 });
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateStats = () => {
      // Simulate stats since we can't read real hardware from browser
      setStats({
        vram: +(Math.random() * 2 + 6).toFixed(1), // 6-8 GB
        gpu: Math.floor(Math.random() * 30 + 10), // 10-40%
        ram: +(Math.random() * 4 + 12).toFixed(1), // 12-16 GB
      });
      setTime(new Date().toLocaleTimeString());
    };
    
    updateStats();
    const interval = setInterval(updateStats, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-inner">
      <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-800/50">
        <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Live Monitor
        </span>
        <span className="text-xs text-slate-500 font-mono">{time}</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-slate-900 p-2 rounded-lg border border-slate-800/50">
          <div className="text-[10px] text-slate-500 uppercase mb-0.5">VRAM</div>
          <div className="text-slate-200 font-semibold font-mono text-sm">
            {stats.vram} <span className="text-[10px] text-slate-500 font-normal">/ 24GB</span>
          </div>
        </div>
        <div className="bg-slate-900 p-2 rounded-lg border border-slate-800/50">
          <div className="text-[10px] text-slate-500 uppercase mb-0.5">GPU</div>
          <div className="text-emerald-400 font-semibold font-mono text-sm">
            {stats.gpu}%
          </div>
        </div>
        <div className="bg-slate-900 p-2 rounded-lg border border-slate-800/50 col-span-2">
          <div className="text-[10px] text-slate-500 uppercase mb-0.5">RAM</div>
          <div className="text-slate-200 font-semibold font-mono text-sm">
            {stats.ram} <span className="text-[10px] text-slate-500 font-normal">/ 32GB</span>
          </div>
        </div>
      </div>
    </div>
  );
}
