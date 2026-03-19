#!/bin/bash
# Stone Bounty - 自动赏金监控脚本
# 每小时运行一次，检测新的赏金任务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$WORKSPACE_DIR/logs/bounty_monitor.log"
PROJECT_LIST="$WORKSPACE_DIR/config/project_list.json"

# 创建日志目录
mkdir -p "$WORKSPACE_DIR/logs"

# 记录开始时间
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始自动赏金监控..." >> "$LOG_FILE"

# 运行赏金跟踪器
"$SCRIPT_DIR/bounty_tracker.sh" --auto-mode >> "$LOG_FILE" 2>&1

# 检查是否有新任务
NEW_TASKS=$(jq '.projects[] | select(.status == "new")' "$PROJECT_LIST" | wc -l)
if [ "$NEW_TASKS" -gt 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 发现 $NEW_TASKS 个新赏金任务!" >> "$LOG_FILE"
    
    # 可选：发送通知（需要配置通知方式）
    # echo "发现新赏金任务，请检查 project_list.json" | mail -s "新赏金任务" your-email@example.com
    
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 未发现新赏金任务" >> "$LOG_FILE"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - 自动赏金监控完成" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"