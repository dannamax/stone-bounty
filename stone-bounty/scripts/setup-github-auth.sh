#!/bin/bash

# Stone Bounty - GitHub Authentication Setup Script
# This script helps you securely configure your GitHub credentials

set -e

echo "🧱 Stone Bounty - GitHub Authentication Setup"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "SKILL.md" ]; then
    echo "❌ Error: Please run this script from the stone-bounty directory"
    exit 1
fi

# Get GitHub username
echo "Your GitHub username is: dannamax"
GITHUB_USERNAME="dannamax"

# Prompt for GitHub token (hidden input)
echo ""
echo "🔐 Please enter your GitHub Personal Access Token:"
echo "   (The token will be hidden as you type)"
read -s GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: Token cannot be empty"
    exit 1
fi

# Create .git-credentials file
echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > .git-credentials

# Set secure permissions
chmod 600 .git-credentials

echo ""
echo "✅ GitHub authentication configured successfully!"
echo "   - Username: ${GITHUB_USERNAME}"
echo "   - Credentials stored in: .git-credentials"
echo "   - File permissions set to 600 (read/write only by owner)"

echo ""
echo "💡 Next steps:"
echo "   1. Make sure your token has the necessary permissions:"
echo "      - Repository contents: Read and write"
echo "      - Pull requests: Read and write" 
echo "      - Issues: Read and write"
echo "   2. Test your setup with: git ls-remote https://github.com/dannamax/any-repo.git"
echo "   3. Remember to add .git-credentials to your .gitignore if not already there"

echo ""
echo "🛡️  Security reminder: Never commit .git-credentials to version control!"