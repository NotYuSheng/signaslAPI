"""
Video downloader for SignASL videos
"""
import os
import requests
import hashlib
import logging
from typing import Optional, List
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Downloads and caches ASL videos
    """

    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize the video downloader

        Args:
            cache_dir: Directory to store downloaded videos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_filename(self, word: str, video_url: str) -> str:
        """
        Generate a cache filename for a video

        Args:
            word: The ASL word
            video_url: The video URL

        Returns:
            Cache filename
        """
        # Create a hash of the URL to handle different sources
        url_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
        # Sanitize word for filename
        safe_word = word.lower().replace(' ', '_').replace('-', '_')
        return f"{safe_word}_{url_hash}.mp4"

    def _get_cache_path(self, word: str, video_url: str) -> Path:
        """
        Get the full cache path for a video

        Args:
            word: The ASL word
            video_url: The video URL

        Returns:
            Path object for the cached video
        """
        filename = self._get_cache_filename(word, video_url)
        return self.cache_dir / filename

    def is_cached(self, word: str, video_url: str) -> bool:
        """
        Check if a video is already cached

        Args:
            word: The ASL word
            video_url: The video URL

        Returns:
            True if video is cached, False otherwise
        """
        cache_path = self._get_cache_path(word, video_url)
        return cache_path.exists()

    def download_video(self, word: str, video_url: str, force: bool = False) -> Optional[str]:
        """
        Download a video to the cache

        Args:
            word: The ASL word
            video_url: The video URL to download
            force: Force re-download even if cached

        Returns:
            Path to the cached video or None if download fails
        """
        cache_path = self._get_cache_path(word, video_url)

        # Check if already cached
        if cache_path.exists() and not force:
            logger.info(f"Video for '{word}' already cached at {cache_path}")
            return str(cache_path)

        try:
            logger.info(f"Downloading video for '{word}' from {video_url}")

            # Download the video
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()

            # Save to cache
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = cache_path.stat().st_size
            logger.info(f"Downloaded video for '{word}' ({file_size} bytes) to {cache_path}")
            return str(cache_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading video for '{word}': {e}")
            # Clean up partial download
            if cache_path.exists():
                cache_path.unlink()
            return None

    def download_all_videos(self, word: str, video_urls: List[str], force: bool = False) -> List[str]:
        """
        Download all videos for a word

        Args:
            word: The ASL word
            video_urls: List of video URLs to download
            force: Force re-download even if cached

        Returns:
            List of paths to cached videos
        """
        cached_paths = []

        for video_url in video_urls:
            cache_path = self.download_video(word, video_url, force=force)
            if cache_path:
                cached_paths.append(cache_path)

        return cached_paths

    def get_cached_videos(self, word: str) -> List[str]:
        """
        Get all cached videos for a word

        Args:
            word: The ASL word

        Returns:
            List of paths to cached videos
        """
        safe_word = word.lower().replace(' ', '_').replace('-', '_')
        pattern = f"{safe_word}_*.mp4"

        cached_videos = list(self.cache_dir.glob(pattern))
        return [str(path) for path in cached_videos]

    def list_all_cached(self) -> List[str]:
        """
        List all cached videos

        Returns:
            List of all cached video paths
        """
        cached_videos = list(self.cache_dir.glob("*.mp4"))
        return [str(path) for path in cached_videos]

    def clear_cache(self, word: Optional[str] = None) -> int:
        """
        Clear cached videos

        Args:
            word: If provided, only clear videos for this word. Otherwise, clear all.

        Returns:
            Number of files deleted
        """
        if word:
            # Clear only videos for specific word
            safe_word = word.lower().replace(' ', '_').replace('-', '_')
            pattern = f"{safe_word}_*.mp4"
            files_to_delete = list(self.cache_dir.glob(pattern))
        else:
            # Clear all videos
            files_to_delete = list(self.cache_dir.glob("*.mp4"))

        count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                count += 1
                logger.info(f"Deleted cached video: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting {file_path}: {e}")

        logger.info(f"Cleared {count} cached video(s)")
        return count

    def get_cache_size(self) -> int:
        """
        Get total size of cache in bytes

        Returns:
            Total cache size in bytes
        """
        total_size = 0
        for file_path in self.cache_dir.glob("*.mp4"):
            total_size += file_path.stat().st_size
        return total_size
