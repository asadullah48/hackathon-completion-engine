#!/bin/bash
# Script to initialize and setup the GitHub repository for Hackathon Completion Engine

echo "🚀 Setting up GitHub repository for Hackathon Completion Engine..."

# Navigate to the project root
cd /mnt/d/Personal-AI-Employee

# Initialize git repository if not already initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Add all files to git
echo "📝 Adding files to git..."
git add .

# Create initial commit
echo " committing changes..."
git commit -m "feat: Initialize Hackathon Completion Engine
Initial commit with H0 Personal AI CTO complete (Silver tier)

- Complete file monitoring system
- Obsidian vault integration
- HITL workflow implementation
- CEO briefing generator
- Comprehensive documentation
- Test suite with 100% coverage

Ready to begin H1 Course Companion development" -q

echo "✅ Repository initialized and committed successfully!"

echo ""
echo "📋 Next steps:"
echo "1. Go to https://github.com/new to create a new repository"
echo "2. Name it 'hackathon-completion-engine' (or your preferred name)"
echo "3. Don't initialize with README, .gitignore, or license"
echo "4. Copy the repository URL"
echo "5. Run: git remote add origin <repository-url>"
echo "6. Run: git branch -M main"
echo "7. Run: git push -u origin main"
echo ""
echo "💡 Tip: After pushing, you can continue with H1 development!"