import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { toast } from "sonner";
import { createReport, ReportCreate } from "../api/reports";

interface ReportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  proposalId?: string;
  poolId?: string;
  reportedUserId?: string;
}

export function ReportDialog({
  open,
  onOpenChange,
  proposalId,
  poolId,
  reportedUserId,
}: ReportDialogProps) {
  const [reportType, setReportType] = useState<string>("");
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!reportType) {
      toast.error("신고 유형을 선택해주세요");
      return;
    }

    if (!reason || reason.trim().length < 10) {
      toast.error("신고 사유를 최소 10자 이상 입력해주세요");
      return;
    }

    setIsSubmitting(true);
    try {
      const reportData: ReportCreate = {
        report_type: reportType as ReportCreate["report_type"],
        reason: reason.trim(),
      };

      if (proposalId) {
        reportData.proposal_id = proposalId;
      }
      if (poolId) {
        reportData.pool_id = poolId;
      }
      if (reportedUserId) {
        reportData.reported_user_id = reportedUserId;
      }

      await createReport(reportData);
      toast.success("신고가 접수되었습니다. 검토 후 조치하겠습니다.");
      onOpenChange(false);
      setReportType("");
      setReason("");
    } catch (error: any) {
      toast.error(
        error?.response?.data?.detail || "신고 접수에 실패했습니다"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onOpenChange(false);
      setReportType("");
      setReason("");
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>신고하기</DialogTitle>
          <DialogDescription>
            부적절한 행위나 내용을 신고해주세요. 검토 후 조치하겠습니다.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="report-type">신고 유형</Label>
            <Select value={reportType} onValueChange={setReportType}>
              <SelectTrigger id="report-type">
                <SelectValue placeholder="신고 유형을 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="inappropriate_behavior">
                  부적절한 행위
                </SelectItem>
                <SelectItem value="spam">스팸</SelectItem>
                <SelectItem value="harassment">괴롭힘/혐오</SelectItem>
                <SelectItem value="fake_profile">가짜 프로필</SelectItem>
                <SelectItem value="other">기타</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="reason">신고 사유</Label>
            <Textarea
              id="reason"
              placeholder="신고 사유를 상세히 입력해주세요 (최소 10자)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={5}
              maxLength={1000}
            />
            <p className="text-xs text-muted-foreground">
              {reason.length}/1000자
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            취소
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting || !reportType || reason.trim().length < 10}
          >
            {isSubmitting ? "제출 중..." : "신고하기"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

