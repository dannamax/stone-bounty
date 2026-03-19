#!/bin/bash

# Stone Bounty - Requirement Analyzer
# Deeply analyzes bounty issue requirements to ensure alignment
# Prevents mismatched submissions

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

# Parse arguments
ISSUE_URL=""
VERBOSE=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --issue-url)
            ISSUE_URL="$2"
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
Stone Bounty Requirement Analyzer - Analyze bounty requirements

Usage: $0 [OPTIONS]

Options:
  --issue-url URL      GitHub issue URL to analyze
  --verbose, -v       Enable verbose output
  --help, -h          Show this help message

Examples:
  $0 --issue-url "https://github.com/repo/issues/123"
  $0 --issue-url "https://github.com/repo/issues/123" --verbose

EOF
    exit 0
fi

if [ -z "$ISSUE_URL" ]; then
    echo -e "${RED}Error: --issue-url is required${NC}"
    echo "Run with --help for usage information"
    exit 1
fi

# Extract repository and issue number from URL
if [[ $ISSUE_URL =~ ^https://github\.com/([^/]+)/([^/]+)/issues/([0-9]+)$ ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
    ISSUE_NUMBER="${BASH_REMATCH[3]}"
else
    echo -e "${RED}Error: Invalid issue URL format${NC}"
    echo "Expected format: https://github.com/owner/repo/issues/number"
    exit 1
fi

echo -e "${BLUE}🔍 Analyzing bounty requirements: $OWNER/$REPO #$ISSUE_NUMBER${NC}"
echo -e "${BLUE}URL: $ISSUE_URL${NC}"
echo

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is required but not installed.${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Get issue details
echo -e "${YELLOW}Fetching issue details...${NC}"
ISSUE_DETAILS=$(gh api "repos/$OWNER/$REPO/issues/$ISSUE_NUMBER" 2>/dev/null || {
    echo -e "${RED}Error: Failed to fetch issue details. Check if issue exists and you have access.${NC}"
    exit 1
})

TITLE=$(echo "$ISSUE_DETAILS" | jq -r '.title')
BODY=$(echo "$ISSUE_DETAILS" | jq -r '.body // ""')
AUTHOR=$(echo "$ISSUE_DETAILS" | jq -r '.user.login')
STATE=$(echo "$ISSUE_DETAILS" | jq -r '.state')
LABELS=$(echo "$ISSUE_DETAILS" | jq -r '[.labels[].name] | join(", ")')

echo -e "${BLUE}Issue Details:${NC}"
echo "  Title: $TITLE"
echo "  Author: $AUTHOR"
echo "  State: $STATE"
echo "  Labels: $LABELS"
echo

# Extract key requirements from issue body
echo -e "${YELLOW}Extracting key requirements...${NC}"

# Look for common requirement patterns
REQUIREMENTS=()

# Check for bounty amount
if [[ "$BODY" =~ ([0-9]+)\s*(RTC|USD|\$) ]]; then
    BOUNTY_AMOUNT="${BASH_REMATCH[1]} ${BASH_REMATCH[2]}"
    REQUIREMENTS+=("Bounty amount: $BOUNTY_AMOUNT")
fi

# Check for technical requirements
if [[ "$BODY" =~ (Requirements|Task|What.*needed): ]]; then
    # Extract requirements section
    REQUIREMENTS_SECTION=$(echo "$BODY" | sed -n '/Requirements:/,/^[^*-]/p' | head -n -1)
    if [ -n "$REQUIREMENTS_SECTION" ]; then
        REQUIREMENTS+=("Technical requirements found in issue body")
    fi
fi

# Check for file mentions
if [[ "$BODY" =~ ([a-zA-Z0-9._/-]+\.[a-zA-Z0-9]+) ]]; then
    FILES_MENTIONED=$(echo "$BODY" | grep -oE '[a-zA-Z0-9._/-]+\.[a-zA-Z0-9]+' | sort -u | head -5 | tr '\n' ', ')
    REQUIREMENTS+=("Files mentioned: $FILES_MENTIONED")
fi

# Check for language/framework mentions
LANGUAGES=("Python" "JavaScript" "TypeScript" "Rust" "Go" "Java" "C++" "C#" "PHP" "Ruby")
for LANG in "${LANGUAGES[@]}"; do
    if [[ "$BODY" =~ $LANG ]] || [[ "$TITLE" =~ $LANG ]]; then
        REQUIREMENTS+=("Language/tech: $LANG")
    fi
done

# Display extracted requirements
if [ ${#REQUIREMENTS[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Extracted Requirements:${NC}"
    for REQ in "${REQUIREMENTS[@]}"; do
        echo "  • $REQ"
    done
else
    echo -e "${YELLOW}⚠️  No specific requirements extracted. Manual analysis required.${NC}"
fi

echo

# Risk assessment
echo -e "${YELLOW}Risk Assessment:${NC}"

RISK_LEVEL="LOW"
RISK_FACTORS=()

# Check if issue is assigned
ASSIGNEES=$(echo "$ISSUE_DETAILS" | jq '.assignees | length')
if [ "$ASSIGNEES" -gt 0 ]; then
    RISK_FACTORS+=("Issue appears to be assigned to someone else")
    RISK_LEVEL="HIGH"
fi

# Check if issue has recent comments
COMMENTS=$(echo "$ISSUE_DETAILS" | jq -r '.comments')
if [ "$COMMENTS" -gt 5 ]; then
    RISK_FACTORS+=("High comment activity - may be actively worked on")
    if [ "$RISK_LEVEL" = "LOW" ]; then
        RISK_LEVEL="MEDIUM"
    fi
fi

# Check creation date
CREATED_AT=$(echo "$ISSUE_DETAILS" | jq -r '.created_at')
DAYS_OLD=$(( ($(date +%s) - $(date -d "$CREATED_AT" +%s)) / 86400 ))
if [ "$DAYS_OLD" -gt 30 ]; then
    RISK_FACTORS+=("Issue is $DAYS_OLD days old - may be stale")
fi

# Display risk assessment
case $RISK_LEVEL in
    "LOW")
        echo -e "${GREEN}🟢 Low Risk${NC}"
        ;;
    "MEDIUM")
        echo -e "${YELLOW}🟡 Medium Risk${NC}"
        ;;
    "HIGH")
        echo -e "${RED}🔴 High Risk${NC}"
        ;;
esac

if [ ${#RISK_FACTORS[@]} -gt 0 ]; then
    echo "Risk factors:"
    for FACTOR in "${RISK_FACTORS[@]}"; do
        echo "  • $FACTOR"
    done
fi

echo

# Recommendations
echo -e "${BLUE}Recommendations:${NC}"

echo "✅ Before proceeding, ensure you:"
echo "  1. Read the entire issue description carefully"
echo "  2. Understand all technical requirements"
echo "  3. Verify you have the necessary skills/tech stack"
echo "  4. Check if the issue is still open and unassigned"
echo "  5. Consider commenting on the issue to express interest"

echo
echo "❌ Avoid submitting if:"
echo "  • The issue seems to be assigned to someone else"
echo "  • Requirements are unclear or ambiguous"
echo "  • You're not confident in your ability to deliver quality work"
echo "  • The bounty amount doesn't justify the effort required"

echo
echo -e "${GREEN}💡 Pro Tip: Take time to fully understand the problem before coding.${NC}"
echo -e "${GREEN}Quality over speed leads to higher success rates!${NC}"

# Save analysis to file for reference
ANALYSIS_FILE="$CONFIG_DIR/analysis_issue_${ISSUE_NUMBER}.json"
cat > "$ANALYSIS_FILE" << EOF
{
  "issue_url": "$ISSUE_URL",
  "title": "$TITLE",
  "analyzed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "requirements": $(printf '%s\n' "${REQUIREMENTS[@]}" | jq -R . | jq -s .),
  "risk_level": "$RISK_LEVEL",
  "risk_factors": $(printf '%s\n' "${RISK_FACTORS[@]}" | jq -R . | jq -s .),
  "days_old": $DAYS_OLD,
  "comment_count": $COMMENTS,
  "assignee_count": $ASSIGNEES
}
EOF

echo
echo -e "${BLUE}Analysis saved to: $ANALYSIS_FILE${NC}"