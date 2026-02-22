#!/bin/bash
# Stone Bounty - Hourly Bounty Check Script
# Automatically monitors for new bounty opportunities and updates project list

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

# Function to update project list with new bounties
update_project_list() {
    log_message "🔍 Searching for new bounty opportunities..."
    
    # Get current timestamp
    CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Temporary file for new results
    TEMP_RESULTS="$PROJECT_ROOT/temp_bounty_results.json"
    
    # Search for bounty issues using GitHub API
    GITHUB_TOKEN=$(cat "$PROJECT_ROOT/.github_token")
    
    # Search queries for different bounty types
    SEARCH_QUERIES=(
        "bounty+label:bounty+state:open+sort:created-desc"
        "reward+label:reward+state:open+sort:created-desc" 
        "label:hacktoberfest+state:open+sort:created-desc"
        "label:good-first-issue+state:open+sort:created-desc"
    )
    
    # Initialize empty array for all results
    echo "[]" > "$TEMP_RESULTS"
    
    # Search each query
    for query in "${SEARCH_QUERIES[@]}"; do
        log_message "🔍 Searching GitHub for: $query"
        
        # Get search results (max 30 per query to avoid rate limits)
        RESULTS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/search/issues?q=$query&per_page=30" | jq '.items')
        
        if [ "$RESULTS" != "null" ] && [ "$RESULTS" != "[]" ]; then
            # Merge results into temp file
            jq --argjson new_results "$RESULTS" \
               --argjson existing_results "$(cat "$TEMP_RESULTS")" \
               -n '$existing_results + $new_results | unique_by(.html_url)' > "$TEMP_RESULTS.tmp"
            mv "$TEMP_RESULTS.tmp" "$TEMP_RESULTS"
        fi
    done
    
    # Load current project list
    PROJECT_LIST="$CONFIG_DIR/project_list.json"
    if [ ! -f "$PROJECT_LIST" ]; then
        cp "$CONFIG_DIR/project_list_template.json" "$PROJECT_LIST"
    fi
    
    # Update project list with new findings
    python3 << EOF
import json
import sys
from datetime import datetime

# Load current project list
with open('$PROJECT_LIST', 'r') as f:
    project_list = json.load(f)

# Load new bounty results  
with open('$TEMP_RESULTS', 'r') as f:
    new_bounties = json.load(f)

# Get existing URLs to avoid duplicates
existing_urls = {item['url'] for item in project_list.get('projects', [])}

# Add new bounties
new_projects_added = 0
for bounty in new_bounties:
    if bounty['html_url'] not in existing_urls:
        project_list['projects'].append({
            'name': bounty['title'],
            'url': bounty['html_url'],
            'repository': bounty['repository_url'].replace('https://api.github.com/repos/', ''),
            'created_at': bounty['created_at'],
            'labels': [label['name'] for label in bounty['labels']],
            'status': 'pending',
            'submitted': False,
            'submission_date': None,
            'reward_info': '',
            'difficulty': 'unknown'
        })
        new_projects_added += 1
        existing_urls.add(bounty['html_url'])

# Update last checked timestamp
project_list['metadata']['last_checked'] = '$CURRENT_TIME'
project_list['metadata']['total_projects'] = len(project_list['projects'])

# Save updated project list
with open('$PROJECT_LIST', 'w') as f:
    json.dump(project_list, f, indent=2)

print(f"Added {new_projects_added} new bounty opportunities")
EOF
    
    # Clean up temp file
    rm -f "$TEMP_RESULTS"
    
    log_message "✅ Project list updated successfully"
}

# Function to filter relevant projects based on blacklist
filter_relevant_projects() {
    log_message "🛡️ Filtering projects against blacklist..."
    
    python3 << EOF
import json

# Load project list
with open('$CONFIG_DIR/project_list.json', 'r') as f:
    project_list = json.load(f)

# Load blacklist
with open('$CONFIG_DIR/blacklisted_projects.json', 'r') as f:
    blacklist_config = json.load(f)
    blacklisted_repos = set(blacklist_config.get('blacklisted_repositories', []))

# Filter out blacklisted projects
filtered_projects = []
for project in project_list.get('projects', []):
    repo_name = project.get('repository', '')
    if repo_name not in blacklisted_repos and not project.get('submitted', False):
        filtered_projects.append(project)

project_list['projects'] = filtered_projects
project_list['metadata']['filtered_count'] = len(filtered_projects)

# Save filtered list
with open('$CONFIG_DIR/project_list.json', 'w') as f:
    json.dump(project_list, f, indent=2)

print(f"Filtered to {len(filtered_projects)} relevant projects")
EOF
    
    log_message "✅ Projects filtered successfully"
}

# Main execution
log_message "🚀 Starting hourly bounty monitoring..."

# Check prerequisites
check_github_token

# Update project list with new bounties
update_project_list

# Filter relevant projects
filter_relevant_projects

# Display summary
TOTAL_PROJECTS=$(jq -r '.metadata.total_projects // 0' "$CONFIG_DIR/project_list.json")
FILTERED_COUNT=$(jq -r '.metadata.filtered_count // 0' "$CONFIG_DIR/project_list.json")

log_message "📊 Monitoring Summary:"
log_message "   Total projects tracked: $TOTAL_PROJECTS"
log_message "   Relevant projects: $FILTERED_COUNT"
log_message "   Next check in 1 hour"

# Optional: Send notification if new high-value bounties found
NEW_HIGH_VALUE=$(jq -r '[.projects[] | select(.status == "pending" and (.reward_info | contains("10") or contains("15") or contains("20")))] | length' "$CONFIG_DIR/project_list.json")
if [ "$NEW_HIGH_VALUE" -gt 0 ]; then
    log_message "🎯 Found $NEW_HIGH_VALUE high-value bounty opportunities!"
fi

log_message "✅ Hourly bounty check completed successfully"