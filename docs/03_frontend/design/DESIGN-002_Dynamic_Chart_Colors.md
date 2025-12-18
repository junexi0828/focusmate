# 🎨 동적 차트 색상 시스템 완성

> **완료 시간**: 2025-12-18 03:30
> **상태**: ✅ **동적 색상 시스템 적용 완료**

---

## 🔄 하드코딩 vs 동적 색상

### ❌ 이전 (하드코딩)
```typescript
// 고정된 색상
const color = "hsl(var(--primary))";
```

### ✅ 현재 (동적)
```typescript
// 수치에 따라 변하는 색상
import { getProgressColor, getIntensityColor } from '@/utils/chart-colors';

const color = getProgressColor(percentage); // 0-100%에 따라 변함
const heatColor = getIntensityColor(hours); // 시간에 따라 변함
```

---

## 📊 동적 색상 함수

### 1. 진행도 색상 (`getProgressColor`)

**용도**: 목표 달성률, 완료율

**색상 변화**:
- 0-30%: 🔴 빨강 `hsl(0, 70%, 75%)` - 위험
- 31-70%: 🟡 노랑 `hsl(45, 85%, 75%)` - 주의
- 71-99%: 🟠 주황 `hsl(25, 80%, 72%)` - 양호
- 100%: 🟢 초록 `hsl(142, 65%, 70%)` - 완료

**사용 예시**:
```typescript
// 목표 진행도 링
const ringColor = getProgressColor(75); // 주황 (양호)

// 배지 색상
const badgeColor = getProgressColor(100); // 초록 (완료)
```

---

### 2. 활동 강도 색상 (`getIntensityColor`)

**용도**: 히트맵, 활동 시간 표시

**색상 변화**:
- 0시간: ⚪ 회색 `hsl(0, 0%, 95%)` - 활동 없음
- 0-1시간: 🔵 매우 연한 파랑 `hsl(210, 70%, 90%)`
- 1-2시간: 🔵 연한 파랑 `hsl(210, 70%, 80%)`
- 2-4시간: 🟠 주황 `hsl(25, 80%, 75%)`
- 4-6시간: 🟢 초록 `hsl(142, 65%, 70%)`
- 6시간+: 🟢 진한 초록 `hsl(142, 70%, 60%)`

**사용 예시**:
```typescript
// 히트맵 셀 색상
<div style={{ backgroundColor: getIntensityColor(dayData.hours) }} />

// 범례
{[0, 1, 3, 5, 7].map(h => (
  <div style={{ backgroundColor: getIntensityColor(h) }} />
))}
```

---

### 3. 트렌드 색상 (`getTrendColor`)

**용도**: 증감 표시, 비교

**색상 변화**:
- 감소: 🔴 빨강 `hsl(0, 70%, 75%)`
- 중립: 🔵 파랑 `hsl(210, 70%, 75%)`
- 증가: 🟢 초록 `hsl(142, 65%, 70%)`

**사용 예시**:
```typescript
// 통계 카드 트렌드
const trendColor = getTrendColor(currentValue, previousValue);

// 변화율 표시
const changeColor = getTrendColorGradient(changePercentage);
```

---

### 4. 그라디언트 색상 (부드러운 전환)

**진행도 그라디언트** (`getProgressColorGradient`):
```typescript
// 0-100% 사이 모든 값에 대해 부드러운 색상 전환
const color = getProgressColorGradient(percentage);

// 예시:
// 0%  → hsl(0, 75%, 75%)    빨강
// 15% → hsl(22, 75%, 75%)   주황빛 빨강
// 30% → hsl(45, 75%, 75%)   노랑
// 50% → hsl(35, 78%, 74%)   주황빛 노랑
// 70% → hsl(25, 80%, 73%)   주황
// 85% → hsl(83, 72%, 71%)   연두
// 100% → hsl(142, 65%, 71%) 초록
```

**활동 강도 그라디언트** (`getIntensityColorGradient`):
```typescript
// 0-10시간 사이 부드러운 색상 전환
const color = getIntensityColorGradient(hours);
```

---

## 🎯 적용된 차트

### ✅ 1. ActivityHeatMap (활동 히트맵)
**동적 색상**: `getIntensityColor(hours)`

```typescript
// 각 셀의 색상이 시간에 따라 변함
<div style={{ backgroundColor: getIntensityColor(dayData.hours) }} />

// 범례도 동적으로 생성
{[0, 1, 3, 5, 7].map(h => (
  <div style={{ backgroundColor: getIntensityColor(h) }} />
))}
```

**효과**:
- 0시간: 회색
- 1시간: 연한 파랑
- 3시간: 주황
- 5시간: 초록
- 7시간+: 진한 초록

---

### ✅ 2. GoalProgressRing (목표 진행도 링)
**동적 색상**: `getProgressColor(percentage)`

```typescript
const getColor = (percentage: number) => {
  return getProgressColor(percentage);
};

<Cell fill={getColor(percentage)} />
```

**효과**:
- 0-30%: 빨강 (목표 달성 낮음)
- 31-70%: 노랑 (진행중)
- 71-99%: 주황 (거의 달성)
- 100%: 초록 (완료!)

---

### ✅ 3. FocusTimeChart (집중 시간 차트)
**고정 색상**: 주황 (활동/에너지)

```typescript
// 집중 시간은 항상 주황색 (활동을 나타냄)
stroke="hsl(25, 80%, 72%)"
```

---

### ✅ 4. SessionDistributionChart (세션 분포)
**고정 색상**: 세션 타입별

```typescript
const sessionDistribution = [
  { name: "포모도로 (25분)", color: "hsl(0, 70%, 75%)" },   // 빨강
  { name: "단기 집중 (15분)", color: "hsl(45, 85%, 75%)" },  // 노랑
  { name: "장기 집중 (50분)", color: "hsl(142, 65%, 70%)" }, // 초록
  { name: "휴식", color: "hsl(210, 70%, 75%)" },             // 파랑
];
```

---

### ✅ 5. WeeklyActivityChart (주간 활동)
**고정 색상 + 호버 효과**

```typescript
fill={
  activeIndex === index
    ? "hsl(25, 80%, 65%)" // 진한 주황 (hover)
    : "hsl(25, 80%, 72%)" // 밝은 주황
}
```

---

### ✅ 6. MonthlyComparisonChart (월별 비교)
**고정 색상**: 올해 vs 작년

```typescript
// 올해: 초록 (성장/현재)
stroke="hsl(142, 65%, 70%)"

// 작년: 파랑 (기준/과거)
stroke="hsl(210, 70%, 75%)"
```

---

### ✅ 7. HourlyPatternChart (시간대별 패턴)
**고정 색상**: 주황 (활동)

```typescript
stroke="hsl(25, 80%, 72%)"
fill="hsl(25, 80%, 72%)"
```

---

## 🔧 추가 유틸리티 함수

### 세션 시간별 색상
```typescript
getSessionDurationColor(minutes: number)

// 20-30분: 빨강 (포모도로)
// <20분: 노랑 (단기)
// >30분: 초록 (장기)
```

### 시간대별 색상
```typescript
getHourColor(hour: number)

// 0-5시: 진한 파랑 (새벽)
// 6-11시: 주황 (아침)
// 12-17시: 초록 (오후)
// 18-23시: 파랑 (저녁)
```

### 업적 등급별 색상
```typescript
getAchievementColor(achievementRate: number)

// 150%+: 보라 (플래티넘)
// 100%+: 금색 (골드)
// 70%+: 은색 (실버)
// 30%+: 동색 (브론즈)
// <30%: 회색 (잠김)
```

### 연속 일수별 색상
```typescript
getStreakColor(streakDays: number)

// 30일+: 보라
// 14일+: 초록
// 7일+: 주황
// 3일+: 노랑
// <3일: 파랑
```

### 범위 기반 색상 스케일
```typescript
getColorScale(value, min, max, colorScheme)

// 값의 범위에 따라 자동으로 색상 계산
const color = getColorScale(75, 0, 100, 'progress');
```

---

## 📝 사용 가이드

### 1. 진행도 표시
```typescript
import { getProgressColor } from '@/utils/chart-colors';

// 목표 달성률
const progress = (current / goal) * 100;
const color = getProgressColor(progress);

<div style={{ backgroundColor: color }}>
  {progress}%
</div>
```

### 2. 히트맵
```typescript
import { getIntensityColor } from '@/utils/chart-colors';

// 활동 강도 표시
{data.map(item => (
  <div style={{ backgroundColor: getIntensityColor(item.hours) }} />
))}
```

### 3. 트렌드 표시
```typescript
import { getTrendColor } from '@/utils/chart-colors';

// 증감 표시
const color = getTrendColor(thisMonth, lastMonth);

<span style={{ color }}>
  {change > 0 ? '↑' : '↓'} {Math.abs(change)}%
</span>
```

### 4. 그라디언트 바
```typescript
import { getProgressColorGradient } from '@/utils/chart-colors';

// 부드러운 색상 전환
<div
  style={{
    background: `linear-gradient(to right,
      ${getProgressColorGradient(0)},
      ${getProgressColorGradient(50)},
      ${getProgressColorGradient(100)})`
  }}
/>
```

---

## 🎨 색상 의미 체계 (요약)

| 색상 | 의미 | 사용 예시 |
|------|------|-----------|
| 🔴 빨강 | 경고, 낮음, 포모도로 | 진행도 0-30%, 포모도로 세션 |
| 🟡 노랑 | 주의, 진행중, 단기 | 진행도 31-70%, 단기 집중 |
| 🟠 주황 | 활동, 에너지, 양호 | 집중 시간, 진행도 71-99% |
| 🟢 초록 | 성공, 완료, 장기 | 목표 달성, 장기 집중 |
| 🔵 파랑 | 안정, 휴식, 기준 | 휴식 시간, 작년 데이터 |
| 🟣 보라 | 특별, 프리미엄 | 플래티넘 배지, 30일+ 연속 |

---

## 🚀 다음 단계

### 추가 적용 가능 영역
1. **통계 카드** - 트렌드 색상
2. **배지 시스템** - 등급별 색상
3. **알림** - 타입별 색상
4. **프로그레스 바** - 진행도 그라디언트
5. **타임라인** - 시간대별 색상

### 개선 사항
1. 다크모드 색상 최적화
2. 색맹 접근성 개선
3. 애니메이션 효과 추가
4. 사용자 커스터마이징

---

**작성일**: 2025-12-18 03:30
**상태**: ✅ 동적 색상 시스템 완성
**핵심**: 수치에 따라 자동으로 변하는 의미있는 색상
