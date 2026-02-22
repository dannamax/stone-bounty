#!/bin/bash
# Stone Bounty - Disk Space Monitor
# Monitors /dev/vdb usage and alerts if approaching 90% limit

set -euo pipefail

DISK_PATH="/dev/vdb"
MOUNT_POINT="/mnt/vdb"
MAX_USAGE_PERCENT=90
WARNING_THRESHOLD=85

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_disk_usage() {
    log_message "🔍 Checking disk space usage for $DISK_PATH..."
    
    # Get current usage percentage
    USAGE_PERCENT=$(df "$DISK_PATH" | awk 'NR==2 {print $5}' | sed 's/%//')
    AVAIL_SPACE=$(df -h "$DISK_PATH" | awk 'NR==2 {print $4}')
    TOTAL_SPACE=$(df -h "$DISK_PATH" | awk 'NR==2 {print $2}')
    
    log_message "📊 Current usage: ${USAGE_PERCENT}% (${AVAIL_SPACE} available of ${TOTAL_SPACE})"
    
    if [ "$USAGE_PERCENT" -ge "$MAX_USAGE_PERCENT" ]; then
        log_message "${RED}❌ CRITICAL: Disk usage (${USAGE_PERCENT}%) exceeds ${MAX_USAGE_PERCENT}% limit!${NC}"
        log_message "${RED}Stopping all operations to prevent system issues.${NC}"
        exit 1
    elif [ "$USAGE_PERCENT" -ge "$WARNING_THRESHOLD" ]; then
        log_message "${YELLOW}⚠️  WARNING: Disk usage (${USAGE_PERCENT}%) approaching ${MAX_USAGE_PERCENT}% limit${NC}"
        log_message "${YELLOW}Available space: ${AVAIL_SPACE} - consider cleaning up test files${NC}"
        return 1
    else
        log_message "${GREEN}✅ Disk space OK: ${USAGE_PERCENT}% used${NC}"
        return 0
    fi
}

# Function to clean up test files if needed
cleanup_test_files() {
    local test_dirs=(
        "/mnt/vdb/stone-bounty/test_*"
        "/mnt/vdb/stone-bounty/logs/test_*"
        "/tmp/test_*"
        "~/.beacon/test_*"
    )
    
    log_message "🧹 Cleaning up test files to free space..."
    
    for dir in "${test_dirs[@]}"; do
        if [ -d "$dir" ]; then
            SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1)
            log_message "Removing $dir ($SIZE)"
            rm -rf "$dir"
        fi
    done
    
    log_message "✅ Test file cleanup completed"
}

# Main execution
log_message "🚀 Starting disk space monitoring..."

# Check current usage
if ! check_disk_usage; then
    log_message "💡 Suggesting cleanup to free space..."
    read -p "Would you like to clean up test files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup_test_files
        # Re-check after cleanup
        check_disk_usage
    fi
fi

log_message "✅ Disk space monitoring completed successfully"