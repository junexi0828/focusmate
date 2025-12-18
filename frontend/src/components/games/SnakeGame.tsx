/**
 * Snake Game - Classic snake
 */
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface SnakeGameProps {
  onGameOver: (score: number, time: number) => void;
}

export function SnakeGame({ onGameOver }: SnakeGameProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    if (!isPlaying || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d')!;
    const gridSize = 20;
    const tileCount = 30;

    // Game state
    let snake = [{ x: 15, y: 15 }];
    let direction = { x: 1, y: 0 };
    let nextDirection = { x: 1, y: 0 };
    let food = {
      x: Math.floor(Math.random() * tileCount),
      y: Math.floor(Math.random() * tileCount),
    };
    let gameScore = 0;
    let gameSpeed = 100;

    // Handle keyboard - document에 등록하여 모달 내부에서도 작동하도록
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!isPlaying) return;

      // 방향키 또는 WASD 지원
      if ((e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') && direction.y === 0) {
        e.preventDefault();
        e.stopPropagation();
        nextDirection = { x: 0, y: -1 };
      }
      if ((e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') && direction.y === 0) {
        e.preventDefault();
        e.stopPropagation();
        nextDirection = { x: 0, y: 1 };
      }
      if ((e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') && direction.x === 0) {
        e.preventDefault();
        e.stopPropagation();
        nextDirection = { x: -1, y: 0 };
      }
      if ((e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') && direction.x === 0) {
        e.preventDefault();
        e.stopPropagation();
        nextDirection = { x: 1, y: 0 };
      }
    };

    document.addEventListener('keydown', handleKeyPress, true);

    // Game loop
    const gameLoop = setInterval(() => {
      // Update direction
      direction = nextDirection;

      // Move snake
      const head = {
        x: snake[0].x + direction.x,
        y: snake[0].y + direction.y,
      };

      // Check wall collision
      if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        setGameOver(true);
        setIsPlaying(false);
        const playTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
        onGameOver(gameScore, playTime);
        clearInterval(gameLoop);
        return;
      }

      // Check self collision
      if (snake.some((segment) => segment.x === head.x && segment.y === head.y)) {
        setGameOver(true);
        setIsPlaying(false);
        const playTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
        onGameOver(gameScore, playTime);
        clearInterval(gameLoop);
        return;
      }

      snake.unshift(head);

      // Check food collision
      if (head.x === food.x && head.y === food.y) {
        gameScore += 10;
        setScore(gameScore);
        food = {
          x: Math.floor(Math.random() * tileCount),
          y: Math.floor(Math.random() * tileCount),
        };
        // Increase speed slightly
        if (gameScore % 50 === 0 && gameSpeed > 50) {
          gameSpeed -= 5;
          clearInterval(gameLoop);
        }
      } else {
        snake.pop();
      }

      // Clear canvas - use theme-aware color
      const bgColor = getComputedStyle(canvas).backgroundColor || '#111827';
      ctx.fillStyle = bgColor === "rgba(0, 0, 0, 0)" ? '#111827' : bgColor;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw grid
      ctx.strokeStyle = '#1f2937';
      for (let i = 0; i <= tileCount; i++) {
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
      }

      // Draw snake
      snake.forEach((segment, index) => {
        ctx.fillStyle = index === 0 ? '#10b981' : '#059669';
        ctx.fillRect(
          segment.x * gridSize + 1,
          segment.y * gridSize + 1,
          gridSize - 2,
          gridSize - 2
        );
      });

      // Draw food
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(
        food.x * gridSize + gridSize / 2,
        food.y * gridSize + gridSize / 2,
        gridSize / 2 - 2,
        0,
        Math.PI * 2
      );
      ctx.fill();

      // Draw score
      ctx.fillStyle = '#fff';
      ctx.font = '20px monospace';
      ctx.fillText(`Score: ${gameScore}`, 10, 25);
      ctx.fillText(`Length: ${snake.length}`, 10, 50);
    }, gameSpeed);

    return () => {
      document.removeEventListener('keydown', handleKeyPress, true);
      clearInterval(gameLoop);
    };
  }, [isPlaying, onGameOver]);

  const startGame = () => {
    setScore(0);
    setGameOver(false);
    setIsPlaying(true);
    startTimeRef.current = Date.now();
  };

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      <canvas
        ref={canvasRef}
        width={600}
        height={600}
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

      <p className="text-sm text-gray-400">Use arrow keys or WASD to control the snake</p>
    </div>
  );
}
