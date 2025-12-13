import React, { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, Users, Heart, Search, Plus, Send } from "lucide-react";
import { chatService, type ChatRoom, type MessageCreate, type Message } from "../features/chat/services/chatService";
import { PageTransition } from "../components/PageTransition";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button-enhanced";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";
import { authService } from "../features/auth/services/authService";
import { useChatWebSocket } from "../features/chat/hooks/useChatWebSocket";
import { ScrollArea } from "../components/ui/scroll-area";
import { MessageItem } from "../features/chat/components/MessageItem";
import { FilePreview } from "../features/chat/components/FilePreview";
import { Paperclip, X } from "lucide-react";
import { toast } from "sonner";

export function MessagesPage() {
  const [selectedRoom, setSelectedRoom] = useState<ChatRoom | null>(null);
  const [activeTab, setActiveTab] = useState<"direct" | "team" | "matching">(
    "direct"
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const user = authService.getCurrentUser();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // WebSocket connection for real-time messages
  const { isConnected, messages: wsMessages, typingUsers, joinRoom, leaveRoom, sendTyping } = useChatWebSocket();
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Fetch rooms
  const { data: roomsData, isLoading } = useQuery({
    queryKey: ["chat-rooms", activeTab],
    queryFn: async () => {
      const response = await chatService.getRooms(activeTab);
      return response.status === "success" ? response.data : { rooms: [], total: 0 };
    },
    refetchInterval: 30000, // Refetch every 30 seconds to update unread counts
  });

  // Fetch messages for selected room
  const { data: messagesData } = useQuery({
    queryKey: ["chat-messages", selectedRoom?.room_id],
    queryFn: async () => {
      if (!selectedRoom) return null;
      const response = await chatService.getMessages(selectedRoom.room_id);
      return response.status === "success" ? response.data : { messages: [], total: 0, has_more: false };
    },
    enabled: !!selectedRoom,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (data: MessageCreate) => {
      // If there are files, upload them first
      if (selectedFiles.length > 0 && selectedRoom) {
        setIsUploading(true);
        try {
          const uploadResponse = await chatService.uploadFiles(
            selectedRoom.room_id,
            selectedFiles
          );
          if (uploadResponse.status === "success" && uploadResponse.data) {
            data.attachments = uploadResponse.data.files.map((f) => f.url);
            // Determine message type based on attachments
            const hasImages = uploadResponse.data.files.some((f) =>
              /\.(jpg|jpeg|png|gif|webp)$/i.test(f.url)
            );
            data.message_type = hasImages ? "image" : "file";
          }
        } catch (error) {
          toast.error("파일 업로드에 실패했습니다");
          throw error;
        } finally {
          setIsUploading(false);
          setSelectedFiles([]);
        }
      }
      return chatService.sendMessage(selectedRoom!.room_id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chat-messages", selectedRoom?.room_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["chat-rooms", activeTab],
      });
      setMessageInput("");
      setSelectedFiles([]);
    },
    onError: (error) => {
      toast.error("메시지 전송에 실패했습니다");
      console.error("Send message error:", error);
    },
  });

  // Update message mutation
  const updateMessageMutation = useMutation({
    mutationFn: ({ messageId, content }: { messageId: string; content: string }) =>
      chatService.updateMessage(selectedRoom!.room_id, messageId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chat-messages", selectedRoom?.room_id],
      });
      toast.success("메시지가 수정되었습니다");
    },
    onError: () => {
      toast.error("메시지 수정에 실패했습니다");
    },
  });

  // Delete message mutation
  const deleteMessageMutation = useMutation({
    mutationFn: (messageId: string) =>
      chatService.deleteMessage(selectedRoom!.room_id, messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["chat-messages", selectedRoom?.room_id],
      });
      toast.success("메시지가 삭제되었습니다");
    },
    onError: () => {
      toast.error("메시지 삭제에 실패했습니다");
    },
  });

  const rooms = roomsData?.rooms || [];
  const apiMessages = messagesData?.messages || [];
  const wsRoomMessages = selectedRoom ? wsMessages.get(selectedRoom.room_id) || [] : [];

  // Merge API messages and WebSocket messages, removing duplicates
  const allMessages = React.useMemo(() => {
    const messageMap = new Map<string, Message>();

    // Add API messages first
    apiMessages.forEach((msg) => {
      messageMap.set(msg.message_id, msg);
    });

    // Add/update with WebSocket messages
    wsRoomMessages.forEach((msg) => {
      messageMap.set(msg.message_id, msg);
    });

    // Sort by created_at
    return Array.from(messageMap.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
  }, [apiMessages, wsRoomMessages]);

  // Join/leave room on selection
  useEffect(() => {
    if (selectedRoom) {
      joinRoom(selectedRoom.room_id);
      chatService.markAsRead(selectedRoom.room_id).then(() => {
        queryClient.invalidateQueries({
          queryKey: ["chat-rooms", activeTab],
        });
      });
      return () => {
        leaveRoom(selectedRoom.room_id);
      };
    }
  }, [selectedRoom, joinRoom, leaveRoom, queryClient, activeTab]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [allMessages]);

  const filteredRooms = rooms.filter((room) =>
    room.room_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if ((!messageInput.trim() && selectedFiles.length === 0) || !selectedRoom) return;

    sendMessageMutation.mutate({
      content: messageInput.trim() || (selectedFiles.length > 0 ? "파일을 공유했습니다" : ""),
      message_type: "text",
    });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      // Validate file sizes (10MB for images, 50MB for files)
      const validFiles: File[] = [];
      for (const file of files) {
        const isImage = file.type.startsWith("image/");
        const maxSize = isImage ? 10 * 1024 * 1024 : 50 * 1024 * 1024;
        if (file.size > maxSize) {
          toast.error(`${file.name}의 크기가 너무 큽니다 (최대 ${isImage ? "10MB" : "50MB"})`);
          continue;
        }
        validFiles.push(file);
      }
      setSelectedFiles((prev) => [...prev, ...validFiles]);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleEditMessage = (messageId: string, newContent: string) => {
    updateMessageMutation.mutate({ messageId, content: newContent });
  };

  const handleDeleteMessage = (messageId: string) => {
    deleteMessageMutation.mutate(messageId);
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
                <ChatRoomItem
                  key={room.room_id}
                  room={room}
                  isSelected={selectedRoom?.room_id === room.room_id}
                  currentUserId={user?.id || ""}
                  onClick={() => setSelectedRoom(room)}
                />
              ))
            )}
          </div>

          {/* Unread Count Summary */}
          <div className="p-3 border-t border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-600 dark:text-slate-400">
                총 {rooms.reduce((sum, r) => sum + r.unread_count, 0)}개의 읽지 않은 메시지
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
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar className="w-10 h-10">
                      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white font-medium">
                        {selectedRoom.room_name?.slice(0, 2).toUpperCase() || "CH"}
                      </AvatarFallback>
                    </Avatar>
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
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        isConnected ? "bg-green-500" : "bg-red-500"
                      }`}
                      title={isConnected ? "연결됨" : "연결 끊김"}
                    />
                  </div>
                </div>
              </div>

              {/* Messages */}
              <ScrollArea className="flex-1 bg-white dark:bg-slate-900">
                <div className="p-4 space-y-4">
                  {allMessages.length === 0 ? (
                    <div className="text-center text-slate-500 dark:text-slate-400 py-8">
                      메시지가 없습니다. 대화를 시작하세요!
                    </div>
                  ) : (
                    <>
                      {allMessages.map((message, index) => {
                        const isOwn = message.sender_id === user?.id;
                        const prevMessage = index > 0 ? allMessages[index - 1] : null;
                        const showAvatar = !prevMessage || prevMessage.sender_id !== message.sender_id;
                        const showSenderName = !prevMessage || prevMessage.sender_id !== message.sender_id;

                        return (
                          <MessageItem
                            key={message.message_id}
                            message={message}
                            isOwn={isOwn}
                            currentUserId={user?.id || ""}
                            onEdit={handleEditMessage}
                            onDelete={handleDeleteMessage}
                            showAvatar={showAvatar}
                            showSenderName={showSenderName}
                          />
                        );
                      })}
                      {/* Typing Indicator */}
                      {selectedRoom && typingUsers.has(selectedRoom.room_id) && (
                        <div className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground italic">
                          <div className="flex gap-1">
                            <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                            <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                            <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                          </div>
                          <span>
                            {Array.from(typingUsers.get(selectedRoom.room_id) || [])
                              .filter((id) => id !== user?.id)
                              .join(", ") || "누군가"}
                            가 입력 중...
                          </span>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </>
                  )}
                </div>
              </ScrollArea>

              {/* Message Input */}
              <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                {/* Selected Files Preview */}
                {selectedFiles.length > 0 && (
                  <div className="mb-2">
                    <div className="flex flex-wrap gap-2">
                      {selectedFiles.map((file, index) => (
                        <FilePreview
                          key={index}
                          file={file}
                          onRemove={() => handleRemoveFile(index)}
                        />
                      ))}
                    </div>
                  </div>
                )}

                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    className="hidden"
                    onChange={handleFileSelect}
                    accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={!isConnected || isUploading}
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>
                  <Input
                    type="text"
                    placeholder="메시지를 입력하세요..."
                    value={messageInput}
                    onChange={(e) => {
                      setMessageInput(e.target.value);
                      // Send typing indicator
                      if (selectedRoom && isConnected) {
                        // Clear existing timeout
                        if (typingTimeoutRef.current) {
                          clearTimeout(typingTimeoutRef.current);
                        }
                        // Send typing indicator
                        sendTyping(selectedRoom.room_id);
                        // Set timeout to stop sending (debounce)
                        typingTimeoutRef.current = setTimeout(() => {
                          // Typing indicator will auto-clear after 3 seconds on server
                        }, 1000);
                      }
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        if (
                          (messageInput.trim() || selectedFiles.length > 0) &&
                          !sendMessageMutation.isPending &&
                          !isUploading
                        ) {
                          handleSendMessage(e);
                        }
                      }
                    }}
                    className="flex-1"
                    disabled={!isConnected || isUploading}
                  />
                  <Button
                    type="submit"
                    disabled={
                      (!messageInput.trim() && selectedFiles.length === 0) ||
                      sendMessageMutation.isPending ||
                      !isConnected ||
                      isUploading
                    }
                    className="bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    {isUploading ? (
                      "업로드 중..."
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        전송
                      </>
                    )}
                  </Button>
                </form>
                {!isConnected && (
                  <p className="text-xs text-red-500 mt-2">
                    연결이 끊어졌습니다. 메시지를 보낼 수 없습니다.
                  </p>
                )}
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

interface ChatRoomItemProps {
  room: ChatRoom;
  isSelected: boolean;
  currentUserId: string;
  onClick: () => void;
}

function ChatRoomItem({ room, isSelected, currentUserId, onClick }: ChatRoomItemProps) {
  const getRoomDisplayName = () => {
    if (room.room_name) return room.room_name;
    if (room.room_type === "direct") return "1:1 대화";
    if (room.room_type === "team") return "팀 채팅";
    if (room.room_type === "matching") return "매칭 채팅";
    return "이름 없음";
  };

  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const formatTime = (dateString: string | null) => {
    if (!dateString) return "";
    return formatDistanceToNow(new Date(dateString), {
      addSuffix: true,
      locale: ko,
    });
  };

  const getLastMessagePreview = () => {
    if (room.last_message_content) {
      const isOwn = room.last_message_sender_id === currentUserId;
      const prefix = isOwn ? "나: " : "";
      return prefix + room.last_message_content;
    }
    return "메시지가 없습니다";
  };

  return (
    <button
      onClick={onClick}
      className={`w-full p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors border-l-2 ${
        isSelected
          ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
          : "border-transparent"
      }`}
    >
      <div className="flex items-start gap-3">
        <Avatar className="w-12 h-12 flex-shrink-0">
          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white">
            {getInitials(getRoomDisplayName())}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-1">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">
              {getRoomDisplayName()}
            </h3>
            {room.unread_count > 0 && (
              <Badge className="ml-2 bg-blue-500 text-white min-w-[20px] h-5 px-1.5 flex items-center justify-center">
                {room.unread_count > 99 ? "99+" : room.unread_count}
              </Badge>
            )}
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 truncate mb-1">
            {getLastMessagePreview()}
          </p>
          <div className="flex items-center justify-between">
            {room.last_message_at && (
              <p className="text-xs text-slate-400 dark:text-slate-500">
                {formatTime(room.last_message_at)}
              </p>
            )}
            {room.unread_count === 0 && room.last_message_at && (
              <div className="w-2 h-2 rounded-full bg-blue-500" />
            )}
          </div>
        </div>
      </div>
    </button>
  );
}
