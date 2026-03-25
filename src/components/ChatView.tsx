import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, GraduationCap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ChatView({ session, setSessions }: any) {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [mode, setMode] = useState<'regular' | 'teacher'>('regular');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { 
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); 
  }, [session.messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userMsg = input.trim();
    setInput('');
    setIsTyping(true);

    const newMessages = [...session.messages, { id: Math.random().toString(), role: 'user', content: userMsg }];
    setSessions((prev: any) => prev.map((s: any) => s.id === session.id ? { ...s, messages: newMessages } : s));

    const sysInst = mode === 'teacher' 
      ? "ROLE: English Teacher. Speak ONLY English. Correct the user's grammar if they make a mistake. Be conversational."
      : "ROLE: Neural OS. Responde em Português, de forma detalhada e estruturada com Markdown.";

    try {
      const formatted = [
        { role: 'system', content: sysInst }, 
        ...newMessages.map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
      ];
      
      const res = await fetch(`http://${window.location.hostname}:8000/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: formatted })
      });

      let aiResponse = '';
      const aiMsgId = Math.random().toString();
      
      setSessions((prev: any) => prev.map((s: any) => s.id === session.id ? { 
        ...s, 
        messages: [...newMessages, { id: aiMsgId, role: 'assistant', content: '' }] 
      } : s));

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      
      while (reader) {
        const { value, done } = await reader.read();
        if (done) break;
        aiResponse += decoder.decode(value, { stream: true });
        
        setSessions((prev: any) => prev.map((s: any) => {
          if (s.id === session.id) {
            return {
              ...s,
              messages: s.messages.map((m: any) => m.id === aiMsgId ? { ...m, content: aiResponse } : m)
            };
          }
          return s;
        }));
      }

      if (mode === 'teacher') {
        const utterance = new SpeechSynthesisUtterance(aiResponse.replace(/[*#]/g, ''));
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
      }

    } catch (e) {
      console.error(e);
    } finally { 
      setIsTyping(false); 
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 relative">
      <div className="flex justify-center p-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md z-10 gap-4">
        <button onClick={() => setMode('regular')} className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all ${mode === 'regular' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>
          <Sparkles size={14} /> CHAT REGULAR
        </button>
        <button onClick={() => setMode('teacher')} className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all ${mode === 'teacher' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/20' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>
          <GraduationCap size={14} /> LANGUAGE TEACHER
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar pb-40">
        <div className="max-w-4xl mx-auto space-y-8">
          {session.messages.map((msg: any) => (
            <div key={msg.id} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`relative max-w-[85%] px-6 py-5 shadow-md ${msg.role === 'user' ? 'bg-slate-800 text-slate-200 rounded-2xl rounded-br-sm' : 'bg-black border-l-4 border-blue-500 text-slate-200 rounded-2xl rounded-bl-sm'}`}>
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="text-blue-500 animate-pulse text-sm font-mono">
              {'>'} Analisando com RX 7900 XTX...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-950 via-slate-950 to-transparent pt-10 pb-6 px-6">
        <div className="max-w-4xl mx-auto flex items-end gap-3">
          <textarea 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); handleSend(); } }} 
            placeholder={mode === 'teacher' ? "Pratica o teu Inglês aqui..." : "Mensagem para o Apriel..."} 
            className="flex-1 bg-slate-900 border border-slate-700 text-slate-200 px-4 py-4 rounded-2xl resize-none focus:outline-none focus:border-blue-500 h-[56px]" 
          />
          <button onClick={handleSend} disabled={!input.trim() || isTyping} className="h-[56px] px-6 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl shadow-lg">
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
