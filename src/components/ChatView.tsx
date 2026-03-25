import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Bot, Paperclip, X, Check, Copy, Terminal } from 'lucide-react';
import { ChatSession, Todo, KanbanTask } from '../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Droppable } from '@hello-pangea/dnd';

const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
  const match = /language-(\w+)/.exec(className || '');
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  if (!inline && match) {
    return (
      <div className="my-4 rounded-xl overflow-hidden bg-[#0d1117] border border-slate-800 shadow-sm">
        <div className="flex items-center justify-between px-4 py-2 bg-[#161b22] border-b border-slate-800">
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
            <Terminal className="w-4 h-4" /> {match[1]}
          </div>
          <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200">
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        <div className="p-4 overflow-x-auto custom-scrollbar">
          <code className={className} {...props}>{children}</code>
        </div>
      </div>
    );
  }
  return <code className="bg-slate-800/80 text-blue-300 px-1.5 py-0.5 rounded-md text-sm font-mono" {...props}>{children}</code>;
};

interface ChatViewProps {
  session: ChatSession;
  setSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>;
  todos: Todo[];
  tasks: KanbanTask[];
  taskToInsert: string | null;
  setTaskToInsert: React.Dispatch<React.SetStateAction<string | null>>;
}

export default function ChatView({ session, setSessions, todos, tasks, taskToInsert, setTaskToInsert }: ChatViewProps) {
  const [input, setInput] = useState('');
  const[isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); },[session.messages, isTyping]);

  useEffect(() => {
    if (taskToInsert) {
      setInput(prev => prev + (prev.endsWith(' ') || prev === '' ? '' : ' ') + `#[TASK:${taskToInsert}] `);
      setTaskToInsert(null);
    }
  }, [taskToInsert]);

  const generateTitle = async (msg: string) => msg.substring(0, 25) + '...';

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userMsg = input.trim();
    setInput('');
    setIsTyping(true);

    const newMessages =[...session.messages, { id: Math.random().toString(), role: 'user' as const, content: userMsg }];
    setSessions(prev => prev.map(s => s.id === session.id ? { ...s, messages: newMessages } : s));

    let contextStr = "--- TAREFAS ---\n";
    tasks.forEach(t => contextStr += `[${t.status}]: ${t.title}\n`);
    
    const systemInstruction = `ROLE: Neural OS.\nResponde de forma detalhada e visualmente bem estruturada. Usa SEMPRE formatação Markdown (tabelas, listas, negrito) e faz quebras de linha duplas para separar parágrafos e ideias.\n\n${contextStr}`;

    try {
      const formattedMessages = newMessages.map(m => ({
        role: m.role,
        parts: [{ text: m.content }]
      }));

      // LIGAÇÃO DIRETA AO SERVIDOR PYTHON DO FEDORA
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: formattedMessages, systemInstruction })
      });

      if (!res.ok) throw new Error('Servidor Python não respondeu corretamente.');

      let aiResponse = '';
      const aiMsgId = Math.random().toString();
      setSessions(prev => prev.map(s => s.id === session.id ? { ...s, messages: [...newMessages, { id: aiMsgId, role: 'assistant', content: '' }] } : s));

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      
      if (reader) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          aiResponse += decoder.decode(value, { stream: true });
          setSessions(prev => prev.map(s => {
            if (s.id === session.id) {
              const msgs = [...s.messages];
              msgs[msgs.length - 1].content = aiResponse;
              return { ...s, messages: msgs };
            }
            return s;
          }));
        }
      }

      if (session.messages.length === 0) {
        const title = await generateTitle(userMsg);
        setSessions(prev => prev.map(s => s.id === session.id ? { ...s, title } : s));
      }

    } catch (error) {
      console.error(error);
      setSessions(prev => prev.map(s => s.id === session.id ? { 
        ...s, 
        messages:[...newMessages, { id: Math.random().toString(), role: 'assistant', content: '❌ [ERRO FRONTEND]: O servidor Python (8000) não está ligado. Verifica se o `python src/logic/server.py` está a rodar!' }] 
      } : s));
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 relative">
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar pb-40">
        <div className="max-w-4xl mx-auto space-y-8">
          {session.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 mt-32">
              <Bot className="w-12 h-12 text-blue-400 mb-4" />
              <h2 className="text-xl text-slate-300">Neural OS Iniciado</h2>
            </div>
          ) : (
            session.messages.map((msg) => (
              <div key={msg.id} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`relative max-w-[85%] px-6 py-5 shadow-md ${msg.role === 'user' ? 'bg-slate-800 text-slate-200 rounded-2xl rounded-br-sm' : 'bg-black border-l-4 border-blue-500 text-slate-200 rounded-2xl rounded-bl-sm'}`}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ code: CodeBlock }}>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))
          )}
          {isTyping && <div className="text-blue-500 animate-pulse">A pensar...</div>}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-950 to-transparent pt-10 pb-6 px-6">
        <div className="max-w-4xl mx-auto flex items-end gap-3">
          <textarea
            value={input} onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); handleSend(); } }}
            placeholder="Ctrl + Enter para enviar..."
            className="flex-1 bg-slate-900 border border-slate-700 text-slate-200 px-4 py-4 rounded-2xl resize-none focus:outline-none focus:border-blue-500"
            rows={1} style={{ height: '56px' }}
          />
          <button onClick={handleSend} disabled={!input.trim() || isTyping} className="h-[56px] px-6 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
