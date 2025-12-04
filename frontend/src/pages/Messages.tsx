import React, { useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import { ScrollArea } from "../components/ui/scroll-area";
import { mockConversations, mockMessages } from "../utils/mock-messages";
import { Conversation, Message } from "../types/message";
import { Send, MessageCircle } from "lucide-react";
import { cn } from "../components/ui/utils";

export function MessagesPage() {
  const [conversations] = useState<Conversation[]>(mockConversations);
  const [selectedConversationId, setSelectedConversationId] = useState<
    string | null
  >(conversations[0]?.id || null);
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [newMessage, setNewMessage] = useState("");

  const currentUserId = "user-1"; // Mock current user

  const selectedConversation = conversations.find(
    (c) => c.id === selectedConversationId
  );
  const conversationMessages = messages.filter(
    (m) => m.conversationId === selectedConversationId
  );

  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60)
    );

    if (diffInMinutes < 60) return `${diffInMinutes}분 전`;
    if (diffInMinutes < 1440)
      return date.toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
      });
    if (diffInMinutes < 10080)
      return date.toLocaleDateString("ko-KR", {
        month: "short",
        day: "numeric",
      });
    return date.toLocaleDateString("ko-KR");
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();

    if (!newMessage.trim() || !selectedConversationId) return;

    const message: Message = {
      id: `msg-${Date.now()}`,
      conversationId: selectedConversationId,
      senderId: currentUserId,
      senderName: "김철수",
      content: newMessage.trim(),
      createdAt: new Date(),
      isRead: true,
    };

    setMessages([...messages, message]);
    setNewMessage("");
  };

  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-primary-foreground" />
            </div>
            <h1>메시지</h1>
          </div>
          <p className="text-muted-foreground">팀원들과 소통하세요</p>
        </div>

        {/* Messages Container */}
        <Card className="h-[calc(100vh-250px)]">
          <div className="grid md:grid-cols-[350px_1fr] h-full">
            {/* Conversations List */}
            <div className="border-r">
              <div className="p-4 border-b">
                <h3>대화</h3>
              </div>
              <ScrollArea className="h-[calc(100%-73px)]">
                <div className="p-2">
                  {conversations.map((conversation) => (
                    <button
                      key={conversation.id}
                      onClick={() => setSelectedConversationId(conversation.id)}
                      className={cn(
                        "w-full flex items-center gap-3 p-3 rounded-lg transition-colors",
                        selectedConversationId === conversation.id
                          ? "bg-primary/10"
                          : "hover:bg-muted"
                      )}
                    >
                      <Avatar>
                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                          {getInitials(conversation.participantName)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0 text-left">
                        <div className="flex items-center justify-between mb-1">
                          <p className="truncate">
                            {conversation.participantName}
                          </p>
                          {conversation.unreadCount > 0 && (
                            <span className="w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center flex-shrink-0">
                              {conversation.unreadCount}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          {conversation.lastMessage}
                        </p>
                        {conversation.lastMessageTime && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatTime(conversation.lastMessageTime)}
                          </p>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </ScrollArea>
            </div>

            {/* Chat Area */}
            {selectedConversation ? (
              <div className="flex flex-col h-full">
                {/* Chat Header */}
                <div className="p-4 border-b flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback className="bg-secondary text-secondary-foreground">
                      {getInitials(selectedConversation.participantName)}
                    </AvatarFallback>
                  </Avatar>
                  <h3>{selectedConversation.participantName}</h3>
                </div>

                {/* Messages */}
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {conversationMessages.map((message) => {
                      const isCurrentUser = message.senderId === currentUserId;
                      return (
                        <div
                          key={message.id}
                          className={cn(
                            "flex",
                            isCurrentUser ? "justify-end" : "justify-start"
                          )}
                        >
                          <div
                            className={cn(
                              "max-w-[70%] rounded-lg p-3",
                              isCurrentUser
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted"
                            )}
                          >
                            {!isCurrentUser && (
                              <p className="text-xs text-muted-foreground mb-1">
                                {message.senderName}
                              </p>
                            )}
                            <p className="break-words">{message.content}</p>
                            <p
                              className={cn(
                                "text-xs mt-1",
                                isCurrentUser
                                  ? "text-primary-foreground/70"
                                  : "text-muted-foreground"
                              )}
                            >
                              {message.createdAt.toLocaleTimeString("ko-KR", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>

                {/* Message Input */}
                <div className="p-4 border-t">
                  <form onSubmit={handleSendMessage} className="flex gap-2">
                    <Input
                      placeholder="메시지를 입력하세요..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      className="flex-1"
                    />
                    <Button type="submit" size="icon">
                      <Send className="w-4 h-4" />
                    </Button>
                  </form>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-muted-foreground">
                  <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>대화를 선택하세요</p>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
