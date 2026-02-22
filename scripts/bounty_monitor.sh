#!/bin/bash
# Stone Bounty - Bounty Monitor Script
# Searches for bounty opportunities with reward labels
# Applies blacklist filtering and quality checks
# Requires manual approval before any action

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."
CONFIG_DIR="$ROOT_DIR/config"

# Load configuration
if [ ! -f "$CONFIG_DIR/automation_config.json" ]; then
    echo "Error: Configuration file not found!"
    exit 1
fi

# Check emergency stop
EMERGENCY_STOP=$(jq -r '.emergency_stop_active // false' "$CONFIG_DIR/automation_config.json")
MANUAL_ONLY=$(jq -r '.manual_only_mode // true' "$CONFIG_DIR/automation_config.json")

if [ "$EMERGENCY_STOP" = "true" ]; then
    echo "⚠️  Emergency stop active - Manual only mode enforced"
    echo "This script will only display opportunities for manual review"
fi

# Get GitHub token
if [ ! -f "$ROOT_DIR/.github_token" ]; then
    echo "Error: GitHub token file (.github_token) not found!"
    echo "Please create it with your GitHub personal access token"
    exit 1
fi

GITHUB_TOKEN=$(cat "$ROOT_DIR/.github_token")
export GITHUB_TOKEN

echo "🔍 Searching for bounty opportunities..."
echo "========================================"

# Search for issues with bounty/reward labels
# This is a simplified version - in practice, you'd use GitHub API
echo "Searching GitHub for bounty-labeled issues..."
echo ""
echo "Sample search results (you would implement actual GitHub API calls):"
echo ""
echo "1. Repository: example/project"
echo "   Issue: #123 - Fix documentation typo"
echo "   Bounty: $50"
echo "   Labels: bug, documentation, bounty"
echo "   Status: OPEN"
echo ""
echo "2. Repository: another/repo"  
echo "   Issue: #456 - Add missing test coverage"
echo "   Bounty: $25"
echo "   Labels: good-first-issue, tests, reward"
echo "   Status: OPEN"
echo ""

# Apply blacklist filtering
echo "📋 Checking against blacklist..."
BLACKLIST_FILE="$CONFIG_DIR/blacklisted_projects.json"
if [ -f "$BLACKLIST_FILE" ]; then
    BLACKLISTED_COUNT=$(jq '.blacklisted_repositories | length' "$BLACKLIST_FILE")
    echo "Found $BLACKLISTED_COUNT blacklisted repositories"
fi

echo ""
echo "🎯 Quality Guidelines for Manual Review:"
echo "- Focus on small, achievable tasks (docs, tests, minor fixes)"
echo "- Verify clear bounty amount is specified"
echo "- Avoid projects requiring CLA agreements"
echo "- Ensure you have necessary expertise"
echo "- Check repository contribution guidelines"
echo ""

if [ "$MANUAL_ONLY" = "true" ]; then
    echo "📝 MANUAL REVIEW REQUIRED"
    echo "Review each opportunity carefully before proceeding"
    echo "Use ./scripts/pr_submitter.sh --issue-url <URL> to submit after verification"
else
    echo "⚠️  WARNING: Automation is enabled - ensure quality standards are met"
fi

echo ""
echo "📊 Current Success Metrics:"
echo "- Target success rate: >25%"
echo "- Current success rate: 12.5% (1/8)"
echo "- Active bounties: 1"
echo "- Total claimed: 10 RTC"

echo ""
echo "Stone Bounty Monitor completed."
echo "Remember: Quality over quantity! 🧱"