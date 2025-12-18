// Achievement Icons
// All icons use Air Mint Sky (#7ED6E8) color scheme with Korean Air design principles

import firstSession from './first-session.svg';
import sevenDayStreak from './seven-day-streak.svg';
import hundredHours from './hundred-hours.svg';
import communityActivist from './community-activist.svg';
import teamLeader from './team-leader.svg';
import minigameMaster from './minigame-master.svg';
import perfectWeek from './perfect-week.svg';
import earlyBird from './early-bird.svg';
import nightOwl from './night-owl.svg';
import focusMaster from './focus-master.svg';
import socialButterfly from './social-butterfly.svg';
import mentor from './mentor.svg';
import speedrunner from './speedrunner.svg';
import marathoner from './marathoner.svg';
import perfectionist from './perfectionist.svg';

export const achievementIcons = {
  'first-session': firstSession,
  'seven-day-streak': sevenDayStreak,
  'hundred-hours': hundredHours,
  'community-activist': communityActivist,
  'team-leader': teamLeader,
  'minigame-master': minigameMaster,
  'perfect-week': perfectWeek,
  'early-bird': earlyBird,
  'night-owl': nightOwl,
  'focus-master': focusMaster,
  'social-butterfly': socialButterfly,
  'mentor': mentor,
  'speedrunner': speedrunner,
  'marathoner': marathoner,
  'perfectionist': perfectionist,
} as const;

export type AchievementId = keyof typeof achievementIcons;

export const achievementNames: Record<AchievementId, string> = {
  'first-session': '첫 세션 완료',
  'seven-day-streak': '7일 연속 출석',
  'hundred-hours': '100시간 달성',
  'community-activist': '커뮤니티 활동가',
  'team-leader': '팀 리더',
  'minigame-master': '미니게임 마스터',
  'perfect-week': '완벽한 주',
  'early-bird': '새벽형 인간',
  'night-owl': '올빼미',
  'focus-master': '집중 마스터',
  'social-butterfly': '소셜 버터플라이',
  'mentor': '멘토',
  'speedrunner': '스피드러너',
  'marathoner': '마라토너',
  'perfectionist': '완벽주의자',
};

export const achievementDescriptions: Record<AchievementId, string> = {
  'first-session': '첫 포모도로 세션을 완료했습니다',
  'seven-day-streak': '7일 연속으로 학습했습니다',
  'hundred-hours': '총 100시간 학습을 달성했습니다',
  'community-activist': '커뮤니티에 활발히 참여했습니다',
  'team-leader': '팀을 성공적으로 이끌었습니다',
  'minigame-master': '모든 미니게임을 마스터했습니다',
  'perfect-week': '일주일 동안 완벽하게 학습했습니다',
  'early-bird': '새벽 시간대에 학습했습니다',
  'night-owl': '밤 시간대에 학습했습니다',
  'focus-master': '높은 집중력을 유지했습니다',
  'social-butterfly': '많은 사람들과 함께 학습했습니다',
  'mentor': '다른 사람들을 도왔습니다',
  'speedrunner': '빠르게 목표를 달성했습니다',
  'marathoner': '장시간 학습을 완료했습니다',
  'perfectionist': '모든 세션을 완벽하게 완료했습니다',
};
