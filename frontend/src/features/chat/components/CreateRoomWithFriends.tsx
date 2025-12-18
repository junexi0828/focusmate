/**
 * Create Room with Friends Component
 * Select friends and create a study room together
 */

import { useState, useEffect } from "react";
import { friendService, type Friend } from "../../friends/services/friendService";
import { invitationService } from "../services/invitationService";

interface CreateRoomWithFriendsProps {
  onClose: () => void;
  onSuccess?: (roomId: string) => void;
}

export function CreateRoomWithFriends({
  onClose,
  onSuccess,
}: CreateRoomWithFriendsProps) {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [selectedFriends, setSelectedFriends] = useState<Set<string>>(new Set());
  const [roomName, setRoomName] = useState("");
  const [description, setDescription] = useState("");
  const [generateInvitation, setGenerateInvitation] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFriends();
  }, []);

  const loadFriends = async () => {
    const response = await friendService.getFriends();
    if (response.status === "success") {
      setFriends(response.data.friends.filter((f) => !f.is_blocked));
    }
  };

  const toggleFriend = (friendId: string) => {
    const newSelected = new Set(selectedFriends);
    if (newSelected.has(friendId)) {
      newSelected.delete(friendId);
    } else {
      newSelected.add(friendId);
    }
    setSelectedFriends(newSelected);
  };

  const handleCreate = async () => {
    if (selectedFriends.size === 0) {
      alert("최소 1명의 친구를 선택해주세요");
      return;
    }

    setLoading(true);
    const response = await invitationService.createRoomWithFriends({
      friend_ids: Array.from(selectedFriends),
      room_name: roomName || undefined,
      description: description || undefined,
      generate_invitation: generateInvitation,
      invitation_expires_hours: 24,
    });

    if (response.status === "success") {
      onSuccess?.(response.data.room_id);
      onClose();
    } else {
      alert(response.error?.message || "방 생성 실패");
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            친구와 함께 방 만들기
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          {/* Room Info */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              방 이름 (선택사항)
            </label>
            <input
              type="text"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              placeholder="예: 시험 준비 스터디"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              설명 (선택사항)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="방 설명을 입력하세요"
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Invitation Option */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="generate-invitation"
              checked={generateInvitation}
              onChange={(e) => setGenerateInvitation(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="generate-invitation" className="text-sm text-gray-700">
              초대 코드 자동 생성 (다른 사람도 참가 가능)
            </label>
          </div>

          {/* Friends Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              친구 선택 ({selectedFriends.size}명 선택됨)
            </label>
            <div className="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-2">
              {friends.length === 0 ? (
                <div className="text-center py-4 text-gray-500">
                  친구가 없습니다
                </div>
              ) : (
                friends.map((friend) => (
                  <div
                    key={friend.id}
                    onClick={() => toggleFriend(friend.friend_id)}
                    className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedFriends.has(friend.friend_id)
                        ? "bg-blue-50 border-2 border-blue-500"
                        : "bg-gray-50 border-2 border-transparent hover:bg-gray-100"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedFriends.has(friend.friend_id)}
                      onChange={() => {}}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="relative">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                        {friend.friend_username.charAt(0)}
                      </div>
                      {friend.friend_is_online && (
                        <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">
                          {friend.friend_username}
                        </span>
                        {friend.friend_is_online && (
                          <span className="text-xs text-green-600">온라인</span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {friend.friend_status_message || friend.friend_email}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-4">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              취소
            </button>
            <button
              onClick={handleCreate}
              disabled={loading || selectedFriends.size === 0}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "생성 중..." : "방 만들기"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
