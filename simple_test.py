import requests
import json

def test_api():
    """Simple API test"""
    try:
        # Test basic endpoint
        print("Testing API health...")
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("API is running successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return False

if __name__ == "__main__":
    test_api()