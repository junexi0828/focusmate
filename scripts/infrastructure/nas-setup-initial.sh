#!/bin/bash

# NAS 초기 설정 스크립트
# 한 번만 실행하면 됩니다. 이후 Git Hook이 자동으로 동기화합니다.
#
# 중요: 이 스크립트는 시스템 파일(/etc/ssh/sshd_config 등)을 변경하지 않습니다.
# SSH 옵션은 명령줄에서만 임시로 사용되며, 스크립트 종료 후에는 영향이 없습니다.

# set -e 제거: y/n 선택 시 메뉴로 돌아가기 위해 에러로 종료하지 않음
# set -e

# 프로젝트 루트 및 백엔드 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCAL_PATH="$PROJECT_ROOT/backend"

# 백엔드 .env 파일에서 NAS 설정 로드
ENV_FILE="$PROJECT_ROOT/backend/.env"
if [ -f "$ENV_FILE" ]; then
    # .env 파일에서 NAS 관련 변수만 추출하여 export
    # 주석과 빈 줄을 제외하고 NAS_로 시작하는 변수만 로드
    while IFS='=' read -r key value; do
        # 주석 제거 및 공백 제거
        key=$(echo "$key" | sed 's/#.*$//' | xargs)
        value=$(echo "$value" | sed 's/#.*$//' | xargs)
        # 빈 줄이나 주석만 있는 줄 건너뛰기
        if [ -n "$key" ] && [[ "$key" =~ ^NAS_ ]]; then
            export "$key=$value"
        fi
    done < <(grep -E '^NAS_' "$ENV_FILE" 2>/dev/null || true)
else
    echo "⚠️  Warning: $ENV_FILE 파일을 찾을 수 없습니다."
    echo "   기본값을 사용합니다."
fi

# 환경변수 기본값 설정 (env 파일에 없을 경우)
# 보안상 실제 IP 주소는 기본값으로 설정하지 않음
if [ -z "$NAS_USER" ] || [ -z "$NAS_IP" ] || [ -z "$NAS_BACKEND_PATH" ]; then
    echo "❌ Error: NAS 설정이 .env 파일에 없습니다."
    echo "   backend/.env 파일에 다음 설정을 추가하세요:"
    echo "   NAS_USER=your-nas-username"
    echo "   NAS_IP=192.168.x.x"
    echo "   NAS_BACKEND_PATH=/volume1/web/focusmate-backend"
    exit 1
fi

NAS_PATH="$NAS_BACKEND_PATH"

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    NAS 초기 설정 스크립트                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. NAS에 디렉토리 생성
echo "📁 1/4 NAS 디렉토리 생성 중..."
ssh "${NAS_USER}@${NAS_IP}" "mkdir -p ${NAS_PATH}"
echo "✅ 디렉토리 생성 완료: ${NAS_PATH}"
echo ""

# 2. 초기 파일 복제
echo "📦 2/4 초기 파일 복제 중..."

# SSH 옵션 설정 (일관성 유지)
# 주의: 이 옵션들은 명령줄에서만 임시로 사용되며, 시스템 파일(/etc/ssh/sshd_config 등)을 변경하지 않습니다.
# SSH는 자동으로 ~/.ssh/id_ed25519, ~/.ssh/id_rsa 등을 찾아서 사용합니다.
# PreferredAuthentications=publickey: 공개키 인증만 사용 (비밀번호 요구 방지)
# PubkeyAuthentication=yes: 공개키 인증 활성화
# ControlMaster=no: SSH 연결 재사용 비활성화 (rsync와의 호환성)
SSH_OPTS="-o BatchMode=yes -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=10 -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=publickey -o PubkeyAuthentication=yes -o ControlMaster=no"

# SSH 에이전트 확인 및 키 로드 상태 체크
if [ -n "$SSH_AUTH_SOCK" ]; then
  echo "   🔑 SSH 에이전트 확인 중..."
  # 에이전트에 로드된 키 확인
  LOADED_KEYS=$(ssh-add -l 2>/dev/null | wc -l | tr -d ' ')

  if [ "$LOADED_KEYS" -eq 0 ] || [ -z "$LOADED_KEYS" ]; then
    echo "   ⚠️  SSH 에이전트에 키가 로드되어 있지 않습니다."
    echo "   💡 passphrase가 있는 키를 사용하려면 먼저 키를 추가하세요:"
    echo "      eval \$(ssh-agent)"
    echo "      ssh-add ~/.ssh/id_ed25519"
    echo ""
    echo "   🔄 에이전트 없이 시도 중... (passphrase 없는 키가 있다면 작동할 수 있습니다)"
  else
    echo "   ✅ SSH 에이전트에 $LOADED_KEYS 개의 키가 로드되어 있습니다."
  fi
fi

# SSH 연결 테스트
echo "   SSH 연결 테스트 중..."
if ! ssh ${SSH_OPTS} "${NAS_USER}@${NAS_IP}" "echo 'SSH OK'" > /dev/null 2>&1; then
  echo "❌ SSH 키 인증 실패"
  echo ""
  echo "🔧 SSH 키 인증 설정 방법:"
  echo "   1. SSH 키 생성 (이미 있다면 건너뛰기):"
  echo "      ssh-keygen -t ed25519 -C 'your_email@example.com'"
  echo ""
  echo "   2. NAS에 SSH 키 복사:"
  echo "      ssh-copy-id ${NAS_USER}@${NAS_IP}"
  echo ""
  echo "   3. SSH 키 인증 테스트:"
  echo "      ssh ${NAS_USER}@${NAS_IP} 'echo SSH OK'"
  echo ""
  echo "   메뉴로 돌아갑니다."
  exit 0
fi
echo "   ✅ SSH 연결 확인됨"
echo ""

# rsync 실행 (SSH 옵션 추가: 비밀번호 프롬프트 방지)
# 주의: 이 명령어는 시스템 파일을 변경하지 않으며, SSH 옵션은 이 명령어에만 적용됩니다.
echo "   rsync 실행 중..."

# rsync가 SSH를 호출할 때 사용할 명령어를 명시적으로 지정
# SSH 옵션을 문자열로 구성하여 rsync에 전달
SSH_CMD="ssh ${SSH_OPTS}"

# rsync 실행 (stderr를 stdout으로 리다이렉트하여 오류 메시지 확인)
# --rsync-path="/usr/bin/rsync": 원격 서버의 rsync 경로 명시 (절대 경로)
# -e "${SSH_CMD}": SSH 옵션으로 키 인증만 사용
# --inplace: 파일을 직접 수정 (호환성 향상)
# rsync 실행 (Google Drive처럼 완전 동기화 - .env 포함)
# ⚠️  주의: .env 파일도 동기화되므로 민감한 정보가 NAS로 전송됩니다.
#     NAS 접근 권한이 안전한지 확인하세요.
RSYNC_OUTPUT=$(rsync -avz \
  --progress \
  --rsync-path="/usr/bin/rsync" \
  --inplace \
  -e "${SSH_CMD}" \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '.pytest_cache' \
  --exclude '.mypy_cache' \
  --exclude '*.log' \
  --exclude '.DS_Store' \
  --exclude 'node_modules' \
  "${LOCAL_PATH}/" \
  "${NAS_USER}@${NAS_IP}:${NAS_PATH}/" 2>&1)

RSYNC_EXIT_CODE=$?

if [ $RSYNC_EXIT_CODE -eq 0 ]; then
  echo "$RSYNC_OUTPUT"
  echo "✅ 파일 복제 완료"
else
  echo "$RSYNC_OUTPUT"
  echo ""
  echo "❌ 파일 복제 실패 (종료 코드: $RSYNC_EXIT_CODE)"
  echo ""

  # "Permission denied" 오류가 있는지 확인
  if echo "$RSYNC_OUTPUT" | grep -q "Permission denied"; then
    echo "🔍 문제 진단: rsync가 SSH를 호출할 때 비밀번호를 요구하고 있습니다."
    echo ""
    echo "💡 해결 방법:"
    echo "   1. SSH 키에 passphrase가 있다면, 먼저 SSH 에이전트에 키를 추가하세요:"
    echo "      eval \$(ssh-agent)"
    echo "      ssh-add ~/.ssh/id_ed25519  # 또는 사용하는 키"
    echo ""
    echo "   2. 또는 SSH 키 인증이 제대로 설정되어 있는지 확인:"
    echo "      ssh ${NAS_USER}@${NAS_IP} 'echo SSH OK'"
    echo ""
    echo "   3. 수동으로 rsync 실행 테스트:"
    echo "      rsync -avz --dry-run -e '${SSH_CMD}' ${LOCAL_PATH}/ ${NAS_USER}@${NAS_IP}:${NAS_PATH}/"
    echo ""
  elif echo "$RSYNC_OUTPUT" | grep -q "unexpected end of file\|protocol version"; then
    echo "🔍 문제 진단: rsync 프로토콜 버전 불일치 (openrsync vs 표준 rsync)"
    echo ""
    echo "💡 해결 방법: 표준 rsync 설치 (권장)"
    echo "   brew install rsync"
    echo ""
    echo "   설치 후 스크립트를 다시 실행하세요."
    echo ""
  else
    echo "🔧 문제 해결 방법:"
    echo "   1. SSH 키 인증이 설정되어 있는지 확인:"
    echo "      ssh ${NAS_USER}@${NAS_IP} 'echo SSH OK'"
    echo ""
    echo "   2. SSH 키가 없다면 복사:"
    echo "      ssh-copy-id ${NAS_USER}@${NAS_IP}"
    echo ""
    echo "   3. 수동으로 rsync 실행 테스트:"
    echo "      rsync -avz -e '${SSH_CMD}' ${LOCAL_PATH}/ ${NAS_USER}@${NAS_IP}:${NAS_PATH}/"
    echo ""
  fi
  echo "   메뉴로 돌아갑니다."
  exit 0
fi
echo ""

# 3. .env 파일 확인
echo "⚙️  3/4 .env 파일 확인"
echo "   .env 파일이 rsync를 통해 자동으로 동기화되었습니다."
echo ""
echo "   ⚠️  중요: CORS 설정 확인 필수!"
echo "   NAS의 .env 파일에서 CORS_ORIGINS에 다음이 포함되어 있는지 확인하세요:"
echo "   - https://eieconcierge.com"
echo "   - https://www.eieconcierge.com"
echo ""
echo "   확인 방법:"
echo "   ssh ${NAS_USER}@${NAS_IP}"
echo "   cd ${NAS_PATH}"
echo "   grep CORS_ORIGINS .env"
echo ""
echo "   예시:"
echo "   CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://eieconcierge.com,https://www.eieconcierge.com"
echo ""
while true; do
  read -p "   .env 파일의 CORS 설정을 확인하셨나요? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    break
  elif [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "⚠️  .env 파일의 CORS 설정을 확인한 후 다시 실행하세요."
    echo ""
    echo "   메뉴로 돌아갑니다."
    exit 0
  else
    echo "⚠️  y 또는 n만 입력 가능합니다. (y/n): "
  fi
done
echo ""

# 4. 가상환경 생성 및 의존성 설치 안내
echo "🐍 4/4 가상환경 생성 및 의존성 설치"
echo "   NAS에 접속하여 다음 명령어를 실행하세요:"
echo ""
echo "   ssh ${NAS_USER}@${NAS_IP}"
echo "   cd ${NAS_PATH}"
echo ""
echo "   # Python 3 경로 확인"
echo "   which python3"
echo ""
echo "   # 가상환경 생성"
echo "   python3 -m venv venv"
echo ""
echo "   # 가상환경 활성화"
echo "   source venv/bin/activate"
echo ""
echo "   # 의존성 설치"
echo "   pip install --upgrade pip"
echo "   pip install -r requirements.txt"
echo ""
while true; do
  read -p "   가상환경과 의존성을 설치하셨나요? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    break
  elif [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "⚠️  가상환경과 의존성을 설치한 후 다시 실행하세요."
    echo ""
    echo "   메뉴로 돌아갑니다."
    exit 0
  else
    echo "⚠️  y 또는 n만 입력 가능합니다. (y/n): "
  fi
done
echo ""

# 완료
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    초기 설정 완료!                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ 이후 Git 커밋 시 자동으로 NAS에 동기화됩니다."
echo ""
echo "🧪 테스트:"
echo "   git commit --allow-empty -m 'test: NAS 동기화 테스트'"
echo ""
echo "📋 NAS에서 백엔드 실행:"
echo "   ssh ${NAS_USER}@${NAS_IP}"
echo "   cd ${NAS_PATH}"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""

# 모든 단계가 성공적으로 완료된 경우에만 exit 0 (성공)
# 실패한 경우는 이미 위에서 exit 0으로 메뉴로 돌아감
# 이 부분은 모든 단계가 성공했을 때만 도달함
exit 0

