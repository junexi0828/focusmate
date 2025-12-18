/**
 * Dino Jump Game - Chrome dinosaur style
 */
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

interface DinoJumpProps {
  onGameOver: (score: number, time: number) => void;
}

export function DinoJump({ onGameOver }: DinoJumpProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const startTimeRef = useRef<number>(0);
  const gameLoopRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isPlaying || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d")!;
    const width = canvas.width;
    const height = canvas.height;

    // Game state
    let dino = {
      x: 50,
      y: height - 60,
      width: 40,
      height: 40,
      velocityY: 0,
      jumping: false,
    };

    let obstacles: Array<{
      x: number;
      width: number;
      height: number;
      scored?: boolean;
    }> = [];
    let gameScore = 0;
    let gameSpeed = 5;
    let obstacleTimer = 0;
    let animationFrameId: number | null = null;

    // 게임 루프 ID를 ref에 저장하여 cleanup 시 사용
    gameLoopRef.current = null;

    // Jump
    const jump = () => {
      if (!dino.jumping) {
        dino.velocityY = -15;
        dino.jumping = true;
      }
    };

    // Handle keyboard - document에 등록하여 모달 내부에서도 작동하도록
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.key === " " || e.key === "w" || e.key === "W" || e.key === "ArrowUp") {
        e.preventDefault();
        e.stopPropagation();
        if (isPlaying) {
          jump();
        }
      }
    };

    // Handle click/touch
    const handleClick = () => {
      if (isPlaying) {
        jump();
      }
    };

    // document에 이벤트 리스너 등록 (모달 내부에서도 작동)
    document.addEventListener("keydown", handleKeyPress, true);
    canvas.addEventListener("click", handleClick);
    canvas.addEventListener("touchstart", (e) => {
      e.preventDefault();
      handleClick();
    });

    // Game loop
    const gameLoop = () => {
      // 게임이 중지되었으면 루프 종료
      if (!isPlaying) {
        if (animationFrameId !== null) {
          cancelAnimationFrame(animationFrameId);
          animationFrameId = null;
        }
        return;
      }

      // Clear canvas
      ctx.fillStyle = "#1a1a1a";
      ctx.fillRect(0, 0, width, height);

      // Update dino
      dino.velocityY += 0.8; // Gravity
      dino.y += dino.velocityY;

      if (dino.y >= height - 60) {
        dino.y = height - 60;
        dino.velocityY = 0;
        dino.jumping = false;
      }

      // Draw dino
      ctx.fillStyle = "#10b981";
      ctx.fillRect(dino.x, dino.y, dino.width, dino.height);

      // Update obstacles
      obstacleTimer++;
      if (obstacleTimer > 60 / gameSpeed) {
        obstacles.push({
          x: width,
          width: 20 + Math.random() * 20,
          height: 40 + Math.random() * 40,
        });
        obstacleTimer = 0;
      }

      obstacles = obstacles.filter((obs) => obs.x + obs.width > 0);

      obstacles.forEach((obs) => {
        obs.x -= gameSpeed;

        // Draw obstacle
        ctx.fillStyle = "#ef4444";
        ctx.fillRect(obs.x, height - obs.height, obs.width, obs.height);

        // Check collision
        if (
          dino.x < obs.x + obs.width &&
          dino.x + dino.width > obs.x &&
          dino.y + dino.height > height - obs.height
        ) {
          setGameOver(true);
          setIsPlaying(false);
          const playTime = Math.floor(
            (Date.now() - startTimeRef.current) / 1000
          );
          onGameOver(gameScore, playTime);
          if (animationFrameId !== null) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
          }
          return;
        }

        // Score
        if (obs.x + obs.width < dino.x && !obs.scored) {
          gameScore += 10;
          setScore(gameScore);
          obs.scored = true;
        }
      });

      // Draw ground
      ctx.fillStyle = "#4b5563";
      ctx.fillRect(0, height - 10, width, 10);

      // Draw score
      ctx.fillStyle = "#fff";
      ctx.font = "20px monospace";
      ctx.fillText(`Score: ${gameScore}`, 10, 30);

      // Increase difficulty
      if (gameScore > 0 && gameScore % 100 === 0) {
        gameSpeed += 0.5;
      }

      if (isPlaying) {
        animationFrameId = requestAnimationFrame(gameLoop);
        gameLoopRef.current = animationFrameId;
      } else {
        // 게임이 중지되면 애니메이션 프레임 취소
        if (animationFrameId !== null) {
          cancelAnimationFrame(animationFrameId);
          animationFrameId = null;
          gameLoopRef.current = null;
        }
      }
    };

    // 게임 시작
    if (isPlaying) {
      animationFrameId = requestAnimationFrame(gameLoop);
      gameLoopRef.current = animationFrameId;
    }

    return () => {
      // Cleanup: 애니메이션 프레임 취소
      if (gameLoopRef.current !== null) {
        cancelAnimationFrame(gameLoopRef.current);
        gameLoopRef.current = null;
      }
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
      document.removeEventListener("keydown", handleKeyPress, true);
      canvas.removeEventListener("click", handleClick);
    };
  }, [isPlaying, onGameOver]);

  const startGame = () => {
    // 이전 게임 루프가 있으면 정리
    if (gameLoopRef.current !== null) {
      cancelAnimationFrame(gameLoopRef.current);
      gameLoopRef.current = null;
    }

    // 상태 초기화
    setScore(0);
    setGameOver(false);
    setIsPlaying(false); // 먼저 false로 설정하여 이전 useEffect cleanup 실행

    // 다음 프레임에서 게임 시작 (cleanup 완료 후)
    setTimeout(() => {
      setIsPlaying(true);
      startTimeRef.current = Date.now();
    }, 0);
  };

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      <canvas
        ref={canvasRef}
        width={800}
        height={400}
        className="border-2 border-border rounded-lg bg-background max-w-full h-auto"
        style={{ maxWidth: '100%', height: 'auto' }}
      />

      {!isPlaying && !gameOver && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={startGame}
          className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold"
        >
          Start Game
        </motion.button>
      )}

      {gameOver && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h3 className="text-2xl font-bold text-red-500 mb-2">Game Over!</h3>
          <p className="text-lg text-gray-300 mb-4">Final Score: {score}</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={startGame}
            className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold"
          >
            Play Again
          </motion.button>
        </motion.div>
      )}

      <p className="text-sm text-gray-400">Press SPACE, W, ↑ or click to jump</p>
    </div>
  );
}
