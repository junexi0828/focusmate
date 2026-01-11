import React, { useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import {
  Home,
  LayoutDashboard,
  BarChart2,
  Users,
  MessageSquare,
  User,
  LogOut,
  Moon,
  Sun,
  ChevronLeft,
  ChevronRight,
  Trophy,
  Heart,
  Settings,
  UserPlus,
} from "lucide-react";
import { authService } from "../features/auth/services/authService";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { cn } from "../utils";
import logoFull from "../assets/logo-full.png";
import darkLogoFull from "../assets/dark-logo-full.png";
import darkLogo from "../assets/dark-logo.png";
import { ThemeToggle } from "./theme-toggle";
import { useTheme } from "../hooks/useTheme";

export function Sidebar() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const user = authService.getCurrentUser();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { theme, setTheme } = useTheme();

  // 실제 읽지 않은 메시지 수 가져오기 (initial load only - WebSocket handles updates)
  const { data: unreadCount = 0 } = useQuery({
    queryKey: ["unreadMessages"],
    queryFn: async () => {
      const { getUnreadMessageCount } = await import("../api/chat");
      return getUnreadMessageCount();
    },
    refetchInterval: false, // Disabled: Chat WebSocket handles real-time updates
    staleTime: 1000 * 60 * 5, // 5 minutes - message count changes infrequently
    retry: 1,
    enabled: !!user && !authService.isTokenExpired(), // Only fetch when user is logged in and token is valid
  });

  const handleLogout = () => {
    authService.logout();
    queryClient.clear();
    navigate({ to: "/login" });
    toast.success("로그아웃되었습니다");
  };

  const getInitials = (name: string) => {
    if (!name) return "U";
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <aside
      className={cn(
        "border-r border-border bg-card/50 backdrop-blur-xl h-screen flex flex-col transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="p-4 flex items-center gap-2 border-b border-border/50 relative">
        {!isCollapsed && (
          <div className="flex items-center justify-center overflow-hidden py-4">
             <img
              src={theme === "dark" ? darkLogoFull : logoFull}
              alt="FocusMate"
              className="h-40 -my-12 object-contain"
            />
          </div>
        )}
        {isCollapsed && (
          <img
            src={logo}
            alt="FocusMate"
            className="h-10 w-10 object-contain"
          />
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={cn(
            "absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full border border-border bg-background shadow-sm flex items-center justify-center hover:bg-accent transition-colors z-10",
            isCollapsed && "right-1"
          )}
          aria-label={isCollapsed ? "사이드바 펼치기" : "사이드바 접기"}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* User Info */}
      {user && !isCollapsed && (
        <div className="p-4 border-b border-border/50">
          <Link
            to="/profile"
            className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-accent transition-colors"
          >
            <Avatar className="w-8 h-8 flex-shrink-0">
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                {getInitials(user.username || user.email)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {user.username || "User"}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {user.email}
              </p>
            </div>
          </Link>
        </div>
      )}

      {user && isCollapsed && (
        <div className="p-4 border-b border-border/50 flex justify-center">
          <Link
            to="/profile"
            className="flex items-center justify-center"
            title={user.username || user.email}
          >
            <Avatar className="w-8 h-8">
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                {getInitials(user.username || user.email)}
              </AvatarFallback>
            </Avatar>
          </Link>
        </div>
      )}

      {/* Login Button for Unauthenticated Users */}
      {!user && !isCollapsed && (
        <div className="p-4 border-b border-border/50">
          <Link
            to="/login"
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium"
          >
            <User size={18} />
            <span>로그인</span>
          </Link>
        </div>
      )}

      {!user && isCollapsed && (
        <div className="p-4 border-b border-border/50 flex justify-center">
          <Link
            to="/login"
            className="flex items-center justify-center w-10 h-10 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            title="로그인"
          >
            <User size={18} />
          </Link>
        </div>
      )}

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <NavItem
          to="/"
          icon={<Home size={18} />}
          label="홈"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/dashboard"
          icon={<LayoutDashboard size={18} />}
          label="대시보드"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/stats"
          icon={<BarChart2 size={18} />}
          label="통계"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/community"
          icon={<Users size={18} />}
          label="커뮤니티"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/ranking"
          icon={<Trophy size={18} />}
          label="랭킹전"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/matching"
          icon={<Heart size={18} />}
          label="핑크캠퍼스"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/messages"
          icon={<MessageSquare size={18} />}
          label="메시지"
          badge={unreadCount > 0 ? unreadCount : undefined}
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/friends"
          icon={<UserPlus size={18} />}
          label="친구"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/profile"
          icon={<User size={18} />}
          label="프로필"
          isCollapsed={isCollapsed}
        />
        <NavItem
          to="/settings"
          icon={<Settings size={18} />}
          label="설정"
          isCollapsed={isCollapsed}
        />
      </nav>

      <div className="p-4 border-t border-border/50 space-y-2">
        {/* Theme Toggle - Dual Behavior */}
        <div
          className={cn(
            "w-full flex items-center rounded-md hover:bg-accent transition-colors cursor-pointer",
            isCollapsed ? "justify-center px-3 py-2" : "justify-between px-3 py-2"
          )}
          onClick={(e) => {
            // Cycle: Light -> Dark -> Light
            const nextTheme = theme === "light" ? "dark" : "light";
            setTheme(nextTheme);
          }}
        >
          {/* Left side (Text) */}
          {!isCollapsed && (
            <div className="flex-1 text-sm text-muted-foreground select-none">
              테마
            </div>
          )}

          {/* Right side (Icon): Opens Dropdown Menu */}
          <ThemeToggle align="end">
            <div
              className="border-0 bg-transparent shadow-none p-1.5 h-auto w-auto hover:bg-transparent flex items-center justify-center cursor-pointer"
              onClick={(e) => e.stopPropagation()}
            >
              <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            </div>
          </ThemeToggle>
        </div>

        {/* Logout */}
        {user && (
          <div
            onClick={handleLogout}
            className={cn(
              "flex items-center rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors cursor-pointer",
              isCollapsed ? "justify-center px-3 py-2" : "gap-3 px-3 py-2"
            )}
            title={isCollapsed ? "로그아웃" : undefined}
          >
            <LogOut size={18} />
            {!isCollapsed && (
              <span className="text-sm font-medium">로그아웃</span>
            )}
          </div>
        )}
      </div>
    </aside>
  );
}

function NavItem({
  to,
  icon,
  label,
  badge,
  isCollapsed,
}: {
  to: string;
  icon: React.ReactNode;
  label: string;
  badge?: number;
  isCollapsed: boolean;
}) {
  return (
    <Link
      to={to}
      className={cn(
        "flex items-center rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-200 group relative",
        isCollapsed ? "justify-center px-3 py-2" : "gap-3 px-3 py-2"
      )}
      activeProps={{
        className: "bg-primary/10 text-primary font-medium",
      }}
      title={isCollapsed ? label : undefined}
    >
      {icon}
      {!isCollapsed && <span>{label}</span>}
      {!isCollapsed && badge !== undefined && badge > 0 && (
        <Badge className="ml-auto w-5 h-5 flex items-center justify-center p-0 text-xs">
          {badge}
        </Badge>
      )}
      {isCollapsed && badge !== undefined && badge > 0 && (
        <Badge className="absolute -top-1 -right-1 w-4 h-4 flex items-center justify-center p-0 text-[10px]">
          {badge}
        </Badge>
      )}
      {/* Active Indicator */}
      {!isCollapsed && (
        <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-[.active]:opacity-100 transition-opacity" />
      )}
    </Link>
  );
}
