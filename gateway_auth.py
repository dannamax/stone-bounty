#!/usr/bin/env python3
"""
Gateway authentication configuration for PlanSuite isolated session execution
"""

import os
import json

def configure_gateway_auth():
    """Configure gateway authentication for sessions_spawn"""
    
    # Get gateway token from config
    gateway_config_path = "/home/admin/.openclaw/openclaw.json"
    
    if os.path.exists(gateway_config_path):
        with open(gateway_config_path, 'r') as f:
            config = json.load(f)
        
        gateway_token = config.get('gateway', {}).get('auth', {}).get('token')
        if gateway_token:
            # Set environment variable for sessions_spawn
            os.environ['GATEWAY_TOKEN'] = gateway_token
            print(f"✅ Gateway token configured: {gateway_token[:8]}...")
            return gateway_token
        else:
            print("❌ Gateway token not found in config")
            return None
    else:
        print("❌ Gateway config file not found")
        return None

def test_gateway_connection():
    """Test gateway connection"""
    try:
        # Test basic gateway connectivity
        import requests
        response = requests.get("http://localhost:19564/health", timeout=5)
        if response.status_code == 200:
            print("✅ Gateway connection successful")
            return True
        else:
            print(f"❌ Gateway health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gateway connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Configuring gateway authentication...")
    token = configure_gateway_auth()
    if token:
        print("🔍 Testing gateway connection...")
        success = test_gateway_connection()
        if success:
            print("🎉 Gateway authentication configured successfully!")
        else:
            print("⚠️  Gateway connection test failed, but token is set")
    else:
        print("❌ Failed to configure gateway authentication")