# Claude OAuth Token Auto-Refresh for GitHub Actions

This repository provides solutions to automatically refresh Claude OAuth tokens in GitHub Actions, solving the token expiration issue reported in [grll/claude-code-action#2](https://github.com/grll/claude-code-action/issues/2).

## Quick Start

### Option 1: Simple Refresh (Recommended for most users)

This option refreshes the token on each run without updating GitHub secrets.

1. **Add your refresh token to GitHub Secrets:**

   - Go to Settings → Secrets and variables → Actions
   - Add `CLAUDE_REFRESH_TOKEN` with your refresh token value

2. **Create `.github/workflows/claude-assistant.yml`:**

   ```yaml
   name: Claude Code Assistant (Simple Token Refresh)

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

3. **Use it:** Comment `@claude` on any issue or PR!

### Option 2: Advanced with Auto-Update (For power users)

This option includes scheduled refreshes and automatically updates GitHub secrets when new refresh tokens are issued.

Use the `claude-auto-refresh-action.yml` file which includes:

- Automatic token refresh before each Claude run
- Scheduled refresh every 6 hours
- Automatic secret updates when new refresh tokens are issued
- Manual trigger support

### Option 3: Custom Implementation

For custom implementations, use the provided scripts:

- **Node.js**: `refresh-token.js`
- **Python**: `refresh-token.py`

## Getting Your Refresh Token

1. Install Claude CLI and authenticate:

   ```bash
   npm install -g @anthropic-ai/claude-cli
   claude auth --method oauth
   ```

2. Find your refresh token:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. Look for the `refresh_token` field in the JSON file

## How It Works

1. **Token Expiration Problem**: Claude OAuth access tokens expire after ~8-24 hours
2. **Solution**: Use the refresh token to get a new access token before each Claude action
3. **API Endpoint**: `POST https://console.anthropic.com/v1/oauth/token`
4. **Required Parameters**:
   - `grant_type`: "refresh_token"
   - `refresh_token`: Your refresh token
   - `client_id`: "9d1c250a-e61b-44d9-88ed-5944d1962f5e" (hardcoded)
5. **Token Management**: The workflow tracks token expiration using `CLAUDE_EXPIRES_AT` and only refreshes when needed

### OAuth Implementation Details

- **Expiration Check**: Tokens are refreshed 5 minutes before expiration
- **Secret Updates**: All three secrets (ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES_AT) are automatically updated
- **Encryption**: Uses PyNaCl library for GitHub secret encryption
- **Fallback**: If OAuth fails, the workflow can fall back to API key authentication

## Comparison of Options

| Feature               | Simple Refresh | Auto-Update | Custom Scripts   |
| --------------------- | -------------- | ----------- | ---------------- |
| Ease of setup         | ⭐⭐⭐⭐⭐     | ⭐⭐⭐      | ⭐⭐             |
| Token always fresh    | ✅             | ✅          | ✅               |
| Scheduled refresh     | ❌             | ✅          | Configurable     |
| Auto-update secrets   | ❌             | ✅          | Configurable     |
| External dependencies | None           | None        | Node.js/Python   |
| Best for              | Most users     | Power users | Custom workflows |

## Alternative: API Key Authentication

If OAuth token refresh is not working due to endpoint restrictions, use API key authentication:

1. **Get an API Key**:

   - Go to [console.anthropic.com](https://console.anthropic.com)
   - Navigate to API Keys section
   - Create a new API key

2. **Add to GitHub Secrets**:

   - Add `ANTHROPIC_API_KEY` to your repository secrets

3. **Use the API Key Workflow**:

   ```yaml
   name: Claude Code Assistant (API Key)

   on:
     issue_comment:
       types: [created]

   permissions:
     contents: write
     issues: write
     pull-requests: write

   jobs:
     claude:
       if: contains(github.event.comment.body, '@claude')
       runs-on: ubuntu-latest

       steps:
         - name: Run Claude Code Action
           uses: nimishchaudhari/claude-code-action-max-sub@main
           with:
             anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
   ```

## Troubleshooting

### Common Issues

1. **"OAuth token has expired"**

   - Ensure `CLAUDE_REFRESH_TOKEN` is set correctly
   - Check if the refresh token itself has expired (rare)
   - Consider using API key authentication as an alternative

2. **"Failed to refresh token" or "HTTP 403: error code: 1010"**

   - This is a Cloudflare protection error on the OAuth endpoint
   - **Solution**: Use API key authentication instead of OAuth
   - Add `ANTHROPIC_API_KEY` to your secrets and use the API key workflow

3. **"Error refreshing token"**

   - The OAuth refresh endpoint may be temporarily unavailable
   - Fallback to API key authentication is recommended

4. **Claude doesn't respond**
   - Ensure comment contains `@claude`
   - Check workflow permissions are set correctly

### Debug Tips

- Add `set -x` to bash scripts for verbose output
- Check the Actions tab in GitHub for workflow runs
- Use `workflow_dispatch` to manually trigger and test

## Security Best Practices

1. **Never commit tokens** to your repository
2. **Use GitHub Secrets** for all sensitive values
3. **Rotate refresh tokens** periodically
4. **Monitor Actions logs** to ensure tokens aren't exposed
5. **Limit workflow permissions** to minimum required

## Contributing

Found an issue or have an improvement? Please:

1. Open an issue at [grll/claude-code-action](https://github.com/grll/claude-code-action/issues)
2. Submit a PR with your improvements

## License

These scripts are provided as-is for use with the Claude Code Action. See the original repository for license details.
