#!/bin/bash
# 监控 PlanSuite 计划执行状态

PLAN_DIR="/home/admin/.openclaw/workspace/stone-bs2.0/plansuite_plans"

echo "📊 PlanSuite 计划状态监控"
echo "========================="

# 列出所有计划文件
echo "📋 计划文件状态:"
for plan_file in $PLAN_DIR/task_plan_*.md; do
    if [ -f "$plan_file" ]; then
        bounty_id=$(basename "$plan_file" | sed 's/task_plan_\(.*\)\.md/\1/')
        status_line=$(head -1 "$plan_file")
        if [[ "$status_line" == *"STATUS: FINALIZED"* ]]; then
            status="✅ FINALIZED"
        else
            status="🔄 DRAFT"
        fi
        echo "PR #$bounty_id: $status"
    fi
done

echo ""
echo "📈 进度文件状态:"
for progress_file in $PLAN_DIR/progress_*.md; do
    if [ -f "$progress_file" ]; then
        bounty_id=$(basename "$progress_file" | sed 's/progress_\(.*\)\.md/\1/')
        current_phase=$(grep "当前阶段" "$progress_file" | cut -d: -f2 | xargs)
        current_milestone=$(grep "当前子计划" "$progress_file" | cut -d: -f2 | xargs)
        echo "PR #$bounty_id: $current_phase - $current_milestone"
    fi
done

echo ""
echo "🔍 最近检查点:"
for progress_file in $PLAN_DIR/progress_*.md; do
    if [ -f "$progress_file" ]; then
        bounty_id=$(basename "$progress_file" | sed 's/progress_\(.*\)\.md/\1/')
        last_checkpoint=$(grep "最近一次检查点" -A 3 "$progress_file" | tail -3)
        echo "PR #$bounty_id 检查点:"
        echo "$last_checkpoint"
        echo ""
    fi
done