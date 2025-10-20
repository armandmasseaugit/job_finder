#!/bin/bash
# ============================================================================
# ChromaDB Installation Script for Azure Ubuntu VM
# ============================================================================
# This script installs and configures ChromaDB server on Ubuntu 22.04
# It will be executed during VM provisioning

set -e  # Exit on any error

# Update system
echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv software-properties-common

# Create chromadb user
echo "👤 Creating chromadb user..."
sudo useradd -m -s /bin/bash chromadb
sudo usermod -aG sudo chromadb

# Create directories
echo "📁 Creating directories..."
sudo mkdir -p /opt/chromadb
sudo mkdir -p /var/lib/chromadb
sudo mkdir -p /var/log/chromadb
sudo chown -R chromadb:chromadb /opt/chromadb /var/lib/chromadb /var/log/chromadb

# Install ChromaDB
echo "🔧 Installing ChromaDB..."
sudo -u chromadb python3.11 -m venv /opt/chromadb/venv
sudo -u chromadb /opt/chromadb/venv/bin/pip install --upgrade pip
sudo -u chromadb /opt/chromadb/venv/bin/pip install chromadb[server] uvicorn

# Create ChromaDB configuration
echo "⚙️ Creating ChromaDB configuration..."
sudo tee /opt/chromadb/config.yaml > /dev/null <<EOF
# ChromaDB Server Configuration
server:
  host: "0.0.0.0"
  port: 8000
  log_config: "/opt/chromadb/logging.yaml"

# Authentication (disabled for now, can be enabled later)
chroma_server_auth_provider: ""

# Database settings
chroma_db_impl: "chromadb.db.duckdb.DuckDB"
persist_directory: "/var/lib/chromadb/data"

# Performance settings
chroma_server_cors_allow_origins: ["*"]
anonymized_telemetry: false

# Logging
chroma_server_host: "0.0.0.0"
chroma_server_http_port: 8000
EOF

# Create logging configuration
echo "📝 Creating logging configuration..."
sudo tee /opt/chromadb/logging.yaml > /dev/null <<EOF
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout
  
  file:
    class: logging.FileHandler
    level: INFO
    formatter: default
    filename: /var/log/chromadb/chromadb.log

loggers:
  chromadb:
    level: INFO
    handlers: [console, file]
    propagate: no

root:
  level: INFO
  handlers: [console, file]
EOF

# Create startup script
echo "🚀 Creating startup script..."
sudo tee /opt/chromadb/start.sh > /dev/null <<'EOF'
#!/bin/bash
# ChromaDB Startup Script

export PYTHONPATH=/opt/chromadb
export CHROMA_SERVER_AUTH_PROVIDER=""
export PERSIST_DIRECTORY="/var/lib/chromadb/data"

# Create data directory if it doesn't exist
mkdir -p "$PERSIST_DIRECTORY"

# Start ChromaDB server
cd /opt/chromadb
exec ./venv/bin/python -m uvicorn chromadb.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-config logging.yaml \
    --access-log
EOF

sudo chmod +x /opt/chromadb/start.sh
sudo chown chromadb:chromadb /opt/chromadb/start.sh

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/chromadb.service > /dev/null <<EOF
[Unit]
Description=ChromaDB Vector Database Server
After=network.target
Wants=network-online.target

[Service]
Type=exec
User=chromadb
Group=chromadb
WorkingDirectory=/opt/chromadb
ExecStart=/opt/chromadb/start.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=chromadb

# Environment
Environment=PYTHONPATH=/opt/chromadb
Environment=PERSIST_DIRECTORY=/var/lib/chromadb/data
Environment=CHROMA_SERVER_AUTH_PROVIDER=""

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/chromadb /var/log/chromadb

[Install]
WantedBy=multi-user.target
EOF

# Install and configure nginx (reverse proxy + health checks)
echo "🌐 Installing nginx..."
sudo apt install -y nginx

sudo tee /etc/nginx/sites-available/chromadb > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/api/v1/heartbeat;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Main ChromaDB API (optional - direct access on port 8000 is preferred)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Status page
    location / {
        return 200 'ChromaDB Server is running. Access API at port 8000.';
        add_header Content-Type text/plain;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/chromadb /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP health checks
sudo ufw allow 8000/tcp # ChromaDB
sudo ufw --force enable

# Enable and start services
echo "🎬 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable chromadb
sudo systemctl enable nginx

# Start ChromaDB
sudo systemctl start chromadb
sleep 5

# Start nginx
sudo systemctl start nginx

# Verify installation
echo "✅ Verifying installation..."
sudo systemctl status chromadb --no-pager
sudo systemctl status nginx --no-pager

# Test ChromaDB
echo "🧪 Testing ChromaDB..."
sleep 10
curl -f http://localhost:8000/api/v1/heartbeat || echo "❌ ChromaDB not responding"
curl -f http://localhost/health || echo "❌ Health check failed"

# Display status
echo ""
echo "🎉 ChromaDB Installation Complete!"
echo "=================================="
echo "ChromaDB Server: http://$(curl -s ifconfig.me):8000"
echo "Health Check: http://$(curl -s ifconfig.me)/health"
echo "Data Directory: /var/lib/chromadb/data"
echo "Logs: /var/log/chromadb/chromadb.log"
echo ""
echo "Commands:"
echo "- Check status: sudo systemctl status chromadb"
echo "- View logs: sudo journalctl -u chromadb -f"
echo "- Restart: sudo systemctl restart chromadb"
echo ""
echo "Connect from Python:"
echo "import chromadb"
echo "client = chromadb.HttpClient(host='$(curl -s ifconfig.me)', port=8000)"
echo ""