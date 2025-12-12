import { createFileRoute } from '@tanstack/react-router';
import { RoomPage } from '../pages/Room';
import { useNavigate } from '@tanstack/react-router';

export const Route = createFileRoute('/room/$roomId')({
  component: RoomComponent,
});

function RoomComponent() {
  const navigate = useNavigate();

  const handleLeaveRoom = () => {
    navigate({ to: '/' });
  };

  return <RoomPage onLeaveRoom={handleLeaveRoom} />;
}

