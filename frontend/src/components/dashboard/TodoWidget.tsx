import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Trash2, Plus, Calendar, CalendarDays, CalendarRange } from "lucide-react";
import { format } from "date-fns";
import { ko } from "date-fns/locale";

import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { ScrollArea } from "../ui/scroll-area";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { cn } from "../ui/utils";
import { todoService, Todo } from "../../features/todo/services/todoService";
import { toast } from "sonner";

type Period = 'daily' | 'weekly' | 'monthly';

export function TodoWidget() {
  const [period, setPeriod] = useState<Period>('daily');
  const [newTodoContent, setNewTodoContent] = useState("");
  const queryClient = useQueryClient();

  // Queries
  const { data: todos = [], isLoading } = useQuery({
    queryKey: ['todos', period],
    queryFn: async () => {
      const response = await todoService.getTodos(period);
      if (response.status === 'error') throw new Error(response.error?.message);
      return response.data || [];
    },
  });

  // Mutations with Optimistic Updates
  const createMutation = useMutation({
    mutationFn: (content: string) => todoService.createTodo({ content, period }),
    onMutate: async (newContent) => {
      await queryClient.cancelQueries({ queryKey: ['todos', period] });
      const previousTodos = queryClient.getQueryData<Todo[]>(['todos', period]);

      const optimisticTodo: Todo = {
        id: Date.now(), // Temp ID
        user_id: "me",
        content: newContent,
        period,
        is_completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      queryClient.setQueryData<Todo[]>(['todos', period], (old = []) => [...old, optimisticTodo]);
      return { previousTodos };
    },
    onError: (_err, _newTodo, context) => {
      queryClient.setQueryData(['todos', period], context?.previousTodos);
      toast.error("할 일을 추가하지 못했습니다");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', period] });
    },
  });

  const toggleMutation = useMutation({
    mutationFn: (todo: Todo) => todoService.updateTodo(todo.id, { is_completed: !todo.is_completed }),
    onMutate: async (todoToToggle) => {
      await queryClient.cancelQueries({ queryKey: ['todos', period] });
      const previousTodos = queryClient.getQueryData<Todo[]>(['todos', period]);

      queryClient.setQueryData<Todo[]>(['todos', period], (old = []) =>
        old.map(t => t.id === todoToToggle.id ? { ...t, is_completed: !t.is_completed } : t)
      );
      return { previousTodos };
    },
    onError: (_err, _todo, context) => {
      queryClient.setQueryData(['todos', period], context?.previousTodos);
      toast.error("상태를 변경하지 못했습니다");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', period] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => todoService.deleteTodo(id),
    onMutate: async (idToDelete) => {
      await queryClient.cancelQueries({ queryKey: ['todos', period] });
      const previousTodos = queryClient.getQueryData<Todo[]>(['todos', period]);

      queryClient.setQueryData<Todo[]>(['todos', period], (old = []) =>
        old.filter(t => t.id !== idToDelete)
      );
      return { previousTodos };
    },
    onError: (_err, _id, context) => {
      queryClient.setQueryData(['todos', period], context?.previousTodos);
      toast.error("삭제 실패");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos', period] });
    },
  });

  const handleAddTodo = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodoContent.trim()) return;
    createMutation.mutate(newTodoContent);
    setNewTodoContent("");
  };

  const completedCount = todos.filter(t => t.is_completed).length;
  const totalCount = todos.length;

  return (
    <Card className="flex flex-col border-border bg-card h-[420px]">
      <CardHeader className="pb-3 space-y-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <CheckSquareIcon className="w-5 h-5 text-primary" />
            체크리스트
            <Badge variant="secondary" className="ml-2 text-xs font-normal">
              {completedCount}/{totalCount}
            </Badge>
          </CardTitle>
          <div className="flex bg-muted/50 p-1 rounded-lg">
            <TabButton
              active={period === 'daily'}
              onClick={() => setPeriod('daily')}
              label="일간"
            />
            <TabButton
              active={period === 'weekly'}
              onClick={() => setPeriod('weekly')}
              label="주간"
            />
            <TabButton
              active={period === 'monthly'}
              onClick={() => setPeriod('monthly')}
              label="월간"
            />
          </div>
        </div>

        <form onSubmit={handleAddTodo} className="relative">
          <Input
            value={newTodoContent}
            onChange={(e) => setNewTodoContent(e.target.value)}
            placeholder={`${
              period === 'daily' ? '오늘' : period === 'weekly' ? '이번 주' : '이번 달'
            } 할 일을 입력하세요...`}
            className="pr-10"
          />
          <Button
            type="submit"
            size="icon"
            variant="ghost"
            className="absolute right-0 top-0 h-full w-10 text-muted-foreground hover:text-primary"
            disabled={!newTodoContent.trim()}
          >
            <Plus className="w-5 h-5" />
          </Button>
        </form>
      </CardHeader>

      <CardContent className="flex-1 min-h-0 pl-2 pr-4 pb-4">
        {isLoading ? (
            <div className="h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            </div>
        ) : todos.length === 0 ? (
          <EmptyState period={period} />
        ) : (
          <ScrollArea className="h-full pr-4">
            <div className="space-y-2">
              {todos.map((todo) => (
                <div
                  key={todo.id}
                  className={cn(
                    "group flex items-center justify-between p-3 rounded-lg border border-transparent transition-all",
                    todo.is_completed
                      ? "bg-muted/30 hover:bg-muted/50"
                      : "bg-background border-border/50 hover:border-border hover:shadow-sm"
                  )}
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <button
                      onClick={() => toggleMutation.mutate(todo)}
                      className={cn(
                        "w-5 h-5 rounded-md border flex items-center justify-center transition-colors shrink-0",
                        todo.is_completed
                          ? "bg-primary border-primary text-primary-foreground"
                          : "border-muted-foreground/30 hover:border-primary/50"
                      )}
                    >
                      {todo.is_completed && <Check className="w-3.5 h-3.5" />}
                    </button>
                    <div className="flex flex-col min-w-0">
                      <span className={cn(
                        "text-sm truncate transition-all",
                        todo.is_completed ? "text-muted-foreground line-through" : "text-foreground"
                      )}>
                        {todo.content}
                      </span>
                      <span className="text-[10px] text-muted-foreground/50">
                        {format(new Date(todo.created_at), "M월 d일", { locale: ko })}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => deleteMutation.mutate(todo.id)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}

function TabButton({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "px-3 py-1 text-xs font-medium rounded-md transition-colors",
        active
          ? "bg-background text-foreground shadow-sm"
          : "text-muted-foreground hover:text-foreground hover:bg-background/50"
      )}
    >
      {label}
    </button>
  );
}

// Custom CheckSquare icon component since lucide-react might not export it directly as CheckSquareIcon in this version
function CheckSquareIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="m9 11 3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  );
}

function EmptyState({ period }: { period: Period }) {
    const message = period === 'daily' ? "오늘 할 일이 없네요" : period === 'weekly' ? "이번 주 할 일이 없네요" : "이번 달 할 일이 없네요";
  return (
    <div className="h-full flex flex-col items-center justify-center text-center p-4 text-muted-foreground/50">
      <div className="w-12 h-12 rounded-full bg-muted/20 flex items-center justify-center mb-3">
        {period === 'daily' ? <Calendar className="w-6 h-6 opacity-40" /> :
         period === 'weekly' ? <CalendarDays className="w-6 h-6 opacity-40" /> :
         <CalendarRange className="w-6 h-6 opacity-40" />}
      </div>
      <p className="text-sm">{message}</p>
    </div>
  );
}
