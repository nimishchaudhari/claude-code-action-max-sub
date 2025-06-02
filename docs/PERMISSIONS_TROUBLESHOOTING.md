# GitHub Actions Permissions Troubleshooting

This guide helps solve common permission issues when setting up the Claude Code Action for commits and pull request creation.

## Common Permission Issues

### Issue: Claude Cannot Commit or Create Pull Requests

**Symptoms:**

- Workflow runs but Claude cannot push commits
- Error messages about permission denied for repository operations
- Action fails when trying to create branches or PRs

**Root Cause:**
Missing or insufficient GitHub Actions permissions in the workflow configuration.

### The Solution

Add the following comprehensive permissions block to your workflow YAML file:

```yaml
permissions:
  contents: write # Required for pushing commits and creating branches
  issues: write # Required for commenting on issues
  pull-requests: write # Required for creating and managing PRs
  id-token: write # Required for OIDC authentication (if using OAuth)
```

### Complete Working Workflow Example

Here's a tested workflow configuration that includes all necessary permissions:

```yaml
name: Claude Code Assistant with Auto Token Refresh

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  workflow_dispatch:
  schedule:
    - cron: "0 */6 * * *"

permissions:
  contents: write
  issues: write
  pull-requests: write
  id-token: write

jobs:
  claude-code-action:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      # Token refresh steps here...

      - name: Run Claude Code Action
        uses: nimishchaudhari/claude-code-action-max-sub@main
        with:
          use_oauth: true
          claude_access_token: ${{ steps.refresh_token.outputs.access_token }}
          allowed_tools: "Task,Bash,Glob,Grep,LS,Read,Edit,MultiEdit,Write,NotebookRead,NotebookEdit,TodoRead,TodoWrite,mcp__github_file_ops__commit_files,mcp__github_file_ops__delete_files,mcp__github__add_issue_comment,mcp__github__add_pull_request_review_comment,mcp__github__create_branch,mcp__github__create_issue,mcp__github__create_or_update_file,mcp__github__create_pull_request,mcp__github__create_pull_request_review,mcp__github__create_repository,mcp__github__delete_file,mcp__github__fork_repository,mcp__github__get_code_scanning_alert,mcp__github__get_commit,mcp__github__get_file_contents,mcp__github__get_issue,mcp__github__get_issue_comments,mcp__github__get_me,mcp__github__get_pull_request,mcp__github__get_pull_request_comments,mcp__github__get_pull_request_files,mcp__github__get_pull_request_reviews,mcp__github__get_pull_request_status,mcp__github__get_secret_scanning_alert,mcp__github__get_tag,mcp__github__list_branches,mcp__github__list_code_scanning_alerts,mcp__github__list_commits,mcp__github__list_issues,mcp__github__list_pull_requests,mcp__github__list_secret_scanning_alerts,mcp__github__list_tags,mcp__github__merge_pull_request,mcp__github__push_files,mcp__github__search_code,mcp__github__search_issues,mcp__github__search_repositories,mcp__github__search_users,mcp__github__update_issue,mcp__github__update_issue_comment,mcp__github__update_pull_request,mcp__github__update_pull_request_branch,mcp__github__update_pull_request_comment"
```

## Additional Repository Settings

### Enable Actions Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**

### Required GitHub Secrets

For OAuth authentication, ensure these secrets are configured:

- `CLAUDE_REFRESH_TOKEN` - Your Claude OAuth refresh token
- `CLAUDE_ACCESS_TOKEN` - Current access token (auto-updated)
- `CLAUDE_EXPIRES_AT` - Token expiration timestamp (auto-updated)
- `PAT_TOKEN` - (Optional) Personal Access Token with 'repo' scope for automatic secret updates via refresh workflow

## Debugging Permission Issues

### Check Workflow Logs

1. Go to **Actions** tab in your repository
2. Click on the failed workflow run
3. Expand the step that failed
4. Look for permission-related error messages

### Common Error Messages and Solutions

| Error Message                            | Solution                                        |
| ---------------------------------------- | ----------------------------------------------- |
| `Resource not accessible by integration` | Add missing permissions to workflow             |
| `Permission denied (publickey)`          | Check token permissions and repository settings |
| `403 Forbidden`                          | Verify token has correct scopes                 |
| `Bad credentials`                        | Regenerate and update token                     |

### Test Your Setup

Create a simple test workflow to verify permissions:

```yaml
name: Test Permissions
on: workflow_dispatch

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test write access
        run: |
          echo "Testing permissions" > test-file.txt
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add test-file.txt
          git commit -m "Test commit"
          git push
```

## OAuth vs API Key Authentication

### OAuth Authentication (Recommended)

- Requires refresh token management
- Uses `use_oauth: true` parameter
- Needs `id-token: write` permission for OIDC

#### Manual Token Refresh Workflow

The repository includes a [`refresh-oauth-token.yml`](.github/workflows/refresh-oauth-token.yml) workflow for manually refreshing OAuth tokens when needed.

**Prerequisites:**
- `CLAUDE_REFRESH_TOKEN` secret must be set with a valid refresh token

**Optional but Recommended:**
- `PAT_TOKEN` secret: Personal Access Token with 'repo' scope for updating secrets
- Without this, the workflow will refresh tokens but cannot update repository secrets automatically

**Usage:**
1. Go to **Actions** tab in your repository
2. Select **"Refresh OAuth Token"** workflow
3. Click **"Run workflow"**
4. Choose whether to update secrets (requires PAT_TOKEN)

**Setting up PAT_TOKEN:**
1. Go to GitHub **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Create a new token with 'repo' scope for your repository
3. Add the token as a repository secret named `PAT_TOKEN`
4. This allows the refresh workflow to automatically update `CLAUDE_ACCESS_TOKEN` and `CLAUDE_EXPIRES_AT` secrets

### API Key Authentication (Fallback)

- Uses Anthropic API key directly
- Set `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
- Simpler setup but may have rate limits

## Best Practices

1. **Use minimal required permissions** - Only add what's needed
2. **Regularly rotate tokens** - Set up automatic refresh
3. **Monitor workflow runs** - Check for permission errors
4. **Test in a fork first** - Verify setup before production use
5. **Keep secrets secure** - Never commit tokens to repository

## Getting Help

If you continue experiencing permission issues:

1. Check the [main setup guide](SETUP_GUIDE.md)
2. Review the [working workflow example](.github/workflows/claude-auto-refresh-action.yml)
3. Use the [manual token refresh workflow](.github/workflows/refresh-oauth-token.yml) if tokens need refreshing
4. Open an issue with your specific error message
5. Include relevant workflow logs (redact any sensitive information)

## Success Indicators

Your setup is working correctly when:

- ✅ Claude responds to `@claude` comments
- ✅ Claude can create commits and push changes
- ✅ Pull requests are created automatically when needed
- ✅ Token refresh happens automatically
- ✅ No permission errors in workflow logs
