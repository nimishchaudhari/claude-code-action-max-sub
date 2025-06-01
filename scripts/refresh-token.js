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
      client_id: "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
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
    return true;
  } catch (error) {
    // Check if it's a permission error
    if (error.message.includes("403") || error.message.includes("not accessible")) {
      console.warn(`⚠️  Cannot update ${secretName}: Insufficient permissions. This requires a Personal Access Token with admin rights.`);
      return false;
    }
    throw new Error(`Failed to update GitHub secret: ${error.message}`);
  }
}

async function main() {
  try {
    // Get environment variables
    const refreshTokenValue = process.env.CLAUDE_REFRESH_TOKEN;
    const owner = process.env.GITHUB_REPOSITORY_OWNER;
    const repo = process.env.GITHUB_REPOSITORY.split("/")[1];

    if (!refreshTokenValue) {
      throw new Error("CLAUDE_REFRESH_TOKEN environment variable is required");
    }

    console.log("🔄 Refreshing Claude OAuth token...");

    // Refresh the token
    const tokenResponse = await refreshToken(refreshTokenValue);

    if (!tokenResponse.access_token) {
      throw new Error("No access token in response");
    }

    console.log("✓ Token refreshed successfully");

    // Update GitHub secrets
    if (process.env.UPDATE_GITHUB_SECRET === "true") {
      console.log("📝 Updating GitHub secrets...");

      let secretsUpdated = true;

      // Update access token
      const accessTokenUpdated = updateGitHubSecret(
        "CLAUDE_ACCESS_TOKEN",
        tokenResponse.access_token,
        owner,
        repo,
      );

      // Update refresh token if a new one was provided
      if (tokenResponse.refresh_token) {
        const refreshTokenUpdated = updateGitHubSecret(
          "CLAUDE_REFRESH_TOKEN",
          tokenResponse.refresh_token,
          owner,
          repo,
        );
        secretsUpdated = accessTokenUpdated && refreshTokenUpdated;
      } else {
        secretsUpdated = accessTokenUpdated;
      }

      if (!secretsUpdated) {
        console.log("\n⚠️  Secrets were not updated due to insufficient permissions.");
        console.log("💡 To update secrets automatically, use a Personal Access Token with repo permissions.");
        console.log("   Add it as a secret named 'PAT_TOKEN' and update the workflow to use it.\n");
      }
    }

    // Calculate expiration timestamp
    const expiresIn = tokenResponse.expires_in || 28800; // Default 8 hours
    const expiresAt = Math.floor(Date.now() / 1000) + expiresIn;
    
    console.log(`✓ Token expires in ${expiresIn} seconds`);

    // Output for GitHub Actions (new format)
    if (process.env.GITHUB_OUTPUT) {
      const fs = require("fs");
      fs.appendFileSync(
        process.env.GITHUB_OUTPUT,
        `access_token=${tokenResponse.access_token}\n` +
        `refresh_token=${tokenResponse.refresh_token || refreshTokenValue}\n` +
        `expires_at=${expiresAt}\n`
      );
    } else {
      // Legacy output format
      console.log(
        `::set-output name=access_token::${tokenResponse.access_token}`,
      );
      console.log(
        `::set-output name=refresh_token::${tokenResponse.refresh_token || refreshTokenValue}`,
      );
      console.log(
        `::set-output name=expires_at::${expiresAt}`,
      );
    }

    // Mask the token in logs
    console.log(`::add-mask::${tokenResponse.access_token}`);
    
    // Set environment variables for subsequent steps
    if (process.env.GITHUB_ENV) {
      const fs = require("fs");
      fs.appendFileSync(
        process.env.GITHUB_ENV,
        `CLAUDE_ACCESS_TOKEN=${tokenResponse.access_token}\n` +
        `CLAUDE_REFRESH_TOKEN=${tokenResponse.refresh_token || refreshTokenValue}\n` +
        `CLAUDE_EXPIRES_AT=${expiresAt}\n`
      );
    }
  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  }
}

main();
