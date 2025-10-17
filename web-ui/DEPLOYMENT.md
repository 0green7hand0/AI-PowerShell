# Deployment Guide - AI PowerShell Assistant Web UI

This guide covers deploying the AI PowerShell Assistant Web UI in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Methods](#deployment-methods)
  - [Docker Deployment](#docker-deployment)
  - [Manual Deployment](#manual-deployment)
  - [Nginx Deployment](#nginx-deployment)
- [Production Checklist](#production-checklist)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), Windows Server 2019+, or macOS
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space

### Software Requirements

- **Node.js**: 18.x or 20.x
- **Python**: 3.9+
- **Docker** (optional): 20.10+
- **Docker Compose** (optional): 2.0+
- **Nginx** (for manual deployment): 1.18+

## Environment Configuration

### Frontend Environment Variables

Create a `.env.production` file in the `web-ui` directory:

```env
# API Configuration
VITE_API_BASE_URL=http://your-domain.com
VITE_WS_URL=ws://your-domain.com

# Authentication
VITE_AUTH_ENABLED=false

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false
```

### Backend Environment Variables

Create a `.env` file in the `web-ui/backend` directory:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Authentication
AUTH_ENABLED=false
JWT_SECRET_KEY=your-jwt-secret-key-here

# CSRF Protection
CSRF_ENABLED=true

# Caching
CACHE_TYPE=RedisCache
CACHE_TIMEOUT=600
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=info

# Gunicorn
GUNICORN_WORKERS=4
```

## Deployment Methods

### Docker Deployment

Docker is the recommended deployment method for production.

#### 1. Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd web-ui

# Copy environment files
cp .env.production.example .env.production
cp backend/.env.example backend/.env

# Edit environment files with your configuration
nano .env.production
nano backend/.env

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### 2. Using Individual Dockerfiles

**Build Frontend:**
```bash
docker build -f Dockerfile.frontend -t ai-powershell-frontend .
docker run -d -p 80:80 --name frontend ai-powershell-frontend
```

**Build Backend:**
```bash
cd ..
docker build -f web-ui/Dockerfile.backend -t ai-powershell-backend .
docker run -d -p 5000:5000 --name backend ai-powershell-backend
```

### Manual Deployment

#### 1. Build the Application

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

**Windows:**
```powershell
.\build.ps1
```

#### 2. Deploy Frontend

The frontend build output is in the `dist` directory. Serve it with any static file server.

**Using Nginx:**
```bash
# Copy built files to nginx directory
sudo cp -r dist/* /var/www/html/

# Copy nginx configuration
sudo cp nginx.conf.example /etc/nginx/sites-available/ai-powershell-assistant
sudo ln -s /etc/nginx/sites-available/ai-powershell-assistant /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

#### 3. Deploy Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Start with gunicorn (Linux/macOS)
gunicorn -c gunicorn.conf.py wsgi:application

# Or use the start script
cd ..
./start-production.sh  # Linux/macOS
# or
.\start-production.ps1  # Windows
```

### Nginx Deployment

#### 1. Install Nginx

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nginx
```

**CentOS/RHEL:**
```bash
sudo yum install nginx
```

#### 2. Configure Nginx

```bash
# Copy configuration
sudo cp nginx.conf.example /etc/nginx/sites-available/ai-powershell-assistant

# Update paths in configuration
sudo nano /etc/nginx/sites-available/ai-powershell-assistant

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-powershell-assistant /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### 3. Enable HTTPS (Recommended)

**Using Let's Encrypt:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Production Checklist

### Security

- [ ] Change default `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Enable CSRF protection
- [ ] Configure firewall rules
- [ ] Set up authentication if needed
- [ ] Review and restrict CORS origins
- [ ] Disable debug mode
- [ ] Remove development dependencies

### Performance

- [ ] Enable Redis caching
- [ ] Configure CDN for static assets (optional)
- [ ] Enable Gzip/Brotli compression
- [ ] Set up load balancing (if needed)
- [ ] Configure appropriate worker count
- [ ] Set up database connection pooling

### Monitoring

- [ ] Set up application logging
- [ ] Configure log rotation
- [ ] Set up health check monitoring
- [ ] Configure alerting
- [ ] Set up performance monitoring (optional)

### Backup

- [ ] Configure database backups (if applicable)
- [ ] Back up configuration files
- [ ] Document recovery procedures

## Monitoring and Maintenance

### Health Checks

The application provides a health check endpoint:

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "success": true,
  "status": "healthy",
  "message": "AI PowerShell Assistant API is running",
  "version": "1.0.0"
}
```

### Logs

**Frontend Logs (Nginx):**
```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

**Backend Logs:**
```bash
# Application logs
tail -f backend/logs/app.log

# Gunicorn logs
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log
```

**Docker Logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Log Rotation

Configure logrotate for application logs:

```bash
sudo nano /etc/logrotate.d/ai-powershell-assistant
```

```
/var/log/ai-powershell-assistant/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

### Updates

**Docker Deployment:**
```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Clean up old images
docker image prune -f
```

**Manual Deployment:**
```bash
# Pull latest code
git pull

# Rebuild
./build.sh

# Restart services
sudo systemctl restart nginx
sudo systemctl restart ai-powershell-backend
```

## Troubleshooting

### Common Issues

#### 1. Frontend Not Loading

**Symptoms:** Blank page or 404 errors

**Solutions:**
- Check nginx configuration and paths
- Verify build output exists in `dist` directory
- Check nginx error logs: `tail -f /var/log/nginx/error.log`
- Verify file permissions

#### 2. API Connection Failed

**Symptoms:** "Network Error" or "Failed to fetch"

**Solutions:**
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check CORS configuration in backend
- Verify `VITE_API_BASE_URL` in frontend environment
- Check firewall rules

#### 3. WebSocket Connection Failed

**Symptoms:** Real-time logs not working

**Solutions:**
- Verify WebSocket proxy configuration in nginx
- Check backend WebSocket support
- Verify `VITE_WS_URL` in frontend environment
- Check for proxy/load balancer WebSocket support

#### 4. High Memory Usage

**Solutions:**
- Reduce number of gunicorn workers
- Enable Redis caching
- Check for memory leaks in logs
- Increase server resources

#### 5. Slow Response Times

**Solutions:**
- Enable caching (Redis)
- Optimize database queries
- Increase worker count
- Enable CDN for static assets
- Check network latency

### Debug Mode

To enable debug mode temporarily:

**Backend:**
```bash
export FLASK_DEBUG=True
export FLASK_ENV=development
```

**Frontend:**
```bash
export VITE_ENABLE_DEBUG=true
```

### Getting Help

If you encounter issues not covered here:

1. Check application logs
2. Review error messages
3. Search existing issues on GitHub
4. Create a new issue with:
   - Error messages
   - Steps to reproduce
   - Environment details
   - Relevant logs

## Performance Tuning

### Gunicorn Workers

Calculate optimal worker count:
```
workers = (2 * CPU_cores) + 1
```

Example for 4-core server:
```
GUNICORN_WORKERS=9
```

### Redis Configuration

For production, configure Redis persistence:

```bash
# Edit redis.conf
appendonly yes
appendfsync everysec
```

### Nginx Caching

Enable nginx caching for API responses:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

## Security Hardening

### 1. Firewall Configuration

**UFW (Ubuntu):**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/TLS Configuration

Use strong SSL configuration in nginx:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

### 3. Rate Limiting

Configure rate limiting in nginx:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
}
```

### 4. Security Headers

Add security headers in nginx:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Scaling

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Backend Instances**: Run multiple backend containers
3. **Shared Cache**: Use Redis cluster
4. **Session Storage**: Use Redis for session storage

Example docker-compose for scaling:

```yaml
services:
  backend:
    deploy:
      replicas: 3
```

### Vertical Scaling

Increase resources for single instance:

- Increase CPU cores
- Increase RAM
- Use faster storage (SSD)
- Optimize database queries

## Backup and Recovery

### Backup Strategy

1. **Configuration Files**: Daily backup
2. **Database**: Hourly backups (if applicable)
3. **Logs**: Weekly archives

### Backup Script Example

```bash
#!/bin/bash
BACKUP_DIR="/backups/ai-powershell-assistant"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" backend/.env backend/config.py

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" backend/logs/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### Recovery Procedure

1. Stop services
2. Restore configuration files
3. Restore database (if applicable)
4. Restart services
5. Verify health checks

## Conclusion

This deployment guide covers the essential steps for deploying the AI PowerShell Assistant Web UI. For specific deployment scenarios or advanced configurations, please refer to the official documentation or contact support.
