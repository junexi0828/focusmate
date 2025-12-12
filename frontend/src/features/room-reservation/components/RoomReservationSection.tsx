import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Calendar, Clock, X, Plus } from "lucide-react";
import { roomReservationService } from "../services/roomReservationService";
import { RoomReservation } from "../types/roomReservation.types";
import { toast } from "sonner";
import { authService } from "../../auth/services/authService";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Textarea } from "../../../components/ui/textarea";

export function RoomReservationSection() {
  const [reservations, setReservations] = useState<RoomReservation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    scheduled_at: "",
    work_duration: 25,
    break_duration: 5,
    description: "",
  });

  useEffect(() => {
    // Only load if user is authenticated
    if (authService.isAuthenticated()) {
      loadReservations();
    } else {
      setIsLoading(false);
    }
  }, []);

  const loadReservations = async () => {
    setIsLoading(true);
    try {
      const response = await roomReservationService.getUpcomingReservations();
      if (response.status === "success" && response.data) {
        setReservations(response.data);
      }
    } catch (error) {
      console.error("Failed to load reservations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateReservation = async () => {
    if (!formData.scheduled_at) {
      toast.error("예약 시간을 선택해주세요");
      return;
    }

    try {
      const response = await roomReservationService.createReservation({
        scheduled_at: new Date(formData.scheduled_at).toISOString(),
        work_duration: formData.work_duration * 60, // 분을 초로 변환
        break_duration: formData.break_duration * 60,
        description: formData.description || null,
      });

      if (response.status === "success") {
        toast.success("방 예약이 생성되었습니다");
        setIsDialogOpen(false);
        setFormData({
          scheduled_at: "",
          work_duration: 25,
          break_duration: 5,
          description: "",
        });
        loadReservations();
      } else {
        toast.error(response.error?.message || "예약 생성에 실패했습니다");
      }
    } catch (error) {
      console.error("Failed to create reservation:", error);
      toast.error("네트워크 오류가 발생했습니다");
    }
  };

  const handleCancelReservation = async (reservationId: string) => {
    try {
      const response =
        await roomReservationService.cancelReservation(reservationId);
      if (response.status === "success") {
        toast.success("예약이 취소되었습니다");
        loadReservations();
      } else {
        toast.error(response.error?.message || "예약 취소에 실패했습니다");
      }
    } catch (error) {
      console.error("Failed to cancel reservation:", error);
      toast.error("네트워크 오류가 발생했습니다");
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Calendar className="w-4 h-4" />방 예약
          </CardTitle>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" variant="outline">
                <Plus className="w-4 h-4 mr-1" />
                예약하기
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
                <Button onClick={handleCreateReservation} className="w-full">
                  예약하기
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground text-center py-4">
            로딩 중...
          </div>
        ) : reservations.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-4">
            예약된 방이 없습니다
          </div>
        ) : (
          <div className="space-y-2">
            {reservations.slice(0, 3).map((reservation) => (
              <div
                key={reservation.id}
                className="flex items-center justify-between p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="w-3 h-3 text-muted-foreground" />
                    <span className="font-medium">
                      {formatDateTime(reservation.scheduled_at)}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {reservation.work_duration / 60}분 집중 ·{" "}
                    {reservation.break_duration / 60}분 휴식
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleCancelReservation(reservation.id)}
                  className="h-7 w-7 p-0"
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
