#!/bin/bash

# Sparklets.IM Deployment Script
# Usage: ./deploy.sh [install|update|restart|logs|status]

set -e

APP_DIR="/var/www/sparklets.im"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
SERVICE_NAME="sparklets-backend"
REPO_URL="https://github.com/yourusername/mti-sites-sparklets.im.git"  # Update with your repo URL

install() {
    echo "Installing Sparklets.IM..."

    # Create directories
    sudo mkdir -p $APP_DIR/{backend,frontend,logs}
    sudo mkdir -p $BACKEND_DIR/contents/imgs
    sudo chown -R appsuser:appsuser $APP_DIR

    # Clone repository
    cd /tmp
    git clone $REPO_URL sparklets-tmp

    # Copy files
    sudo -u appsuser cp -r sparklets-tmp/backend/* $BACKEND_DIR/
    sudo -u appsuser cp -r sparklets-tmp/frontend/* $FRONTEND_DIR/
    rm -rf sparklets-tmp

    # Setup backend
    cd $BACKEND_DIR
    sudo -u appsuser uv venv
    sudo -u appsuser $BACKEND_DIR/.venv/bin/uv sync
    sudo -u appsuser $BACKEND_DIR/.venv/bin/python seed_demo.py

    # Setup frontend
    cd $FRONTEND_DIR
    npm install
    npm run build

    # Install systemd service
    sudo cp $APP_DIR/deployment/sparklets-backend.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl start $SERVICE_NAME

    # Install nginx config
    sudo cp $APP_DIR/deployment/nginx-sparklets.im.conf /etc/nginx/sites-available/sparklets.im
    sudo ln -sf /etc/nginx/sites-available/sparklets.im /etc/nginx/sites-enabled/
    sudo nginx -t

    echo "✓ Installation complete!"
    echo "Next steps:"
    echo "1. Run: sudo certbot certonly --webroot -w /var/www/certbot -d sparklets.im -d www.sparklets.im"
    echo "2. Uncomment HTTPS section in /etc/nginx/sites-available/sparklets.im"
    echo "3. Run: sudo systemctl reload nginx"
}

update() {
    echo "Updating Sparklets.IM..."

    # Pull latest changes
    cd $BACKEND_DIR
    sudo -u appsuser git pull origin main

    # Update backend dependencies
    sudo -u appsuser $BACKEND_DIR/.venv/bin/uv sync

    # Rebuild frontend
    cd $FRONTEND_DIR
    npm install
    npm run build

    # Restart service
    sudo systemctl restart $SERVICE_NAME

    echo "✓ Update complete!"
    status
}

restart() {
    echo "Restarting Sparklets.IM backend..."
    sudo systemctl restart $SERVICE_NAME
    sleep 2
    status
}

logs() {
    echo "Showing Sparklets.IM logs (Ctrl+C to exit)..."
    sudo journalctl -u $SERVICE_NAME -f
}

status() {
    echo "Sparklets.IM Backend Status:"
    sudo systemctl status $SERVICE_NAME --no-pager

    echo ""
    echo "Health Check:"
    curl -s http://127.0.0.1:8000/health || echo "Backend not responding"
}

case "$1" in
    install)
        install
        ;;
    update)
        update
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {install|update|restart|logs|status}"
        exit 1
        ;;
esac
