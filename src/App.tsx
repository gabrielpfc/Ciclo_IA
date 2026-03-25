import { useState, useEffect } from 'react';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import Sidebar from './components/Sidebar';
import ChatView from './components/ChatView';
import KanbanView from './components/KanbanView';
import LinkedinView from './components/LinkedinView';
import { ChatSession, Todo, KanbanTask, Sprint } from './types';

export default function App() {
  const [activeView, setActiveView] = useState<'chat' | 'kanban' | 'linkedin'>('chat');
  const [sessions, setSessions] = useState<ChatSession[]>([
    { id: 'default', title: 'Sessão Inicial', messages: [], lastUpdate: new Date().toISOString() }
  ]);
  const [currentSessionId, setCurrentSessionId] = useState('default');
  const [todos, setTodos] = useState<Todo[]>([]);
  
  const [sprints, setSprints] = useState<Sprint[]>([
    { id: 'sprint-1', name: 'Sprint 1: MVP', createdAt: Date.now() }
  ]);
  const [activeSprintId, setActiveSprintId] = useState('sprint-1');
  
  const [tasks, setTasks] = useState<KanbanTask[]>([
    { id: '1', title: 'Refatorar UI/UX', status: 'doing', description: 'Melhorar a interface do Neural OS', sprintIds: ['sprint-1'], createdAt: Date.now(), order: 0 },
    { id: '2', title: 'Integrar Gemini', status: 'todo', description: 'Substituir Ollama por Gemini API', sprintIds: ['sprint-1'], createdAt: Date.now(), order: 1 }
  ]);

  const [taskToInsert, setTaskToInsert] = useState<string | null>(null);

  useEffect(() => {
    const syncData = async () => {
      try {
        await fetch(`http://${window.location.hostname}:8000/sync_kanban`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sprints, tasks })
        });
      } catch (e) {
        // Silent error handling
      }
    };
    const timeoutId = setTimeout(syncData, 1000);
    return () => clearTimeout(timeoutId);
  }, [sprints, tasks]);

  const currentSession = sessions.find(s => s.id === currentSessionId) || sessions[0];

  const onDragEnd = (result: DropResult) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;

    if (destination.droppableId === 'chat-input') {
      setTaskToInsert(draggableId);
      setActiveView('chat');
      return;
    }

    if (['todo', 'doing', 'done'].includes(destination.droppableId)) {
      const destStatus = destination.droppableId as KanbanTask['status'];
      
      setTasks(prev => {
        const newTasks = [...prev];
        const taskIndex = newTasks.findIndex(t => t.id === draggableId);
        if (taskIndex === -1) return prev;

        const [task] = newTasks.splice(taskIndex, 1);
        task.status = destStatus;

        const isTaskInView = (t: KanbanTask) => t.status === destStatus && (activeSprintId ? t.sprintIds.includes(activeSprintId) : true);
        
        const destTasks = newTasks.filter(isTaskInView).sort((a, b) => (a.order || 0) - (b.order || 0));
        destTasks.splice(destination.index, 0, task);

        destTasks.forEach((t, i) => { t.order = i; });

        const otherTasks = newTasks.filter(t => !isTaskInView(t));
        return [...otherTasks, ...destTasks];
      });
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden font-sans selection:bg-indigo-500/30">
        <Sidebar 
          activeView={activeView} 
          setActiveView={setActiveView}
          sessions={sessions}
          setSessions={setSessions}
          currentSessionId={currentSessionId}
          setCurrentSessionId={setCurrentSessionId}
          todos={todos}
          setTodos={setTodos}
        />
        <main className="flex-1 relative flex flex-col min-w-0 overflow-hidden">
          {activeView === 'chat' ? (
            <ChatView 
              session={currentSession} 
              setSessions={setSessions} 
              todos={todos}
              tasks={tasks}
              taskToInsert={taskToInsert}
              setTaskToInsert={setTaskToInsert}
            />
          ) : (
            <KanbanView 
              tasks={tasks} 
              setTasks={setTasks} 
              sprints={sprints}
              setSprints={setSprints}
              activeSprintId={activeSprintId}
              setActiveSprintId={setActiveSprintId}
            />
          )}
          {activeView === 'linkedin' && <LinkedinView />}

        </main>
      </div>
    </DragDropContext>
  );
}
