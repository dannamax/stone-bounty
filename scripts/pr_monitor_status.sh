#!/bin/bash
# Stone Bounty - PR Monitor Status Report
# Displays current status of all monitored PRs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../config"
SUBMITTED_PRS="$CONFIG_DIR/submitted_prs.json"

echo "📊 Stone Bounty PR Monitoring Status"
echo "====================================="

if [[ ! -f "$SUBMITTED_PRS" ]]; then
    echo "❌ No submitted PRs found"
    exit 0
fi

# Count total PRs
TOTAL_PRS=$(jq '.prs | length' "$SUBMITTED_PRS")
echo "Total submitted PRs: $TOTAL_PRS"

if [[ $TOTAL_PRS -eq 0 ]]; then
    echo "✅ No PRs currently being monitored"
    exit 0
fi

echo ""
echo "Active PRs:"
echo "-----------"

# Display each PR with status
for ((i=0; i<$TOTAL_PRS; i++)); do
    PR_URL=$(jq -r ".prs[$i].pr_url" "$SUBMITTED_PRS")
    ISSUE_URL=$(jq -r ".prs[$i].issue_url" "$SUBMITTED_PRS")
    STATUS=$(jq -r ".prs[$i].status" "$SUBMITTED_PRS")
    LAST_CHECKED=$(jq -r ".prs[$i].last_checked // 'Never'" "$SUBMITTED_PRS")
    HAS_NEW_COMMENTS=$(jq -r ".prs[$i].has_new_comments // false" "$SUBMITTED_PRS")
    
    echo "PR #$((i+1)): $PR_URL"
    echo "  Issue: $ISSUE_URL"
    echo "  Status: $STATUS"
    echo "  Last checked: $LAST_CHECKED"
    if [[ "$HAS_NEW_COMMENTS" == "true" ]]; then
        echo "  📩 NEW COMMENTS DETECTED!"
    fi
    echo ""
done

# Show summary
PENDING_REVIEW=$(jq '[.prs[] | select(.status == "pending_review")] | length' "$SUBMITTED_PRS")
NEEDS_RESPONSE=$(jq '[.prs[] | select(.has_new_comments == true)] | length' "$SUBMITTED_PRS")

echo "Summary:"
echo "  Pending review: $PENDING_REVIEW"
echo "  Need response: $NEEDS_RESPONSE"

echo ""
echo "💡 Use './scripts/pr_analysis_reporter.sh' for detailed analysis of PRs needing response"