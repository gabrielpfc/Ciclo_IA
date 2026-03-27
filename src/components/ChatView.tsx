import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, GraduationCap, Mic, Square } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ChatView({ session, setSessions }: any) {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [mode, setMode] = useState<'regular' | 'teacher'>('regular');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [session.messages, isTyping]);

  const cleanTextForTTS = (t: string) => t.replace(/[\*#_~`>]/g, '').replace(/\[(.*?)\]\(.*?\)/g, '$1').trim();

  const handleSend = async (override?: string) => {
    const text = override || input.trim();
    if (!text || isTyping) return;
    if (!override) setInput('');
    setIsTyping(true);

    const newMsgs = [...session.messages, { id: Math.random().toString(), role: 'user', content: text }];
    setSessions((prev: any) => prev.map((s: any) => s.id === session.id ? { ...s, messages: newMsgs } : s));

    // NOMEAR AUTOMATICAMENTE
    if (session.title.includes("Sessão") || session.title === "Conversa") {
        fetch('http://127.0.0.1:8000/generate_title', { method: 'POST', body: JSON.stringify({ prompt: text }) })
        .then(r => r.json()).then(d => {
            setSessions((prev: any) => prev.map((s: any) => s.id === session.id ? { ...s, title: d.title } : s));
        }).catch(() => {});
    }

    const sysInst = mode === 'teacher' 
      ? "You are Apriel, a concise English Tutor. MANDATORY: Max 2 sentences. Correct the user, ask ONE question. No bold." 
      : "Responda em Português de forma curta.";

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMsgs.map(m => ({ role: m.role, parts: [{ text: m.content }] })), systemInstruction: sysInst })
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let aiResponse = '';
      let spokenCount = 0;
      const aiMsgId = Math.random().toString();

      setSessions((prev: any) => prev.map((s: any) => s.id === session.id ? { ...s, messages: [...newMsgs, { id: aiMsgId, role: 'assistant', content: '' }] } : s));

      while (true) {
        const { value, done } = await reader!.read();
        if (done) break;
        aiResponse += decoder.decode(value);
        
        setSessions((prev: any) => prev.map((s: any) => s.id === session.id ? {
          ...s, messages: s.messages.map((m: any) => m.id === aiMsgId ? { ...m, content: aiResponse } : m)
        } : s));

        if (mode === 'teacher') {
          const sentences = aiResponse.match(/[^.!?\n]+[.!?\n]+/g) || [];
          if (sentences.length > spokenCount) {
            fetch('http://127.0.0.1:8000/tts', { method: 'POST', body: JSON.stringify({ text: cleanTextForTTS(sentences[spokenCount]), lang: 'en' }) });
            spokenCount++;
          }
        }
      }
    } catch (e) { console.error(e); } finally { setIsTyping(false); }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950">
      <div className="flex justify-center p-4 border-b border-slate-800 gap-4">
        <button onClick={() => setMode('regular')} className={`px-4 py-2 rounded-full text-xs font-bold transition-all ${mode === 'regular' ? 'bg-blue-600' : 'bg-slate-800'}`}>CHAT REGULAR</button>
        <button onClick={() => setMode('teacher')} className={`px-4 py-2 rounded-full text-xs font-bold transition-all ${mode === 'teacher' ? 'bg-emerald-600' : 'bg-slate-800'}`}>ENGLISH TEACHER</button>
      </div>
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar pb-32">
        <div className="max-w-4xl mx-auto space-y-6">
          {session.messages.map((msg: any) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`p-4 rounded-2xl max-w-[85%] ${msg.role === 'user' ? 'bg-slate-800 text-slate-100' : 'bg-black border-l-4 border-emerald-500 text-slate-100'}`}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="fixed bottom-0 left-80 right-0 p-6 bg-gradient-to-t from-slate-950">
        <div className="max-w-4xl mx-auto flex gap-3">
          <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.ctrlKey && e.key === 'Enter' && handleSend()} className="flex-1 bg-slate-900 border border-slate-700 rounded-xl p-4 h-14 resize-none outline-none focus:border-emerald-500 text-slate-100" placeholder="Type here..." />
          <button onClick={() => handleSend()} className="bg-emerald-600 p-4 rounded-xl"><Send size={20} /></button>
        </div>
      </div>
    </div>
  );
}
