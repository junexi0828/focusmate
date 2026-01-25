# NAS Performance Incident Report & Resolution Plan

> **Date:** 2026-01-26
> **Subject:** Solution for system hang caused by insufficient resources during NAS Docker Build

## 1. 🚨 Problem Definition
### Symptoms
*   **System Hang:** Backend login timeout, WebSocket connection failure.
*   **Resource Exhaustion:**
    *   **Memory:** Free memory dropped to **~116MB**.
    *   **Swap:** Swap usage spiked to **1.1GB** (Disk thrashing).
    *   **Disk I/O:** Load Average (I/O Wait) exceeded **10.0**.

### Root Cause
*   **"On-Device Build" Anti-pattern:**
    *   Currently, the NAS (low-power CPU, limited RAM) performs the heavy `docker build` process directly.
    *   `pip install`, layer extraction, and image compression are extremely I/O and CPU intensive.
    *   The NAS hardware (designed for file storage) cannot handle simultaneous Service Hosting + Image Building.

---

## 2. 🛠️ Immediate Countermeasure
*   **Action:** Full restart of Docker services.
*   **Effect:** Flushes the accumulated Swap memory and kills hanging zombie processes.
*   **Command:**
    ```bash
    docker-compose down && docker-compose up -d
    ```

---

## 3. 🚀 Future Solution: "Build-Ship-Run" Architecture
### Concept
Shift the burden of **"Building"** from the weak NAS to the powerful Development Machine (Mac). The NAS should **only** be responsible for **"Running"**.

### Proposed Workflow (Draft)

1.  **Local (Mac) - Build Phase:**
    *   Developer commits code.
    *   Local script builds the Docker image.
    *   *(Crucial)* Build for NAS architecture (usually `linux/amd64` or `linux/arm64`).
    ```bash
    docker buildx build --platform linux/amd64 -t focusmate-backend:latest .
    ```

2.  **Transfer Phase (The "Rsync" Idea):**
    *   Save the built image to a tarball.
    *   Sync the **Image File** (not just code) to NAS via SSH/SCP/Rsync.
    ```bash
    docker save focusmate-backend:latest | gzip > focusmate-backend.tar.gz
    scp focusmate-backend.tar.gz juns@nas:/tmp/
    ```

3.  **Remote (NAS) - Run Phase:**
    *   NAS loads the pre-built image (almost 0 CPU cost).
    *   NAS restarts clean.
    ```bash
    ssh juns@nas "docker load < /tmp/focusmate_backend.tar.gz && docker-compose up -d"
    ```

### expected Benefits
| Feature | AS-IS (Current) | TO-BE (Proposed) |
| :--- | :--- | :--- |
| **Build Agent** | **NAS** (Slow, Low RAM) | **Mac** (Fast M-series Chip) |
| **NAS Load** | High (High risk of crash) | **Low** (Stable) |
| **Downtime** | 5~10 minutes (during build) | < 30 seconds (container swap) |
| **Stability** | Vulnerable to OOM (Out of Memory) | Guaranteed service stability |

---

## 4. Next Steps
- [ ] Create `scripts/deployment/build-and-deploy.sh` script on Mac.
- [ ] Verify NAS CPU architecture (`uname -m`).
- [ ] Disable automatic building in `docker-compose.nas.yml` on NAS (change `build: .` to `image: focusmate-backend:latest`).
