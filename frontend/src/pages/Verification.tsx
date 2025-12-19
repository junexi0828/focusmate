/**
 * Verification page for school authentication
 */

import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Upload, FileText, CheckCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button-enhanced";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageTransition } from "@/components/PageTransition";
import { matchingApi } from "@/api/matching";
import { toast } from "sonner";

export default function VerificationPage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    school_name: "",
    department: "",
    major_category: "",
    grade: "",
    student_id: "",
    gender: "male" as "male" | "female" | "other",
  });

  // Fetch current verification status
  const { data: verification, isLoading } = useQuery({
    queryKey: ["verification-status"],
    queryFn: matchingApi.getVerificationStatus,
  });

  // Submit verification mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) {
        throw new Error("파일을 선택해주세요");
      }

      // 1. Upload file first
      const uploadResponse =
        await matchingApi.uploadVerificationFile(selectedFile);

      if (
        !uploadResponse.uploaded_files ||
        uploadResponse.uploaded_files.length === 0
      ) {
        throw new Error("파일 업로드에 실패했습니다");
      }

      const fileUrl = uploadResponse.uploaded_files[0];

      // 2. Submit verification with file URL
      const submitData: any = {
        school_name: formData.school_name,
        department: formData.department,
        grade: formData.grade,
        gender: formData.gender,
        documents: [fileUrl],
      };

      if (formData.major_category) {
        submitData.major_category = formData.major_category;
      }

      if (formData.student_id) {
        submitData.student_id = formData.student_id;
      }

      return matchingApi.submitVerification(submitData);
    },
    onSuccess: () => {
      toast.success("인증이 제출되었습니다. 검토까지 1-2일 소요됩니다.");
      navigate({ to: "/matching" });
    },
    onError: (error: any) => {
      toast.error(error?.message || "인증 제출에 실패했습니다");
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/pdf",
      ];
      if (!validTypes.includes(file.type)) {
        toast.error("JPG, PNG, PDF 파일만 업로드 가능합니다");
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("파일 크기는 5MB 이하여야 합니다");
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!selectedFile) {
      toast.error("학생증 또는 재학증명서를 업로드해주세요");
      return;
    }
    if (!formData.school_name || !formData.department || !formData.grade) {
      toast.error("모든 필수 항목을 입력해주세요");
      return;
    }

    await submitMutation.mutateAsync();
  };

  if (isLoading) {
    return (
      <PageTransition>
        <div className="min-h-full bg-muted/30 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </PageTransition>
    );
  }

  // If already verified, show status
  if (verification?.status === "approved") {
    return (
      <PageTransition>
        <div className="min-h-full bg-muted/30 p-6">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                  <div>
                    <CardTitle>인증 완료</CardTitle>
                    <CardDescription>
                      학교 인증이 완료되었습니다
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">대학교</p>
                  <p className="font-medium">
                    {(verification as any).school_name ||
                      verification.university}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">학과</p>
                  <p className="font-medium">{verification.department}</p>
                </div>
                <Button
                  onClick={() => navigate({ to: "/matching" })}
                  className="w-full"
                >
                  매칭 시작하기
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </PageTransition>
    );
  }

  // If pending, show pending status
  if (verification?.status === "pending") {
    return (
      <PageTransition>
        <div className="min-h-full bg-muted/30 p-6">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <Clock className="w-8 h-8 text-yellow-600" />
                  <div>
                    <CardTitle>인증 검토 중</CardTitle>
                    <CardDescription>
                      제출하신 인증이 검토 중입니다
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  일반적으로 1-2일 내에 검토가 완료됩니다.
                </p>
                <Button
                  variant="outline"
                  onClick={() => navigate({ to: "/matching" })}
                  className="w-full"
                >
                  돌아가기
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </PageTransition>
    );
  }

  // Show verification form
  return (
    <PageTransition>
      <div className="min-h-full bg-muted/30 p-6">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>학교 인증</CardTitle>
              <CardDescription>
                핑크캠퍼스 매칭 서비스를 이용하려면 학교 인증이 필요합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* File Upload */}
                <div className="space-y-2">
                  <Label htmlFor="file">학생증 또는 재학증명서 *</Label>
                  <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                    <input
                      type="file"
                      id="file"
                      accept="image/*,.pdf"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <label htmlFor="file" className="cursor-pointer">
                      {selectedFile ? (
                        <div className="flex items-center justify-center gap-2">
                          <FileText className="w-5 h-5 text-primary" />
                          <span className="text-sm font-medium">
                            {selectedFile.name}
                          </span>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <Upload className="w-8 h-8 mx-auto text-muted-foreground" />
                          <p className="text-sm text-muted-foreground">
                            클릭하여 파일 선택 (JPG, PNG, PDF)
                          </p>
                          <p className="text-xs text-muted-foreground">
                            최대 5MB
                          </p>
                        </div>
                      )}
                    </label>
                  </div>
                </div>

                {/* School Name */}
                <div className="space-y-2">
                  <Label htmlFor="school_name">대학교 *</Label>
                  <Input
                    id="school_name"
                    placeholder="예: 서울대학교"
                    value={formData.school_name}
                    onChange={(e) =>
                      setFormData({ ...formData, school_name: e.target.value })
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

                {/* Major Category */}
                <div className="space-y-2">
                  <Label htmlFor="major_category">전공 분야 (선택)</Label>
                  <Input
                    id="major_category"
                    placeholder="예: 공학"
                    value={formData.major_category}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        major_category: e.target.value,
                      })
                    }
                  />
                </div>

                {/* Grade */}
                <div className="space-y-2">
                  <Label htmlFor="grade">학년 *</Label>
                  <Input
                    id="grade"
                    placeholder="예: 1, 2, 3, 4"
                    value={formData.grade}
                    onChange={(e) =>
                      setFormData({ ...formData, grade: e.target.value })
                    }
                    required
                  />
                </div>

                {/* Student ID */}
                <div className="space-y-2">
                  <Label htmlFor="student_id">학번 (선택)</Label>
                  <Input
                    id="student_id"
                    placeholder="예: 2021123456"
                    value={formData.student_id}
                    onChange={(e) =>
                      setFormData({ ...formData, student_id: e.target.value })
                    }
                  />
                </div>

                {/* Gender */}
                <div className="space-y-2">
                  <Label htmlFor="gender">성별 *</Label>
                  <select
                    id="gender"
                    value={formData.gender}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        gender: e.target.value as "male" | "female" | "other",
                      })
                    }
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                  >
                    <option value="male">남성</option>
                    <option value="female">여성</option>
                    <option value="other">기타</option>
                  </select>
                </div>

                {/* Submit Buttons */}
                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate({ to: "/matching" })}
                    className="flex-1"
                  >
                    취소
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4]"
                    disabled={submitMutation.isPending}
                  >
                    {submitMutation.isPending ? "제출 중..." : "인증 제출"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageTransition>
  );
}
