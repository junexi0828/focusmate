import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Team, TeamMember } from "../features/ranking/services/rankingService";
import { Button } from "../components/ui/button-enhanced";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../components/ui/form";
import { Input } from "../components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Switch } from "../components/ui/switch";
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";
import { ArrowLeft, UserX, Trash2 } from "lucide-react";

const teamManagementSchema = z.object({
  team_name: z
    .string()
    .min(2, "팀 이름은 2자 이상이어야 합니다.")
    .max(50, "팀 이름은 50자를 초과할 수 없습니다."),
  team_type: z.enum(["general", "department", "lab", "club"]),
  mini_game_enabled: z.boolean(),
});

export type TeamManagementFormValues = z.infer<typeof teamManagementSchema>;

interface TeamManagementPageProps {
  team: Team;
  members: TeamMember[];
  currentUserId?: string;
  onBack: () => void;
  onUpdateTeam?: (values: TeamManagementFormValues) => void;
  onDeleteTeam?: () => void;
  onRemoveMember?: (userId: string) => void;
  onRegenerateInviteCode?: () => void;
}

export function TeamManagementPage({
  team,
  members,
  currentUserId,
  onBack,
  onUpdateTeam,
  onDeleteTeam,
  onRemoveMember,
}: TeamManagementPageProps) {
  const form = useForm<TeamManagementFormValues>({
    resolver: zodResolver(teamManagementSchema),
    defaultValues: {
      team_name: team.team_name,
      team_type: team.team_type,
      mini_game_enabled: team.mini_game_enabled,
    },
  });

  const onSubmit = (values: TeamManagementFormValues) => {
    console.log("Form submitted", values);
    onUpdateTeam?.(values);
  };

  return (
    <div className="container mx-auto max-w-4xl py-8">
      <div className="mb-6">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />팀 상세 페이지로 돌아가기
        </Button>
        <h1 className="text-3xl font-bold">팀 관리</h1>
        <p className="text-muted-foreground">
          '{team.team_name}' 팀의 설정을 변경합니다.
        </p>
      </div>

      <div className="space-y-8">
        {/* Edit Team Info Card */}
        <Card>
          <CardHeader>
            <CardTitle>팀 정보 수정</CardTitle>
            <CardDescription>팀의 기본 정보를 수정합니다.</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-6"
              >
                <FormField
                  control={form.control}
                  name="team_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>팀 이름</FormLabel>
                      <FormControl>
                        <Input placeholder="팀 이름을 입력하세요" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="team_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>팀 타입</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="팀 타입을 선택하세요" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="general">일반</SelectItem>
                          <SelectItem value="department">학과</SelectItem>
                          <SelectItem value="lab">연구실</SelectItem>
                          <SelectItem value="club">동아리</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="mini_game_enabled"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel>미니게임 활성화</FormLabel>
                        <FormDescription>
                          팀원들과 함께 미니게임을 즐길 수 있습니다.
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                <div className="flex justify-end">
                  <Button type="submit" variant="primary">
                    변경사항 저장
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>

        {/* Member Management */}
        <Card>
          <CardHeader>
            <CardTitle>멤버 관리</CardTitle>
            <CardDescription>
              {members.length}명의 멤버가 활동 중입니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {members.map((member) => (
                <div
                  key={member.member_id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    <Avatar>
                      <AvatarFallback>
                        {member.user_id.slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-semibold">
                        {member.role === "leader" ? "👑 " : ""}
                        {member.user_id}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        역할: {member.role === "leader" ? "리더" : "멤버"}
                      </p>
                    </div>
                  </div>
                  {member.role !== "leader" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRemoveMember?.(member.user_id)}
                      disabled={member.user_id === currentUserId}
                      aria-label="멤버 내보내기"
                    >
                      <UserX className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">위험 구역</CardTitle>
            <CardDescription>
              팀 삭제와 같은 위험한 작업은 신중하게 진행해주세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-destructive rounded-lg">
                <div>
                  <p className="font-semibold text-destructive">팀 삭제</p>
                  <p className="text-sm text-muted-foreground">
                    팀을 삭제하면 모든 데이터가 영구적으로 사라집니다. 이 작업은
                    되돌릴 수 없습니다.
                  </p>
                </div>
                <Button variant="destructive" onClick={onDeleteTeam} size="sm">
                  <Trash2 className="w-4 h-4 mr-2" />팀 삭제
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
