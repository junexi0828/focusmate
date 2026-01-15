#!/usr/bin/env python3
"""GitHub Webhook Listener for NAS Auto-Deployment.

NAS에서 실행하여 GitHub push 이벤트를 받아 자동으로 git pull을 수행합니다.
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
                # main 또는 develop 브랜치만 처리
                if ref in ["refs/heads/main", "refs/heads/master"]:
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

    def handle_git_pull(self):
        """Git Pull 수행 및 서버 재시작."""
        try:
            self.log_message("🔄 Starting deployment...")

            # 환경변수 설정 (PYTHONPATH 추가)
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_DIR)

            # 1. Git Reset (Hard) - 로컬 변경사항(Rsync 등) 무시하고 강제 동기화
            cmd = ["git", "fetch", "--all"]
            subprocess.check_call(cmd, cwd=PROJECT_DIR, env=env)

            cmd = ["git", "reset", "--hard", "origin/main"]
            subprocess.check_call(cmd, cwd=PROJECT_DIR, env=env)

            self.log_message("✅ Code updated successfully")

            # 2. 서버 재시작
            self.restart_server(env)

        except subprocess.CalledProcessError as e:
            self.log_message(f"❌ Git/Deployment failed: {e}")
            raise
        except Exception as e:
            self.log_message(f"❌ Error during deployment: {e}")
            raise

    def restart_server(self, env=None):
        """서버 재시작."""
        try:
            self.log_message("🔄 Restarting backend service...")
            if env is None:
                env = os.environ.copy()
                env["PYTHONPATH"] = str(PROJECT_DIR)

            # stop-nas.sh 실행
            subprocess.run(["bash", "stop-nas.sh"], cwd=PROJECT_DIR, check=False, env=env)

            # start-nas.sh 실행 (nohup 아님 - 리스너가 관리하지 않음, 별도 프로세스로 분리)
            # 주의: 리스너가 죽지 않도록 Popen 사용
            subprocess.Popen(["bash", "start-nas.sh"], cwd=PROJECT_DIR,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

            self.log_message("✅ Restart command issued")

        except Exception as e:
            self.log_message(f"❌ Restart failed: {e}")
            raise


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
