# Troubleshooting Guide - AI PowerShell Assistant Web UI

This guide helps you diagnose and resolve common issues with the AI PowerShell Assistant Web UI.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Frontend Issues](#frontend-issues)
- [Backend Issues](#backend-issues)
- [Network Issues](#network-issues)
- [Performance Issues](#performance-issues)
- [Docker Issues](#docker-issues)
- [Database Issues](#database-issues)

## Quick Diagnostics

### Health Check Commands

Run these commands to quickly check system status:

```bash
# Check frontend (if using nginx)
curl -I http://localhost/

# Check backend API
curl http://localhost:5000/api/health

# Check Docker containers
docker-compose ps

# Check logs
docker-compose logs --tail=50

# Check system resources
docker stats
```

### Common Quick Fixes

1. **Restart services:**
   ```bash
   docker-compose restart
   # or
   sudo systemctl restart nginx
   sudo systemctl restart ai-powershell-backend
   ```

2. **Clear cache:**
   ```bash
   # Frontend
   rm -rf node_modules/.vite
   
   # Backend
   redis-cli FLUSHALL
   ```

3. **Rebuild:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Frontend Issues

### Issue: Blank Page or White Screen

**Symptoms:**
- Browser shows blank page
- No errors in console
- Page loads but nothing displays

**Diagnosis:**
```bash
# Check if files exist
ls -la dist/

# Check nginx configuration
sudo nginx -t

# Check nginx logs
tail -f /var/log/nginx/error.log
```

**Solutions:**

1. **Verify build output:**
   ```bash
   npm run build
   ls -la dist/
   ```

2. **Check nginx configuration:**
   ```nginx
   # Ensure correct root path
   root /path/to/web-ui/dist;
   try_files $uri $uri/ /index.html;
   ```

3. **Clear browser cache:**
   - Press Ctrl+Shift+R (hard refresh)
   - Clear browser cache and cookies

4. **Check file permissions:**
   ```bash
   sudo chown -R www-data:www-data /var/www/html
   sudo chmod -R 755 /var/www/html
   ```

### Issue: JavaScript Errors in Console

**Symptoms:**
- Console shows errors like "Cannot read property of undefined"
- Features not working
- Buttons not responding

**Diagnosis:**
```javascript
// Open browser console (F12)
// Look for error messages
```

**Solutions:**

1. **Check API connection:**
   ```javascript
   // In browser console
   fetch('/api/health').then(r => r.json()).then(console.log)
   ```

2. **Verify environment variables:**
   ```bash
   # Check .env.production
   cat .env.production
   ```

3. **Rebuild with source maps:**
   ```bash
   # Temporarily enable source maps for debugging
   VITE_BUILD_SOURCEMAP=true npm run build
   ```

### Issue: API Requests Failing

**Symptoms:**
- "Network Error" messages
- "Failed to fetch" errors
- 404 or 500 errors

**Diagnosis:**
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check browser console for CORS errors
# Check network tab in browser DevTools
```

**Solutions:**

1. **Verify API URL:**
   ```env
   # .env.production
   VITE_API_BASE_URL=http://your-domain.com
   ```

2. **Check CORS configuration:**
   ```python
   # backend/app.py
   CORS(app, resources={
       r"/api/*": {
           "origins": ["http://localhost:5173", "http://your-domain.com"]
       }
   })
   ```

3. **Check nginx proxy:**
   ```nginx
   location /api/ {
       proxy_pass http://backend:5000;
       proxy_set_header Host $host;
   }
   ```

### Issue: Slow Page Load

**Symptoms:**
- Page takes long time to load
- Slow initial render
- Large bundle size

**Diagnosis:**
```bash
# Check bundle size
npm run build
ls -lh dist/assets/

# Analyze bundle
npm run build -- --mode analyze
```

**Solutions:**

1. **Enable compression:**
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **Optimize images:**
   ```bash
   # Use WebP format
   # Compress images before deployment
   ```

3. **Enable caching:**
   ```nginx
   location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## Backend Issues

### Issue: Backend Not Starting

**Symptoms:**
- Backend fails to start
- Port already in use
- Import errors

**Diagnosis:**
```bash
# Check if port is in use
lsof -i :5000
# or
netstat -tulpn | grep 5000

# Check Python version
python --version

# Check dependencies
pip list
```

**Solutions:**

1. **Kill existing process:**
   ```bash
   # Find process
   lsof -i :5000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Check Python path:**
   ```bash
   export PYTHONPATH=/path/to/ai-powershell-assistant:$PYTHONPATH
   ```

4. **Check logs:**
   ```bash
   tail -f backend/logs/app.log
   ```

### Issue: 500 Internal Server Error

**Symptoms:**
- API returns 500 errors
- Backend crashes
- Errors in logs

**Diagnosis:**
```bash
# Check backend logs
tail -f backend/logs/app.log

# Check gunicorn logs
tail -f /var/log/gunicorn/error.log

# Enable debug mode temporarily
export FLASK_DEBUG=True
```

**Solutions:**

1. **Check error logs:**
   ```bash
   # Look for stack traces
   tail -100 backend/logs/app.log
   ```

2. **Verify configuration:**
   ```bash
   # Check environment variables
   env | grep FLASK
   
   # Verify config file
   cat backend/.env
   ```

3. **Test API directly:**
   ```bash
   # Test with curl
   curl -X POST http://localhost:5000/api/command/translate \
     -H "Content-Type: application/json" \
     -d '{"input": "test"}'
   ```

### Issue: Memory Leaks

**Symptoms:**
- Memory usage keeps increasing
- Server becomes slow over time
- Out of memory errors

**Diagnosis:**
```bash
# Monitor memory usage
docker stats

# Check process memory
ps aux | grep gunicorn

# Profile memory usage
python -m memory_profiler backend/app.py
```

**Solutions:**

1. **Restart workers periodically:**
   ```python
   # gunicorn.conf.py
   max_requests = 1000
   max_requests_jitter = 50
   ```

2. **Reduce worker count:**
   ```env
   GUNICORN_WORKERS=2
   ```

3. **Enable garbage collection:**
   ```python
   import gc
   gc.collect()
   ```

4. **Check for circular references:**
   ```python
   # Use weakref for circular references
   import weakref
   ```

## Network Issues

### Issue: CORS Errors

**Symptoms:**
- "Access-Control-Allow-Origin" errors
- Preflight request failures
- API calls blocked by browser

**Diagnosis:**
```bash
# Check browser console for CORS errors
# Check network tab for OPTIONS requests
```

**Solutions:**

1. **Update CORS configuration:**
   ```python
   # backend/app.py
   CORS(app, resources={
       r"/api/*": {
           "origins": ["*"],  # For testing only
           "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
           "allow_headers": ["Content-Type", "Authorization"]
       }
   })
   ```

2. **Add CORS headers in nginx:**
   ```nginx
   add_header Access-Control-Allow-Origin *;
   add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
   add_header Access-Control-Allow-Headers "Content-Type, Authorization";
   ```

### Issue: WebSocket Connection Failed

**Symptoms:**
- Real-time logs not working
- WebSocket connection errors
- "WebSocket is closed" messages

**Diagnosis:**
```bash
# Check WebSocket endpoint
wscat -c ws://localhost:5000/ws/logs

# Check nginx WebSocket configuration
sudo nginx -t
```

**Solutions:**

1. **Update nginx configuration:**
   ```nginx
   location /ws/ {
       proxy_pass http://backend:5000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

2. **Check SocketIO configuration:**
   ```python
   # backend/app.py
   socketio = SocketIO(app, cors_allowed_origins="*")
   ```

3. **Verify WebSocket URL:**
   ```env
   # .env.production
   VITE_WS_URL=ws://your-domain.com
   ```

### Issue: Timeout Errors

**Symptoms:**
- Requests timeout
- "Gateway Timeout" errors
- Long-running operations fail

**Diagnosis:**
```bash
# Check timeout settings
grep timeout /etc/nginx/sites-available/ai-powershell-assistant

# Test with longer timeout
curl --max-time 60 http://localhost:5000/api/command/execute
```

**Solutions:**

1. **Increase nginx timeout:**
   ```nginx
   proxy_connect_timeout 120s;
   proxy_send_timeout 120s;
   proxy_read_timeout 120s;
   ```

2. **Increase gunicorn timeout:**
   ```python
   # gunicorn.conf.py
   timeout = 120
   ```

3. **Increase application timeout:**
   ```python
   # backend/app.py
   app.config['TIMEOUT'] = 120
   ```

## Performance Issues

### Issue: Slow API Responses

**Symptoms:**
- API calls take long time
- High response times
- Slow page loads

**Diagnosis:**
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/health

# Monitor backend performance
docker stats backend

# Check database queries (if applicable)
```

**Solutions:**

1. **Enable caching:**
   ```python
   # backend/app.py
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'RedisCache'})
   ```

2. **Optimize database queries:**
   ```python
   # Use indexes
   # Limit result sets
   # Use pagination
   ```

3. **Increase worker count:**
   ```env
   GUNICORN_WORKERS=8
   ```

4. **Use connection pooling:**
   ```python
   # backend/utils/pool.py
   from utils.pool import session_pool
   ```

### Issue: High CPU Usage

**Symptoms:**
- CPU usage at 100%
- Server becomes unresponsive
- Slow performance

**Diagnosis:**
```bash
# Check CPU usage
top
htop

# Profile CPU usage
python -m cProfile backend/app.py
```

**Solutions:**

1. **Optimize code:**
   - Remove unnecessary loops
   - Use generators instead of lists
   - Cache expensive operations

2. **Reduce worker count:**
   ```env
   GUNICORN_WORKERS=4
   ```

3. **Use async operations:**
   ```python
   # Use async/await for I/O operations
   import asyncio
   ```

## Docker Issues

### Issue: Container Won't Start

**Symptoms:**
- Container exits immediately
- "Container exited with code 1"
- Build failures

**Diagnosis:**
```bash
# Check container logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect <container-id>
```

**Solutions:**

1. **Check Dockerfile:**
   ```bash
   # Verify syntax
   docker build -f Dockerfile.backend .
   ```

2. **Check environment variables:**
   ```bash
   # Verify .env file
   cat backend/.env
   ```

3. **Check dependencies:**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Issue: Volume Mount Issues

**Symptoms:**
- Files not updating
- Permission denied errors
- Volume not mounting

**Diagnosis:**
```bash
# Check volume mounts
docker inspect <container-id> | grep Mounts

# Check permissions
ls -la /path/to/volume
```

**Solutions:**

1. **Fix permissions:**
   ```bash
   sudo chown -R 1000:1000 /path/to/volume
   ```

2. **Update docker-compose.yml:**
   ```yaml
   volumes:
     - ./backend:/app/backend:rw
   ```

3. **Use named volumes:**
   ```yaml
   volumes:
     backend-data:
       driver: local
   ```

## Database Issues

### Issue: Redis Connection Failed

**Symptoms:**
- "Connection refused" errors
- Cache not working
- Redis errors in logs

**Diagnosis:**
```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs
docker-compose logs redis

# Test connection
redis-cli -h localhost -p 6379
```

**Solutions:**

1. **Start Redis:**
   ```bash
   docker-compose up -d redis
   ```

2. **Check Redis URL:**
   ```env
   REDIS_URL=redis://redis:6379/0
   ```

3. **Verify network:**
   ```bash
   docker network ls
   docker network inspect <network-name>
   ```

## Getting Additional Help

If your issue is not covered here:

1. **Enable debug logging:**
   ```env
   FLASK_DEBUG=True
   LOG_LEVEL=debug
   ```

2. **Collect diagnostic information:**
   ```bash
   # System info
   uname -a
   docker --version
   python --version
   node --version
   
   # Logs
   docker-compose logs > logs.txt
   
   # Configuration
   cat .env.production > config.txt
   ```

3. **Search existing issues:**
   - Check GitHub issues
   - Search Stack Overflow
   - Check documentation

4. **Create a new issue:**
   - Include error messages
   - Provide steps to reproduce
   - Include diagnostic information
   - Describe expected vs actual behavior

## Preventive Measures

### Regular Maintenance

1. **Update dependencies:**
   ```bash
   npm update
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor logs:**
   ```bash
   # Set up log monitoring
   tail -f backend/logs/app.log
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

4. **Rotate logs:**
   ```bash
   # Configure logrotate
   sudo nano /etc/logrotate.d/ai-powershell-assistant
   ```

### Monitoring Setup

1. **Health checks:**
   ```bash
   # Add to cron
   */5 * * * * curl -f http://localhost:5000/api/health || alert
   ```

2. **Resource monitoring:**
   ```bash
   # Use monitoring tools
   # - Prometheus
   # - Grafana
   # - New Relic
   ```

3. **Error tracking:**
   ```python
   # Integrate error tracking
   # - Sentry
   # - Rollbar
   # - Bugsnag
   ```
