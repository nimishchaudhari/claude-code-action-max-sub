#!/usr/bin/env python3

import os
import json
import requests
import subprocess
import sys

def refresh_token(refresh_token):
    """Refreshes the Claude OAuth token using a refresh token"""
    
    url = "https://console.anthropic.com/v1/oauth/token"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Claude-Code-Action/1.0",
        "Accept": "application/json"
    }
    
    # The client_id is hardcoded as per the OAuth implementation
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # Check for Cloudflare errors
        if response.status_code == 403:
            error_body = response.text
            if "error code: 1010" in error_body:
                raise Exception(
                    "Cloudflare blocked the request (error 1010). "
                    "The OAuth token refresh endpoint may not be publicly accessible. "
                    "Please ensure you have a valid Claude access token or use API key authentication instead."
                )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_body = e.response.text
            raise Exception(f"Failed to refresh token: HTTP {e.response.status_code} - {error_body}")
        raise Exception(f"Failed to refresh token: {str(e)}")

def update_github_secret(secret_name, secret_value, owner, repo):
    """Updates a GitHub secret using the GitHub CLI"""
    
    try:
        # Use GitHub CLI to update the secret
        cmd = ["gh", "secret", "set", secret_name, "--body", secret_value, "--repo", f"{owner}/{repo}"]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Updated GitHub secret: {secret_name}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to update GitHub secret: {e.stderr}")

def check_token_expired(expires_at):
    """Check if the token has expired or is about to expire"""
    if not expires_at:
        return True
    
    try:
        # Parse the expiration timestamp
        if isinstance(expires_at, str):
            # If it's an ISO format string
            if 'T' in expires_at:
                from datetime import datetime
                expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                current_time = datetime.now(expiry_time.tzinfo)
            else:
                # If it's a Unix timestamp string
                import time
                expiry_time = float(expires_at)
                current_time = time.time()
                return current_time >= expiry_time - 300  # Refresh 5 minutes before expiry
        else:
            # If it's already a number
            import time
            return time.time() >= float(expires_at) - 300  # Refresh 5 minutes before expiry
            
        # For datetime objects, check if expired
        from datetime import timedelta
        return current_time >= expiry_time - timedelta(minutes=5)
    except Exception as e:
        print(f"Warning: Could not parse expiration time: {e}")
        return True  # Assume expired if we can't parse

def main():
    """Main function to refresh token and update GitHub secrets"""
    
    try:
        # Get environment variables
        refresh_token_value = os.environ.get("CLAUDE_REFRESH_TOKEN")
        current_access_token = os.environ.get("CLAUDE_ACCESS_TOKEN")
        expires_at = os.environ.get("CLAUDE_EXPIRES_AT")
        github_repository = os.environ.get("GITHUB_REPOSITORY", "")
        owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
        update_secret = os.environ.get("UPDATE_GITHUB_SECRET", "false").lower() == "true"
        
        if not refresh_token_value:
            raise Exception("CLAUDE_REFRESH_TOKEN environment variable is required")
        
        # Check if token needs refreshing
        if not check_token_expired(expires_at):
            print("✅ Token is still valid, no refresh needed")
            if current_access_token and "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    f.write(f"access_token={current_access_token}\n")
                    f.write(f"expires_at={expires_at}\n")
            return
        
        if "/" in github_repository:
            repo = github_repository.split("/")[1]
        else:
            repo = github_repository
        
        print("🔄 Refreshing Claude OAuth token...")
        
        # Refresh the token
        token_response = refresh_token(refresh_token_value)
        
        if "access_token" not in token_response:
            raise Exception("No access token in response")
        
        access_token = token_response["access_token"]
        new_refresh_token = token_response.get("refresh_token", refresh_token_value)
        expires_in = token_response.get("expires_in", 28800)  # Default 8 hours
        
        # Calculate expiration timestamp
        import time
        new_expires_at = str(int(time.time() + expires_in))
        
        print("✓ Token refreshed successfully")
        print(f"✓ Token expires in {expires_in} seconds")
        
        # Update GitHub secrets if requested
        if update_secret and owner and repo:
            print("📝 Updating GitHub secrets...")
            
            # Update all three secrets
            update_github_secret("CLAUDE_ACCESS_TOKEN", access_token, owner, repo)
            update_github_secret("CLAUDE_EXPIRES_AT", new_expires_at, owner, repo)
            
            # Update refresh token if a new one was provided
            if "refresh_token" in token_response:
                update_github_secret("CLAUDE_REFRESH_TOKEN", token_response["refresh_token"], owner, repo)
        
        # Output for GitHub Actions
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"access_token={access_token}\n")
                f.write(f"refresh_token={new_refresh_token}\n")
                f.write(f"expires_at={new_expires_at}\n")
        else:
            # Legacy output format
            print(f"::set-output name=access_token::{access_token}")
            print(f"::set-output name=refresh_token::{new_refresh_token}")
            print(f"::set-output name=expires_at::{new_expires_at}")
        
        # Mask the token in logs
        print(f"::add-mask::{access_token}")
        
        # Set environment variables for subsequent steps
        if "GITHUB_ENV" in os.environ:
            with open(os.environ["GITHUB_ENV"], "a") as f:
                f.write(f"CLAUDE_ACCESS_TOKEN={access_token}\n")
                f.write(f"CLAUDE_REFRESH_TOKEN={new_refresh_token}\n")
                f.write(f"CLAUDE_EXPIRES_AT={new_expires_at}\n")
        
        print("✅ Token refresh completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()