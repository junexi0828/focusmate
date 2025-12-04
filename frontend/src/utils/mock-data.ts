import { SessionRecord, DailyStats, WeeklyStats, MonthlyStats } from "../types/stats";

// Generate mock session records for the last 30 days
export function generateMockSessions(): SessionRecord[] {
  const sessions: SessionRecord[] = [];
  const now = new Date();
  
  for (let i = 0; i < 30; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // Random number of sessions per day (1-6)
    const sessionsPerDay = Math.floor(Math.random() * 6) + 1;
    
    for (let j = 0; j < sessionsPerDay; j++) {
      const isFocus = Math.random() > 0.3; // 70% focus, 30% break
      sessions.push({
        id: `session-${i}-${j}`,
        date: new Date(date),
        duration: isFocus ? 25 : 5,
        type: isFocus ? "focus" : "break",
        completed: Math.random() > 0.1, // 90% completion rate
        roomName: Math.random() > 0.5 ? "팀 작업" : "개인 학습",
      });
    }
  }
  
  return sessions.sort((a, b) => b.date.getTime() - a.date.getTime());
}

// Calculate daily statistics from sessions
export function calculateDailyStats(sessions: SessionRecord[]): DailyStats[] {
  const statsMap = new Map<string, DailyStats>();
  
  sessions.forEach((session) => {
    const dateKey = session.date.toISOString().split("T")[0];
    
    if (!statsMap.has(dateKey)) {
      statsMap.set(dateKey, {
        date: dateKey,
        focusTime: 0,
        breakTime: 0,
        sessions: 0,
      });
    }
    
    const stats = statsMap.get(dateKey)!;
    
    if (session.completed) {
      if (session.type === "focus") {
        stats.focusTime += session.duration;
      } else {
        stats.breakTime += session.duration;
      }
      stats.sessions += 1;
    }
  });
  
  return Array.from(statsMap.values()).sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );
}

// Calculate weekly statistics
export function calculateWeeklyStats(sessions: SessionRecord[]): WeeklyStats[] {
  const statsMap = new Map<string, WeeklyStats>();
  
  sessions.forEach((session) => {
    const date = new Date(session.date);
    const weekStart = new Date(date);
    weekStart.setDate(date.getDate() - date.getDay());
    const weekKey = weekStart.toISOString().split("T")[0];
    
    if (!statsMap.has(weekKey)) {
      statsMap.set(weekKey, {
        week: weekKey,
        focusTime: 0,
        breakTime: 0,
        sessions: 0,
      });
    }
    
    const stats = statsMap.get(weekKey)!;
    
    if (session.completed) {
      if (session.type === "focus") {
        stats.focusTime += session.duration;
      } else {
        stats.breakTime += session.duration;
      }
      stats.sessions += 1;
    }
  });
  
  return Array.from(statsMap.values()).sort((a, b) => 
    new Date(a.week).getTime() - new Date(b.week).getTime()
  );
}

// Calculate monthly statistics
export function calculateMonthlyStats(sessions: SessionRecord[]): MonthlyStats[] {
  const statsMap = new Map<string, MonthlyStats>();
  
  sessions.forEach((session) => {
    const date = new Date(session.date);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    
    if (!statsMap.has(monthKey)) {
      statsMap.set(monthKey, {
        month: monthKey,
        focusTime: 0,
        breakTime: 0,
        sessions: 0,
      });
    }
    
    const stats = statsMap.get(monthKey)!;
    
    if (session.completed) {
      if (session.type === "focus") {
        stats.focusTime += session.duration;
      } else {
        stats.breakTime += session.duration;
      }
      stats.sessions += 1;
    }
  });
  
  return Array.from(statsMap.values()).sort((a, b) => 
    a.month.localeCompare(b.month)
  );
}

export const mockSessions = generateMockSessions();
