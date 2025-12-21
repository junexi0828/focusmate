import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { PageTransition } from "../components/PageTransition";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Calendar,
  Clock,
  X,
  Plus,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { roomReservationService } from "../features/room-reservation/services/roomReservationService";
import { RoomReservation } from "../features/room-reservation/types/roomReservation.types";
import { toast } from "sonner";
import { authService } from "../features/auth/services/authService";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { formatDistanceToNow, format } from "date-fns";
import { ko } from "date-fns/locale";
import { useReservationNotification } from "../features/room-reservation/hooks/useReservationNotification";

export const Route = createFileRoute("/reservations")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      throw new Error("로그인이 필요합니다");
    }
  },
  component: ReservationsComponent,
});

function ReservationsComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const user = authService.getCurrentUser();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    scheduled_at: "",
    work_duration: 25,
    break_duration: 5,
    description: "",
  });

  const { data: reservations = [], isLoading } = useQuery({
    queryKey: ["reservations", "all"],
    queryFn: async () => {
      const response = await roomReservationService.getMyReservations(false);
      return response.status === "success" ? response.data : [];
    },
    enabled: !!user?.id,
  });

  const cancelMutation = useMutation({
    mutationFn: (reservationId: string) =>
      roomReservationService.cancelReservation(reservationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      toast.success("예약이 취소되었습니다");
    },
    onError: () => {
      toast.error("예약 취소에 실패했습니다");
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: {
      scheduled_at: string;
      work_duration: number;
      break_duration: number;
      description?: string | null;
    }) => roomReservationService.createReservation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      setIsDialogOpen(false);
      setFormData({
        scheduled_at: "",
        work_duration: 25,
        break_duration: 5,
        description: "",
      });
      toast.success("방 예약이 생성되었습니다");
    },
    onError: () => {
      toast.error("예약 생성에 실패했습니다");
    },
  });

  const handleCreateReservation = () => {
    if (!formData.scheduled_at || !formData.scheduled_at.trim()) {
      toast.error("예약 시간을 선택해주세요");
      return;
    }

    try {
      // datetime-local input returns format: "YYYY-MM-DDTHH:mm"
      // Convert to ISO 8601 format properly
      const localDateTime = formData.scheduled_at;

      // Validate format
      if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(localDateTime)) {
        toast.error("올바른 날짜와 시간 형식을 입력해주세요");
        return;
      }

      // Create date object from local datetime string
      // This preserves the local timezone
      const scheduledDate = new Date(localDateTime);

      // Validate date
      if (isNaN(scheduledDate.getTime())) {
        toast.error("올바른 날짜와 시간을 입력해주세요");
        return;
      }

      // Check if date is in the future
      if (scheduledDate <= new Date()) {
        toast.error("미래 시간으로 예약해주세요");
        return;
      }

      // Convert to ISO string (UTC)
      const isoString = scheduledDate.toISOString();

      createMutation.mutate({
        scheduled_at: isoString,
        work_duration: formData.work_duration * 60,
        break_duration: formData.break_duration * 60,
        description: formData.description || null,
      });
    } catch (error) {
      console.error("Failed to create reservation:", error);
      toast.error("예약 생성 중 오류가 발생했습니다");
    }
  };

  const activeReservations = reservations.filter(
    (r) => r.is_active && !r.is_completed
  );
  const upcomingReservations = activeReservations.filter(
    (r) => new Date(r.scheduled_at) > new Date()
  );
  const pastReservations = reservations.filter(
    (r) => !r.is_active || r.is_completed || new Date(r.scheduled_at) <= new Date()
  );

  // Enable reservation notifications
  useReservationNotification(upcomingReservations);

  return (
    <PageTransition>
      <div className="min-h-screen bg-muted/30">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold">방 예약 관리</h1>
              <p className="text-muted-foreground mt-1">
                예약된 집중 세션을 관리하세요
              </p>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  새 예약
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>방 예약하기</DialogTitle>
                  <DialogDescription>
                    미래에 시작할 집중 세션을 예약하세요
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="scheduled_at">예약 시간</Label>
                    <Input
                      id="scheduled_at"
                      type="datetime-local"
                      value={formData.scheduled_at}
                      onChange={(e) =>
                        setFormData({ ...formData, scheduled_at: e.target.value })
                      }
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="work_duration">집중 시간 (분)</Label>
                      <Input
                        id="work_duration"
                        type="number"
                        min="1"
                        max="60"
                        value={formData.work_duration}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            work_duration: parseInt(e.target.value) || 25,
                          })
                        }
                      />
                    </div>
                    <div>
                      <Label htmlFor="break_duration">휴식 시간 (분)</Label>
                      <Input
                        id="break_duration"
                        type="number"
                        min="1"
                        max="30"
                        value={formData.break_duration}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            break_duration: parseInt(e.target.value) || 5,
                          })
                        }
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="description">설명 (선택)</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) =>
                        setFormData({ ...formData, description: e.target.value })
                      }
                      placeholder="예약에 대한 메모를 입력하세요"
                    />
                  </div>
                  <Button
                    onClick={handleCreateReservation}
                    className="w-full"
                    disabled={createMutation.isPending}
                  >
                    예약하기
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">로딩 중...</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Upcoming Reservations */}
              {upcomingReservations.length > 0 && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">다가오는 예약</h2>
                  <div className="grid gap-4">
                    {upcomingReservations.map((reservation) => (
                      <ReservationCard
                        key={reservation.id}
                        reservation={reservation}
                        onCancel={() => {
                          if (confirm("정말 취소하시겠습니까?")) {
                            cancelMutation.mutate(reservation.id);
                          }
                        }}
                        onJoin={() => {
                          if (reservation.room_id) {
                            navigate({ to: `/room/${reservation.room_id}` });
                          }
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Past Reservations */}
              {pastReservations.length > 0 && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">과거 예약</h2>
                  <div className="grid gap-4">
                    {pastReservations.map((reservation) => (
                      <ReservationCard
                        key={reservation.id}
                        reservation={reservation}
                        onCancel={() => {
                          if (confirm("정말 취소하시겠습니까?")) {
                            cancelMutation.mutate(reservation.id);
                          }
                        }}
                        onJoin={() => {
                          if (reservation.room_id) {
                            navigate({ to: `/room/${reservation.room_id}` });
                          }
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {reservations.length === 0 && (
                <Card>
                  <CardContent className="py-12 text-center">
                    <Calendar className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <p className="text-lg font-medium text-muted-foreground mb-2">
                      예약된 방이 없습니다
                    </p>
                    <p className="text-sm text-muted-foreground">
                      새 예약을 만들어 시작하세요
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}

interface ReservationCardProps {
  reservation: RoomReservation;
  onCancel: () => void;
  onJoin?: () => void;
}

function ReservationCard({
  reservation,
  onCancel,
  onJoin,
}: ReservationCardProps) {
  const [timeRemaining, setTimeRemaining] = useState<string>("");

  useEffect(() => {
    const updateTimeRemaining = () => {
      const now = new Date();
      const scheduled = new Date(reservation.scheduled_at);
      const diff = scheduled.getTime() - now.getTime();

      if (diff <= 0) {
        setTimeRemaining("예약 시간이 지났습니다");
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

      if (days > 0) {
        setTimeRemaining(`${days}일 ${hours}시간 후`);
      } else if (hours > 0) {
        setTimeRemaining(`${hours}시간 ${minutes}분 후`);
      } else {
        setTimeRemaining(`${minutes}분 후`);
      }
    };

    updateTimeRemaining();
    const interval = setInterval(updateTimeRemaining, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [reservation.scheduled_at]);

  const isUpcoming = new Date(reservation.scheduled_at) > new Date();
  const isPast = new Date(reservation.scheduled_at) <= new Date();
  const canJoin = reservation.room_id && isUpcoming;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <CardTitle className="text-lg">
                {format(new Date(reservation.scheduled_at), "yyyy년 M월 d일 HH:mm", {
                  locale: ko,
                })}
              </CardTitle>
              {isUpcoming && (
                <Badge variant="default" className="ml-2">
                  예정
                </Badge>
              )}
              {isPast && (
                <Badge variant="secondary" className="ml-2">
                  완료
                </Badge>
              )}
              {!reservation.is_active && (
                <Badge variant="outline" className="ml-2">
                  취소됨
                </Badge>
              )}
            </div>
            {isUpcoming && reservation.is_active && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span>{timeRemaining}</span>
              </div>
            )}
          </div>
          {isUpcoming && reservation.is_active && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onCancel}
              className="text-destructive"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span>
                {reservation.work_duration / 60}분 집중 ·{" "}
                {reservation.break_duration / 60}분 휴식
              </span>
            </div>
          </div>
          {reservation.description && (
            <p className="text-sm text-muted-foreground">{reservation.description}</p>
          )}
          {canJoin && (
            <Button
              onClick={onJoin}
              className="w-full"
              variant="default"
            >
              <ArrowRight className="w-4 h-4 mr-2" />
              방 입장하기
            </Button>
          )}
          {isPast && reservation.room_id && (
            <Button
              onClick={onJoin}
              className="w-full"
              variant="outline"
            >
              방 보기
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

