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
  const notifiedReservationsRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    // Request notification permission if needed
    if (notificationService.isSupported() && notificationService.getPermission() === "default") {
      notificationService.requestPermission().catch(console.error);
    }

    // Check for upcoming reservations
    const checkReservations = () => {
      const now = new Date();
      const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000);
      const oneMinuteFromNow = new Date(now.getTime() + 1 * 60 * 1000);

      reservations.forEach((reservation) => {
        if (!reservation.is_active || reservation.is_completed) return;
        if (notifiedReservationsRef.current.has(reservation.id)) return;

        const scheduledTime = new Date(reservation.scheduled_at);
        const timeDiff = scheduledTime.getTime() - now.getTime();

        // 5분 전 알림 (4분 30초 ~ 5분 30초 사이)
        if (
          timeDiff > 4.5 * 60 * 1000 &&
          timeDiff < 5.5 * 60 * 1000 &&
          !notifiedReservationsRef.current.has(`${reservation.id}-5min`)
        ) {
          showNotification(
            "방 예약 알림",
            `5분 후 "${formatReservationTime(reservation.scheduled_at)}" 예약이 시작됩니다.`
          );
          notifiedReservationsRef.current.add(`${reservation.id}-5min`);
        }

        // 1분 전 알림 (30초 ~ 1분 30초 사이)
        if (
          timeDiff > 30 * 1000 &&
          timeDiff < 1.5 * 60 * 1000 &&
          !notifiedReservationsRef.current.has(`${reservation.id}-1min`)
        ) {
          showNotification(
            "방 예약 알림",
            `1분 후 "${formatReservationTime(reservation.scheduled_at)}" 예약이 시작됩니다.`
          );
          notifiedReservationsRef.current.add(`${reservation.id}-1min`);
        }

        // 예약 시간 도달 (과거 1분 이내)
        if (timeDiff <= 0 && timeDiff > -60 * 1000) {
          if (!notifiedReservationsRef.current.has(`${reservation.id}-start`)) {
            showNotification(
              "방 예약 시작",
              `"${formatReservationTime(reservation.scheduled_at)}" 예약 시간입니다. 방에 입장하세요!`
            );
            notifiedReservationsRef.current.add(`${reservation.id}-start`);
          }
        }
      });
    };

    // Check every 30 seconds
    const interval = setInterval(checkReservations, 30000);
    checkReservations(); // Initial check

    return () => clearInterval(interval);
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

