import { useState, useEffect } from 'react';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import KanbanView from './components/KanbanView';
import LinkedinView from './components/LinkedinView';
import { ChatSession, Todo, KanbanTask, Sprint } from './types';

export default function App() {
  const[activeView, setActiveView] = useState<'chat' | 'kanban' | 'linkedin'>('chat');
  const[sessions, setSessions] = useState<ChatSession[]>([
    { id: 'default', title: 'Sessão Inicial', messages: [], lastUpdate: new Date().toISOString() }
  ]);
  const[currentSessionId, setCurrentSessionId] = useState('default');
  const [todos, setTodos] = useState<Todo[]>([]);
  const [sprints, setSprints] = useState<Sprint[]>([{ id: 'sprint-1', name: 'Sprint 1: MVP', createdAt: Date.now() }]);
  const [activeSprintId, setActiveSprintId] = useState('sprint-1');
  const [tasks, setTasks] = useState<KanbanTask[]>([]);
  const[taskToInsert, setTaskToInsert] = useState<string | null>(null);

  useEffect(() => {
    const syncData = async () => {
      try {
        await fetch('http://127.0.0.1:8000/sync_kanban', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sprints, tasks })
        });
      } catch (e) {}
    };
    const timeoutId = setTimeout(syncData, 1000);
    return () => clearTimeout(timeoutId);
  }, [sprints, tasks]);

  const currentSession = sessions.find(s => s.id === currentSessionId) || sessions[0];

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    if (result.destination.droppableId === 'chat-input') {
      setTaskToInsert(result.draggableId);
      setActiveView('chat');
      return;
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden font-sans selection:bg-indigo-500/30">
        <Sidebar 
          activeView={activeView} setActiveView={setActiveView}
          sessions={sessions} setSessions={setSessions}
          currentSessionId={currentSessionId} setCurrentSessionId={setCurrentSessionId}
          todos={todos} setTodos={setTodos}
        />
        <main className="flex-1 relative flex flex-col min-w-0 overflow-hidden">
          {activeView === 'chat' && (
            <ChatView 
              session={currentSession} setSessions={setSessions} todos={todos} tasks={tasks}
              taskToInsert={taskToInsert} setTaskToInsert={setTaskToInsert}
            />
          )}
          {activeView === 'kanban' && (
            <KanbanView 
              tasks={tasks} setTasks={setTasks} sprints={sprints} setSprints={setSprints}
              activeSprintId={activeSprintId} setActiveSprintId={setActiveSprintId}
            />
          )}
          {activeView === 'linkedin' && <LinkedinView />}
        </main>
      </div>
    </DragDropContext>
  );
}
