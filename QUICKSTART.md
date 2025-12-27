# SignASL Scraper API - Quick Start Guide

## Fastest Way to Get Started (Docker)

### 1. Start the API

```bash
docker compose up -d
```

That's it! The API is now running at `http://localhost:8000`

### 2. Test the API

```bash
# Check if "hello" exists
curl http://localhost:8000/api/check/hello

# Get video URLs
curl http://localhost:8000/api/video-url/hello

# Download videos
curl http://localhost:8000/api/download/hello
```

### 3. View Logs

```bash
docker compose logs -f
```

### 4. Stop the API

```bash
docker compose down
```

## Common Operations

### Download Videos for Multiple Words

```bash
curl -X POST http://localhost:8000/api/batch/download \
  -H "Content-Type: application/json" \
  -d '{"words": ["hello", "world", "thank-you", "computer", "internet"]}'
```

### List Cached Videos

```bash
curl http://localhost:8000/api/cache/list
```

### Clear Cache

```bash
# Clear all cache
curl -X DELETE http://localhost:8000/api/cache/clear

# Clear cache for specific word
curl -X DELETE http://localhost:8000/api/cache/clear?word=hello
```

### View Downloaded Videos

```bash
# List videos in cache directory
ls -lh cache/

# Count cached videos
docker compose exec signasl-api ls -1 /app/cache | wc -l
```

## Development Mode

For development with hot reload:

```bash
# Start in development mode
docker compose -f docker-compose.dev.yml up -d

# Edit code in scraper/ or api/ - changes will auto-reload
```

## Troubleshooting

### Port Already in Use

If port 8000 is in use, edit `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### View Container Logs

```bash
docker compose logs signasl-api
```

### Access Container Shell

```bash
docker compose exec signasl-api sh
```

### Rebuild Image

```bash
docker compose up -d --build
```

### Complete Reset

```bash
# Stop and remove everything including volumes
docker compose down -v

# Rebuild and start fresh
docker compose up -d --build
```

## Integration with GestureGPT

This API is designed to work with the GestureGPT project:

1. Start this SignASL API on port 8000
2. Use it to download ASL videos
3. Integrate video URLs with GestureGPT's video_index.json
4. GestureGPT serves the videos to clients

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [api/main.py](api/main.py) to see all available endpoints
- Review [Dockerfile](Dockerfile) and [docker-compose.yml](docker-compose.yml) for configuration options
