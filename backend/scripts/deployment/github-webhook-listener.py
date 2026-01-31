#!/usr/bin/env python3
"""GitHub Webhook Listener for NAS Auto-Deployment.

NAS에서 실행하여 GitHub push 이벤트를 받아 자동으로 git pull을 수행합니다.
참고: .env 파일은 Git에서 관리되지 않으므로, 환경 변수 변경 시에는
로컬에서 ./deploy-nas.sh를 실행하여 수동으로 동기화해야 합니다.
"""

import hmac
import hashlib
import json
import subprocess
import sys
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# 프로젝트 디렉토리 (NAS 경로)
PROJECT_DIR = Path("/volume1/web/focusmate-backend")
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")  # .env에서 로드하거나 환경변수로 설정
PORT = 9000  # Webhook 리스너 포트
MAX_PAYLOAD_BYTES = 1_000_000  # 1MB payload cap to avoid abuse


class WebhookHandler(BaseHTTPRequestHandler):
    """GitHub webhook 요청 핸들러."""

    def log_message(self, format, *args):
        """로그 메시지 출력 (표준 출력으로)."""
        print(f"[Webhook] {format % args}")

    def do_POST(self):
        """POST 요청 처리 (GitHub webhook)."""
        try:
            if not WEBHOOK_SECRET:
                self.log_message("❌ Webhook secret not configured")
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"Webhook secret not configured")
                return

            # Content-Length 확인
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Empty payload")
                return
            if content_length > MAX_PAYLOAD_BYTES:
                self.send_response(413)
                self.end_headers()
                self.wfile.write(b"Payload too large")
                return

            # Payload 읽기
            payload = self.rfile.read(content_length)
            payload_str = payload.decode("utf-8")

            # GitHub Signature 확인 (보안)
            github_signature = self.headers.get("X-Hub-Signature-256", "")
            if not github_signature:
                self.log_message("❌ Missing signature")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Missing signature")
                return

            expected_signature = (
                "sha256="
                + hmac.new(
                    WEBHOOK_SECRET.encode(),
                    payload,
                    hashlib.sha256,
                ).hexdigest()
            )
            if not hmac.compare_digest(github_signature, expected_signature):
                self.log_message("❌ Invalid signature")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid signature")
                return

            # JSON 파싱
            try:
                event_data = json.loads(payload_str)
            except json.JSONDecodeError:
                self.log_message("❌ Invalid JSON")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
                return

            # GitHub Event 타입 확인
            event_type = self.headers.get("X-GitHub-Event", "")
            self.log_message(f"📥 Event: {event_type}")

            # push 이벤트만 처리
            if event_type == "push":
                ref = event_data.get("ref", "")
                # main 또는 master 브랜치만 처리
                if ref in ["refs/heads/main", "refs/heads/master"]:
                    self.log_message(f"🔄 Processing push to {ref}")
                    after_hash = event_data.get("after", "")
                    self.handle_git_pull(after_hash)
                else:
                    self.log_message(f"⏭️  Skipping push to {ref}")
            else:
                self.log_message(f"⏭️  Skipping event: {event_type}")

            # 성공 응답
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def do_GET(self):
        """GET 요청 처리 (health check)."""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GitHub Webhook Listener is running")

    def handle_git_pull(self, after_hash=None):
        """NAS에서 git pull 실행."""
        if not PROJECT_DIR.exists():
            self.log_message(f"❌ Project directory not found: {PROJECT_DIR}")
            return

        self.log_message(f"📂 Project directory: {PROJECT_DIR}")

        # Defense Logic: Check if rsync already deployed this hash
        rsync_hash_file = PROJECT_DIR / ".last_rsync_hash"
        if after_hash and rsync_hash_file.exists():
            try:
                with open(rsync_hash_file) as f:
                    last_rsync_hash = f.read().strip()
                if last_rsync_hash == after_hash:
                    self.log_message(f"🛡️  Defense: Hash {after_hash[:7]} already deployed via rsync. Syncing git only...")
                    # Sync git state without restarting
                    env = os.environ.copy()
                    subprocess.check_call(["git", "fetch", "--all"], cwd=PROJECT_DIR, env=env)
                    subprocess.check_call(["git", "reset", "--hard", "origin/main"], cwd=PROJECT_DIR, env=env)
                    self.log_message("✅ Git state synchronized. Skipping restart.")
                    return
            except Exception as e:
                self.log_message(f"⚠️  Error checking rsync hash: {e}")

        try:
            # 환경변수 설정 (PYTHONPATH 추가)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_DIR)

            # 1. Git Fetch 및 Reset (Hard) - 로컬 변경사항 무시하고 강제 동기화
            # Agent의 개선된 로직 유지
            subprocess.check_call(["git", "fetch", "--all"], cwd=PROJECT_DIR, env=env)

            # 변경사항이 있는지 확인하기 위해 현재 HEAD 기록
            old_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR).strip()

            subprocess.check_call(["git", "reset", "--hard", "origin/main"], cwd=PROJECT_DIR, env=env)

            new_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR).strip()

            if old_head != new_head:
                self.log_message("✅ Code updated successfully")
                self.log_message("🔄 Code changes detected, updating server...")

                # 의존성 설치 (requirements.txt 변경 감지)
                self.install_dependencies(env)

                # 마이그레이션 실행 (필요시)
                self.run_migrations(env)

                # 서버 재시작
                self.restart_server(env)
            else:
                self.log_message("✅ Already up to date, no restart needed")

        except subprocess.CalledProcessError as e:
            self.log_message(f"❌ Git/Deployment failed: {e}")
        except Exception as e:
            self.log_message(f"❌ Error during deployment: {e}")

    def install_dependencies(self, env):
        """의존성 자동 설치 (requirements.txt).

        Git pull 후 requirements.txt가 변경되었을 수 있으므로
        항상 pip install을 실행하여 최신 의존성을 유지합니다.
        """
        try:
            self.log_message("📦 Installing dependencies from requirements.txt...")

            # Conda 환경의 Python 사용
            conda_python = "/volume1/web/miniconda3/envs/focusmate_env/bin/python"
            requirements_file = PROJECT_DIR / "requirements.txt"

            if not Path(conda_python).exists():
                self.log_message(f"⚠️  Conda Python not found: {conda_python}")
                return

            if not requirements_file.exists():
                self.log_message(f"⚠️  requirements.txt not found: {requirements_file}")
                return

            # pip install 실행 (--quiet로 출력 최소화)
            result = subprocess.run(
                [conda_python, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
                env=env
            )

            if result.returncode == 0:
                self.log_message("✅ Dependencies installed successfully")
            else:
                self.log_message(f"⚠️  Dependency installation warning: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.log_message("⚠️  Dependency installation timeout (continuing anyway)")
        except Exception as e:
            self.log_message(f"⚠️  Dependency installation error: {e}")

    def run_migrations(self, env):
        """데이터베이스 마이그레이션 실행."""
        try:
            # Conda 환경의 Python 사용
            conda_python = "/volume1/web/miniconda3/envs/focusmate_env/bin/python"
            if Path(conda_python).exists():
                result = subprocess.run(
                    [conda_python, "-m", "alembic", "upgrade", "head"],
                    cwd=PROJECT_DIR,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env=env
                )
                if result.returncode == 0:
                    self.log_message("✅ Migrations completed")
                else:
                    self.log_message(f"⚠️  Migration warning: {result.stderr}")
        except Exception as e:
            self.log_message(f"⚠️  Migration error: {e}")

    def restart_server(self, env):
        """서버 재시작."""
        try:
            self.log_message("🔄 Restarting backend service...")

            # Fast Restart (Backend only)
            # NAS code mount (./:/app) means we only need to restart the container to pick up code changes
            self.log_message("🔄 Performing fast restart (backend only)...")

            subprocess.run(
                ["sudo", "/usr/local/bin/docker-compose", "-f", "docker-compose.nas.yml", "restart", "backend"],
                cwd=PROJECT_DIR,
                check=True,
                env=env
            )

            self.log_message("✅ Restart command issued")

        except Exception as e:
            self.log_message(f"❌ Restart failed: {e}")


def run(server_class=HTTPServer, handler_class=WebhookHandler, port=PORT):
    # .env 로드 (간이)
    global WEBHOOK_SECRET
    env_path = PROJECT_DIR / ".env"
    if env_path.exists() and not WEBHOOK_SECRET:
        try:
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GITHUB_WEBHOOK_SECRET="):
                        WEBHOOK_SECRET = line.strip().split("=", 1)[1]
                        # 따옴표 제거
                        WEBHOOK_SECRET = WEBHOOK_SECRET.strip("'").strip('"')
                        break
        except Exception as e:
            print(f"⚠️  Failed to load .env: {e}")

    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"🚀 Starting webhook listener on port {port}...")
    if WEBHOOK_SECRET:
        print("🔒 Webhook secret configured")
    else:
        print("⚠️  No webhook secret configured!")

    httpd.serve_forever()


if __name__ == "__main__":
    run()
