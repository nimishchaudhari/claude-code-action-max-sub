#!/bin/bash

# Claude OAuth Token Refresh Script
# This script refreshes a Claude OAuth token using a refresh token

set -e

# Function to refresh token
refresh_token() {
    local refresh_token="$1"
    local response
    
    echo "🔄 Refreshing Claude OAuth token..."
    
    # Make the POST request to refresh the token
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"grant_type\":\"refresh_token\",\"refresh_token\":\"$refresh_token\"}" \
        "https://console.anthropic.com/v1/oauth/token")
    
    # Check if curl succeeded
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to make request to token endpoint"
        exit 1
    fi
    
    # Extract access token using grep and sed (works on most systems)
    local access_token=$(echo "$response" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
    
    if [ -z "$access_token" ]; then
        echo "❌ Error: No access token in response"
        echo "Response: $response"
        exit 1
    fi
    
    echo "✓ Token refreshed successfully"
    
    # Extract refresh token if present
    local new_refresh_token=$(echo "$response" | grep -o '"refresh_token":"[^"]*' | sed 's/"refresh_token":"//')
    
    # Output for GitHub Actions
    if [ -n "$GITHUB_OUTPUT" ]; then
        echo "access_token=$access_token" >> "$GITHUB_OUTPUT"
        if [ -n "$new_refresh_token" ]; then
            echo "new_refresh_token=$new_refresh_token" >> "$GITHUB_OUTPUT"
        fi
    else
        # Legacy output format
        echo "::set-output name=access_token::$access_token"
        if [ -n "$new_refresh_token" ]; then
            echo "::set-output name=new_refresh_token::$new_refresh_token"
        fi
    fi
    
    # Mask the token in logs
    echo "::add-mask::$access_token"
    
    # Set environment variable for subsequent steps
    if [ -n "$GITHUB_ENV" ]; then
        echo "CLAUDE_ACCESS_TOKEN=$access_token" >> "$GITHUB_ENV"
    fi
}

# Function to update GitHub secret using gh CLI
update_github_secret() {
    local secret_name="$1"
    local secret_value="$2"
    local owner="$3"
    local repo="$4"
    
    if command -v gh &> /dev/null; then
        echo "📝 Updating GitHub secret: $secret_name"
        echo "$secret_value" | gh secret set "$secret_name" --repo "$owner/$repo"
        echo "✓ Updated GitHub secret: $secret_name"
    else
        echo "⚠️  Warning: gh CLI not found, skipping secret update"
    fi
}

# Main execution
main() {
    # Get environment variables
    REFRESH_TOKEN="${CLAUDE_REFRESH_TOKEN}"
    UPDATE_SECRET="${UPDATE_GITHUB_SECRET:-false}"
    OWNER="${GITHUB_REPOSITORY_OWNER}"
    REPO_FULL="${GITHUB_REPOSITORY}"
    
    # Extract repo name from full repository path
    if [[ "$REPO_FULL" == *"/"* ]]; then
        REPO="${REPO_FULL#*/}"
    else
        REPO="$REPO_FULL"
    fi
    
    # Check for required refresh token
    if [ -z "$REFRESH_TOKEN" ]; then
        echo "❌ Error: CLAUDE_REFRESH_TOKEN environment variable is required"
        exit 1
    fi
    
    # Refresh the token
    refresh_token "$REFRESH_TOKEN"
    
    # Update GitHub secrets if requested
    if [ "$UPDATE_SECRET" = "true" ] && [ -n "$OWNER" ] && [ -n "$REPO" ]; then
        # Note: This requires additional parsing of the response
        # For production use, consider using jq for JSON parsing
        echo "⚠️  Note: Automatic secret update requires manual implementation or jq"
    fi
    
    echo "✅ Token refresh completed successfully"
}

# Run main function
main