import { useState, useRef, useEffect } from 'react';
import { ExternalLink, Target, Square, MousePointer2, Pause, Play, MessageSquareReply, Copy, Check, Trash2, Search } from 'lucide-react';

export default function LinkedinView() {
  const [keyword, setKeyword] = useState('Senior Java');
  const [location, setLocation] = useState('Lisboa, Portugal');
  const [enforceLocation, setEnforceLocation] = useState(true);
  const[jobs, setJobs] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [paused, setPaused] = useState(false);
  const [stats, setStats] = useState({ analyzed: 0, approved: 0 });
  const [history, setHistory] = useState<any>({});
  const logEndRef = useRef<HTMLDivElement>(null);

  const [replies, setReplies] = useState<any[]>([]);
  const [msgLogs, setMsgLogs] = useState<string[]>([]);
  const[scanning, setScanning] = useState(false);
  const [copiedId, setCopiedId] = useState<number | null>(null);

  useEffect(() => { 
    fetch('http://127.0.0.1:8000/get_history').then(r => r.json()).then(setHistory);
    fetch('http://127.0.0.1:8000/get_mined_jobs').then(r => r.json()).then(setJobs);
  },[]);

  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }); },[logs, msgLogs]);

  const togglePause = async () => {
    const endpoint = paused ? 'resume' : 'pause';
    await fetch(`http://127.0.0.1:8000/${endpoint}`);
    setPaused(!paused);
  };

  const handleTrackClick = async (link: string) => {
    const res = await fetch('http://127.0.0.1:8000/track_click', { method: 'POST', body: JSON.stringify({ link }) });
    const data = await res.json();
    setHistory({ ...history, [link]: data.count });
    window.open(link, '_blank');
  };

  const clearJobs = async () => {
    await fetch('http://127.0.0.1:8000/clear_mined_jobs');
    setJobs([]);
    setLogs(prev =>[...prev, "🧹 Vagas limpas."]);
  };

  const stopHunt = async () => {
    setLoading(false); setPaused(false);
    await fetch('http://127.0.0.1:8000/stop');
  };

  const startHunt = async () => {
    setLoading(true); setPaused(false); setLogs([]);
    try {
      const response = await fetch(`http://127.0.0.1:8000/hunt?keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}&max_hours=72&enforce_location=${enforceLocation}`);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        decoder.decode(value).split("\n\n").forEach(line => {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.replace("data: ", ""));
            if (data.log) setLogs(prev =>[...prev, `> ${data.log}`]);
            if (data.job) setJobs(prev => {
                if (prev.find(j => j.link === data.job.link)) return prev;
                return[data.job, ...prev];
            });
            if (data.stats) setStats(data.stats);
          }
        });
      }
    } catch (e) {}
    setLoading(false);
  };

  const stopScan = async () => {
    setScanning(false);
    await fetch('http://127.0.0.1:8000/stop_messages');
  };

  const startMessageScan = async () => {
    setScanning(true); setMsgLogs([]);
    try {
      const response = await fetch(`http://127.0.0.1:8000/scan_messages`);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        decoder.decode(value).split("\n\n").forEach(line => {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.replace("data: ", ""));
            if (data.log) setMsgLogs(prev =>[...prev, `> ${data.log}`]);
            if (data.type === "message_reply") setReplies(prev => [data.data, ...prev]);
          }
        });
      }
    } catch (e) {}
    setScanning(false);
  };

  const copyReply = (text: string, id: number) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex h-full bg-slate-950 overflow-hidden">
      
      <div className="w-1/3 border-r border-slate-800 flex flex-col p-6 overflow-y-auto custom-scrollbar bg-slate-950/50">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2 mb-2"><MessageSquareReply className="text-emerald-500" /> Auto Responder</h2>
        <div className="text-xs text-slate-400 mb-6">O bot varre as conversas dos últimos 30 dias e gera drafts.</div>
        
        <div className="flex gap-2 mb-4">
          {scanning ? (
            <button onClick={stopScan} className="flex-1 bg-red-600 text-white py-2.5 rounded-xl font-bold text-xs transition-all flex justify-center items-center gap-2"><Square size={14} fill="currentColor"/> PARAR SCANNER</button>
          ) : (
            <button onClick={startMessageScan} className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white py-2.5 rounded-xl font-bold text-xs transition-all flex justify-center items-center gap-2"><Search size={14}/> ESCANEAR MENSAGENS</button>
          )}
          <button onClick={() => setReplies([])} className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2.5 rounded-xl transition-all" title="Limpar Sugestões"><Trash2 size={16} /></button>
        </div>

        {msgLogs.length > 0 && (
            <div className="bg-black/40 border border-slate-800 rounded-xl p-3 h-24 overflow-y-auto font-mono text-[10px] text-emerald-400 custom-scrollbar mb-4">{msgLogs.map((log, i) => <div key={i}>{log}</div>)}</div>
        )}

        <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4 pr-2">
          {replies.map((reply, idx) => (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg border-l-2 border-l-emerald-500">
              <h3 className="font-bold text-slate-200 text-sm mb-2">👤 {reply.name}</h3>
              <p className="text-xs text-slate-400 italic bg-slate-950 p-2 rounded-lg mb-3">"{reply.message}"</p>
              <div className="relative">
                <textarea readOnly value={reply.reply} className="w-full h-24 bg-slate-800 border border-emerald-500/30 rounded-xl p-3 text-emerald-100 text-sm outline-none resize-none" />
                <button onClick={() => copyReply(reply.reply, idx)} className="absolute bottom-2 right-2 bg-slate-950 p-1.5 rounded-lg text-emerald-400 hover:bg-slate-900">{copiedId === idx ? <Check size={16} /> : <Copy size={16} />}</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="w-2/3 flex flex-col p-6 overflow-y-auto custom-scrollbar">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3"><Target className="text-indigo-500" /> LinkedIn Hunter</h1>
          <div className="flex gap-4 bg-slate-900 p-3 rounded-xl border border-slate-800">
            <div className="text-center px-4"><div className="text-[10px] text-slate-500 uppercase font-black">Analisadas</div><div className="text-xl font-mono text-slate-300">{stats.analyzed}</div></div>
            <div className="text-center px-4 border-l border-slate-800"><div className="text-[10px] text-emerald-500 uppercase font-black">Aprovadas</div><div className="text-xl font-mono text-emerald-400">{stats.approved}</div></div>
          </div>
        </header>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 mb-6">
          <div className="grid grid-cols-5 gap-4 mb-4">
            <input className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 col-span-2" value={keyword} onChange={e => setKeyword(e.target.value)} />
            <input className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 col-span-1" value={location} onChange={e => setLocation(e.target.value)} />
            
            {loading ? (
              <div className="col-span-2 flex gap-2">
                <button onClick={togglePause} className="flex-1 bg-amber-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 text-sm">{paused ? <Play size={14} /> : <Pause size={14} />} {paused ? "RESUME" : "PAUSE"}</button>
                <button onClick={stopHunt} className="flex-1 bg-red-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 text-sm"><Square size={14} fill="white"/> STOP</button>
              </div>
            ) : (
              <div className="col-span-2 flex gap-2">
                <button onClick={startHunt} className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-colors">MINERAR VAGAS</button>
                <button onClick={clearJobs} className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 rounded-xl transition-all" title="Limpar Vagas"><Trash2 size={18} /></button>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="enforceLoc" checked={enforceLocation} onChange={e => setEnforceLocation(e.target.checked)} className="w-4 h-4 accent-indigo-500 cursor-pointer" />
            <label htmlFor="enforceLoc" className="text-sm text-slate-400 cursor-pointer select-none">📍 Enforce Location Filter (A IA rejeita se for fora da cidade exigida)</label>
          </div>
        </div>

        <div className="bg-black/40 border border-slate-800 rounded-xl p-4 h-32 overflow-y-auto font-mono text-xs text-indigo-400 custom-scrollbar mb-6">
          {logs.map((log, i) => <div key={i}>{log}</div>)}
          <div ref={logEndRef} />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 pb-12">
          {jobs.map((job, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between border-l-4 border-l-indigo-500 shadow-lg hover:border-indigo-400 transition-colors">
              <div className="flex justify-between items-start gap-2">
                <div>
                  <h3 className="text-base font-bold text-slate-200 leading-tight">{job.company}</h3>
                  <p className="text-slate-400 text-sm mt-1">{job.title}</p>
                  {job.location && <p className="text-slate-500 text-xs mt-1">📍 {job.location}</p>}
                </div>
                {history[job.link] && <span className="bg-indigo-500/20 text-indigo-400 text-[10px] px-2 py-1 rounded-md flex items-center gap-1 font-bold shrink-0"><MousePointer2 size={10} /> {history[job.link]} Cliques</span>}
              </div>
              <button onClick={() => handleTrackClick(job.link)} className="mt-4 flex items-center justify-center gap-2 w-full bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 py-2.5 rounded-xl transition-all font-bold text-xs">VER VAGA <ExternalLink size={14} /></button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
