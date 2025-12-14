/**
 * Dialog for creating a new matching pool.
 */

import { useState } from "react";
import { Button } from "@/components/ui/button-enhanced";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { MatchingPoolCreate } from "@/types/matching";

interface CreatePoolDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: MatchingPoolCreate) => Promise<void>;
}

export function CreatePoolDialog({
  open,
  onOpenChange,
  onSubmit,
}: CreatePoolDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<MatchingPoolCreate>({
    university: "",
    department: "",
    member_count: 3,
    age_range_min: 20,
    age_range_max: 30,
    matching_type: "blind",
    description: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      // Reset form
      setFormData({
        university: "",
        department: "",
        member_count: 3,
        age_range_min: 20,
        age_range_max: 30,
        matching_type: "blind",
        description: "",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>매칭 풀 생성</DialogTitle>
            <DialogDescription>
              새로운 매칭 풀을 생성하여 과팅 매칭을 시작하세요
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* University */}
            <div className="space-y-2">
              <Label htmlFor="university">대학교 *</Label>
              <Input
                id="university"
                placeholder="예: 서울대학교"
                value={formData.university}
                onChange={(e) =>
                  setFormData({ ...formData, university: e.target.value })
                }
                required
              />
            </div>

            {/* Department */}
            <div className="space-y-2">
              <Label htmlFor="department">학과 *</Label>
              <Input
                id="department"
                placeholder="예: 컴퓨터공학과"
                value={formData.department}
                onChange={(e) =>
                  setFormData({ ...formData, department: e.target.value })
                }
                required
              />
            </div>

            {/* Member Count */}
            <div className="space-y-2">
              <Label htmlFor="member_count">인원 수 *</Label>
              <Select
                value={formData.member_count.toString()}
                onValueChange={(value) =>
                  setFormData({ ...formData, member_count: parseInt(value) })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2">2명</SelectItem>
                  <SelectItem value="3">3명</SelectItem>
                  <SelectItem value="4">4명</SelectItem>
                  <SelectItem value="5">5명</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Age Range */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age_min">최소 나이</Label>
                <Input
                  id="age_min"
                  type="number"
                  min="18"
                  max="40"
                  value={formData.age_range_min}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      age_range_min: parseInt(e.target.value),
                    })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="age_max">최대 나이</Label>
                <Input
                  id="age_max"
                  type="number"
                  min="18"
                  max="40"
                  value={formData.age_range_max}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      age_range_max: parseInt(e.target.value),
                    })
                  }
                  required
                />
              </div>
            </div>

            {/* Matching Type */}
            <div className="space-y-2">
              <Label htmlFor="matching_type">매칭 타입 *</Label>
              <Select
                value={formData.matching_type}
                onValueChange={(value: "blind" | "open") =>
                  setFormData({ ...formData, matching_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="blind">🎭 블라인드 (정보 비공개)</SelectItem>
                  <SelectItem value="open">👀 공개 (정보 공개)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">소개 (선택)</Label>
              <Textarea
                id="description"
                placeholder="우리 팀을 간단히 소개해주세요..."
                value={formData.description || ""}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              취소
            </Button>
            <Button
              type="submit"
              className="bg-gradient-to-r from-blue-600 to-purple-600"
              disabled={isSubmitting}
            >
              {isSubmitting ? "생성 중..." : "풀 생성"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
