import { useState } from "react";
import { X, Save, Trash2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { apiClient, Room } from "../lib/api";
import { toast } from "sonner";

interface RoomSettingsProps {
  room: Room;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export default function RoomSettings({
  room,
  isOpen,
  onClose,
  onUpdate,
}: RoomSettingsProps) {
  const [roomName, setRoomName] = useState(room.room_name ?? room.name);
  const [focusTime, setFocusTime] = useState(
    Math.floor(room.work_duration / 60)
  );
  const [breakTime, setBreakTime] = useState(
    Math.floor(room.break_duration / 60)
  );
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  if (!isOpen) return null;

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (
      !roomName ||
      !roomName.trim() ||
      roomName.length < 3 ||
      roomName.length > 50
    ) {
      newErrors.roomName = "방 이름은 3자에서 50자 사이여야 합니다";
    }

    if (focusTime < 1 || focusTime > 60) {
      newErrors.focusTime = "집중 시간은 1분에서 60분 사이여야 합니다";
    }

    if (breakTime < 1 || breakTime > 30) {
      newErrors.breakTime = "휴식 시간은 1분에서 30분 사이여야 합니다";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setIsSaving(true);
    try {
      const response = await apiClient.updateRoomSettings(
        room.room_id ?? room.id,
        {
          work_duration: focusTime * 60, // 분을 초로 변환
          break_duration: breakTime * 60, // 분을 초로 변환
        }
      );

      if (response.status === "error") {
        setErrors({
          general: response.error?.message || "방 설정 업데이트에 실패했습니다",
        });
        return;
      }

      toast.success("방 설정이 업데이트되었습니다");
      onUpdate();
    } catch (error) {
      console.error("Error updating room:", error);
      setErrors({ general: "방 설정 업데이트에 실패했습니다" });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      const response = await apiClient.deleteRoom(room.room_id ?? room.id);

      if (response.status === "error") {
        setErrors({
          general: response.error?.message || "방 삭제에 실패했습니다",
        });
        return;
      }

      toast.success("방이 삭제되었습니다");
      window.location.reload();
    } catch (error) {
      console.error("Error deleting room:", error);
      setErrors({ general: "방 삭제에 실패했습니다" });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">방 설정</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close settings"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="px-6 py-4 space-y-4">
          {errors.general && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{errors.general}</p>
            </div>
          )}

          <div>
            <Label
              htmlFor="settings-roomName"
              className="text-sm font-medium text-[#111827]"
            >
              방 이름
            </Label>
            <Input
              id="settings-roomName"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              className={`mt-1 bg-[#f9fafb] border-[#e5e7eb] rounded-xl ${
                errors.roomName ? "border-red-500" : ""
              }`}
              maxLength={50}
              disabled
            />
            {errors.roomName && (
              <p className="text-sm text-red-600 mt-1">{errors.roomName}</p>
            )}
          </div>

          <div>
            <Label
              htmlFor="settings-focusTime"
              className="text-sm font-medium text-[#111827]"
            >
              집중 시간 (분)
            </Label>
            <Input
              id="settings-focusTime"
              type="number"
              min="1"
              max="60"
              value={focusTime}
              onChange={(e) => setFocusTime(parseInt(e.target.value) || 25)}
              className={`mt-1 bg-[#f9fafb] border-[#e5e7eb] rounded-xl ${
                errors.focusTime ? "border-red-500" : ""
              }`}
            />
            {errors.focusTime && (
              <p className="text-sm text-red-600 mt-1">{errors.focusTime}</p>
            )}
            <p className="text-sm text-[#6b7280] mt-1">
              집중 작업 세션 시간
            </p>
          </div>

          <div>
            <Label
              htmlFor="settings-breakTime"
              className="text-sm font-medium text-[#111827]"
            >
              휴식 시간 (분)
            </Label>
            <Input
              id="settings-breakTime"
              type="number"
              min="1"
              max="30"
              value={breakTime}
              onChange={(e) => setBreakTime(parseInt(e.target.value) || 5)}
              className={`mt-1 bg-[#f9fafb] border-[#e5e7eb] rounded-xl ${
                errors.breakTime ? "border-red-500" : ""
              }`}
            />
            {errors.breakTime && (
              <p className="text-sm text-red-600 mt-1">{errors.breakTime}</p>
            )}
            <p className="text-sm text-[#6b7280] mt-1">
              세션 사이 휴식 시간
            </p>
          </div>

          <div className="pt-4 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">
              주의 구역 (위험)
            </h3>
            {!showDeleteConfirm ? (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
                className="w-full"
              >
                <Trash2 className="w-4 h-4" />
                <span>방 삭제</span>
              </Button>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-[#6b7280]">
                  정말 삭제하시겠습니까? 모든 참가자가 퇴장 처리되며 되돌릴 수 없습니다.
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="flex-1"
                  >
                    {isDeleting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>삭제 중...</span>
                      </>
                    ) : (
                      <span>네, 삭제합니다</span>
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1"
                  >
                    <span>취소</span>
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="sticky bottom-0 bg-[#f9fafb] border-t border-[#e5e7eb] px-6 py-4 flex gap-3">
          <Button variant="ghost" onClick={onClose} className="flex-1">
            취소
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 bg-[#4f46e5] hover:bg-[#4338ca] text-white"
          >
            {isSaving ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>저장 중...</span>
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                <span>변경사항 저장</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
