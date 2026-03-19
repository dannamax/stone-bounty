#!/bin/bash
# Stone Bounty - Issue History Analyzer
# Analyzes GitHub issue history to check for previous submissions by the same user
# Prevents duplicate submissions and ensures quality contribution tracking

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
CONFIG_FILE="$ROOT_DIR/config/automation_config.json"

# Check if config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Configuration file not found!${NC}"
    exit 1
fi

# Load GitHub username from config
GITHUB_USERNAME=$(jq -r '.github_username // empty' "$CONFIG_FILE")
if [[ -z "$GITHUB_USERNAME" ]]; then
    echo -e "${RED}Error: GitHub username not configured in $CONFIG_FILE${NC}"
    exit 1
fi

# Function to display usage
usage() {
    echo "Usage: $0 --issue-url <ISSUE_URL> [--detailed]"
    echo ""
    echo "Options:"
    echo "  --issue-url URL    GitHub issue URL to analyze"
    echo "  --detailed         Show detailed PR analysis (default: summary only)"
    echo "  --help             Show this help message"
}

# Parse arguments
ISSUE_URL=""
DETAILED=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --issue-url)
            ISSUE_URL="$2"
            shift 2
            ;;
        --detailed)
            DETAILED=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$ISSUE_URL" ]]; then
    echo -e "${RED}Error: --issue-url is required${NC}"
    usage
    exit 1
fi

# Validate GitHub issue URL format
if [[ ! "$ISSUE_URL" =~ ^https://github\.com/[^/]+/[^/]+/issues/[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid GitHub issue URL format${NC}"
    echo "Expected format: https://github.com/owner/repo/issues/number"
    exit 1
fi

# Extract repository info
OWNER_REPO=$(echo "$ISSUE_URL" | sed -E 's|https://github\.com/([^/]+/[^/]+)/issues/[0-9]+|\1|')
ISSUE_NUMBER=$(echo "$ISSUE_URL" | sed -E 's|https://github\.com/[^/]+/[^/]+/issues/([0-9]+)|\1|')

echo -e "${BLUE}=== Issue History Analysis ===${NC}"
echo -e "${BLUE}Issue URL: $ISSUE_URL${NC}"
echo -e "${BLUE}GitHub Username: $GITHUB_USERNAME${NC}"
echo

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Please install GitHub CLI: https://cli.github.com/"
    exit 1
fi

# Check GitHub authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI is not authenticated${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Get issue details
echo -e "${YELLOW}🔍 Fetching issue details...${NC}"
ISSUE_DETAILS=$(gh api "repos/$OWNER_REPO/issues/$ISSUE_NUMBER" 2>/dev/null || {
    echo -e "${RED}Error: Failed to fetch issue details. Check if issue exists and you have access.${NC}"
    exit 1
})

ISSUE_TITLE=$(echo "$ISSUE_DETAILS" | jq -r '.title')
ISSUE_STATE=$(echo "$ISSUE_DETAILS" | jq -r '.state')
ISSUE_CREATED=$(echo "$ISSUE_DETAILS" | jq -r '.created_at')

echo -e "${BLUE}Issue Title: $ISSUE_TITLE${NC}"
echo -e "${BLUE}Issue State: $ISSUE_STATE${NC}"
echo -e "${BLUE}Created: $ISSUE_CREATED${NC}"
echo

if [[ "$ISSUE_STATE" != "open" ]]; then
    echo -e "${RED}❌ Issue is not open! State: $ISSUE_STATE${NC}"
    exit 1
fi

# Get all PRs that reference this issue
echo -e "${YELLOW}🔍 Searching for PRs referencing this issue...${NC}"

# Search for PRs in the repository that mention this issue
SEARCH_QUERY="repo:$OWNER_REPO is:pr $ISSUE_NUMBER"
PR_SEARCH_RESULTS=$(gh search prs --match=exact "$ISSUE_NUMBER" --repo "$OWNER_REPO" --json number,title,author,createdAt,url,state 2>/dev/null || {
    echo "No PRs found referencing this issue."
    echo "{}"
})

# Alternative method: get issue timeline to find referenced PRs
echo -e "${YELLOW}🔍 Checking issue timeline for referenced PRs...${NC}"
TIMELINE_EVENTS=$(gh api "repos/$OWNER_REPO/issues/$ISSUE_NUMBER/timeline" --paginate 2>/dev/null || {
    echo "Could not fetch timeline events."
    echo "[]"
})

# Extract PR references from timeline
REFERENCED_PRS=()
while IFS= read -r event; do
    if [[ "$event" == *"cross-referenced"* ]] && [[ "$event" == *"pull_request"* ]]; then
        PR_URL=$(echo "$event" | jq -r '.source.issue.html_url // empty')
        if [[ -n "$PR_URL" ]]; then
            REFERENCED_PRS+=("$PR_URL")
        fi
    fi
done < <(echo "$TIMELINE_EVENTS" | jq -c '.[]')

# Check for PRs authored by current user
echo -e "${YELLOW}🔍 Checking for submissions by $GITHUB_USERNAME...${NC}"

USER_SUBMISSIONS=()
TOTAL_REFERENCED=${#REFERENCED_PRS[@]}

if [[ $TOTAL_REFERENCED -gt 0 ]]; then
    echo -e "${BLUE}Found $TOTAL_REFERENCED referenced PRs:${NC}"
    for pr_url in "${REFERENCED_PRS[@]}"; do
        echo "  - $pr_url"
        
        # Extract PR number from URL
        if [[ $pr_url =~ /pull/([0-9]+)$ ]]; then
            PR_NUM="${BASH_REMATCH[1]}"
            REPO_NAME=$(echo "$OWNER_REPO" | cut -d'/' -f2)
            
            # Get PR author
            PR_AUTHOR=$(gh api "repos/$OWNER_REPO/pulls/$PR_NUM" 2>/dev/null | jq -r '.user.login // empty' || echo "unknown")
            
            if [[ "$PR_AUTHOR" == "$GITHUB_USERNAME" ]]; then
                USER_SUBMISSIONS+=("$pr_url")
                echo -e "${RED}    ⚠️  Authored by you: $pr_url${NC}"
            else
                echo -e "${GREEN}    ✅ Authored by: $PR_AUTHOR${NC}"
            fi
        fi
    done
else
    echo -e "${GREEN}✅ No PRs found referencing this issue${NC}"
fi

# Also check closed PRs that might have been submitted by user
echo -e "${YELLOW}🔍 Checking for closed PRs by $GITHUB_USERNAME in this repo...${NC}"
USER_CLOSED_PRS=$(gh search prs --repo "$OWNER_REPO" --author "$GITHUB_USERNAME" --state closed --json number,title,url,createdAt 2>/dev/null || echo "[]")

USER_CLOSED_COUNT=$(echo "$USER_CLOSED_PRS" | jq 'length')
if [[ $USER_CLOSED_COUNT -gt 0 ]]; then
    echo -e "${YELLOW}Found $USER_CLOSED_COUNT closed PRs by you in this repository:${NC}"
    echo "$USER_CLOSED_PRS" | jq -r '.[] | "  - \(.title) (\(.url))"'
    
    # Check if any closed PRs mention this issue
    while IFS= read -r pr; do
        PR_TITLE=$(echo "$pr" | jq -r '.title')
        PR_URL=$(echo "$pr" | jq -r '.url')
        if [[ "$PR_TITLE" == *"$ISSUE_NUMBER"* ]] || [[ "$PR_TITLE" == *"#$ISSUE_NUMBER"* ]]; then
            USER_SUBMISSIONS+=("$PR_URL")
            echo -e "${RED}    ⚠️  References this issue: $PR_URL${NC}"
        fi
    done < <(echo "$USER_CLOSED_PRS" | jq -c '.[]')
fi

# Final analysis
USER_SUBMISSION_COUNT=${#USER_SUBMISSIONS[@]}

echo
echo -e "${BLUE}=== Analysis Summary ===${NC}"
echo -e "${BLUE}Total referenced PRs: $TOTAL_REFERENCED${NC}"
echo -e "${BLUE}Your submissions found: $USER_SUBMISSION_COUNT${NC}"

if [[ $USER_SUBMISSION_COUNT -gt 0 ]]; then
    echo -e "${RED}❌ DUPLICATE SUBMISSION DETECTED!${NC}"
    echo -e "${RED}You have already submitted PR(s) for this issue:${NC}"
    for submission in "${USER_SUBMISSIONS[@]}"; do
        echo -e "${RED}  - $submission${NC}"
    done
    echo
    echo -e "${YELLOW}Recommendation: DO NOT submit another PR for this issue.${NC}"
    echo -e "${YELLOW}Consider improving your existing submission or choosing a different issue.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ NO DUPLICATE SUBMISSIONS FOUND!${NC}"
    echo -e "${GREEN}It is safe to proceed with a new submission for this issue.${NC}"
    
    # Check submission frequency (last 24 hours)
    echo -e "${YELLOW}🔍 Checking recent submission frequency...${NC}"
    SUBMISSION_LOG="$ROOT_DIR/submissions.log"
    if [[ -f "$SUBMISSION_LOG" ]]; then
        TODAY=$(date -u +%Y-%m-%d)
        TODAY_SUBMISSIONS=$(grep "$TODAY" "$SUBMISSION_LOG" | grep "$OWNER_REPO" | wc -l)
        echo -e "${BLUE}Today's submissions for $OWNER_REPO: $TODAY_SUBMISSIONS${NC}"
        
        if [[ $TODAY_SUBMISSIONS -ge 2 ]]; then
            echo -e "${RED}⚠️  WARNING: You have already submitted $TODAY_SUBMISSIONS PRs today for this repository${NC}"
            echo -e "${RED}Daily limit is 2 submissions per repository${NC}"
            echo -e "${YELLOW}Consider waiting until tomorrow or choosing a different repository${NC}"
            # Don't exit, just warn - let user decide
        else
            echo -e "${GREEN}✅ Within daily submission limits${NC}"
        fi
    fi
    
    echo
    echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}You can safely proceed with this bounty submission.${NC}"
    exit 0
fi