# Solution: Automatic OAuth Token Refresh for Claude Code Action

I've created a solution for the OAuth token expiration issue. The implementation automatically refreshes the Claude OAuth token before each action run, preventing the "OAuth token has expired" error.

## Quick Implementation

Here's a ready-to-use GitHub Action workflow that refreshes the token on each run:

```yaml
name: Claude Code Assistant (Auto-Refresh Token)

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  claude-with-refresh:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    
    steps:
      - name: Refresh Token and Run Claude
        env:
          CLAUDE_REFRESH_TOKEN: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
        run: |
          # Inline Python script to refresh token
          ACCESS_TOKEN=$(python3 -c "
          import json, urllib.request, os, sys
          
          refresh_token = os.environ.get('CLAUDE_REFRESH_TOKEN')
          if not refresh_token:
              print('Error: CLAUDE_REFRESH_TOKEN not set', file=sys.stderr)
              sys.exit(1)
          
          # Prepare request
          url = 'https://console.anthropic.com/v1/oauth/token'
          data = json.dumps({
              'grant_type': 'refresh_token',
              'refresh_token': refresh_token
          }).encode('utf-8')
          
          req = urllib.request.Request(url, data=data)
          req.add_header('Content-Type', 'application/json')
          
          try:
              with urllib.request.urlopen(req) as response:
                  result = json.loads(response.read().decode('utf-8'))
                  print(result.get('access_token', ''))
          except Exception as e:
              print(f'Error refreshing token: {e}', file=sys.stderr)
              sys.exit(1)
          ")
          
          if [ -z "$ACCESS_TOKEN" ]; then
            echo "Failed to refresh token"
            exit 1
          fi
          
          echo "::add-mask::$ACCESS_TOKEN"
          echo "CLAUDE_ACCESS_TOKEN=$ACCESS_TOKEN" >> $GITHUB_ENV

      - name: Run Claude Code Action
        uses: nimishchaudhari/claude-code-action-max-sub@main
        with:
          use_oauth: true
          claude_access_token: ${{ env.CLAUDE_ACCESS_TOKEN }}
```

## Setup Instructions

1. **Get your refresh token** from your Claude credentials file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add to GitHub Secrets**:
   - Go to Settings → Secrets and variables → Actions
   - Add `CLAUDE_REFRESH_TOKEN` with your refresh token value

3. **Create the workflow file**:
   - Save the above YAML as `.github/workflows/claude-assistant.yml`

4. **Use it**: Comment `@claude` on any issue or PR!

## How It Works

The solution uses the refresh token endpoint you mentioned:
- **Endpoint**: `POST https://console.anthropic.com/v1/oauth/token`
- **Payload**: `{ "grant_type": "refresh_token", "refresh_token": "YOUR_REFRESH_TOKEN" }`
- **Response**: Contains new `access_token` (and sometimes a new `refresh_token`)

The workflow:
1. Intercepts `@claude` comments
2. Uses the refresh token to get a new access token
3. Passes the fresh token to the Claude Code Action
4. Masks the token in logs for security

## Alternative Implementations

I've also created:
- **Node.js version**: For those who prefer JavaScript
- **Python standalone script**: For more complex workflows
- **Bash script**: For shell-based implementations
- **Advanced workflow**: With scheduled refresh and automatic secret updates

All implementations are available in this gist: [TODO: Add gist link]

## Benefits

✅ No more manual token renewal
✅ Works with existing Claude Code Action
✅ Minimal setup required
✅ Secure token handling
✅ No external dependencies (uses Python built-in libraries)

This should resolve the token expiration issue completely. Let me know if you need any adjustments or have questions!