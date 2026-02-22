#!/bin/bash
# Stone Bounty - PR Monitor Script
# Monitors submitted PRs for maintainer feedback and updates

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$ROOT_DIR/config"
LOG_FILE="$ROOT_DIR/logs/pr_monitor_$(date +%Y%m).log"

# Create logs directory if it doesn't exist
mkdir -p "$ROOT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if GitHub token exists
check_github_token() {
    if [ ! -f "$ROOT_DIR/.github_token" ]; then
        log_message "❌ ERROR: GitHub token file not found at $ROOT_DIR/.github_token"
        exit 1
    fi
}

# Function to load submitted PRs
load_submitted_prs() {
    SUBMITTED_PRS_FILE="$CONFIG_DIR/submitted_prs.json"
    if [ ! -f "$SUBMITTED_PRS_FILE" ]; then
        log_message "ℹ️  No submitted PRs file found, creating empty one"
        echo '{"prs": []}' > "$SUBMITTED_PRS_FILE"
    fi
}

# Function to get PR details from GitHub
get_pr_details() {
    local owner="$1"
    local repo="$2" 
    local pr_number="$3"
    
    GITHUB_TOKEN=$(cat "$ROOT_DIR/.github_token")
    
    # Get PR details
    PR_DETAILS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$owner/$repo/pulls/$pr_number")
    
    # Get PR comments
    PR_COMMENTS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$owner/$repo/issues/$pr_number/comments")
    
    # Get PR reviews
    PR_REVIEWS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$owner/$repo/pulls/$pr_number/reviews")
    
    echo "$PR_DETAILS" > "/tmp/pr_details_$pr_number.json"
    echo "$PR_COMMENTS" > "/tmp/pr_comments_$pr_number.json"  
    echo "$PR_REVIEWS" > "/tmp/pr_reviews_$pr_number.json"
}

# Function to check for new activity
check_new_activity() {
    local pr_url="$1"
    local last_checked="$2"
    
    # Extract owner, repo, pr_number from URL
    if [[ $pr_url =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)$ ]]; then
        OWNER="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        PR_NUMBER="${BASH_REMATCH[3]}"
    else
        log_message "❌ Invalid PR URL format: $pr_url"
        return 1
    fi
    
    log_message "🔍 Checking PR: $OWNER/$REPO #$PR_NUMBER"
    
    # Get current PR data
    get_pr_details "$OWNER" "$REPO" "$PR_NUMBER"
    
    # Load current PR data
    PR_DETAILS_FILE="/tmp/pr_details_$PR_NUMBER.json"
    PR_COMMENTS_FILE="/tmp/pr_comments_$PR_NUMBER.json"
    PR_REVIEWS_FILE="/tmp/pr_reviews_$PR_NUMBER.json"
    
    if [ ! -f "$PR_DETAILS_FILE" ]; then
        log_message "❌ Failed to fetch PR details for $pr_url"
        return 1
    fi
    
    # Check PR status
    PR_STATE=$(jq -r '.state' "$PR_DETAILS_FILE")
    PR_MERGED=$(jq -r '.merged_at // "null"' "$PR_DETAILS_FILE")
    PR_CLOSED=$(jq -r '.closed_at // "null"' "$PR_DETAILS_FILE")
    
    # Check for new comments
    COMMENT_COUNT=$(jq 'length' "$PR_COMMENTS_FILE")
    NEW_COMMENTS=0
    
    if [ "$COMMENT_COUNT" -gt 0 ]; then
        # Find comments after last checked timestamp
        while IFS= read -r comment; do
            COMMENT_CREATED=$(echo "$comment" | jq -r '.created_at')
            COMMENT_AUTHOR=$(echo "$comment" | jq -r '.user.login')
            COMMENT_BODY=$(echo "$comment" | jq -r '.body')
            
            # Skip if comment is from yourself
            if [ "$COMMENT_AUTHOR" = "$(jq -r '.github_username' "$CONFIG_DIR/automation_config.json")" ]; then
                continue
            fi
            
            # Check if comment is newer than last checked
            if [ "$COMMENT_CREATED" \> "$last_checked" ]; then
                log_message "💬 New comment from @$COMMENT_AUTHOR on PR #$PR_NUMBER"
                log_message "   Comment: $(echo "$COMMENT_BODY" | head -c 100)..."
                ((NEW_COMMENTS++))
            fi
        done < <(jq -c '.[]' "$PR_COMMENTS_FILE")
    fi
    
    # Check for new reviews
    REVIEW_COUNT=$(jq 'length' "$PR_REVIEWS_FILE")
    NEW_REVIEWS=0
    
    if [ "$REVIEW_COUNT" -gt 0 ]; then
        while IFS= read -r review; do
            REVIEW_CREATED=$(echo "$review" | jq -r '.submitted_at')
            REVIEW_AUTHOR=$(echo "$review" | jq -r '.user.login')
            REVIEW_STATE=$(echo "$review" | jq -r '.state')
            REVIEW_BODY=$(echo "$review" | jq -r '.body // ""')
            
            # Skip if review is from yourself
            if [ "$REVIEW_AUTHOR" = "$(jq -r '.github_username' "$CONFIG_DIR/automation_config.json")" ]; then
                continue
            fi
            
            # Check if review is newer than last checked
            if [ "$REVIEW_CREATED" \> "$last_checked" ]; then
                log_message "📋 New review from @$REVIEW_AUTHOR on PR #$PR_NUMBER: $REVIEW_STATE"
                if [ -n "$REVIEW_BODY" ]; then
                    log_message "   Review: $(echo "$REVIEW_BODY" | head -c 100)..."
                fi
                ((NEW_REVIEWS++))
            fi
        done < <(jq -c '.[]' "$PR_REVIEWS_FILE")
    fi
    
    # Update PR status in tracking file
    update_pr_status "$pr_url" "$PR_STATE" "$PR_MERGED" "$PR_CLOSED" "$NEW_COMMENTS" "$NEW_REVIEWS"
    
    # Return total new activity
    echo $((NEW_COMMENTS + NEW_REVIEWS))
}

# Function to update PR status in tracking file
update_pr_status() {
    local pr_url="$1"
    local state="$2"
    local merged="$3"
    local closed="$4"
    local new_comments="$5"
    local new_reviews="$6"
    
    SUBMITTED_PRS_FILE="$CONFIG_DIR/submitted_prs.json"
    TEMP_FILE="/tmp/submitted_prs_updated.json"
    
    # Update the PR entry
    jq --arg url "$pr_url" \
       --arg state "$state" \
       --arg merged "$merged" \
       --arg closed "$closed" \
       --argjson new_comments "$new_comments" \
       --argjson new_reviews "$new_reviews" \
       --arg current_time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '(.prs[] | select(.pr_url == $url)) |= 
       (.status = $state |
        .merged_at = ($merged != "null" ? $merged : .merged_at) |
        .closed_at = ($closed != "null" ? $closed : .closed_at) |
        .last_checked = $current_time |
        .new_comments += $new_comments |
        .new_reviews += $new_reviews |
        .requires_attention = ($new_comments > 0 or $new_reviews > 0))' \
       "$SUBMITTED_PRS_FILE" > "$TEMP_FILE"
    
    mv "$TEMP_FILE" "$SUBMITTED_PRS_FILE"
}

# Function to add new PR to monitoring
add_pr_to_monitoring() {
    local pr_url="$1"
    local issue_url="$2"
    
    SUBMITTED_PRS_FILE="$CONFIG_DIR/submitted_prs.json"
    TEMP_FILE="/tmp/submitted_prs_new.json"
    
    # Add new PR entry
    jq --arg pr_url "$pr_url" \
       --arg issue_url "$issue_url" \
       --arg current_time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '.prs += [{
         "pr_url": $pr_url,
         "issue_url": $issue_url,
         "status": "open",
         "last_checked": $current_time,
         "new_comments": 0,
         "new_reviews": 0,
         "requires_attention": false,
         "merged_at": null,
         "closed_at": null
       }]' "$SUBMITTED_PRS_FILE" > "$TEMP_FILE"
    
    mv "$TEMP_FILE" "$SUBMITTED_PRS_FILE"
    log_message "✅ Added PR to monitoring: $pr_url"
}

# Main monitoring function
monitor_all_prs() {
    log_message "🚀 Starting PR monitoring cycle..."
    
    SUBMITTED_PRS_FILE="$CONFIG_DIR/submitted_prs.json"
    TOTAL_ACTIVITY=0
    
    # Load all submitted PRs
    PR_COUNT=$(jq '.prs | length' "$SUBMITTED_PRS_FILE")
    
    if [ "$PR_COUNT" -eq 0 ]; then
        log_message "ℹ️  No submitted PRs to monitor"
        return 0
    fi
    
    log_message "📊 Monitoring $PR_COUNT submitted PRs..."
    
    # Check each PR for new activity
    for ((i=0; i<PR_COUNT; i++)); do
        PR_URL=$(jq -r ".prs[$i].pr_url" "$SUBMITTED_PRS_FILE")
        LAST_CHECKED=$(jq -r ".prs[$i].last_checked" "$SUBMITTED_PRS_FILE")
        STATUS=$(jq -r ".prs[$i].status" "$SUBMITTED_PRS_FILE")
        
        # Skip closed/merged PRs (optional - you might want to monitor them too)
        if [ "$STATUS" = "closed" ] || [ "$STATUS" = "merged" ]; then
            log_message "⏭️  Skipping $PR_URL (status: $STATUS)"
            continue
        fi
        
        # Check for new activity
        NEW_ACTIVITY=$(check_new_activity "$PR_URL" "$LAST_CHECKED")
        TOTAL_ACTIVITY=$((TOTAL_ACTIVITY + NEW_ACTIVITY))
    done
    
    # Summary
    log_message "✅ PR monitoring cycle completed"
    log_message "📊 Total new activity found: $TOTAL_ACTIVITY"
    
    if [ "$TOTAL_ACTIVITY" -gt 0 ]; then
        log_message "🔔 Attention required! New maintainer feedback detected."
        # Optional: Send notification or create alert file
        echo "$(date): $TOTAL_ACTIVITY new activities requiring attention" >> "$ROOT_DIR/alerts/pr_attention_needed.txt"
    fi
}

# Function to display PR status summary
show_pr_summary() {
    SUBMITTED_PRS_FILE="$CONFIG_DIR/submitted_prs.json"
    echo -e "${BLUE}=== Submitted PRs Status Summary ===${NC}"
    
    PR_COUNT=$(jq '.prs | length' "$SUBMITTED_PRS_FILE")
    if [ "$PR_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}No submitted PRs tracked${NC}"
        return 0
    fi
    
    ATTENTION_NEEDED=0
    
    for ((i=0; i<PR_COUNT; i++)); do
        PR_URL=$(jq -r ".prs[$i].pr_url" "$SUBMITTED_PRS_FILE")
        STATUS=$(jq -r ".prs[$i].status" "$SUBMITTED_PRS_FILE")
        NEW_COMMENTS=$(jq -r ".prs[$i].new_comments" "$SUBMITTED_PRS_FILE")
        NEW_REVIEWS=$(jq -r ".prs[$i].new_reviews" "$SUBMITTED_PRS_FILE")
        REQUIRES_ATTENTION=$(jq -r ".prs[$i].requires_attention" "$SUBMITTED_PRS_FILE")
        
        if [ "$REQUIRES_ATTENTION" = "true" ]; then
            echo -e "${RED}⚠️  $PR_URL${NC}"
            echo -e "   Status: $STATUS | New Comments: $NEW_COMMENTS | New Reviews: $NEW_REVIEWS"
            ((ATTENTION_NEEDED++))
        else
            echo -e "${GREEN}✅ $PR_URL${NC}"
            echo -e "   Status: $STATUS"
        fi
    done
    
    if [ "$ATTENTION_NEEDED" -gt 0 ]; then
        echo -e "\n${RED}❗ $ATTENTION_NEEDED PR(s) require your attention!${NC}"
    fi
}

# Parse arguments
ACTION="monitor"
PR_URL=""
ISSUE_URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --add-pr)
            ACTION="add"
            PR_URL="$2"
            ISSUE_URL="$3"
            shift 3
            ;;
        --summary|-s)
            ACTION="summary"
            shift
            ;;
        --help|-h)
            cat << EOF
Stone Bounty PR Monitor

Usage:
  $0                           # Monitor all submitted PRs
  $0 --add-pr <PR_URL> <ISSUE_URL>  # Add new PR to monitoring
  $0 --summary                 # Show PR status summary
  $0 --help                   # Show this help

Examples:
  $0
  $0 --add-pr "https://github.com/repo/pull/123" "https://github.com/repo/issues/456"
  $0 --summary
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main execution
check_github_token
load_submitted_prs

case $ACTION in
    "monitor")
        monitor_all_prs
        ;;
    "add")
        if [ -z "$PR_URL" ] || [ -z "$ISSUE_URL" ]; then
            echo "Error: --add-pr requires both PR_URL and ISSUE_URL"
            exit 1
        fi
        add_pr_to_monitoring "$PR_URL" "$ISSUE_URL"
        ;;
    "summary")
        show_pr_summary
        ;;
    *)
        echo "Unknown action: $ACTION"
        exit 1
        ;;
esac