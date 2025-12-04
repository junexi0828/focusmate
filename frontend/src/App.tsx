import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { HomePage } from "./pages/Home";
import { RoomPage } from "./pages/Room";
import { StatsPage } from "./pages/Stats";
import { CommunityPage } from "./pages/Community";
import { MessagesPage } from "./pages/Messages";
import { ProfilePage } from "./pages/Profile";
import { AuthPage } from "./pages/Auth";
import { Navigation } from "./components/navigation";
import { Footer } from "./components/footer";
import { ThemeToggle } from "./components/theme-toggle";
import { Toaster } from "./components/ui/sonner";
import { User } from "./types/user";
import { toast } from "sonner";
import { roomService } from "./features/room/services/roomService";
import { LoadingOverlay } from "./components/ui/loading";
import { ErrorBoundary } from "./components/ErrorBoundary";

interface RoomState {
  roomName: string;
  roomId: string;
  focusTime: number;
  breakTime: number;
}

// Component to require authentication
function ProtectedRoute({ children, user }: { children: React.ReactNode; user: User | null }) {
  if (!user) {
    toast.error("로그인이 필요한 서비스입니다");
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

// Main App Content Component
function AppContent() {
  const [roomState, setRoomState] = useState<RoomState | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleCreateRoom = async (
    roomName: string,
    focusTime: number,
    breakTime: number,
  ) => {
    setIsLoading(true);
    try {
      const response = await roomService.createRoom({
        room_name: roomName,
        work_duration_minutes: focusTime,
        break_duration_minutes: breakTime,
        auto_start_break: false,
      });

      if (response.status === "success" && response.data) {
        const room = response.data;
        setRoomState({
          roomName: room.room_name,
          roomId: room.room_id,
          focusTime: room.work_duration / 60, // seconds to minutes
          breakTime: room.break_duration / 60, // seconds to minutes
        });
        navigate(`/room/${room.room_id}`);
        toast.success("방이 생성되었습니다!");
      } else {
        const errorMessage =
          response.error?.message || "방 생성에 실패했습니다";
        toast.error(errorMessage);
      }
    } catch (error) {
      console.error("Failed to create room:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinRoom = async (roomId: string) => {
    setIsLoading(true);
    try {
      // Extract room ID from URL if full URL is provided
      const extractedRoomId = roomId.includes("/room/")
        ? roomId.split("/room/")[1].split("?")[0]
        : roomId.trim();

      const response = await roomService.getRoom(extractedRoomId);

      if (response.status === "success" && response.data) {
        const room = response.data;
        setRoomState({
          roomName: room.room_name,
          roomId: room.room_id,
          focusTime: room.work_duration / 60, // seconds to minutes
          breakTime: room.break_duration / 60, // seconds to minutes
        });
        navigate(`/room/${room.room_id}`);
        toast.success("방에 참여했습니다!");
      } else {
        if (response.error?.code === "ROOM_NOT_FOUND") {
          toast.error("방을 찾을 수 없습니다. 방 ID를 확인해주세요.");
        } else {
          const errorMessage =
            response.error?.message || "방 참여에 실패했습니다";
          toast.error(errorMessage);
        }
      }
    } catch (error) {
      console.error("Failed to join room:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLeaveRoom = () => {
    navigate("/");
    setRoomState(null);
  };

  const handleLogin = (email: string, password: string) => {
    // Mock login - in real app, this would authenticate with backend
    const mockUser: User = {
      id: "user-1",
      email,
      name: "김철수",
      bio: "포모도로 기법으로 생산성 향상 중입니다!",
      createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // 90 days ago
      totalFocusTime: 450, // 7.5 hours
      totalSessions: 36,
    };
    setUser(mockUser);
    navigate("/");
    toast.success("로그인 성공!");
  };

  const handleSignup = (email: string, password: string, name: string) => {
    // Mock signup
    const mockUser: User = {
      id: "user-new",
      email,
      name,
      createdAt: new Date(),
      totalFocusTime: 0,
      totalSessions: 0,
    };
    setUser(mockUser);
    navigate("/");
    toast.success("회원가입 성공! Focus Mate에 오신 것을 환영합니다.");
  };

  const handleLogout = () => {
    setUser(null);
    navigate("/");
    toast.success("로그아웃되었습니다");
  };

  const handleUpdateProfile = (updates: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...updates });
    }
  };

  const handleCreatePost = () => {
    toast.info("게시글 작성 기능은 곧 추가됩니다");
  };

  const handleViewPost = (postId: string) => {
    toast.info(`게시글 보기: ${postId}`);
  };

  // Check if we're on the room page
  const isRoomPage = location.pathname === "/room";

  return (
    <div className="flex flex-col min-h-screen">
      <ThemeToggle />
      <Toaster position="top-center" />
      {isLoading && <LoadingOverlay />}

      {/* Navigation - Show on all pages except room and login */}
      {!isRoomPage && location.pathname !== "/login" && (
        <Navigation user={user} unreadMessages={2} />
      )}

      {/* Main Content */}
      <main className="flex-1">
        <Routes>
          <Route
            path="/"
            element={<HomePage onCreateRoom={handleCreateRoom} onJoinRoom={handleJoinRoom} />}
          />

          <Route
            path="/room/:roomId"
            element={
              <RoomPage
                onLeaveRoom={handleLeaveRoom}
              />
            }
          />

          <Route
            path="/stats"
            element={
              <ProtectedRoute user={user}>
                <StatsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/community"
            element={
              <ProtectedRoute user={user}>
                <CommunityPage onCreatePost={handleCreatePost} onViewPost={handleViewPost} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/messages"
            element={
              <ProtectedRoute user={user}>
                <MessagesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute user={user}>
                <ProfilePage user={user!} onUpdateProfile={handleUpdateProfile} onLogout={handleLogout} />
              </ProtectedRoute>
            }
          />

          <Route
            path="/login"
            element={
              user ? (
                <Navigate to="/" replace />
              ) : (
                <AuthPage onLogin={handleLogin} onSignup={handleSignup} />
              )
            }
          />

          {/* 404 Page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {/* Footer - Show on all pages except room */}
      {!isRoomPage && <Footer />}
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ErrorBoundary>
  );
}
