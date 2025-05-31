#!/usr/bin/env python3
"""
Local test script for OAuth token refresh.
Set environment variables before running:
- CLAUDE_ACCESS_TOKEN
- CLAUDE_REFRESH_TOKEN  
- CLAUDE_EXPIRES_AT
"""

import os
import json
import requests
import sys
import time

def test_refresh():
    """Test the OAuth token refresh locally"""
    
    # Get environment variables
    access_token = os.environ.get("CLAUDE_ACCESS_TOKEN")
    refresh_token = os.environ.get("CLAUDE_REFRESH_TOKEN")
    expires_at = os.environ.get("CLAUDE_EXPIRES_AT")
    
    print("=== Claude OAuth Token Refresh Test ===")
    print(f"Access Token: {'✓ Set' if access_token else '✗ Not set'}")
    print(f"Refresh Token: {'✓ Set' if refresh_token else '✗ Not set'}")
    print(f"Expires At: {expires_at if expires_at else '✗ Not set'}")
    
    if not refresh_token:
        print("\n❌ Error: CLAUDE_REFRESH_TOKEN is required")
        return False
    
    # Check if expired
    if expires_at:
        try:
            current_time = time.time()
            expiry_time = float(expires_at)
            time_left = expiry_time - current_time
            
            if time_left > 0:
                hours_left = time_left / 3600
                print(f"\n⏰ Token expires in {hours_left:.2f} hours")
                if time_left > 300:  # More than 5 minutes
                    print("✅ Token is still valid")
            else:
                print("\n⚠️  Token has expired")
        except Exception as e:
            print(f"\n⚠️  Could not parse expiration: {e}")
    
    # Test refresh
    print("\n🔄 Testing token refresh...")
    
    url = "https://console.anthropic.com/v1/oauth/token"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Claude-Code-Action/1.0"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Token refresh successful!")
            print(f"New access token: {result.get('access_token', '')[:20]}...")
            if "expires_in" in result:
                print(f"Expires in: {result['expires_in']} seconds ({result['expires_in']/3600:.2f} hours)")
            if "refresh_token" in result:
                print("New refresh token provided: Yes")
            return True
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_refresh()
    sys.exit(0 if success else 1)