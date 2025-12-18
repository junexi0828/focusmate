/**
 * Room Reservation Feature API Service
 * 방 예약 관련 API 호출 담당
 */

import { BaseApiClient, ApiResponse } from "../../../lib/api/base";
import {
  RoomReservation,
  CreateRoomReservationRequest,
  UpdateRoomReservationRequest,
} from "../types/roomReservation.types";

class RoomReservationService extends BaseApiClient {
  async createReservation(
    data: CreateRoomReservationRequest
  ): Promise<ApiResponse<RoomReservation>> {
    return this.request("/room-reservations/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMyReservations(
    activeOnly: boolean = true
  ): Promise<ApiResponse<RoomReservation[]>> {
    return this.request(`/room-reservations/?active_only=${activeOnly}`);
  }

  async getUpcomingReservations(): Promise<ApiResponse<RoomReservation[]>> {
    return this.request("/room-reservations/upcoming");
  }

  async updateReservation(
    reservationId: string,
    data: UpdateRoomReservationRequest
  ): Promise<ApiResponse<RoomReservation>> {
    return this.request(`/room-reservations/${reservationId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async cancelReservation(reservationId: string): Promise<ApiResponse<void>> {
    return this.request(`/room-reservations/${reservationId}`, {
      method: "DELETE",
    });
  }
}

export const roomReservationService = new RoomReservationService();

