/**
 * Dot Collector Game - Pac-Man style dot collection
 */
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface DotCollectorProps {
  onGameOver: (score: number, time: number) => void;
}

export function DotCollector({ onGameOver }: DotCollectorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    if (!isPlaying || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d')!;
    const width = canvas.width;
    const height = canvas.height;

    // Game state
    let player = {
      x: width / 2,
      y: height / 2,
      radius: 15,
      speed: 4,
    };

    let dots: Array<{ x: number; y: number; collected: boolean }> = [];
    let enemies: Array<{ x: number; y: number; vx: number; vy: number }> = [];
    let gameScore = 0;
    let keys = { up: false, down: false, left: false, right: false };

    // Generate dots
    for (let i = 0; i < 50; i++) {
      dots.push({
        x: Math.random() * (width - 40) + 20,
        y: Math.random() * (height - 40) + 20,
        collected: false,
      });
    }

    // Generate enemies
    for (let i = 0; i < 3; i++) {
      enemies.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4,
      });
    }

    // Handle keyboard
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowUp' || e.key === 'w') keys.up = true;
      if (e.key === 'ArrowDown' || e.key === 's') keys.down = true;
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === 'ArrowUp' || e.key === 'w') keys.up = false;
      if (e.key === 'ArrowDown' || e.key === 's') keys.down = false;
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    // Game loop
    const gameLoop = () => {
      // Clear canvas
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, width, height);

      // Update player
      if (keys.up) player.y -= player.speed;
      if (keys.down) player.y += player.speed;
      if (keys.left) player.x -= player.speed;
      if (keys.right) player.x += player.speed;

      // Boundary check
      player.x = Math.max(player.radius, Math.min(width - player.radius, player.x));
      player.y = Math.max(player.radius, Math.min(height - player.radius, player.y));

      // Draw player
      ctx.fillStyle = '#fbbf24';
      ctx.beginPath();
      ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
      ctx.fill();

      // Draw and check dots
      dots.forEach((dot) => {
        if (dot.collected) return;

        const dx = player.x - dot.x;
        const dy = player.y - dot.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < player.radius + 5) {
          dot.collected = true;
          gameScore += 10;
          setScore(gameScore);
        }

        ctx.fillStyle = '#60a5fa';
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, 5, 0, Math.PI * 2);
        ctx.fill();
      });

      // Update and draw enemies
      enemies.forEach((enemy) => {
        enemy.x += enemy.vx;
        enemy.y += enemy.vy;

        // Bounce off walls
        if (enemy.x < 10 || enemy.x > width - 10) enemy.vx *= -1;
        if (enemy.y < 10 || enemy.y > height - 10) enemy.vy *= -1;

        // Draw enemy
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(enemy.x, enemy.y, 12, 0, Math.PI * 2);
        ctx.fill();

        // Check collision with player
        const dx = player.x - enemy.x;
        const dy = player.y - enemy.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < player.radius + 12) {
          setGameOver(true);
          setIsPlaying(false);
          const playTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
          onGameOver(gameScore, playTime);
          return;
        }
      });

      // Draw score
      ctx.fillStyle = '#fff';
      ctx.font = '20px monospace';
      ctx.fillText(`Score: ${gameScore}`, 10, 30);
      ctx.fillText(`Dots: ${dots.filter((d) => !d.collected).length}`, 10, 60);

      // Check win condition
      if (dots.every((d) => d.collected)) {
        setGameOver(true);
        setIsPlaying(false);
        const playTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
        onGameOver(gameScore + 500, playTime); // Bonus for completing
        return;
      }

      if (isPlaying) {
        requestAnimationFrame(gameLoop);
      }
    };

    gameLoop();

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isPlaying, onGameOver]);

  const startGame = () => {
    setScore(0);
    setGameOver(false);
    setIsPlaying(true);
    startTimeRef.current = Date.now();
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        className="border-2 border-gray-700 rounded-lg bg-gray-900"
      />

      {!isPlaying && !gameOver && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={startGame}
          className="px-6 py-3 bg-yellow-600 text-white rounded-lg font-semibold"
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
          <h3 className="text-2xl font-bold text-yellow-500 mb-2">
            {score >= 500 ? 'You Win! 🎉' : 'Game Over!'}
          </h3>
          <p className="text-lg text-gray-300 mb-4">Final Score: {score}</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={startGame}
            className="px-6 py-3 bg-yellow-600 text-white rounded-lg font-semibold"
          >
            Play Again
          </motion.button>
        </motion.div>
      )}

      <p className="text-sm text-gray-400">Use arrow keys or WASD to move</p>
    </div>
  );
}
