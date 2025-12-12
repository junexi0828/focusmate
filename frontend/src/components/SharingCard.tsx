import { motion } from "framer-motion";
import { Share2, Download, X } from "lucide-react";
import { useState } from "react";
import { Button } from "./ui/button-enhanced";
import html2canvas from "html2canvas";

interface SharingCardProps {
  type: "achievement" | "streak" | "weekly" | "monthly";
  data: {
    title: string;
    value: string;
    subtitle?: string;
    icon?: React.ReactNode;
  };
}

export function SharingCard({ type, data }: SharingCardProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const gradients = {
    achievement: "from-purple-500 to-pink-500",
    streak: "from-orange-500 to-red-500",
    weekly: "from-blue-500 to-cyan-500",
    monthly: "from-green-500 to-emerald-500",
  };

  const handleDownload = async () => {
    setIsGenerating(true);
    const element = document.getElementById("sharing-card");
    if (!element) return;

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        backgroundColor: null,
      });

      const link = document.createElement("a");
      link.download = `focusmate-${type}-${Date.now()}.png`;
      link.href = canvas.toDataURL();
      link.click();
    } catch (error) {
      console.error("Failed to generate image:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleShare = async () => {
    setIsGenerating(true);
    const element = document.getElementById("sharing-card");
    if (!element) return;

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        backgroundColor: null,
      });

      canvas.toBlob(async (blob) => {
        if (!blob) return;

        const file = new File([blob], `focusmate-${type}.png`, {
          type: "image/png",
        });

        if (navigator.share && navigator.canShare({ files: [file] })) {
          await navigator.share({
            files: [file],
            title: data.title,
            text: `${data.title}: ${data.value}`,
          });
        } else {
          // Fallback to download
          handleDownload();
        }
      });
    } catch (error) {
      console.error("Failed to share:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Preview Card */}
      <div
        id="sharing-card"
        className={`relative w-full aspect-[1.91/1] rounded-2xl bg-gradient-to-br ${gradients[type]} p-8 overflow-hidden`}
      >
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.8),transparent_50%)]" />
          <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_48%,rgba(255,255,255,0.1)_49%,rgba(255,255,255,0.1)_51%,transparent_52%)] bg-[length:20px_20px]" />
        </div>

        {/* Content */}
        <div className="relative h-full flex flex-col justify-between text-white">
          <div>
            {data.icon && (
              <div className="mb-4 opacity-90">{data.icon}</div>
            )}
            <h2 className="text-3xl font-bold mb-2">{data.title}</h2>
            {data.subtitle && (
              <p className="text-white/80 text-sm">{data.subtitle}</p>
            )}
          </div>

          <div>
            <p className="text-6xl font-bold mb-4">{data.value}</p>
            <div className="flex items-center gap-2 text-sm opacity-80">
              <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                🎯
              </div>
              <span>Focus Mate</span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleDownload}
          disabled={isGenerating}
          className="flex-1 gap-2"
        >
          <Download className="h-4 w-4" />
          다운로드
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={handleShare}
          disabled={isGenerating}
          className="flex-1 gap-2"
        >
          <Share2 className="h-4 w-4" />
          공유하기
        </Button>
      </div>
    </div>
  );
}

interface SharingModalProps {
  isOpen: boolean;
  onClose: () => void;
  card: SharingCardProps;
}

export function SharingModal({ isOpen, onClose, card }: SharingModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-2xl bg-card border border-border rounded-xl shadow-lg p-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">공유 카드 생성</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Card */}
        <SharingCard {...card} />
      </motion.div>
    </div>
  );
}
