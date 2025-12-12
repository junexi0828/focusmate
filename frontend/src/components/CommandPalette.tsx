import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "./ui/command";
import {
  Home,
  BarChart2,
  Users,
  MessageSquare,
  User,
  LogOut,
} from "lucide-react";
import { authService } from "../features/auth/services/authService";
import { toast } from "sonner";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  const handleLogout = () => {
    authService.logout();
    navigate({ to: "/login" });
    toast.success("로그아웃되었습니다");
  };

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="명령어 또는 검색어를 입력하세요..." />
      <CommandList>
        <CommandEmpty>결과를 찾을 수 없습니다.</CommandEmpty>

        <CommandGroup heading="페이지">
          <CommandItem
            onSelect={() => runCommand(() => navigate({ to: "/" }))}
          >
            <Home className="mr-2 h-4 w-4" />
            <span>홈</span>
            <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <span className="text-xs">G</span>
              <span className="text-xs">H</span>
            </kbd>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => navigate({ to: "/stats" }))}
          >
            <BarChart2 className="mr-2 h-4 w-4" />
            <span>통계</span>
            <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <span className="text-xs">G</span>
              <span className="text-xs">S</span>
            </kbd>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => navigate({ to: "/community" }))}
          >
            <Users className="mr-2 h-4 w-4" />
            <span>커뮤니티</span>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => navigate({ to: "/messages" }))}
          >
            <MessageSquare className="mr-2 h-4 w-4" />
            <span>메시지</span>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => navigate({ to: "/profile" }))}
          >
            <User className="mr-2 h-4 w-4" />
            <span>프로필</span>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="작업">
          <CommandItem onSelect={() => runCommand(handleLogout)}>
            <LogOut className="mr-2 h-4 w-4" />
            <span>로그아웃</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
