/**
 * 동적 차트 색상 시스템
 *
 * 수치에 따라 자동으로 색상이 변하는 시스템
 */

export const chartColors = {
  // 기본 파스텔 색상
  primary: {
    blue: 'hsl(210, 70%, 75%)',
    green: 'hsl(142, 65%, 70%)',
    red: 'hsl(0, 70%, 75%)',
    yellow: 'hsl(45, 85%, 75%)',
    purple: 'hsl(270, 60%, 75%)',
    orange: 'hsl(25, 80%, 72%)',
  },

  // 세션 타입별 색상 (고정)
  session: {
    work: 'hsl(25, 80%, 72%)',       // 오렌지 - 작업/집중
    break: 'hsl(210, 70%, 75%)',     // 블루 - 휴식
    pomodoro: 'hsl(0, 70%, 75%)',    // 레드 - 포모도로
    short: 'hsl(45, 85%, 75%)',      // 옐로우 - 단기
    long: 'hsl(142, 65%, 70%)',      // 그린 - 장기
  },
};

/**
 * 진행도에 따른 동적 색상 (0-100%)
 *
 * 색상 변화:
 * - 0-30%: 빨강 (위험)
 * - 31-70%: 노랑 (주의)
 * - 71-99%: 주황 (양호)
 * - 100%: 초록 (완료)
 *
 * @param percentage 진행도 (0-100)
 * @returns HSL 색상 문자열
 */
export function getProgressColor(percentage: number): string {
  if (percentage >= 100) {
    return 'hsl(142, 65%, 70%)'; // 초록 - 완료
  }
  if (percentage >= 71) {
    return 'hsl(25, 80%, 72%)'; // 주황 - 양호
  }
  if (percentage >= 31) {
    return 'hsl(45, 85%, 75%)'; // 노랑 - 주의
  }
  return 'hsl(0, 70%, 75%)'; // 빨강 - 위험
}

/**
 * 진행도에 따른 그라디언트 색상 (부드러운 전환)
 *
 * @param percentage 진행도 (0-100)
 * @returns HSL 색상 문자열
 */
export function getProgressColorGradient(percentage: number): string {
  // 0-30%: 빨강에서 노랑으로
  if (percentage <= 30) {
    const ratio = percentage / 30;
    const hue = 0 + (45 * ratio); // 0 (빨강) -> 45 (노랑)
    return `hsl(${hue}, 75%, 75%)`;
  }

  // 31-70%: 노랑에서 주황으로
  if (percentage <= 70) {
    const ratio = (percentage - 30) / 40;
    const hue = 45 - (20 * ratio); // 45 (노랑) -> 25 (주황)
    return `hsl(${hue}, 80%, 73%)`;
  }

  // 71-100%: 주황에서 초록으로
  const ratio = (percentage - 70) / 30;
  const hue = 25 + (117 * ratio); // 25 (주황) -> 142 (초록)
  const saturation = 80 - (15 * ratio); // 80% -> 65%
  return `hsl(${hue}, ${saturation}%, 71%)`;
}

/**
 * 활동 강도에 따른 동적 색상 (히트맵용)
 *
 * 색상 변화:
 * - 0시간: 회색 (활동 없음)
 * - 0-1시간: 매우 연한 파랑
 * - 1-2시간: 연한 파랑
 * - 2-4시간: 주황
 * - 4-6시간: 초록
 * - 6시간+: 진한 초록
 *
 * @param hours 집중 시간 (시간 단위)
 * @returns HSL 색상 문자열
 */
export function getIntensityColor(hours: number): string {
  if (hours === 0) {
    return 'hsl(0, 0%, 95%)'; // 회색
  }
  if (hours < 1) {
    return 'hsl(210, 70%, 90%)'; // 매우 연한 파랑
  }
  if (hours < 2) {
    return 'hsl(210, 70%, 80%)'; // 연한 파랑
  }
  if (hours < 4) {
    return 'hsl(25, 80%, 75%)'; // 주황
  }
  if (hours < 6) {
    return 'hsl(142, 65%, 70%)'; // 초록
  }
  return 'hsl(142, 70%, 60%)'; // 진한 초록
}

/**
 * 활동 강도에 따른 그라디언트 색상 (부드러운 전환)
 *
 * @param hours 집중 시간 (0-10+)
 * @returns HSL 색상 문자열
 */
export function getIntensityColorGradient(hours: number): string {
  if (hours === 0) {
    return 'hsl(0, 0%, 95%)';
  }

  // 최대값 제한
  const clampedHours = Math.min(hours, 10);

  // 0-2시간: 파랑 계열
  if (clampedHours <= 2) {
    const lightness = 90 - (clampedHours * 5); // 90% -> 80%
    return `hsl(210, 70%, ${lightness}%)`;
  }

  // 2-4시간: 파랑에서 주황으로
  if (clampedHours <= 4) {
    const ratio = (clampedHours - 2) / 2;
    const hue = 210 - (185 * ratio); // 210 (파랑) -> 25 (주황)
    const lightness = 80 - (5 * ratio); // 80% -> 75%
    return `hsl(${hue}, 75%, ${lightness}%)`;
  }

  // 4-10시간: 주황에서 초록으로
  const ratio = (clampedHours - 4) / 6;
  const hue = 25 + (117 * ratio); // 25 (주황) -> 142 (초록)
  const lightness = 75 - (15 * ratio); // 75% -> 60%
  return `hsl(${hue}, 68%, ${lightness}%)`;
}

/**
 * 트렌드에 따른 동적 색상
 *
 * @param value 현재 값
 * @param previousValue 이전 값
 * @param threshold 변화 임계값 (기본 0)
 * @returns HSL 색상 문자열
 */
export function getTrendColor(
  value: number,
  previousValue: number,
  threshold: number = 0
): string {
  const change = value - previousValue;

  if (change > threshold) {
    return 'hsl(142, 65%, 70%)'; // 초록 - 상승
  }
  if (change < -threshold) {
    return 'hsl(0, 70%, 75%)'; // 빨강 - 하락
  }
  return 'hsl(210, 70%, 75%)'; // 파랑 - 중립
}

/**
 * 트렌드 변화율에 따른 그라디언트 색상
 *
 * @param changePercentage 변화율 (-100 ~ +100)
 * @returns HSL 색상 문자열
 */
export function getTrendColorGradient(changePercentage: number): string {
  // 음수 (하락): 빨강
  if (changePercentage < 0) {
    const intensity = Math.min(Math.abs(changePercentage), 100) / 100;
    const lightness = 85 - (10 * intensity); // 85% -> 75%
    return `hsl(0, 70%, ${lightness}%)`;
  }

  // 0 (중립): 파랑
  if (changePercentage === 0) {
    return 'hsl(210, 70%, 75%)';
  }

  // 양수 (상승): 초록
  const intensity = Math.min(changePercentage, 100) / 100;
  const lightness = 85 - (15 * intensity); // 85% -> 70%
  return `hsl(142, 65%, ${lightness}%)`;
}

/**
 * 세션 시간에 따른 동적 색상
 *
 * @param minutes 세션 시간 (분)
 * @returns HSL 색상 문자열
 */
export function getSessionDurationColor(minutes: number): string {
  if (minutes >= 20 && minutes <= 30) {
    return 'hsl(0, 70%, 75%)'; // 빨강 - 포모도로
  }
  if (minutes < 20) {
    return 'hsl(45, 85%, 75%)'; // 노랑 - 단기
  }
  return 'hsl(142, 65%, 70%)'; // 초록 - 장기
}

/**
 * 시간대에 따른 동적 색상 (24시간)
 *
 * @param hour 시간 (0-23)
 * @returns HSL 색상 문자열
 */
export function getHourColor(hour: number): string {
  // 새벽 (0-5): 진한 파랑
  if (hour < 6) {
    return 'hsl(210, 70%, 65%)';
  }
  // 아침 (6-11): 주황
  if (hour < 12) {
    return 'hsl(25, 80%, 72%)';
  }
  // 오후 (12-17): 초록
  if (hour < 18) {
    return 'hsl(142, 65%, 70%)';
  }
  // 저녁 (18-23): 파랑
  return 'hsl(210, 70%, 75%)';
}

/**
 * 목표 달성률에 따른 배지 색상
 *
 * @param achievementRate 달성률 (0-100+)
 * @returns HSL 색상 문자열
 */
export function getAchievementColor(achievementRate: number): string {
  if (achievementRate >= 150) {
    return 'hsl(270, 60%, 75%)'; // 보라 - 플래티넘
  }
  if (achievementRate >= 100) {
    return 'hsl(45, 85%, 70%)'; // 금색 - 골드
  }
  if (achievementRate >= 70) {
    return 'hsl(0, 0%, 75%)'; // 은색 - 실버
  }
  if (achievementRate >= 30) {
    return 'hsl(25, 70%, 70%)'; // 동색 - 브론즈
  }
  return 'hsl(0, 0%, 80%)'; // 회색 - 잠김
}

/**
 * 연속 일수에 따른 동적 색상
 *
 * @param streakDays 연속 일수
 * @returns HSL 색상 문자열
 */
export function getStreakColor(streakDays: number): string {
  if (streakDays >= 30) {
    return 'hsl(270, 60%, 75%)'; // 보라 - 1개월+
  }
  if (streakDays >= 14) {
    return 'hsl(142, 65%, 70%)'; // 초록 - 2주+
  }
  if (streakDays >= 7) {
    return 'hsl(25, 80%, 72%)'; // 주황 - 1주+
  }
  if (streakDays >= 3) {
    return 'hsl(45, 85%, 75%)'; // 노랑 - 3일+
  }
  return 'hsl(210, 70%, 75%)'; // 파랑 - 시작
}

/**
 * 값의 범위에 따른 색상 스케일
 *
 * @param value 현재 값
 * @param min 최소값
 * @param max 최대값
 * @param colorScheme 색상 스킴 ('progress' | 'intensity' | 'trend')
 * @returns HSL 색상 문자열
 */
export function getColorScale(
  value: number,
  min: number,
  max: number,
  colorScheme: 'progress' | 'intensity' | 'trend' = 'progress'
): string {
  const percentage = ((value - min) / (max - min)) * 100;

  switch (colorScheme) {
    case 'progress':
      return getProgressColorGradient(percentage);
    case 'intensity':
      return getIntensityColorGradient(value);
    case 'trend':
      return getTrendColorGradient(percentage - 50); // -50 ~ +50
    default:
      return getProgressColorGradient(percentage);
  }
}

// 차트별 색상 배열 (고정)
export const chartColorArrays = {
  sessionDistribution: [
    'hsl(0, 70%, 75%)',   // 레드 - 포모도로
    'hsl(45, 85%, 75%)',  // 옐로우 - 단기
    'hsl(142, 65%, 70%)', // 그린 - 장기
    'hsl(210, 70%, 75%)', // 블루 - 휴식
  ],
  weeklyActivity: [
    'hsl(25, 80%, 72%)',  // 오렌지 - 집중 시간
    'hsl(210, 70%, 75%)', // 블루 - 세션 수
  ],
  monthlyComparison: [
    'hsl(142, 65%, 70%)', // 그린 - 올해
    'hsl(210, 70%, 75%)', // 블루 - 작년
  ],
};

// CSS 변수 내보내기
export const chartColorsCss = `
  :root {
    --chart-primary-blue: hsl(210, 70%, 75%);
    --chart-primary-green: hsl(142, 65%, 70%);
    --chart-primary-red: hsl(0, 70%, 75%);
    --chart-primary-yellow: hsl(45, 85%, 75%);
    --chart-primary-purple: hsl(270, 60%, 75%);
    --chart-primary-orange: hsl(25, 80%, 72%);
  }
`;
