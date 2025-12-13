import { Conversation } from "../../../types/message";
import { Avatar, AvatarFallback } from "../../../components/ui/avatar";
import { ScrollArea } from "../../../components/ui/scroll-area";
import { Badge } from "../../../components/ui/badge";
import { cn } from "../../../components/ui/utils";

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversationId: string | null;
  onSelectConversation: (id: string) => void;
  currentUserId: string;
}

export function ConversationList({
  conversations,
  selectedConversationId,
  onSelectConversation,
  currentUserId: _currentUserId,
}: ConversationListProps) {
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

    if (diffInMinutes < 1) return "방금";
    if (diffInMinutes < 60) return `${diffInMinutes}분 전`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}시간 전`;
    if (diffInMinutes < 10080)
      return `${Math.floor(diffInMinutes / 1440)}일 전`;
    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="border-r bg-background h-full flex flex-col min-w-0 overflow-hidden">
      <div className="p-4 border-b flex-shrink-0">
        <h3 className="font-semibold text-lg">대화</h3>
      </div>
      <ScrollArea className="flex-1 min-w-0">
        <div className="p-2 space-y-1 min-w-0">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => onSelectConversation(conversation.id)}
              className={cn(
                "w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 min-w-0",
                selectedConversationId === conversation.id
                  ? "bg-primary/10 border border-primary/20 shadow-sm"
                  : "hover:bg-muted/50 border border-transparent"
              )}
            >
              {/* 아바타 with Online Status (Discourse 스타일) */}
              <div className="relative">
                <Avatar className="w-10 h-10">
                  <AvatarFallback className="bg-secondary text-secondary-foreground">
                    {getInitials(conversation.participantName)}
                  </AvatarFallback>
                </Avatar>
                {/* 온라인 상태 표시기 - Discourse 스타일 */}
                <div className="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-green-500 border-2 border-background" />
              </div>

              <div className="flex-1 min-w-0 text-left">
                <div className="flex items-center justify-between mb-1">
                  <p className="truncate font-medium text-sm">
                    {conversation.participantName}
                  </p>
                  {conversation.unreadCount > 0 && (
                    <Badge
                      variant="default"
                      className="ml-2 min-w-[20px] h-5 px-1 flex items-center justify-center"
                    >
                      {conversation.unreadCount}
                    </Badge>
                  )}
                </div>

                {/* 마지막 메시지 미리보기 - Discourse 스타일 */}
                {conversation.lastMessage && (
                  <p className="text-sm text-muted-foreground truncate">
                    {conversation.lastMessage}
                  </p>
                )}

                {/* 시간 및 상태 정보 - Discourse 스타일 */}
                <div className="flex items-center justify-between mt-1">
                  {conversation.lastMessageTime && (
                    <p className="text-xs text-muted-foreground">
                      {formatTime(conversation.lastMessageTime)}
                    </p>
                  )}

                  {/* 읽음 상태 표시 (Discourse 스타일) */}
                  {conversation.unreadCount === 0 && (
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
