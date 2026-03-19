#!/bin/bash
# Stone Bounty - Simple PR Monitor
# Monitors submitted PRs for comments and updates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"
LOG_FILE="$SCRIPT_DIR/../logs/pr_monitor_$(date +%Y%m).log"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/../logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if GitHub token exists
if [ ! -f "$SCRIPT_DIR/../.github_token" ]; then
    log_message "❌ ERROR: GitHub token file not found"
    exit 1
fi

GITHUB_TOKEN=$(cat "$SCRIPT_DIR/../.github_token")

# Load submitted PRs
if [ ! -f "$CONFIG_DIR/submitted_prs.json" ]; then
    log_message "ℹ️ No submitted PRs found"
    exit 0
fi

# Get PR data from submitted_prs.json
PR_URL=$(jq -r '.prs[0].pr_url // empty' "$CONFIG_DIR/submitted_prs.json")
if [ -z "$PR_URL" ]; then
    log_message "ℹ️ No PR URLs found in submitted_prs.json"
    exit 0
fi

# Extract owner, repo, and PR number
if [[ $PR_URL =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)$ ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
    PR_NUMBER="${BASH_REMATCH[3]}"
else
    log_message "❌ Invalid PR URL format: $PR_URL"
    exit 1
fi

log_message "🔍 Monitoring PR: $OWNER/$REPO #$PR_NUMBER"

# Get PR details
PR_DATA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER")

if [ "$(echo "$PR_DATA" | jq -r '.message // empty')" = "Not Found" ]; then
    log_message "❌ PR not found or access denied"
    exit 1
fi

# Get PR status
STATE=$(echo "$PR_DATA" | jq -r '.state')
MERGED=$(echo "$PR_DATA" | jq -r '.merged // false')

# Get comments count
COMMENTS_URL=$(echo "$PR_DATA" | jq -r '.comments_url')
COMMENTS_COUNT=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "$COMMENTS_URL" | jq 'length')

# Get last comment if any
LAST_COMMENT=""
if [ "$COMMENTS_COUNT" -gt 0 ]; then
    LAST_COMMENT_DATA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$COMMENTS_URL" | jq -r '.[-1]')
    LAST_COMMENT_AUTHOR=$(echo "$LAST_COMMENT_DATA" | jq -r '.user.login')
    LAST_COMMENT_BODY=$(echo "$LAST_COMMENT_DATA" | jq -r '.body')
    LAST_COMMENT_CREATED=$(echo "$LAST_COMMENT_DATA" | jq -r '.created_at')
    LAST_COMMENT="Author: $LAST_COMMENT_AUTHOR\nBody: $LAST_COMMENT_BODY\nCreated: $LAST_COMMENT_CREATED"
fi

# Update submitted_prs.json with latest info
jq --arg state "$STATE" \
   --arg merged "$MERGED" \
   --arg comments "$COMMENTS_COUNT" \
   --arg last_comment "$LAST_COMMENT" \
   --arg checked_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
   '.prs[0] |= (.status = $state | .merged = ($merged == "true") | .comments_count = ($comments | tonumber) | .last_check = $checked_at | .last_comment = $last_comment)' \
   "$CONFIG_DIR/submitted_prs.json" > "$CONFIG_DIR/submitted_prs.json.tmp"

mv "$CONFIG_DIR/submitted_prs.json.tmp" "$CONFIG_DIR/submitted_prs.json"

# Log results
log_message "✅ PR Status: $STATE"
log_message "✅ Merged: $MERGED"
log_message "✅ Comments: $COMMENTS_COUNT"

if [ "$COMMENTS_COUNT" -gt 0 ]; then
    log_message "🔔 New comment detected! Check submitted_prs.json for details."
    # Here you could add notification logic
fi

log_message "✅ PR monitoring completed successfully"