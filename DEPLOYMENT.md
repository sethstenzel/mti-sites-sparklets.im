# Sparklets.IM VPS Deployment Guide

This guide walks you through deploying Sparklets.IM on your VPS alongside the existing sethstenzel.me application.

## Prerequisites

- VPS running Ubuntu/Debian
- Nginx already installed and configured
- Certbot installed for SSL
- `appsuser` account exists
- DNS records pointing to your VPS:
  - `sparklets.im` → Your VPS IP
  - `www.sparklets.im` → Your VPS IP

## Architecture Overview

```
Internet → Nginx (443/HTTPS)
           ├─ sparklets.im/api → Backend (127.0.0.1:18002)
           ├─ sparklets.im/contents → Static uploads
           └─ sparklets.im/ → Frontend (Vue dist/)

Existing:
           └─ sethstenzel.me → Your existing app (18001)
```

## Deployment Steps

### 1. Initial Setup on VPS

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Create directory structure
sudo mkdir -p /var/www/sparklets.im/{backend,frontend,logs,deployment}
sudo mkdir -p /var/www/sparklets.im/backend/contents/imgs
sudo chown -R appsuser:appsuser /var/www/sparklets.im

# Create certbot directory if it doesn't exist
sudo mkdir -p /var/www/certbot
```

### 2. Clone Repository

```bash
# Switch to appsuser
sudo su - appsuser
cd /var/www/sparklets.im

# Clone your repository
git clone https://github.com/YOUR-USERNAME/mti-sites-sparklets.im.git tmp
mv tmp/backend/* backend/
mv tmp/frontend/* frontend/
mv tmp/deployment/* deployment/
rm -rf tmp
```

### 3. Setup Backend

```bash
cd /var/www/sparklets.im/backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync

# Create demo sparklet (optional)
uv run python seed_demo.py

# Test backend locally
uv run python main.py
# In another terminal: curl http://127.0.0.1:18002/health
# Should return: {"status":"healthy"}
# Press Ctrl+C to stop the test
```

### 4. Build Frontend

```bash
cd /var/www/sparklets.im/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Verify dist/ directory was created
ls -la dist/
```

### 5. Install Systemd Service

```bash
# Exit from appsuser
exit

# Copy service file
sudo cp /var/www/sparklets.im/deployment/sparklets-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable sparklets-backend
sudo systemctl start sparklets-backend

# Check status
sudo systemctl status sparklets-backend

# View logs
sudo journalctl -u sparklets-backend -n 50
```

### 6. Configure Nginx (Pre-SSL)

```bash
# Copy nginx config
sudo cp /var/www/sparklets.im/deployment/nginx-sparklets.im.conf /etc/nginx/sites-available/sparklets.im

# Enable site
sudo ln -s /etc/nginx/sites-available/sparklets.im /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 7. Obtain SSL Certificate

```bash
# Use certbot with webroot method
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d sparklets.im \
  -d www.sparklets.im \
  --email seth.c.stenzel@gmail.com \
  --agree-tos \
  --no-eff-email

# Certificate will be saved to:
# /etc/letsencrypt/live/sparklets.im/fullchain.pem
# /etc/letsencrypt/live/sparklets.im/privkey.pem
```

### 8. Enable HTTPS in Nginx

```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/sparklets.im

# Uncomment the entire HTTPS server block (lines starting with # server {)
# Remove the # from all lines in the HTTPS section

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 9. Verify Deployment

```bash
# Check backend health
curl https://sparklets.im/api/health

# Check demo sparklet
curl https://sparklets.im/api/sparklets/1

# Visit in browser
# https://sparklets.im - Should show homepage
# https://sparklets.im/sparklet/1 - Should show demo sparklet
# https://sparklets.im/create - Should show create form
```

## Using the Deployment Script

After initial setup, use the deployment script for updates:

```bash
# Make script executable
chmod +x /var/www/sparklets.im/deployment/deploy.sh

# View status
./deployment/deploy.sh status

# View logs
./deployment/deploy.sh logs

# Restart service
./deployment/deploy.sh restart

# Update from git (pull latest changes)
./deployment/deploy.sh update
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u sparklets-backend -n 100

# Check if port 18002 is already in use
sudo lsof -i :18002

# Check file permissions
ls -la /var/www/sparklets.im/backend/
ls -la /var/www/sparklets.im/backend/contents/
```

### Frontend shows blank page

```bash
# Check if dist/ directory exists
ls -la /var/www/sparklets.im/frontend/dist/

# Rebuild frontend
cd /var/www/sparklets.im/frontend
npm run build

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### SSL certificate issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --dry-run

# Check nginx SSL configuration
sudo nginx -t
```

### API calls failing

```bash
# Check CORS settings in backend/main.py
# Verify ALLOWED_ORIGINS in systemd service file

# Test backend directly
curl http://127.0.0.1:18002/api/health

# Check nginx proxy configuration
sudo nginx -t
sudo tail -f /var/log/nginx/access.log
```

### File upload not working

```bash
# Check directory permissions
ls -la /var/www/sparklets.im/backend/contents/imgs/

# Fix permissions if needed
sudo chown -R appsuser:appsuser /var/www/sparklets.im/backend/contents
sudo chmod -R 755 /var/www/sparklets.im/backend/contents
```

## Monitoring

### View Backend Logs

```bash
# Real-time logs
sudo journalctl -u sparklets-backend -f

# Last 100 lines
sudo journalctl -u sparklets-backend -n 100

# Since specific time
sudo journalctl -u sparklets-backend --since "1 hour ago"
```

### View Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log

# Filter for sparklets.im
sudo tail -f /var/log/nginx/access.log | grep sparklets
```

### Check Service Status

```bash
# Backend status
sudo systemctl status sparklets-backend

# Nginx status
sudo systemctl status nginx

# Check if backend is responding
curl -I https://sparklets.im/api/health
```

## Maintenance

### Update Application

```bash
cd /var/www/sparklets.im

# Pull latest changes
sudo -u appsuser git pull origin main

# Update backend
cd backend
sudo -u appsuser .venv/bin/uv sync

# Rebuild frontend
cd ../frontend
npm install
npm run build

# Restart backend
sudo systemctl restart sparklets-backend
```

### Backup Database

```bash
# Backup SQLite database
sudo cp /var/www/sparklets.im/backend/sparklets.sqlite \
       /var/www/sparklets.im/backend/sparklets.sqlite.backup-$(date +%Y%m%d)

# Backup uploaded images
sudo tar -czf /var/www/sparklets.im/contents-backup-$(date +%Y%m%d).tar.gz \
       /var/www/sparklets.im/backend/contents/
```

### SSL Certificate Renewal

Certbot should auto-renew. To manually renew:

```bash
# Test renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal

# Reload nginx after renewal
sudo systemctl reload nginx
```

## Security Checklist

- [x] Backend runs as non-root user (`appsuser`)
- [x] SQLite database has proper permissions
- [x] Upload directory is writable only by backend
- [x] CORS restricted to production domain
- [x] SSL/TLS certificates from Let's Encrypt
- [x] Security headers in nginx config
- [x] Nginx serves frontend as static files
- [x] Backend only accessible via nginx proxy

## Port Reference

| Service | Internal Port | External Access |
|---------|--------------|-----------------|
| Sparklets Backend | 127.0.0.1:18002 | Via nginx proxy only |
| Sparklets Frontend | N/A (static files) | Via nginx on 443 |
| sethstenzel.me | 127.0.0.1:18001 | Via nginx on 443 |
| Nginx HTTPS | 0.0.0.0:443 | Public |
| Nginx HTTP | 0.0.0.0:80 | Public (redirects to 443) |

## Support

For issues specific to:
- **Deployment**: Check this guide's troubleshooting section
- **Backend API**: See [backend/README.md](../backend/README.md)
- **Frontend**: See [frontend/README.md](../frontend/README.md)
- **Nginx**: Check `/var/log/nginx/error.log`
- **Systemd**: Check `sudo journalctl -u sparklets-backend`
