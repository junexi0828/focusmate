import { useEffect, useRef } from "react";
import { RoomReservation } from "../types/roomReservation.types";
import { notificationService } from "../../../lib/notificationService";

/**
 * 예약 시간 알림 훅
 * 예약 시작 5분 전, 1분 전에 브라우저 알림을 표시합니다.
 */
export function useReservationNotification(
  reservations: RoomReservation[]
) {
  const timeoutRefs = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());
  const notifiedRefs = useRef<Set<string>>(new Set());

  useEffect(() => {
    // Request notification permission if needed
    if (notificationService.isSupported() && notificationService.getPermission() === "default") {
      notificationService.requestPermission().catch(console.error);
    }

    // Clear any existing scheduled notifications
    timeoutRefs.current.forEach((timeoutId) => {
      clearTimeout(timeoutId);
    });
    timeoutRefs.current.clear();

    const now = Date.now();

    const scheduleNotification = (key: string, delayMs: number, title: string, body: string) => {
      if (notifiedRefs.current.has(key)) {
        return;
      }
      if (delayMs <= 0) {
        showNotification(title, body);
        notifiedRefs.current.add(key);
        return;
      }
      const timeoutId = setTimeout(() => {
        showNotification(title, body);
        notifiedRefs.current.add(key);
        timeoutRefs.current.delete(key);
      }, delayMs);
      timeoutRefs.current.set(key, timeoutId);
    };

    reservations.forEach((reservation) => {
      if (!reservation.is_active || reservation.is_completed) {
        return;
      }
      const scheduledAt = new Date(reservation.scheduled_at).getTime();
      const timeDiff = scheduledAt - now;
      if (timeDiff <= -60 * 1000) {
        return;
      }

      const formattedTime = formatReservationTime(reservation.scheduled_at);

      const fiveMinKey = `${reservation.id}-5min`;
      const oneMinKey = `${reservation.id}-1min`;
      const startKey = `${reservation.id}-start`;

      const fiveMinDelay = scheduledAt - now - 5 * 60 * 1000;
      const oneMinDelay = scheduledAt - now - 1 * 60 * 1000;
      const startDelay = scheduledAt - now;

      scheduleNotification(
        fiveMinKey,
        fiveMinDelay,
        "방 예약 알림",
        `5분 후 "${formattedTime}" 예약이 시작됩니다.`
      );

      scheduleNotification(
        oneMinKey,
        oneMinDelay,
        "방 예약 알림",
        `1분 후 "${formattedTime}" 예약이 시작됩니다.`
      );

      scheduleNotification(
        startKey,
        startDelay,
        "방 예약 시작",
        `"${formattedTime}" 예약 시간입니다. 방에 입장하세요!`
      );
    });

    return () => {
      timeoutRefs.current.forEach((timeoutId) => clearTimeout(timeoutId));
      timeoutRefs.current.clear();
    };
  }, [reservations]);

  const showNotification = (title: string, body: string) => {
    if (notificationService.isAllowed()) {
      notificationService.show({
        title,
        body,
        icon: "/favicon.ico",
        tag: "reservation-notification",
      });
    }
  };

  const formatReservationTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };
}
