#!/bin/bash

# Stone Bounty PR状态监控脚本
# 每6小时检查一次关键PR的状态

set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 监控Rustchain #247
check_rustchain_pr() {
    log "Checking Rustchain PR #247 status..."
    STATUS=$(gh pr view 247 --json state --repo Scottcjn/Rustchain --jq '.state')
    
    case "$STATUS" in
        "MERGED")
            log "🎉 PR #247 MERGED! Expected bounty: 75 RTC"
            # 发送通知
            echo "Rustchain PR #247 merged! Check for 75 RTC bounty." > /tmp/pr247_success.txt
            ;;
        "CLOSED")
            log "❌ PR #247 CLOSED! Check reason for closure."
            ;;
        "OPEN")
            log "⏳ PR #247 still OPEN, waiting for review..."
            ;;
        *)
            log "⚠️  Unknown status: $STATUS"
            ;;
    esac
}

# 检查赏金到账
check_bounty_balance() {
    log "Checking bounty balance..."
    BALANCE=$(curl -sk "https://50.28.86.131/wallet/balance?miner_id=dannamax" | jq -r '.amount_rtc // "0"')
    log "Current balance: $BALANCE RTC"
    
    if (( $(echo "$BALANCE > 20.0" | bc -l) )); then
        log "🎉 New bounty detected! Balance increased from 20.0 to $BALANCE RTC"
    fi
}

# 主函数
main() {
    log "=== Stone Bounty Monitoring Run ==="
    check_rustchain_pr
    check_bounty_balance
    log "=== Monitoring Complete ==="
}

main