import { Link, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { User } from "../types/user";
import {
  Timer,
  Home,
  TrendingUp,
  MessageCircle,
  Users,
  UserCircle,
} from "lucide-react";

export type NavPage = "home" | "room" | "stats" | "community" | "messages" | "profile";

interface NavigationProps {
  user: User | null;
  unreadMessages?: number;
}

export function Navigation({ user, unreadMessages = 0 }: NavigationProps) {
  const location = useLocation();
  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const navItems = [
    { path: "/", label: "홈", icon: Home },
    { path: "/stats", label: "통계", icon: TrendingUp },
    { path: "/community", label: "커뮤니티", icon: Users },
    { path: "/messages", label: "메시지", icon: MessageCircle, badge: unreadMessages },
  ];

  const isActive = (path: string) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="border-b bg-card sticky top-0 z-40">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Timer className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="hidden sm:block">Focus Mate</span>
          </Link>

          {/* Nav Items */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link key={item.path} to={item.path}>
                <Button
                  variant={isActive(item.path) ? "secondary" : "ghost"}
                  className="relative"
                >
                  <item.icon className="w-4 h-4 sm:mr-2" />
                  <span className="hidden sm:inline">{item.label}</span>
                  {item.badge ? (
                    <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 text-xs">
                      {item.badge}
                    </Badge>
                  ) : null}
                </Button>
              </Link>
            ))}

            {/* Profile */}
            {user ? (
              <Link to="/profile">
                <Button
                  variant={isActive("/profile") ? "secondary" : "ghost"}
                  className="ml-2"
                >
                  <Avatar className="w-6 h-6 sm:mr-2">
                    <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                      {getInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden sm:inline">{user.name}</span>
                </Button>
              </Link>
            ) : (
              <Link to="/login">
                <Button variant="ghost">
                  <UserCircle className="w-4 h-4 sm:mr-2" />
                  <span className="hidden sm:inline">로그인</span>
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
