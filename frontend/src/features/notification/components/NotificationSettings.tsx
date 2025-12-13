import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button-enhanced";
import { Badge } from "../../../components/ui/badge";
import { Bell, BellOff, CheckCircle2, XCircle, AlertCircle, Settings } from "lucide-react";
import { notificationService, NotificationPermission } from "../../../lib/notificationService";
import { toast } from "sonner";
import { Switch } from "../../../components/ui/switch";
import { Label } from "../../../components/ui/label";

export function NotificationSettings() {
  const [permission, setPermission] = useState<NotificationPermission>("default");
  const [isRequesting, setIsRequesting] = useState(false);
  const [testNotificationEnabled, setTestNotificationEnabled] = useState(true);

  useEffect(() => {
    // Update permission status
    const updatePermission = () => {
      setPermission(notificationService.getPermission());
    };

    updatePermission();

    // Check permission periodically (in case user changes it in browser settings)
    const interval = setInterval(updatePermission, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleRequestPermission = async () => {
    setIsRequesting(true);
    try {
      const newPermission = await notificationService.requestPermission();
      setPermission(newPermission);

      if (newPermission === "granted") {
        toast.success("알림 권한이 허용되었습니다!");
        // Show test notification if enabled
        if (testNotificationEnabled) {
          setTimeout(() => {
            notificationService.notify(
              "알림 테스트",
              "알림이 정상적으로 작동합니다!",
              "/favicon.ico"
            );
          }, 500);
        }
      } else if (newPermission === "denied") {
        toast.error("알림 권한이 거부되었습니다. 브라우저 설정에서 허용해주세요.");
      }
    } catch (error) {
      console.error("Failed to request notification permission:", error);
      toast.error("알림 권한 요청에 실패했습니다");
    } finally {
      setIsRequesting(false);
    }
  };

  const handleTestNotification = () => {
    if (!notificationService.isAllowed()) {
      toast.error("알림 권한이 필요합니다");
      return;
    }

    notificationService.notify(
      "알림 테스트",
      "이것은 테스트 알림입니다. 알림이 정상적으로 작동합니다!",
      "/favicon.ico"
    );
    toast.success("테스트 알림을 전송했습니다");
  };

  const getPermissionBadge = () => {
    switch (permission) {
      case "granted":
        return (
          <Badge variant="default" className="bg-green-500">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            허용됨
          </Badge>
        );
      case "denied":
        return (
          <Badge variant="destructive">
            <XCircle className="w-3 h-3 mr-1" />
            차단됨
          </Badge>
        );
      case "default":
        return (
          <Badge variant="secondary">
            <AlertCircle className="w-3 h-3 mr-1" />
            요청 필요
          </Badge>
        );
    }
  };

  const isSupported = notificationService.isSupported();

  if (!isSupported) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BellOff className="w-5 h-5" />
            알림 설정
          </CardTitle>
          <CardDescription>브라우저 알림 관리</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-muted-foreground">
            <AlertCircle className="w-4 h-4" />
            <p>이 브라우저는 알림을 지원하지 않습니다</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="w-5 h-5" />
          알림 설정
        </CardTitle>
        <CardDescription>브라우저 알림 권한 및 테스트</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Permission Status */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-base font-medium">알림 권한</Label>
              <p className="text-sm text-muted-foreground">
                {notificationService.getPermissionMessage()}
              </p>
            </div>
            {getPermissionBadge()}
          </div>

          {/* Request Permission Button */}
          {permission !== "granted" && (
            <Button
              variant="primary"
              onClick={handleRequestPermission}
              disabled={isRequesting || !notificationService.canRequestPermission()}
              className="w-full"
            >
              {isRequesting ? (
                <>
                  <Settings className="w-4 h-4 mr-2 animate-spin" />
                  권한 요청 중...
                </>
              ) : permission === "denied" ? (
                <>
                  <BellOff className="w-4 h-4 mr-2" />
                  브라우저 설정에서 허용 필요
                </>
              ) : (
                <>
                  <Bell className="w-4 h-4 mr-2" />
                  알림 권한 요청
                </>
              )}
            </Button>
          )}

          {/* Permission Denied Help */}
          {permission === "denied" && (
            <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-destructive mt-0.5" />
                <div className="space-y-2 text-sm">
                  <p className="font-medium text-destructive">
                    알림이 차단되어 있습니다
                  </p>
                  <p className="text-muted-foreground">
                    브라우저 설정에서 알림 권한을 허용해주세요:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-2">
                    <li>Chrome: 설정 → 개인정보 및 보안 → 사이트 설정 → 알림</li>
                    <li>Firefox: 설정 → 개인정보 보호 → 권한 → 알림</li>
                    <li>Safari: 환경설정 → 웹사이트 → 알림</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Test Notification */}
        {permission === "granted" && (
          <div className="space-y-4 border-t pt-6">
            <div className="space-y-2">
              <Label className="text-base font-medium">테스트 알림</Label>
              <p className="text-sm text-muted-foreground">
                알림이 정상적으로 작동하는지 확인하세요
              </p>
            </div>

            <div className="flex items-center justify-between rounded-lg border p-4">
              <div className="space-y-1">
                <Label htmlFor="test-notification" className="text-sm font-medium">
                  권한 허용 시 자동 테스트
                </Label>
                <p className="text-xs text-muted-foreground">
                  권한 허용 시 자동으로 테스트 알림을 보냅니다
                </p>
              </div>
              <Switch
                id="test-notification"
                checked={testNotificationEnabled}
                onCheckedChange={setTestNotificationEnabled}
              />
            </div>

            <Button
              variant="outline"
              onClick={handleTestNotification}
              className="w-full"
            >
              <Bell className="w-4 h-4 mr-2" />
              테스트 알림 보내기
            </Button>
          </div>
        )}

        {/* Notification Types Info */}
        <div className="space-y-2 border-t pt-6">
          <Label className="text-base font-medium">알림 유형</Label>
          <div className="space-y-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>방 예약 알림 (5분 전, 1분 전, 시작 시)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>타이머 완료 알림 (집중/휴식 시간 종료)</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>채팅 메시지 알림 (향후 추가 예정)</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

