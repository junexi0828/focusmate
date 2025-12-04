import React from "react";
import { Timer } from "lucide-react";
import { CreateRoomCard } from "../features/room/components/CreateRoomCard";
import { JoinRoomCard } from "../features/room/components/JoinRoomCard";

interface HomePageProps {
  onCreateRoom: (
    roomName: string,
    focusTime: number,
    breakTime: number
  ) => void;
  onJoinRoom: (roomId: string) => void;
}

export function HomePage({ onCreateRoom, onJoinRoom }: HomePageProps) {
  return (
    <div
      /*
        전체 레이아웃 설정
        - p-4: 전체 패딩 (변경: p-2, p-6, p-8 등)
        - bg-muted/30: 배경색 투명도 (변경: bg-muted, bg-background 등)
      */
      className="min-h-screen flex flex-col items-center justify-center p-4 bg-muted/30"
    >
      {/*
        컨테이너 최대 너비 설정
        - max-w-6xl: 최대 너비 (변경: max-w-4xl, max-w-5xl, max-w-7xl 등)
      */}
      <div className="w-full max-w-6xl mx-auto">
        {/* Header */}
        {/*
          헤더 섹션 간격 설정
          - mb-12: 하단 여백 (변경: mb-8, mb-16 등)
        */}
        <div className="text-center mb-12">
          {/*
            로고 및 제목 영역
            - gap-3: 로고와 제목 사이 간격 (변경: gap-2, gap-4 등)
            - mb-4: 하단 여백 (변경: mb-2, mb-6 등)
          */}
          <div className="flex items-center justify-center gap-3 mb-4">
            {/*
              로고 아이콘 컨테이너
              - w-12 h-12: 로고 원 크기 (변경: w-10 h-10, w-14 h-14, w-16 h-16 등)
            */}
            <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
              {/*
                로고 아이콘 크기
                - w-7 h-7: 아이콘 크기 (변경: w-5 h-5, w-6 h-6, w-8 h-8 등)
              */}
              <Timer className="w-7 h-7 text-primary-foreground" />
            </div>
            {/*
              메인 제목 크기
              - text-4xl: 제목 크기 (변경: text-3xl, text-5xl, text-6xl 등)
            */}
            <h1 className="text-4xl">Focus Mate</h1>
          </div>
          {/*
            설명 텍스트 설정
            - max-w-2xl: 최대 너비 (변경: max-w-xl, max-w-3xl 등)
            - text-muted-foreground: 텍스트 색상 (변경: text-foreground, text-muted 등)
          */}
          <p className="text-muted-foreground max-w-2xl mx-auto">
            팀과 함께 집중력을 향상시키는 실시간 협업 포모도로 타이머
          </p>
        </div>

        {/* Cards */}
        {/*
          카드 그리드 레이아웃 설정
          - md:grid-cols-2: 중간 화면 이상에서 2열 (변경: sm:grid-cols-2, lg:grid-cols-2 등)
          - gap-8: 카드 간 간격 (변경: gap-4, gap-6, gap-12 등)
          - mb-16: 하단 여백 (변경: mb-8, mb-12, mb-20 등)
        */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <CreateRoomCard onCreateRoom={onCreateRoom} />
          <JoinRoomCard onJoinRoom={onJoinRoom} />
        </div>

        {/* How It Works Section */}
        {/*
          "사용 방법" 섹션 상단 여백
          - mt-16: 상단 여백 (변경: mt-8, mt-12, mt-20 등)
        */}
        <div className="mt-16">
          {/*
            섹션 제목 설정
            - text-3xl: 제목 크기 (변경: text-2xl, text-4xl 등)
            - mb-12: 하단 여백 (변경: mb-8, mb-16 등)
          */}
          <h2 className="text-3xl font-bold text-center mb-12">사용 방법</h2>

          {/*
            단계 그리드 레이아웃 설정
            - grid-cols-3: 기본 3열 (변경: grid-cols-1, grid-cols-2 등)
            - gap-4: 작은 화면 간격 (변경: gap-2, gap-6 등)
            - sm:gap-8: 큰 화면 간격 (변경: sm:gap-6, sm:gap-12 등)
          */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-8">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center">
              <div
                className="w-16 h-16 min-w-16 min-h-16 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mb-4"
                style={{ aspectRatio: "1 / 1" }}
              >
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h3 className="text-xl font-bold mb-3">
                방 만들기 또는 참여하기
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                새로운 방을 만들거나 팀원과 함께 기존 방에 참여하세요
              </p>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center text-center">
              <div
                className="w-16 h-16 min-w-16 min-h-16 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mb-4"
                style={{ aspectRatio: "1 / 1" }}
              >
                <span className="text-2xl font-bold text-primary">2</span>
              </div>
              <h3 className="text-xl font-bold mb-3">함께 집중하기</h3>
              <p className="text-muted-foreground leading-relaxed">
                모든 사람이 동일한 타이머를 보고 동기화된 상태를 유지합니다
              </p>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col items-center text-center">
              <div
                className="w-16 h-16 min-w-16 min-h-16 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mb-4"
                style={{ aspectRatio: "1 / 1" }}
              >
                <span className="text-2xl font-bold text-primary">3</span>
              </div>
              <h3 className="text-xl font-bold mb-3">함께 휴식하기</h3>
              <p className="text-muted-foreground leading-relaxed">
                동기화된 휴식을 취하며 생산성을 높이세요
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
