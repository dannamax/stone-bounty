#!/usr/bin/env python3
"""
Test script for RustChain Mining Status Badge API
"""
import requests
import json

def test_badge_api():
    """Test the badge API endpoint"""
    base_url = "http://localhost:8099"
    
    # Test with a sample wallet
    wallet = "frozen-factorio-ryan"
    url = f"{base_url}/api/badge/{wallet}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Validate response format
        data = response.json()
        expected_keys = ["schemaVersion", "label", "message", "color"]
        for key in expected_keys:
            if key not in data:
                print(f"❌ Missing key: {key}")
                return False
        
        print("✅ Badge API test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_badge_api()