export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  attachments?: { name: string }[];
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  lastUpdate: string;
}

export interface Todo {
  id: string;
  task: string;
  done: boolean;
}

export type TaskStatus = 'todo' | 'doing' | 'done';

export interface Sprint {
  id: string;
  name: string;
  createdAt: number;
}

export interface KanbanTask {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  sprintIds: string[];
  createdAt: number;
  order: number;
  movedTo?: { fromSprintId: string; toSprintName: string; date: number }[];
}
