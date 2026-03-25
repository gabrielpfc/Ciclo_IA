import { useState, useRef, useEffect, useCallback } from 'react';
import { KanbanTask, Sprint } from '../types';
import { Plus, MoreHorizontal, Calendar, Trash2, Edit2, Copy, CheckSquare, X, AlignLeft, GripVertical, Check } from 'lucide-react';
import { Droppable, Draggable } from '@hello-pangea/dnd';

interface KanbanViewProps {
  tasks: KanbanTask[];
  setTasks: React.Dispatch<React.SetStateAction<KanbanTask[]>>;
  sprints: Sprint[];
  setSprints: React.Dispatch<React.SetStateAction<Sprint[]>>;
  activeSprintId: string | null;
  setActiveSprintId: React.Dispatch<React.SetStateAction<string | null>>;
}

export default function KanbanView({ tasks, setTasks, sprints, setSprints, activeSprintId, setActiveSprintId }: KanbanViewProps) {
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [addingTo, setAddingTo] = useState<'todo' | 'doing' | 'done' | null>(null);
  
  // Selection
  const [selectedTaskIds, setSelectedTaskIds] = useState<Set<string>>(new Set());
  
  // Edit Modal
  const [editingTask, setEditingTask] = useState<KanbanTask | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  
  // Sprint Management
  const [isCreatingSprint, setIsCreatingSprint] = useState(false);
  const [newSprintName, setNewSprintName] = useState('');
  
  // Clipboard for tasks
  const [clipboardTasks, setClipboardTasks] = useState<KanbanTask[]>([]);

  const columns = [
    { id: 'todo', title: 'A Fazer', color: 'bg-slate-800 border-slate-700', headerColor: 'text-slate-200' },
    { id: 'doing', title: 'Em Progresso', color: 'bg-indigo-900/20 border-indigo-800/30', headerColor: 'text-indigo-300' },
    { id: 'done', title: 'Concluído', color: 'bg-emerald-900/20 border-emerald-800/30', headerColor: 'text-emerald-300' }
  ] as const;

  const activeTasks = tasks.filter(t => activeSprintId ? t.sprintIds.includes(activeSprintId) : true)
                           .sort((a, b) => (a.order || 0) - (b.order || 0));

  const handleAddTask = (status: 'todo' | 'doing' | 'done') => {
    if (newTaskTitle.trim()) {
      const newTask: KanbanTask = {
        id: Math.random().toString(36).substring(2, 9),
        title: newTaskTitle.trim(),
        status,
        sprintIds: activeSprintId ? [activeSprintId] : [],
        createdAt: Date.now(),
        order: activeTasks.filter(t => t.status === status).length,
        movedTo: []
      };
      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      setAddingTo(null);
    }
  };

  const handleTaskClick = (e: React.MouseEvent, taskId: string) => {
    if (e.ctrlKey || e.metaKey) {
      const newSelected = new Set(selectedTaskIds);
      if (newSelected.has(taskId)) {
        newSelected.delete(taskId);
      } else {
        newSelected.add(taskId);
      }
      setSelectedTaskIds(newSelected);
    } else {
      setSelectedTaskIds(new Set([taskId]));
    }
  };

  const handleTaskDoubleClick = (task: KanbanTask) => {
    setEditingTask(task);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
  };

  const saveEditedTask = () => {
    if (editingTask && editTitle.trim()) {
      setTasks(tasks.map(t => t.id === editingTask.id ? { ...t, title: editTitle.trim(), description: editDescription.trim() } : t));
      setEditingTask(null);
    }
  };

  const deleteSelectedTasks = () => {
    setTasks(tasks.filter(t => !selectedTaskIds.has(t.id)));
    setSelectedTaskIds(new Set());
  };

  const copySelectedTasks = () => {
    const tasksToCopy = tasks.filter(t => selectedTaskIds.has(t.id));
    setClipboardTasks(tasksToCopy);
  };

  const pasteTasks = () => {
    if (clipboardTasks.length > 0 && activeSprintId) {
      const newTasks = clipboardTasks.map(t => ({
        ...t,
        id: Math.random().toString(36).substring(2, 9),
        sprintIds: [activeSprintId],
        createdAt: Date.now()
      }));
      setTasks([...tasks, ...newTasks]);
    }
  };

  const createSprint = () => {
    if (newSprintName.trim()) {
      const newSprint: Sprint = {
        id: Math.random().toString(36).substring(2, 9),
        name: newSprintName.trim(),
        createdAt: Date.now()
      };
      setSprints([...sprints, newSprint]);
      setActiveSprintId(newSprint.id);
      setNewSprintName('');
      setIsCreatingSprint(false);
    }
  };

  const deleteSprint = (id: string) => {
    setSprints(sprints.filter(s => s.id !== id));
    if (activeSprintId === id) {
      setActiveSprintId(sprints.length > 1 ? sprints.find(s => s.id !== id)?.id || null : null);
    }
    // Remove sprintId from tasks
    setTasks(tasks.map(t => ({
      ...t,
      sprintIds: t.sprintIds.filter(sId => sId !== id)
    })));
  };

  // Keyboard shortcuts for the modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (editingTask) {
        if (e.key === 'Escape') {
          setEditingTask(null);
        } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          saveEditedTask();
        }
      } else {
        if (e.key === 'Delete' && selectedTaskIds.size > 0) {
          deleteSelectedTasks();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'c' && selectedTaskIds.size > 0) {
          copySelectedTasks();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'v' && clipboardTasks.length > 0) {
          pasteTasks();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [editingTask, editTitle, editDescription, selectedTaskIds, clipboardTasks, activeSprintId]);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('pt-PT', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="flex h-full bg-slate-950 overflow-hidden text-slate-200 font-sans">
      
      {/* Sidebar for Sprints */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col z-10">
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Sprints</h2>
          {isCreatingSprint ? (
            <div className="space-y-2">
              <input
                autoFocus
                type="text"
                value={newSprintName}
                onChange={(e) => setNewSprintName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') createSprint();
                  if (e.key === 'Escape') setIsCreatingSprint(false);
                }}
                placeholder="Nome do Sprint..."
                className="w-full bg-slate-950 border border-indigo-500/50 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              />
              <div className="flex gap-2">
                <button onClick={createSprint} className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs py-1.5 rounded-md transition-colors">Criar</button>
                <button onClick={() => setIsCreatingSprint(false)} className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-1.5 rounded-md transition-colors">Cancelar</button>
              </div>
            </div>
          ) : (
            <button 
              onClick={() => setIsCreatingSprint(true)}
              className="w-full flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 rounded-lg text-sm transition-colors border border-slate-700"
            >
              <Plus className="w-4 h-4" />
              Novo Sprint
            </button>
          )}
        </div>
        
        <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
          <button
            onClick={() => setActiveSprintId(null)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeSprintId === null ? 'bg-indigo-600/20 text-indigo-300 font-medium' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
            }`}
          >
            <Calendar className="w-4 h-4" />
            <span className="truncate">Todas as Tarefas</span>
          </button>
          
          {sprints.map(sprint => (
            <div key={sprint.id} className="group flex items-center">
              <button
                onClick={() => setActiveSprintId(sprint.id)}
                className={`flex-1 flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors truncate ${
                  activeSprintId === sprint.id ? 'bg-indigo-600/20 text-indigo-300 font-medium' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <CheckSquare className="w-4 h-4 opacity-70" />
                <span className="truncate">{sprint.name}</span>
              </button>
              <button 
                onClick={() => deleteSprint(sprint.id)}
                className="p-2 text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Eliminar Sprint"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Kanban Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        {/* Header */}
        <div className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/50 backdrop-blur-sm z-10">
          <div>
            <h1 className="text-xl font-bold text-slate-100">
              {activeSprintId ? sprints.find(s => s.id === activeSprintId)?.name : 'Todas as Tarefas'}
            </h1>
            <p className="text-slate-500 text-xs mt-0.5">
              {activeTasks.length} tarefas {activeSprintId ? 'neste sprint' : 'no total'}
            </p>
          </div>
          
          {/* Bulk Actions Toolbar */}
          {selectedTaskIds.size > 0 && (
            <div className="flex items-center gap-2 bg-indigo-900/30 border border-indigo-500/30 px-4 py-1.5 rounded-full">
              <span className="text-xs font-medium text-indigo-300 mr-2">{selectedTaskIds.size} selecionadas</span>
              <button onClick={copySelectedTasks} className="p-1.5 text-indigo-400 hover:text-indigo-200 hover:bg-indigo-500/20 rounded-md transition-colors" title="Copiar (Ctrl+C)">
                <Copy className="w-4 h-4" />
              </button>
              <button onClick={deleteSelectedTasks} className="p-1.5 text-red-400 hover:text-red-200 hover:bg-red-500/20 rounded-md transition-colors" title="Eliminar (Delete)">
                <Trash2 className="w-4 h-4" />
              </button>
              <button onClick={() => setSelectedTaskIds(new Set())} className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-md transition-colors ml-2" title="Limpar Seleção (Esc)">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
          {clipboardTasks.length > 0 && selectedTaskIds.size === 0 && activeSprintId && (
            <button onClick={pasteTasks} className="flex items-center gap-2 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-colors border border-slate-700">
              <Copy className="w-3.5 h-3.5" />
              Colar {clipboardTasks.length} tarefas
            </button>
          )}
        </div>

        {/* Board */}
        <div className="flex-1 p-8 overflow-x-auto custom-scrollbar">
          <div className="flex gap-6 h-full min-w-max items-start">
            {columns.map(col => (
              <div key={col.id} className={`w-80 flex flex-col rounded-2xl border ${col.color} bg-slate-900/40 max-h-full`}>
                <div className="p-4 flex items-center justify-between group/header">
                  <div className="flex items-center gap-2">
                    <h3 className={`font-semibold ${col.headerColor}`}>{col.title}</h3>
                    <span className="text-xs font-medium px-2 py-1 rounded-full bg-slate-950/50 text-slate-400 border border-slate-800/50">
                      {activeTasks.filter(t => t.status === col.id).length}
                    </span>
                  </div>
                  <button 
                    onClick={() => {
                      const colTasks = activeTasks.filter(t => t.status === col.id).map(t => t.id);
                      setSelectedTaskIds(new Set([...selectedTaskIds, ...colTasks]));
                    }}
                    className="text-[10px] uppercase font-bold tracking-wider text-slate-500 hover:text-indigo-400 opacity-0 group-hover/header:opacity-100 transition-opacity"
                    title="Selecionar todas as tarefas desta coluna"
                  >
                    Selecionar Tudo
                  </button>
                </div>
                
                <Droppable droppableId={col.id}>
                  {(provided, snapshot) => (
                    <div 
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`flex-1 p-3 overflow-y-auto custom-scrollbar space-y-3 min-h-[150px] transition-colors ${snapshot.isDraggingOver ? 'bg-slate-800/30' : ''}`}
                    >
                      {activeTasks.filter(t => t.status === col.id).map((task, index) => (
                        <Draggable key={task.id} draggableId={task.id} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              onClick={(e) => handleTaskClick(e, task.id)}
                              onDoubleClick={() => handleTaskDoubleClick(task)}
                              className={`group relative bg-slate-800 border p-4 rounded-xl shadow-sm transition-all ${
                                snapshot.isDragging ? 'shadow-2xl shadow-indigo-500/20 border-indigo-500 rotate-2 z-50' : 
                                selectedTaskIds.has(task.id) ? 'border-indigo-500 ring-1 ring-indigo-500 bg-slate-800/80' : 
                                'border-slate-700 hover:border-slate-500'
                              }`}
                            >
                              <div 
                                {...provided.dragHandleProps}
                                className="absolute top-3 right-3 text-slate-600 opacity-0 group-hover:opacity-100 hover:text-slate-400 cursor-grab active:cursor-grabbing transition-opacity"
                              >
                                <GripVertical className="w-4 h-4" />
                              </div>
                              
                              <div className="pr-6">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-[10px] font-mono text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                                    TSK-{task.id.substring(0,4).toUpperCase()}
                                  </span>
                                  {task.createdAt && (
                                    <span className="text-[10px] text-slate-500">{formatDate(task.createdAt)}</span>
                                  )}
                                </div>
                                <h4 className="text-sm font-medium text-slate-200 leading-snug mb-2">{task.title}</h4>
                                {task.description && (
                                  <div className="flex items-start gap-1.5 text-slate-400">
                                    <AlignLeft className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                                    <p className="text-xs line-clamp-2">{task.description}</p>
                                  </div>
                                )}
                              </div>
                              
                              {/* Selection Indicator */}
                              {selectedTaskIds.has(task.id) && (
                                <div className="absolute top-3 left-3 w-4 h-4 bg-indigo-500 rounded-full flex items-center justify-center shadow-sm">
                                  <Check className="w-3 h-3 text-white" />
                                </div>
                              )}
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}

                      {addingTo === col.id ? (
                        <div className="bg-slate-800 border border-indigo-500/50 p-3 rounded-xl shadow-lg">
                          <input
                            autoFocus
                            type="text"
                            value={newTaskTitle}
                            onChange={(e) => setNewTaskTitle(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleAddTask(col.id);
                              if (e.key === 'Escape') { setAddingTo(null); setNewTaskTitle(''); }
                            }}
                            placeholder="Título da tarefa..."
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 mb-3"
                          />
                          <div className="flex items-center gap-2">
                            <button onClick={() => handleAddTask(col.id)} className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg font-medium transition-colors">
                              Adicionar
                            </button>
                            <button onClick={() => { setAddingTo(null); setNewTaskTitle(''); }} className="text-xs text-slate-400 hover:text-slate-200 px-2 py-1.5">
                              Cancelar
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button 
                          onClick={() => setAddingTo(col.id)}
                          className="w-full py-3 flex items-center justify-center gap-2 text-sm text-slate-500 hover:text-slate-300 hover:bg-slate-800/80 rounded-xl transition-colors border border-dashed border-slate-700 hover:border-slate-500"
                        >
                          <Plus className="w-4 h-4" />
                          Adicionar Tarefa
                        </button>
                      )}
                    </div>
                  )}
                </Droppable>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50">
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2 py-1 rounded-md border border-slate-800">
                  TSK-{editingTask.id.substring(0,4).toUpperCase()}
                </span>
                <h3 className="text-sm font-medium text-slate-300">Editar Tarefa</h3>
              </div>
              <button onClick={() => setEditingTask(null)} className="text-slate-400 hover:text-slate-200 p-1 rounded-md hover:bg-slate-800 transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2 uppercase tracking-wider">Título</label>
                <input
                  autoFocus
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  placeholder="Título da tarefa..."
                />
              </div>
              
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2 uppercase tracking-wider">Descrição</label>
                <textarea
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all custom-scrollbar min-h-[200px] resize-y"
                  placeholder="Adiciona uma descrição mais detalhada..."
                />
              </div>
            </div>
            
            <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between">
              <div className="text-xs text-slate-500 flex items-center gap-4">
                <span><kbd className="bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700 font-mono">Ctrl</kbd> + <kbd className="bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700 font-mono">Enter</kbd> para guardar</span>
                <span><kbd className="bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700 font-mono">Esc</kbd> para cancelar</span>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setEditingTask(null)} className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-slate-100 transition-colors">
                  Cancelar
                </button>
                <button onClick={saveEditedTask} className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition-colors shadow-lg shadow-indigo-500/20">
                  Guardar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
