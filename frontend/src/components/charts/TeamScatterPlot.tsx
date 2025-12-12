/**
 * Team Performance Scatter Plot - Interactive visualization
 */
import { useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  Cell,
} from 'recharts';
import { motion } from 'framer-motion';

interface TeamData {
  team_id: string;
  team_name: string;
  team_type: string;
  total_focus_time: number;
  session_count: number;
  total_game_score: number;
  game_count: number;
}

interface TeamScatterPlotProps {
  teams: TeamData[];
  currentTeamId?: string;
}

export function TeamScatterPlot({ teams, currentTeamId }: TeamScatterPlotProps) {
  // Transform data for scatter plot
  const scatterData = useMemo(() => {
    return teams.map((team) => ({
      ...team,
      x: team.total_focus_time, // X-axis: Focus time
      y: team.total_game_score, // Y-axis: Game score
      z: team.session_count + team.game_count, // Size: Total activity
      isCurrentTeam: team.team_id === currentTeamId,
    }));
  }, [teams, currentTeamId]);

  // Color mapping for team types
  const teamTypeColors: Record<string, string> = {
    general: '#6366f1', // Indigo
    department: '#8b5cf6', // Purple
    lab: '#ec4899', // Pink
    club: '#f59e0b', // Amber
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gray-800/95 backdrop-blur-sm border border-gray-700 rounded-lg p-4 shadow-xl"
        >
          <h3 className="text-white font-bold text-lg mb-2">{data.team_name}</h3>
          <div className="space-y-1 text-sm">
            <p className="text-gray-300">
              <span className="text-gray-400">Type:</span>{' '}
              <span className="capitalize">{data.team_type}</span>
            </p>
            <p className="text-blue-400">
              <span className="text-gray-400">Focus Time:</span>{' '}
              <span className="font-semibold">{data.total_focus_time.toFixed(0)} min</span>
            </p>
            <p className="text-yellow-400">
              <span className="text-gray-400">Game Score:</span>{' '}
              <span className="font-semibold">{data.total_game_score}</span>
            </p>
            <p className="text-green-400">
              <span className="text-gray-400">Total Activity:</span>{' '}
              <span className="font-semibold">{data.z}</span>
            </p>
          </div>
          {data.isCurrentTeam && (
            <div className="mt-2 pt-2 border-t border-gray-700">
              <span className="text-green-400 font-semibold">⭐ Your Team</span>
            </div>
          )}
        </motion.div>
      );
    }
    return null;
  };

  // Custom legend
  const renderLegend = () => {
    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {Object.entries(teamTypeColors).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-sm text-gray-300 capitalize">{type}</span>
          </div>
        ))}
        {currentTeamId && (
          <div className="flex items-center gap-2 ml-4 pl-4 border-l border-gray-600">
            <div className="w-4 h-4 rounded-full bg-green-400 ring-2 ring-green-400/50" />
            <span className="text-sm text-green-400 font-semibold">Your Team</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={500}>
        <ScatterChart
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            type="number"
            dataKey="x"
            name="Focus Time"
            unit=" min"
            stroke="#9ca3af"
            label={{
              value: 'Total Focus Time (minutes)',
              position: 'insideBottom',
              offset: -10,
              fill: '#9ca3af',
            }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Game Score"
            stroke="#9ca3af"
            label={{
              value: 'Total Game Score',
              angle: -90,
              position: 'insideLeft',
              fill: '#9ca3af',
            }}
          />
          <ZAxis
            type="number"
            dataKey="z"
            range={[100, 1000]}
            name="Activity"
          />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
          <Scatter name="Teams" data={scatterData} shape="circle">
            {scatterData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  entry.isCurrentTeam
                    ? '#10b981' // Green for current team
                    : teamTypeColors[entry.team_type] || '#6366f1'
                }
                stroke={entry.isCurrentTeam ? '#10b981' : 'none'}
                strokeWidth={entry.isCurrentTeam ? 3 : 0}
                opacity={entry.isCurrentTeam ? 1 : 0.7}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      {renderLegend()}
    </div>
  );
}
