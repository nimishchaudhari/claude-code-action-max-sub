# Claude OAuth Token Auto-Refresh Setup Guide

This solution automatically refreshes your Claude OAuth token before running the Claude Code Action, preventing token expiration issues.

## Prerequisites

1. A Claude account with OAuth access
2. Your initial refresh token
3. A GitHub repository where you want to use Claude Code Action

## Setup Instructions

### Step 1: Get Your Initial Tokens

1. Authenticate with Claude CLI locally:
   ```bash
   claude auth --method oauth
   ```

2. Find your refresh token in the credentials file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. Look for the `refresh_token` field in the JSON file.

### Step 2: Add GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `CLAUDE_REFRESH_TOKEN`: Your refresh token from Step 1
   - `CLAUDE_ACCESS_TOKEN`: Your initial access token (will be auto-updated)

### Step 3: Add the Workflow

1. Create the directory structure in your repository:
   ```
   .github/
   └── workflows/
       └── claude-code-with-refresh.yml
   ```

2. Copy the `claude-code-with-refresh.yml` file to your repository

3. Create a `scripts/` directory and add either:
   - `refresh-token.js` (Node.js version)
   - `refresh-token.py` (Python version)

### Step 4: Configure Permissions

Ensure your GitHub Actions have the necessary permissions:

1. Go to Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"

## Usage

### Triggering Claude

Once set up, you can trigger Claude by commenting on issues or pull requests:

```
@claude Can you help me implement this feature?
```

### Manual Token Refresh

To manually refresh the token, you can trigger the workflow from the Actions tab.

## Alternative: Python-based Workflow

If you prefer Python over Node.js, use this workflow instead:

```yaml
name: Claude Code Assistant with Token Refresh (Python)

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

permissions:
  contents: write
  issues: write
  pull-requests: write
  actions: write
  secrets: write

jobs:
  claude-code-action:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Refresh Claude OAuth Token
        id: refresh_token
        env:
          CLAUDE_REFRESH_TOKEN: ${{ secrets.CLAUDE_REFRESH_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          UPDATE_GITHUB_SECRET: 'true'
        run: |
          # Download the refresh token script
          curl -o refresh-token.py https://raw.githubusercontent.com/${{ github.repository }}/main/scripts/refresh-token.py
          
          # Make it executable and run it
          chmod +x refresh-token.py
          python refresh-token.py

      - name: Run Claude Code Action
        uses: nimishchaudhari/claude-code-action-max-sub@main
        with:
          use_oauth: true
          claude_access_token: ${{ steps.refresh_token.outputs.access_token || secrets.CLAUDE_ACCESS_TOKEN }}
```

## Troubleshooting

### Token Refresh Fails

1. Check that your `CLAUDE_REFRESH_TOKEN` is valid
2. Ensure the GitHub token has permissions to update secrets
3. Check the Actions logs for specific error messages

### Claude Action Doesn't Trigger

1. Ensure the comment contains `@claude`
2. Check that the workflow has the correct permissions
3. Verify the action is enabled in your repository settings

### Scheduled Refresh Not Working

1. GitHub Actions scheduled workflows might be disabled if the repository is inactive
2. Check the Actions tab to see if the scheduled workflow is running
3. Consider using a different scheduling solution if needed

## Security Considerations

1. **Never commit tokens directly to your repository**
2. Always use GitHub Secrets for sensitive values
3. The refresh token is long-lived but should still be rotated periodically
4. Monitor your Actions logs to ensure tokens aren't being exposed

## Contributing

If you encounter issues or have improvements, please open an issue at:
https://github.com/grll/claude-code-action/issues