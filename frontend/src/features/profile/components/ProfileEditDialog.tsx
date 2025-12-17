import { useState } from "react";
import { Button } from "../../../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Textarea } from "../../../components/ui/textarea";
import { User } from "../../../types/user";
import { updateProfile, uploadProfileImage } from "../../../api/profile";
import { toast } from "sonner";
import { Loader2, Upload } from "lucide-react";

interface ProfileEditDialogProps {
  user: User;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpdate: (user: User) => void;
}

export function ProfileEditDialog({
  user,
  open,
  onOpenChange,
  onUpdate,
}: ProfileEditDialogProps) {
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    username: user.name || "",
    bio: user.bio || "",
    school: user.school || "",
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(
    user.profile_image || null
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error("파일 크기는 5MB 이하여야 합니다");
        return;
      }
      if (!file.type.startsWith("image/")) {
        toast.error("이미지 파일만 업로드할 수 있습니다");
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleUploadImage = async () => {
    if (!selectedFile) return null;

    setUploading(true);
    try {
      const result = await uploadProfileImage(user.id, selectedFile);
      toast.success("프로필 이미지가 업로드되었습니다");
      return result.profile_image;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "이미지 업로드에 실패했습니다");
      return null;
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Upload image first if selected
      let profileImageUrl = user.profile_image;
      if (selectedFile) {
        const uploadedUrl = await handleUploadImage();
        if (uploadedUrl) {
          profileImageUrl = uploadedUrl;
        }
      }

      // Update profile
      const updatedUser = await updateProfile(user.id, {
        username: formData.username,
        bio: formData.bio,
        school: formData.school,
        profile_image: profileImageUrl,
      });

      toast.success("프로필이 업데이트되었습니다");
      onUpdate(updatedUser);
      onOpenChange(false);
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || "프로필 업데이트에 실패했습니다"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>프로필 편집</DialogTitle>
          <DialogDescription>
            프로필 정보를 수정할 수 있습니다.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Profile Image */}
            <div className="flex flex-col items-center gap-4">
              <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Profile preview"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-3xl">
                    {formData.username.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <Label
                htmlFor="profile-image"
                className="cursor-pointer flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
              >
                <Upload className="w-4 h-4" />
                프로필 이미지 변경
              </Label>
              <Input
                id="profile-image"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>

            {/* Username */}
            <div className="grid gap-2">
              <Label htmlFor="username">닉네임</Label>
              <Input
                id="username"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                placeholder="닉네임을 입력하세요"
                required
              />
            </div>

            {/* School */}
            <div className="grid gap-2">
              <Label htmlFor="school">학교</Label>
              <Input
                id="school"
                value={formData.school}
                onChange={(e) =>
                  setFormData({ ...formData, school: e.target.value })
                }
                placeholder="학교를 입력하세요"
              />
            </div>

            {/* Bio */}
            <div className="grid gap-2">
              <Label htmlFor="bio">자기소개</Label>
              <Textarea
                id="bio"
                value={formData.bio}
                onChange={(e) =>
                  setFormData({ ...formData, bio: e.target.value })
                }
                placeholder="자기소개를 입력하세요"
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              취소
            </Button>
            <Button type="submit" disabled={loading || uploading}>
              {loading || uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  저장 중...
                </>
              ) : (
                "저장"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
