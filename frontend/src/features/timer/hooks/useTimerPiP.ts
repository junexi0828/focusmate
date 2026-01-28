import { useCallback, useEffect, useRef, useState } from "react";
import { TimerStatus, SessionType } from "../components/TimerDisplay";
import { toast } from "sonner";

interface UseTimerPiPProps {
  minutes: number;
  seconds: number;
  status: TimerStatus;
  sessionType: SessionType;
  progress: number; // 0-100
  userName?: string; // User name to display
  onPlayPause?: () => void; // Callback for play/pause from PiP controls
}

export function useTimerPiP({
  minutes,
  seconds,
  status,
  sessionType,
  progress,
  userName = "User",
  onPlayPause,
}: UseTimerPiPProps) {
  const isMounted = useRef(true);
  const [isPipActive, setIsPipActive] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const rafRef = useRef<number | null>(null);

  // Check browser support
  const isSupported = 'pictureInPictureEnabled' in document;

  // Initialize canvas and video elements once
  useEffect(() => {
    isMounted.current = true;
    if (!canvasRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 512;
      canvasRef.current = canvas;
    }

    if (!videoRef.current) {
      const video = document.createElement("video");
      video.muted = true;
      video.playsInline = true; // Important for generic browser support
      // Mount to DOM key for browser recognition
      video.style.position = 'absolute';
      video.style.width = '1px';
      video.style.height = '1px';
      video.style.opacity = '0';
      video.style.pointerEvents = 'none';
      video.style.zIndex = '-1';
      document.body.appendChild(video);
      videoRef.current = video;
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
    const centerY = height / 2;
    const radius = 200;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Background (Dark theme for PiP legibility)
    ctx.fillStyle = "#09090b"; // zinc-950
    ctx.fillRect(0, 0, width, height);

    // Draw User Name (top)
    ctx.font = "bold 32px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    ctx.fillStyle = "#a1a1aa"; // zinc-400
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(userName, centerX, centerY - 120);

    // Draw Session Type Text
    ctx.font = "bold 36px Inter, sans-serif";
    ctx.fillStyle = "#71717a"; // zinc-500
    const sessionLabel = sessionType === "focus" ? "FOCUS" : "BREAK";
    ctx.fillText(sessionLabel, centerX, centerY - 70);

    // Draw Time (large, centered)
    const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    ctx.font = "bold 120px 'SF Mono', 'Monaco', 'Courier New', monospace";
    ctx.fillStyle = status === "running" ? "#ffffff" : "#fbbf24"; // White or Amber (paused)
    if (status === "completed") ctx.fillStyle = "#22c55e"; // Green

    ctx.fillText(timeStr, centerX, centerY + 20);

    // Draw Progress Ring
    // Background Ring
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = "#27272a"; // zinc-800
    ctx.lineWidth = 20;
    ctx.stroke();

    // Foreground Ring (Progress)
    const startAngle = -0.5 * Math.PI; // Top
    const endAngle = startAngle + (2 * Math.PI * (progress / 100));

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.strokeStyle = status === 'completed' ? '#22c55e' : (sessionType === 'focus' ? '#ef4444' : '#3b82f6');
    ctx.lineWidth = 20;
    ctx.lineCap = "round";
    ctx.stroke();

    // Draw Status Indicator Dot (bottom center)
    const dotY = centerY + radius + 40;
    const dotRadius = 8;

    ctx.fillStyle = status === "running" ? "#22c55e" : (status === "paused" ? "#fbbf24" : "#71717a");
    ctx.beginPath();
    ctx.arc(centerX, dotY, dotRadius, 0, Math.PI * 2);
    ctx.fill();

    // Pulse effect for running status
    if (status === "running") {
      ctx.fillStyle = "rgba(34, 197, 94, 0.3)";
      ctx.beginPath();
      ctx.arc(centerX, dotY, dotRadius * 1.8, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [minutes, seconds, status, sessionType, progress, userName]);

  // Loop to keep updating the canvas stream
  const loop = useCallback(() => {
    drawTimer();
    rafRef.current = requestAnimationFrame(loop);
  }, [drawTimer]);

  // Start/Stop loop based on PiP status
  useEffect(() => {
    if (isPipActive) {
      loop();
    } else {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    }
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [isPipActive, loop]);

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
        // connect stream if needed
        if (videoRef.current.srcObject == null) {
          const stream = canvasRef.current.captureStream(30); // 30 FPS
          videoRef.current.srcObject = stream;
        }

        // Ensure video is playing for PiP to work
        await videoRef.current.play();

        // Initial draw before opening
        drawTimer();

        await videoRef.current.requestPictureInPicture();
        if (isMounted.current) setIsPipActive(true);
        toast.success("타이머가 PiP 모드로 전환되었습니다");

        videoRef.current.onleavepictureinpicture = () => {
          if (isMounted.current) setIsPipActive(false);
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
  }, [isSupported, drawTimer]);

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
