import { useState } from "react";
import { Avatar, AvatarFallback } from "../../../components/ui/avatar";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";
import { Message } from "../services/chatService";
import { MoreVertical, Edit, Trash2, Check } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../../../components/ui/dropdown-menu";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { cn } from "../../../components/ui/utils";
import { FileAttachment } from "./FileAttachment";
import { ImagePreview } from "./ImagePreview";

interface MessageItemProps {
  message: Message;
  isOwn: boolean;
  currentUserId: string;
  onEdit?: (messageId: string, newContent: string) => void;
  onDelete?: (messageId: string) => void;
  showAvatar?: boolean;
  showSenderName?: boolean;
}

export function MessageItem({
  message,
  isOwn,
  currentUserId: _currentUserId,
  onEdit,
  onDelete,
  showAvatar = true,
  showSenderName = true,
}: MessageItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [previewImageIndex, setPreviewImageIndex] = useState<number | null>(null);

  const handleEdit = () => {
    if (onEdit && editContent.trim() && editContent !== message.content) {
      onEdit(message.message_id, editContent);
      setIsEditing(false);
    } else {
      setIsEditing(false);
      setEditContent(message.content);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditContent(message.content);
  };

  const getInitials = (id: string) => {
    return id.slice(0, 2).toUpperCase();
  };

  const isImage = (url: string) => {
    return /\.(jpg|jpeg|png|gif|webp)$/i.test(url);
  };

  const imageAttachments = message.attachments?.filter((url) => isImage(url)) || [];
  const fileAttachments = message.attachments?.filter((url) => !isImage(url)) || [];

  return (
    <div
      className={cn(
        "flex gap-3 p-2 rounded-lg transition-colors group",
        isOwn ? "flex-row-reverse" : ""
      )}
    >
      {!isOwn && showAvatar && (
        <Avatar className="w-8 h-8 flex-shrink-0">
          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white text-xs">
            {getInitials(message.sender_id)}
          </AvatarFallback>
        </Avatar>
      )}

      <div className={cn("flex-1 min-w-0", isOwn ? "text-right" : "")}>
        {!isOwn && showSenderName && (
          <div className="flex items-baseline gap-2 mb-1">
            <span className="font-medium text-slate-900 dark:text-slate-100 text-sm">
              {message.sender_id}
            </span>
          </div>
        )}

        <div
          className={cn(
            "inline-block rounded-2xl px-4 py-2 max-w-[85%] sm:max-w-[75%] md:max-w-[70%]",
            isOwn
              ? "bg-primary text-primary-foreground rounded-br-md"
              : "bg-muted rounded-bl-md"
          )}
        >
          {isEditing ? (
            <div className="space-y-2">
              <Input
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleEdit();
                  } else if (e.key === "Escape") {
                    handleCancelEdit();
                  }
                }}
                className="text-sm"
                autoFocus
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleEdit}
                  className="h-6 text-xs"
                >
                  저장
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleCancelEdit}
                  className="h-6 text-xs"
                >
                  취소
                </Button>
              </div>
            </div>
          ) : (
            <>
              {/* Attachments */}
              {message.attachments && message.attachments.length > 0 && (
                <div className="space-y-2 mb-2">
                  {/* Image attachments */}
                  {imageAttachments.length > 0 && (
                    <div className="space-y-2">
                      {imageAttachments.map((url, index) => (
                        <FileAttachment
                          key={index}
                          url={url}
                          isImage={true}
                          onImageClick={() => {
                            setPreviewImageIndex(index);
                          }}
                        />
                      ))}
                    </div>
                  )}
                  {/* File attachments */}
                  {fileAttachments.length > 0 && (
                    <div className="space-y-2">
                      {fileAttachments.map((url, index) => (
                        <FileAttachment key={index} url={url} isImage={false} />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Image Preview Modal */}
              {previewImageIndex !== null && imageAttachments.length > 0 && (
                <ImagePreview
                  images={imageAttachments}
                  initialIndex={previewImageIndex}
                  isOpen={previewImageIndex !== null}
                  onClose={() => setPreviewImageIndex(null)}
                />
              )}

              {/* Message content */}
              {message.is_deleted ? (
                <p className="text-sm italic opacity-60">메시지가 삭제되었습니다</p>
              ) : (
                <p className="text-sm break-words whitespace-pre-wrap">{message.content}</p>
              )}

              {/* Message metadata */}
              <div
                className={cn(
                  "flex items-center gap-1 mt-1 text-xs",
                  isOwn ? "text-primary-foreground/70" : "text-muted-foreground"
                )}
              >
                <span className="whitespace-nowrap">
                  {formatDistanceToNow(new Date(message.created_at), {
                    addSuffix: true,
                    locale: ko,
                  })}
                </span>
                {message.is_edited && !message.is_deleted && (
                  <span>(수정됨)</span>
                )}
                {isOwn && !message.is_deleted && (
                  <span className="flex items-center ml-1" title="읽음 상태">
                    {/* Note: Read status would need to be tracked separately */}
                    {/* For now, we show single check for sent, double check for read */}
                    <Check className="w-3 h-3 opacity-60" />
                  </span>
                )}
              </div>
            </>
          )}
        </div>

        {/* Action menu (own messages only) */}
        {isOwn && !isEditing && !message.is_deleted && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreVertical className="w-3 h-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align={isOwn ? "end" : "start"}>
              <DropdownMenuItem onClick={() => setIsEditing(true)}>
                <Edit className="w-4 h-4 mr-2" />
                수정
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  if (confirm("정말 이 메시지를 삭제하시겠습니까?")) {
                    onDelete?.(message.message_id);
                  }
                }}
                className="text-destructive"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                삭제
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      {isOwn && showAvatar && (
        <Avatar className="w-8 h-8 flex-shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground text-xs">
            {getInitials(message.sender_id)}
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}

