# Deployment Guide - Clinical Protocol AI

## Overview

This guide covers deploying Clinical Protocol AI in various environments, from development to production.

## Development Deployment

### Quick Start (Recommended)
```bash
# Use provided batch files
start-backend-simple.bat
start-frontend-simple.bat
```

### Manual Setup
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm start
```

**Access**: http://localhost:3000

## Production Deployment

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama with Llama 3.1
- Reverse proxy (nginx/Apache)
- SSL certificate

### Backend Production Setup

#### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
pip install gunicorn
```

#### 2. Environment Configuration
Create `.env` file:
```env
OLLAMA_URL=http://localhost:11434
MODEL=llama3.1:latest
CHROMA_DB_PATH=/var/lib/clinical-ai/chroma_db
LOG_LEVEL=INFO
```

#### 3. Run with Gunicorn
```bash
gunicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-logfile /var/log/clinical-ai/access.log \
  --error-logfile /var/log/clinical-ai/error.log
```

#### 4. Systemd Service (Linux)
Create `/etc/systemd/system/clinical-ai-backend.service`:
```ini
[Unit]
Description=Clinical Protocol AI Backend
After=network.target

[Service]
Type=exec
User=clinical-ai
Group=clinical-ai
WorkingDirectory=/opt/clinical-protocol-ai/backend
Environment=PATH=/opt/clinical-protocol-ai/venv/bin
ExecStart=/opt/clinical-protocol-ai/venv/bin/gunicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable clinical-ai-backend
sudo systemctl start clinical-ai-backend
```

### Frontend Production Setup

#### 1. Build for Production
```bash
cd frontend
npm install
npm run build
```

#### 2. Serve Static Files
The `build/` directory contains optimized static files. Serve with nginx or Apache.

### Nginx Configuration

#### Complete nginx config (`/etc/nginx/sites-available/clinical-ai`):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;

    # Frontend static files
    location / {
        root /opt/clinical-protocol-ai/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for long operations
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/clinical-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker Deployment

### Dockerfile (Backend)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

### Dockerfile (Frontend)
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### Using EC2
1. Launch EC2 instance (t3.large or larger)
2. Install Docker and Docker Compose
3. Clone repository and run docker-compose
4. Configure security groups (ports 80, 443)
5. Set up Application Load Balancer
6. Configure Route 53 for domain

#### Using ECS
1. Create ECS cluster
2. Build and push images to ECR
3. Create task definitions
4. Set up ALB and target groups
5. Configure auto-scaling

### Azure Deployment

#### Using Container Instances
```bash
# Create resource group
az group create --name clinical-ai-rg --location eastus

# Deploy containers
az container create \
  --resource-group clinical-ai-rg \
  --name clinical-ai \
  --image your-registry/clinical-ai:latest \
  --ports 80 443 \
  --dns-name-label clinical-ai-app
```

### Google Cloud Deployment

#### Using Cloud Run
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/clinical-ai

# Deploy to Cloud Run
gcloud run deploy clinical-ai \
  --image gcr.io/PROJECT-ID/clinical-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

### Backend Environment Variables
```env
# LLM Configuration
OLLAMA_URL=http://localhost:11434
MODEL=llama3.1:latest

# Database
CHROMA_DB_PATH=/var/lib/clinical-ai/chroma_db

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/clinical-ai/app.log

# Security
CORS_ORIGINS=https://your-domain.com
MAX_FILE_SIZE=50MB

# Performance
WORKER_TIMEOUT=300
MAX_WORKERS=4
```

### Frontend Environment Variables
```env
# API Configuration
REACT_APP_API_URL=https://api.your-domain.com

# Features
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_FEEDBACK=true

# Build Configuration
GENERATE_SOURCEMAP=false
```

## Monitoring and Logging

### Backend Logging
```python
# Configure in main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/clinical-ai/app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks
```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:3000/
```

### Monitoring with Prometheus
Add metrics endpoint to backend:
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Security Considerations

### SSL/TLS
- Use Let's Encrypt for free SSL certificates
- Configure strong cipher suites
- Enable HSTS headers

### Firewall
```bash
# UFW configuration
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Application Security
- Validate all inputs
- Implement rate limiting
- Use secure headers
- Regular security updates

## Backup and Recovery

### Database Backup
```bash
# Backup ChromaDB
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz /var/lib/clinical-ai/chroma_db

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/clinical-ai"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/chroma_$DATE.tar.gz /var/lib/clinical-ai/chroma_db

# Keep only last 7 days
find $BACKUP_DIR -name "chroma_*.tar.gz" -mtime +7 -delete
```

### Application Backup
```bash
# Backup application code and config
tar -czf app_backup_$(date +%Y%m%d).tar.gz \
  /opt/clinical-protocol-ai \
  /etc/nginx/sites-available/clinical-ai \
  /etc/systemd/system/clinical-ai-backend.service
```

## Troubleshooting

### Common Issues
1. **Ollama Connection**: Ensure Ollama is running and accessible
2. **Memory Issues**: Increase server memory or reduce worker count
3. **Timeout Errors**: Increase proxy timeout settings
4. **CORS Errors**: Check CORS configuration in backend

### Log Analysis
```bash
# Backend logs
tail -f /var/log/clinical-ai/app.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u clinical-ai-backend -f
```

## Performance Optimization

### Backend Optimization
- Use connection pooling
- Implement caching
- Optimize database queries
- Use async operations

### Frontend Optimization
- Enable gzip compression
- Use CDN for static assets
- Implement code splitting
- Optimize images

### Infrastructure Optimization
- Use load balancers
- Implement auto-scaling
- Use caching layers (Redis)
- Monitor resource usage

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor disk space
- Review logs
- Test backups
- Security updates

### Update Process
```bash
# Backend updates
cd /opt/clinical-protocol-ai/backend
git pull
pip install -r requirements.txt
sudo systemctl restart clinical-ai-backend

# Frontend updates
cd /opt/clinical-protocol-ai/frontend
git pull
npm install
npm run build
sudo systemctl reload nginx
```