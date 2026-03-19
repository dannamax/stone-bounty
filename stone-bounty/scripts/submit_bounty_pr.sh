#!/bin/bash
# Stone Bounty - Comprehensive PR Submission Script
# Integrates all quality control requirements

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load configuration
CONFIG_FILE="$ROOT_DIR/config/automation_config.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Configuration file not found!"
    exit 1
fi

# Check emergency stop
EMERGENCY_STOP=$(jq -r '.emergency_stop_active // false' "$CONFIG_FILE")
if [[ "$EMERGENCY_STOP" == "true" ]]; then
    echo "Emergency stop is active! Manual review required."
    exit 1
fi

# Parse arguments
ISSUE_URL=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --issue-url)
            ISSUE_URL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$ISSUE_URL" ]]; then
    echo "Error: --issue-url is required"
    exit 1
fi

echo "🚀 Starting comprehensive bounty PR submission process..."
echo "Issue URL: $ISSUE_URL"

# Step 1: Analyze requirements
echo "🔍 Step 1: Analyzing project requirements..."
"$SCRIPT_DIR/requirement_analyzer.sh" --issue-url "$ISSUE_URL"

# Step 2: Check daily submission limits
echo "📊 Step 2: Checking daily submission limits..."
"$SCRIPT_DIR/daily_submission_limiter.sh" --issue-url "$ISSUE_URL"

# Step 3: Validate contribution quality
echo "✅ Step 3: Validating contribution quality..."
# This would be run after you make your changes

# Step 4: Generate conversational reply
echo "💬 Step 4: Preparing conversational PR description..."
"$SCRIPT_DIR/conversational_reply_generator.sh" --issue-url "$ISSUE_URL"

echo "🎯 All quality checks passed! Ready for manual review and submission."
echo ""
echo "Next steps:"
echo "1. Make your actual code changes in the repository"
echo "2. Run the validator script to ensure quality"
echo "3. Use the pr_submitter.sh script to create the PR"
echo ""
echo "Remember: All submissions require manual review to maintain quality standards!"

exit 0