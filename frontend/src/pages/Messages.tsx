import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, Users, Heart, Search, Plus, Send } from "lucide-react";
import { chatApi } from "@/api/chat";
import { useChatWebSocket } from "@/hooks/useChatWebSocket";
import type { ChatRoom, MessageCreate } from "@/types/chat";
import { PageTransition } from "@/components/PageTransition";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button-enhanced";
import { Input } from "@/components/ui/input";

export function MessagesPage() {
  const [selectedRoom, setSelectedRoom] = useState<ChatRoom | null>(null);
  const [activeTab, setActiveTab] = useState<"direct" | "team" | "matching">(
    "direct"
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [messageInput, setMessageInput] = useState("");

  const queryClient = useQueryClient();
  const token = localStorage.getItem("access_token");

  // WebSocket connection
  const {
    isConnected,
    messages: wsMessages,
    joinRoom,
    leaveRoom,
  } = useChatWebSocket(token);

  // Fetch rooms
  const { data: roomsData, isLoading } = useQuery({
    queryKey: ["chat-rooms", activeTab],
    queryFn: () => chatApi.getRooms(activeTab),
  });

  // Fetch messages for selected room
  const { data: messagesData } = useQuery({
    queryKey: ["chat-messages", selectedRoom?.room_id],
    queryFn: () =>
      selectedRoom ? chatApi.getMessages(selectedRoom.room_id) : null,
    enabled: !!selectedRoom,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (data: MessageCreate) =>
      chatApi.sendMessage(selectedRoom!.room_id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chat-messages", selectedRoom?.room_id],
      });
      setMessageInput("");
    },
  });

  const rooms = roomsData?.rooms || [];
  const apiMessages = messagesData?.messages || [];
  const roomWsMessages = selectedRoom
    ? wsMessages.get(selectedRoom.room_id) || []
    : [];
  const allMessages = [...apiMessages, ...roomWsMessages];

  // Join/leave room on selection
  useEffect(() => {
    if (selectedRoom) {
      joinRoom(selectedRoom.room_id);
      chatApi.markAsRead(selectedRoom.room_id);
      return () => leaveRoom(selectedRoom.room_id);
    }
  }, [selectedRoom, joinRoom, leaveRoom]);

  const filteredRooms = rooms.filter((room) =>
    room.room_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedRoom) return;

    sendMessageMutation.mutate({
      content: messageInput.trim(),
      message_type: "text",
    });
  };

  const getRoomIcon = (type: string) => {
    switch (type) {
      case "direct":
        return <MessageSquare className="w-4 h-4" />;
      case "team":
        return <Users className="w-4 h-4" />;
      case "matching":
        return <Heart className="w-4 h-4" />;
      default:
        return <MessageSquare className="w-4 h-4" />;
    }
  };

  return (
    <PageTransition>
      <div className="h-[calc(100vh-4rem)] flex bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
        {/* Sidebar */}
        <div className="w-80 border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Messages
              </h1>
              <Button size="icon" variant="ghost">
                <Plus className="w-5 h-5" />
              </Button>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-slate-200 dark:border-slate-700">
            {(["direct", "team", "matching"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 transition-colors ${
                  activeTab === tab
                    ? "border-b-2 border-blue-500 text-blue-600 dark:text-blue-400"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                }`}
              >
                {getRoomIcon(tab)}
                <span className="text-sm font-medium capitalize">{tab}</span>
              </button>
            ))}
          </div>

          {/* Room List */}
          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-slate-500">Loading...</div>
            ) : filteredRooms.length === 0 ? (
              <div className="p-8 text-center">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-slate-300 dark:text-slate-600" />
                <p className="text-slate-500 dark:text-slate-400">
                  No conversations yet
                </p>
              </div>
            ) : (
              filteredRooms.map((room) => (
                <button
                  key={room.room_id}
                  onClick={() => setSelectedRoom(room)}
                  className={`w-full p-4 text-left hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors border-l-2 ${
                    selectedRoom?.room_id === room.room_id
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-transparent"
                  }`}
                >
                  <div className="flex items-start justify-between mb-1">
                    <h3 className="font-medium text-slate-900 dark:text-slate-100">
                      {room.room_name || "Unnamed Room"}
                    </h3>
                    {room.unread_count > 0 && (
                      <span className="px-2 py-0.5 text-xs font-medium text-white bg-blue-500 rounded-full">
                        {room.unread_count}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 truncate">
                    {room.description || "No description"}
                  </p>
                </button>
              ))
            )}
          </div>

          {/* Connection Status */}
          <div className="p-3 border-t border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-2 text-xs">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <span className="text-slate-600 dark:text-slate-400">
                {isConnected ? "Connected" : "Disconnected"}
              </span>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedRoom ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium">
                    {selectedRoom.room_name?.slice(0, 2).toUpperCase() || "CH"}
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                      {selectedRoom.room_name || "Unnamed Room"}
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {selectedRoom.room_type === "matching" &&
                      selectedRoom.display_mode === "blind"
                        ? "🎭 Blind Mode"
                        : selectedRoom.room_type === "team"
                          ? "👥 Team Channel"
                          : "💬 Direct Message"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white dark:bg-slate-900">
                {allMessages.length === 0 ? (
                  <div className="text-center text-slate-500 dark:text-slate-400 py-8">
                    No messages yet. Start the conversation!
                  </div>
                ) : (
                  allMessages.map((message) => (
                    <div
                      key={message.message_id}
                      className="flex gap-3 hover:bg-slate-50 dark:hover:bg-slate-800 p-2 rounded-lg transition-colors"
                    >
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium flex-shrink-0">
                        {message.sender_id.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-baseline gap-2 mb-1">
                          <span className="font-medium text-slate-900 dark:text-slate-100">
                            {message.sender_id}
                          </span>
                          <span className="text-xs text-slate-400 dark:text-slate-500">
                            {new Date(message.created_at).toLocaleTimeString()}
                          </span>
                          {message.is_edited && (
                            <span className="text-xs text-slate-400 dark:text-slate-500">
                              (edited)
                            </span>
                          )}
                        </div>
                        <p className="text-slate-700 dark:text-slate-300 break-words">
                          {message.content}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="Type a message..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    type="submit"
                    disabled={
                      !messageInput.trim() || sendMessageMutation.isPending
                    }
                    className="bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Send
                  </Button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-white dark:bg-slate-900">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 text-slate-300 dark:text-slate-600" />
                <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                  Select a conversation
                </h3>
                <p className="text-slate-500 dark:text-slate-400">
                  Choose a chat from the sidebar to start messaging
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
