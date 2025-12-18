/**
 * Invitation Code Dialog Component
 * Generate and join rooms via invitation codes
 */

import { useState } from "react";
import { invitationService, type InvitationCodeInfo } from "../services/invitationService";

interface InvitationCodeDialogProps {
  roomId?: string;
  mode: "generate" | "join";
  onClose: () => void;
  onSuccess?: (roomId: string) => void;
}

export function InvitationCodeDialog({
  roomId,
  mode,
  onClose,
  onSuccess,
}: InvitationCodeDialogProps) {
  const [loading, setLoading] = useState(false);
  const [invitationCode, setInvitationCode] = useState<InvitationCodeInfo | null>(null);
  const [joinCode, setJoinCode] = useState("");
  const [expiresHours, setExpiresHours] = useState(24);
  const [maxUses, setMaxUses] = useState<number | undefined>(undefined);

  const handleGenerate = async () => {
    if (!roomId) return;

    setLoading(true);
    const response = await invitationService.generateInvitation(roomId, {
      expires_hours: expiresHours,
      max_uses: maxUses,
    });

    if (response.status === "success") {
      setInvitationCode(response.data);
    } else {
      alert(response.error?.message || "초대 코드 생성 실패");
    }
    setLoading(false);
  };

  const handleJoin = async () => {
    if (!joinCode.trim()) {
      alert("초대 코드를 입력해주세요");
      return;
    }

    setLoading(true);
    const response = await invitationService.joinByInvitation(joinCode);

    if (response.status === "success") {
      onSuccess?.(response.data.room_id);
      onClose();
    } else {
      alert(response.error?.message || "방 참가 실패");
    }
    setLoading(false);
  };

  const copyToClipboard = () => {
    if (invitationCode) {
      navigator.clipboard.writeText(invitationCode.code);
      alert("초대 코드가 복사되었습니다!");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            {mode === "generate" ? "초대 코드 생성" : "초대 코드로 참가"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        {mode === "generate" ? (
          <div className="space-y-4">
            {!invitationCode ? (
              <>
                {/* Generate Form */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    유효 시간 (시간)
                  </label>
                  <input
                    type="number"
                    value={expiresHours}
                    onChange={(e) => setExpiresHours(Number(e.target.value))}
                    min="1"
                    max="168"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    최대 사용 횟수 (선택사항)
                  </label>
                  <input
                    type="number"
                    value={maxUses || ""}
                    onChange={(e) =>
                      setMaxUses(e.target.value ? Number(e.target.value) : undefined)
                    }
                    min="1"
                    placeholder="무제한"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "생성 중..." : "초대 코드 생성"}
                </button>
              </>
            ) : (
              <>
                {/* Generated Code Display */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-center">
                    <p className="text-sm text-gray-600 mb-2">초대 코드</p>
                    <p className="text-3xl font-mono font-bold text-blue-600 tracking-wider">
                      {invitationCode.code}
                    </p>
                  </div>

                  <div className="mt-4 space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>만료일:</span>
                      <span>
                        {invitationCode.expires_at
                          ? new Date(invitationCode.expires_at).toLocaleString()
                          : "무제한"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>최대 사용:</span>
                      <span>
                        {invitationCode.max_uses
                          ? `${invitationCode.current_uses}/${invitationCode.max_uses}`
                          : "무제한"}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={copyToClipboard}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  코드 복사
                </button>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Join Form */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                초대 코드
              </label>
              <input
                type="text"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                placeholder="8자리 코드 입력"
                maxLength={8}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-lg tracking-wider text-center"
              />
            </div>

            <button
              onClick={handleJoin}
              disabled={loading || joinCode.length !== 8}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "참가 중..." : "방 참가하기"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
