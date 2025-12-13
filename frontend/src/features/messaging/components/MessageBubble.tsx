import { Message } from "../../../types/message";
import { Avatar, AvatarFallback } from "../../../components/ui/avatar";
import { cn } from "../../../components/ui/utils";
import { Check, CheckCheck } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
  isOwn: boolean;
  showAvatar: boolean;
  showSenderName: boolean;
}

export function MessageBubble({
  message,
  isOwn,
  showAvatar,
  showSenderName,
}: MessageBubbleProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <div className={cn("flex gap-2 group w-full min-w-0", isOwn ? "justify-end" : "justify-start")}>
      {/* 상대방 아바타 (자신의 메시지일 때는 숨김) */}
      {!isOwn && showAvatar && (
        <Avatar className="w-8 h-8 flex-shrink-0">
          <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">
            {getInitials(message.senderName)}
          </AvatarFallback>
        </Avatar>
      )}

      <div className="flex flex-col min-w-0 max-w-[85%] sm:max-w-[75%] md:max-w-[70%]">
        {/* 발신자 이름 (상대방 메시지일 때만 표시) */}
        {!isOwn && showSenderName && (
          <p className="text-xs text-muted-foreground mb-1 ml-1 truncate">
            {message.senderName}
          </p>
        )}

        {/* 메시지 버블 */}
        <div
          className={cn(
            "rounded-2xl px-4 py-2 relative min-w-0 w-full",
            isOwn
              ? "bg-primary text-primary-foreground rounded-br-md"
              : "bg-muted rounded-bl-md"
          )}
        >
          {/* 메시지 내용 - 긴 텍스트 처리 개선 */}
          <p
            className="break-words text-sm whitespace-pre-wrap"
            style={{
              wordBreak: 'break-word',
              overflowWrap: 'anywhere',
              hyphens: 'auto'
            }}
          >
            {message.content}
          </p>

          {/* 메시지 정보 (시간 + 읽음 상태) */}
          <div
            className={cn(
              "flex items-center gap-1 mt-1 text-xs flex-shrink-0",
              isOwn ? "text-primary-foreground/70" : "text-muted-foreground"
            )}
          >
            <span className="whitespace-nowrap">{formatTime(message.createdAt)}</span>

            {/* 읽음 상태 표시 (자신의 메시지일 때만) */}
            {isOwn && (
              <span className="flex items-center flex-shrink-0">
                {message.isRead ? (
                  <CheckCheck className="w-3 h-3" />
                ) : (
                  <Check className="w-3 h-3" />
                )}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 자신의 아바타 (상대방 메시지일 때는 숨김) */}
      {isOwn && showAvatar && (
        <Avatar className="w-8 h-8 flex-shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground text-xs">
            {getInitials(message.senderName)}
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}

