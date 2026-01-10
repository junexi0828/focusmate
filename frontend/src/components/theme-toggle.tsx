import { Moon, Sun, Laptop, Sparkles } from "lucide-react";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { useTheme } from "../hooks/useTheme";
import { cn } from "../utils";

interface ThemeToggleProps {
  className?: string;
  align?: "center" | "end" | "start";
  children?: React.ReactNode;
}

export function ThemeToggle({ className, align = "end", children }: ThemeToggleProps) {
  const { setTheme, isFunMode, toggleFunMode } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        {children ? (
          children
        ) : (
          <Button
            variant="outline"
            size="icon"
            className={cn("", className)}
          >
            <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">테마 설정</span>
          </Button>
        )}
      </DropdownMenuTrigger>
      <DropdownMenuContent align={align}>
        <DropdownMenuItem onClick={(e) => {
          e.stopPropagation();
          setTheme("light");
        }}>
          <Sun className="mr-2 h-4 w-4" />
          라이트 (Light)
        </DropdownMenuItem>
        <DropdownMenuItem onClick={(e) => {
          e.stopPropagation();
          setTheme("dark");
        }}>
          <Moon className="mr-2 h-4 w-4" />
          다크 (Dark)
        </DropdownMenuItem>

        <DropdownMenuItem onClick={(e) => {
          e.stopPropagation();
          setTheme("system");
        }}>
          <Laptop className="mr-2 h-4 w-4" />
          시스템 설정 (System)
        </DropdownMenuItem>

        <div className="h-px bg-border my-1" />

        <DropdownMenuItem onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          toggleFunMode();
        }}>
          <Sparkles className={cn("mr-2 h-4 w-4", isFunMode ? "text-purple-500 fill-purple-500" : "text-muted-foreground")} />
          <span>3D 이펙트 {isFunMode ? "(On)" : "(Off)"}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
