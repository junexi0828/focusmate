import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { getUnreadCount } from "../../api/notifications";
import { NotificationList } from "./NotificationList";
import { useNotifications } from "../../hooks/useNotifications";

export function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);

  // WebSocket connection for real-time updates
  const { isConnected } = useNotifications(() => {
    // Reload count when new notification arrives (only if authenticated)
    if (localStorage.getItem("access_token")) {
      loadUnreadCount();
    }
  });

  useEffect(() => {
    // Only load if authenticated
    const token = localStorage.getItem("access_token");
    if (!token) {
      return; // Don't poll if not authenticated
    }

    loadUnreadCount();
    // Poll every 30 seconds
    const interval = setInterval(() => {
      // Check token again before each poll
      if (localStorage.getItem("access_token")) {
        loadUnreadCount();
      }
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadUnreadCount = async () => {
    // Check authentication before making request
    const token = localStorage.getItem("access_token");
    if (!token) {
      setUnreadCount(0);
      return;
    }

    try {
      const count = await getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      // Don't log errors if it's a 401 (expected when not authenticated)
      if (error && typeof error === "object" && "response" in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status === 401) {
          setUnreadCount(0);
          return;
        }
      }
      console.error("Failed to load unread count:", error);
    }
  };

  const handleMarkAsRead = () => {
    loadUnreadCount();
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
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
      <PopoverContent className="w-96 p-0" align="end">
        <NotificationList onMarkAsRead={handleMarkAsRead} />
      </PopoverContent>
    </Popover>
  );
}
