"""
FastAPI application for SignASL scraper
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.signasl_scraper import SignASLScraper
from scraper.video_downloader import VideoDownloader

app = FastAPI(
    title="SignASL Scraper API",
    description="API for scraping and downloading ASL videos from SignASL.org",
    version="1.0.0"
)

# Initialize scraper and downloader
scraper = SignASLScraper(rate_limit_delay=1.0)
downloader = VideoDownloader(cache_dir="cache")


# Pydantic models
class WordCheckResponse(BaseModel):
    word: str
    exists: bool
    video_count: int


class VideoUrlResponse(BaseModel):
    word: str
    video_urls: List[str]


class VideoDownloadResponse(BaseModel):
    word: str
    success: bool
    cached_videos: List[str]
    message: str


class BatchDownloadRequest(BaseModel):
    words: List[str]
    force: bool = False


class BatchDownloadResponse(BaseModel):
    total_words: int
    successful: int
    failed: int
    results: List[dict]


class CacheListResponse(BaseModel):
    total_videos: int
    cache_size_bytes: int
    cache_size_mb: float
    videos: List[str]


class CacheClearResponse(BaseModel):
    deleted_count: int
    message: str


# API Endpoints

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "SignASL Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "check": "/api/check/{word}",
            "video_urls": "/api/video-url/{word}",
            "download": "/api/download/{word}",
            "batch_download": "/api/batch/download",
            "cache_list": "/api/cache/list",
            "cache_clear": "/api/cache/clear"
        }
    }


@app.get("/api/check/{word}", response_model=WordCheckResponse)
def check_word(word: str):
    """
    Check if a word exists on SignASL.org

    Args:
        word: The ASL word to check

    Returns:
        JSON with word existence and video count
    """
    try:
        exists = scraper.word_exists(word)
        if exists:
            video_urls = scraper.get_video_urls(word)
            video_count = len(video_urls)
        else:
            video_count = 0

        return WordCheckResponse(
            word=word,
            exists=exists,
            video_count=video_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking word: {str(e)}")


@app.get("/api/video-url/{word}", response_model=VideoUrlResponse)
def get_video_urls(word: str):
    """
    Get video URLs for a word without downloading

    Args:
        word: The ASL word to look up

    Returns:
        JSON with list of video URLs
    """
    try:
        video_urls = scraper.get_video_urls(word)

        if not video_urls:
            raise HTTPException(
                status_code=404,
                detail=f"No videos found for word: {word}"
            )

        return VideoUrlResponse(
            word=word,
            video_urls=video_urls
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video URLs: {str(e)}")


@app.get("/api/download/{word}", response_model=VideoDownloadResponse)
def download_video(word: str, force: bool = False):
    """
    Download video(s) for a word to local cache

    Args:
        word: The ASL word to download
        force: Force re-download even if cached (default: False)

    Returns:
        JSON with download status and cached video paths
    """
    try:
        # Get video URLs
        video_urls = scraper.get_video_urls(word)

        if not video_urls:
            raise HTTPException(
                status_code=404,
                detail=f"No videos found for word: {word}"
            )

        # Download all videos
        cached_paths = downloader.download_all_videos(word, video_urls, force=force)

        if not cached_paths:
            return VideoDownloadResponse(
                word=word,
                success=False,
                cached_videos=[],
                message="Failed to download videos"
            )

        return VideoDownloadResponse(
            word=word,
            success=True,
            cached_videos=cached_paths,
            message=f"Successfully downloaded {len(cached_paths)} video(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")


@app.post("/api/batch/download", response_model=BatchDownloadResponse)
def batch_download(request: BatchDownloadRequest, background_tasks: BackgroundTasks):
    """
    Download videos for multiple words

    Args:
        request: Batch download request with list of words

    Returns:
        JSON with batch download results
    """
    results = []
    successful = 0
    failed = 0

    for word in request.words:
        try:
            # Get video URLs
            video_urls = scraper.get_video_urls(word)

            if not video_urls:
                results.append({
                    "word": word,
                    "success": False,
                    "error": "No videos found"
                })
                failed += 1
                continue

            # Download videos
            cached_paths = downloader.download_all_videos(word, video_urls, force=request.force)

            if cached_paths:
                results.append({
                    "word": word,
                    "success": True,
                    "video_count": len(cached_paths),
                    "cached_videos": cached_paths
                })
                successful += 1
            else:
                results.append({
                    "word": word,
                    "success": False,
                    "error": "Failed to download videos"
                })
                failed += 1

        except Exception as e:
            results.append({
                "word": word,
                "success": False,
                "error": str(e)
            })
            failed += 1

    return BatchDownloadResponse(
        total_words=len(request.words),
        successful=successful,
        failed=failed,
        results=results
    )


@app.get("/api/cache/list", response_model=CacheListResponse)
def list_cache():
    """
    List all cached videos

    Returns:
        JSON with cached video information
    """
    try:
        cached_videos = downloader.list_all_cached()
        cache_size = downloader.get_cache_size()

        return CacheListResponse(
            total_videos=len(cached_videos),
            cache_size_bytes=cache_size,
            cache_size_mb=round(cache_size / (1024 * 1024), 2),
            videos=cached_videos
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cache: {str(e)}")


@app.delete("/api/cache/clear", response_model=CacheClearResponse)
def clear_cache(word: Optional[str] = None):
    """
    Clear video cache

    Args:
        word: Optional word to clear (clears all if not provided)

    Returns:
        JSON with deletion results
    """
    try:
        deleted_count = downloader.clear_cache(word=word)

        if word:
            message = f"Cleared {deleted_count} video(s) for word: {word}"
        else:
            message = f"Cleared all {deleted_count} cached video(s)"

        return CacheClearResponse(
            deleted_count=deleted_count,
            message=message
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
