/**
 * Mini-Games Page - Arcade games for ranking competition
 */
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { DinoJump } from '../components/games/DinoJump';
import { DotCollector } from '../components/games/DotCollector';
import { SnakeGame } from '../components/games/SnakeGame';
import { PageTransition } from '../components/PageTransition';
import { rankingService } from '../features/ranking/services/rankingService';
import { toast } from 'sonner';

type GameType = 'dino_jump' | 'dot_collector' | 'snake' | null;

const games = [
  {
    id: 'dino_jump' as const,
    name: 'Dino Jump',
    description: 'Jump over obstacles like Chrome dinosaur',
    icon: '🦖',
    color: 'from-green-500 to-emerald-600',
  },
  {
    id: 'dot_collector' as const,
    name: 'Dot Collector',
    description: 'Collect all dots while avoiding enemies',
    icon: '🟡',
    color: 'from-yellow-500 to-amber-600',
  },
  {
    id: 'snake' as const,
    name: 'Snake',
    description: 'Classic snake game - eat and grow',
    icon: '🐍',
    color: 'from-green-500 to-teal-600',
  },
];

export default function MiniGames() {
  const [selectedGame, setSelectedGame] = useState<GameType>(null);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  // Get user's teams
  const { data: teams = [] } = useQuery({
    queryKey: ['my-teams'],
    queryFn: async () => {
      const response = await rankingService.getMyTeams();
      if (response.status === 'error') {
        throw new Error(response.error?.message || 'Failed to load teams');
      }
      return response.data || [];
    },
  });

  // Get first team with mini_game_enabled
  const activeTeam = teams.find((team) => team.mini_game_enabled);

  // Load leaderboard when game is selected
  useEffect(() => {
    if (selectedGame) {
      loadLeaderboard();
    }
  }, [selectedGame]);

  const loadLeaderboard = async () => {
    if (!selectedGame) return;
    try {
      const { getMiniGameLeaderboard } = await import('../api/miniGames');
      const leaderboardData = await getMiniGameLeaderboard(selectedGame);
      setLeaderboard(leaderboardData);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    }
  };

  const handleGameOver = async (score: number, time: number) => {
    console.log('Game Over:', { score, time, game: selectedGame });

    if (!activeTeam) {
      toast.error('미니게임이 활성화된 팀에 가입해주세요');
      return;
    }

    // Submit score to backend
    try {
      const { submitMiniGameScore, getMiniGameLeaderboard } = await import('../api/miniGames');
      if (selectedGame) {
        await submitMiniGameScore(
          activeTeam.team_id,
          selectedGame,
          score,
          time
        );
        toast.success('점수가 제출되었습니다!');

        // Refresh leaderboard after submission
        const leaderboardData = await getMiniGameLeaderboard(selectedGame);
        setLeaderboard(leaderboardData);
      }
    } catch (error: any) {
      console.error('Failed to submit score or refresh leaderboard:', error);
      toast.error(error?.response?.data?.detail || '점수 제출에 실패했습니다');
    }
  };

  if (selectedGame) {
    return (
      <PageTransition>
        <div className="min-h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
          <div className="max-w-6xl mx-auto">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedGame(null)}
              className="mb-6 px-4 py-2 bg-gray-700 text-white rounded-lg"
            >
              ← Back to Games
            </motion.button>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
              {selectedGame === 'dino_jump' && <DinoJump onGameOver={handleGameOver} />}
              {selectedGame === 'dot_collector' && <DotCollector onGameOver={handleGameOver} />}
              {selectedGame === 'snake' && <SnakeGame onGameOver={handleGameOver} />}
            </div>

            {/* Leaderboard */}
            {leaderboard.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700"
              >
                <h3 className="text-2xl font-bold text-white mb-4">🏆 Leaderboard</h3>
                <div className="space-y-2">
                  {leaderboard.map((entry, index) => (
                    <div
                      key={entry.team_id}
                      className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">
                          {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                        </span>
                        <span className="text-white font-semibold">{entry.team_name}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-yellow-400">{entry.best_score}</div>
                        <div className="text-sm text-gray-400">{entry.games_played} games</div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </PageTransition>
    );
  }

  if (!activeTeam) {
    return (
      <PageTransition>
        <div className="min-h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              <h1 className="text-5xl font-bold text-white mb-4">
                🎮 Mini-Games
              </h1>
              <p className="text-xl text-gray-300 mb-8">
                미니게임을 플레이하려면 미니게임이 활성화된 팀에 가입해야 합니다.
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => (window.location.href = '/ranking')}
                className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold"
              >
                랭킹 페이지로 이동
              </motion.button>
            </motion.div>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl font-bold text-white mb-4">
              🎮 Mini-Games
            </h1>
            <p className="text-xl text-gray-300">
              Play arcade games and compete with other teams!
            </p>
            <p className="text-sm text-gray-400 mt-2">
              현재 팀: {activeTeam.team_name}
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {games.map((game, index) => (
              <motion.div
                key={game.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                onClick={() => setSelectedGame(game.id)}
                className="cursor-pointer"
              >
                <div className={`bg-gradient-to-br ${game.color} rounded-2xl p-8 text-white shadow-2xl`}>
                  <div className="text-6xl mb-4 text-center">{game.icon}</div>
                  <h3 className="text-2xl font-bold mb-2 text-center">{game.name}</h3>
                  <p className="text-white/90 text-center mb-6">{game.description}</p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full py-3 bg-white/20 backdrop-blur-sm rounded-lg font-semibold hover:bg-white/30 transition-colors"
                  >
                    Play Now
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Overall Leaderboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-12 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700"
          >
            <h2 className="text-3xl font-bold text-white mb-6">🏆 Top Teams</h2>
            <p className="text-gray-400 text-center py-8">
              Play games to see your team on the leaderboard!
            </p>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
}
