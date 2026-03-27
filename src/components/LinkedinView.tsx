import { useState, useRef, useEffect } from 'react';
import { ExternalLink, Target, Square, MousePointer2, Pause, Play } from 'lucide-react';

export default function LinkedinView() {
  const [keyword, setKeyword] = useState('Senior Java');
  const [location, setLocation] = useState('Portugal');
  const [jobs, setJobs] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [paused, setPaused] = useState(false);
  const [stats, setStats] = useState({ analyzed: 0, approved: 0 });
  const [history, setHistory] = useState<any>({});
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { 
    fetch('http://127.0.0.1:8000/get_history').then(r => r.json()).then(setHistory);
    logEndRef.current?.scrollIntoView({ behavior: "smooth" }); 
  }, [logs]);

  const togglePause = async () => {
    const endpoint = paused ? 'resume' : 'pause';
    await fetch(`http://127.0.0.1:8000/${endpoint}`);
    setPaused(!paused);
    setLogs(prev => [...prev, paused ? "▶️ Retomando..." : "⏸️ Pausado pelo usuário."]);
  };

  const handleTrackClick = async (link: string) => {
    const res = await fetch('http://127.0.0.1:8000/track_click', {
      method: 'POST', body: JSON.stringify({ link })
    });
    const data = await res.json();
    setHistory({ ...history, [link]: data.count });
    window.open(link, '_blank');
  };

  const startHunt = async () => {
    setLoading(true); setPaused(false); setJobs([]); setLogs(["🚀 Iniciando Agente..."]);
    try {
      const response = await fetch(`http://127.0.0.1:8000/hunt?keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}&max_hours=72`);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader!.read();
        if (done) break;
        decoder.decode(value).split("\n\n").forEach(line => {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.replace("data: ", ""));
            if (data.log) setLogs(prev => [...prev, `> ${data.log}`]);
            if (data.job) setJobs(prev => [data.job, ...prev]);
            if (data.stats) setStats(data.stats);
          }
        });
      }
    } catch (e) {}
    setLoading(false);
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-slate-950">
      <div className="max-w-5xl mx-auto space-y-6">
        <header className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3"><Target className="text-indigo-500" /> LinkedIn Hunter</h1>
          <div className="flex gap-4 bg-slate-900 p-3 rounded-xl border border-slate-800">
            <div className="text-center px-4"><div className="text-[10px] text-slate-500 uppercase font-black">Analisadas</div><div className="text-xl font-mono text-slate-300">{stats.analyzed}</div></div>
            <div className="text-center px-4 border-l border-slate-800"><div className="text-[10px] text-emerald-500 uppercase font-black">Aprovadas</div><div className="text-xl font-mono text-emerald-400">{stats.approved}</div></div>
          </div>
        </header>

        <div className="grid grid-cols-4 gap-4 bg-slate-900 p-5 rounded-2xl border border-slate-800">
          <input className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 col-span-1" value={keyword} onChange={e => setKeyword(e.target.value)} />
          <input className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 col-span-1" value={location} onChange={e => setLocation(e.target.value)} />
          
          {loading ? (
            <>
              <button onClick={togglePause} className="bg-amber-600 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                {paused ? <Play size={16} /> : <Pause size={16} />} {paused ? "RESUME" : "PAUSE"}
              </button>
              <button onClick={() => fetch('http://127.0.0.1:8000/stop')} className="bg-red-600 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                <Square size={16} fill="white"/> STOP
              </button>
            </>
          ) : (
            <button onClick={startHunt} className="bg-indigo-600 text-white rounded-xl font-bold col-span-2">MINERAR VAGAS</button>
          )}
        </div>

        <div className="bg-black/40 border border-slate-800 rounded-xl p-4 h-40 overflow-y-auto font-mono text-xs text-indigo-400 custom-scrollbar">
          {logs.map((log, i) => <div key={i}>{log}</div>)}
          <div ref={logEndRef} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-12">
          {jobs.map((job, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between border-l-4 border-l-emerald-500">
              <div>
                <div className="flex justify-between items-start gap-2">
                  <h3 className="text-lg font-bold text-slate-200 leading-tight">{job.company}</h3>
                  {history[job.link] && <span className="bg-indigo-500/20 text-indigo-400 text-[10px] px-2 py-1 rounded-md flex items-center gap-1 font-bold shrink-0"><MousePointer2 size={10} /> {history[job.link]} Cliques</span>}
                </div>
                <p className="text-slate-400 text-sm mt-2">{job.title}</p>
              </div>
              <button onClick={() => handleTrackClick(job.link)} className="mt-4 flex items-center justify-center gap-2 w-full bg-slate-950 border border-slate-800 hover:border-indigo-500 text-slate-300 py-2.5 rounded-xl transition-all font-bold text-xs">VER VAGA <ExternalLink size={14} /></button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
