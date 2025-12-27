"""
Test the FastAPI endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 80)
    print("TESTING SIGNASL API ENDPOINTS")
    print("=" * 80)

    # Test 1: Root endpoint
    print("\n1. Testing GET / (root)...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Check word endpoint
    print("\n2. Testing GET /api/check/hello...")
    response = requests.get(f"{BASE_URL}/api/check/hello")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Check non-existent word
    print("\n3. Testing GET /api/check/nonexistentword...")
    response = requests.get(f"{BASE_URL}/api/check/nonexistentword12345")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Get video URLs
    print("\n4. Testing GET /api/video-url/world...")
    response = requests.get(f"{BASE_URL}/api/video-url/world")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Found {len(data['video_urls'])} videos")
    print(f"   First URL: {data['video_urls'][0]}")

    # Test 5: Download video
    print("\n5. Testing GET /api/download/world...")
    response = requests.get(f"{BASE_URL}/api/download/world")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Success: {data['success']}")
    print(f"   Message: {data['message']}")
    print(f"   Cached videos: {len(data['cached_videos'])}")

    # Test 6: Batch download
    print("\n6. Testing POST /api/batch/download...")
    batch_request = {
        "words": ["computer", "internet"],
        "force": False
    }
    response = requests.post(f"{BASE_URL}/api/batch/download", json=batch_request)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total words: {data['total_words']}")
    print(f"   Successful: {data['successful']}")
    print(f"   Failed: {data['failed']}")

    # Test 7: List cache
    print("\n7. Testing GET /api/cache/list...")
    response = requests.get(f"{BASE_URL}/api/cache/list")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total videos: {data['total_videos']}")
    print(f"   Cache size: {data['cache_size_mb']} MB")

    # Test 8: Clear cache for specific word
    print("\n8. Testing DELETE /api/cache/clear?word=hello...")
    response = requests.delete(f"{BASE_URL}/api/cache/clear?word=hello")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Deleted: {data['deleted_count']}")
    print(f"   Message: {data['message']}")

    print("\n" + "=" * 80)
    print("API TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server. Is it running on port 8000?")
    except Exception as e:
        print(f"ERROR: {e}")
