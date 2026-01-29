import { useCallback, useEffect, useRef, useState } from "react";
import { TimerStatus, SessionType } from "../components/TimerDisplay";
import { toast } from "sonner";

interface UseTimerPiPProps {
  minutes: number;
  seconds: number;
  status: TimerStatus;
  sessionType: SessionType;
  progress: number; // 0-100
  pipMode?: "square" | "wide";
  userName?: string; // User name to display
  onPlayPause?: () => void; // Callback for play/pause from PiP controls
  participantCount?: number; // Number of active participants
}

export function useTimerPiP({
  minutes,
  seconds,
  status,
  sessionType,
  progress,
  pipMode = "square",
  userName = "User",
  onPlayPause,
  participantCount = 0,
}: UseTimerPiPProps) {
  const isMounted = useRef(true);
  const [isPipActive, setIsPipActive] = useState(false);
  const [pipWindowSize, setPipWindowSize] = useState<{ width: number; height: number }>({ width: 400, height: 400 });
  const [etaInfo, setEtaInfo] = useState<{ text: string; percentText: string; percentValue: number; etaText: string }>({
    text: "",
    percentText: "",
    percentValue: 0,
    etaText: ""
  });
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

  useEffect(() => {
    const remainingSeconds = minutes * 60 + seconds;
    const eta = new Date(Date.now() + remainingSeconds * 1000);
    const etaText = `${String(eta.getHours()).padStart(2, "0")}:${String(eta.getMinutes()).padStart(2, "0")}`;
    const percentValue = Math.round(progress);
    const percentText = `${percentValue}%`;
    setEtaInfo({ text: `종료 ${etaText} · ${percentText}`, percentText, percentValue, etaText });
  }, [minutes, seconds, progress]);

  useEffect(() => {
    const nextSize = pipMode === "wide" ? { width: 800, height: 200 } : { width: 400, height: 400 };
    if (canvasRef.current) {
      canvasRef.current.width = nextSize.width;
      canvasRef.current.height = nextSize.height;
    }
    setPipWindowSize(nextSize);

    if (isPipActive && document.pictureInPictureElement) {
      document.exitPictureInPicture().catch(() => {});
      setIsPipActive(false);
      toast.info("PiP 모드가 변경되어 종료되었습니다. 다시 켜주세요.");
    }
  }, [pipMode, isPipActive]);

  const drawTimer = useCallback(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx || !canvasRef.current) return;

    const width = canvasRef.current.width;
    const height = canvasRef.current.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 145; // Adjusted for 400x400 canvas

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Determine display level based on ACTUAL PiP window size
    // Get real-time size from pictureInPictureElement instead of state
    const pipElement = document.pictureInPictureElement as HTMLVideoElement | null;
    const actualWidth = pipElement?.width || pipWindowSize.width || width;
    const actualHeight = pipElement?.height || pipWindowSize.height || height;

    const pipWidth = actualWidth;
    const pipHeight = actualHeight;

    // Level 1 (Small): Timer only - matches browser minimum (<300px width)
    // Level 2 (Medium): Timer + Participant count (>=300px)
    const isWide = pipMode === "wide";
    const isSmall = !isWide && (pipWidth < 300 || pipHeight < 250);
    const isMedium = !isWide && !isSmall;

    // Debug: Log size and level (only when PiP is active)
    if (document.pictureInPictureElement) {
      console.log(
        `[PiP] Size: ${pipWidth}x${pipHeight}, Level: ${isWide ? 'Wide' : isSmall ? 'Small' : 'Medium'}`
      );
    }

    const drawRoundRect = (x: number, y: number, w: number, h: number, r: number) => {
      if ("roundRect" in ctx) {
        (ctx as CanvasRenderingContext2D & { roundRect: Function }).roundRect(x, y, w, h, r);
      } else {
        ctx.rect(x, y, w, h);
      }
    };

    if (isWide) {
      // Wide bar-only layout
      const scale = Math.min(1.6, Math.max(1, width / 800));
      const paddingX = Math.round(16 * scale);
      const barHeight = Math.round(8 * scale);
      const barWidth = Math.max(Math.round(120 * scale), width - paddingX * 2);
      const barX = (width - barWidth) / 2;
      const barY = Math.round(height * 0.55);

      // Background
      const bgGradient = ctx.createLinearGradient(0, 0, width, 0);
      bgGradient.addColorStop(0, "#18181b");
      bgGradient.addColorStop(1, "#09090b");
      ctx.fillStyle = bgGradient;
      ctx.fillRect(0, 0, width, height);

      // Left text: participants + percent
      const leftText = participantCount > 0
        ? `${participantCount}명 집중 중 · ${etaInfo.percentText}`
        : `${etaInfo.percentText}`;
      ctx.font = `${Math.round(12 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
      ctx.fillStyle = "#a1a1aa";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.shadowColor = "rgba(0, 0, 0, 0.2)";
      ctx.shadowBlur = 6 * scale;
      ctx.fillText(leftText, barX, Math.round(height * 0.35));

      // Right text: ETA
      if (etaInfo.etaText) {
        ctx.textAlign = "right";
        ctx.fillText(`종료 ${etaInfo.etaText}`, barX + barWidth, Math.round(height * 0.35));
      }
      ctx.shadowBlur = 0;

      // Track
      ctx.beginPath();
      ctx.fillStyle = "rgba(255, 255, 255, 0.12)";
      drawRoundRect(barX, barY, barWidth, barHeight, Math.round(4 * scale));
      ctx.fill();

      // Fill
      const fillWidth = (Math.max(0, Math.min(100, etaInfo.percentValue)) / 100) * barWidth;
      if (fillWidth > 0) {
        ctx.beginPath();
        const time = Date.now() / 1000;
        const breathe = (Math.sin(time * 2) + 1) / 2; // 0..1
        ctx.fillStyle = sessionType === "focus"
          ? `rgba(239, 68, 68, ${0.7 + 0.3 * breathe})`
          : `rgba(59, 130, 246, ${0.7 + 0.3 * breathe})`;
        drawRoundRect(barX, barY, fillWidth, barHeight, Math.round(4 * scale));
        ctx.fill();
      }

      // Moving highlight sweep on the bar (subtle)
      if (status === "running" && fillWidth > 0) {
        const time = Date.now() / 1000;
        const sweepWidth = Math.max(Math.round(24 * scale), Math.round(barWidth * 0.15));
        const speed = 90 * scale; // px/sec
        const travel = barWidth + sweepWidth;
        const offset = (time * speed) % travel;
        const sweepX = barX + offset - sweepWidth;

        ctx.beginPath();
        ctx.globalCompositeOperation = "lighter";
        ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
        drawRoundRect(sweepX, barY - Math.round(1 * scale), sweepWidth, barHeight + Math.round(2 * scale), Math.round(6 * scale));
        ctx.fill();
        ctx.globalCompositeOperation = "source-over";
      }

      // Neon baseline glow under bar
      ctx.beginPath();
      ctx.globalCompositeOperation = "lighter";
      ctx.strokeStyle = sessionType === "focus" ? "rgba(239, 68, 68, 0.18)" : "rgba(59, 130, 246, 0.18)";
      ctx.lineWidth = Math.max(1, Math.round(2 * scale));
      ctx.shadowColor = sessionType === "focus" ? "rgba(239, 68, 68, 0.35)" : "rgba(59, 130, 246, 0.35)";
      ctx.shadowBlur = 10 * scale;
      ctx.moveTo(barX, barY + barHeight + Math.round(6 * scale));
      ctx.lineTo(barX + barWidth, barY + barHeight + Math.round(6 * scale));
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.globalCompositeOperation = "source-over";

      // Pulse at fill edge
      if (status === "running") {
        const time = Date.now() / 1000;
        const alpha = (Math.sin(time * 2) + 1) / 2 * 0.6 + 0.2;
        const pulseX = barX + Math.max(6, fillWidth);
        const pulseY = barY + barHeight / 2;
        ctx.beginPath();
        ctx.arc(pulseX, pulseY, Math.round(6 * scale), 0, 2 * Math.PI);
        ctx.fillStyle = sessionType === "focus" ? `rgba(239, 68, 68, ${alpha})` : `rgba(59, 130, 246, ${alpha})`;
        ctx.shadowColor = sessionType === "focus" ? "#ef4444" : "#3b82f6";
        ctx.shadowBlur = 14 * alpha * scale;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
      return;
    }

    // 1. Modern Deep Gradient Background
    // Create a radial gradient for a "spotlight" effect
    const bgGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, width);
    bgGradient.addColorStop(0, "#27272a"); // zinc-800 center
    bgGradient.addColorStop(0.7, "#18181b"); // zinc-900 mid
    bgGradient.addColorStop(1, "#09090b");   // zinc-950 edge
    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, width, height);

    // 2. Draw Status Indicator (User Name & Session) - Top
    // Always show in Small/Medium
    ctx.font = "500 20px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    ctx.fillStyle = "#a1a1aa"; // zinc-400
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(userName, centerX, centerY - 80);

    // Session Type Active Text
    const sessionLabel = sessionType === "focus" ? "FOCUS" : "BREAK";
    ctx.font = "800 26px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    ctx.fillStyle = sessionType === "focus" ? "#fca5a5" : "#93c5fd"; // Soft Red or Blue
    ctx.shadowColor = sessionType === "focus" ? "rgba(239, 68, 68, 0.5)" : "rgba(59, 130, 246, 0.5)";
    ctx.shadowBlur = 12;
    ctx.fillText(sessionLabel, centerX, centerY - 50);
    ctx.shadowBlur = 0; // Reset shadow

    // 3. Draw Time (Modern Typography)
    const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    // Use tabular-nums feature settings if possible, or a font known for good tabular numbers
    ctx.font = "700 100px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
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

    ctx.fillText(timeStr, centerX, centerY + 20);
    ctx.shadowBlur = 0; // Reset

    // 4. Hologram-like accents (Square mode only)
    if (!isWide && status === "running") {
      const time = Date.now() / 1000;
      const pulse = (Math.sin(time * 1.6) + 1) / 2;

      ctx.save();
      ctx.translate(centerX, centerY);

      // Outer faint halo
      ctx.beginPath();
      ctx.strokeStyle = sessionType === "focus"
        ? `rgba(239, 68, 68, ${0.08 + 0.08 * pulse})`
        : `rgba(59, 130, 246, ${0.08 + 0.08 * pulse})`;
      ctx.lineWidth = 2;
      ctx.shadowColor = sessionType === "focus" ? "rgba(239, 68, 68, 0.25)" : "rgba(59, 130, 246, 0.25)";
      ctx.shadowBlur = 12;
      ctx.arc(0, 0, radius + 16, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Rotating thin rings
      const ringAlpha = 0.12 + 0.12 * pulse;
      ctx.rotate(time * 0.4);
      ctx.beginPath();
      ctx.strokeStyle = `rgba(255, 255, 255, ${ringAlpha})`;
      ctx.lineWidth = 1;
      ctx.arc(0, 0, radius + 8, 0.1, 2.2 * Math.PI);
      ctx.stroke();

      ctx.rotate(-time * 0.9);
      ctx.beginPath();
      ctx.strokeStyle = sessionType === "focus"
        ? `rgba(239, 68, 68, ${0.12 + 0.1 * pulse})`
        : `rgba(59, 130, 246, ${0.12 + 0.1 * pulse})`;
      ctx.lineWidth = 1;
      ctx.arc(0, 0, radius + 4, 1.3, 2.6 * Math.PI);
      ctx.stroke();

      // Subtle sparkle points
      for (let i = 0; i < 6; i++) {
        const angle = time * 0.8 + i * (Math.PI / 3);
        const x = Math.cos(angle) * (radius + 14);
        const y = Math.sin(angle) * (radius + 14);
        ctx.beginPath();
        ctx.fillStyle = `rgba(255,255,255, ${0.15 + 0.2 * pulse})`;
        ctx.arc(x, y, 1.5, 0, 2 * Math.PI);
        ctx.fill();
      }

      ctx.restore();
    }

    // 5. Progress Ring with Gradient & Glow
    // Background Ring (Track)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.1)"; // Very subtle white track
    ctx.lineWidth = 12;
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
        ctx.lineWidth = 12;
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
        ctx.arc(endX, endY, 10, 0, 2 * Math.PI);
        ctx.fillStyle = "#ffffff";
        ctx.shadowColor = "rgba(255,255,255,0.8)";
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    // 6. Participant Count (Small/Medium)
    let participantTextY = 0;
    if (participantCount > 0) {
      ctx.font = "600 15px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
      ctx.fillStyle = "#a1a1aa"; // zinc-400
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const participantText = `${participantCount}명 집중 중`;
      participantTextY = centerY + radius + (isMedium ? 38 : 25);

      ctx.fillText(participantText, centerX, participantTextY);
    }

    // 8. Pulse / Breathing Effect (Bottom Indicator)
    if (status === "running") {
      const time = Date.now() / 1000;
      const alpha = (Math.sin(time * 2) + 1) / 2 * 0.5 + 0.2; // 0.2 to 0.7

      let dotY = 390; // Fixed near bottom to ensure visibility
      if (participantTextY > 0) {
        dotY = Math.min(390, participantTextY + 20);
      }

      ctx.beginPath();
      ctx.arc(centerX, dotY, 6, 0, 2 * Math.PI);

      ctx.fillStyle = sessionType === 'focus' ? `rgba(239, 68, 68, ${alpha})` : `rgba(59, 130, 246, ${alpha})`;
      ctx.shadowColor = sessionType === 'focus' ? "#ef4444" : "#3b82f6";
      ctx.shadowBlur = 10 * alpha;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }, [minutes, seconds, status, sessionType, userName, participantCount, pipWindowSize, etaInfo, pipMode]);

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

        const modeSize = pipMode === "wide" ? { width: 800, height: 200 } : { width: 400, height: 400 };
        if (canvasRef.current) {
          canvasRef.current.width = modeSize.width;
          canvasRef.current.height = modeSize.height;
        }
        setPipWindowSize(modeSize);

        // Request PiP
        const pipWindow = await videoRef.current.requestPictureInPicture();
        if (isMounted.current) {
          setIsPipActive(true);
          const initialSize = { width: pipWindow.width || 400, height: pipWindow.height || 400 };
          setPipWindowSize(initialSize);
          console.log('[PiP] Opened with size:', initialSize);
        }
        toast.success("타이머가 PiP 모드로 전환되었습니다");

        // Track PiP window size changes
        pipWindow.addEventListener('resize', () => {
          if (isMounted.current) {
            const newSize = { width: pipWindow.width, height: pipWindow.height };
            setPipWindowSize(newSize);
            console.log('[PiP] Window resized:', newSize);
            // Immediately redraw when size changes
            drawTimer();
          }
        });

        // Handle PiP close
        videoRef.current.onleavepictureinpicture = () => {
          if (isMounted.current) {
            setIsPipActive(false);
            setPipWindowSize({ width: 400, height: 400 });
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
  }, [isSupported, drawTimer, pipMode]);

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
