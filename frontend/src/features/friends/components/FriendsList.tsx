/**
 * Friends List Component
 * Displays friends with online status and quick chat
 */

import { useState, useEffect } from "react";
import { friendService, type Friend } from "../services/friendService";
import { useNavigate } from "@tanstack/react-router";

export function FriendsList() {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<"all" | "online" | "blocked">("all");
  const navigate = useNavigate();

  useEffect(() => {
    loadFriends();
  }, []);

  const loadFriends = async () => {
    setLoading(true);
    const response = await friendService.getFriends();
    if (response.status === "success") {
      setFriends(response.data.friends);
    }
    setLoading(false);
  };

  const handleSearch = async () => {
    setLoading(true);
    const response = await friendService.searchFriends(searchQuery, filterType);
    if (response.status === "success") {
      setFriends(response.data.friends);
    }
    setLoading(false);
  };

  const handleQuickChat = async (friendId: string) => {
    const response = await friendService.createFriendChat(friendId);
    if (response.status === "success") {
      // Navigate to chat - adjust route as needed
      navigate({ to: "/chat" });
    }
  };

  const formatLastSeen = (lastSeenAt: string | null | undefined) => {
    if (!lastSeenAt) return "오프라인";

    const lastSeen = new Date(lastSeenAt);
    const now = new Date();
    const diff = now.getTime() - lastSeen.getTime();

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}일 전`;
    if (hours > 0) return `${hours}시간 전`;
    if (minutes > 0) return `${minutes}분 전`;
    return "방금 전";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* Search and Filter */}
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="친구 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          검색
        </button>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilterType("all")}
          className={`px-4 py-2 rounded-lg ${
            filterType === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          전체
        </button>
        <button
          onClick={() => setFilterType("online")}
          className={`px-4 py-2 rounded-lg ${
            filterType === "online"
              ? "bg-green-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          온라인만
        </button>
      </div>

      {/* Friends List */}
      <div className="space-y-2">
        {friends.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            친구가 없습니다
          </div>
        ) : (
          friends.map((friend) => (
            <div
              key={friend.id}
              className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
            >
              {/* Profile Image with Online Indicator */}
              <div className="relative">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold">
                  {friend.friend_username.charAt(0)}
                </div>
                {friend.friend_is_online && (
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                )}
              </div>

              {/* Friend Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-900">
                    {friend.friend_username}
                  </h3>
                  {friend.friend_is_online && (
                    <span className="text-xs text-green-600 font-medium">
                      온라인
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500">
                  {friend.friend_status_message || formatLastSeen(friend.friend_last_seen_at)}
                </p>
              </div>

              {/* Quick Chat Button */}
              <button
                onClick={() => handleQuickChat(friend.friend_id)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                채팅하기
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
