import React from "react";
import { Tabs, TabsList, TabsTrigger } from "../../../components/ui/tabs";
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
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
        <TabsList className="w-full justify-start bg-transparent h-auto p-0">
          <TabsTrigger
            value="overview"
            className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-4 py-3"
          >
            <User className="w-4 h-4" />
            개요
          </TabsTrigger>
          <TabsTrigger
            value="activity"
            className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-4 py-3"
          >
            <Activity className="w-4 h-4" />
            활동
          </TabsTrigger>
          <TabsTrigger
            value="stats"
            className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-4 py-3"
          >
            <BarChart3 className="w-4 h-4" />
            통계
          </TabsTrigger>
          <TabsTrigger
            value="achievements"
            className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-4 py-3"
          >
            <Award className="w-4 h-4" />
            업적
          </TabsTrigger>
          <TabsTrigger
            value="settings"
            className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-4 py-3"
          >
            <Settings className="w-4 h-4" />
            설정
          </TabsTrigger>
        </TabsList>
      </div>

      <div className="py-6">
        {children}
      </div>
    </Tabs>
  );
}

