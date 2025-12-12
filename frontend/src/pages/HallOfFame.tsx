/**
 * Hall of Fame Page - Comprehensive leaderboard with scatter plot
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { TeamScatterPlot } from '../components/charts/TeamScatterPlot';
import { PageTransition } from '../components/PageTransition';

type Period = 'weekly' | 'monthly' | 'all';

// Sample data - replace with API call
const sampleTeams = [
  {
    team_id: '1',
    team_name: 'AI 연구실',
    team_type: 'lab',
    total_focus_time: 1250,
    session_count: 50,
    total_game_score: 3200,
    game_count: 25,
  },
  {
    team_id: '2',
    team_name: '컴공 동아리',
    team_type: 'club',
    total_focus_time: 980,
    session_count: 42,
    total_game_score: 2800,
    game_count: 20,
  },
  {
    team_id: '3',
    team_name: '소프트웨어학과',
    team_type: 'department',
    total_focus_time: 1500,
    session_count: 65,
    total_game_score: 2100,
    game_count: 15,
  },
  {
    team_id: '4',
    team_name: '일반팀 A',
    team_type: 'general',
    total_focus_time: 750,
    session_count: 30,
    total_game_score: 1800,
    game_count: 18,
  },
  {
    team_id: '5',
    team_name: '데이터사이언스 연구실',
    team_type: 'lab',
    total_focus_time: 1100,
    session_count: 48,
    total_game_score: 2900,
    game_count: 22,
  },
];

export default function HallOfFame() {
  const [period, setPeriod] = useState<Period>('all');
  const [teams] = useState(sampleTeams);
  const currentTeamId = '1'; // Replace with actual current team ID

  // Sort teams for rankings
  const topFocusTeams = [...teams]
    .sort((a, b) => b.total_focus_time - a.total_focus_time)
    .slice(0, 10);

  const topGameTeams = [...teams]
    .sort((a, b) => b.total_game_score - a.total_game_score)
    .slice(0, 10);

  const periods: { value: Period; label: string }[] = [
    { value: 'weekly', label: 'This Week' },
    { value: 'monthly', label: 'This Month' },
    { value: 'all', label: 'All Time' },
  ];

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-5xl font-bold text-white mb-4">
              🏆 Hall of Fame
            </h1>
            <p className="text-xl text-gray-300">
              Comprehensive team performance overview
            </p>
          </motion.div>

          {/* Period Filter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-center gap-4 mb-8"
          >
            {periods.map((p) => (
              <motion.button
                key={p.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setPeriod(p.value)}
                className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                  period === p.value
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {p.label}
              </motion.button>
            ))}
          </motion.div>

          {/* Scatter Plot */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700 mb-8"
          >
            <h2 className="text-2xl font-bold text-white mb-6">
              📊 Team Performance Overview
            </h2>
            <p className="text-gray-400 mb-6">
              Scatter plot showing all teams' focus time vs game scores. Larger bubbles indicate higher activity.
            </p>
            <TeamScatterPlot teams={teams} currentTeamId={currentTeamId} />
          </motion.div>

          {/* Top Rankings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Top Focus Teams */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700"
            >
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <span>⏱️</span> Top Focus Teams
              </h3>
              <div className="space-y-3">
                {topFocusTeams.map((team, index) => (
                  <motion.div
                    key={team.team_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className={`flex items-center justify-between p-4 rounded-lg ${
                      team.team_id === currentTeamId
                        ? 'bg-green-600/20 border border-green-600/50'
                        : 'bg-gray-700/50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                      </span>
                      <div>
                        <div className="text-white font-semibold flex items-center gap-2">
                          {team.team_name}
                          {team.team_id === currentTeamId && (
                            <span className="text-xs bg-green-600 px-2 py-0.5 rounded">YOU</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-400 capitalize">{team.team_type}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-blue-400">
                        {team.total_focus_time.toFixed(0)} min
                      </div>
                      <div className="text-sm text-gray-400">{team.session_count} sessions</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Top Game Teams */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700"
            >
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <span>🎮</span> Top Game Teams
              </h3>
              <div className="space-y-3">
                {topGameTeams.map((team, index) => (
                  <motion.div
                    key={team.team_id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className={`flex items-center justify-between p-4 rounded-lg ${
                      team.team_id === currentTeamId
                        ? 'bg-green-600/20 border border-green-600/50'
                        : 'bg-gray-700/50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                      </span>
                      <div>
                        <div className="text-white font-semibold flex items-center gap-2">
                          {team.team_name}
                          {team.team_id === currentTeamId && (
                            <span className="text-xs bg-green-600 px-2 py-0.5 rounded">YOU</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-400 capitalize">{team.team_type}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-yellow-400">{team.total_game_score}</div>
                      <div className="text-sm text-gray-400">{team.game_count} games</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Stats Summary */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-8 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700"
          >
            <h3 className="text-xl font-bold text-white mb-4">📈 Overall Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-400">{teams.length}</div>
                <div className="text-sm text-gray-400">Total Teams</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400">
                  {teams.reduce((sum, t) => sum + t.total_focus_time, 0).toFixed(0)}
                </div>
                <div className="text-sm text-gray-400">Total Focus Time (min)</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-400">
                  {teams.reduce((sum, t) => sum + t.total_game_score, 0)}
                </div>
                <div className="text-sm text-gray-400">Total Game Score</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400">
                  {teams.reduce((sum, t) => sum + t.session_count + t.game_count, 0)}
                </div>
                <div className="text-sm text-gray-400">Total Activities</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </PageTransition>
  );
}
