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
        "Content-Type": "application/json"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
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

def main():
    """Main function to refresh token and update GitHub secrets"""
    
    try:
        # Get environment variables
        refresh_token_value = os.environ.get("CLAUDE_REFRESH_TOKEN")
        github_repository = os.environ.get("GITHUB_REPOSITORY", "")
        owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
        update_secret = os.environ.get("UPDATE_GITHUB_SECRET", "false").lower() == "true"
        
        if not refresh_token_value:
            raise Exception("CLAUDE_REFRESH_TOKEN environment variable is required")
        
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
        print("✓ Token refreshed successfully")
        
        # Update GitHub secrets if requested
        if update_secret and owner and repo:
            print("📝 Updating GitHub secrets...")
            
            # Update access token
            update_github_secret("CLAUDE_ACCESS_TOKEN", access_token, owner, repo)
            
            # Update refresh token if a new one was provided
            if "refresh_token" in token_response:
                update_github_secret("CLAUDE_REFRESH_TOKEN", token_response["refresh_token"], owner, repo)
        
        # Output for GitHub Actions
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"access_token={access_token}\n")
        else:
            # Legacy output format
            print(f"::set-output name=access_token::{access_token}")
        
        # Mask the token in logs
        print(f"::add-mask::{access_token}")
        
        # Set environment variable for subsequent steps
        if "GITHUB_ENV" in os.environ:
            with open(os.environ["GITHUB_ENV"], "a") as f:
                f.write(f"CLAUDE_ACCESS_TOKEN={access_token}\n")
        
        print("✅ Token refresh completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()