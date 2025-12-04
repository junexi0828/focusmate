/**
 * Timer Feature API Service
 * 타이머 제어 관련 API 호출 담당
 */

import { BaseApiClient, ApiResponse } from "../../../lib/api/base";
import { TimerState, SessionType } from "../types/timer.types";

class TimerService extends BaseApiClient {
  async startTimer(
    roomId: string,
    sessionType: SessionType = "work"
  ): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/start`, {
      method: "POST",
      body: JSON.stringify({ session_type: sessionType }),
    });
  }

  async pauseTimer(roomId: string): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/pause`, {
      method: "POST",
    });
  }

  async resumeTimer(roomId: string): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/resume`, {
      method: "POST",
    });
  }

  async resetTimer(roomId: string): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/reset`, {
      method: "POST",
    });
  }
}

export const timerService = new TimerService();

