#!/bin/bash
# Stone Bounty - PR Notification Handler
# Handles notifications and alerts for PR monitoring events

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$ROOT_DIR/config"
LOG_FILE="$ROOT_DIR/logs/pr_monitor_$(date +%Y%m).log"

# Create logs directory if needed
mkdir -p "$ROOT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send notification
send_notification() {
    local pr_url="$1"
    local event_type="$2"
    local message="$3"
    
    log_message "🔔 PR Notification: $event_type - $pr_url"
    log_message "   Message: $message"
    
    # TODO: Add actual notification methods (email, webhook, etc.)
    # For now, just log to file
    
    # Save to notifications file
    NOTIFICATION_FILE="$CONFIG_DIR/pr_notifications.json"
    if [[ ! -f "$NOTIFICATION_FILE" ]]; then
        echo '{"notifications": []}' > "$NOTIFICATION_FILE"
    fi
    
    # Add new notification
    jq --arg url "$pr_url" \
       --arg type "$event_type" \
       --arg msg "$message" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.notifications += [{"pr_url": $url, "event_type": $type, "message": $msg, "timestamp": $timestamp, "handled": false}]' \
       "$NOTIFICATION_FILE" > "$NOTIFICATION_FILE.tmp" && mv "$NOTIFICATION_FILE.tmp" "$NOTIFICATION_FILE"
}

# Function to check for new comments
check_new_comments() {
    local pr_url="$1"
    local last_check="$2"
    
    # Extract owner/repo/pr_number from URL
    if [[ $pr_url =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)$ ]]; then
        OWNER="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        PR_NUMBER="${BASH_REMATCH[3]}"
    else
        log_message "❌ Invalid PR URL format: $pr_url"
        return 1
    fi
    
    # Get PR comments
    COMMENTS=$(curl -s -H "Authorization: token $(cat "$ROOT_DIR/.github_token")" \
        "https://api.github.com/repos/$OWNER/$REPO/issues/$PR_NUMBER/comments")
    
    NEW_COMMENTS=0
    while IFS= read -r comment; do
        COMMENT_ID=$(echo "$comment" | jq -r '.id')
        COMMENT_USER=$(echo "$comment" | jq -r '.user.login')
        COMMENT_BODY=$(echo "$comment" | jq -r '.body')
        COMMENT_CREATED=$(echo "$comment" | jq -r '.created_at')
        
        # Check if comment is newer than last check
        if [[ "$COMMENT_CREATED" > "$last_check" ]] && [[ "$COMMENT_USER" != "dannamax" ]]; then
            send_notification "$pr_url" "new_comment" "New comment from @$COMMENT_USER: $COMMENT_BODY"
            ((NEW_COMMENTS++))
        fi
    done < <(echo "$COMMENTS" | jq -c '.[]')
    
    if [[ $NEW_COMMENTS -gt 0 ]]; then
        log_message "✅ Found $NEW_COMMENTS new comment(s) on PR $pr_url"
    fi
    
    return $NEW_COMMENTS
}

# Function to check PR status changes
check_status_changes() {
    local pr_url="$1"
    local current_status="$2"
    
    if [[ $pr_url =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)$ ]]; then
        OWNER="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        PR_NUMBER="${BASH_REMATCH[3]}"
    else
        return 1
    fi
    
    # Get current PR status
    PR_DETAILS=$(curl -s -H "Authorization: token $(cat "$ROOT_DIR/.github_token")" \
        "https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER")
    
    NEW_STATUS=$(echo "$PR_DETAILS" | jq -r '.state')
    MERGED=$(echo "$PR_DETAILS" | jq -r '.merged')
    
    if [[ "$NEW_STATUS" != "$current_status" ]]; then
        if [[ "$NEW_STATUS" == "closed" ]]; then
            if [[ "$MERGED" == "true" ]]; then
                send_notification "$pr_url" "merged" "Your PR has been merged! 🎉"
            else
                send_notification "$pr_url" "closed" "Your PR has been closed without merging."
            fi
        fi
    fi
}

# Main function
main() {
    log_message "🚀 Starting PR notification handler..."
    
    # Load submitted PRs
    SUBMITTED_PRS_FILE="$CONFIG_DIR/submitted_prs.json"
    if [[ ! -f "$SUBMITTED_PRS_FILE" ]]; then
        log_message "⚠️ No submitted PRs found"
        return 0
    fi
    
    # Process each submitted PR
    jq -r '.prs[] | select(.status == "submitted") | .pr_url' "$SUBMITTED_PRS_FILE" | while read -r pr_url; do
        if [[ -z "$pr_url" || "$pr_url" == "null" ]]; then
            continue
        fi
        
        log_message "🔍 Checking PR: $pr_url"
        
        # Get last check time
        LAST_CHECK=$(jq -r --arg url "$pr_url" '.prs[] | select(.pr_url == $url) | .last_monitored // "1970-01-01T00:00:00Z"' "$SUBMITTED_PRS_FILE")
        
        # Check for new comments
        check_new_comments "$pr_url" "$LAST_CHECK"
        
        # Check for status changes
        CURRENT_STATUS=$(jq -r --arg url "$pr_url" '.prs[] | select(.pr_url == $url) | .github_status // "open"' "$SUBMITTED_PRS_FILE")
        check_status_changes "$pr_url" "$CURRENT_STATUS"
        
        # Update last monitored time
        jq --arg url "$pr_url" \
           --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '(.prs[] | select(.pr_url == $url) | .last_monitored) = $timestamp' \
           "$SUBMITTED_PRS_FILE" > "$SUBMITTED_PRS_FILE.tmp" && mv "$SUBMITTED_PRS_FILE.tmp" "$SUBMITTED_PRS_FILE"
    done
    
    log_message "✅ PR notification check completed"
}

# Run main function
main "$@"