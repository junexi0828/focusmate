/**
 * Verification status display component.
 */

import { useQuery } from "@tanstack/react-query";
import { Shield, CheckCircle, XCircle, Clock, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button-enhanced";
import { verificationService } from "../services/verificationService";
import { VerificationForm } from "./VerificationForm";
import { useState } from "react";

export function VerificationStatus() {
  const [showForm, setShowForm] = useState(false);
  const { data: statusResponse, isLoading } = useQuery({
    queryKey: ["verification-status"],
    queryFn: async () => {
      const response = await verificationService.getStatus();
      if (response.status === "error") {
        // If error, return null to show "not verified" state
        return null;
      }
      return response.data || null;
    },
  });

  const status = statusResponse;

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
        </div>
      </Card>
    );
  }

  if (!status || !status.status) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-[#7ED6E8]" />
            <div>
              <h3 className="font-semibold text-lg">인증 상태</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                인증이 필요합니다
              </p>
            </div>
          </div>
          <Button
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4]"
          >
            인증 시작하기
          </Button>
        </div>
        {showForm && (
          <div className="mt-6">
            <VerificationForm
              onSuccess={() => {
                setShowForm(false);
              }}
            />
          </div>
        )}
      </Card>
    );
  }

  const getStatusDisplay = () => {
    switch (status.status) {
      case "approved":
        return {
          icon: CheckCircle,
          label: "인증 완료",
          color: "text-green-600 dark:text-green-400",
          bgColor: "bg-green-50 dark:bg-green-900/20",
        };
      case "pending":
        return {
          icon: Clock,
          label: "검토 중",
          color: "text-yellow-600 dark:text-yellow-400",
          bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
        };
      case "rejected":
        return {
          icon: XCircle,
          label: "인증 거부됨",
          color: "text-red-600 dark:text-red-400",
          bgColor: "bg-red-50 dark:bg-red-900/20",
        };
      default:
        return {
          icon: AlertCircle,
          label: "알 수 없음",
          color: "text-slate-600 dark:text-slate-400",
          bgColor: "bg-slate-50 dark:bg-slate-800",
        };
    }
  };

  const statusDisplay = getStatusDisplay();
  const StatusIcon = statusDisplay.icon;

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-[#7ED6E8]" />
            <div>
              <h3 className="font-semibold text-lg">인증 상태</h3>
              <div className={`flex items-center gap-2 ${statusDisplay.color}`}>
                <StatusIcon className="w-4 h-4" />
                <span className="text-sm font-medium">{statusDisplay.label}</span>
              </div>
            </div>
          </div>
          {status.status === "rejected" && (
            <Button
              onClick={() => setShowForm(true)}
              variant="outline"
            >
              다시 신청하기
            </Button>
          )}
        </div>

        {status.status === "approved" && status.verified_at && (
          <div className={`p-4 rounded-lg ${statusDisplay.bgColor}`}>
            <p className="text-sm">
              <strong>인증 완료일:</strong>{" "}
              {new Date(status.verified_at).toLocaleDateString("ko-KR")}
            </p>
            {status.school_name && (
              <p className="text-sm mt-1">
                <strong>학교:</strong> {status.school_name}
              </p>
            )}
            {status.department && (
              <p className="text-sm mt-1">
                <strong>학과:</strong> {status.department}
              </p>
            )}
          </div>
        )}

        {status.status === "pending" && (
          <div className={`p-4 rounded-lg ${statusDisplay.bgColor}`}>
            <p className="text-sm">
              인증 신청이 제출되었습니다. 관리자 검토 후 결과를 알려드립니다.
            </p>
          </div>
        )}

        {status.status === "rejected" && (
          <div className={`p-4 rounded-lg ${statusDisplay.bgColor}`}>
            <p className="text-sm">
              인증이 거부되었습니다. 올바른 서류를 제출하여 다시 신청해주세요.
            </p>
          </div>
        )}

        {showForm && (
          <div className="mt-6">
            <VerificationForm
              onSuccess={() => {
                setShowForm(false);
              }}
            />
          </div>
        )}
      </div>
    </Card>
  );
}

