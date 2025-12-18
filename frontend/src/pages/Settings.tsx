import { useEffect, useState } from "react";
import { PageTransition } from "../components/PageTransition";
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
import { Loader2, Settings as SettingsIcon, Lock, Mail, Bell, Palette } from "lucide-react";

export default function Settings() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

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

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await getSettings();
      setSettings(data);
    } catch (error) {
      toast.error("설정을 불러오는데 실패했습니다");
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
      toast.success("설정이 저장되었습니다");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "설정 저장에 실패했습니다");
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
      toast.error(error.response?.data?.detail || "비밀번호 변경에 실패했습니다");
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
      toast.error(error.response?.data?.detail || "이메일 변경에 실패했습니다");
    }
  };

  if (loading || !settings) {
    return (
      <PageTransition>
        <div className="min-h-full flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-full bg-background p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <SettingsIcon className="h-8 w-8" />
            <h1 className="text-3xl font-bold">설정</h1>
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
                      onCheckedChange={(checked) =>
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
                      onCheckedChange={(checked) =>
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
                      onCheckedChange={(checked) =>
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
                      onCheckedChange={(checked) =>
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
                      onCheckedChange={(checked) =>
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
        </div>
      </div>
    </PageTransition>
  );
}
