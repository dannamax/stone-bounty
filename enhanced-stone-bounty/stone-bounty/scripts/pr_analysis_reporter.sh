#!/bin/bash
# Stone Bounty - PR Analysis Reporter
# Generates analysis reports for submitted PRs and maintainer feedback

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$ROOT_DIR/config"
LOG_DIR="$ROOT_DIR/logs"
SUBMITTED_PRS="$CONFIG_DIR/submitted_prs.json"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/pr_monitor.log"
}

# Function to generate PR analysis report
generate_pr_analysis() {
    local pr_url="$1"
    local pr_number="$2"
    local repo_name="$3"
    
    log_message "📊 Generating analysis report for PR #$pr_number in $repo_name"
    
    # Get PR details
    PR_DETAILS=$(gh api "repos/$repo_name/pulls/$pr_number" 2>/dev/null || {
        echo -e "${RED}Error: Failed to fetch PR details${NC}"
        return 1
    })
    
    TITLE=$(echo "$PR_DETAILS" | jq -r '.title')
    STATE=$(echo "$PR_DETAILS" | jq -r '.state')
    CREATED_AT=$(echo "$PR_DETAILS" | jq -r '.created_at')
    UPDATED_AT=$(echo "$PR_DETAILS" | jq -r '.updated_at')
    AUTHOR=$(echo "$PR_DETAILS" | jq -r '.user.login')
    
    # Get PR comments
    COMMENTS=$(gh api "repos/$repo_name/issues/$pr_number/comments" 2>/dev/null || {
        echo -e "${YELLOW}Warning: Could not fetch comments${NC}"
        echo "[]"
    })
    
    COMMENT_COUNT=$(echo "$COMMENTS" | jq 'length')
    
    # Get PR reviews
    REVIEWS=$(gh api "repos/$repo_name/pulls/$pr_number/reviews" 2>/dev/null || {
        echo -e "${YELLOW}Warning: Could not fetch reviews${NC}"
        echo "[]"
    })
    
    REVIEW_COUNT=$(echo "$REVIEWS" | jq 'length')
    
    # Generate report
    REPORT_FILE="$LOG_DIR/pr_analysis_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# PR Analysis Report

## PR Details
- **URL**: $pr_url
- **Title**: $TITLE
- **Repository**: $repo_name
- **Status**: $STATE
- **Created**: $CREATED_AT
- **Last Updated**: $UPDATED_AT
- **Author**: $AUTHOR

## Activity Summary
- **Comments**: $COMMENT_COUNT
- **Reviews**: $REVIEW_COUNT

## Comments
EOF
    
    if [ "$COMMENT_COUNT" -gt 0 ]; then
        echo "### Recent Comments" >> "$REPORT_FILE"
        for ((i=0; i<$COMMENT_COUNT; i++)); do
            COMMENT_USER=$(echo "$COMMENTS" | jq -r ".[$i].user.login")
            COMMENT_BODY=$(echo "$COMMENTS" | jq -r ".[$i].body")
            COMMENT_DATE=$(echo "$COMMENTS" | jq -r ".[$i].created_at")
            
            cat >> "$REPORT_FILE" << EOF
#### Comment by @$COMMENT_USER ($COMMENT_DATE)
\`\`\`
$COMMENT_BODY
\`\`\`

---
EOF
        done
    fi
    
    if [ "$REVIEW_COUNT" -gt 0 ]; then
        echo "### Reviews" >> "$REPORT_FILE"
        for ((i=0; i<$REVIEW_COUNT; i++)); do
            REVIEW_USER=$(echo "$REVIEWS" | jq -r ".[$i].user.login")
            REVIEW_STATE=$(echo "$REVIEWS" | jq -r ".[$i].state")
            REVIEW_BODY=$(echo "$REVIEWS" | jq -r ".[$i].body // \"No comment\"")
            REVIEW_DATE=$(echo "$REVIEWS" | jq -r ".[$i].submitted_at")
            
            cat >> "$REPORT_FILE" << EOF
#### Review by @$REVIEW_USER - $REVIEW_STATE ($REVIEW_DATE)
\`\`\`
$REVIEW_BODY
\`\`\`

---
EOF
        done
    fi
    
    # Add actionable insights
    echo "## Actionable Insights" >> "$REPORT_FILE"
    
    if [ "$STATE" = "closed" ]; then
        MERGED=$(echo "$PR_DETAILS" | jq -r '.merged')
        if [ "$MERGED" = "true" ]; then
            echo "- ✅ **PR has been merged!** Ready for bounty claim." >> "$REPORT_FILE"
        else
            echo "- ❌ **PR was closed without merging.** Review feedback for future improvements." >> "$REPORT_FILE"
        fi
    elif [ "$COMMENT_COUNT" -gt 0 ] || [ "$REVIEW_COUNT" -gt 0 ]; then
        echo "- 💬 **New feedback received!** Review comments and prepare response." >> "$REPORT_FILE"
        echo "- 📝 **Manual analysis recommended** before responding to maintainers." >> "$REPORT_FILE"
    else
        echo "- ⏳ **Waiting for maintainer review.** No new activity detected." >> "$REPORT_FILE"
    fi
    
    echo -e "${GREEN}✅ Analysis report generated: $REPORT_FILE${NC}"
    
    # Update submitted_prs.json with latest status
    python3 << EOF
import json
from datetime import datetime

with open('$SUBMITTED_PRS', 'r') as f:
    prs_data = json.load(f)

for pr in prs_data['prs']:
    if pr['pr_url'] == '$pr_url':
        pr['last_checked'] = datetime.utcnow().isoformat() + 'Z'
        pr['current_status'] = '$STATE'
        pr['comment_count'] = $COMMENT_COUNT
        pr['review_count'] = $REVIEW_COUNT
        pr['has_new_feedback'] = $COMMENT_COUNT > pr.get('previous_comment_count', 0) or $REVIEW_COUNT > pr.get('previous_review_count', 0)
        pr['previous_comment_count'] = $COMMENT_COUNT
        pr['previous_review_count'] = $REVIEW_COUNT
        break

with open('$SUBMITTED_PRS', 'w') as f:
    json.dump(prs_data, f, indent=2)
EOF
    
    log_message "✅ PR analysis completed for $pr_url"
}

# Main execution
if [ $# -eq 0 ]; then
    echo "Usage: $0 <PR_URL>"
    echo "Example: $0 https://github.com/Scottcjn/grazer-skill/pull/9"
    exit 1
fi

PR_URL="$1"

# Validate PR URL format
if [[ ! "$PR_URL" =~ ^https://github\.com/([^/]+/[^/]+)/pull/([0-9]+)$ ]]; then
    echo -e "${RED}Error: Invalid PR URL format${NC}"
    echo "Expected format: https://github.com/owner/repo/pull/number"
    exit 1
fi

REPO_NAME="${BASH_REMATCH[1]}"
PR_NUMBER="${BASH_REMATCH[2]}"

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is required but not installed${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI is not authenticated${NC}"
    echo "Run 'gh auth login' to authenticate"
    exit 1
fi

# Generate analysis
generate_pr_analysis "$PR_URL" "$PR_NUMBER" "$REPO_NAME"

echo -e "${GREEN}🎉 PR analysis completed successfully!${NC}"