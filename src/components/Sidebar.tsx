import { Activity, MessageSquare, Trello, Plus, Trash2, CheckSquare, Square } from 'lucide-react';
import { ChatSession, Todo } from '../types';
import LiveMonitor from './LiveMonitor';

interface SidebarProps {
  activeView: 'chat' | 'kanban';
  setActiveView: (view: 'chat' | 'kanban') => void;
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

  const toggleTodo = (id: string) => {
    setTodos(todos.map(t => t.id === id ? { ...t, done: !t.done } : t));
  };

  const deleteTodo = (id: string) => {
    setTodos(todos.filter(t => t.id !== id));
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
        </div>
      </div>

      <div className="px-6 py-4 border-t border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Regras & Tarefas</h2>
        </div>
        <input 
          type="text" 
          placeholder="Adicionar tarefa... (Enter)" 
          onKeyDown={handleAddTodo}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 mb-3 transition-all"
        />
        <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar pr-1">
          {todos.length === 0 && <p className="text-xs text-slate-600 italic">Nenhuma regra ativa.</p>}
          {todos.map(todo => (
            <div key={todo.id} className="flex items-start gap-2 group">
              <button onClick={() => toggleTodo(todo.id)} className="mt-0.5 text-slate-500 hover:text-indigo-400 transition-colors">
                {todo.done ? <CheckSquare className="w-4 h-4 text-emerald-500" /> : <Square className="w-4 h-4" />}
              </button>
              <span className={`text-sm flex-1 ${todo.done ? 'text-slate-600 line-through' : 'text-slate-300'}`}>
                {todo.task}
              </span>
              <button onClick={() => deleteTodo(todo.id)} className="opacity-0 group-hover:opacity-100 text-slate-600 hover:text-red-400 transition-all">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
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
              onClick={() => setCurrentSessionId(session.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-all ${currentSessionId === session.id ? 'bg-slate-800 text-slate-200 font-medium' : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-300'}`}
            >
              {session.title}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
