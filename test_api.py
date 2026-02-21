#!/usr/bin/env python3
"""
Simple test script to demonstrate the API workflow.
Make sure the server is running before executing this script.
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint response:")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health check response:")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_api_info():
    """Test the API info endpoint"""
    response = requests.get(f"{BASE_URL}/api/v1")
    print("API info response:")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_list_textbooks():
    """Test listing textbooks"""
    response = requests.get(f"{BASE_URL}/api/v1/textbooks/")
    print("List textbooks response:")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def main():
    """Run all tests"""
    print("=" * 50)
    print("AI Teaching Assistant API Test")
    print("=" * 50)
    print()
    
    try:
        test_root()
        test_health()
        test_api_info()
        test_list_textbooks()
        
        print("\n✅ All tests completed successfully!")
        print("\n📚 Next steps:")
        print("1. Set your OpenAI API key in the .env file")
        print("2. Upload a PDF textbook using the /api/v1/textbooks/upload endpoint")
        print("3. Extract table of contents pages")
        print("4. Detect chapters using AI")
        print("5. Create chapters with page ranges")
        print("\n📖 Visit http://localhost:8000/docs for interactive API documentation")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the server is running with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()