# Focus Mate 프론트엔드 기능 구현 문서

## 📋 목차
1. [개요](#개요)
2. [UI/UX 프리미엄 개선](#uiux-프리미엄-개선)
3. [데이터 시각화](#데이터-시각화)
4. [인터랙티브 기능](#인터랙티브-기능)
5. [고급 차트](#고급-차트)
6. [프리미엄 기능](#프리미엄-기능)
7. [기술 스택](#기술-스택)
8. [컴포넌트 구조](#컴포넌트-구조)

---

## 개요

Focus Mate는 포모도로 기반 집중 관리 애플리케이션으로, Linear, Notion, Figma 등 대기업 제품에서 영감을 받은 프리미엄 UI/UX를 제공합니다.

### 주요 특징
- 🎨 **프리미엄 디자인**: Framer Motion 기반 부드러운 애니메이션
- 📊 **데이터 시각화**: Recharts 기반 인터랙티브 차트
- ⚡ **빠른 액션**: Linear 스타일 커맨드 팔레트 (⌘K)
- 🎯 **목표 관리**: 커스텀 목표 설정 및 진행률 추적
- 🎉 **축하 시스템**: 성취 시 confetti 애니메이션
- 📱 **소셜 공유**: 아름다운 공유 카드 생성

---

## UI/UX 프리미엄 개선

### 1. 애니메이션 시스템

#### PageTransition 컴포넌트
**파일**: `src/components/PageTransition.tsx`

```typescript
// 페이지 전환 애니메이션
<PageTransition className="space-y-6">
  {/* 페이지 콘텐츠 */}
</PageTransition>
```

**기능**:
- 페이지 진입/퇴장 애니메이션
- Stagger 애니메이션 (순차 등장)
- 부드러운 fade-in/slide-up 효과

#### Button Enhanced
**파일**: `src/components/ui/button-enhanced.tsx`

**기능**:
- Hover/Tap 애니메이션 (scale, shadow)
- 로딩 상태 (스피너)
- 5가지 변형 (primary, outline, ghost, destructive, link)
- 3가지 크기 (sm, md, lg)

---

### 2. Command Palette

**파일**: `src/components/CommandPalette.tsx`

**기능**:
- **키보드 단축키**: `⌘K` (Mac) / `Ctrl+K` (Windows)
- 빠른 네비게이션 (대시보드, 통계, 로그아웃)
- 검색 기능
- ESC로 닫기

**사용법**:
```typescript
// __root.tsx에 통합
<CommandPalette />
```

---

### 3. Empty State

**파일**: `src/components/EmptyState.tsx`

**기능**:
- 데이터 없을 때 표시
- 애니메이션 아이콘
- 액션 버튼 (선택사항)

---

## 데이터 시각화

### 1. FocusTimeChart (Area Chart)

**파일**: `src/components/charts/FocusTimeChart.tsx`

**기능**:
- 주간 집중 시간 추이
- 그라데이션 fill
- 커스텀 툴팁 (시간 + 세션 수)
- 부드러운 애니메이션

**데이터 형식**:
```typescript
{
  date: string;    // "1/6"
  hours: number;   // 2.5
  sessions: number; // 5
}[]
```

---

### 2. WeeklyActivityChart (Bar Chart)

**파일**: `src/components/charts/WeeklyActivityChart.tsx`

**기능**:
- 요일별 집중 시간
- Hover 시 색상 변화 (인터랙티브)
- 둥근 모서리 (radius: 8px)
- 커스텀 툴팁

**데이터 형식**:
```typescript
{
  day: string;     // "월"
  hours: number;   // 3.2
  sessions: number; // 6
}[]
```

---

### 3. SessionDistributionChart (Donut Chart)

**파일**: `src/components/charts/SessionDistributionChart.tsx`

**기능**:
- 세션 유형별 분포
- 도넛 차트 (innerRadius: 60, outerRadius: 90)
- 우측 범례 (개수 + 퍼센트)
- 4가지 색상 (chart-1 ~ chart-4)

**데이터 형식**:
```typescript
{
  name: string;  // "포모도로 (25분)"
  value: number; // 45
  color: string; // "hsl(var(--chart-1))"
}[]
```

---

### 4. ActivityHeatMap (GitHub-style)

**파일**: `src/components/charts/ActivityHeatMap.tsx`

**기능**:
- 12주간 일일 활동
- 5단계 색상 강도
- Hover 툴팁 (날짜, 시간, 강도)
- Scale 애니메이션 (1.2배)

**색상 범례**:
- 0시간: `bg-muted`
- 0-2시간: `bg-primary/20`
- 2-4시간: `bg-primary/40`
- 4-6시간: `bg-primary/60`
- 6시간+: `bg-primary`

---

## 인터랙티브 기능

### 1. DateRangePicker

**파일**: `src/components/DateRangePicker.tsx`

**기능**:
- 달력 UI (2개월 동시 표시)
- 한국어 로케일
- Popover로 깔끔한 UI
- date-fns 포맷팅

**사용법**:
```typescript
<DateRangePicker
  dateRange={dateRange}
  onDateRangeChange={(range) => setDateRange(range)}
/>
```

---

### 2. ChartFilters

**파일**: `src/components/ChartFilters.tsx`

**기능**:
- 세션 유형 필터 (전체/포모도로/단기/장기/휴식)
- 날짜 범위 필터
- 활성 필터 개수 표시
- 필터 초기화 버튼
- 접기/펼치기 애니메이션

**사용법**:
```typescript
<ChartFilters onFilterChange={(filters) => {
  // filters.sessionType: string[]
  // filters.dateRange: DateRange | undefined
}} />
```

---

## 고급 차트

### 1. HourlyPatternChart (Radar Chart)

**파일**: `src/components/charts/HourlyPatternChart.tsx`

**기능**:
- 24시간 시간대별 집중 패턴
- 평균 집중 시간 표시
- 커스텀 툴팁
- Primary 색상 그라데이션

**데이터 형식**:
```typescript
{
  hour: string;      // "0" ~ "23"
  sessions: number;  // 5
  avgDuration: number; // 25 (분)
}[]
```

---

### 2. MonthlyComparisonChart (Line Chart)

**파일**: `src/components/charts/MonthlyComparisonChart.tsx`

**기능**:
- 올해 vs 작년 비교
- 2개 라인 (실선 + 점선)
- 범례 표시
- **Brush 컴포넌트** (확대/축소)

**데이터 형식**:
```typescript
{
  month: string;   // "1월"
  thisYear: number; // 45
  lastYear: number; // 38
}[]
```

---

### 3. GoalProgressRing (Progress Ring)

**파일**: `src/components/charts/GoalProgressRing.tsx`

**기능**:
- 원형 진행률 (0-100%)
- 중앙에 퍼센트 + 상세 정보
- 달성률에 따른 색상 변화:
  - 100%+: `chart-2` (Green)
  - 75-99%: `primary`
  - 50-74%: `chart-4` (Yellow)
  - 0-49%: `chart-5` (Orange)
- Spring 애니메이션

**사용법**:
```typescript
<GoalProgressRing
  current={23.4}
  goal={30}
  label="주간 목표"
  unit="시간"
/>
```

---

## 프리미엄 기능

### 1. DataExporter (CSV/PDF)

**파일**: `src/utils/dataExporter.ts`

#### CSV 내보내기
```typescript
DataExporter.exportToCSV({
  sessions: [...],
  stats: { totalFocusTime, totalSessions, averageSession }
});
```

**기능**:
- UTF-8 BOM 포함 (한글 지원)
- 세션 상세 + 요약 통계
- 자동 파일명 (날짜 포함)

#### PDF 내보내기
```typescript
DataExporter.exportToPDF({
  sessions: [...],
  stats: { totalFocusTime, totalSessions, averageSession }
});
```

**기능**:
- jsPDF + jspdf-autotable
- 프로페셔널 리포트 형식
- Primary 색상 헤더

---

### 2. CelebrationSystem (Confetti)

**파일**: `src/utils/celebrationSystem.ts`

#### 6가지 축하 효과

1. **celebrate()** - 기본 축하
```typescript
CelebrationSystem.celebrate();
```

2. **goalAchieved()** - 목표 달성 (3초 연속)
```typescript
CelebrationSystem.goalAchieved();
```

3. **streakAchieved()** - 연속 기록 (불꽃놀이)
```typescript
CelebrationSystem.streakAchieved();
```

4. **levelUp()** - 레벨업 (황금 별)
```typescript
CelebrationSystem.levelUp();
```

5. **firstSession()** - 첫 세션 (양쪽 발사)
```typescript
CelebrationSystem.firstSession();
```

6. **perfectWeek()** - 완벽한 한 주 (황금 비)
```typescript
CelebrationSystem.perfectWeek();
```

---

### 3. GoalSettingModal

**파일**: `src/components/GoalSettingModal.tsx`

**기능**:
- 3가지 목표 기간 (주간/월간/연간)
- 프리셋 버튼:
  - 주간: 20, 30, 40, 50시간
  - 월간: 80, 120, 160, 200시간
  - 연간: 500, 1000, 1500, 2000시간
- 커스텀 시간 입력
- 실시간 미리보기 (일일 평균 계산)

**사용법**:
```typescript
<GoalSettingModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  onSave={(goal) => {
    // goal.type: "weekly" | "monthly" | "yearly"
    // goal.targetHours: number
  }}
/>
```

---

### 4. StreakCalendar (GitHub-style)

**파일**: `src/components/StreakCalendar.tsx`

**기능**:
- 12주간 활동 히트맵
- 6단계 색상 강도
- Hover 툴팁 (날짜, 시간, 세션 수)
- 현재/최장 연속 기록 표시
- 스태거 애니메이션

**데이터 형식**:
```typescript
{
  date: string;    // "2025-01-06"
  hours: number;   // 2.5
  sessions: number; // 5
}[]
```

---

### 5. PomodoroWidget

**파일**: `src/components/PomodoroWidget.tsx`

**기능**:
- 원형 진행률 (SVG)
- 집중/휴식 모드 전환
- 자동 모드 전환 (세션 완료 시)
- 프리셋:
  - 집중: 15, 25, 50분
  - 휴식: 5, 10, 15분
- 재생/일시정지/초기화
- 세션 완료 콜백

**사용법**:
```typescript
<PomodoroWidget
  onSessionComplete={(duration, type) => {
    // duration: number (분)
    // type: "work" | "break"
  }}
/>
```

---

### 6. SharingCard

**파일**: `src/components/SharingCard.tsx`

**기능**:
- html2canvas로 이미지 생성
- 4가지 카드 타입:
  - **achievement**: 보라-핑크 그라데이션
  - **streak**: 주황-빨강 그라데이션
  - **weekly**: 파랑-청록 그라데이션
  - **monthly**: 초록-에메랄드 그라데이션
- 배경 패턴 (라디얼 + 선형)
- 다운로드 / Web Share API

**사용법**:
```typescript
<SharingModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  card={{
    type: "weekly",
    data: {
      title: "이번 주 집중 시간",
      value: "23.4시간",
      subtitle: "45개의 세션 완료",
      icon: <Clock className="h-12 w-12" />
    }
  }}
/>
```

---

## 기술 스택

### 핵심 라이브러리
- **React 18**: UI 프레임워크
- **TypeScript**: 타입 안정성
- **TanStack Router**: 라우팅
- **TanStack Query**: 데이터 페칭

### UI/UX
- **Framer Motion**: 애니메이션
- **cmdk**: 커맨드 팔레트
- **Lucide React**: 아이콘

### 데이터 시각화
- **Recharts**: 차트 라이브러리
- **canvas-confetti**: 축하 애니메이션

### 날짜/시간
- **date-fns**: 날짜 포맷팅
- **react-day-picker**: 달력 UI

### 내보내기
- **jsPDF**: PDF 생성
- **jspdf-autotable**: PDF 테이블
- **html2canvas**: HTML → 이미지

---

## 컴포넌트 구조

```
src/
├── components/
│   ├── ui/
│   │   ├── button-enhanced.tsx      # 향상된 버튼
│   │   ├── calendar.tsx             # 달력 UI
│   │   ├── command.tsx              # 커맨드 팔레트 UI
│   │   ├── popover.tsx              # 팝오버
│   │   └── skeleton.tsx             # 로딩 스켈레톤
│   ├── charts/
│   │   ├── FocusTimeChart.tsx       # Area 차트
│   │   ├── WeeklyActivityChart.tsx  # Bar 차트
│   │   ├── SessionDistributionChart.tsx # Donut 차트
│   │   ├── ActivityHeatMap.tsx      # 히트맵
│   │   ├── HourlyPatternChart.tsx   # Radar 차트
│   │   ├── MonthlyComparisonChart.tsx # Line 차트
│   │   └── GoalProgressRing.tsx     # Progress Ring
│   ├── CommandPalette.tsx           # 커맨드 팔레트
│   ├── PageTransition.tsx           # 페이지 전환
│   ├── EmptyState.tsx               # 빈 상태
│   ├── DateRangePicker.tsx          # 날짜 선택기
│   ├── ChartFilters.tsx             # 차트 필터
│   ├── GoalSettingModal.tsx         # 목표 설정 모달
│   ├── StreakCalendar.tsx           # 연속 기록 달력
│   ├── PomodoroWidget.tsx           # 포모도로 타이머
│   └── SharingCard.tsx              # 공유 카드
├── pages/
│   ├── Dashboard.tsx                # 대시보드 (프리미엄 기능 통합)
│   └── Stats.tsx                    # 통계 (고급 차트 통합)
└── utils/
    ├── dataExporter.ts              # CSV/PDF 내보내기
    ├── celebrationSystem.ts         # 축하 애니메이션
    └── stats-calculator.ts          # 통계 계산
```

---

## 페이지별 기능

### Dashboard (`/`)

**주요 기능**:
1. 통계 카드 4개 (오늘 집중 시간, 완료 세션, 연속 기록, 주간 평균)
2. 주간 집중 시간 차트 (Area)
3. 세션 분포 차트 (Donut)
4. 연속 기록 달력 (GitHub 스타일)
5. 포모도로 타이머 (통합)
6. 액션 버튼 (목표 설정, 공유, CSV/PDF 내보내기)

**레이아웃**:
- 3열 그리드 (lg:grid-cols-3)
- 왼쪽 2열: 차트 + 달력
- 오른쪽 1열: 포모도로 타이머

---

### Stats (`/stats`)

**주요 기능**:
1. 필터 (세션 유형, 날짜 범위)
2. 통계 카드 3개
3. 목표 진행률 3개 (주간/월간/연간)
4. 주간 활동 차트 (Bar)
5. 시간대별 집중 패턴 (Radar)
6. 월별 비교 (Line with Zoom)
7. 활동 히트맵 (12주)
8. 업적 시스템

**레이아웃**:
- 반응형 그리드
- 필터 상단 고정
- 차트 2열 그리드 (lg:grid-cols-2)

---

## 색상 시스템

### CSS 변수
```css
--primary: 주요 색상
--secondary: 보조 색상
--muted: 비활성 색상
--accent: 강조 색상
--destructive: 경고 색상

--chart-1: 차트 색상 1
--chart-2: 차트 색상 2 (Green)
--chart-3: 차트 색상 3
--chart-4: 차트 색상 4 (Yellow)
--chart-5: 차트 색상 5 (Orange)
```

### 다크모드 지원
- 모든 컴포넌트 자동 지원
- CSS 변수 기반
- 부드러운 전환

---

## 애니메이션 가이드

### Framer Motion 패턴

#### 페이지 전환
```typescript
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.4 }}
```

#### Stagger 애니메이션
```typescript
variants={staggerContainer}
initial="initial"
animate="animate"
```

#### Hover 효과
```typescript
whileHover={{ scale: 1.02, y: -2 }}
```

---

## 성능 최적화

### 1. useMemo 활용
- 차트 데이터 변환 캐싱
- 통계 계산 최적화

### 2. 조건부 렌더링
- 데이터 없을 때 빈 상태 표시
- 로딩 스켈레톤

### 3. 애니메이션 최적화
- GPU 가속 (transform, opacity)
- will-change 속성

---

## 접근성

### 키보드 네비게이션
- 커맨드 팔레트 (`⌘K`)
- Tab 네비게이션
- ESC로 모달 닫기

### ARIA 속성
- Recharts 자동 생성
- 버튼 레이블
- 툴팁 설명

---

## 브라우저 지원

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 향후 개선 사항

1. **음악 플레이어**: Spotify API 통합
2. **팀 기능**: 리더보드, 공동 목표
3. **주간 리포트**: 이메일 자동 발송
4. **브라우저 확장**: Chrome/Firefox 확장 프로그램
5. **모바일 앱**: React Native

---

## 문의 및 지원

기능 관련 문의나 버그 리포트는 GitHub Issues를 이용해주세요.

**마지막 업데이트**: 2025-01-12
