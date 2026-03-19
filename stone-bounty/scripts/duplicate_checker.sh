#!/bin/bash
# Stone Bounty - Duplicate Submission Checker
# Checks for duplicate submissions using both local records and GitHub history

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_LIST="$ROOT_DIR/config/project_list.json"
SUBMISSION_LOG="$ROOT_DIR/submissions.log"

# Function to check local records
check_local_records() {
    local issue_url="$1"
    local issue_number=$(echo "$issue_url" | sed -E 's|.*issues/([0-9]+)|\1|')
    
    echo -e "${BLUE}🔍 Checking local project records...${NC}"
    
    # Check if already marked as submitted in project list
    local submitted=$(jq -r --arg url "$issue_url" '.projects[] | select(.url == $url) | .submitted' "$PROJECT_LIST" 2>/dev/null || echo "false")
    
    if [[ "$submitted" == "true" ]]; then
        echo -e "${RED}❌ LOCAL RECORD: Issue already marked as submitted${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ LOCAL RECORD: Issue not previously submitted${NC}"
    return 0
}

# Function to check GitHub history
check_github_history() {
    local issue_url="$1"
    local owner_repo=$(echo "$issue_url" | sed -E 's|https://github\.com/([^/]+/[^/]+)/issues/[0-9]+|\1|')
    local issue_number=$(echo "$issue_url" | sed -E 's|.*issues/([0-9]+)|\1|')
    
    echo -e "${BLUE}🔍 Checking GitHub issue history...${NC}"
    
    # Get issue details
    local issue_details=$(gh api "repos/$owner_repo/issues/$issue_number" 2>/dev/null || {
        echo -e "${RED}Error: Could not fetch issue details${NC}"
        return 1
    })
    
    # Check if issue is closed (might indicate resolved)
    local issue_state=$(echo "$issue_details" | jq -r '.state')
    if [[ "$issue_state" == "closed" ]]; then
        echo -e "${YELLOW}⚠️  GITHUB: Issue is closed - may be resolved${NC}"
        # Check if it was closed by a PR
        local events=$(gh api "repos/$owner_repo/issues/$issue_number/events" 2>/dev/null || echo "[]")
        local pr_closed=$(echo "$events" | jq -r '.[] | select(.event == "closed" and .commit_id != null) | .commit_id' | head -1)
        if [[ -n "$pr_closed" ]]; then
            echo -e "${RED}❌ GITHUB: Issue closed by PR - likely already resolved${NC}"
            return 1
        fi
    fi
    
    # Check for existing PRs that reference this issue
    local repo_name=$(echo "$owner_repo" | cut -d'/' -f2)
    local search_query="repo:$owner_repo is:pr $issue_number"
    local existing_prs=$(gh search prs --query "$search_query" --json number,title,url 2>/dev/null || echo '{"data":[]}')
    
    if [[ "$existing_prs" != '{"data":[]}' ]]; then
        local pr_count=$(echo "$existing_prs" | jq '.data | length')
        if [[ $pr_count -gt 0 ]]; then
            echo -e "${RED}❌ GITHUB: Found $pr_count existing PR(s) referencing this issue:${NC}"
            echo "$existing_prs" | jq -r '.data[] | "   - #\(.number): \(.title) (\(.url))"'
            return 1
        fi
    fi
    
    echo -e "${GREEN}✅ GITHUB: No duplicate submissions found${NC}"
    return 0
}

# Function to check submission log
check_submission_log() {
    local issue_url="$1"
    local issue_number=$(echo "$issue_url" | sed -E 's|.*issues/([0-9]+)|\1|')
    
    echo -e "${BLUE}🔍 Checking submission log...${NC}"
    
    if [[ -f "$SUBMISSION_LOG" ]]; then
        local today=$(date +%Y-%m-%d)
        local today_submissions=$(grep "$issue_number" "$SUBMISSION_LOG" | grep "$today" | wc -l)
        
        if [[ $today_submissions -gt 0 ]]; then
            if [[ $today_submissions -ge 2 ]]; then
                echo -e "${RED}❌ SUBMISSION LOG: Already submitted $today_submissions times today (max 2 allowed)${NC}"
                return 1
            else
                echo -e "${YELLOW}⚠️  SUBMISSION LOG: Already submitted $today_submissions time(s) today${NC}"
            fi
        else
            echo -e "${GREEN}✅ SUBMISSION LOG: No recent submissions for this issue${NC}"
        fi
    else
        echo -e "${GREEN}✅ SUBMISSION LOG: No submission log found (first time)${NC}"
    fi
    
    return 0
}

# Main function
main() {
    if [[ $# -ne 1 ]]; then
        echo "Usage: $0 <ISSUE_URL>"
        exit 1
    fi
    
    local issue_url="$1"
    
    echo -e "${BLUE}=== Duplicate Submission Check ===${NC}"
    echo -e "${BLUE}Issue URL: $issue_url${NC}"
    echo
    
    local can_proceed=true
    
    # Check all three sources
    if ! check_local_records "$issue_url"; then
        can_proceed=false
    fi
    
    echo
    
    if ! check_github_history "$issue_url"; then
        can_proceed=false
    fi
    
    echo
    
    if ! check_submission_log "$issue_url"; then
        can_proceed=false
    fi
    
    echo
    
    if [[ "$can_proceed" == "true" ]]; then
        echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
        echo -e "${GREEN}Safe to proceed with this bounty submission.${NC}"
        exit 0
    else
        echo -e "${RED}❌ DUPLICATE DETECTED!${NC}"
        echo -e "${RED}Do not submit to this issue to avoid spam.${NC}"
        exit 1
    fi
}

main "$@"