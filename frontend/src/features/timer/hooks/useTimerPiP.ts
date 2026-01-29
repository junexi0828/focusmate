import { useCallback, useEffect, useRef, useState } from "react";
import { TimerStatus, SessionType } from "../components/TimerDisplay";
import { toast } from "sonner";

interface ChatMessage {
  sender: string;
  text: string;
}

interface UseTimerPiPProps {
  minutes: number;
  seconds: number;
  status: TimerStatus;
  sessionType: SessionType;
  progress: number; // 0-100
  userName?: string; // User name to display
  onPlayPause?: () => void; // Callback for play/pause from PiP controls
  participantCount?: number; // Number of active participants
  recentMessages?: ChatMessage[]; // Recent chat messages (max 2)
}

export function useTimerPiP({
  minutes,
  seconds,
  status,
  sessionType,
  progress,
  userName = "User",
  onPlayPause,
  participantCount = 0,
  recentMessages = [],
}: UseTimerPiPProps) {
  const isMounted = useRef(true);
  const [isPipActive, setIsPipActive] = useState(false);
  const [pipWindowSize, setPipWindowSize] = useState<{ width: number; height: number }>({ width: 400, height: 400 });
  const lastPipSizeRef = useRef<{ width: number; height: number }>({ width: 400, height: 400 });
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const rafRef = useRef<number | null>(null);

  // Check browser support
  const isSupported = 'pictureInPictureEnabled' in document;

  const updateCanvasSize = useCallback((width: number, height: number) => {
    const nextWidth = Math.round(width || 400);
    const nextHeight = Math.round(height || 400);
    const canvas = canvasRef.current;
    if (canvas && (canvas.width !== nextWidth || canvas.height !== nextHeight)) {
      canvas.width = nextWidth;
      canvas.height = nextHeight;
    }

    const last = lastPipSizeRef.current;
    if (last.width !== nextWidth || last.height !== nextHeight) {
      lastPipSizeRef.current = { width: nextWidth, height: nextHeight };
      setPipWindowSize({ width: nextWidth, height: nextHeight });
    }
  }, []);

  // Initialize canvas and video elements once
  useEffect(() => {
    isMounted.current = true;
    if (!canvasRef.current) {
      const canvas = document.createElement("canvas");
      // Smaller canvas for better PiP performance and smaller window support
      canvas.width = 400;
      canvas.height = 400;
      canvasRef.current = canvas;
    }

    if (!videoRef.current) {
      const video = document.createElement("video");
      video.muted = true;
      video.playsInline = true;
      video.loop = true;

      // Mount to DOM - REQUIRED for browser PiP button
      video.style.position = 'absolute';
      video.style.width = '1px';
      video.style.height = '1px';
      video.style.opacity = '0';
      video.style.pointerEvents = 'none';
      video.style.zIndex = '-1';
      document.body.appendChild(video);
      videoRef.current = video;

      // Connect canvas stream and start playing
      // This makes the browser PiP button active
      if (canvasRef.current) {
        const stream = canvasRef.current.captureStream(30);
        video.srcObject = stream;

        // Start playing (required for browser PiP button)
        video.play().catch(err => {
          console.debug('Auto-play failed (expected):', err);
          // This is OK - browser may block auto-play
          // User clicking our PiP button will trigger play with user gesture
        });
      }
    }

    // Cleanup on unmount
    return () => {
      isMounted.current = false;
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }

      // Cleanup PiP only if active
      if (document.pictureInPictureElement && videoRef.current && document.pictureInPictureElement === videoRef.current) {
         // We don't await here as it's cleanup
         document.exitPictureInPicture().catch(() => {});
      }

      // Clear MediaSession
      if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = null;
        navigator.mediaSession.setActionHandler('play', null);
        navigator.mediaSession.setActionHandler('pause', null);
      }
      // Remove video from DOM
      if (videoRef.current && videoRef.current.parentNode) {
        videoRef.current.parentNode.removeChild(videoRef.current);
      }
      // Clear refs
      canvasRef.current = null;
      videoRef.current = null;
    };
  }, []);

  const drawTimer = useCallback(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx || !canvasRef.current) return;

    const width = canvasRef.current.width;
    const height = canvasRef.current.height;
    const centerX = width / 2;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Determine display level based on ACTUAL PiP window size
    // Get real-time size from pictureInPictureElement instead of state
    const pipElement = document.pictureInPictureElement as HTMLVideoElement | null;
    const actualWidth = pipElement?.width || pipWindowSize.width || width;
    const actualHeight = pipElement?.height || pipWindowSize.height || height;

    const pipWidth = actualWidth;
    const pipHeight = actualHeight;
    const minDim = Math.min(pipWidth, pipHeight);

    // Level 1 (Small): Timer only - matches browser minimum
    // Level 2 (Medium): Timer + Participant count
    // Level 3 (Large): Full info (chat)
    const isSmall = minDim < 280;
    const isMedium = !isSmall && minDim < 340;
    const isLarge = !isSmall && !isMedium;

    // Debug: Log size and level (only when PiP is active)
    if (document.pictureInPictureElement) {
      console.log(`[PiP] Size: ${pipWidth}x${pipHeight}, Level: ${isSmall ? 'Small' : isMedium ? 'Medium' : 'Large'}`);
    }

    const scale = Math.min(width, height) / 400;
    const padding = 16 * scale;
    const centerY = height * (isLarge ? 0.46 : isMedium ? 0.48 : 0.5);
    const radiusMax = Math.min(width, height) / 2 - padding - (isLarge ? 40 * scale : 20 * scale);
    const radius = Math.min(145 * scale, radiusMax);

    // 1. Modern Deep Gradient Background
    // Create a radial gradient for a "spotlight" effect
    const bgGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, width);
    bgGradient.addColorStop(0, "#27272a"); // zinc-800 center
    bgGradient.addColorStop(0.7, "#18181b"); // zinc-900 mid
    bgGradient.addColorStop(1, "#09090b");   // zinc-950 edge
    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, width, height);

    // 2. Draw Status Indicator (User Name & Session) - Top
    // Hide in Small mode for clean minimal view (YouTube PiP style)
    if (!isSmall) {
      // User Name
      ctx.font = `500 ${Math.round(20 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
      ctx.fillStyle = "#a1a1aa"; // zinc-400
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(userName, centerX, centerY - 80 * scale);

      // Session Type Active Text
      const sessionLabel = sessionType === "focus" ? "FOCUS" : "BREAK";
      ctx.font = `800 ${Math.round(26 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
      ctx.fillStyle = sessionType === "focus" ? "#fca5a5" : "#93c5fd"; // Soft Red or Blue
      ctx.shadowColor = sessionType === "focus" ? "rgba(239, 68, 68, 0.5)" : "rgba(59, 130, 246, 0.5)";
      ctx.shadowBlur = 12;
      ctx.fillText(sessionLabel, centerX, centerY - 50 * scale);
      ctx.shadowBlur = 0; // Reset shadow
    }

    // 3. Draw Time (Modern Typography)
    const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    // Use tabular-nums feature settings if possible, or a font known for good tabular numbers
    ctx.font = `700 ${Math.round(100 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    // Time color based on state
    if (status === "completed") {
        ctx.fillStyle = "#4ade80"; // Bright Green
        ctx.shadowColor = "rgba(74, 222, 128, 0.4)";
        ctx.shadowBlur = 20;
    } else if (status === "paused") {
        ctx.fillStyle = "#fcd34d"; // Amber
        ctx.shadowColor = "rgba(251, 191, 36, 0.2)";
        ctx.shadowBlur = 10;
    } else {
        ctx.fillStyle = "#ffffff"; // White
        ctx.shadowColor = "rgba(255, 255, 255, 0.1)";
        ctx.shadowBlur = 10;
    }

    ctx.fillText(timeStr, centerX, centerY + 20 * scale);
    ctx.shadowBlur = 0; // Reset

    // 4. Progress Ring with Gradient & Glow
    // Background Ring (Track)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.1)"; // Very subtle white track
    ctx.lineWidth = 12 * scale;
    ctx.lineCap = "round";
    ctx.stroke();

    // Foreground Ring (Progress)
    if (progress > 0) {
        const startAngle = -0.5 * Math.PI; // Top
        const endAngle = startAngle + (2 * Math.PI * (progress / 100));

        ctx.beginPath();
        // Counter-clockwise for "countdown" feel? No, standard clockwise is better for "progress done"
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);

        // Gradient Stroke
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        if (status === 'completed') {
            gradient.addColorStop(0, "#22c55e");
            gradient.addColorStop(1, "#86efac");
        } else if (sessionType === 'focus') {
            gradient.addColorStop(0, "#ef4444"); // Red-500
            gradient.addColorStop(1, "#f97316"); // Orange-500
        } else {
            gradient.addColorStop(0, "#3b82f6"); // Blue-500
            gradient.addColorStop(1, "#06b6d4"); // Cyan-500
        }

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 12 * scale;
        ctx.lineCap = "round";

        // Add Glow to the ring
        ctx.shadowColor = sessionType === 'focus' ? "rgba(239, 68, 68, 0.4)" : "rgba(59, 130, 246, 0.4)";
        ctx.shadowBlur = 15;

        ctx.stroke();
        ctx.shadowBlur = 0; // Reset

        // 5. End Cap Dot (Indicator)
        // Calculate position of the end of the arc
        const endX = centerX + radius * Math.cos(endAngle);
        const endY = centerY + radius * Math.sin(endAngle);

        ctx.beginPath();
        ctx.arc(endX, endY, 10 * scale, 0, 2 * Math.PI);
        ctx.fillStyle = "#ffffff";
        ctx.shadowColor = "rgba(255,255,255,0.8)";
        ctx.shadowBlur = 10 * scale;
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    // 6. Participant Count (Level 2+: Medium and Large)
    let participantTextY = 0;
    if ((isMedium || isLarge) && participantCount > 0) {
      ctx.font = `600 ${Math.round(15 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
      ctx.fillStyle = "#a1a1aa"; // zinc-400
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const participantText = `${participantCount}명 집중 중`;
      participantTextY = centerY + radius + 18 * scale;

      ctx.fillText(participantText, centerX, participantTextY);
    }

    // 7. Chat Messages (Level 3: Large only)
    let chatEndY = participantTextY;
    if (isLarge && recentMessages.length > 0) {
      const messages = recentMessages.slice(-2); // Last 2 messages
      let yOffset = participantTextY > 0 ? participantTextY + 12 * scale : centerY + radius + 18 * scale;

      ctx.font = `500 ${Math.round(11 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
      ctx.textAlign = "center";

      const lineHeight = 12 * scale;
      const availableWidth = width - padding * 2;
      const availableHeight = height - padding - yOffset;
      const maxLines = Math.min(messages.length, Math.floor(availableHeight / lineHeight));
      const visibleMessages = maxLines > 0 ? messages.slice(-maxLines) : [];

      const truncateToWidth = (text: string) => {
        if (ctx.measureText(text).width <= availableWidth) return text;
        let truncated = text;
        while (truncated.length > 0 && ctx.measureText(`${truncated}...`).width > availableWidth) {
          truncated = truncated.slice(0, -1);
        }
        return truncated.length > 0 ? `${truncated}...` : text;
      };

      visibleMessages.forEach((msg) => {
        const senderText = `${msg.sender}:`;
        const messageText = msg.text;

        const fullText = truncateToWidth(`${senderText} ${messageText}`);
        ctx.fillStyle = "#71717a"; // zinc-500
        ctx.fillText(fullText, centerX, yOffset);

        yOffset += lineHeight;
      });

      chatEndY = yOffset;
    }

    // 8. Pulse / Breathing Effect (Bottom Indicator)
    if (status === "running") {
      const time = Date.now() / 1000;
      const alpha = (Math.sin(time * 2) + 1) / 2 * 0.5 + 0.2; // 0.2 to 0.7

      // Position dot below all content
      let dotY = centerY + radius + 35 * scale;
      if (chatEndY > 0) {
        dotY = chatEndY + 8 * scale;
      } else if (participantTextY > 0) {
        dotY = participantTextY + 20 * scale;
      }

      if (dotY + 8 * scale < height - padding) {
        ctx.beginPath();
        ctx.arc(centerX, dotY, 6 * scale, 0, 2 * Math.PI);

        ctx.fillStyle = sessionType === 'focus' ? `rgba(239, 68, 68, ${alpha})` : `rgba(59, 130, 246, ${alpha})`;
        ctx.shadowColor = sessionType === 'focus' ? "#ef4444" : "#3b82f6";
        ctx.shadowBlur = 10 * alpha;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }
  }, [minutes, seconds, status, sessionType, progress, userName, participantCount, recentMessages, pipWindowSize]);

  // Loop to keep updating the canvas stream
  // Use setInterval instead of requestAnimationFrame for better background performance
  useEffect(() => {
    let intervalId: number | null = null;

    if (isPipActive && status === 'running') {
      // 20fps (50ms) - Balanced for battery life vs animation smoothness
      // Reduced from 30fps to save resources while keeping breathing effect acceptable
      intervalId = window.setInterval(() => {
        drawTimer();
      }, 50);
    } else {
      // If paused or not PiP, just draw once when dependencies change
      // (This effect re-runs when drawTimer changes, which happens when time changes)
      drawTimer();
    }

    return () => {
      if (intervalId) window.clearInterval(intervalId);
    };
  }, [isPipActive, status, drawTimer]);

  const togglePiP = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) {
      toast.error("PiP 초기화 실패");
      return;
    }

    if (!isSupported) {
      toast.error("이 브라우저는 PiP를 지원하지 않습니다");
      return;
    }

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
        if (isMounted.current) setIsPipActive(false);
        toast.success("PiP 모드를 종료했습니다");
      } else {
        // Ensure stream is connected (should already be from init)
        if (videoRef.current.srcObject == null) {
          const stream = canvasRef.current.captureStream(30);
          videoRef.current.srcObject = stream;
        }

        // Ensure video is playing (may have been paused by browser)
        if (videoRef.current.paused) {
          await videoRef.current.play();
        }

        // Draw current frame
        drawTimer();

        // Request PiP
        const pipWindow = await videoRef.current.requestPictureInPicture();
        if (isMounted.current) {
          setIsPipActive(true);
          const initialSize = { width: pipWindow.width || 400, height: pipWindow.height || 400 };
          updateCanvasSize(initialSize.width, initialSize.height);
          console.log('[PiP] Opened with size:', initialSize);
        }
        toast.success("타이머가 PiP 모드로 전환되었습니다");

        // Track PiP window size changes
        pipWindow.addEventListener('resize', () => {
          if (isMounted.current) {
            const newSize = { width: pipWindow.width, height: pipWindow.height };
            updateCanvasSize(newSize.width, newSize.height);
            console.log('[PiP] Window resized:', newSize);
            // Immediately redraw when size changes
            drawTimer();
          }
        });

        // Handle PiP close
        videoRef.current.onleavepictureinpicture = () => {
          if (isMounted.current) {
            setIsPipActive(false);
            updateCanvasSize(400, 400);
          }
        };
      }
    } catch (error) {
      console.error("Failed to toggle PiP:", error);
      const err = error as Error;

      if (err.name === 'NotAllowedError') {
        toast.error("PiP 권한이 거부되었습니다");
      } else if (err.name === 'NotSupportedError') {
        toast.error("PiP가 지원되지 않습니다");
      } else if (err.name === 'InvalidStateError') {
        toast.error("PiP를 시작할 수 없습니다. 비디오를 먼저 재생해주세요");
      } else {
        toast.error("PiP 실행 중 오류가 발생했습니다");
      }
    }
  }, [isSupported, drawTimer, updateCanvasSize]);

  // Handle Browser Native PiP Button
  useEffect(() => {
    if (!('mediaSession' in navigator)) return;
    try {
      navigator.mediaSession.setActionHandler('enterpictureinpicture' as any, () => {
        togglePiP();
      });
    } catch (e) {
      console.debug('MediaSession enterpictureinpicture action not supported');
    }
    return () => {
      try {
        navigator.mediaSession.setActionHandler('enterpictureinpicture' as any, null);
      } catch (e) {}
    };
  }, [togglePiP]);

  // Setup MediaSession API for PiP controls
  useEffect(() => {
    if (!isPipActive || !('mediaSession' in navigator) || !onPlayPause) {
      // Return empty cleanup function when conditions not met
      return () => {};
    }

    const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    const sessionLabel = sessionType === "focus" ? "집중 시간" : "휴식 시간";

    // Set metadata
    navigator.mediaSession.metadata = new MediaMetadata({
      title: `FocusMate - ${sessionLabel}`,
      artist: userName,
      album: timeStr,
    });

    // Set action handlers
    navigator.mediaSession.setActionHandler('play', () => {
      if (status === 'paused' || status === 'idle') {
        onPlayPause();
      }
    });

    navigator.mediaSession.setActionHandler('pause', () => {
      if (status === 'running') {
        onPlayPause();
      }
    });

    // Update playback state
    navigator.mediaSession.playbackState = status === 'running' ? 'playing' : 'paused';

    return () => {
      if ('mediaSession' in navigator) {
        navigator.mediaSession.setActionHandler('play', null);
        navigator.mediaSession.setActionHandler('pause', null);
      }
    };
  }, [isPipActive, status, minutes, seconds, sessionType, userName, onPlayPause]);



  return { togglePiP, isPipActive, isSupported };
}
