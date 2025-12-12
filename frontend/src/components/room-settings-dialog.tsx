import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";
import { Settings, Trash2 } from "lucide-react";

interface RoomSettingsDialogProps {
  isHost: boolean;
  focusTime: number;
  breakTime: number;
  autoStart: boolean;
  onUpdateSettings: (
    focusTime: number,
    breakTime: number,
    autoStart: boolean
  ) => void;
  onDeleteRoom: () => void;
}

export function RoomSettingsDialog({
  isHost,
  focusTime: initialFocusTime,
  breakTime: initialBreakTime,
  autoStart: initialAutoStart,
  onUpdateSettings,
  onDeleteRoom,
}: RoomSettingsDialogProps) {
  const [open, setOpen] = useState(false);
  const [focusTime, setFocusTime] = useState(initialFocusTime);
  const [breakTime, setBreakTime] = useState(initialBreakTime);
  const [autoStart, setAutoStart] = useState(initialAutoStart);

  const handleSave = () => {
    onUpdateSettings(focusTime, breakTime, autoStart);
    setOpen(false);
  };

  const handleCancel = () => {
    setFocusTime(initialFocusTime);
    setBreakTime(initialBreakTime);
    setAutoStart(initialAutoStart);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon">
          <Settings className="w-4 h-4" />
          <span className="sr-only">방 설정</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>방 설정</DialogTitle>
          <DialogDescription>타이머 설정을 조정하세요</DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <Label htmlFor="focus-time-setting">집중 시간</Label>
              <span className="text-sm text-muted-foreground">
                {focusTime}분
              </span>
            </div>
            <Slider
              id="focus-time-setting"
              min={5}
              max={60}
              step={5}
              value={[focusTime]}
              onValueChange={(value: number[]) => setFocusTime(value[0])}
              disabled={!isHost}
            />
          </div>

          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <Label htmlFor="break-time-setting">휴식 시간</Label>
              <span className="text-sm text-muted-foreground">
                {breakTime}분
              </span>
            </div>
            <Slider
              id="break-time-setting"
              min={5}
              max={30}
              step={5}
              value={[breakTime]}
              onValueChange={(value: number[]) => setBreakTime(value[0])}
              disabled={!isHost}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="auto-start" className="flex flex-col gap-1">
              <span>자동 시작</span>
              <span className="text-xs text-muted-foreground">
                휴식 후 자동으로 집중 시간 시작
              </span>
            </Label>
            <Switch
              id="auto-start"
              checked={autoStart}
              onCheckedChange={setAutoStart}
              disabled={!isHost}
            />
          </div>

          {isHost && (
            <div className="pt-4 border-t">
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" className="w-full">
                    <Trash2 className="w-4 h-4 mr-2" />방 삭제
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>방을 삭제하시겠습니까?</AlertDialogTitle>
                    <AlertDialogDescription>
                      이 작업은 취소할 수 없습니다. 방이 영구적으로 삭제되며
                      모든 참여자가 퇴장됩니다.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>취소</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={onDeleteRoom}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      삭제
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          )}

          {!isHost && (
            <p className="text-xs text-muted-foreground text-center">
              방장만 설정을 변경할 수 있습니다
            </p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel}>
            취소
          </Button>
          <Button onClick={handleSave} disabled={!isHost}>
            저장
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
