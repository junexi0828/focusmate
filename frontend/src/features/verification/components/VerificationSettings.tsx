/**
 * Verification settings component for managing display preferences.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Settings, Eye, EyeOff } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button-enhanced";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { verificationService } from "../services/verificationService";
import { toast } from "sonner";

export function VerificationSettings() {
  const queryClient = useQueryClient();
  const { data: statusResponse } = useQuery({
    queryKey: ["verification-status"],
    queryFn: async () => {
      const response = await verificationService.getStatus();
      if (response.status === "error") {
        return null;
      }
      return response.data || null;
    },
  });

  const status = statusResponse;

  const updateMutation = useMutation({
    mutationFn: async (settings: { badge_visible?: boolean; department_visible?: boolean }) => {
      const response = await verificationService.updateSettings(settings);
      if (response.status === "error") {
        throw new Error(response.error?.message || "설정 변경에 실패했습니다.");
      }
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["verification-status"] });
      toast.success("설정이 변경되었습니다.");
    },
    onError: (error: any) => {
      toast.error(error?.message || "설정 변경에 실패했습니다.");
    },
  });

  const handleToggle = (field: "badge_visible" | "department_visible", value: boolean) => {
    updateMutation.mutate({ [field]: value });
  };

  if (!status || status.status !== "approved") {
    return null;
  }

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-4">
        <Settings className="w-5 h-5 text-slate-600 dark:text-slate-400" />
        <h3 className="font-semibold text-lg">인증 표시 설정</h3>
      </div>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {status.badge_visible ? (
              <Eye className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            ) : (
              <EyeOff className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            )}
            <Label htmlFor="badge_visible">인증 배지 표시</Label>
          </div>
          <Switch
            id="badge_visible"
            checked={status.badge_visible ?? true}
            onCheckedChange={(checked) => handleToggle("badge_visible", checked)}
            disabled={updateMutation.isPending}
          />
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {status.department_visible ? (
              <Eye className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            ) : (
              <EyeOff className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            )}
            <Label htmlFor="department_visible">학과 정보 표시</Label>
          </div>
          <Switch
            id="department_visible"
            checked={status.department_visible ?? true}
            onCheckedChange={(checked) => handleToggle("department_visible", checked)}
            disabled={updateMutation.isPending}
          />
        </div>
      </div>
    </Card>
  );
}

