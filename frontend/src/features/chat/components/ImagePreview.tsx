import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { Button } from "../../../components/ui/button";
import { Download, X, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "../../../components/ui/utils";

interface ImagePreviewProps {
  images: string[];
  initialIndex?: number;
  onClose: () => void;
  isOpen: boolean;
}

export function ImagePreview({
  images,
  initialIndex = 0,
  onClose,
  isOpen,
}: ImagePreviewProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [isLoading, setIsLoading] = useState(true);

  const currentImage = images[currentIndex];
  const hasMultiple = images.length > 1;

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1));
    setIsLoading(true);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0));
    setIsLoading(true);
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(currentImage);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = currentImage.split("/").pop() || "image";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download image:", error);
    }
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl w-full h-[90vh] p-0 gap-0">
        <DialogHeader className="sr-only">
          <DialogTitle>이미지 미리보기</DialogTitle>
        </DialogHeader>
        <div className="relative w-full h-full flex items-center justify-center bg-black/95">
          {/* Close button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 z-10 text-white hover:bg-white/20"
            onClick={onClose}
          >
            <X className="w-5 h-5" />
          </Button>

          {/* Download button */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-16 z-10 text-white hover:bg-white/20"
            onClick={handleDownload}
          >
            <Download className="w-5 h-5" />
          </Button>

          {/* Previous button */}
          {hasMultiple && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute left-4 z-10 text-white hover:bg-white/20"
              onClick={handlePrevious}
            >
              <ChevronLeft className="w-6 h-6" />
            </Button>
          )}

          {/* Image */}
          <div className="relative w-full h-full flex items-center justify-center p-8">
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              </div>
            )}
            <img
              src={getImageUrl(currentImage)}
              alt={`이미지 ${currentIndex + 1}`}
              className={cn(
                "max-w-full max-h-full object-contain",
                isLoading && "opacity-0"
              )}
              onLoad={() => setIsLoading(false)}
              onError={() => setIsLoading(false)}
            />
          </div>

          {/* Next button */}
          {hasMultiple && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-4 z-10 text-white hover:bg-white/20"
              onClick={handleNext}
            >
              <ChevronRight className="w-6 h-6" />
            </Button>
          )}

          {/* Image counter */}
          {hasMultiple && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/50 text-white px-4 py-2 rounded-full text-sm">
              {currentIndex + 1} / {images.length}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

