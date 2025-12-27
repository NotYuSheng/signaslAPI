"""
SignASL.org web scraper for extracting ASL video URLs
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignASLScraper:
    """
    Scraper for SignASL.org website to extract ASL video URLs
    """

    BASE_URL = "https://www.signasl.org/sign/{word}"

    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize the scraper

        Args:
            rate_limit_delay: Delay in seconds between requests (default: 1.0)
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _respect_rate_limit(self):
        """Ensure we respect rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _normalize_word(self, word: str) -> str:
        """
        Normalize word for URL (lowercase, replace spaces with hyphens)

        Args:
            word: The word to normalize

        Returns:
            Normalized word for URL
        """
        return word.lower().strip().replace(' ', '-')

    def _fetch_page(self, word: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse the SignASL.org page for a given word

        Args:
            word: The ASL word to look up

        Returns:
            BeautifulSoup object or None if request fails
        """
        normalized_word = self._normalize_word(word)
        url = self.BASE_URL.format(word=normalized_word)

        self._respect_rate_limit()

        try:
            logger.info(f"Fetching page for word: {word} ({url})")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            return BeautifulSoup(response.content, 'lxml')

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Word '{word}' not found on SignASL.org")
                return None
            logger.error(f"HTTP error fetching page for '{word}': {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page for '{word}': {e}")
            raise

    def word_exists(self, word: str) -> bool:
        """
        Check if a word exists on SignASL.org

        Args:
            word: The ASL word to check

        Returns:
            True if the word exists, False otherwise
        """
        try:
            soup = self._fetch_page(word)
            if soup is None:
                return False

            # Check if there are any video elements on the page
            videos = soup.find_all('video')
            return len(videos) > 0

        except Exception as e:
            logger.error(f"Error checking if word '{word}' exists: {e}")
            return False

    def get_video_urls(self, word: str) -> List[str]:
        """
        Get all video URLs for a given word

        Args:
            word: The ASL word to look up

        Returns:
            List of video URLs (empty list if word not found)
        """
        soup = self._fetch_page(word)
        if soup is None:
            return []

        video_urls = []

        # Find all source tags within video elements
        sources = soup.find_all('source')
        for source in sources:
            src = source.get('src')
            if src and src.endswith('.mp4'):
                video_urls.append(src)

        logger.info(f"Found {len(video_urls)} video(s) for word '{word}'")
        return video_urls

    def get_video_details(self, word: str) -> List[Dict[str, str]]:
        """
        Get detailed information about all videos for a given word

        Args:
            word: The ASL word to look up

        Returns:
            List of dictionaries containing video details (url, poster, id)
        """
        soup = self._fetch_page(word)
        if soup is None:
            return []

        videos_info = []

        # Find all video elements
        videos = soup.find_all('video')
        for video in videos:
            source = video.find('source')
            if source:
                video_info = {
                    'url': source.get('src', ''),
                    'poster': video.get('poster', ''),
                    'id': video.get('id', ''),
                    'type': source.get('type', 'video/mp4')
                }
                videos_info.append(video_info)

        logger.info(f"Found {len(videos_info)} video(s) with details for word '{word}'")
        return videos_info

    def get_primary_video_url(self, word: str) -> Optional[str]:
        """
        Get the primary (first) video URL for a given word

        Args:
            word: The ASL word to look up

        Returns:
            Primary video URL or None if not found
        """
        video_urls = self.get_video_urls(word)
        return video_urls[0] if video_urls else None
