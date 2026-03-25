import { Activity, MessageSquare, Trello, Plus, Trash2, CheckSquare, Square, Target } from 'lucide-react';
import { ChatSession, Todo } from '../types';
import LiveMonitor from './LiveMonitor';

interface SidebarProps {
  activeView: 'chat' | 'kanban' | 'linkedin';
  setActiveView: (view: 'chat' | 'kanban' | 'linkedin') => void;
  sessions: ChatSession[];
  setSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>;
  currentSessionId: string;
  setCurrentSessionId: (id: string) => void;
  todos: Todo[];
  setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
}

export default function Sidebar({
  activeView, setActiveView, sessions, setSessions, currentSessionId, setCurrentSessionId, todos, setTodos
}: SidebarProps) {
  
  const handleAddSession = () => {
    const newId = Math.random().toString(36).substring(7);
    setSessions([{ id: newId, title: 'Nova Conversa', messages: [], lastUpdate: new Date().toISOString() }, ...sessions]);
    setCurrentSessionId(newId);
  };

  const handleAddTodo = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
      setTodos([...todos, { id: Math.random().toString(36).substring(7), task: e.currentTarget.value.trim(), done: false }]);
      e.currentTarget.value = '';
    }
  };

  return (
    <div className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col h-full overflow-y-auto custom-scrollbar">
      <div className="p-6">
        <h1 className="text-xl font-bold flex items-center gap-2 text-indigo-400 mb-6">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <Activity className="w-5 h-5" />
          </div>
          Neural OS
        </h1>

        <LiveMonitor />

        <div className="mt-8 space-y-2">
          <button 
            onClick={() => setActiveView('chat')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeView === 'chat' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
          >
            <MessageSquare className="w-5 h-5" />
            <span className="font-medium">Chat Inteligente</span>
          </button>
          
          <button 
            onClick={() => setActiveView('kanban')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeView === 'kanban' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
          >
            <Trello className="w-5 h-5" />
            <span className="font-medium">Kanban Board</span>
          </button>

          <button 
            onClick={() => setActiveView('linkedin')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeView === 'linkedin' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
          >
            <Target className="w-5 h-5" />
            <span className="font-medium">LinkedIn Hunter</span>
          </button>
        </div>
      </div>

      <div className="px-6 py-4 border-t border-slate-800 flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Conversas</h2>
          <button onClick={handleAddSession} className="text-slate-400 hover:text-indigo-400 transition-colors p-1 rounded-md hover:bg-indigo-500/10">
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <div className="space-y-1 overflow-y-auto custom-scrollbar pr-1 flex-1">
          {sessions.map(session => (
            <button
              key={session.id}
              onClick={() => { setCurrentSessionId(session.id); setActiveView('chat'); }}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-all ${currentSessionId === session.id && activeView === 'chat' ? 'bg-slate-800 text-slate-200 font-medium' : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-300'}`}
            >
              {session.title}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
