import os
import sys
import time
import subprocess
import json
import httpx
import asyncio
from pathlib import Path

# Add root to sys.path
SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
sys.path.append(str(BACKEND_DIR))

# Try to load env manually if needed or just use os.environ
# Assuming .env is sourced or loaded by the caller

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
LOG_FILE = os.environ.get("LOG_FILE", "/volume1/web/focusmate-backend/logs/app.log")
ERROR_PATTERNS = [
    "sqlalchemy.exc.TimeoutError",
    "DatabaseError",
    "ConnectionError",
    "CRITICAL",
    "ERROR"
]

async def send_slack(message, level="error"):
    if not SLACK_WEBHOOK_URL:
        return

    color = "#e01e5a" if level == "error" else "#ecb22e"
    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"[ALERT] Log Monitor",
                "text": f"Detected critical log entry:\n```{message}```",
                "footer": "Log Alerter",
                "ts": int(time.time())
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(SLACK_WEBHOOK_URL, json=payload)

async def tail_f(filename):
    if not os.path.exists(filename):
        print(f"Log file {filename} not found.")
        return

    process = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print(f"Monitoring logs: {filename}...")
    while True:
        line = process.stdout.readline()
        if not line:
            await asyncio.sleep(0.1)
            continue

        for pattern in ERROR_PATTERNS:
            if pattern in line:
                print(f"Match found: {line.strip()}")
                await send_slack(line.strip())
                break

if __name__ == "__main__":
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set.")
        sys.exit(1)

    try:
        asyncio.run(tail_f(LOG_FILE))
    except KeyboardInterrupt:
        print("Stopping log monitor...")
