import React, { useState } from "react";
import { X, Save, Trash2 } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { roomService, Room, UpdateRoomSettingsRequest } from "../index";
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
  const [roomName, setRoomName] = useState(room.room_name);
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

    if (!roomName.trim() || roomName.length < 3 || roomName.length > 50) {
      newErrors.roomName = "Room name must be between 3 and 50 characters";
    }

    if (focusTime < 1 || focusTime > 60) {
      newErrors.focusTime = "Focus time must be between 1 and 60 minutes";
    }

    if (breakTime < 1 || breakTime > 30) {
      newErrors.breakTime = "Break time must be between 1 and 30 minutes";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setIsSaving(true);
    try {
      const response = await roomService.updateRoomSettings(room.room_id, {
        work_duration_minutes: focusTime,
        break_duration_minutes: breakTime,
      });

      if (response.status === "error") {
        setErrors({
          general: response.error?.message || "Failed to update room settings",
        });
        return;
      }

      toast.success("Room settings updated successfully");
      onUpdate();
    } catch (error) {
      console.error("Error updating room:", error);
      setErrors({ general: "Failed to update room settings" });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      const response = await roomService.deleteRoom(room.room_id);

      if (response.status === "error") {
        setErrors({
          general: response.error?.message || "Failed to delete room",
        });
        return;
      }

      toast.success("Room deleted successfully");
      window.location.reload();
    } catch (error) {
      console.error("Error deleting room:", error);
      setErrors({ general: "Failed to delete room" });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Room Settings</h2>
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
              Room Name
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
              Focus Time (minutes)
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
              Time for focused work sessions
            </p>
          </div>

          <div>
            <Label
              htmlFor="settings-breakTime"
              className="text-sm font-medium text-[#111827]"
            >
              Break Time (minutes)
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
              Time for rest between sessions
            </p>
          </div>

          <div className="pt-4 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">
              Danger Zone
            </h3>
            {!showDeleteConfirm ? (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
                className="w-full"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete Room</span>
              </Button>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-[#6b7280]">
                  Are you sure? This will remove all participants and cannot be
                  undone.
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
                        <span>Deleting...</span>
                      </>
                    ) : (
                      <span>Yes, Delete</span>
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1"
                  >
                    <span>Cancel</span>
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="sticky bottom-0 bg-[#f9fafb] border-t border-[#e5e7eb] px-6 py-4 flex gap-3">
          <Button variant="ghost" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 bg-[#4f46e5] hover:bg-[#4338ca] text-white"
          >
            {isSaving ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                <span>Save Changes</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

