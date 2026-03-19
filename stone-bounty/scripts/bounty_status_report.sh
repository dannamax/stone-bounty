#!/bin/bash
# Stone Bounty - Status Report Script
# Generates a report of current bounty opportunities and submission status

set -e

PROJECT_LIST="config/project_list.json"
TRACKER_FILE="config/bounty_tracker.json"

echo "🧱 Stone Bounty Status Report"
echo "================================"
echo "📅 $(date)"
echo ""

# Check if files exist
if [ ! -f "$PROJECT_LIST" ]; then
    echo "❌ Project list not found. Run hourly check first."
    exit 1
fi

if [ ! -f "$TRACKER_FILE" ]; then
    echo "❌ Tracker file not found. Run hourly check first."
    exit 1
fi

# Get total projects
total_projects=$(jq '.projects | length' "$PROJECT_LIST")
echo "📊 Total tracked projects: $total_projects"

# Get submitted projects
submitted_count=$(jq '[.projects[] | select(.submitted == true)] | length' "$PROJECT_LIST")
echo "✅ Submitted projects: $submitted_count"

# Get available opportunities
available_count=$(jq '[.projects[] | select(.submitted == false)] | length' "$PROJECT_LIST")
echo "🔍 Available opportunities: $available_count"
echo ""

# Show recent bounties
echo "🎯 Recent Bounty Opportunities:"
echo "-------------------------------"
jq -r '.projects[] | select(.submitted == false) | "\(.repo)/\(.issue_number): \(.title) - \(.reward)"' "$PROJECT_LIST" | head -10

echo ""
echo "📈 Submission History:"
echo "---------------------"
jq -r '.projects[] | select(.submitted == true) | "\(.repo)/\(.issue_number): \(.title) - Submitted: \(.submitted_at)"' "$PROJECT_LIST" | tail -5

echo ""
echo "💡 Next Steps:"
echo "- Review available opportunities above"
echo "- Use ./scripts/pr_submitter.sh to submit PRs"
echo "- Run ./scripts/hourly_bounty_check.sh manually for updates"