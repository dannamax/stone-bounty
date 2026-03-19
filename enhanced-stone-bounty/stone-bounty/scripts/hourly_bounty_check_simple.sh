#!/bin/bash
# Stone Bounty - Simplified Hourly Bounty Check Script
# Automatically monitors for new bounty opportunities

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config"
LOG_FILE="$PROJECT_ROOT/logs/bounty_monitor_$(date +%Y%m).log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if GitHub token exists
check_github_token() {
    if [ ! -f "$PROJECT_ROOT/.github_token" ]; then
        log_message "❌ ERROR: GitHub token file not found"
        exit 1
    fi
}

# Main function to search bounties
search_bounties() {
    log_message "🔍 Searching for bounty opportunities..."
    
    GITHUB_TOKEN=$(cat "$PROJECT_ROOT/.github_token")
    TEMP_FILE="/tmp/bounty_search_$$"
    
    # Search for bounty issues (simplified query)
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
         -H "Accept: application/vnd.github.v3+json" \
         "https://api.github.com/search/issues?q=label:bounty+state:open&per_page=20" > "$TEMP_FILE"
    
    # Extract relevant info using jq safely
    if command -v jq &> /dev/null; then
        # Count total results
        TOTAL=$(jq '.total_count // 0' "$TEMP_FILE")
        log_message "Found $TOTAL bounty opportunities"
        
        # Get first few results
        jq -r '.items[0:5][] | "\(.html_url) - \(.title)"' "$TEMP_FILE" 2>/dev/null || true
    else
        log_message "⚠️ jq not available, showing raw count only"
        grep -o '"total_count":[0-9]*' "$TEMP_FILE" | head -1
    fi
    
    # Clean up
    rm -f "$TEMP_FILE"
}

# Update project list with current known opportunities
update_project_list() {
    PROJECT_LIST="$CONFIG_DIR/project_list.json"
    
    # If project list doesn't exist, create it with current RustChain opportunities
    if [ ! -f "$PROJECT_LIST" ]; then
        cat > "$PROJECT_LIST" << EOF
{
  "metadata": {
    "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "total_projects": 9,
    "filtered_count": 9
  },
  "projects": [
    {
      "name": "[BOUNTY] SVG Sanitization in Grazer Image Generation — 5 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/310",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:30:56Z",
      "labels": ["bounty", "security"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "5 RTC",
      "difficulty": "medium"
    },
    {
      "name": "[BOUNTY] Create a RustChain Tutorial Video — 10 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/309",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:30:51Z",
      "labels": ["bounty", "good first issue", "community"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "10 RTC",
      "difficulty": "easy"
    },
    {
      "name": "[BOUNTY] TOFU Key Revocation and Rotation — 15 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/308",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:30:40Z",
      "labels": ["bounty", "security"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "15 RTC",
      "difficulty": "hard"
    },
    {
      "name": "[BOUNTY] Add Signature Verification to /relay/ping — 10 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/307",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:30:35Z",
      "labels": ["bounty", "security"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "10 RTC",
      "difficulty": "medium"
    },
    {
      "name": "[BOUNTY] Add Rate Limiting to Beacon Atlas API — 8 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/306",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:30:33Z",
      "labels": ["bounty", "security"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "8 RTC",
      "difficulty": "medium"
    },
    {
      "name": "[BOUNTY] Report a Bug — 5-15 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/305",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:29:53Z",
      "labels": ["bounty", "bug", "community"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "5-15 RTC",
      "difficulty": "varies"
    },
    {
      "name": "[BOUNTY] Improve README or Docs — 5 RTC per PR",
      "url": "https://github.com/Scottcjn/Rustchain/issues/304",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:29:47Z",
      "labels": ["bounty", "documentation", "good first issue", "community"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "5 RTC",
      "difficulty": "easy"
    },
    {
      "name": "[BOUNTY] Post About RustChain on Social Media — 3 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/303",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:29:40Z",
      "labels": ["bounty", "good first issue", "community"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "3 RTC",
      "difficulty": "easy"
    },
    {
      "name": "[BOUNTY] Write a Blog Post About RustChain — 5 RTC",
      "url": "https://github.com/Scottcjn/Rustchain/issues/302",
      "repository": "Scottcjn/Rustchain",
      "created_at": "2026-02-21T02:29:31Z",
      "labels": ["bounty", "good first issue", "community"],
      "status": "pending",
      "submitted": false,
      "submission_date": null,
      "reward_info": "5 RTC",
      "difficulty": "easy"
    }
  ]
}
EOF
        log_message "✅ Created initial project list with 9 RustChain opportunities"
    else
        # Update timestamp only
        jq --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           '.metadata.last_updated = $timestamp' "$PROJECT_LIST" > "$PROJECT_LIST.tmp" && \
        mv "$PROJECT_LIST.tmp" "$PROJECT_LIST"
        log_message "✅ Updated project list timestamp"
    fi
}

# Main execution
log_message "🚀 Starting hourly bounty monitoring..."

# Check prerequisites
check_github_token

# Search for new bounties
search_bounties

# Update project list
update_project_list

log_message "✅ Hourly bounty check completed successfully"