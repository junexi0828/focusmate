import React from "react";
import { X, FileIcon } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { cn } from "../../../components/ui/utils";

interface FilePreviewProps {
  file: File;
  onRemove: () => void;
  className?: string;
}

export function FilePreview({ file, onRemove, className }: FilePreviewProps) {
  const isImage = file.type.startsWith("image/");
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (isImage) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }

    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [file, isImage]);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div
      className={cn(
        "relative group border rounded-lg overflow-hidden bg-muted/50",
        isImage ? "w-24 h-24" : "w-full",
        className
      )}
    >
      {isImage && previewUrl ? (
        <>
          <img
            src={previewUrl}
            alt={file.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-6 w-6 opacity-0 group-hover:opacity-100 bg-background/80 hover:bg-background"
              onClick={onRemove}
            >
              <X className="w-3 h-3" />
            </Button>
          </div>
        </>
      ) : (
        <div className="flex items-center gap-2 p-2">
          <FileIcon className="w-4 h-4 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm truncate">{file.name}</p>
            <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-6 w-6 flex-shrink-0"
            onClick={onRemove}
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
      )}
    </div>
  );
}

