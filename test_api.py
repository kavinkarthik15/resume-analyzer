#!/usr/bin/env python3
"""
Test the Resume Analyzer API
"""

import requests

def test_api():
    # Test health endpoint
    print("Testing health endpoint...")
    response = requests.get("http://127.0.0.1:8000/health")
    print(f"Health: {response.json()}")

    # Test root endpoint
    print("Testing root endpoint...")
    response = requests.get("http://127.0.0.1:8000/")
    print(f"Root: {response.json()}")

    # Test analyze endpoint with a resume
    print("Testing analyze endpoint...")
    with open("phase13_resumes/strong/senior_data_scientist_7years.txt", "rb") as f:
        files = {"file": ("resume.txt", f, "text/plain")}
        response = requests.post("http://127.0.0.1:8000/analyze", files=files)

    if response.status_code == 200:
        result = response.json()
        print("✅ Analysis successful!")
        print(f"Prediction: {result.get('prediction')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Decision: {result.get('decision')}")
        print(f"Top factors: {result.get('top_factors')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_api()