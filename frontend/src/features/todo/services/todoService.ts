import { BaseApiClient, ApiResponse } from '../../../lib/api/base';

export interface Todo {
  id: number;
  user_id: string;
  content: string;
  is_completed: boolean;
  period: 'daily' | 'weekly' | 'monthly';
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  content: string;
  period?: 'daily' | 'weekly' | 'monthly';
  is_completed?: boolean;
}

export interface TodoUpdate {
  content?: string;
  period?: 'daily' | 'weekly' | 'monthly';
  is_completed?: boolean;
}

class TodoService extends BaseApiClient {
  async getTodos(period?: 'daily' | 'weekly' | 'monthly'): Promise<ApiResponse<Todo[]>> {
    const params = new URLSearchParams();
    if (period) {
      params.append('period', period);
    }
    const queryString = params.toString();
    return this.request<Todo[]>(`/todos${queryString ? `?${queryString}` : ''}`);
  }

  async createTodo(data: TodoCreate): Promise<ApiResponse<Todo>> {
    return this.request<Todo>('/todos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTodo(id: number, data: TodoUpdate): Promise<ApiResponse<Todo>> {
    return this.request<Todo>(`/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteTodo(id: number): Promise<ApiResponse<void>> {
    return this.request<void>(`/todos/${id}`, {
      method: 'DELETE',
    });
  }
}

export const todoService = new TodoService();
