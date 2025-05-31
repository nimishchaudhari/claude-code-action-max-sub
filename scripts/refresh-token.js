#!/usr/bin/env node

const https = require("https");
const { execSync } = require("child_process");

/**
 * Refreshes the Claude OAuth token using a refresh token
 */
async function refreshToken(refreshToken) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      grant_type: "refresh_token",
      refresh_token: refreshToken,
    });

    const options = {
      hostname: "console.anthropic.com",
      port: 443,
      path: "/v1/oauth/token",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": data.length,
      },
    };

    const req = https.request(options, (res) => {
      let responseData = "";

      res.on("data", (chunk) => {
        responseData += chunk;
      });

      res.on("end", () => {
        if (res.statusCode === 200) {
          try {
            const parsed = JSON.parse(responseData);
            resolve(parsed);
          } catch (error) {
            reject(new Error(`Failed to parse response: ${error.message}`));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
        }
      });
    });

    req.on("error", (error) => {
      reject(new Error(`Request failed: ${error.message}`));
    });

    req.write(data);
    req.end();
  });
}

/**
 * Updates a GitHub secret
 */
function updateGitHubSecret(secretName, secretValue, owner, repo) {
  try {
    // Use GitHub CLI to update the secret
    execSync(
      `gh secret set ${secretName} --body "${secretValue}" --repo ${owner}/${repo}`,
      {
        stdio: "inherit",
      },
    );
    console.log(`✓ Updated GitHub secret: ${secretName}`);
  } catch (error) {
    throw new Error(`Failed to update GitHub secret: ${error.message}`);
  }
}

async function main() {
  try {
    // Get environment variables
    const refreshToken = process.env.CLAUDE_REFRESH_TOKEN;
    const owner = process.env.GITHUB_REPOSITORY_OWNER;
    const repo = process.env.GITHUB_REPOSITORY.split("/")[1];

    if (!refreshToken) {
      throw new Error("CLAUDE_REFRESH_TOKEN environment variable is required");
    }

    console.log("🔄 Refreshing Claude OAuth token...");

    // Refresh the token
    const tokenResponse = await refreshToken(refreshToken);

    if (!tokenResponse.access_token) {
      throw new Error("No access token in response");
    }

    console.log("✓ Token refreshed successfully");

    // Update GitHub secrets
    if (process.env.UPDATE_GITHUB_SECRET === "true") {
      console.log("📝 Updating GitHub secrets...");

      // Update access token
      updateGitHubSecret(
        "CLAUDE_ACCESS_TOKEN",
        tokenResponse.access_token,
        owner,
        repo,
      );

      // Update refresh token if a new one was provided
      if (tokenResponse.refresh_token) {
        updateGitHubSecret(
          "CLAUDE_REFRESH_TOKEN",
          tokenResponse.refresh_token,
          owner,
          repo,
        );
      }
    }

    // Output the new token for the current workflow
    console.log(
      `::set-output name=access_token::${tokenResponse.access_token}`,
    );

    // Also set it as an environment variable for subsequent steps
    console.log(`::add-mask::${tokenResponse.access_token}`);
    console.log(
      `CLAUDE_ACCESS_TOKEN=${tokenResponse.access_token} >> $GITHUB_ENV`,
    );
  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  }
}

main();
