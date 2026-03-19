#!/bin/bash

# Stone Bounty - Contribution Validator
# Validates PR quality before submission to ensure high standards
# Prevents template comments and ensures actual code changes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"

# Load configuration
if [ ! -f "$CONFIG_DIR/automation_config.json" ]; then
    echo -e "${RED}Error: Configuration file not found!${NC}"
    echo "Please run setup.sh first or create config/automation_config.json"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install jq: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
    exit 1
fi

# Parse arguments
PR_URL=""
VERBOSE=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --pr-url)
            PR_URL="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            HELP=true
            shift
            ;;
    esac
done

if [ "$HELP" = true ]; then
    cat << EOF
Stone Bounty Validator - Validate PR Quality

Usage: $0 [OPTIONS]

Options:
  --pr-url URL        GitHub PR URL to validate
  --verbose, -v       Enable verbose output
  --help, -h          Show this help message

Examples:
  $0 --pr-url "https://github.com/repo/pull/123"
  $0 --pr-url "https://github.com/repo/pull/123" --verbose

EOF
    exit 0
fi

if [ -z "$PR_URL" ]; then
    echo -e "${RED}Error: --pr-url is required${NC}"
    echo "Run with --help for usage information"
    exit 1
fi

# Extract repository and PR number from URL
if [[ $PR_URL =~ ^https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)$ ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
    PR_NUMBER="${BASH_REMATCH[3]}"
else
    echo -e "${RED}Error: Invalid PR URL format${NC}"
    echo "Expected format: https://github.com/owner/repo/pull/number"
    exit 1
fi

echo -e "${BLUE}🔍 Validating PR: $OWNER/$REPO #$PR_NUMBER${NC}"
echo -e "${BLUE}URL: $PR_URL${NC}"
echo

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is required but not installed.${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Verify GitHub authentication
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI is not authenticated.${NC}"
    echo "Run 'gh auth login' to authenticate"
    exit 1
fi

# Get PR details
echo -e "${YELLOW}Fetching PR details...${NC}"
PR_DETAILS=$(gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER" 2>/dev/null || {
    echo -e "${RED}Error: Failed to fetch PR details. Check if PR exists and you have access.${NC}"
    exit 1
})

TITLE=$(echo "$PR_DETAILS" | jq -r '.title')
BODY=$(echo "$PR_DETAILS" | jq -r '.body // ""')
AUTHOR=$(echo "$PR_DETAILS" | jq -r '.user.login')
STATE=$(echo "$PR_DETAILS" | jq -r '.state')
CREATED_AT=$(echo "$PR_DETAILS" | jq -r '.created_at')

if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}PR Details:${NC}"
    echo "  Title: $TITLE"
    echo "  Author: $AUTHOR"
    echo "  State: $STATE"
    echo "  Created: $CREATED_AT"
    echo
fi

# Get PR files and changes
echo -e "${YELLOW}Analyzing PR changes...${NC}"
PR_FILES=$(gh api "repos/$OWNER/$REPO/pulls/$PR_NUMBER/files" 2>/dev/null || {
    echo -e "${RED}Error: Failed to fetch PR files.${NC}"
    exit 1
})

FILE_COUNT=$(echo "$PR_FILES" | jq 'length')
echo -e "${BLUE}Files changed: $FILE_COUNT${NC}"

if [ "$FILE_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ FAILED: No files changed in PR${NC}"
    exit 1
fi

# Check for template comments or placeholder content
echo -e "${YELLOW}Checking for template comments and placeholder content...${NC}"

HAS_TEMPLATE_COMMENTS=false
HAS_ACTUAL_CHANGES=false

for ((i=0; i<$FILE_COUNT; i++)); do
    FILENAME=$(echo "$PR_FILES" | jq -r ".[$i].filename")
    PATCH=$(echo "$PR_FILES" | jq -r ".[$i].patch // \"\"")
    
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}File: $FILENAME${NC}"
    fi
    
    # Skip if no patch (new file without content diff)
    if [ -z "$PATCH" ]; then
        HAS_ACTUAL_CHANGES=true
        continue
    fi
    
    # Check for common template comments
    if echo "$PATCH" | grep -Eiq "(TODO|FIXME|PLACEHOLDER|TEMPLATE|REPLACE_THIS|YOUR_CODE_HERE|example|sample|test.*test)"; then
        echo -e "${RED}⚠️  Template/placeholder detected in: $FILENAME${NC}"
        HAS_TEMPLATE_COMMENTS=true
        if [ "$VERBOSE" = true ]; then
            echo "$PATCH" | grep -Ei "(TODO|FIXME|PLACEHOLDER|TEMPLATE|REPLACE_THIS|YOUR_CODE_HERE|example|sample|test.*test)" || true
        fi
    fi
    
    # Check if there are actual meaningful changes
    # Count non-whitespace lines added
    ADDED_LINES=$(echo "$PATCH" | grep -E "^\\+" | grep -v "^\\+\\s*$" | wc -l)
    if [ "$ADDED_LINES" -gt 0 ]; then
        HAS_ACTUAL_CHANGES=true
    fi
    
    if [ "$VERBOSE" = true ]; then
        REMOVED_LINES=$(echo "$PATCH" | grep -E "^-" | grep -v "^-\\s*$" | wc -l)
        echo "  Added lines: $ADDED_LINES, Removed lines: $REMOVED_LINES"
    fi
done

echo

# Validation checks
VALIDATION_PASSED=true

# Check 1: Must have actual changes
if [ "$HAS_ACTUAL_CHANGES" = false ]; then
    echo -e "${RED}❌ FAILED: No actual code changes detected${NC}"
    VALIDATION_PASSED=false
else
    echo -e "${GREEN}✅ PASSED: Actual code changes detected${NC}"
fi

# Check 2: No template comments
if [ "$HAS_TEMPLATE_COMMENTS" = true ]; then
    echo -e "${RED}❌ FAILED: Template/placeholder comments detected${NC}"
    VALIDATION_PASSED=false
else
    echo -e "${GREEN}✅ PASSED: No template comments found${NC}"
fi

# Check 3: PR title quality
if [[ "$TITLE" =~ ^(fix|feat|docs|chore|refactor|test|style): ]]; then
    echo -e "${GREEN}✅ PASSED: PR title follows conventional commits format${NC}"
elif [[ "$TITLE" =~ ^(update|add|remove|improve) ]]; then
    echo -e "${GREEN}✅ PASSED: PR title is descriptive${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: PR title may not be descriptive enough${NC}"
    echo -e "   Current title: \"$TITLE\""
    echo -e "   Consider starting with: fix:, feat:, docs:, add:, improve:, etc."
fi

# Check 4: PR body quality
if [ -z "$BODY" ] || [[ "$BODY" =~ ^(fixes|closes|resolves) ]]; then
    echo -e "${YELLOW}⚠️  WARNING: PR description is minimal${NC}"
else
    BODY_WORD_COUNT=$(echo "$BODY" | wc -w)
    if [ "$BODY_WORD_COUNT" -lt 10 ]; then
        echo -e "${YELLOW}⚠️  WARNING: PR description is brief ($BODY_WORD_COUNT words)${NC}"
    else
        echo -e "${GREEN}✅ PASSED: PR has adequate description ($BODY_WORD_COUNT words)${NC}"
    fi
fi

echo

# Final validation result
if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}🎉 VALIDATION PASSED!${NC}"
    echo -e "${GREEN}This PR meets quality standards for bounty submission.${NC}"
    echo
    echo -e "${BLUE}Recommendation: ✅ APPROVED for bounty submission${NC}"
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED!${NC}"
    echo -e "${RED}This PR does not meet quality standards.${NC}"
    echo
    echo -e "${YELLOW}Required fixes:${NC}"
    if [ "$HAS_ACTUAL_CHANGES" = false ]; then
        echo "  - Add meaningful code changes (not just whitespace/formatting)"
    fi
    if [ "$HAS_TEMPLATE_COMMENTS" = true ]; then
        echo "  - Remove all TODO/FIXME/PLACEHOLDER comments"
        echo "  - Replace template content with actual implementation"
    fi
    echo
    echo -e "${RED}Recommendation: ❌ REJECTED - Fix issues before submission${NC}"
    exit 1
fi