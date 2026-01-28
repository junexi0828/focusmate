import { useCallback, useEffect, useRef, useState } from "react";
import { TimerStatus, SessionType } from "../components/TimerDisplay";

interface UseTimerPiPProps {
  minutes: number;
  seconds: number;
  status: TimerStatus;
  sessionType: SessionType;
  progress: number; // 0-100
}

export function useTimerPiP({
  minutes,
  seconds,
  status,
  sessionType,
  progress,
}: UseTimerPiPProps) {
  const [isPipActive, setIsPipActive] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const rafRef = useRef<number | null>(null);

  // Initialize canvas and video elements once
  useEffect(() => {
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
      videoRef.current = video;

      // Cleanup listener on unmount
      return () => {
        video.removeEventListener("leavepictureinpicture", () => {});
      };
    }
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

    // Filter Background (Dark theme assumed for PiP legibility)
    ctx.fillStyle = "#09090b"; // zinc-950
    ctx.fillRect(0, 0, width, height);

    // Draw Session Text
    ctx.font = "bold 40px Inter, sans-serif";
    ctx.fillStyle = "#a1a1aa"; // zinc-400
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const sessionLabel = sessionType === "focus" ? "FOCUS" : "BREAK";
    ctx.fillText(sessionLabel, centerX, centerY - 80);

    // Draw Time
    const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    ctx.font = "bold 120px monospace"; // Monospace for stable numbers
    ctx.fillStyle = status === "running" ? "#ffffff" : "#fbbf24"; // White or Amber (paused)
    if (status === "completed") ctx.fillStyle = "#22c55e"; // Green

    // Add simple pulse effect if running
    if (status === "running") {
        // Subtle opacity pulse could be simulated by alpha?
        // For simplicity, we just keep it solid white for clarity
    }

    ctx.fillText(timeStr, centerX, centerY + 20);

    // Draw Progress Ring
    // Background Ring
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = "#27272a"; // zinc-800
    ctx.lineWidth = 20;
    ctx.stroke();

    // Foreground Ring
    const startAngle = -0.5 * Math.PI; // Top
    const endAngle = startAngle + (2 * Math.PI * (progress / 100));

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.strokeStyle = status === 'completed' ? '#22c55e' : (sessionType === 'focus' ? '#ef4444' : '#3b82f6');
    ctx.lineWidth = 20;
    ctx.lineCap = "round";
    ctx.stroke();
  }, [minutes, seconds, status, sessionType, progress]);

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

  const togglePiP = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
        setIsPipActive(false);
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
        setIsPipActive(true);

        videoRef.current.onleavepictureinpicture = () => {
          setIsPipActive(false);
        };
      }
    } catch (error) {
      console.error("Failed to toggle PiP:", error);
    }
  };

  return { togglePiP, isPipActive };
}
