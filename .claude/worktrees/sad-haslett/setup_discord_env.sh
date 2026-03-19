#!/bin/bash
# Setup script for Discord Integration Environment Variables

echo "Setting up environment variables for Discord Integration..."

# Create .env file if it doesn't exist
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
    echo "# Discord Integration Environment Variables" >> "$ENV_FILE"
    echo "" >> "$ENV_FILE"
fi

# Prompt for GitHub webhook secret
read -p "Enter your GitHub webhook secret (or press Enter to skip): " GH_SECRET
if [ ! -z "$GH_SECRET" ]; then
    # Check if the variable already exists in the file
    if grep -q "GITHUB_WEBHOOK_SECRET=" "$ENV_FILE"; then
        # Update existing entry
        sed -i "s|GITHUB_WEBHOOK_SECRET=.*|GITHUB_WEBHOOK_SECRET=$GH_SECRET|" "$ENV_FILE"
    else
        # Add new entry
        echo "GITHUB_WEBHOOK_SECRET=$GH_SECRET" >> "$ENV_FILE"
    fi
    echo "✓ GitHub webhook secret added to $ENV_FILE"
else
    echo "ℹ️  Skipping GitHub webhook secret setup"
fi

echo ""
echo "Environment setup complete!"
echo "To activate these variables in your current session, run: source $ENV_FILE"