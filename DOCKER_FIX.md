# Docker Setup - Quick Fix Guide

## Issues Fixed

1. **No Dockerfile** - Created proper Dockerfile for backend
2. **Dependencies not cached** - Now installed during build, not runtime
3. **Better error handling** - Startup script verifies everything before running
4. **Proper volume mounts** - Fixed paths for death certificate images

## How to Run

### Clean Start (Recommended)
```bash
# Remove old containers and images
docker-compose down
docker rmi ccap-claimstraingame-backend

# Build and start
docker-compose up --build
```

### Quick Start
```bash
docker-compose up --build
```

## Verify It's Working

1. Backend should start and show:
   ```
   ✓ All dependencies installed
   ✓ All required files present
   ✓ All checks passed - starting application...
   ```

2. Check health endpoint:
   ```bash
   curl http://localhost:5000/api/health
   ```
   Should return: `{"status":"ok"}`

## Common Issues

### Issue: "Module not found"
**Solution:** Rebuild the image
```bash
docker-compose build --no-cache
docker-compose up
```

### Issue: "AI models not found"
**Expected:** The app will show a warning but still work using fallback mode:
```
⚠ AI models not found - using fallback mode
```
This is normal - the app uses hand-crafted scenarios instead.

### Issue: Port 5000 already in use
**Solution:** Stop other services or change port in docker-compose.yml:
```yaml
ports:
  - "5001:5000"  # Use 5001 instead
```

### Issue: Database errors
**Solution:** Delete the database and restart:
```bash
rm backend/data.db
docker-compose restart
```

## View Logs

```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Backend only
docker-compose logs backend
```

## Stop Everything

```bash
docker-compose down
```

## Frontend Setup

The docker-compose only runs the backend. For the frontend:

```bash
cd frontend
npm install
npm start
```

Frontend will run on http://localhost:3000
Backend API on http://localhost:5000
