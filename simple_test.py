#!/usr/bin/env python3
"""
简化版 PlanSuite 集成测试
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plansuite_planner import PlanSuitePlanner

def test_plansuite_planner():
    """测试 PlanSuite 计划生成器"""
    
    print("🧪 开始 PlanSuite 计划生成器测试...")
    
    # 创建测试 bounty 数据
    test_bounty = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "type": "test",
        "complexity": "MODERATE",
        "reward": "5 RTC",
        "description": "Add social graph API endpoints to BoTTube with Flask integration tests"
    }
    
    # 创建设计分析数据（模拟 Superpowers 输出）
    design_analysis = {
        "approach": "Create Flask API endpoints for social graph data",
        "milestones": [
            {
                "name": "API Endpoint Design",
                "description": "Design the social graph API endpoints",
                "steps": ["Define GET /api/social/graph endpoint", "Define GET /api/agents/<name>/interactions endpoint"]
            },
            {
                "name": "Database Integration", 
                "description": "Integrate with existing subscriptions table",
                "steps": ["Create SQL JOIN queries", "Implement limit parameter with bounds checking"]
            },
            {
                "name": "Flask Integration Tests",
                "description": "Create Flask test_client() integration tests",
                "steps": ["Follow pattern in tests/test_tipping.py", "Test both endpoints with sample data"]
            }
        ]
    }
    
    # 初始化 PlanSuite 计划生成器
    planner = PlanSuitePlanner("/home/admin/.openclaw/workspace/stone-bs2.0")
    
    # 生成计划
    print("📋 生成 PlanSuite 计划...")
    plan_result = planner.create_milestone_plan(test_bounty, design_analysis)
    print(f"✅ 计划生成结果: {plan_result}")
    
    # 验证文件生成
    plan_file = Path("plansuite_plans/task_plan_555.md")
    progress_file = Path("plansuite_plans/progress_555.md") 
    findings_file = Path("plansuite_plans/findings_555.md")
    
    if plan_file.exists():
        print(f"✅ 计划文件 {plan_file} 已生成")
        # 显示计划文件内容预览
        content = plan_file.read_text()
        print(f"📄 计划文件预览 (前200字符):\n{content[:200]}...")
    else:
        print(f"❌ 计划文件 {plan_file} 未生成")
        return False
        
    if progress_file.exists():
        print(f"✅ 进度文件 {progress_file} 已生成")
    else:
        print(f"❌ 进度文件 {progress_file} 未生成")
        return False
        
    if findings_file.exists():
        print(f"✅ 发现文件 {findings_file} 已生成")
    else:
        print(f"❌ 发现文件 {findings_file} 未生成")
        return False
    
    print("🎉 PlanSuite 计划生成器测试通过！")
    return True

if __name__ == "__main__":
    success = test_plansuite_planner()
    sys.exit(0 if success else 1)