import os
import sys
import time
import subprocess
import json
import httpx
import asyncio
import re
from pathlib import Path
from datetime import datetime, timedelta

# Add root to sys.path
SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
sys.path.append(str(BACKEND_DIR))

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
LOG_FILE = os.environ.get("LOG_FILE", "/volume1/web/focusmate-backend/logs/app.log")
ERROR_PATTERNS = [
    "sqlalchemy.exc.TimeoutError",
    "DatabaseError",
    "ConnectionError",
    "CRITICAL",
    "ERROR"
]

# Debounce settings
DEBOUNCE_INTERVAL = 600  # 10 minutes in seconds
SENT_ALERTS = {}         # key -> timestamp

def get_alert_key(line: str) -> str:
    """Create a unique key for the error to prevent redundant alerts.

    Extracts request_id if available, otherwise creates a fingerprint by
    removing timestamps and variable IDs.
    """
    # Try to extract request_id
    request_id_match = re.search(r"request_id=([a-f0-9-]+)", line)
    if request_id_match:
        return f"req_{request_id_match.group(1)}"

    # Otherwise, create a fingerprint:
    # 1. Remove date/time (YYYY-MM-DD HH:MM:SS,ms)
    fingerprint = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}", "", line)
    # 2. Remove memory addresses (0x...)
    fingerprint = re.sub(r"0x[a-fA-F0-9]+", "", fingerprint)
    # 3. Remove UUID-like strings
    fingerprint = re.sub(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", "", fingerprint)

    return fingerprint.strip()

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

    try:
        async with httpx.AsyncClient() as client:
            await client.post(SLACK_WEBHOOK_URL, json=payload, timeout=10.0)
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")

async def tail_f(filename):
    if not os.path.exists(filename):
        print(f"Log file {filename} not found.")
        return

    process = subprocess.Popen(['tail', '-F', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print(f"Monitoring logs: {filename} (Debounce: {DEBOUNCE_INTERVAL}s)...")

    last_cleanup = time.time()

    # Process lines
    while True:
        line = process.stdout.readline()
        if not line:
            await asyncio.sleep(0.1)
            continue

        for pattern in ERROR_PATTERNS:
            if pattern in line:
                key = get_alert_key(line)
                now = time.time()

                # Check debounce
                if key in SENT_ALERTS:
                    last_sent = SENT_ALERTS[key]
                    if now - last_sent < DEBOUNCE_INTERVAL:
                        # Skip redundant alert
                        break

                # Update cache and send
                SENT_ALERTS[key] = now
                print(f"Match found (sending): {line.strip()}")
                await send_slack(line.strip())
                break

        # Periodic cleanup of old cache entries
        if time.time() - last_cleanup > 3600:
            expired = [k for k, v in SENT_ALERTS.items() if time.time() - v > DEBOUNCE_INTERVAL]
            for k in expired:
                del SENT_ALERTS[k]
            last_cleanup = time.time()

if __name__ == "__main__":
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set.")
        sys.exit(1)

    try:
        asyncio.run(tail_f(LOG_FILE))
    except KeyboardInterrupt:
        print("Stopping log monitor...")
