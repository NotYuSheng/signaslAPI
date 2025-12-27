"""
Test the full scraper functionality
"""
from scraper.signasl_scraper import SignASLScraper
from scraper.video_downloader import VideoDownloader

def test_scraper():
    print("=" * 80)
    print("TESTING SIGNASL SCRAPER")
    print("=" * 80)

    scraper = SignASLScraper()
    downloader = VideoDownloader()

    # Test 1: Check if word exists
    print("\n1. Testing word_exists()...")
    words_to_test = ["hello", "world", "thank-you", "nonexistentword12345"]

    for word in words_to_test:
        exists = scraper.word_exists(word)
        print(f"   '{word}' exists: {exists}")

    # Test 2: Get video URLs
    print("\n2. Testing get_video_urls()...")
    word = "hello"
    video_urls = scraper.get_video_urls(word)
    print(f"   Found {len(video_urls)} videos for '{word}':")
    for i, url in enumerate(video_urls[:3], 1):  # Show first 3
        print(f"   {i}. {url}")

    # Test 3: Get primary video URL
    print("\n3. Testing get_primary_video_url()...")
    primary_url = scraper.get_primary_video_url(word)
    print(f"   Primary URL for '{word}': {primary_url}")

    # Test 4: Get video details
    print("\n4. Testing get_video_details()...")
    details = scraper.get_video_details(word)
    print(f"   Found {len(details)} videos with details:")
    for i, detail in enumerate(details[:2], 1):  # Show first 2
        print(f"   Video {i}:")
        print(f"     ID: {detail['id']}")
        print(f"     URL: {detail['url'][:60]}...")
        print(f"     Poster: {detail['poster'][:60]}...")

    # Test 5: Download a video
    print("\n5. Testing video download...")
    if video_urls:
        first_url = video_urls[0]
        cache_path = downloader.download_video(word, first_url)
        if cache_path:
            print(f"   Successfully downloaded to: {cache_path}")
            print(f"   Video is cached: {downloader.is_cached(word, first_url)}")
        else:
            print("   Failed to download video")

    # Test 6: List cached videos
    print("\n6. Testing cache listing...")
    cached = downloader.list_all_cached()
    print(f"   Total cached videos: {len(cached)}")
    cache_size = downloader.get_cache_size()
    print(f"   Cache size: {cache_size / (1024*1024):.2f} MB")

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_scraper()
