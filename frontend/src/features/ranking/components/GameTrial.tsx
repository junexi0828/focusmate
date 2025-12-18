import React, { useState, useEffect, useRef } from "react";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { X, RotateCcw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface GameTrialProps {
  gameType: string;
  onClose: () => void;
}

export function GameTrial({ gameType, onClose }: GameTrialProps) {
  const [score, setScore] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const gameRef = useRef<HTMLDivElement>(null);

  const getGameName = () => {
    const names: Record<string, string> = {
      dino_jump: "공룡 점프",
      dot_collector: "점 수집",
      snake: "스네이크",
    };
    return names[gameType] || "게임";
  };

  const handleStart = () => {
    setIsPlaying(true);
    setGameOver(false);
    setScore(0);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setGameOver(false);
    setScore(0);
  };

  const handleGameOver = () => {
    setIsPlaying(false);
    setGameOver(true);
  };

  // 간단한 게임 로직 (클라이언트 사이드만)
  useEffect(() => {
    if (!isPlaying || gameOver) return;

    const interval = setInterval(() => {
      setScore((prev) => {
        const newScore = prev + 1;
        // 게임 종료 조건 (예: 100점 도달)
        if (newScore >= 100) {
          handleGameOver();
          return prev;
        }
        return newScore;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, gameOver]);

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="w-full max-w-2xl"
      >
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{getGameName()} - 체험하기</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 게임 영역 */}
              <div
                ref={gameRef}
                className="w-full h-96 bg-muted rounded-lg flex items-center justify-center relative overflow-hidden"
              >
                {!isPlaying && !gameOver && (
                  <div className="text-center space-y-4">
                    <p className="text-muted-foreground">
                      게임을 시작하려면 시작 버튼을 클릭하세요
                    </p>
                    <Button onClick={handleStart} size="lg">
                      게임 시작
                    </Button>
                  </div>
                )}

                {isPlaying && (
                  <div className="text-center space-y-4">
                    <div className="text-4xl font-bold">{score}</div>
                    <p className="text-muted-foreground">점수</p>
                    <div className="mt-8">
                      <p className="text-sm text-muted-foreground">
                        {gameType === "dino_jump" && "스페이스바를 눌러 점프하세요"}
                        {gameType === "dot_collector" && "점을 클릭하여 수집하세요"}
                        {gameType === "snake" && "방향키로 이동하세요"}
                      </p>
                    </div>
                  </div>
                )}

                {gameOver && (
                  <div className="text-center space-y-4">
                    <div className="text-4xl font-bold text-primary">{score}</div>
                    <p className="text-lg">최종 점수</p>
                    <p className="text-sm text-muted-foreground">
                      체험하기 모드에서는 점수가 저장되지 않습니다
                    </p>
                    <div className="flex gap-2 justify-center">
                      <Button onClick={handleReset} variant="outline">
                        <RotateCcw className="w-4 h-4 mr-2" />
                        다시하기
                      </Button>
                      <Button onClick={onClose}>닫기</Button>
                    </div>
                  </div>
                )}
              </div>

              {/* 게임 정보 */}
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>게임 타입: {getGameName()}</span>
                {isPlaying && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setIsPlaying(false);
                      setGameOver(true);
                    }}
                  >
                    종료
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

