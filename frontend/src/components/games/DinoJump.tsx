/**
 * Dino Jump Game - Chrome dinosaur style
 */
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface DinoJumpProps {
  onGameOver: (score: number, time: number) => void;
}

export function DinoJump({ onGameOver }: DinoJumpProps) {
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
    let dino = {
      x: 50,
      y: height - 60,
      width: 40,
      height: 40,
      velocityY: 0,
      jumping: false,
    };

    let obstacles: Array<{ x: number; width: number; height: number }> = [];
    let gameScore = 0;
    let gameSpeed = 5;
    let obstacleTimer = 0;

    // Jump
    const jump = () => {
      if (!dino.jumping) {
        dino.velocityY = -15;
        dino.jumping = true;
      }
    };

    // Handle keyboard
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault();
        jump();
      }
    };

    // Handle click/touch
    const handleClick = () => jump();

    window.addEventListener('keydown', handleKeyPress);
    canvas.addEventListener('click', handleClick);

    // Game loop
    const gameLoop = () => {
      // Clear canvas
      ctx.fillStyle = '#1a1a1a';
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
      ctx.fillStyle = '#10b981';
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
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(obs.x, height - obs.height, obs.width, obs.height);

        // Check collision
        if (
          dino.x < obs.x + obs.width &&
          dino.x + dino.width > obs.x &&
          dino.y + dino.height > height - obs.height
        ) {
          setGameOver(true);
          setIsPlaying(false);
          const playTime = Math.floor((Date.now() - startTimeRef.current) / 1000);
          onGameOver(gameScore, playTime);
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
      ctx.fillStyle = '#4b5563';
      ctx.fillRect(0, height - 10, width, 10);

      // Draw score
      ctx.fillStyle = '#fff';
      ctx.font = '20px monospace';
      ctx.fillText(`Score: ${gameScore}`, 10, 30);

      // Increase difficulty
      if (gameScore > 0 && gameScore % 100 === 0) {
        gameSpeed += 0.5;
      }

      if (isPlaying) {
        requestAnimationFrame(gameLoop);
      }
    };

    gameLoop();

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
      canvas.removeEventListener('click', handleClick);
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
        height={400}
        className="border-2 border-gray-700 rounded-lg bg-gray-900"
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

      <p className="text-sm text-gray-400">Press SPACE or click to jump</p>
    </div>
  );
}
