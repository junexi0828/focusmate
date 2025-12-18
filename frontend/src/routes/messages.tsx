import { createFileRoute, redirect } from '@tanstack/react-router';
import { MessagesPage } from '../pages/Messages';
import { authService } from '../features/auth/services/authService';
import { PageTransition } from '../components/PageTransition';
import { toast } from 'sonner';
import { z } from 'zod';

const messagesSearchSchema = z.object({
  roomId: z.string().optional(),
});

export const Route = createFileRoute('/messages')({
  validateSearch: messagesSearchSchema,
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error('로그인이 필요한 서비스입니다');
      throw redirect({ to: '/login' });
    }
  },
  component: MessagesComponent,
});

function MessagesComponent() {
  const { roomId } = Route.useSearch();

  return (
    <PageTransition>
      <MessagesPage initialRoomId={roomId} />
    </PageTransition>
  );
}

