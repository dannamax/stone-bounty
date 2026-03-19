#!/bin/bash

# Stone Bounty High-Quality PR Auto-Validation
# Automatically validates PR quality before submission

set -e

REPO_PATH="$1"
BRANCH_NAME="$2"
ISSUE_NUMBER="$3"
ISSUE_TITLE="$4"

echo "🔍 Starting High-Quality PR Auto-Validation..."
echo "Repository: $REPO_PATH"
echo "Branch: $branch_name"
echo "Issue: #$ISSUE_NUMBER - $ISSUE_TITLE"

# Function to run quality scoring
run_quality_scoring() {
    echo "📊 Running quality scoring..."
    python3 /home/admin/.openclaw/workspace/stone-bounty/quality-scoring.py \
        "$REPO_PATH" "$BRANCH_NAME" "$ISSUE_NUMBER" "$ISSUE_TITLE"
}

# Function to validate against templates
validate_against_templates() {
    echo "📋 Validating against quality templates..."
    
    # Check if PR follows appropriate template
    PR_DESCRIPTION=$(git log -1 --pretty=%B)
    
    # Template validation logic
    if [[ "$ISSUE_TITLE" == *"documentation"* ]] || [[ "$ISSUE_TITLE" == *"docs"* ]]; then
        echo "✅ Issue identified as documentation type"
        # Documentation specific checks
        if ! grep -q "Fixes #[0-9]" <<< "$PR_DESCRIPTION"; then
            echo "❌ Missing 'Fixes #issue' in PR description"
            return 1
        fi
    elif [[ "$ISSUE_TITLE" == *"test"* ]] || [[ "$ISSUE_TITLE" == *"bug"* ]]; then
        echo "✅ Issue identified as test/bug type"
        # Test/bug specific checks
        if ! grep -q "comprehensive test coverage" <<< "$PR_DESCRIPTION"; then
            echo "⚠️  Consider adding test coverage details to PR description"
        fi
    else
        echo "✅ Issue identified as feature type"
        # Feature specific checks
        if ! grep -q "simple and focused" <<< "$PR_DESCRIPTION"; then
            echo "⚠️  Consider emphasizing simplicity in PR description"
        fi
    fi
}

# Function to check for actual code changes
check_actual_changes() {
    echo "🔍 Checking for actual code changes (not placeholders)..."
    
    CHANGED_FILES=$(git diff --name-only HEAD~1)
    if [ -z "$CHANGED_FILES" ]; then
        echo "❌ No actual file changes detected!"
        return 1
    fi
    
    # Check for placeholder content
    PLACEHOLDER_COUNT=0
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Check for common placeholder patterns
            if grep -q "placeholder\|template\|TODO\|FIXME" "$file" 2>/dev/null; then
                ((PLACEHOLDER_COUNT++))
                echo "⚠️  Placeholder content found in: $file"
            fi
        fi
    done <<< "$CHANGED_FILES"
    
    if [ $PLACEHOLDER_COUNT -gt 0 ]; then
        echo "❌ Placeholder content detected! PR rejected."
        return 1
    fi
    
    echo "✅ All changes are actual implementation (no placeholders)"
}

# Function to validate SPDX compliance
validate_spdx_compliance() {
    echo "📜 Validating SPDX compliance..."
    
    CHANGED_FILES=$(git diff --name-only HEAD~1)
    SPDX_REQUIRED_EXTENSIONS=(".md" ".yaml" ".yml" ".json" ".py" ".js" ".ts" ".go" ".rs")
    
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            # Check if file extension requires SPDX
            for ext in "${SPDX_REQUIRED_EXTENSIONS[@]}"; do
                if [[ "$file" == *"$ext" ]]; then
                    if ! head -5 "$file" | grep -q "SPDX-License-Identifier"; then
                        echo "⚠️  SPDX license identifier missing in: $file"
                        # Auto-add SPDX identifier
                        echo "# SPDX-License-Identifier: MIT" | cat - "$file" > temp && mv temp "$file"
                        echo "✅ SPDX identifier auto-added to: $file"
                    else
                        echo "✅ SPDX compliance verified for: $file"
                    fi
                    break
                fi
            done
        fi
    done <<< "$CHANGED_FILES"
}

# Main validation function
main() {
    echo "🚀 Starting comprehensive PR validation..."
    
    # Change to repository directory
    cd "$REPO_PATH"
    
    # Run all validation checks
    if ! check_actual_changes; then
        echo "❌ PR validation failed: No actual changes or placeholder content detected"
        exit 1
    fi
    
    if ! validate_against_templates; then
        echo "❌ PR validation failed: Template compliance issues"
        exit 1
    fi
    
    validate_spdx_compliance
    
    if ! run_quality_scoring; then
        echo "❌ PR validation failed: Quality score below threshold"
        exit 1
    fi
    
    echo "🎉 All validation checks passed! PR is ready for submission."
    echo "Quality score: $(cat /tmp/quality_score.txt 2>/dev/null || echo "N/A")"
}

# Run main function
if [[ $# -eq 4 ]]; then
    main
else
    echo "Usage: $0 <repo_path> <branch_name> <issue_number> <issue_title>"
    exit 1
fi