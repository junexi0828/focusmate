/**
 * Room Feature Public API
 * 외부에서 사용할 수 있는 인터페이스만 export
 */

export { roomService } from "./services/roomService";
export type {
  Room,
  TimerState,
  CreateRoomRequest,
  UpdateRoomSettingsRequest,
} from "./types/room.types";

