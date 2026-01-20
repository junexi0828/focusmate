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
   ```

### C. Basic Controls
| Action | Command |
| :--- | :--- |
| **Check Status** | `sudo docker ps` |
| **View Logs** | `sudo docker-compose -f docker-compose.nas.yml logs -f backend` |
| **Stop All** | `sudo docker-compose -f docker-compose.nas.yml down` |
| **Start All** | `sudo docker-compose -f docker-compose.nas.yml up -d` |

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
