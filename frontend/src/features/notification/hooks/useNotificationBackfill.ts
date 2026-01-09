import { useState, useCallback } from 'react';
import { api } from '../../../api/client';
import { NotificationData } from '../../../hooks/useNotifications';

export function useNotificationBackfill() {
  const [isSyncing, setIsSyncing] = useState(false);

  const syncMissedNotifications = useCallback(async (lastSyncTime: string): Promise<NotificationData[]> => {
    setIsSyncing(true);
    try {
      const response = await api.get<NotificationData[]>("/notifications/backfill", {
        params: { since: lastSyncTime },
      });
      return response.data || [];
    } catch (error) {
      console.warn("[Backfill] Sync failed:", error);
      return [];
    } finally {
      setIsSyncing(false);
    }
  }, []);

  return { syncMissedNotifications, isSyncing };
}
