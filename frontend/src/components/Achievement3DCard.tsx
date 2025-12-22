import { use3DCard } from '../hooks/use3DCard';
import { celebrateAchievement } from '../utils/confetti';
import { achievementIcons, type AchievementId } from '../assets/achievements';

interface Achievement3DCardProps {
  achievement: {
    achievement_id: string;
    achievement_name: string;
    achievement_description: string;
    is_unlocked: boolean;
    unlocked_at?: string;
    progress?: number;
    target?: number;
  };
  size?: 'small' | 'medium' | 'large';
  showProgress?: boolean;
}

export function Achievement3DCard({
  achievement,
  size = 'medium',
  showProgress = false
}: Achievement3DCardProps) {
  const card3D = use3DCard(15);
  const achievementId = achievement.achievement_id as AchievementId;
  const iconSrc = achievementIcons[achievementId] || achievementIcons['first-session'];

  const sizeClasses = {
    small: 'p-3',
    medium: 'p-4',
    large: 'p-6',
  };

  const iconSizes = {
    small: 'w-10 h-10',
    medium: 'w-16 h-16',
    large: 'w-20 h-20',
  };

  const handleClick = () => {
    if (achievement.is_unlocked) {
      celebrateAchievement();
    }
  };

  return (
    <div
      {...card3D}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label={`${achievement.achievement_name} 업적${achievement.is_unlocked ? ' - 획득 완료' : ''}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
      className={`
        card-3d
        flex items-center gap-4 rounded-lg
        ${achievement.is_unlocked
          ? 'bg-primary/5 border border-primary/20'
          : 'bg-muted/30 border border-border opacity-60'
        }
        ${sizeClasses[size]}
        cursor-pointer
        hover:shadow-lg
        transition-shadow duration-200
      `}
    >
      <div className={`flex items-center justify-center flex-shrink-0 ${iconSizes[size]}`}>
        <img
          src={iconSrc}
          alt=""
          className={`${iconSizes[size]} ${!achievement.is_unlocked && 'opacity-30 grayscale'}`}
          aria-hidden="true"
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <p className="font-semibold truncate">
            {achievement.achievement_name}
          </p>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {achievement.achievement_description}
        </p>

        {showProgress && achievement.progress !== undefined && achievement.target && (
          <div className="mt-2">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>진행도</span>
              <span>{achievement.progress} / {achievement.target}</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${Math.min((achievement.progress / achievement.target) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
