import os
import sys
import subprocess
import re
import time
import argparse
from pathlib import Path

# Add project root to sys.path to handle potential imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

def load_env():
    """Load environment variables from backend/.env"""
    env_path = PROJECT_ROOT / "backend" / ".env"
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return {}

    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

def fetch_logs(nas_user, nas_ip, log_file, lines=100):
    """Fetch recent logs from NAS without tailing."""
    print(f"� Fetching last {lines} lines from NAS log...")
    ssh_cmd = [
        "ssh",
        "-o", "ConnectTimeout=5",
        f"{nas_user}@{nas_ip}",
        f"tail -n {lines} {log_file}"
    ]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch logs: {e.stderr}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="FocusMate Auto-Debug Watcher")
    parser.add_argument("--fetch", action="store_true", help="Fetch recent logs and exit (non-interactive)")
    parser.add_argument("--lines", type=int, default=100, help="Number of lines to fetch")
    args = parser.parse_args()

    env = load_env()
    nas_user = env.get("NAS_USER", "juns")
    nas_ip = env.get("NAS_IP", "192.168.45.58")
    log_file = "/volume1/web/focusmate-backend/logs/app.log"

    if args.fetch:
        logs = fetch_logs(nas_user, nas_ip, log_file, args.lines)
        if logs:
            print("\n--- NAS LOG START ---")
            print(logs)
            print("--- NAS LOG END ---\n")
        return

    print("🚀 Starting FocusMate Auto-Debug Watcher (Mac Local)...")

    print(f"📡 Connecting to {nas_user}@{nas_ip}...")
    print(f"📜 Tailing log: {log_file}")

    # SSH Command to tail the log
    # Using -o ConnectTimeout to fail fast
    ssh_cmd = [
        "ssh",
        "-o", "ConnectTimeout=5",
        f"{nas_user}@{nas_ip}",
        f"tail -n 0 -F {log_file}"
    ]

    try:
        process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    print("❌ SSH connection lost.")
                    break
                continue

            line = line.strip()
            # Detect Error patterns
            if "[ERROR]" in line or "[CRITICAL]" in line or "Traceback" in line:
                print("\n" + "!" * 50)
                print("🐞 ERROR DETECTED ON NAS")
                print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Log: {line}")

                # Check for Traceback context in subsequent lines if needed
                # (Simple version: just alert the user to look at the agent)
                print("!" * 50 + "\n")

                # Highlight for Antigravity (the agent)
                if "request_id=" in line:
                    req_id = re.search(r"request_id=([a-f0-9-]+)", line)
                    if req_id:
                        print(f"🔍 Context: Request ID {req_id.group(1)}")

    except KeyboardInterrupt:
        print("\n👋 Stopping watcher...")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()
