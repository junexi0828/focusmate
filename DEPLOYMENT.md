# FocusMate Deployment Guide

Complete guide for deploying FocusMate to production with GitHub Actions, Docker Hub, monitoring, and load balancing.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Actions Setup](#github-actions-setup)
3. [Docker Hub Setup](#docker-hub-setup)
4. [Slack Notifications](#slack-notifications)
5. [Production Deployment](#production-deployment)
6. [Monitoring Setup](#monitoring-setup)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Maintenance](#maintenance)

## Prerequisites

- Docker and Docker Compose installed
- GitHub account with repository
- Docker Hub account
- Slack workspace (for notifications)
- Domain name (for production)
- Server with at least 4GB RAM, 2 CPU cores

## GitHub Actions Setup

### 1. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password-or-token
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2. CI/CD Pipeline

The CI/CD pipeline is already configured in `.github/workflows/ci-cd.yml`:

- **On Push to `main` or `develop`**: Runs tests, builds Docker image, pushes to Docker Hub
- **On Pull Request**: Runs tests only
- **Security Scan**: Trivy vulnerability scanner on main branch

### 3. Workflow Stages

1. **Test**: Runs unit, integration tests with PostgreSQL and Redis
2. **Build**: Builds Docker image and pushes to Docker Hub
3. **Security**: Scans for vulnerabilities

## Docker Hub Setup

### 1. Create Docker Hub Account

Visit https://hub.docker.com and create an account

### 2. Create Repository

```bash
# Create a repository named: focusmate-backend
# Set it to public or private based on your needs
```

### 3. Generate Access Token

1. Go to Account Settings → Security → Access Tokens
2. Create new token with Read/Write permissions
3. Add token to GitHub Secrets as `DOCKER_PASSWORD`

## Slack Notifications

### 1. Create Slack Webhook

1. Go to https://api.slack.com/apps
2. Create new app → "From scratch"
3. Select your workspace
4. Go to "Incoming Webhooks" → Enable
5. Click "Add New Webhook to Workspace"
6. Select channel for notifications
7. Copy the Webhook URL

### 2. Configure Webhook

Add webhook URL to:
- GitHub Secrets: `SLACK_WEBHOOK_URL`
- Production `.env`: `SLACK_WEBHOOK_URL`

### 3. Test Notifications

```python
# Test from backend
from app.infrastructure.monitoring.slack_notifier import slack_notifier

await slack_notifier.send_message("Test notification from FocusMate!")
```

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create deployment directory
mkdir -p /opt/focusmate
cd /opt/focusmate
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.production.example .env.production

# Edit environment variables
nano .env.production
```

**CRITICAL: Change these values:**
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `POSTGRES_PASSWORD`: Strong password
- `REDIS_PASSWORD`: Strong password
- `TRUSTED_HOSTS`: Your domain names
- `CORS_ORIGINS`: Your frontend URLs
- `SLACK_WEBHOOK_URL`: Your Slack webhook
- `GRAFANA_ADMIN_PASSWORD`: Strong password

### 3. Deploy Services

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Initialize Database

```bash
# Run migrations
docker exec focus-mate-backend-1 alembic upgrade head

# Verify database
docker exec -it focus-mate-postgres psql -U postgres -d focus_mate -c "\dt"
```

## Monitoring Setup

### 1. Access Monitoring Dashboards

- **Grafana**: http://your-server:3001 (admin/your-password)
- **Prometheus**: http://your-server:9090 (internal)

### 2. Configure Grafana Dashboards

1. Login to Grafana
2. Go to Dashboards → Import
3. Import these dashboard IDs:
   - FastAPI Dashboard: `13451`
   - PostgreSQL: `9628`
   - Redis: `11835`
   - Node Exporter: `1860`
   - Docker Containers: `193`

### 3. Set Up Alerts

Prometheus alerts are configured in `monitoring/prometheus/alert_rules.yml`:

- High error rate (>5%)
- High response time (>1s)
- Service down
- Database issues

Alerts will be sent to Slack webhook automatically.

### 4. Metrics Endpoints

- Backend metrics: http://your-server/metrics
- Prometheus: http://your-server:9090
- Grafana: http://your-server:3001

## SSL Certificate Setup

### 1. Let's Encrypt (Production)

```bash
# Update nginx.conf with your domain
sed -i 's/server_name _;/server_name yourdomain.com www.yourdomain.com;/' nginx/nginx.conf

# Generate certificate
docker-compose -f docker-compose.prod.yml --profile ssl run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com

# Update nginx SSL paths in nginx.conf
# Uncomment the Let's Encrypt lines
# Comment out the self-signed lines

# Reload nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 2. Auto-Renewal

Certbot container automatically renews certificates every 12 hours.

## Load Balancing

The production setup includes:

- **3 Backend Instances**: backend-1, backend-2, backend-3
- **Nginx Load Balancer**: Least connections algorithm
- **Health Checks**: Automatic failover
- **Session Persistence**: Via Redis

### Scaling

Add more backend instances:

```yaml
# In docker-compose.prod.yml
backend-4:
  # ... same config as backend-1
```

Update nginx upstream:

```nginx
# In nginx/nginx.conf
upstream backend {
    server backend-4:8000 max_fails=3 fail_timeout=30s;
}
```

## Maintenance

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend-1

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Backup Database

```bash
# Create backup
docker exec focus-mate-postgres pg_dump -U postgres focus_mate > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i focus-mate-postgres psql -U postgres focus_mate < backup_20250122.sql
```

### Update Deployment

```bash
# Pull new images
docker-compose -f docker-compose.prod.yml pull

# Recreate services (zero-downtime with load balancer)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend-1
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend-2
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend-3
```

### Health Checks

```bash
# Application health
curl http://your-server/health

# Nginx status
curl http://your-server:8080/nginx-status

# Prometheus targets
curl http://your-server:9090/api/v1/targets
```

## Monitoring MCP Support

**Note**: Prometheus and Grafana don't have official MCP (Model Context Protocol) servers at this time. However, you can:

1. **Use Slack for AI-accessible alerts**: All alerts are sent to Slack, which can be integrated with Claude
2. **Export metrics via HTTP**: Prometheus exposes metrics at `/metrics` endpoint
3. **Custom MCP wrapper**: Build a simple MCP server wrapper around Prometheus API if needed

For now, Slack webhook integration provides the best monitoring visibility for AI systems.

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check container status
docker ps -a

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Database connection errors

```bash
# Check PostgreSQL
docker exec focus-mate-postgres pg_isready

# Check credentials
docker exec focus-mate-postgres psql -U postgres -c "SELECT version();"
```

### High memory usage

```bash
# Check resource usage
docker stats

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend-1
```

## Production Checklist

- [ ] Changed all passwords in `.env.production`
- [ ] Configured `TRUSTED_HOSTS` with your domains
- [ ] Set up Slack webhook
- [ ] Configured SSL certificates
- [ ] Set up database backups
- [ ] Configured Grafana dashboards
- [ ] Tested health endpoints
- [ ] Verified load balancing
- [ ] Set up monitoring alerts
- [ ] Documented custom configurations

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/focusmate/issues
- Slack Channel: #focusmate-support
