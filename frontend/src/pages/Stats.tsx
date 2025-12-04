import React from "react";
import { StatsChart } from "../components/stats-chart";
import { SessionHistory } from "../components/session-history";
import { TrendingUp } from "lucide-react";

export function StatsPage() {
  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-primary-foreground" />
            </div>
            <h1>통계 및 히스토리</h1>
          </div>
          <p className="text-muted-foreground">
            집중 시간 분석 및 세션 기록을 확인하세요
          </p>
        </div>

        {/* Content */}
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="lg:col-span-2">
            <StatsChart />
          </div>
          <div className="lg:col-span-2">
            <SessionHistory />
          </div>
        </div>
      </div>
    </div>
  );
}
