import { useEffect, useState } from "react";
import { PageTransition } from "../components/PageTransition";
import { motion } from "framer-motion";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  getSettings,
  updateSettings,
  changePassword,
  changeEmail,
} from "../api/settings";
import { UserSettings } from "../types/settings";
import { toast } from "sonner";
import { Loader2, Lock, Bell, Palette, AlertTriangle } from "lucide-react";
import { getErrorMessage } from "../utils/error";
import { useTheme } from "../hooks/useTheme";
import { authService } from "../features/auth/services/authService";
import { useNavigate } from "@tanstack/react-router";

export default function Settings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { isFunMode, toggleFunMode } = useTheme();

  // Password change form
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  // Email change form
  const [emailForm, setEmailForm] = useState({
    new_email: "",
    password: "",
  });

  // Account deletion form
  const [deleteForm, setDeleteForm] = useState({
    password: "",
    confirmation: "",
  });
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  // Sync settings theme with current localStorage theme on initial load
  useEffect(() => {
    if (settings) {
      const currentTheme = localStorage.getItem("theme");
      // If localStorage has a theme but settings don't match, update settings to match localStorage
      // This ensures Settings page shows the current active theme
      if (currentTheme && settings.theme !== currentTheme) {
        setSettings({ ...settings, theme: currentTheme as 'light' | 'dark' | 'system' });
      }
    }
  }, [settings?.theme]); // Only run when settings first load

  // Helper function to apply theme (consistent with __root.tsx)
  const applyTheme = (theme: 'light' | 'dark' | 'system') => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
      localStorage.removeItem("theme"); // Remove explicit theme to follow system
    } else {
      root.classList.add(theme);
      localStorage.setItem("theme", theme);
    }
  };

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await getSettings();
      setSettings(data);
    } catch (error: any) {
      console.error("Failed to load settings:", error);
      const errorMessage = getErrorMessage(error, "설정을 불러오는데 실패했습니다");
      toast.error(errorMessage);
      // If unauthorized, redirect to login
      if (error?.response?.status === 401) {
        window.location.href = "/login";
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSettings = async (updates: Partial<UserSettings>) => {
    if (!settings) return;

    setSaving(true);
    try {
      const updated = await updateSettings(updates);
      setSettings(updated);

      // Apply theme immediately if theme was updated
      if (updates.theme !== undefined) {
        applyTheme(updates.theme);
        // Also update localStorage for consistency with sidebar
        localStorage.setItem("theme", updates.theme === "system" ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : updates.theme);
      }

      toast.success("설정이 저장되었습니다");
    } catch (error: any) {
      toast.error(getErrorMessage(error, "설정 저장에 실패했습니다"));
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error("새 비밀번호가 일치하지 않습니다");
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error("비밀번호는 최소 8자 이상이어야 합니다");
      return;
    }

    try {
      await changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });
      toast.success("비밀번호가 변경되었습니다");
      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error: any) {
      toast.error(getErrorMessage(error, "비밀번호 변경에 실패했습니다"));
    }
  };

  const handleEmailChange = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await changeEmail({
        new_email: emailForm.new_email,
        password: emailForm.password,
      });
      toast.success("이메일이 변경되었습니다. 새 이메일을 인증해주세요.");
      setEmailForm({ new_email: "", password: "" });
    } catch (error: any) {
      toast.error(getErrorMessage(error, "이메일 변경에 실패했습니다"));
    }
  };

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();

    if (deleteForm.confirmation !== "계정 삭제") {
      toast.error("'계정 삭제'를 정확히 입력해주세요");
      return;
    }

    if (!deleteForm.password) {
      toast.error("비밀번호를 입력해주세요");
      return;
    }

    setIsDeleting(true);
    try {
      const response = await authService.deleteAccount(deleteForm.password);
      if (response.status === "success") {
        toast.success("계정이 삭제되었습니다");
        setTimeout(() => {
          navigate({ to: "/login" });
        }, 1000);
      } else {
        toast.error(response.error?.message || "계정 삭제에 실패했습니다");
      }
    } catch (error: any) {
      toast.error(getErrorMessage(error, "계정 삭제에 실패했습니다"));
    } finally {
      setIsDeleting(false);
    }
  };

  if (loading || !settings) {
    return (
      <PageTransition>
        <div className="min-h-full">
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-bold">설정</h1>
        <p className="text-muted-foreground mt-1">
          계정 및 앱 설정을 관리하세요
        </p>
      </div>

          <Tabs defaultValue="account" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="account">
                <Lock className="h-4 w-4 mr-2" />
                계정
              </TabsTrigger>
              <TabsTrigger value="notifications">
                <Bell className="h-4 w-4 mr-2" />
                알림
              </TabsTrigger>
              <TabsTrigger value="appearance">
                <Palette className="h-4 w-4 mr-2" />
                테마
              </TabsTrigger>
            </TabsList>

            {/* Account Settings */}
            <TabsContent value="account" className="space-y-6">
              {/* Password Change */}
              <Card>
                <CardHeader>
                  <CardTitle>비밀번호 변경</CardTitle>
                  <CardDescription>
                    계정의 비밀번호를 변경합니다
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordChange} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current-password">현재 비밀번호</Label>
                      <Input
                        id="current-password"
                        type="password"
                        autoComplete="current-password"
                        value={passwordForm.current_password}
                        onChange={(e) =>
                          setPasswordForm({
                            ...passwordForm,
                            current_password: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-password">새 비밀번호</Label>
                      <Input
                        id="new-password"
                        type="password"
                        autoComplete="new-password"
                        value={passwordForm.new_password}
                        onChange={(e) =>
                          setPasswordForm({
                            ...passwordForm,
                            new_password: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirm-password">비밀번호 확인</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        autoComplete="new-password"
                        value={passwordForm.confirm_password}
                        onChange={(e) =>
                          setPasswordForm({
                            ...passwordForm,
                            confirm_password: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <Button type="submit">비밀번호 변경</Button>
                  </form>
                </CardContent>
              </Card>

              {/* Email Change */}
              <Card>
                <CardHeader>
                  <CardTitle>이메일 변경</CardTitle>
                  <CardDescription>
                    계정의 이메일 주소를 변경합니다
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleEmailChange} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="new-email">새 이메일</Label>
                      <Input
                        id="new-email"
                        type="email"
                        value={emailForm.new_email}
                        onChange={(e) =>
                          setEmailForm({
                            ...emailForm,
                            new_email: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email-password">비밀번호 확인</Label>
                      <Input
                        id="email-password"
                        type="password"
                        autoComplete="current-password"
                        value={emailForm.password}
                        onChange={(e) =>
                          setEmailForm({
                            ...emailForm,
                            password: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <Button type="submit">이메일 변경</Button>
                  </form>
                </CardContent>
              </Card>

              {/* Account Deletion - Danger Zone */}
              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-destructive">
                    <AlertTriangle className="h-5 w-5" />
                    위험 구역
                  </CardTitle>
                  <CardDescription>
                    계정을 영구적으로 삭제합니다. 이 작업은 되돌릴 수 없습니다.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleDeleteAccount} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="delete-confirmation">
                        계속하려면 <strong className="text-destructive">'계정 삭제'</strong>를 입력하세요
                      </Label>
                      <Input
                        id="delete-confirmation"
                        type="text"
                        placeholder="계정 삭제"
                        value={deleteForm.confirmation}
                        onChange={(e) =>
                          setDeleteForm({
                            ...deleteForm,
                            confirmation: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="delete-password">비밀번호 확인</Label>
                      <Input
                        id="delete-password"
                        type="password"
                        autoComplete="current-password"
                        value={deleteForm.password}
                        onChange={(e) =>
                          setDeleteForm({
                            ...deleteForm,
                            password: e.target.value,
                          })
                        }
                        required
                      />
                    </div>
                    <Button
                      type="submit"
                      variant="destructive"
                      disabled={isDeleting || deleteForm.confirmation !== "계정 삭제"}
                    >
                      {isDeleting ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          삭제 중...
                        </>
                      ) : (
                        "계정 영구 삭제"
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Notification Settings */}
            <TabsContent value="notifications" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>알림 설정</CardTitle>
                  <CardDescription>
                    받고 싶은 알림을 선택하세요
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="notification-email">이메일 알림</Label>
                      <p className="text-sm text-muted-foreground">
                        이메일로 알림을 받습니다
                      </p>
                    </div>
                    <Switch
                      id="notification-email"
                      checked={settings.notification_email}
                      onCheckedChange={(checked: boolean) =>
                        handleUpdateSettings({ notification_email: checked })
                      }
                      disabled={saving}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="notification-push">푸시 알림</Label>
                      <p className="text-sm text-muted-foreground">
                        브라우저 푸시 알림을 받습니다
                      </p>
                    </div>
                    <Switch
                      id="notification-push"
                      checked={settings.notification_push}
                      onCheckedChange={(checked: boolean) =>
                        handleUpdateSettings({ notification_push: checked })
                      }
                      disabled={saving}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="notification-session">세션 알림</Label>
                      <p className="text-sm text-muted-foreground">
                        세션 시작/종료 알림을 받습니다
                      </p>
                    </div>
                    <Switch
                      id="notification-session"
                      checked={settings.notification_session}
                      onCheckedChange={(checked: boolean) =>
                        handleUpdateSettings({ notification_session: checked })
                      }
                      disabled={saving}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="notification-achievement">업적 알림</Label>
                      <p className="text-sm text-muted-foreground">
                        업적 달성 알림을 받습니다
                      </p>
                    </div>
                    <Switch
                      id="notification-achievement"
                      checked={settings.notification_achievement}
                      onCheckedChange={(checked: boolean) =>
                        handleUpdateSettings({ notification_achievement: checked })
                      }
                      disabled={saving}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="notification-message">메시지 알림</Label>
                      <p className="text-sm text-muted-foreground">
                        새 메시지 알림을 받습니다
                      </p>
                    </div>
                    <Switch
                      id="notification-message"
                      checked={settings.notification_message}
                      onCheckedChange={(checked: boolean) =>
                        handleUpdateSettings({ notification_message: checked })
                      }
                      disabled={saving}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Appearance Settings */}
            <TabsContent value="appearance" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>테마 설정</CardTitle>
                  <CardDescription>
                    앱의 외관을 설정합니다
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>테마</Label>
                    <div className="grid grid-cols-3 gap-4">
                      {["light", "dark", "system"].map((theme) => (
                        <Button
                          key={theme}
                          variant={settings.theme === theme ? "default" : "outline"}
                          onClick={() =>
                            handleUpdateSettings({ theme: theme as any })
                          }
                          disabled={saving}
                        >
                          {theme === "light" && "라이트"}
                          {theme === "dark" && "다크"}
                          {theme === "system" && "시스템"}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="fun-mode" className="text-base">3D 이펙트 (Fun 모드)</Label>
                      <p className="text-sm text-muted-foreground">
                        배경에 부유하는 3D 오브젝트 효과를 적용합니다 (다크 모드와 함께 사용 가능)
                      </p>
                    </div>
                    <Switch
                      id="fun-mode"
                      checked={isFunMode}
                      onCheckedChange={toggleFunMode}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="language">언어</Label>
                    <Input
                      id="language"
                      value={settings.language}
                      onChange={(e) =>
                        handleUpdateSettings({ language: e.target.value })
                      }
                      disabled={saving}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
    </motion.div>
  );
}
