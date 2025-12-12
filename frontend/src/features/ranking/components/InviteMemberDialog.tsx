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
import { Loader2 } from "lucide-react";

interface InviteMemberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (email: string) => Promise<void>;
  inviteCode?: string | null;
}

export function InviteMemberDialog({
  open,
  onOpenChange,
  onSubmit,
  inviteCode,
}: InviteMemberDialogProps) {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email.trim()) {
      setError("이메일을 입력해주세요");
      return;
    }

    if (!validateEmail(email.trim())) {
      setError("올바른 이메일 형식이 아닙니다");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(email.trim());
      setEmail("");
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to invite member:", error);
      setError("초대에 실패했습니다");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!isSubmitting) {
      if (!newOpen) {
        setEmail("");
        setError("");
      }
      onOpenChange(newOpen);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>팀원 초대</DialogTitle>
          <DialogDescription>
            이메일로 팀원을 초대하거나 초대 코드를 공유하세요
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {inviteCode && (
            <div className="p-4 bg-muted rounded-lg">
              <Label className="text-sm font-medium mb-2 block">초대 코드</Label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-3 py-2 bg-background border rounded font-mono text-sm">
                  {inviteCode}
                </code>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(inviteCode);
                    } catch (err) {
                      console.error("Failed to copy:", err);
                    }
                  }}
                >
                  복사
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                이 코드를 팀원에게 공유하세요
              </p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">이메일 주소</Label>
            <Input
              id="email"
              type="email"
              placeholder="member@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={error ? "border-destructive" : ""}
            />
            {error && <p className="text-sm text-destructive">{error}</p>}
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
                  초대 중...
                </>
              ) : (
                "초대하기"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

