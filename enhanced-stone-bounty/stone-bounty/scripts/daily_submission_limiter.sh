#!/bin/bash

# Stone Bounty - Daily Submission Limiter
# Ensures maximum 2 PR submissions per project per day

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"
STATE_FILE="$CONFIG_DIR/daily_submission_state.json"

# Create state file if it doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << EOF
{
  "date": "$(date +%Y-%m-%d)",
  "submissions": {}
}
EOF
fi

# Load current state
CURRENT_DATE=$(date +%Y-%m-%d)
STATE_DATE=$(jq -r '.date' "$STATE_FILE")

# Reset if new day
if [ "$STATE_DATE" != "$CURRENT_DATE" ]; then
    jq --arg date "$CURRENT_DATE" '.date = $date | .submissions = {}' "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
fi

# Function to check if can submit
can_submit_to_project() {
    local repo_url="$1"
    
    # Check current submission count
    COUNT=$(jq --arg repo "$repo_url" '.submissions[$repo] // 0' "$STATE_FILE")
    
    if [ "$COUNT" -lt 2 ]; then
        echo "true"
        return 0
    else
        echo "false"
        return 1
    fi
}

# Function to record submission
record_submission() {
    local repo_url="$1"
    
    # Increment submission count
    jq --arg repo "$repo_url" \
       '.submissions[$repo] = (.submissions[$repo] // 0) + 1' \
       "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
}

# Main execution
if [ $# -eq 0 ]; then
    echo "Usage: $0 [--check REPO_URL] [--record REPO_URL]"
    exit 1
fi

case "$1" in
    "--check")
        if [ $# -ne 2 ]; then
            echo "Usage: $0 --check REPO_URL"
            exit 1
        fi
        can_submit_to_project "$2"
        ;;
    "--record")
        if [ $# -ne 2 ]; then
            echo "Usage: $0 --record REPO_URL"
            exit 1
        fi
        record_submission "$2"
        echo "Recorded submission for $2"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: $0 [--check REPO_URL] [--record REPO_URL]"
        exit 1
        ;;
esac