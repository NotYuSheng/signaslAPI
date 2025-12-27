# SignASL Scraper API

A web scraper and REST API for retrieving ASL (American Sign Language) videos from [SignASL.org](https://www.signasl.org/).

## Overview

This project scrapes ASL sign language videos from SignASL.org and provides a FastAPI-based REST API to:
- Check if a word/sign exists on SignASL.org
- Retrieve video URLs without downloading
- Download and cache videos locally
- Batch download multiple videos
- Manage the local video cache

## Features

- 🔍 **Word Lookup** - Search for ASL signs by word
- 📥 **Video Download** - Scrape and download ASL videos
- 🚀 **REST API** - Simple API interface for video retrieval
- 💾 **Local Cache** - Cache downloaded videos to avoid re-scraping
- 🎯 **URL Extraction** - Get direct video URLs from SignASL.org

## Project Structure

```
signaslAPI/
├── scraper/
│   ├── __init__.py
│   ├── signasl_scraper.py    # Core scraping logic
│   └── video_downloader.py   # Video download utilities
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI application
├── cache/                    # Downloaded videos cache
├── venv/                     # Virtual environment
├── requirements.txt
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker Compose for production
├── docker-compose.dev.yml   # Docker Compose for development
├── .dockerignore            # Docker ignore patterns
├── test_scraper.py          # Test HTML inspection
├── test_full_scraper.py     # Test scraper functions
├── test_api.py              # Test API endpoints
└── README.md
```

## Installation

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker 20.10+
- Docker Compose v2.0+

**Using Pre-built Image from GHCR:**

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/notyusheng/signasl-api:latest

# Run the container
docker run -d \
  --name signasl-api \
  -p 8000:8000 \
  -v $(pwd)/cache:/app/cache \
  ghcr.io/notyusheng/signasl-api:latest

# Or use a specific version
docker pull ghcr.io/notyusheng/signasl-api:v0.0.0-abc1234
```

**Building from Source:**

```bash
# Clone or navigate to the project
cd Desktop/signaslAPI

# Build and start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down

# Stop and remove volumes (clears cache)
docker compose down -v
```

The API will be available at `http://localhost:8000`

**Development Mode with Hot Reload:**

```bash
# Use the development compose file
docker compose -f docker-compose.dev.yml up -d

# Code changes will automatically reload the server
```

### Option 2: Python Virtual Environment

**Prerequisites:**
- Python 3.11+
- pip

**Setup:**

```bash
# Clone or navigate to the project
cd Desktop/signaslAPI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### As a Python Module

```python
from scraper.signasl_scraper import SignASLScraper
from scraper.video_downloader import VideoDownloader

scraper = SignASLScraper()
downloader = VideoDownloader()

# Check if word exists
exists = scraper.word_exists("hello")
print(f"Word exists: {exists}")

# Get all video URLs for a word
video_urls = scraper.get_video_urls("hello")
print(f"Found {len(video_urls)} videos")
print(f"First URL: {video_urls[0]}")

# Get primary video URL
primary_url = scraper.get_primary_video_url("hello")
print(f"Primary URL: {primary_url}")

# Get detailed video information
details = scraper.get_video_details("hello")
for detail in details:
    print(f"Video ID: {detail['id']}, URL: {detail['url']}")

# Download all videos for a word
cached_paths = downloader.download_all_videos("hello", video_urls)
print(f"Downloaded to: {cached_paths}")

# Check if a video is cached
is_cached = downloader.is_cached("hello", video_urls[0])
print(f"Cached: {is_cached}")
```

### As a REST API

**Using Docker (Recommended):**

```bash
# Start the API with Docker Compose
docker compose up -d

# The API will be available at http://localhost:8000

# Test the endpoints:
curl http://localhost:8000/api/check/hello
```

**Using Python Virtual Environment:**

```bash
# Start the API server
./venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or use Python directly
./venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# In a new terminal, test the endpoints:

# Check if word exists
curl http://localhost:8000/api/check/hello

# Get video URLs
curl http://localhost:8000/api/video-url/hello

# Download videos
curl http://localhost:8000/api/download/hello

# Batch download
curl -X POST http://localhost:8000/api/batch/download \
  -H "Content-Type: application/json" \
  -d '{"words": ["hello", "world", "thank-you"], "force": false}'

# List cached videos
curl http://localhost:8000/api/cache/list

# Clear cache for a specific word
curl -X DELETE http://localhost:8000/api/cache/clear?word=hello

# Clear entire cache
curl -X DELETE http://localhost:8000/api/cache/clear
```

### Running Tests

```bash
# Test HTML inspection
./venv/bin/python test_scraper.py

# Test scraper functions
./venv/bin/python test_full_scraper.py

# Test API endpoints (requires API server running)
./venv/bin/python test_api.py
```

## API Endpoints

### 1. Check Word Existence

**Endpoint:** `GET /api/check/{word}`

**Description:** Check if a word/sign exists on SignASL.org

**Path Parameters:**
- `word` (string, required) - The word to search for (case-insensitive)

**Success Response (200 OK):**
```json
{
  "word": "hello",
  "exists": true,
  "video_count": 7
}
```

**Word Not Found (200 OK):**
```json
{
  "word": "nonexistentword",
  "exists": false,
  "video_count": 0
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error checking word: Connection timeout"
}
```

---

### 2. Get Video URL

**Endpoint:** `GET /api/video-url/{word}`

**Description:** Get the direct video URL for a word without downloading

**Path Parameters:**
- `word` (string, required) - The word to get video URL for

**Success Response (200 OK):**
```json
{
  "word": "hello",
  "video_urls": [
    "https://media.signbsl.com/videos/asl/startasl/mp4/hello.mp4",
    "https://media.signbsl.com/videos/asl/elementalaslconcepts/mp4/hello.mp4",
    "https://media.signbsl.com/videos/asl/youtube/mp4/6kvCOzxP9_A.mp4"
  ]
}
```

**Not Found Response (404 Not Found):**
```json
{
  "detail": "No videos found for word: nonexistentword"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error fetching video URLs: Connection timeout"
}
```

---

### 3. Download Video

**Endpoint:** `GET /api/download/{word}`

**Description:** Download the video and save to local cache

**Path Parameters:**
- `word` (string, required) - The word to download video for

**Query Parameters:**
- `force` (boolean, optional, default=false) - Force re-download even if cached

**Success Response (200 OK):**
```json
{
  "word": "hello",
  "success": true,
  "cached_videos": [
    "cache/hello_d6975bb6.mp4",
    "cache/hello_8a3f2c1e.mp4",
    "cache/hello_4b9e7d2a.mp4"
  ],
  "message": "Successfully downloaded 3 video(s)"
}
```

**Not Found Response (404 Not Found):**
```json
{
  "detail": "No videos found for word: nonexistentword"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Error downloading video: Connection timeout"
}
```

---

### 4. Batch Download

**Endpoint:** `POST /api/batch/download`

**Description:** Download multiple videos in batch

**Request Body:**
```json
{
  "words": ["hello", "world", "thank", "you"],
  "force": false
}
```

**Request Schema:**
- `words` (array of strings, required) - List of words to download
- `force` (boolean, optional, default=false) - Force re-download cached videos

**Success Response (200 OK):**
```json
{
  "total_words": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "word": "hello",
      "success": true,
      "video_count": 7,
      "cached_videos": [
        "cache/hello_d6975bb6.mp4",
        "cache/hello_8a3f2c1e.mp4"
      ]
    },
    {
      "word": "world",
      "success": true,
      "video_count": 27,
      "cached_videos": [
        "cache/world_a1b2c3d4.mp4"
      ]
    },
    {
      "word": "nonexistent",
      "success": false,
      "error": "No videos found"
    }
  ]
}
```

---

### 5. List Cached Videos

**Endpoint:** `GET /api/cache/list`

**Description:** List all videos in local cache

**Success Response (200 OK):**
```json
{
  "total_videos": 58,
  "cache_size_bytes": 6205440,
  "cache_size_mb": 5.92,
  "videos": [
    "cache/hello_d6975bb6.mp4",
    "cache/world_a1b2c3d4.mp4",
    "cache/computer_5e8f9a2b.mp4"
  ]
}
```

---

### 6. Clear Cache

**Endpoint:** `DELETE /api/cache/clear`

**Description:** Clear cached videos (all or for a specific word)

**Query Parameters:**
- `word` (string, optional) - If provided, only clear videos for this word

**Success Response (200 OK) - Clear all:**
```json
{
  "deleted_count": 58,
  "message": "Cleared all 58 cached video(s)"
}
```

**Success Response (200 OK) - Clear specific word:**
```json
{
  "deleted_count": 7,
  "message": "Cleared 7 video(s) for word: hello"
}
```

## Dependencies

```txt
beautifulsoup4==4.12.3     # HTML parsing
requests==2.31.0           # HTTP requests
fastapi==0.109.0           # API framework
uvicorn[standard]==0.27.0  # ASGI server
aiofiles==23.2.1           # Async file operations
lxml==5.1.0                # XML/HTML parser
```

## Docker Deployment

### Docker Commands

```bash
# Build the image
docker compose build

# Start the container
docker compose up -d

# View logs
docker compose logs -f

# Check container status
docker compose ps

# Stop the container
docker compose down

# Rebuild and restart
docker compose up -d --build

# Access container shell
docker compose exec signasl-api sh

# Remove everything including volumes
docker compose down -v
```

### Docker Configuration

**Production (`docker-compose.yml`):**
- Runs on port 8000
- Persistent cache volume
- Auto-restart enabled
- Health checks configured

**Development (`docker-compose.dev.yml`):**
- Hot reload enabled
- Source code mounted as volumes
- Immediate code changes reflection

### Volume Management

The Docker setup uses a volume to persist the video cache:

```bash
# View cache contents
docker compose exec signasl-api ls -lah /app/cache

# Backup cache
docker compose exec signasl-api tar -czf /tmp/cache-backup.tar.gz /app/cache
docker compose cp signasl-api:/tmp/cache-backup.tar.gz ./cache-backup.tar.gz

# Clear cache via API
curl -X DELETE http://localhost:8000/api/cache/clear
```

## How It Works

1. **Word Lookup**: The scraper constructs a URL to SignASL.org using the word
2. **Page Fetch**: Retrieves the HTML page using requests with proper headers
3. **Video Extraction**: Parses HTML with BeautifulSoup to find all `<video>` and `<source>` tags
4. **Multiple Videos**: SignASL.org typically provides 5-10+ videos per word from different sources
5. **Video Download**: Downloads video files to local cache with unique filenames (word + URL hash)
6. **Caching**: Checks cache before downloading to avoid redundant requests
7. **Response**: Returns video URLs or local file paths via REST API

## SignASL.org Structure

SignASL.org URLs follow the pattern:
```
https://www.signasl.org/sign/{word}
```

Examples:
- `https://www.signasl.org/sign/hello` (9 videos found)
- `https://www.signasl.org/sign/world` (27 videos found)
- `https://www.signasl.org/sign/thank-you`

**Video Sources:**
SignASL.org aggregates videos from multiple sources:
- `media.signbsl.com/videos/asl/startasl/`
- `media.signbsl.com/videos/asl/elementalaslconcepts/`
- `media.signbsl.com/videos/asl/youtube/`
- `media.signbsl.com/videos/asl/aslsignbank/`
- `player.vimeo.com/external/` (for ASL Study videos)

## Integration with GestureGPT

This scraper is designed to populate the video repository for [GestureGPT](../GestureGPT).

**Workflow:**
1. Use this scraper to download ASL videos
2. Update GestureGPT's `data/video_index.json` with video URLs
3. GestureGPT API serves these videos to clients

## Limitations

- Rate limiting: Be respectful of SignASL.org's servers
- Video availability: Not all words may have videos
- Network dependency: Requires internet connection
- Copyright: Videos belong to SignASL.org - respect their terms of use

## Ethical Considerations

⚠️ **Important**: This scraper is for educational and accessibility purposes only.

- Respect SignASL.org's robots.txt
- Implement rate limiting
- Cache videos to minimize requests
- Credit SignASL.org as the source
- Do not redistribute videos commercially

## GitHub Container Registry (GHCR)

The SignASL API is automatically published to GitHub Container Registry on every push to main and on releases.

### Image Naming Convention

- **Push to main:** `ghcr.io/notyusheng/signasl-api:v0.0.0-{short-sha}`
- **Release:** `ghcr.io/notyusheng/signasl-api:v1.0.0` (and tagged as `latest`)

### Using GHCR Images

```bash
# Pull latest version
docker pull ghcr.io/notyusheng/signasl-api:latest

# Run directly
docker run -d -p 8000:8000 \
  -v ./cache:/app/cache \
  ghcr.io/notyusheng/signasl-api:latest

# Use in docker-compose.yml (uncomment the image line)
# See docker-compose.yml for details
```

### Workflow Details

The GitHub Actions workflow (`.github/workflows/publish-ghcr.yml`) automatically:
1. Builds multi-platform images (linux/amd64, linux/arm64)
2. Tags images with version + short SHA for pushes to main
3. Tags images with version only for releases
4. Pushes `latest` tag only on releases
5. Uses GitHub Actions cache for faster builds

## Implementation Status

✅ **Completed:**
- Core scraping functionality with BeautifulSoup
- Video URL extraction from SignASL.org
- Multiple video support (returns all available videos per word)
- Video download and caching system
- Rate limiting (1 second delay between requests)
- FastAPI REST API with all 6 endpoints
- Batch download support
- Cache management (list, clear by word, clear all)
- Error handling and logging
- Comprehensive test suite
- **Docker & Docker Compose setup**
- **Production and development configurations**
- **Volume persistence for cache**
- **Health checks and auto-restart**
- **GitHub Container Registry (GHCR) publishing**
- **Multi-platform Docker images (amd64, arm64)**
- **Automated CI/CD with GitHub Actions**

## Future Enhancements

- [ ] Add robots.txt parser
- [ ] Make rate limiting configurable
- [ ] Support for other sign language websites (WLASL, ASL-LEX)
- [ ] Video quality selection
- [ ] Metadata extraction (poster images, video IDs, sources)
- [ ] Progress tracking for batch downloads
- [ ] Database integration for video metadata
- [ ] Video format conversion
- [ ] Async download support for better performance

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [SignASL.org](https://www.signasl.org/) - ASL video source
- Built to support the [GestureGPT](https://github.com/NotYuSheng/GestureGPT) project

---

**Note**: This is a work in progress. Always check SignASL.org's terms of service and robots.txt before scraping.
