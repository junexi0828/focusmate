#!/usr/bin/env python3
"""GitHub Webhook Listener for NAS Auto-Deployment.

NAS에서 실행하여 GitHub push 이벤트를 받아 자동으로 git pull을 수행합니다.
"""

import hmac
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 프로젝트 디렉토리 (NAS 경로)
PROJECT_DIR = Path("/volume1/web/focusmate-backend")
WEBHOOK_SECRET = None  # .env에서 로드하거나 환경변수로 설정
PORT = 9000  # Webhook 리스너 포트


class WebhookHandler(BaseHTTPRequestHandler):
    """GitHub webhook 요청 핸들러."""

    def log_message(self, format, *args):
        """로그 메시지 출력 (표준 출력으로)."""
        print(f"[Webhook] {format % args}")

    def do_POST(self):
        """POST 요청 처리 (GitHub webhook)."""
        try:
            # Content-Length 확인
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Empty payload")
                return

            # Payload 읽기
            payload = self.rfile.read(content_length)
            payload_str = payload.decode("utf-8")

            # GitHub Signature 확인 (보안)
            github_signature = self.headers.get("X-Hub-Signature-256", "")
            if WEBHOOK_SECRET and github_signature:
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
                # main 또는 develop 브랜치만 처리
                if ref in ["refs/heads/main", "refs/heads/develop"]:
                    self.log_message(f"🔄 Processing push to {ref}")
                    self.handle_git_pull()
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

    def handle_git_pull(self):
        """NAS에서 git pull 실행."""
        if not PROJECT_DIR.exists():
            self.log_message(f"❌ Project directory not found: {PROJECT_DIR}")
            return

        self.log_message(f"📂 Project directory: {PROJECT_DIR}")

        try:
            # Git pull 실행
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.log_message("✅ Git pull successful")
                self.log_message(f"Output: {result.stdout}")

                # 실제로 변경사항이 있는지 확인
                output_lower = result.stdout.lower()
                has_changes = not ("already up to date" in output_lower or "already up-to-date" in output_lower)

                if has_changes:
                    self.log_message("🔄 Code changes detected, updating server...")

                    # 마이그레이션 실행 (필요시)
                    self.run_migrations()

                    # ⚠️ 개발 환경용: 서버 자동 재시작 활성화
                    # 🚨 실운영 배포 전 반드시 주석 처리 필요!
                    # 실운영에서는 무중단 배포 또는 수동 재시작 권장
                    self.restart_server()
                else:
                    self.log_message("✅ Already up to date, no restart needed")
            else:
                self.log_message(f"❌ Git pull failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.log_message("❌ Git pull timeout")
        except Exception as e:
            self.log_message(f"❌ Error during git pull: {e}")

    def run_migrations(self):
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
                )
                if result.returncode == 0:
                    self.log_message("✅ Migrations completed")
                else:
                    self.log_message(f"⚠️  Migration warning: {result.stderr}")
        except Exception as e:
            self.log_message(f"⚠️  Migration error: {e}")

    def restart_server(self):
        """서버 재시작 (선택적)."""
        try:
            # stop-nas.sh 실행
            stop_script = PROJECT_DIR / "stop-nas.sh"
            if stop_script.exists():
                subprocess.run([str(stop_script)], cwd=PROJECT_DIR, timeout=10)
                self.log_message("✅ Server stopped")

            # start-nas.sh 실행
            start_script = PROJECT_DIR / "start-nas.sh"
            if start_script.exists():
                subprocess.Popen(
                    [str(start_script)],
                    cwd=PROJECT_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.log_message("✅ Server started")
        except Exception as e:
            self.log_message(f"⚠️  Server restart error: {e}")


def load_webhook_secret():
    """.env 파일에서 webhook secret 로드."""
    global WEBHOOK_SECRET
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("GITHUB_WEBHOOK_SECRET="):
                    WEBHOOK_SECRET = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break


def main():
    """메인 함수."""
    print("=" * 60)
    print("GitHub Webhook Listener for NAS Auto-Deployment")
    print("=" * 60)
    print(f"Project directory: {PROJECT_DIR}")
    print(f"Port: {PORT}")
    print()

    # Webhook secret 로드
    load_webhook_secret()
    if WEBHOOK_SECRET:
        print("✅ Webhook secret loaded")
    else:
        print("⚠️  Warning: GITHUB_WEBHOOK_SECRET not found in .env")
        print("   Webhook will accept requests without signature verification")

    print()
    print(f"🚀 Starting webhook listener on port {PORT}...")
    print(f"   GitHub webhook URL: http://your-nas-ip:{PORT}/webhook")
    print(f"   Or via Cloudflare Tunnel: https://your-tunnel-url/webhook")
    print()

    # HTTP 서버 시작
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down webhook listener...")
        server.shutdown()


if __name__ == "__main__":
    main()
