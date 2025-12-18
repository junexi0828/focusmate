/**
 * Notification Bell Component
 * Shows unread notification count and allows viewing recent notifications
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Bell } from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "./ui/popover";
import { ScrollArea } from "./ui/scroll-area";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";
import { api } from "../api/client";
import { useNotifications } from "../hooks/useNotifications";
import { useNavigate } from "@tanstack/react-router";

interface Notification {
  notification_id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  data?: {
    routing?: {
      type: string;
      path: string;
      params?: Record<string, any>;
    };
    [key: string]: any;
  };
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  updated_at: string;
}

export function NotificationBell() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  // Fetch notifications from API
  const { data: apiNotifications = [], refetch } = useQuery<Notification[]>({
    queryKey: ["notifications"],
    queryFn: async () => {
      const response = await api.get<Notification[]>("/notifications/");
      return response.data;
    },
    refetchInterval: isOpen ? 5000 : 30000, // Refetch more frequently when open
  });

  // Get unread count
  const { data: unreadData } = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: async () => {
      const response = await api.get<{ unread_count: number }>("/notifications/unread-count");
      return response.data;
    },
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // WebSocket for real-time updates
  const { isConnected, notifications: wsNotifications } = useNotifications((notification) => {
    // Refetch when new notification arrives
    refetch();
  });

  const unreadCount = unreadData?.unread_count || 0;

  const handleNotificationClick = async (notification: Notification) => {
    // Mark as read
    try {
      await api.post("/notifications/mark-read", {
        notification_ids: [notification.notification_id],
      });
      refetch();
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }

    // Navigate if routing info exists
    if (notification.data?.routing?.path) {
      const path = notification.data.routing.path;
      navigate({ to: path as any });
      setIsOpen(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.post("/notifications/mark-all-read");
      refetch();
    } catch (error) {
      console.error("Failed to mark all as read:", error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "friend_request":
        return "👋";
      case "friend_request_accepted":
        return "✅";
      case "team_invitation":
        return "👥";
      case "new_message":
        return "💬";
      case "post_comment":
        return "💭";
      case "post_like":
        return "❤️";
      case "achievement":
        return "🏆";
      case "system":
        return "ℹ️";
      default:
        return "🔔";
    }
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <Badge
              className="absolute -top-1 -right-1 h-5 min-w-5 flex items-center justify-center p-0 bg-red-500 border-none"
              variant="destructive"
            >
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
          {isConnected && (
            <div className="absolute bottom-0 right-0 w-2 h-2 bg-green-500 rounded-full border border-background" />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold">알림</h3>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAllRead}
              className="text-xs"
            >
              모두 읽음
            </Button>
          )}
        </div>
        <ScrollArea className="h-96">
          {apiNotifications.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">알림이 없습니다</p>
            </div>
          ) : (
            <div className="divide-y">
              {apiNotifications.map((notification) => (
                <button
                  key={notification.notification_id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`w-full p-4 text-left hover:bg-muted/50 transition-colors ${
                    !notification.is_read ? "bg-blue-50 dark:bg-blue-950/20" : ""
                  }`}
                >
                  <div className="flex gap-3">
                    <div className="text-2xl flex-shrink-0">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <h4 className="font-medium text-sm truncate">
                          {notification.title}
                        </h4>
                        {!notification.is_read && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {formatDistanceToNow(new Date(notification.created_at), {
                          addSuffix: true,
                          locale: ko,
                        })}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
