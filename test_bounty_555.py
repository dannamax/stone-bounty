#!/usr/bin/env python3
"""
完整赏金 #555 任务测试
"""

import json
from pathlib import Path

def create_bounty_555_plan():
    """创建赏金 #555 的完整 PlanSuite 计划"""
    
    bounty_data = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "description": "Add social graph API endpoints to BoTTube:\n- GET /api/social/graph — network visualization data (follower/following pairs, top connections)\n- GET /api/agents/<name>/interactions — per-agent incoming/outgoing followers\n\nRequirements:\n- SQL JOINs on existing subscriptions table\n- Limit parameter with bounds checking\n- Flask test_client() integration tests (NOT mock-based)\n- Follow pattern in tests/test_tipping.py",
        "reward": "5 RTC",
        "complexity": "LOW",
        "type": "test"
    }
    
    # 使用 PlanSuite 计划生成器
    from plansuite_planner import PlanSuitePlanner
    
    planner = PlanSuitePlanner("/home/admin/.openclaw/workspace/stone-bs2.0")
    
    # 模拟 Superpowers 设计分析结果
    design_analysis = {
        "approach": "Flask integration tests with real database",
        "requirements": [
            "SQL JOINs on subscriptions table",
            "Limit parameter validation", 
            "Flask test_client integration",
            "Follow existing test patterns"
        ],
        "technical_details": {
            "endpoints": ["/api/social/graph", "/api/agents/{name}/interactions"],
            "database": "existing subscriptions table",
            "testing": "Flask test_client with real DB"
        }
    }
    
    result = planner.create_milestone_plan(bounty_data, design_analysis)
    print(f"✅ 赏金 #555 PlanSuite 计划创建完成: {result}")
    
    return result

if __name__ == "__main__":
    create_bounty_555_plan()