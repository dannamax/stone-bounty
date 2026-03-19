#!/bin/bash
# Stone Bounty - Hourly Bounty Check with PR Monitoring
# Automatically monitors for new bounty opportunities AND tracks submitted PRs

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
        log_message "❌ ERROR: GitHub token file not found at $PROJECT_ROOT/.github_token"
        exit 1
    fi
}

# Main execution
log_message "🚀 Starting hourly bounty monitoring with PR tracking..."

# Check prerequisites
check_github_token

# Run bounty opportunity monitoring
log_message "🔍 Checking for new bounty opportunities..."
"$SCRIPT_DIR/hourly_bounty_check_simple.sh"

# Run PR monitoring
log_message "👀 Monitoring submitted PRs for maintainer feedback..."
"$SCRIPT_DIR/pr_monitor.sh"

# Display summary
log_message "✅ Hourly monitoring completed successfully"