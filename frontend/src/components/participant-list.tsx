import { Users, Crown } from "lucide-react";
import { Card } from "./ui/card";

export interface Participant {
  id: string;
  name: string;
  isHost: boolean;
}

interface ParticipantListProps {
  participants: Participant[];
  currentUserName?: string;
}

export function ParticipantList({
  participants,
  currentUserName,
}: ParticipantListProps) {
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((word) => word[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const colors = [
    "bg-indigo-100 text-indigo-700",
    "bg-emerald-100 text-emerald-700",
    "bg-amber-100 text-amber-700",
    "bg-rose-100 text-rose-700",
    "bg-blue-100 text-blue-700",
    "bg-purple-100 text-purple-700",
  ];

  return (
    <Card className="bg-white shadow-sm p-6 sticky top-24">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-gray-600" />
        <h2 className="text-lg font-semibold text-gray-900">Participants</h2>
        <span className="ml-auto text-sm text-gray-500">
          {participants.length}
        </span>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {participants.map((participant, index) => (
          <div
            key={participant.id}
            className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
              participant.name === currentUserName
                ? "bg-indigo-50 border border-indigo-200"
                : "bg-gray-50"
            }`}
          >
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                colors[index % colors.length]
              }`}
              aria-label={`${participant.name}'s avatar`}
            >
              {getInitials(participant.name)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-medium text-gray-900 truncate">
                  {participant.name}
                  {participant.name === currentUserName && (
                    <span className="text-xs text-gray-500 ml-1">(You)</span>
                  )}
                </p>
                {participant.isHost && (
                  <Crown
                    className="w-4 h-4 text-amber-500 flex-shrink-0"
                    aria-label="Host"
                  />
                )}
              </div>
              {participant.isHost && (
                <p className="text-xs text-gray-500">Room Host</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {participants.length === 0 && (
        <div className="text-center py-8">
          <Users className="w-12 h-12 text-gray-300 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">No participants yet</p>
        </div>
      )}
    </Card>
  );
}
