import { motion } from "framer-motion";
import { X, Target, Calendar, Clock } from "lucide-react";
import { useState } from "react";
import { Button } from "./ui/button-enhanced";

interface GoalSettingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (goal: {
    type: "weekly" | "monthly" | "yearly";
    targetHours: number;
  }) => void;
  currentGoal?: {
    type: "weekly" | "monthly" | "yearly";
    targetHours: number;
  };
}

export function GoalSettingModal({
  isOpen,
  onClose,
  onSave,
  currentGoal,
}: GoalSettingModalProps) {
  const [goalType, setGoalType] = useState<"weekly" | "monthly" | "yearly">(
    currentGoal?.type || "weekly"
  );
  const [targetHours, setTargetHours] = useState(
    currentGoal?.targetHours || 30
  );

  if (!isOpen) return null;

  const handleSave = () => {
    onSave({ type: goalType, targetHours });
    onClose();
  };

  const presets = {
    weekly: [20, 30, 40, 50],
    monthly: [80, 120, 160, 200],
    yearly: [500, 1000, 1500, 2000],
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-md bg-card border border-border rounded-xl shadow-lg p-6 m-4"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Target className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-bold">목표 설정</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-accent transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Goal Type Selection */}
        <div className="space-y-4 mb-6">
          <label className="text-sm font-medium">목표 기간</label>
          <div className="grid grid-cols-3 gap-2">
            {(["weekly", "monthly", "yearly"] as const).map((type) => (
              <button
                key={type}
                onClick={() => {
                  setGoalType(type);
                  setTargetHours(presets[type][1]); // Set default preset
                }}
                className={`p-3 rounded-lg border transition-all ${
                  goalType === type
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-background border-border hover:bg-accent"
                }`}
              >
                <div className="flex flex-col items-center gap-1">
                  {type === "weekly" && <Calendar className="h-4 w-4" />}
                  {type === "monthly" && <Calendar className="h-4 w-4" />}
                  {type === "yearly" && <Clock className="h-4 w-4" />}
                  <span className="text-xs font-medium">
                    {type === "weekly" && "주간"}
                    {type === "monthly" && "월간"}
                    {type === "yearly" && "연간"}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Target Hours Input */}
        <div className="space-y-4 mb-6">
          <label className="text-sm font-medium">목표 시간</label>
          <div className="flex items-center gap-4">
            <input
              type="number"
              value={targetHours}
              onChange={(e) => setTargetHours(Number(e.target.value))}
              className="flex-1 px-4 py-2 bg-input-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              min="1"
              max="10000"
            />
            <span className="text-sm text-muted-foreground">시간</span>
          </div>

          {/* Presets */}
          <div className="flex flex-wrap gap-2">
            {presets[goalType].map((preset) => (
              <button
                key={preset}
                onClick={() => setTargetHours(preset)}
                className={`px-3 py-1 text-sm rounded-md border transition-colors ${
                  targetHours === preset
                    ? "bg-primary/10 text-primary border-primary/50"
                    : "bg-background border-border hover:bg-accent"
                }`}
              >
                {preset}시간
              </button>
            ))}
          </div>
        </div>

        {/* Preview */}
        <div className="mb-6 p-4 rounded-lg bg-muted/50 border border-border">
          <p className="text-sm text-muted-foreground mb-1">목표 미리보기</p>
          <p className="text-lg font-semibold">
            {goalType === "weekly" && "주간"}{goalType === "monthly" && "월간"}{goalType === "yearly" && "연간"}{" "}
            <span className="text-primary">{targetHours}시간</span> 집중하기
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            {goalType === "weekly" && `하루 평균 ${(targetHours / 7).toFixed(1)}시간`}
            {goalType === "monthly" && `하루 평균 ${(targetHours / 30).toFixed(1)}시간`}
            {goalType === "yearly" && `한 달 평균 ${(targetHours / 12).toFixed(1)}시간`}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            size="md"
            onClick={onClose}
            className="flex-1"
          >
            취소
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={handleSave}
            className="flex-1"
          >
            저장
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
