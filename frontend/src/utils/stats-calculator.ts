import { SessionRecord } from '../features/stats/services/statsService';
import { DailyStats, WeeklyStats, MonthlyStats } from '../types/stats';

export function calculateDailyStats(sessions: SessionRecord[]): DailyStats[] {
  const statsMap = new Map<string, DailyStats>();

  sessions.forEach((session) => {
    const dateKey = new Date(session.completed_at).toISOString().split('T')[0];

    if (!statsMap.has(dateKey)) {
      statsMap.set(dateKey, {
        date: dateKey,
        focusTime: 0,
        breakTime: 0,
        sessions: 0,
      });
    }

    const stats = statsMap.get(dateKey)!;

    if (session.session_type === 'work') {
      stats.focusTime += session.duration_minutes;
    } else {
      stats.breakTime += session.duration_minutes;
    }
    stats.sessions += 1;
  });

  return Array.from(statsMap.values()).sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );
}

export function calculateWeeklyStats(sessions: SessionRecord[]): WeeklyStats[] {
  const statsMap = new Map<string, WeeklyStats>();

  sessions.forEach((session) => {
    const date = new Date(session.completed_at);
    const weekStart = new Date(date);
    weekStart.setDate(date.getDate() - date.getDay());
    const weekKey = weekStart.toISOString().split('T')[0];

    if (!statsMap.has(weekKey)) {
      statsMap.set(weekKey, {
        week: weekKey,
        focusTime: 0,
        breakTime: 0,
        sessions: 0,
      });
    }

    const stats = statsMap.get(weekKey)!;

    if (session.session_type === 'work') {
      stats.focusTime += session.duration_minutes;
    } else {
      stats.breakTime += session.duration_minutes;
    }
    stats.sessions += 1;
  });

  return Array.from(statsMap.values()).sort(
    (a, b) => new Date(a.week).getTime() - new Date(b.week).getTime()
  );
}

export function calculateMonthlyStats(sessions: SessionRecord[]): MonthlyStats[] {
  const statsMap = new Map<string, MonthlyStats>();

  sessions.forEach((session) => {
    const date = new Date(session.completed_at);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

    if (!statsMap.has(monthKey)) {
      statsMap.set(monthKey, {
        month: monthKey,
        focusTime: 0,
        breakTime: 0,
        sessions: 0,
      });
    }

    const stats = statsMap.get(monthKey)!;

    if (session.session_type === 'work') {
      stats.focusTime += session.duration_minutes;
    } else {
      stats.breakTime += session.duration_minutes;
    }
    stats.sessions += 1;
  });

  return Array.from(statsMap.values()).sort((a, b) =>
    a.month.localeCompare(b.month)
  );
}

