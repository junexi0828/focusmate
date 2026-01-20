# Docker Operation Manual (Hybrid Deployment)

Use this manual for daily operations and troubleshooting of the FocusMate backend on Synology NAS.

## 1. Architecture Overview: Hybrid Deployment
We use a **Hybrid Docker Strategy** to balance stability and deployment speed.

| Component | Handled By | How it Updates |
| :--- | :--- | :--- |
| **OS / Python / Dependencies** | Docker Image (`focusmate-backend:latest`) | Rebuild Image & Re-deploy |
| **Application Code** | Volume Mount (`/volume1/web/...:/app`) | `git pull` & Restart Container |
| **Database / Redis** | Independent Services (Supabase / Docker Redis) | Configuration / Docker |

---

## 2. Daily Operations Runbook

### A. Deploying Code Changes (Routine Update)
When you only change Python code (`.py`), templates, or `docker-compose.nas.yml`.

1. **Local Machine**: Push changes to GitHub.
   ```bash
   git push origin main
   ```

2. **NAS Terminal (SSH)**: Pull code and restart container.
   ```bash
   # 1. Update Code
   cd /volume1/web/focusmate-backend
   sudo git pull

   # 2. Restart Backend (Takes ~5 seconds)
   sudo docker-compose -f docker-compose.nas.yml restart backend
   ```

### B. Updating Dependencies (Heavy Update)
When you change `requirements.txt` or `Dockerfile`.

1. **Local Machine**: Build and Transfer new image.
   ```bash
   # 1. Build
   docker build -t focusmate-backend:latest -f backend/Dockerfile.nas backend/

   # 2. Save to file
   docker save -o focusmate-backend.tar focusmate-backend:latest

   # 3. Transfer to NAS
   rsync -avz --progress focusmate-backend.tar juns@192.168.45.58:/volume1/docker/
   ```

2. **NAS Terminal (SSH)**: Load image and recreate container.
   ```bash
   cd /volume1/web/focusmate-backend

   # 1. Remove old container
   sudo docker-compose -f docker-compose.nas.yml down

   # 2. Load new image
   sudo docker load -i /volume1/docker/focusmate-backend.tar

   # 3. Start up
   sudo docker-compose -f docker-compose.nas.yml up -d
   sudo docker-compose -f docker-compose.nas.yml restart backend
   ```

### A-2. Manual Deployment (When Git Auth Fails)
If `git pull` fails on NAS due to authentication/password issues, use **Rsync** or **SCP** from your local machine.

#### Option 1: Full Code Sync (Recommended)
Use the provided script or `rsync` to overwrite NAS code with local code.
1. **Run locally (Mac)**:
   ```bash
   # Option A: Use Script (Safe, Excludes venv/logs)
   ./backend/deploy-nas.sh

   # Option B: Manual Rsync Command
   rsync -avz --progress \
     --exclude 'venv' --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' \
     --exclude '.git' --exclude '.DS_Store' --exclude 'logs' \
     backend/ juns@192.168.45.58:/volume1/web/focusmate-backend/
   ```
2. **Restart on NAS**:
   ```bash
   sudo docker-compose -f docker-compose.nas.yml restart backend
   ```

#### Option 2: Single Config File Update (SCP)
If `scp` fails (Synology default), use **SSH Pipe** to transfer a single file (e.g., `docker-compose.nas.yml`).
1. **Run locally (Mac)**:
   ```bash
   # Syntax: cat [LocalFile] | ssh [User]@[Host] "cat > [RemoteFile]"
   cat backend/docker-compose.nas.yml | ssh juns@192.168.45.58 "cat > /volume1/web/focusmate-backend/docker-compose.nas.yml"
   ```
2. **Apply Config on NAS** (Important: restart won't apply config changes):
   ```bash
   sudo docker-compose -f docker-compose.nas.yml up -d
   ```

### C. Command Reference (Cheat Sheet)

#### 1. Docker Operations (Run on NAS)
| Category | Command | Description |
| :--- | :--- | :--- |
| **Lifecycle** | `sudo docker-compose -f docker-compose.nas.yml up -d` | Start/Update containers (Recreates if config changed) |
| | `sudo docker-compose -f docker-compose.nas.yml down` | Stop and remove containers |
| | `sudo docker-compose -f docker-compose.nas.yml restart [service]` | Simple restart (No config changes applied) |
| **Inspection** | `sudo docker ps` | Show running containers |
| | `sudo docker-compose -f docker-compose.nas.yml logs -f [service]` | Stream logs (Ctrl+C to exit) |
| | `sudo docker logs --tail 100 focusmate-backend` | View last 100 lines of specific container |
| **Debugging** | `sudo docker exec -it focusmate-backend /bin/bash` | **Enter container shell** (Run commands inside) |
| | `sudo docker stats` | Live CPU/Memory usage stats |
| | `sudo docker network inspect focusmate-network` | Inspect network connections |
| **Cleanup** | `sudo docker system prune -a` | Delete unused images/containers (Free up space) |

#### 2. File Transfer Tools (Run on Mac)
Use these when you need to move files manually without our scripts.

**RSYNC** (Smart Synchronization)
*   **Best for:** Syncing entire folders, codebases. Only sends changed parts.
*   **Syntax:** `rsync [options] [Source] [Destination]`
*   **Example**:
    ```bash
    # Sync local 'backend' folder to NAS (recursively)
    rsync -avz backend/ juns@192.168.45.58:/volume1/web/focusmate-backend/
    ```
    *   `-a`: Archive mode (preserve permissions/dates)
    *   `-v`: Verbose (show progress)
    *   `-z`: Compress (faster over network)

**SCP** (Secure Copy)
*   **Best for:** Sending a single file quickly.
*   **Syntax:** `scp [SourceFile] [User]@[Host]:[RemotePath]`
*   **Example**:
    ```bash
    # Send a config file to NAS
    scp .env juns@192.168.45.58:/volume1/web/focusmate-backend/.env
    ```

**SSH Pipe** (When SCP is disabled)
*   **Best for:** Bypassing restrictions or writing text directly.
*   **Syntax:** `cat [LocalFile] | ssh [Remote] "cat > [Destination]"`

---

## 3. Troubleshooting Guide (FAQ)
Solutions to errors encountered during the migration.

### Q1. `ModuleNotFoundError: No module named '...'`
**Cause**: The file exists in Git/Local but not inside the Docker container.
**Solution**:
1. Run `ls` inside container to check:
   ```bash
   sudo docker exec focusmate-backend ls -R /app/app
   ```
2. If file missing: Run `sudo git pull` on NAS.
3. If file visible but error persists: Check for missing `__init__.py`.
   *   **Fix**: Create `__init__.py` locally → Push → Pull on NAS → Restart.

### Q2. `bind: address already in use` (Port 6379 / 8000)
**Cause**: An old process (system Redis or zombie python script) is holding the port.
**Solution**:
1. Find the culprit process:
   ```bash
   sudo netstat -tlnp | grep 6379  # For Redis
   ```
2. Kill it:
   ```bash
   # Ideally stop the service
   sudo synoservice --stop pkgctl-Redis

   # Or force kill
   sudo pkill redis-server
   sudo kill -9 <PID>
   ```
3. Start Docker again: `up -d`

### Q3. `failed to mount local volume: no such file or directory`
**Cause**: Docker bind mounts (like `./redis-data:/data`) require the host directory to exist *before* starting.
**Solution**:
1. Create directory manually:
   ```bash
   mkdir -p redis-data
   ```
2. Start Docker again.

### Q4. `Permission denied` inside container
**Cause**: Files pulled via `git` on Synology sometimes have restrictive permissions (only owner readable).
**Solution**:
1. Grant read/execute permissions to everyone:
   ```bash
   sudo chmod -R 755 /volume1/web/focusmate-backend
   ```
2. Restart container.

### Q5. `git push` hangs or fails (Large File)
**Cause**: Accidentally committed a large `.tar` file (>100MB).
**Solution**:
1. Remove valid from git tracking (keep local file):
   ```bash
   git rm --cached focusmate-backend.tar
   ```
2. Add to `.gitignore`.
3. Commit and push again.
