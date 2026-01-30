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
  const pipWindowRef = useRef<PictureInPictureWindow | null>(null);
  const rafRef = useRef<number | null>(null);
  const squareBgRef = useRef<HTMLCanvasElement | null>(null);
  const wideBgRef = useRef<HTMLCanvasElement | null>(null);
  const squareBgKeyRef = useRef<string>("");
  const wideBgKeyRef = useRef<string>("");
  const squareTextRef = useRef<HTMLCanvasElement | null>(null);
  const wideTextRef = useRef<HTMLCanvasElement | null>(null);
  const squareTextKeyRef = useRef<string>("");
  const wideTextKeyRef = useRef<string>("");
  const squareTrackRef = useRef<HTMLCanvasElement | null>(null);
  const squareTrackKeyRef = useRef<string>("");
  const squareProgressGradientRef = useRef<CanvasGradient | null>(null);
  const squareProgressKeyRef = useRef<string>("");
  const wideTrackPatternRef = useRef<CanvasPattern | null>(null);
  const wideTrackPatternKeyRef = useRef<string>("");
  const wideFillPatternRef = useRef<CanvasPattern | null>(null);
  const wideFillPatternKeyRef = useRef<string>("");

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
    const now = Date.now() / 1000;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Determine display level based on ACTUAL PiP window size
    // Get real-time size from pictureInPictureElement instead of state
    const pipElement = document.pictureInPictureElement as HTMLVideoElement | null;
    const windowWidth = pipWindowRef.current?.width || 0;
    const windowHeight = pipWindowRef.current?.height || 0;
    const actualWidth = windowWidth || pipElement?.width || pipWindowSize.width || width;
    const actualHeight = windowHeight || pipElement?.height || pipWindowSize.height || height;

    const pipWidth = actualWidth > 0 ? actualWidth : width;
    const pipHeight = actualHeight > 0 ? actualHeight : height;

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

    const drawSquareBackground = () => {
      const key = `${width}x${height}`;
      if (!squareBgRef.current || squareBgKeyRef.current !== key) {
        const bg = document.createElement("canvas");
        bg.width = width;
        bg.height = height;
        const bgCtx = bg.getContext("2d");
        if (bgCtx) {
          const bgGradient = bgCtx.createRadialGradient(centerX, centerY, 0, centerX, centerY, width);
          bgGradient.addColorStop(0, "#27272a");
          bgGradient.addColorStop(0.7, "#18181b");
          bgGradient.addColorStop(1, "#09090b");
          bgCtx.fillStyle = bgGradient;
          bgCtx.fillRect(0, 0, width, height);
        }
        squareBgRef.current = bg;
        squareBgKeyRef.current = key;
      }
      if (squareBgRef.current) {
        ctx.drawImage(squareBgRef.current, 0, 0);
      }
    };

    const drawWideBackground = () => {
      const key = `${width}x${height}`;
      if (!wideBgRef.current || wideBgKeyRef.current !== key) {
        const bg = document.createElement("canvas");
        bg.width = width;
        bg.height = height;
        const bgCtx = bg.getContext("2d");
        if (bgCtx) {
          const bgGradient = bgCtx.createLinearGradient(0, 0, width, 0);
          bgGradient.addColorStop(0, "#18181b");
          bgGradient.addColorStop(1, "#09090b");
          bgCtx.fillStyle = bgGradient;
          bgCtx.fillRect(0, 0, width, height);
        }
        wideBgRef.current = bg;
        wideBgKeyRef.current = key;
      }
      if (wideBgRef.current) {
        ctx.drawImage(wideBgRef.current, 0, 0);
      }
    };

    const drawSquareText = () => {
      const key = `${width}x${height}|${userName}|${sessionType}|${isSmall ? "S" : "M"}|${status}`;
      if (!squareTextRef.current || squareTextKeyRef.current !== key) {
        const textCanvas = document.createElement("canvas");
        textCanvas.width = width;
        textCanvas.height = height;
        const textCtx = textCanvas.getContext("2d");
        if (textCtx) {
          // Name
          textCtx.font = "500 20px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
          textCtx.fillStyle = "#a1a1aa";
          textCtx.textAlign = "center";
          textCtx.textBaseline = "middle";
          textCtx.fillText(userName, centerX, centerY - 80);

          // Session label
          const sessionLabel = sessionType === "focus" ? "FOCUS" : "BREAK";
          textCtx.font = "800 26px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
          textCtx.fillStyle = sessionType === "focus" ? "#fca5a5" : "#93c5fd";
          textCtx.shadowColor = sessionType === "focus" ? "rgba(239, 68, 68, 0.5)" : "rgba(59, 130, 246, 0.5)";
          textCtx.shadowBlur = 12;
          textCtx.fillText(sessionLabel, centerX, centerY - 50);
          textCtx.shadowBlur = 0;
        }
        squareTextRef.current = textCanvas;
        squareTextKeyRef.current = key;
      }
      if (squareTextRef.current) {
        ctx.drawImage(squareTextRef.current, 0, 0);
      }
    };

    const drawWideText = () => {
      const leftText = participantCount > 0
        ? `${participantCount}명 집중 중 · ${etaInfo.percentText}`
        : `${etaInfo.percentText}`;
      const rightText = etaInfo.etaText ? `종료 ${etaInfo.etaText}` : "";
      const key = `${width}x${height}|${leftText}|${rightText}|${status}|${sessionType}`;
      if (!wideTextRef.current || wideTextKeyRef.current !== key) {
        const textCanvas = document.createElement("canvas");
        textCanvas.width = width;
        textCanvas.height = height;
        const textCtx = textCanvas.getContext("2d");
        if (textCtx) {
          const scale = Math.min(1.6, Math.max(1, width / 800));
          const paddingX = Math.round(16 * scale);
          const barWidth = Math.max(Math.round(120 * scale), width - paddingX * 2);
          const barX = (width - barWidth) / 2;

          textCtx.font = `${Math.round(12 * scale)}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`;
          textCtx.fillStyle = "#a1a1aa";
          textCtx.textAlign = "left";
          textCtx.textBaseline = "middle";
          textCtx.shadowColor = "rgba(0, 0, 0, 0.2)";
          textCtx.shadowBlur = 6 * scale;
          textCtx.fillText(leftText, barX, Math.round(height * 0.35));

          if (rightText) {
            textCtx.textAlign = "right";
            textCtx.fillText(rightText, barX + barWidth, Math.round(height * 0.35));
          }
          textCtx.shadowBlur = 0;
        }
        wideTextRef.current = textCanvas;
        wideTextKeyRef.current = key;
      }
      if (wideTextRef.current) {
        ctx.drawImage(wideTextRef.current, 0, 0);
      }
    };

    const drawSquareTrack = () => {
      const key = `${width}x${height}|${radius}`;
      if (!squareTrackRef.current || squareTrackKeyRef.current !== key) {
        const trackCanvas = document.createElement("canvas");
        trackCanvas.width = width;
        trackCanvas.height = height;
        const trackCtx = trackCanvas.getContext("2d");
        if (trackCtx) {
          trackCtx.beginPath();
          trackCtx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
          trackCtx.strokeStyle = "rgba(255, 255, 255, 0.1)";
          trackCtx.lineWidth = 12;
          trackCtx.lineCap = "round";
          trackCtx.stroke();
        }
        squareTrackRef.current = trackCanvas;
        squareTrackKeyRef.current = key;
      }
      if (squareTrackRef.current) {
        ctx.drawImage(squareTrackRef.current, 0, 0);
      }
    };

    const getSquareProgressGradient = () => {
      const key = `${width}x${height}|${status}|${sessionType}`;
      if (!squareProgressGradientRef.current || squareProgressKeyRef.current !== key) {
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        if (status === "completed") {
          gradient.addColorStop(0, "#22c55e");
          gradient.addColorStop(1, "#86efac");
        } else if (sessionType === "focus") {
          gradient.addColorStop(0, "#ef4444");
          gradient.addColorStop(1, "#f97316");
        } else {
          gradient.addColorStop(0, "#3b82f6");
          gradient.addColorStop(1, "#06b6d4");
        }
        squareProgressGradientRef.current = gradient;
        squareProgressKeyRef.current = key;
      }
      return squareProgressGradientRef.current!;
    };

    const getWideTrackPattern = (barHeight: number) => {
      const key = `${barHeight}`;
      if (!wideTrackPatternRef.current || wideTrackPatternKeyRef.current !== key) {
        const patternCanvas = document.createElement("canvas");
        patternCanvas.width = 160;
        patternCanvas.height = barHeight;
        const pctx = patternCanvas.getContext("2d");
        if (pctx) {
          const grad = pctx.createLinearGradient(0, 0, patternCanvas.width, 0);
          grad.addColorStop(0, "rgba(255, 255, 255, 0.06)");
          grad.addColorStop(0.5, "rgba(255, 255, 255, 0.14)");
          grad.addColorStop(1, "rgba(255, 255, 255, 0.06)");
          pctx.fillStyle = grad;
          pctx.fillRect(0, 0, patternCanvas.width, barHeight);
        }
        wideTrackPatternRef.current = ctx.createPattern(patternCanvas, "repeat");
        wideTrackPatternKeyRef.current = key;
      }
      return wideTrackPatternRef.current!;
    };

    const getWideFillPattern = (barHeight: number) => {
      const key = `${barHeight}|${sessionType}`;
      if (!wideFillPatternRef.current || wideFillPatternKeyRef.current !== key) {
        const patternCanvas = document.createElement("canvas");
        patternCanvas.width = 160;
        patternCanvas.height = barHeight;
        const pctx = patternCanvas.getContext("2d");
        if (pctx) {
          const grad = pctx.createLinearGradient(0, 0, patternCanvas.width, 0);
          if (sessionType === "focus") {
            grad.addColorStop(0, "rgba(239, 68, 68, 1)");
            grad.addColorStop(0.5, "rgba(249, 115, 22, 1)");
            grad.addColorStop(1, "rgba(239, 68, 68, 1)");
          } else {
            grad.addColorStop(0, "rgba(59, 130, 246, 1)");
            grad.addColorStop(0.5, "rgba(6, 182, 212, 1)");
            grad.addColorStop(1, "rgba(59, 130, 246, 1)");
          }
          pctx.fillStyle = grad;
          pctx.fillRect(0, 0, patternCanvas.width, barHeight);
        }
        wideFillPatternRef.current = ctx.createPattern(patternCanvas, "repeat");
        wideFillPatternKeyRef.current = key;
      }
      return wideFillPatternRef.current!;
    };

    if (isWide) {
      // Wide bar-only layout
      const scale = Math.min(1.6, Math.max(1, width / 800));
      const paddingX = Math.round(16 * scale);
      const barHeight = Math.round(8 * scale);
      const barWidth = Math.max(Math.round(120 * scale), width - paddingX * 2);
      const barX = (width - barWidth) / 2;
      const barY = Math.round(height * 0.55);

      drawWideBackground();

      drawWideText();

      const fillWidth = (Math.max(0, Math.min(100, etaInfo.percentValue)) / 100) * barWidth;

      // Track (animated gradient background)
      const trackOffset = (now * 40) % 160;
      const trackPattern = getWideTrackPattern(barHeight);
      ctx.beginPath();
      ctx.save();
      ctx.translate(-trackOffset, 0);
      ctx.fillStyle = trackPattern;
      drawRoundRect(barX, barY, barWidth, barHeight, Math.round(4 * scale));
      ctx.fill();
      ctx.restore();

      // Fill (animated gradient + breathe)
      if (fillWidth > 0) {
        const breathe = (Math.sin(now * 2) + 1) / 2; // 0..1
        const fillOffset = (now * 60) % 160;
        const fillPattern = getWideFillPattern(barHeight);
        ctx.beginPath();
        ctx.save();
        ctx.globalAlpha = 0.55 + 0.3 * breathe;
        ctx.translate(-fillOffset, 0);
        ctx.fillStyle = fillPattern;
        drawRoundRect(barX, barY, fillWidth, barHeight, Math.round(4 * scale));
        ctx.fill();
        ctx.restore();
      }

      // Moving highlight sweep on the bar (subtle)
      if (status === "running" && fillWidth > 0) {
        const sweepWidth = Math.max(Math.round(24 * scale), Math.round(barWidth * 0.15));
        const speed = 90 * scale; // px/sec
        const travel = barWidth + sweepWidth;
        const offset = (now * speed) % travel;
        const sweepX = barX + offset - sweepWidth;

        ctx.beginPath();
        ctx.globalCompositeOperation = "lighter";
        ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
        drawRoundRect(sweepX, barY - Math.round(1 * scale), sweepWidth, barHeight + Math.round(2 * scale), Math.round(6 * scale));
        ctx.fill();
        ctx.globalCompositeOperation = "source-over";
      }

      // Alive particles inside the filled bar
      if (status === "running" && fillWidth > 0) {
        ctx.save();
        ctx.globalCompositeOperation = "lighter";
        const particleCount = 8;
        for (let i = 0; i < particleCount; i++) {
          const phase = (now * 40 + i * (barWidth / particleCount)) % barWidth;
          const px = barX + phase;
          if (px > barX + fillWidth) continue;
          const py = barY + barHeight / 2 + Math.sin(now * 2 + i) * (barHeight * 0.35);
          ctx.beginPath();
          ctx.fillStyle = "rgba(255, 255, 255, 0.18)";
          ctx.arc(px, py, Math.max(1.2, 2 * scale), 0, 2 * Math.PI);
          ctx.fill();
        }
        ctx.restore();
      }

      // Neon baseline glow under bar
      ctx.beginPath();
      ctx.globalCompositeOperation = "lighter";
      ctx.strokeStyle = sessionType === "focus" ? "rgba(239, 68, 68, 0.1)" : "rgba(59, 130, 246, 0.1)";
      ctx.lineWidth = Math.max(1, Math.round(2 * scale));
      ctx.shadowColor = sessionType === "focus" ? "rgba(239, 68, 68, 0.2)" : "rgba(59, 130, 246, 0.2)";
      ctx.shadowBlur = 6 * scale;
      ctx.moveTo(barX, barY + barHeight + Math.round(6 * scale));
      ctx.lineTo(barX + barWidth, barY + barHeight + Math.round(6 * scale));
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.globalCompositeOperation = "source-over";

      // Pulse at fill edge
      if (status === "running") {
        const alpha = (Math.sin(now * 2) + 1) / 2 * 0.5 + 0.2;
        const pulseX = barX + Math.max(6, fillWidth);
        const pulseY = barY + barHeight / 2;
        ctx.beginPath();
        ctx.arc(pulseX, pulseY, Math.round(5 * scale), 0, 2 * Math.PI);
        ctx.fillStyle = sessionType === "focus" ? `rgba(239, 68, 68, ${alpha})` : `rgba(59, 130, 246, ${alpha})`;
        ctx.shadowColor = sessionType === "focus" ? "#ef4444" : "#3b82f6";
        ctx.shadowBlur = 10 * alpha * scale;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
      return;
    }

    // 1. Modern Deep Gradient Background (cached)
    drawSquareBackground();

    // 2. Draw Status Indicator (User Name & Session) - Top (cached)
    drawSquareText();

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

    // 4. Progress Ring with Gradient & Glow
    // Background Ring (Track) - cached
    drawSquareTrack();

    // Foreground Ring (Progress)
    if (progress > 0) {
        const startAngle = -0.5 * Math.PI; // Top
        const endAngle = startAngle + (2 * Math.PI * (progress / 100));

        ctx.beginPath();
        // Counter-clockwise for "countdown" feel? No, standard clockwise is better for "progress done"
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);

        const gradient = getSquareProgressGradient();
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

    // Medium-only breathing ring accents (soft pulse)
    if (isMedium && status === "running") {
      const smoothPulse = 0.5 - 0.5 * Math.cos(now * 1.6);
      const ringAlpha = 0.06 + 0.08 * smoothPulse;

      ctx.beginPath();
      ctx.strokeStyle = sessionType === "focus"
        ? `rgba(239, 68, 68, ${ringAlpha})`
        : `rgba(59, 130, 246, ${ringAlpha})`;
      ctx.lineWidth = 2;
      ctx.arc(centerX, centerY, radius + 14, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // Medium-only extra motion accents
    if (isMedium && status === "running") {
      const time = Date.now() / 1000;
      const arcStart = time * 0.8;
      const arcEnd = arcStart + Math.PI * 0.35;

      ctx.beginPath();
      ctx.strokeStyle = sessionType === "focus" ? "rgba(239, 68, 68, 0.25)" : "rgba(59, 130, 246, 0.25)";
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.arc(centerX, centerY, radius + 10, arcStart, arcEnd);
      ctx.stroke();

      const pulse = (Math.sin(time * 2) + 1) / 2;
      ctx.beginPath();
      ctx.strokeStyle = sessionType === "focus"
        ? `rgba(239, 68, 68, ${0.06 + 0.08 * pulse})`
        : `rgba(59, 130, 246, ${0.06 + 0.08 * pulse})`;
      ctx.lineWidth = 1;
      ctx.arc(centerX, centerY, radius + 18, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // 6. Participant Count (Small/Medium)
    let participantTextY = 0;
    if (participantCount > 0) {
      ctx.font = "600 15px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
      ctx.fillStyle = "#a1a1aa"; // zinc-400
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const participantText = `${participantCount}명 집중 중`;
      participantTextY = centerY + radius + (isMedium ? 25 : 20);

      ctx.fillText(participantText, centerX, participantTextY);
    }

    // 8. Pulse / Breathing Effect (Bottom Indicator)
    const pulseActive = status === "running" || status === "completed";
    if (pulseActive) {
      const speed = status === "completed" ? 0.9 : 1.6;
      const smoothPulse = 0.5 - 0.5 * Math.cos(now * speed);
      const alpha = 0.2 + 0.25 * smoothPulse;

      let dotY = centerY + radius + 45;
      if (participantTextY > 0) {
        dotY = Math.max(dotY, participantTextY + 18);
      }

      const pulseColor = status === "completed"
        ? "#22c55e"
        : (sessionType === "focus" ? "#ef4444" : "#3b82f6");

      ctx.beginPath();
      ctx.arc(centerX, dotY, 5, 0, 2 * Math.PI);

      ctx.fillStyle = `rgba(${pulseColor === "#22c55e" ? "34, 197, 94" : pulseColor === "#ef4444" ? "239, 68, 68" : "59, 130, 246"}, ${alpha})`;
      ctx.shadowColor = pulseColor;
      ctx.shadowBlur = 6 + 6 * smoothPulse;
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

  // Poll PiP window size to ensure Small/Medium transitions work across browsers
  useEffect(() => {
    if (!isPipActive) return;
    const id = window.setInterval(() => {
      const w = pipWindowRef.current?.width || 0;
      const h = pipWindowRef.current?.height || 0;
      if (w > 0 && h > 0) {
        setPipWindowSize({ width: w, height: h });
      }
    }, 200);

    return () => window.clearInterval(id);
  }, [isPipActive]);

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
        pipWindowRef.current = pipWindow;
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
          pipWindowRef.current = null;
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
