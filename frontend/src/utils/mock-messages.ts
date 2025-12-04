import { Message, Conversation } from "../types/message";

export const mockConversations: Conversation[] = [
  {
    id: "conv-1",
    participantId: "user-2",
    participantName: "이영희",
    lastMessage: "내일 함께 집중 시간 가져요!",
    lastMessageTime: new Date(Date.now() - 30 * 60 * 1000),
    unreadCount: 2,
  },
  {
    id: "conv-2",
    participantId: "user-3",
    participantName: "박민수",
    lastMessage: "오늘 작업 고생하셨습니다 👍",
    lastMessageTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
    unreadCount: 0,
  },
  {
    id: "conv-3",
    participantId: "user-4",
    participantName: "최지은",
    lastMessage: "포모도로 팁 감사합니다!",
    lastMessageTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    unreadCount: 0,
  },
];

export const mockMessages: Message[] = [
  {
    id: "msg-1",
    conversationId: "conv-1",
    senderId: "user-2",
    senderName: "이영희",
    content: "안녕하세요! 포모도로 타이머 같이 사용하실래요?",
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    isRead: true,
  },
  {
    id: "msg-2",
    conversationId: "conv-1",
    senderId: "user-1",
    senderName: "김철수",
    content: "네 좋아요! 언제 하시면 될까요?",
    createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    isRead: true,
  },
  {
    id: "msg-3",
    conversationId: "conv-1",
    senderId: "user-2",
    senderName: "이영희",
    content: "내일 오전 10시 어떠세요?",
    createdAt: new Date(Date.now() - 40 * 60 * 1000),
    isRead: true,
  },
  {
    id: "msg-4",
    conversationId: "conv-1",
    senderId: "user-2",
    senderName: "이영희",
    content: "내일 함께 집중 시간 가져요!",
    createdAt: new Date(Date.now() - 30 * 60 * 1000),
    isRead: false,
  },
];
