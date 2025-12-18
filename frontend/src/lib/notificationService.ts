/**
 * Browser Notification Service
 * Handles notification permissions and displays notifications
 */

export type NotificationPermission = "default" | "granted" | "denied";

export interface NotificationOptions {
  title: string;
  body: string;
  icon?: string;
  tag?: string;
  requireInteraction?: boolean;
  silent?: boolean;
}

class NotificationService {
  /**
   * Check if browser supports notifications
   */
  isSupported(): boolean {
    return "Notification" in window;
  }

  /**
   * Get current notification permission status
   */
  getPermission(): NotificationPermission {
    if (!this.isSupported()) {
      return "denied";
    }
    return Notification.permission as NotificationPermission;
  }

  /**
   * Request notification permission from user
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!this.isSupported()) {
      throw new Error("Browser does not support notifications");
    }

    if (Notification.permission === "granted") {
      return "granted";
    }

    if (Notification.permission === "denied") {
      return "denied";
    }

    const permission = await Notification.requestPermission();
    return permission as NotificationPermission;
  }

  /**
   * Check if notifications are allowed
   */
  isAllowed(): boolean {
    return this.getPermission() === "granted";
  }

  /**
   * Show a notification
   */
  show(options: NotificationOptions): void {
    if (!this.isSupported()) {
      console.warn("Browser does not support notifications");
      return;
    }

    if (!this.isAllowed()) {
      console.warn("Notification permission not granted");
      return;
    }

    try {
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon || "/favicon.ico",
        tag: options.tag,
        requireInteraction: options.requireInteraction || false,
        silent: options.silent || false,
      });

      // Auto-close after 5 seconds (unless requireInteraction is true)
      if (!options.requireInteraction) {
        setTimeout(() => {
          notification.close();
        }, 5000);
      }

      // Handle click
      notification.onclick = () => {
        window.focus();
        notification.close();
      };
    } catch (error) {
      console.error("Failed to show notification:", error);
    }
  }

  /**
   * Show a simple notification (convenience method)
   */
  notify(title: string, body: string, icon?: string): void {
    this.show({ title, body, icon });
  }

  /**
   * Get permission status message in Korean
   */
  getPermissionMessage(): string {
    const permission = this.getPermission();
    switch (permission) {
      case "granted":
        return "알림이 활성화되어 있습니다";
      case "denied":
        return "알림이 차단되어 있습니다. 브라우저 설정에서 허용해주세요";
      case "default":
        return "알림 권한을 요청해주세요";
      default:
        return "알림을 사용할 수 없습니다";
    }
  }

  /**
   * Check if permission can be requested (not denied)
   */
  canRequestPermission(): boolean {
    return this.getPermission() !== "denied";
  }
}

export const notificationService = new NotificationService();

