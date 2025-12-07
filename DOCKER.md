# Docker Deployment Guide

This guide explains how to deploy the Resume Matcher application using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)
- OpenAI API key (for LLM features)

## Quick Start

1. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Deploy the application:**
   ```bash
   ./deploy.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:5001
   - Health Check: http://localhost:5001/api/health

## Deployment Commands

The `deploy.sh` script provides several commands:

### Start the application
```bash
./deploy.sh up
```
Builds and starts all containers in detached mode.

### Stop the application
```bash
./deploy.sh down
```
Stops and removes all containers.

### Restart the application
```bash
./deploy.sh restart
```
Restarts all running containers without rebuilding.

### View logs
```bash
./deploy.sh logs
```
Shows real-time logs from all containers.

### Build only (no start)
```bash
./deploy.sh build
```
Builds Docker images without starting containers.

### Check status
```bash
./deploy.sh status
```
Shows the status of all containers.

### Clean up
```bash
./deploy.sh clean
```
Removes all containers, volumes, and images. **Warning:** This deletes all data!

## Architecture

### Services

1. **Backend (Flask API)**
   - Port: 5001
   - Container: `resume-matcher-backend`
   - Image: Python 3.11-slim
   - Features: Resume parsing, vector search, scoring

2. **Frontend (React + Vite)**
   - Port: 80
   - Container: `resume-matcher-frontend`
   - Image: Nginx Alpine
   - Multi-stage build for optimized production

### Volumes

- `./data:/app/data` - Persists ChromaDB vector store and uploaded resumes
- `backend_models` - Caches downloaded ML models for faster restarts

### Network

All services communicate via the `resume-network` bridge network.

## Configuration

### Environment Variables

The application uses the following environment variables (set in `.env`):

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
FLASK_ENV=production
FLASK_DEBUG=False
CHROMA_PERSIST_DIR=../data/chroma
UPLOAD_FOLDER=../data/uploads
VITE_API_URL=http://localhost:5001
```

### Port Configuration

To change default ports, edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5001:5001"  # Change host port (left side)
  
  frontend:
    ports:
      - "80:80"      # Change host port (left side)
```

## Data Persistence

The `./data` directory persists:
- **ChromaDB vector store** (`data/chroma/`) - Indexed resume embeddings
- **Uploaded resumes** (`data/uploads/`) - User-uploaded files

This data survives container restarts but is removed with `./deploy.sh clean`.

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Backend health check failing

Test directly:
```bash
curl http://localhost:5001/api/health
```

### Frontend can't connect to backend

Verify backend is running:
```bash
docker-compose ps
```

Check if backend is accessible:
```bash
docker exec resume-matcher-backend curl localhost:5001/api/health
```

### Permission errors with data directory

Fix ownership:
```bash
sudo chown -R $USER:$USER ./data
```

### Out of disk space

Clean up unused Docker resources:
```bash
docker system prune -a --volumes
```

## Development vs Production

### Development Mode

For development with hot-reload, modify `docker-compose.yml`:

```yaml
services:
  backend:
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
```

### Production Mode

The default configuration is optimized for production:
- Multi-stage builds for smaller images
- Nginx for efficient static file serving
- Health checks for container monitoring
- Automatic restart policies

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Create .env file
        run: |
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" > .env
      
      - name: Deploy
        run: ./deploy.sh up
```

## Cloud Deployment

### AWS EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure `.env`
5. Run `./deploy.sh up`
6. Configure security groups for ports 80 and 5001

### DigitalOcean Droplet

1. Create Docker Droplet
2. Clone repository
3. Configure `.env`
4. Run `./deploy.sh up`

### Docker Hub Deployment

Build and push images:
```bash
docker build -t yourusername/resume-matcher-backend:latest ./backend
docker build -t yourusername/resume-matcher-frontend:latest ./frontend
docker push yourusername/resume-matcher-backend:latest
docker push yourusername/resume-matcher-frontend:latest
```

## Monitoring

### View resource usage
```bash
docker stats
```

### Check container health
```bash
docker inspect --format='{{.State.Health.Status}}' resume-matcher-backend
```

### Access container shell
```bash
docker exec -it resume-matcher-backend /bin/bash
docker exec -it resume-matcher-frontend /bin/sh
```

## Backup and Restore

### Backup data
```bash
tar -czf resume-data-backup-$(date +%Y%m%d).tar.gz ./data
```

### Restore data
```bash
tar -xzf resume-data-backup-YYYYMMDD.tar.gz
```

## Security Considerations

1. **Never commit `.env` file** - Contains sensitive API keys
2. **Use secrets management** - For production deployments
3. **Limit exposed ports** - Only expose necessary ports
4. **Regular updates** - Keep base images updated
5. **HTTPS in production** - Use reverse proxy (Nginx/Traefik) with SSL

## Performance Optimization

### Build cache
Docker caches layers for faster rebuilds. To force rebuild:
```bash
docker-compose build --no-cache
```

### Image size
The multi-stage frontend build reduces image size from ~800MB to ~25MB.

### Model caching
ML models are cached in a Docker volume to avoid re-downloading on restarts.

## Support

For issues or questions:
1. Check logs: `./deploy.sh logs`
2. Review this documentation
3. Check Docker and Docker Compose versions
4. Ensure `.env` is properly configured
