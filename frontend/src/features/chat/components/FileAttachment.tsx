import { FileIcon, Download } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { cn } from "../../../components/ui/utils";

interface FileAttachmentProps {
  url: string;
  fileName?: string;
  isImage?: boolean;
  onImageClick?: () => void;
  className?: string;
}

export function FileAttachment({
  url,
  fileName,
  isImage,
  onImageClick,
  className,
}: FileAttachmentProps) {
  const getFileName = () => {
    if (fileName) return fileName;
    return url.split("/").pop() || "파일";
  };

  const getImageUrl = (url: string) => {
    // If URL is relative, prepend API base URL
    if (url.startsWith("/")) {
      const env = (import.meta as any).env;
      const apiBaseUrl = env?.VITE_API_BASE_URL || "http://localhost:8000";
      return `${apiBaseUrl}${url}`;
    }
    return url;
  };

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const response = await fetch(getImageUrl(url));
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = getFileName();
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Failed to download file:", error);
      // Fallback: open in new tab
      window.open(getImageUrl(url), "_blank");
    }
  };

  if (isImage) {
    return (
      <div
        className={cn(
          "relative group rounded-lg overflow-hidden cursor-pointer",
          className
        )}
        onClick={onImageClick}
      >
        <img
          src={getImageUrl(url)}
          alt={getFileName()}
          className="max-w-full max-h-64 object-contain rounded-lg"
          loading="lazy"
          onError={(e) => {
            // Fallback to file icon if image fails to load
            const target = e.target as HTMLImageElement;
            target.style.display = "none";
            const parent = target.parentElement;
            if (parent) {
              parent.innerHTML = `
                <div class="flex items-center gap-2 p-2 bg-background/50 rounded-lg">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span class="text-sm">${getFileName()}</span>
                </div>
              `;
            }
          }}
        />
        {/* Download overlay on hover */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleDownload}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            다운로드
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 p-2 bg-background/50 rounded-lg hover:bg-background/80 transition-colors",
        className
      )}
    >
      <FileIcon className="w-4 h-4 flex-shrink-0" />
      <span className="text-sm truncate flex-1">{getFileName()}</span>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleDownload}
        className="h-6 w-6 p-0 flex-shrink-0"
        title="다운로드"
      >
        <Download className="w-4 h-4" />
      </Button>
    </div>
  );
}

