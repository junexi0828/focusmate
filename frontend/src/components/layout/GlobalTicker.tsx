import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { cn } from "@/utils";

interface GlobalTickerProps {
  className?: string;
  messages?: string[];
}

export function GlobalTicker({ className, messages = [
  "📢 FocusMate에 오신 것을 환영합니다!",
  "🔥 현재 128명의 메이트가 집중하고 있습니다.",
  "💡 팁: 뽀모도로 타이머를 활용해보세요!",
  "🚀 새로운 기능이 곧 업데이트됩니다."
] }: GlobalTickerProps) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  // Simple rotation for now, users can upgrade to scrolling marquee later
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % messages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [messages.length]);

  return (
    <div className={cn("flex items-center overflow-hidden h-full", className)}>
      <motion.div
        key={currentMessageIndex}
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: -20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="text-sm font-medium text-muted-foreground whitespace-nowrap"
      >
        {messages[currentMessageIndex]}
      </motion.div>
    </div>
  );
}

// Alternative: Scrolling Marquee Style
export function ScrollingTicker({ className, messages = [
  "📢 FocusMate 공지: 서버 점검 예정 (03:00~03:30)",
  "🏆 이번 주 집중왕: User123 (42시간)",
  "🎉 신규 기능 '다크 모드'가 추가되었습니다!"
]}: GlobalTickerProps) {
  return (
    <div className={cn("overflow-hidden flex items-center w-[40rem] mask-linear-fade", className)}>
      <motion.div
        className="flex gap-8 whitespace-nowrap text-sm text-muted-foreground font-medium"
        animate={{ x: ["100%", "-100%"] }}
        transition={{
          repeat: Infinity,
          duration: 20, // Adjust speed
          ease: "linear",
        }}
      >
        {messages.join(" • ")}
      </motion.div>
    </div>
  );
}
