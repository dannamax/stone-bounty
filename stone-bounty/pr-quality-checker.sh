#!/bin/bash

# PR Quality Checker for Stone Bounty System
# Validates PRs before submission to avoid common failure patterns

set -e

REPO_PATH="$1"
PR_TITLE="$2"
ISSUE_NUMBER="$3"

echo "🔍 Running PR Quality Check..."

# Check 1: Detect submodule modifications
if git diff --name-only HEAD~1 | grep -q "\.gitmodules\|\.git/"; then
    echo "❌ ERROR: Submodule modifications detected!"
    echo "   This is not allowed in most projects."
    exit 1
fi

# Check 2: Check if changes are meaningful (not just placeholder files)
CHANGED_FILES=$(git diff --name-only HEAD~1 | wc -l)
if [ "$CHANGED_FILES" -eq 0 ]; then
    echo "❌ ERROR: No files changed in PR!"
    exit 1
fi

# Check 3: Check for actual code changes vs placeholder content
ACTUAL_CHANGES=$(git diff HEAD~1 | grep -v "^+" | grep -v "^-" | wc -l)
if [ "$ACTUAL_CHANGES" -lt 3 ]; then
    echo "⚠️  WARNING: Very minimal changes detected. Verify this is a real fix."
fi

# Check 4: Validate commit message format
COMMIT_MSG=$(git log -1 --pretty=%B)
if [[ "$COMMIT_MSG" == *"#"* ]] && [[ "$COMMIT_MSG" != *"$ISSUE_NUMBER"* ]]; then
    echo "⚠️  WARNING: Commit message contains issue references."
    echo "   Move issue references to PR description instead."
fi

# Check 5: Validate against project-specific rules
PROJECT_NAME=$(basename "$REPO_PATH")
case "$PROJECT_NAME" in
    "rust")
        echo "❌ BLOCKED: rust-lang/rust is too complex for automated fixes"
        echo "   Focus on documentation, tests, or simple bug fixes instead."
        exit 1
        ;;
    "vue")
        # Vue.js specific checks
        if ! git diff HEAD~1 | grep -q "test\|spec"; then
            echo "⚠️  RECOMMENDATION: Add unit tests for Vue.js fixes"
        fi
        ;;
    "vscode")
        # VS Code specific checks
        if ! git diff HEAD~1 | grep -q "package.json\|tsconfig.json"; then
            echo "⚠️  INFO: VS Code PRs should include proper manifest updates if needed"
        fi
        ;;
esac

echo "✅ PR Quality Check Passed!"
exit 0