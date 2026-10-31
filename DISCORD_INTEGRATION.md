# Discord Integration for GitHub Activity

This document explains how to set up Discord integration for your GitHub repository to sync activity like commits, issues, discussions, and pull requests.

## Features

- Real-time notifications for GitHub events (commits, issues, discussions, pull requests)
- Dedicated Discord channels for different types of GitHub activity
- Interactive Discord bot with slash commands
- Feedback system connecting Discord and GitHub

## Setup Instructions

### 1. Setting Up Discord Webhooks

1. Go to your Discord server
2. Select the channel where you want GitHub notifications
3. Go to channel settings → Integrations → Webhooks
4. Click "Create Webhook"
5. Customize the name and avatar (suggested: "GitHub Bot")
6. Copy the webhook URL
7. Repeat for each channel you want to dedicate to different GitHub activities (commits, issues, discussions, PRs)

### 2. Configuring the Webhook URLs

Update the `discord_config.json` file with your actual webhook URLs:

```json
{
  "webhooks": {
    "commits": {
      "url": "https://discord.com/api/webhooks/YOUR_ACTUAL_COMMIT_WEBHOOK_URL",
      "channel_name": "github-commits",
      "events": ["push"]
    },
    "issues": {
      "url": "https://discord.com/api/webhooks/YOUR_ACTUAL_ISSUE_WEBHOOK_URL",
      "channel_name": "github-issues",
      "events": ["issues", "issue_comment"]
    },
    "discussions": {
      "url": "https://discord.com/api/webhooks/YOUR_ACTUAL_DISCUSSION_WEBHOOK_URL",
      "channel_name": "github-discussions",
      "events": ["discussion", "discussion_comment"]
    },
    "pull_requests": {
      "url": "https://discord.com/api/webhooks/YOUR_ACTUAL_PR_WEBHOOK_URL",
      "channel_name": "github-pull-requests",
      "events": ["pull_request", "pull_request_review", "pull_request_review_comment"]
    }
  }
}
```

### 3. Creating a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give your application a name (e.g., "GitHub Activity Bot")
4. Go to the "Bot" tab
5. Click "Add Bot"
6. Under "Token", click "Copy" to copy the bot token
7. Update the `discord_config.json` file with your bot token:

```json
{
  "bot_token": "YOUR_ACTUAL_BOT_TOKEN_HERE"
}
```

### 4. Inviting the Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" → "URL Generator" tab
2. Under "Scopes", select `bot` and `applications.commands`
3. Under "Bot Permissions", select:
   - View Channel
   - Send Messages
   - Embed Links
   - Read Message History
   - Mention Everyone
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 5. Setting Up GitHub Webhooks

1. Go to your GitHub repository
2. Click on "Settings" → "Webhooks"
3. Click "Add webhook"
4. Set the Payload URL to your server endpoint (e.g., `https://yourdomain.com/github-webhook`)
5. Set Content type to `application/json`
6. Optionally add a secret for security
7. Select the events you want to trigger the webhook:
   - Pushes
   - Issues
   - Pull Requests
   - Discussions
8. Click "Add webhook"

### 6. Running the Integration

#### Installing Dependencies

```bash
pip install -r requirements.txt
```

#### Running the Webhook Server

```bash
python webhook_server.py
```

#### Running the Discord Bot

```bash
python discord_bot.py
```

## Available Discord Commands

Once the bot is running, you can use these slash commands:

- `/github_info` - Get information about the GitHub integration
- `/github_activity` - Get latest GitHub activity
- `/feedback <message>` - Submit feedback about the GitHub project

## Security Considerations

- Store your Discord bot token and GitHub webhook secrets securely
- Use environment variables for sensitive information
- Validate incoming webhook requests using the GitHub secret
- Regularly rotate your tokens and secrets

## Troubleshooting

- If webhooks aren't triggering, check that your server is accessible from the internet
- Verify that your Discord bot has the necessary permissions in the channels
- Check that the GitHub webhook URL is correctly formatted
- Look at server logs for error messages