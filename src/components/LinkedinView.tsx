import { useState, useRef, useEffect } from 'react';
import { Search, ShieldCheck, ExternalLink, Target, Clock, MapPin, Square } from 'lucide-react';

export default function LinkedinView() {
  const [keyword, setKeyword] = useState('Senior Java');
  const [location, setLocation] = useState('Grande Lisboa');
  const[maxHours, setMaxHours] = useState(72);
  const [jobs, setJobs] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  const stopHunt = async () => {
    try { await fetch(`http://${window.location.hostname}:8000/stop`); } catch (e) {}
    setLoading(false);
    setLogs(prev =>[...prev, "> 🛑 Ordem de paragem enviada..."]);
  };

  const startHunt = async () => {
    setLoading(true); setJobs([]); setLogs(["Iniciando scanner infinito..."]);
    try {
      const response = await fetch(`http://localhost:8000/hunt?keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}&max_hours=${maxHours}`);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        decoder.decode(value).split("\n\n").forEach(line => {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.replace("data: ", ""));
              if (data.log) setLogs(prev =>[...prev, `> ${data.log}`]);
              if (data.job) setJobs(prev => [data.job, ...prev]);
            } catch (e) {}
          }
        });
      }
    } catch (error) { setLogs(prev =>[...prev, "❌ Erro de conexão com o servidor Python."]); }
    setLoading(false);
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-slate-950">
      <div className="max-w-5xl mx-auto space-y-6">
        <header className="mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-sm mb-4">
            <ShieldCheck size={16} /> Anti-Outsourcing AI
          </div>
          <h1 className="text-3xl font-bold text-slate-100">LinkedIn Hunter</h1>
          <p className="text-slate-400">Varredura contínua. Ignora consultoras e vagas sem fit.</p>
        </header>

        <div className="flex flex-wrap gap-4 p-5 bg-slate-900 border border-slate-800 rounded-2xl shadow-lg text-slate-200">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 outline-none focus:border-indigo-500" value={keyword} onChange={e => setKeyword(e.target.value)} />
          </div>
          <div className="relative w-48">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 outline-none focus:border-indigo-500" value={location} onChange={e => setLocation(e.target.value)} />
          </div>
          <div className="relative w-36">
            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input type="number" className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-10 pr-4 outline-none focus:border-indigo-500" value={maxHours} onChange={e => setMaxHours(Number(e.target.value))} />
          </div>
          {loading ? (
            <button onClick={stopHunt} className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 px-6 rounded-xl font-bold flex items-center gap-2 transition-all"><Square size={18} fill="currentColor"/> PARAR</button>
          ) : (
            <button onClick={startHunt} className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg"><Target size={18} /> MINERAR</button>
          )}
        </div>

        <div className="bg-[#0d1117] border border-slate-800 rounded-xl p-4 h-48 overflow-y-auto font-mono text-sm text-emerald-400/80 custom-scrollbar shadow-inner">
          {logs.map((log, i) => <div key={i} className="mb-1">{log}</div>)}
          <div ref={logEndRef} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-10">
          {jobs.map((job, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-1 rounded uppercase font-bold">Cliente Final</span>
                <h3 className="text-lg font-bold mt-3 text-slate-200">{job.company}</h3>
                <p className="text-slate-400 text-sm mt-1">{job.title}</p>
              </div>
              <a href={job.link} target="_blank" className="mt-4 flex items-center justify-center gap-2 w-full bg-slate-950 border border-slate-800 hover:border-emerald-500 hover:text-emerald-400 text-slate-300 py-2.5 rounded-xl transition-all font-bold text-xs uppercase">
                Ver Vaga <ExternalLink size={14} />
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
