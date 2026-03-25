import { useState, useEffect } from 'react';
import { DragDropContext } from '@hello-pangea/dnd';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import KanbanView from './components/KanbanView';
import LinkedinView from './components/LinkedinView';
import { ChatSession, Todo, KanbanTask, Sprint } from './types';

export default function App() {
  const [activeView, setActiveView] = useState<'chat' | 'kanban' | 'linkedin'>('chat');
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState('default');
  const [todos, setTodos] = useState<Todo[]>([]);
  const [sprints, setSprints] = useState<Sprint[]>([{ id: 'sprint-1', name: 'Sprint 1: MVP', createdAt: Date.now() }]);
  const [activeSprintId, setActiveSprintId] = useState('sprint-1');
  const [tasks, setTasks] = useState<KanbanTask[]>([]);

  // CARREGAR DADOS DO DISCO AO INICIAR
  useEffect(() => {
    const init = async () => {
      try {
        const res = await fetch(`http://${window.location.hostname}:8000/load_chats`);
        const data = await res.json();
        if (data.length > 0) {
          setSessions(data);
          setCurrentSessionId(data[0].id);
        } else {
          setSessions([{ id: 'default', title: 'Sessão Inicial', messages: [], lastUpdate: new Date().toISOString() }]);
        }
      } catch (e) {
        setSessions([{ id: 'default', title: 'Sessão Inicial', messages: [], lastUpdate: new Date().toISOString() }]);
      }
    };
    init();
  }, []);

  // SALVAR CONVERSAS AUTOMATICAMENTE
  useEffect(() => {
    if (sessions.length > 0) {
      fetch(`http://${window.location.hostname}:8000/save_chats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessions)
      });
    }
  }, [sessions]);

  const currentSession = sessions.find(s => s.id === currentSessionId) || sessions[0];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden font-sans">
      <Sidebar activeView={activeView} setActiveView={setActiveView} sessions={sessions} setSessions={setSessions} currentSessionId={currentSessionId} setCurrentSessionId={setCurrentSessionId} todos={todos} setTodos={setTodos} />
      <main className="flex-1 relative flex flex-col min-w-0 overflow-hidden">
        {activeView === 'chat' && currentSession && <ChatView session={currentSession} setSessions={setSessions} todos={todos} tasks={tasks} taskToInsert={null} setTaskToInsert={()=>{}} />}
        {activeView === 'kanban' && <KanbanView tasks={tasks} setTasks={setTasks} sprints={sprints} setSprints={setSprints} activeSprintId={activeSprintId} setActiveSprintId={setActiveSprintId} />}
        {activeView === 'linkedin' && <LinkedinView />}
      </main>
    </div>
  );
}
