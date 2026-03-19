#!/bin/bash
# Stone Bounty - Hourly Comprehensive Monitor
# Monitors both new bounty opportunities and existing PR status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$ROOT_DIR/logs/comprehensive_monitor_$(date +%Y%m).log"

# Create logs directory if it doesn't exist
mkdir -p "$ROOT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "🚀 Starting hourly comprehensive monitoring..."

# 1. Check for new bounty opportunities
log_message "🔍 Checking for new bounty opportunities..."
"$SCRIPT_DIR/hourly_bounty_check_simple.sh"

# 2. Monitor existing PRs
log_message "👀 Monitoring submitted PRs for feedback..."
if [ -f "$ROOT_DIR/config/submitted_prs.json" ]; then
    SUBMITTED_PR_COUNT=$(jq '.prs | length' "$ROOT_DIR/config/submitted_prs.json")
    if [ "$SUBMITTED_PR_COUNT" -gt 0 ]; then
        "$SCRIPT_DIR/pr_monitor.sh"
    else
        log_message "📝 No submitted PRs to monitor"
    fi
else
    log_message "📝 No submitted PRs file found"
fi

# 3. Generate summary report
log_message "📊 Generating monitoring summary..."
TOTAL_PROJECTS=$(jq -r '.metadata.total_projects // 0' "$ROOT_DIR/config/project_list.json" 2>/dev/null || echo "0")
ACTIVE_PRS=$(jq -r '.prs | length' "$ROOT_DIR/config/submitted_prs.json" 2>/dev/null || echo "0")

log_message "✅ Hourly comprehensive monitoring completed!"
log_message "   Total projects tracked: $TOTAL_PROJECTS"
log_message "   Active PRs monitored: $ACTIVE_PRS"

# Optional: Send notification if there are updates
if [ "$ACTIVE_PRS" -gt 0 ]; then
    RECENT_COMMENTS=$(jq -r '.prs[] | select(.last_checked_comments > .last_processed_comments) | .url' "$ROOT_DIR/config/submitted_prs.json" 2>/dev/null | wc -l)
    if [ "$RECENT_COMMENTS" -gt 0 ]; then
        log_message "🔔 Found $RECENT_COMMENTS PR(s) with new comments requiring attention!"
    fi
fi