import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { Button } from "../../../components/ui/button-enhanced";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../../components/ui/select";
import { Switch } from "../../../components/ui/switch";
import { Loader2 } from "lucide-react";
import { TeamCreateRequest } from "../services/rankingService";

interface CreateTeamDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TeamCreateRequest) => Promise<void>;
}

export function CreateTeamDialog({
  open,
  onOpenChange,
  onSubmit,
}: CreateTeamDialogProps) {
  const [teamName, setTeamName] = useState("");
  const [teamType, setTeamType] = useState<
    "general" | "department" | "lab" | "club"
  >("general");
  const [miniGameEnabled, setMiniGameEnabled] = useState(true);
  const [affiliationInfo, setAffiliationInfo] = useState<{
    school?: string;
    department?: string;
    lab?: string;
    club?: string;
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{
    teamName?: string;
    teamType?: string;
  }>({});

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!teamName.trim()) {
      newErrors.teamName = "팀명을 입력해주세요";
    } else if (teamName.trim().length < 2) {
      newErrors.teamName = "팀명은 최소 2자 이상이어야 합니다";
    } else if (teamName.trim().length > 100) {
      newErrors.teamName = "팀명은 최대 100자까지 가능합니다";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const data: TeamCreateRequest = {
        team_name: teamName.trim(),
        team_type: teamType,
        mini_game_enabled: miniGameEnabled,
      };

      // Add affiliation info if not general
      if (teamType !== "general") {
        data.affiliation_info = affiliationInfo;
      }

      await onSubmit(data);
      // Reset form
      setTeamName("");
      setTeamType("general");
      setMiniGameEnabled(true);
      setAffiliationInfo({});
      setErrors({});
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to create team:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!isSubmitting) {
      if (!newOpen) {
        // Reset form when closing
        setTeamName("");
        setTeamType("general");
        setMiniGameEnabled(true);
        setAffiliationInfo({});
        setErrors({});
      }
      onOpenChange(newOpen);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>새 팀 만들기</DialogTitle>
          <DialogDescription>
            랭킹전에 참여할 팀을 생성하세요. 최소 4명 이상이 필요합니다.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="teamName">팀명 *</Label>
            <Input
              id="teamName"
              placeholder="팀명을 입력하세요"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              className={errors.teamName ? "border-destructive" : ""}
              maxLength={100}
            />
            {errors.teamName && (
              <p className="text-sm text-destructive">{errors.teamName}</p>
            )}
            <p className="text-xs text-muted-foreground text-right">
              {teamName.length}/100
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="teamType">소속 유형 *</Label>
            <Select
              value={teamType}
              onValueChange={(value) =>
                setTeamType(value as "general" | "department" | "lab" | "club")
              }
            >
              <SelectTrigger id="teamType">
                <SelectValue placeholder="소속 유형 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="general">일반</SelectItem>
                <SelectItem value="department">학과</SelectItem>
                <SelectItem value="lab">연구실</SelectItem>
                <SelectItem value="club">동아리</SelectItem>
              </SelectContent>
            </Select>
            {errors.teamType && (
              <p className="text-sm text-destructive">{errors.teamType}</p>
            )}
          </div>

          {/* Affiliation Info (for non-general types) */}
          {teamType !== "general" && (
            <div className="space-y-3 p-4 bg-muted/50 rounded-lg">
              <Label className="text-sm font-medium">소속 정보</Label>
              {teamType === "department" && (
                <div className="space-y-2">
                  <Input
                    placeholder="학교명 (선택)"
                    value={affiliationInfo.school || ""}
                    onChange={(e) =>
                      setAffiliationInfo({
                        ...affiliationInfo,
                        school: e.target.value,
                      })
                    }
                  />
                  <Input
                    placeholder="학과명 (선택)"
                    value={affiliationInfo.department || ""}
                    onChange={(e) =>
                      setAffiliationInfo({
                        ...affiliationInfo,
                        department: e.target.value,
                      })
                    }
                  />
                </div>
              )}
              {teamType === "lab" && (
                <div className="space-y-2">
                  <Input
                    placeholder="학교명 (선택)"
                    value={affiliationInfo.school || ""}
                    onChange={(e) =>
                      setAffiliationInfo({
                        ...affiliationInfo,
                        school: e.target.value,
                      })
                    }
                  />
                  <Input
                    placeholder="연구실명 (선택)"
                    value={affiliationInfo.lab || ""}
                    onChange={(e) =>
                      setAffiliationInfo({
                        ...affiliationInfo,
                        lab: e.target.value,
                      })
                    }
                  />
                </div>
              )}
              {teamType === "club" && (
                <div className="space-y-2">
                  <Input
                    placeholder="학교명 (선택)"
                    value={affiliationInfo.school || ""}
                    onChange={(e) =>
                      setAffiliationInfo({
                        ...affiliationInfo,
                        school: e.target.value,
                      })
                    }
                  />
                  <Input
                    placeholder="동아리명 (선택)"
                    value={affiliationInfo.club || ""}
                    onChange={(e) =>
                      setAffiliationInfo({
                        ...affiliationInfo,
                        club: e.target.value,
                      })
                    }
                  />
                </div>
              )}
            </div>
          )}

          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
            <div className="space-y-0.5">
              <Label htmlFor="miniGame">미니게임 참여</Label>
              <p className="text-xs text-muted-foreground">
                휴식 시간에 미니게임을 플레이하여 추가 점수를 획득할 수 있습니다
              </p>
            </div>
            <Switch
              id="miniGame"
              checked={miniGameEnabled}
              onCheckedChange={setMiniGameEnabled}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={isSubmitting}
            >
              취소
            </Button>
            <Button type="submit" variant="primary" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  생성 중...
                </>
              ) : (
                "팀 만들기"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
