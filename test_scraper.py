"""
Test script to inspect SignASL.org HTML structure
"""
import requests
from bs4 import BeautifulSoup

def inspect_signasl_page(word):
    url = f"https://www.signasl.org/sign/{word}"
    print(f"Fetching: {url}\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        print("=" * 80)
        print("VIDEO ELEMENTS FOUND:")
        print("=" * 80)

        # Look for video tags
        videos = soup.find_all('video')
        print(f"\nFound {len(videos)} video tag(s)")
        for i, video in enumerate(videos, 1):
            print(f"\nVideo {i}:")
            print(video.prettify()[:500])

        # Look for source tags
        sources = soup.find_all('source')
        print(f"\n\nFound {len(sources)} source tag(s)")
        for i, source in enumerate(sources, 1):
            print(f"\nSource {i}:")
            print(f"  src: {source.get('src')}")
            print(f"  type: {source.get('type')}")

        # Look for any mp4/video URLs in the page
        print("\n" + "=" * 80)
        print("SEARCHING FOR VIDEO URLs IN PAGE:")
        print("=" * 80)

        page_text = str(soup)
        video_extensions = ['.mp4', '.webm', '.mov', '.avi', '.m4v']

        for ext in video_extensions:
            if ext in page_text.lower():
                print(f"\nFound '{ext}' in page content!")
                # Find context around the extension
                idx = page_text.lower().find(ext)
                context = page_text[max(0, idx-100):min(len(page_text), idx+100)]
                print(f"Context: ...{context}...")

        # Look for iframes
        iframes = soup.find_all('iframe')
        print(f"\n\nFound {len(iframes)} iframe(s)")
        for i, iframe in enumerate(iframes, 1):
            print(f"\nIframe {i}:")
            print(f"  src: {iframe.get('src')}")

        # Look for specific div classes that might contain videos
        print("\n" + "=" * 80)
        print("SEARCHING FOR COMMON VIDEO CONTAINER CLASSES:")
        print("=" * 80)

        video_divs = soup.find_all('div', class_=lambda x: x and ('video' in x.lower() or 'player' in x.lower()))
        print(f"\nFound {len(video_divs)} div(s) with video-related classes")
        for i, div in enumerate(video_divs[:3], 1):  # Show first 3
            print(f"\nDiv {i}:")
            print(f"  class: {div.get('class')}")
            print(div.prettify()[:300])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")

if __name__ == "__main__":
    # Test with a common word
    inspect_signasl_page("hello")
