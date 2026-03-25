import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Bot, User, Paperclip, X, Check, Copy, Terminal } from 'lucide-react';
import { ChatSession, Todo, KanbanTask } from '../types';
import ReactMarkdown from 'react-markdown';
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
            <Terminal className="w-4 h-4" />
            {match[1]}
          </div>
          <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors">
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        <div className="p-4 overflow-x-auto custom-scrollbar">
          <code className={className} {...props}>
            {children}
          </code>
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
  const [isTyping, setIsTyping] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [attachments, setAttachments] = useState<{name: string, data: string, mimeType: string}[]>([]);
  
  const [mentionState, setMentionState] = useState<{ active: boolean; filter: string; index: number }>({ active: false, filter: '', index: 0 });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session.messages, isTyping]);

  useEffect(() => {
    if (taskToInsert) {
      setInput(prev => prev + (prev.endsWith(' ') || prev === '' ? '' : ' ') + `#[TASK:${taskToInsert}] `);
      setTaskToInsert(null);
    }
  }, [taskToInsert, setTaskToInsert]);

  const mentionsList = [
    ...tasks.map(t => ({ type: 'TASK', id: t.id, display: `✅ TSK-${t.id.substring(0,4).toUpperCase()}: ${t.title}` })),
    { type: 'SPRINT', id: 'sprint-1', display: `📅 Sprint 1: MVP` }
  ];
  
  const filteredMentions = mentionsList.filter(m => m.display.toLowerCase().includes(mentionState.filter.toLowerCase()));

  const insertMention = (mention: any) => {
    if (!textareaRef.current) return;
    const cursor = textareaRef.current.selectionStart;
    const textBefore = input.substring(0, cursor);
    const textAfter = input.substring(cursor);
    const hashIndex = textBefore.lastIndexOf('#');
    
    const newValue = input.substring(0, hashIndex) + `#[${mention.type}:${mention.id}] ` + textAfter;
    setInput(newValue);
    setMentionState({ active: false, filter: '', index: 0 });
    textareaRef.current.focus();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setInput(val);
    
    const cursor = e.target.selectionStart;
    const textBefore = val.substring(0, cursor);
    const hashIndex = textBefore.lastIndexOf('#');
    
    if (hashIndex !== -1) {
      const textAfterHash = textBefore.substring(hashIndex + 1);
      if (!/\s/.test(textAfterHash)) {
        setMentionState({ active: true, filter: textAfterHash, index: 0 });
        return;
      }
    }
    setMentionState({ active: false, filter: '', index: 0 });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (mentionState.active) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setMentionState(prev => ({ ...prev, index: (prev.index + 1) % filteredMentions.length }));
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setMentionState(prev => ({ ...prev, index: (prev.index - 1 + filteredMentions.length) % filteredMentions.length }));
        return;
      }
      if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredMentions[mentionState.index]) {
          insertMention(filteredMentions[mentionState.index]);
        }
        return;
      }
      if (e.key === 'Escape') {
        setMentionState({ active: false, filter: '', index: 0 });
        return;
      }
    }

    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      const data = base64.split(',')[1];
      setAttachments(prev => [...prev, { name: file.name, data, mimeType: file.type }]);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
    } else {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'pt-PT';
        recognition.interimResults = false;
        recognition.onstart = () => setIsRecording(true);
        recognition.onresult = (e: any) => {
          const transcript = e.results[0][0].transcript;
          setInput(prev => prev + (prev ? ' ' : '') + transcript);
          setIsVoiceMode(true);
        };
        recognition.onend = () => setIsRecording(false);
        recognition.start();
      } else {
        alert('Reconhecimento de voz não suportado neste browser.');
      }
    }
  };

  const generateTitle = async (msg: string) => msg.substring(0, 20) + '...';

  const handleSend = async () => {
    if ((!input.trim() && attachments.length === 0) || isTyping) return;

    const userMsg = input.trim();
    setInput('');
    setIsTyping(true);
    setMentionState({ active: false, filter: '', index: 0 });

    const newMessages = [...session.messages, { 
      id: Math.random().toString(), 
      role: 'user' as const, 
      content: userMsg,
      attachments: attachments.map(a => ({ name: a.name }))
    }];
    
    setSessions(prev => prev.map(s => s.id === session.id ? { ...s, messages: newMessages } : s));

    let enrichedPrompt = userMsg;
    enrichedPrompt = enrichedPrompt.replace(/#\[TASK:([^\]]+)\]/g, (match, id) => {
      const task = tasks.find(t => t.id === id);
      if (task) {
        return `\n[CONTEXTO TAREFA: ${task.title} | Status: ${task.status} | Desc: ${task.description || ''}]\n`;
      }
      return match;
    });
    enrichedPrompt = enrichedPrompt.replace(/#\[SPRINT:([^\]]+)\]/g, (match, id) => {
      return `\n[CONTEXTO SPRINT: ${id}]\n`;
    });

    let contextStr = "--- FATOS CONHECIDOS ---\n";
    todos.forEach(t => {
      contextStr += `- TAREFA/REGRA: ${t.task} (Concluída: ${t.done})\n`;
    });
    contextStr += "\n--- ESTADO DO KANBAN ---\n";
    tasks.forEach(t => {
      contextStr += `[${t.status.toUpperCase()}]: ${t.title}\n`;
    });
    
    const systemInstruction = isVoiceMode 
      ? `ROLE: English Tutor. Speak English. You are helping the user practice English. Respond naturally and conversationally in English.\n\n${contextStr}`
      : `ROLE: Neural OS. Responde em Português de Portugal. És um assistente avançado.\n\n${contextStr}`;

    try {
      const formattedMessages = newMessages.map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }]
      }));

      const lastMsgParts: any[] = [{ text: enrichedPrompt }];
      attachments.forEach(att => {
        lastMsgParts.push({
          inlineData: {
            data: att.data,
            mimeType: att.mimeType
          }
        });
      });
      formattedMessages[formattedMessages.length - 1].parts = lastMsgParts;

      setAttachments([]);

      const responseStream = await ai.models.generateContentStream({
        model: 'gemini-3.1-pro-preview',
        contents: formattedMessages,
        config: { systemInstruction }
      });

      let aiResponse = '';
      const aiMsgId = Math.random().toString();
      
      setSessions(prev => prev.map(s => s.id === session.id ? { 
        ...s, 
        messages: [...newMessages, { id: aiMsgId, role: 'assistant', content: '' }] 
      } : s));

      for await (const chunk of responseStream) {
        aiResponse += chunk.text;
        setSessions(prev => prev.map(s => {
          if (s.id === session.id) {
            const msgs = [...s.messages];
            const lastIdx = msgs.length - 1;
            if (msgs[lastIdx].id === aiMsgId) {
              msgs[lastIdx] = { ...msgs[lastIdx], content: aiResponse };
            }
            return { ...s, messages: msgs };
          }
          return s;
        }));
      }

      if (isVoiceMode) {
        const utterance = new SpeechSynthesisUtterance(aiResponse);
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
        setIsVoiceMode(false);
      }

      if (session.messages.length === 0) {
        const title = await generateTitle(userMsg);
        setSessions(prev => prev.map(s => s.id === session.id ? { ...s, title } : s));
      }

    } catch (error) {
      console.error(error);
      setSessions(prev => prev.map(s => s.id === session.id ? { 
        ...s, 
        messages: [...newMessages, { id: Math.random().toString(), role: 'assistant', content: '❌ [ERRO FRONTEND]: A ligação ao backend (Porto 8000) falhou. Verifica o terminal do Python ou o ficheiro neural_os.log!' }] 
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
              <div className="w-16 h-16 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-4 border border-blue-500/20">
                <Bot className="w-8 h-8 text-blue-400" />
              </div>
              <h2 className="text-xl font-medium text-slate-300 mb-2">Neural OS Iniciado</h2>
              <p className="text-sm">Pressiona Ctrl + Enter para enviar. Usa # para mencionar tarefas.</p>
            </div>
          ) : (
            session.messages.map((msg) => (
              <div key={msg.id} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`relative max-w-[85%] px-6 py-5 shadow-md ${
                  msg.role === 'user'
                    ? 'bg-slate-800 text-slate-200 rounded-2xl rounded-br-sm'
                    : 'bg-black border-l-4 border-blue-500 text-slate-200 rounded-2xl rounded-bl-sm'
                }`}>
                  {msg.attachments && msg.attachments.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-3">
                      {msg.attachments.map((att, i) => (
                        <div key={i} className="flex items-center gap-1.5 bg-slate-900/50 px-3 py-1.5 rounded-lg text-xs border border-slate-700">
                          <Paperclip className="w-3.5 h-3.5 text-blue-400" />
                          <span className="truncate max-w-[150px]">{att.name}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent">
                    <ReactMarkdown components={{ code: CodeBlock }}>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          {isTyping && (
            <div className="flex w-full justify-start">
              <div className="px-6 py-5 rounded-2xl rounded-bl-sm bg-black border-l-4 border-blue-500 flex items-center gap-2 shadow-md">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent pt-10 pb-6 px-6">
        <div className="max-w-4xl mx-auto relative">
          
          {mentionState.active && filteredMentions.length > 0 && (
            <div className="absolute bottom-full mb-2 left-0 w-80 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl overflow-hidden z-50">
              <div className="max-h-60 overflow-y-auto custom-scrollbar py-1">
                {filteredMentions.map((m, idx) => (
                  <button
                    key={m.id}
                    onClick={() => insertMention(m)}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center gap-2 ${
                      idx === mentionState.index ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {m.display}
                  </button>
                ))}
              </div>
            </div>
          )}

          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {attachments.map((att, i) => (
                <div key={i} className="flex items-center gap-2 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-lg text-sm text-slate-300">
                  <Paperclip className="w-4 h-4 text-blue-400" />
                  <span className="truncate max-w-[200px]">{att.name}</span>
                  <button onClick={() => setAttachments(prev => prev.filter((_, idx) => idx !== i))} className="hover:text-red-400 ml-1">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-end gap-3">
            <Droppable droppableId="chat-input">
              {(provided, snapshot) => (
                <div 
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`relative flex-1 bg-slate-900 border rounded-2xl transition-all shadow-lg flex items-end ${snapshot.isDraggingOver ? 'border-indigo-500 ring-1 ring-indigo-500 bg-indigo-500/10' : 'border-slate-700 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500'}`}
                >
                  
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFileChange} 
                    className="hidden" 
                    multiple 
                  />
                  
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="p-3 text-slate-400 hover:text-blue-400 transition-colors mb-1 ml-1 rounded-xl hover:bg-slate-800"
                    title="Anexar ficheiro"
                  >
                    <Paperclip className="w-5 h-5" />
                  </button>

                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Ctrl + Enter para enviar | # para tarefas..."
                    className="flex-1 bg-transparent text-slate-200 placeholder-slate-500 px-2 py-4 max-h-60 min-h-[56px] resize-none focus:outline-none custom-scrollbar leading-relaxed"
                    rows={1}
                    style={{ height: 'auto' }}
                  />
                  
                  <button 
                    onClick={toggleRecording}
                    className={`p-3 transition-colors mb-1 mr-1 rounded-xl ${isRecording ? 'text-red-400 bg-red-400/10 animate-pulse' : 'text-slate-400 hover:text-blue-400 hover:bg-slate-800'}`}
                    title="Modo Voz (Inglês)"
                  >
                    <Mic className="w-5 h-5" />
                  </button>
                  {provided.placeholder}
                </div>
              )}
            </Droppable>

            <button 
              onClick={handleSend}
              disabled={(!input.trim() && attachments.length === 0) || isTyping}
              className="h-[56px] px-6 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-2xl font-medium transition-all flex items-center justify-center shadow-lg"
              title="Enviar (Ctrl + Enter)"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
