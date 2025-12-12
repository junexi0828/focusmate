import { useState, useEffect, useCallback, useRef } from "react";

interface UseTypingIndicatorOptions {
  debounceMs?: number;
  onTypingChange?: (isTyping: boolean) => void;
}

export function useTypingIndicator(options: UseTypingIndicatorOptions = {}) {
  const { debounceMs = 300, onTypingChange } = options;
  const [isTyping, setIsTyping] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleTyping = useCallback(() => {
    if (!isTyping) {
      setIsTyping(true);
      onTypingChange?.(true);
    }

    // 기존 타이머 클리어
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // 디바운스: 일정 시간 후 타이핑 종료로 간주
    timeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      onTypingChange?.(false);
    }, debounceMs);
  }, [isTyping, debounceMs, onTypingChange]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    isTyping,
    handleTyping,
  };
}

