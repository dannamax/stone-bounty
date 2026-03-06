#!/usr/bin/env python3
"""
PlanSuite 集成测试脚本
"""

import sys
import os
import json
from pathlib import Path

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plansuite_planner import PlanSuitePlanner
from bs2_orchestrator_enhanced import BS2OrchestratorEnhanced

def create_test_bounty():
    """创建测试 bounty 数据"""
    return {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "type": "test",
        "complexity": "MODERATE", 
        "reward": "5 RTC",
        "description": "Add social graph API endpoints to BoTTube with Flask integration tests",
        "url": "https://github.com/Scottcjn/rustchain-bounties/issues/555"
    }

def test_plansuite_integration():
    """测试 PlanSuite 集成"""
    print("🧪 开始 PlanSuite 集成测试...")
    
    # 初始化增强协调器
    orchestrator = BS2OrchestratorEnhanced()
    
    # 创建测试 bounty
    test_bounty = create_test_bounty()
    
    # 测试计划创建
    print("📋 测试 PlanSuite 计划创建...")
    try:
        plan_result = orchestrator.create_enhanced_bounty_workflow(test_bounty)
        print(f"✅ 计划创建成功:\n{plan_result[:200]}...")
    except Exception as e:
        print(f"❌ 计划创建失败: {e}")
        return False
    
    # 验证文件生成
    plan_file = Path("plansuite_plans/task_plan_555.md")
    progress_file = Path("plansuite_plans/progress_555.md") 
    findings_file = Path("plansuite_plans/findings_555.md")
    
    if not plan_file.exists():
        print(f"❌ 计划文件 {plan_file} 未生成")
        return False
    print(f"✅ 计划文件 {plan_file} 已生成")
    
    if not progress_file.exists():
        print(f"❌ 进度文件 {progress_file} 未生成")
        return False
    print(f"✅ 进度文件 {progress_file} 已生成")
    
    if not findings_file.exists():
        print(f"❌ 发现文件 {findings_file} 未生成")
        return False
    print(f"✅ 发现文件 {findings_file} 已生成")
    
    # 验证计划内容
    plan_content = plan_file.read_text()
    if "STATUS: DRAFT" not in plan_content:
        print("❌ 计划文件缺少 STATUS: DRAFT 标记")
        return False
    
    if "M1:" not in plan_content or "M2:" not in plan_content:
        print("❌ 计划文件缺少里程碑分解")
        return False
    
    print("✅ 计划内容验证通过")
    
    # 测试计划冻结
    print("🔒 测试计划冻结机制...")
    try:
        # 模拟用户确认
        frozen_plan_content = plan_content.replace("STATUS: DRAFT", "STATUS: FINALIZED (2026-03-06 17:58:00)")
        plan_file.write_text(frozen_plan_content)
        
        # 测试执行冻结计划
        execute_result = orchestrator.execute_frozen_plan("555")
        print(f"✅ 计划冻结和执行测试通过:\n{execute_result[:100]}...")
    except Exception as e:
        print(f"❌ 计划冻结测试失败: {e}")
        return False
    
    print("🎉 PlanSuite 集成测试全部通过！")
    return True

if __name__ == "__main__":
    success = test_plansuite_integration()
    sys.exit(0 if success else 1)