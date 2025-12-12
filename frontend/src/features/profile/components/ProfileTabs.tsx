import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../../components/ui/tabs";
import { User, Activity, BarChart3, Award, Settings } from "lucide-react";

interface ProfileTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  children: React.ReactNode;
}

export function ProfileTabs({
  activeTab,
  onTabChange,
  children,
}: ProfileTabsProps) {
  return (
    <Tabs value={activeTab} onValueChange={onTabChange} className="w-full">
      <div className="bg-background border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 max-w-5xl">
          <TabsList className="w-full justify-start bg-transparent h-auto p-0">
            <TabsTrigger
              value="overview"
              className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              <User className="w-4 h-4" />
              개요
            </TabsTrigger>
            <TabsTrigger
              value="activity"
              className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              <Activity className="w-4 h-4" />
              활동
            </TabsTrigger>
            <TabsTrigger
              value="stats"
              className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              <BarChart3 className="w-4 h-4" />
              통계
            </TabsTrigger>
            <TabsTrigger
              value="achievements"
              className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              <Award className="w-4 h-4" />
              업적
            </TabsTrigger>
            <TabsTrigger
              value="settings"
              className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
            >
              <Settings className="w-4 h-4" />
              설정
            </TabsTrigger>
          </TabsList>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-5xl">
        {children}
      </div>
    </Tabs>
  );
}

