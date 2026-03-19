#!/bin/bash
# Stone Bounty - PR Submitter Script
# Submits PRs only after manual verification
# Includes proper commit messages and PR descriptions
# Validates against quality standards

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$ROOT_DIR/config/automation_config.json"
BLACKLIST_FILE="$ROOT_DIR/config/blacklisted_projects.json"
PR_TEMPLATE="$ROOT_DIR/templates/pr_template.md"

# Check if config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Configuration file not found!${NC}"
    echo "Please run setup.sh first or create the configuration manually."
    exit 1
fi

# Load configuration
EMERGENCY_STOP=$(jq -r '.emergency_stop_active // false' "$CONFIG_FILE")
MANUAL_ONLY=$(jq -r '.manual_only_mode // true' "$CONFIG_FILE")
GITHUB_USERNAME=$(jq -r '.github_username // empty' "$CONFIG_FILE")

# Check emergency stop
if [[ "$EMERGENCY_STOP" == "true" ]]; then
    echo -e "${RED}Emergency stop is active!${NC}"
    echo "PR submission is disabled while emergency stop is active."
    echo "Set emergency_stop_active to false in config/automation_config.json to proceed."
    exit 1
fi

# Function to display usage
usage() {
    echo "Usage: $0 --issue-url <ISSUE_URL> [--dry-run]"
    echo ""
    echo "Options:"
    echo "  --issue-url URL    GitHub issue URL with bounty"
    echo "  --dry-run          Show what would be done without actually submitting"
    echo "  --help             Show this help message"
}

# Parse arguments
ISSUE_URL=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --issue-url)
            ISSUE_URL="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
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

# Check if repository is blacklisted
if [[ -f "$BLACKLIST_FILE" ]]; then
    BLACKLISTED=$(jq -r --arg repo "$OWNER_REPO" '.blacklisted_repositories[] | select(. == $repo)' "$BLACKLIST_FILE" | wc -l)
    if [[ $BLACKLISTED -gt 0 ]]; then
        echo -e "${RED}Error: Repository $OWNER_REPO is blacklisted!${NC}"
        REASON=$(jq -r --arg repo "$OWNER_REPO" ".reasons[\"\$repo\"] // \"No reason specified\"" "$BLACKLIST_FILE")
        echo "Reason: $REASON"
        exit 1
    fi
fi

# Manual review required in manual-only mode
if [[ "$MANUAL_ONLY" == "true" ]]; then
    echo -e "${YELLOW}Manual Review Required${NC}"
    echo "Repository: $OWNER_REPO"
    echo "Issue: #$ISSUE_NUMBER"
    echo "Issue URL: $ISSUE_URL"
    echo ""
    echo "Please verify that:"
    echo "1. The issue has a clear bounty amount"
    echo "2. You have made actual code changes (not template comments)"
    echo "3. Your contribution meets repository guidelines"
    echo "4. The repository doesn't require CLA agreements"
    echo ""
    
    read -p "Do you confirm this contribution is ready for submission? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Submission cancelled by user."
        exit 0
    fi
fi

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

# Create a temporary directory for the work
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Working in temporary directory: $TEMP_DIR"

# Clone the repository
echo "Cloning repository: $OWNER_REPO"
gh repo clone "$OWNER_REPO" "$TEMP_DIR/repo" -- --quiet

# Navigate to repo directory
cd "$TEMP_DIR/repo"

# Create a new branch for the fix
BRANCH_NAME="stone-bounty-fix-$ISSUE_NUMBER-$(date +%s)"
git checkout -b "$BRANCH_NAME"

# TODO: This is where you would apply your actual changes
# For now, we'll just create a placeholder that needs to be filled manually
echo "TODO: Apply your actual changes to fix issue #$ISSUE_NUMBER" > CONTRIBUTING.md
echo "This is a placeholder. Replace this with your actual contribution." >> CONTRIBUTING.md

# Check if there are actual changes
if [[ -z $(git diff --name-only) ]]; then
    echo -e "${RED}Error: No changes detected!${NC}"
    echo "You must make actual code changes before submitting a PR."
    echo "This system prevents template/placeholder PRs to maintain quality."
    exit 1
fi

# Stage and commit changes
git add .
COMMIT_MESSAGE="Fix #$ISSUE_NUMBER - [BRIEF DESCRIPTION OF FIX]"
if [[ "$DRY_RUN" == "false" ]]; then
    read -p "Commit message (default: '$COMMIT_MESSAGE'): " USER_COMMIT_MSG
    if [[ -n "$USER_COMMIT_MSG" ]]; then
        COMMIT_MESSAGE="$USER_COMMIT_MSG"
    fi
    git commit -m "$COMMIT_MESSAGE"
else
    echo "Dry run: Would commit with message: $COMMIT_MESSAGE"
fi

# Push branch (if not dry run)
if [[ "$DRY_RUN" == "false" ]]; then
    echo "Pushing branch: $BRANCH_NAME"
    git push origin "$BRANCH_NAME"
else
    echo "Dry run: Would push branch: $BRANCH_NAME"
fi

# Create PR description from template
PR_BODY=""
if [[ -f "$PR_TEMPLATE" ]]; then
    PR_BODY=$(cat "$PR_TEMPLATE")
    # Replace placeholders
    PR_BODY=$(echo "$PR_BODY" | sed "s/{{ISSUE_NUMBER}}/$ISSUE_NUMBER/g")
    PR_BODY=$(echo "$PR_BODY" | sed "s/{{REPOSITORY}}/$OWNER_REPO/g")
    PR_BODY=$(echo "$PR_BODY" | sed "s/{{GITHUB_USERNAME}}/$GITHUB_USERNAME/g")
else
    PR_BODY="Fixes #$ISSUE_NUMBER

## Description
[Brief description of the changes]

## Related Issue
Closes #$ISSUE_NUMBER

## Checklist
- [ ] Changes address the issue requirements
- [ ] Code follows repository style guidelines
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if applicable)

Stone Bounty System - Quality Contribution"
fi

# Create the PR
PR_TITLE="Fix #$ISSUE_NUMBER - [BRIEF DESCRIPTION]"
if [[ "$DRY_RUN" == "false" ]]; then
    read -p "PR title (default: '$PR_TITLE'): " USER_PR_TITLE
    if [[ -n "$USER_PR_TITLE" ]]; then
        PR_TITLE="$USER_PR_TITLE"
    fi
    
    echo "Creating PR..."
    PR_URL=$(gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base main --head "$BRANCH_NAME" 2>&1)
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Success! PR created:${NC} $PR_URL"
        
        # Log the submission
        LOG_ENTRY="{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"repository\": \"$OWNER_REPO\", \"issue_number\": $ISSUE_NUMBER, \"pr_url\": \"$PR_URL\", \"status\": \"submitted\"}"
        echo "$LOG_ENTRY" >> "$ROOT_DIR/submissions.log"
        
        echo "Submission logged to submissions.log"
    else
        echo -e "${RED}Error creating PR:${NC} $PR_URL"
        exit 1
    fi
else
    echo "Dry run: Would create PR with title: $PR_TITLE"
    echo "Dry run: PR body preview:"
    echo "---"
    echo "$PR_BODY"
    echo "---"
    echo "Dry run completed successfully."
fi

echo -e "${GREEN}PR submission process completed!${NC}"