#!/bin/bash
# Stone Bounty - Setup Script
# Installs dependencies and configures the environment

set -e

echo "🧱 Setting up Stone Bounty System..."

# Check if required tools are installed
echo "🔍 Checking dependencies..."
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ jq not found. Installing..."
    if command -v apt &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    else
        echo "Please install jq manually"
        exit 1
    fi
fi

# Create config directory if it doesn't exist
mkdir -p config

# Check for GitHub token
if [ ! -f .github_token ]; then
    echo "⚠️  No GitHub token found. Please create .github_token file with your token"
    echo "   Get token from: https://github.com/settings/tokens"
    echo "   Required scopes: repo, read:org"
    exit 1
fi

# Check for wallet address
if [ ! -f .wallet_address ]; then
    echo "⚠️  No wallet address found. Please create .wallet_address file"
    echo "   This is used for bounty claims"
    exit 1
fi

# Initialize default config if not exists
if [ ! -f config/automation_config.json ]; then
    echo "⚙️  Creating default automation config..."
    cat > config/automation_config.json << EOF
{
  "github_username": "",
  "emergency_stop_active": true,
  "auto_pr_submission_enabled": false,
  "manual_only_mode": true,
  "monitor_only_mode": true,
  "max_daily_submissions": 0,
  "wallet_address": "",
  "spam_prevention_enabled": true,
  "rate_limiting_strict": true
}
EOF
fi

# Initialize blacklist if not exists
if [ ! -f config/blacklisted_projects.json ]; then
    echo "🛡️  Creating blacklist config..."
    cat > config/blacklisted_projects.json << EOF
{
  "blacklisted_repositories": [
    "rust-lang/rust",
    "vuejs/vue",
    "microsoft/vscode",
    "angular/angular",
    "golang/go",
    "nodejs/node",
    "pytorch/pytorch"
  ],
  "reasons": {
    "rust-lang/rust": "High complexity, CLA required, low success rate",
    "vuejs/vue": "Large codebase, strict review process",
    "nodejs/node": "Complex build system, CLA required"
  }
}
EOF
fi

# Initialize strategy config if not exists
if [ ! -f config/strategy_config.json ]; then
    echo "🎯 Creating strategy config..."
    cat > config/strategy_config.json << EOF
{
  "focus_areas": ["documentation", "tests", "minor_fixes"],
  "min_bounty_amount": "5",
  "preferred_languages": ["javascript", "python", "typescript", "markdown"],
  "avoid_cla_projects": true,
  "success_rate_target": 25,
  "current_success_rate": 12.5
}
EOF
fi

# Set permissions
chmod +x scripts/*.sh

# Initialize bounty tracker if not exists
if [ ! -f config/bounty_tracker.json ]; then
    echo "📊 Initializing bounty tracker..."
    cat > config/bounty_tracker.json << EOF
{
  "last_check": "",
  "tracked_projects": {},
  "total_opportunities_found": 0,
  "successful_submissions": 0
}
EOF
fi

# Initialize project list if not exists  
if [ ! -f config/project_list.json ]; then
    echo "📋 Creating project list..."
    cp config/project_list_template.json config/project_list.json
fi

echo "✅ Stone Bounty setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit config/automation_config.json with your GitHub username"
echo "2. Ensure your .github_token and .wallet_address files are correct"
echo "3. Review blacklisted_projects.json and add any projects to avoid"
echo "4. Run ./scripts/bounty_monitor.sh --manual-only to start monitoring"
echo "5. Hourly auto-monitoring is enabled (check config/project_list.json)"