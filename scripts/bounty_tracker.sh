#!/bin/bash
# Stone Bounty - Real-time Bounty Tracker
# Monitors GitHub for new bounty opportunities every hour
# Tracks submission status to avoid duplicates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/bounty_tracker.json"
LOG_FILE="$PROJECT_ROOT/logs/bounty_tracker.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check if bounty has been submitted
is_bounty_submitted() {
    local issue_url="$1"
    if [ -f "$CONFIG_FILE" ]; then
        if jq -e --arg url "$issue_url" '.submitted_bounties[] | select(.issue_url == $url)' "$CONFIG_FILE" > /dev/null 2>&1; then
            return 0  # Already submitted
        fi
    fi
    return 1  # Not submitted
}

# Function to add bounty to submitted list
mark_bounty_submitted() {
    local issue_url="$1"
    local pr_url="$2"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo '{"tracked_bounties": [], "submitted_bounties": []}' > "$CONFIG_FILE"
    fi
    
    # Add to submitted bounties
    jq --arg url "$issue_url" --arg pr "$pr_url" --arg date "$(date -Iseconds)" '
        .submitted_bounties += [{
            "issue_url": $url,
            "pr_url": $pr,
            "submission_date": $date,
            "status": "submitted"
        }]
    ' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    
    log_message "Marked bounty as submitted: $issue_url"
}

# Function to search for bounty issues
search_bounty_issues() {
    log_message "🔍 Searching for new bounty opportunities..."
    
    # Search for bounty-labeled issues in relevant repositories
    local search_repos=("Scottcjn/Rustchain" "Flutter-Bounty-Hunters/super_editor")
    local found_bounties=()
    
    for repo in "${search_repos[@]}"; do
        log_message "Searching repository: $repo"
        
        # Use GitHub API to search for bounty issues
        local api_response
        api_response=$(curl -s -H "Authorization: token $(cat $PROJECT_ROOT/.github_token)" \
            "https://api.github.com/repos/$repo/issues?labels=bounty&state=open")
        
        # Parse the response and extract bounty info
        echo "$api_response" | jq -r --arg repo "$repo" '
            if type == "array" then
                .[] | select(.pull_request | not) | 
                "\($repo)|\(.number)|\(.title)|\(.html_url)|\(.created_at)"
            else
                ""
            end
        ' >> /tmp/bounty_search_results.txt
    done
    
    # Also search globally for bounty issues (limited scope)
    local global_search
    global_search=$(curl -s -H "Authorization: token $(cat $PROJECT_ROOT/.github_token)" \
        "https://api.github.com/search/issues?q=label:bounty+state:open+sort:created-desc&per_page=10")
    
    echo "$global_search" | jq -r '
        if .items then
            .items[] | "\(.repository_url | sub(\"https://api.github.com/repos/\"; \"\"))|\(.number)|\(.title)|\(.html_url)|\(.created_at)"
        else
            ""
        end
    ' >> /tmp/bounty_search_results.txt
    
    # Remove duplicates and process results
    sort -u /tmp/bounty_search_results.txt > /tmp/bounty_results_unique.txt
    
    # Process each bounty
    while IFS='|' read -r repo number title url created_at; do
        if [ -n "$repo" ] && [ "$repo" != "null" ]; then
            # Check if already submitted
            if is_bounty_submitted "$url"; then
                log_message "Skipping already submitted bounty: $url"
                continue
            fi
            
            # Check against blacklist
            if grep -q "$repo" "$PROJECT_ROOT/config/blacklisted_projects.json"; then
                log_message "Skipping blacklisted repository: $repo"
                continue
            fi
            
            # Add to tracked bounties if not already tracked
            if [ ! -f "$CONFIG_FILE" ] || ! jq -e --arg url "$url" '.tracked_bounties[] | select(.issue_url == $url)' "$CONFIG_FILE" > /dev/null 2>&1; then
                log_message "Found new bounty: $title ($url)"
                
                # Add to tracked bounties
                if [ ! -f "$CONFIG_FILE" ]; then
                    echo '{"tracked_bounties": [], "submitted_bounties": []}' > "$CONFIG_FILE"
                fi
                
                jq --arg repo "$repo" --arg num "$number" --arg title "$title" --arg url "$url" --arg created "$created_at" --arg detected "$(date -Iseconds)" '
                    .tracked_bounties += [{
                        "repository": $repo,
                        "issue_number": ($num | tonumber),
                        "title": $title,
                        "issue_url": $url,
                        "created_at": $created,
                        "detected_at": $detected,
                        "status": "new",
                        "priority": "medium",
                        "estimated_reward": "unknown",
                        "difficulty": "unknown"
                    }]
                ' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
            fi
        fi
    done < /tmp/bounty_results_unique.txt
    
    # Cleanup temp files
    rm -f /tmp/bounty_search_results.txt /tmp/bounty_results_unique.txt
    
    log_message "✅ Bounty search completed"
}

# Function to generate project list report
generate_project_list() {
    local report_file="$PROJECT_ROOT/reports/project_list_$(date +%Y%m%d_%H%M).md"
    mkdir -p "$PROJECT_ROOT/reports"
    
    cat > "$report_file" << EOF
# 🧱 Stone Bounty Project List
*Generated on $(date)*

## 📊 Summary
- **Total Tracked Bounties**: $(jq '.tracked_bounties | length' "$CONFIG_FILE" 2>/dev/null || echo "0")
- **Submitted Bounties**: $(jq '.submitted_bounties | length' "$CONFIG_FILE" 2>/dev/null || echo "0")
- **New Opportunities**: $(jq '.tracked_bounties | map(select(.status == "new")) | length' "$CONFIG_FILE" 2>/dev/null || echo "0")

## 🎯 Active Bounty Opportunities

EOF
    
    # Add tracked bounties
    if [ -f "$CONFIG_FILE" ]; then
        jq -r '.tracked_bounties[] | 
            "- **[\(.repository)#\(.issue_number)](\(.issue_url))** - \(.title)\n  - Created: \(.created_at)\n  - Status: \(.status)\n  - Priority: \(.priority)\n"' "$CONFIG_FILE" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

## ✅ Submitted Bounties

EOF
    
    # Add submitted bounties
    if [ -f "$CONFIG_FILE" ]; then
        jq -r '.submitted_bounties[] | 
            "- **[\(.issue_url)](\(.pr_url))** - Submitted on \(.submission_date)\n  - Status: \(.status)\n"' "$CONFIG_FILE" >> "$report_file"
    fi
    
    log_message "Generated project list report: $report_file"
}

# Main execution
main() {
    log_message "🚀 Starting Stone Bounty Tracker..."
    
    # Validate configuration
    if [ ! -f "$PROJECT_ROOT/.github_token" ]; then
        log_message "❌ Error: GitHub token not found. Please create .github_token file."
        exit 1
    fi
    
    if [ ! -f "$PROJECT_ROOT/config/automation_config.json" ]; then
        log_message "❌ Error: Automation config not found. Run setup.sh first."
        exit 1
    fi
    
    # Check if emergency stop is active
    if jq -e '.emergency_stop_active // false' "$PROJECT_ROOT/config/automation_config.json" > /dev/null 2>&1; then
        log_message "⚠️ Emergency stop active - Running in monitor-only mode"
    fi
    
    # Search for bounties
    search_bounty_issues
    
    # Generate project list
    generate_project_list
    
    log_message "🏁 Bounty tracker completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --mark-submitted)
        if [ $# -eq 3 ]; then
            mark_bounty_submitted "$2" "$3"
        else
            echo "Usage: $0 --mark-submitted <issue_url> <pr_url>"
            exit 1
        fi
        ;;
    --generate-report)
        generate_project_list
        ;;
    *)
        main
        ;;
esac