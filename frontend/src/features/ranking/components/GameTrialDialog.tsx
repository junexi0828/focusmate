import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Gamepad2, Zap, Target, Activity } from "lucide-react";

interface GameTrialDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectGame: (gameType: string) => void;
}

const GAMES = [
  {
    id: "dino_jump",
    name: "공룡 점프",
    description: "장애물을 피하며 점프하는 게임",
    icon: Zap,
    color: "text-yellow-500",
  },
  {
    id: "dot_collector",
    name: "점 수집",
    description: "점을 모으는 게임",
    icon: Target,
    color: "text-blue-500",
  },
  {
    id: "snake",
    name: "스네이크",
    description: "전통적인 스네이크 게임",
    icon: Activity,
    color: "text-green-500",
  },
];

export function GameTrialDialog({
  open,
  onOpenChange,
  onSelectGame,
}: GameTrialDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Gamepad2 className="w-5 h-5" />
            게임 선택
          </DialogTitle>
          <DialogDescription>
            체험할 게임을 선택하세요. 체험하기 모드에서는 점수가 저장되지 않습니다.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 md:grid-cols-3 mt-4">
          {GAMES.map((game) => {
            const Icon = game.icon;
            return (
              <Card
                key={game.id}
                className="cursor-pointer hover:border-primary transition-colors"
                onClick={() => {
                  onSelectGame(game.id);
                  onOpenChange(false);
                }}
              >
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-6 h-6 ${game.color}`} />
                    <CardTitle className="text-lg">{game.name}</CardTitle>
                  </div>
                  <CardDescription>{game.description}</CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </DialogContent>
    </Dialog>
  );
}

