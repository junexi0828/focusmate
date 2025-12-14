/**
 * Verification form component for submitting verification requests.
 */

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, X, FileText, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button-enhanced";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { verificationService, type VerificationSubmit } from "../services/verificationService";
import { toast } from "sonner";

interface VerificationFormProps {
  onSuccess?: () => void;
}

export function VerificationForm({ onSuccess }: VerificationFormProps) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<VerificationSubmit>({
    school_name: "",
    department: "",
    major_category: "",
    grade: "",
    student_id: "",
    gender: "male",
    documents: [],
  });
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const submitMutation = useMutation({
    mutationFn: verificationService.submitVerification,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["verification-status"] });
      toast.success("인증 신청이 제출되었습니다.");
      onSuccess?.();
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "인증 신청에 실패했습니다.");
    },
  });

  const uploadMutation = useMutation({
    mutationFn: verificationService.uploadDocuments,
    onSuccess: (data) => {
      setFormData((prev) => ({
        ...prev,
        documents: data.uploaded_files,
      }));
      toast.success(`${data.count}개의 파일이 업로드되었습니다.`);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "파일 업로드에 실패했습니다.");
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (selectedFiles.length + files.length > 5) {
      toast.error("최대 5개의 파일만 업로드할 수 있습니다.");
      return;
    }
    setFiles((prev) => [...prev, ...selectedFiles]);
  };

  const handleRemoveFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error("업로드할 파일을 선택해주세요.");
      return;
    }
    setUploading(true);
    try {
      await uploadMutation.mutateAsync(files);
      setFiles([]);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.school_name || !formData.department || !formData.grade) {
      toast.error("필수 항목을 모두 입력해주세요.");
      return;
    }
    submitMutation.mutate(formData);
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label htmlFor="school_name">학교명 *</Label>
            <Input
              id="school_name"
              value={formData.school_name}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, school_name: e.target.value }))
              }
              placeholder="예: 부경대학교"
              required
            />
          </div>

          <div>
            <Label htmlFor="department">학과/전공 *</Label>
            <Input
              id="department"
              value={formData.department}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, department: e.target.value }))
              }
              placeholder="예: 컴퓨터공학과"
              required
            />
          </div>

          <div>
            <Label htmlFor="major_category">전공 분류</Label>
            <Input
              id="major_category"
              value={formData.major_category}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, major_category: e.target.value }))
              }
              placeholder="예: 공학"
            />
          </div>

          <div>
            <Label htmlFor="grade">학년 *</Label>
            <Input
              id="grade"
              value={formData.grade}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, grade: e.target.value }))
              }
              placeholder="예: 3학년"
              required
            />
          </div>

          <div>
            <Label htmlFor="student_id">학번</Label>
            <Input
              id="student_id"
              value={formData.student_id}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, student_id: e.target.value }))
              }
              placeholder="선택사항"
            />
          </div>

          <div>
            <Label htmlFor="gender">성별 *</Label>
            <Select
              value={formData.gender}
              onValueChange={(value: "male" | "female" | "other") =>
                setFormData((prev) => ({ ...prev, gender: value }))
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">남성</SelectItem>
                <SelectItem value="female">여성</SelectItem>
                <SelectItem value="other">기타</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <Label>인증 서류 업로드 (최대 5개)</Label>
            <div className="mt-2 space-y-2">
              <div className="flex items-center gap-2">
                <Input
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileChange}
                  className="flex-1"
                />
                <Button
                  type="button"
                  onClick={handleUpload}
                  disabled={files.length === 0 || uploading}
                  variant="outline"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  업로드
                </Button>
              </div>
              {files.length > 0 && (
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-slate-100 dark:bg-slate-800 rounded"
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        <span className="text-sm">{file.name}</span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveFile(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
              {formData.documents.length > 0 && (
                <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                  <AlertCircle className="w-4 h-4" />
                  <span>{formData.documents.length}개의 파일이 업로드되었습니다.</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button
            type="submit"
            disabled={submitMutation.isPending}
            className="bg-gradient-to-r from-blue-600 to-purple-600"
          >
            {submitMutation.isPending ? "제출 중..." : "인증 신청 제출"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

