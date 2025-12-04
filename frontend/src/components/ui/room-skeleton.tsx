/**
 * Room 페이지용 스켈레톤 UI 컴포넌트
 */

import { Skeleton } from "./skeleton";
import { Card, CardContent, CardHeader } from "./card";

export function RoomPageSkeleton() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header Skeleton */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 min-w-0">
              <Skeleton className="h-8 w-48 mb-2" />
              <Skeleton className="h-4 w-32" />
            </div>
            <div className="flex items-center gap-2">
              <Skeleton className="h-10 w-24" />
              <Skeleton className="h-10 w-20" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Skeleton */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[1fr_350px] gap-8">
          {/* Timer Section Skeleton */}
          <div className="flex flex-col items-center justify-center gap-8">
            {/* Session Type Badge */}
            <Skeleton className="h-10 w-32 rounded-full" />

            {/* Timer Circle */}
            <div className="relative w-80 h-80 flex items-center justify-center">
              <Skeleton className="w-full h-full rounded-full" />
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <Skeleton className="h-20 w-32 mb-2" />
                <Skeleton className="h-4 w-16" />
              </div>
            </div>

            {/* Timer Controls */}
            <div className="flex gap-4">
              <Skeleton className="h-12 w-36" />
              <Skeleton className="h-12 w-36" />
            </div>
          </div>

          {/* Participant List Skeleton */}
          <div className="lg:block hidden">
            <ParticipantListSkeleton />
          </div>
        </div>

        {/* Mobile Participant List Skeleton */}
        <div className="lg:hidden mt-8">
          <ParticipantListSkeleton />
        </div>
      </main>
    </div>
  );
}

export function ParticipantListSkeleton() {
  return (
    <Card className="w-full h-full">
      <CardHeader>
        <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"
            >
              <Skeleton className="w-10 h-10 rounded-full" />
              <div className="flex-1 min-w-0 space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-16" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

