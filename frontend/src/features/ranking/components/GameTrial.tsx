import React, { useState, useRef, useEffect } from "react";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { X } from "lucide-react";
import { motion } from "framer-motion";
import { DinoJump } from "../../../components/games/DinoJump";
import { DotCollector } from "../../../components/games/DotCollector";
import { SnakeGame } from "../../../components/games/SnakeGame";

interface GameTrialProps {
  gameType: string;
  onClose: () => void;
}

export function GameTrial({ gameType, onClose }: GameTrialProps) {
  const gameContainerRef = useRef<HTMLDivElement>(null);

  const getGameName = () => {
    const names: Record<string, string> = {
      dino_jump: "공룡 점프",
      dot_collector: "점 수집",
      snake: "스네이크",
    };
    return names[gameType] || "게임";
  };

  // 체험하기 모드에서는 점수를 저장하지 않음
  const handleGameOver = (score: number, time: number) => {
    console.log("체험하기 모드 - 점수:", score, "시간:", time);
    // 점수 저장하지 않음
  };

  // 모달이 열릴 때 게임 컨테이너에 포커스를 주어 키보드 이벤트가 작동하도록 함
  useEffect(() => {
    if (gameContainerRef.current) {
      gameContainerRef.current.focus();
    }
  }, []);

  const renderGame = () => {
    switch (gameType) {
      case "dino_jump":
        return <DinoJump onGameOver={handleGameOver} />;
      case "dot_collector":
        return <DotCollector onGameOver={handleGameOver} />;
      case "snake":
        return <SnakeGame onGameOver={handleGameOver} />;
      default:
        return <div className="text-center text-muted-foreground">게임을 찾을 수 없습니다</div>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="w-full max-w-4xl"
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
              {/* 실제 게임 렌더링 - 키보드 이벤트를 받을 수 있도록 tabIndex 추가 */}
              <div
                ref={gameContainerRef}
                tabIndex={-1}
                className="w-full flex justify-center overflow-auto outline-none"
                onKeyDown={(e) => {
                  // ESC 키로 모달 닫기
                  if (e.key === "Escape") {
                    onClose();
                  }
                }}
              >
                <div className="w-full max-w-full">
                  {renderGame()}
                </div>
              </div>

              {/* 게임 정보 */}
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>게임 타입: {getGameName()}</span>
                <span className="text-xs">체험하기 모드에서는 점수가 저장되지 않습니다</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

