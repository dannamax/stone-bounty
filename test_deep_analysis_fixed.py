#!/usr/bin/env python3
"""
深度分析测试脚本 - 修复版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deep_analysis_workflow import DeepAnalysisWorkflow

def test_deep_analysis():
    """测试深度分析功能"""
    print("🔍 开始深度分析...")
    
    # 创建测试 bounty
    test_bounty = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "description": "Add social graph API endpoints to BoTTube:\n- GET /api/social/graph — network visualization data (follower/following pairs, top connections)\n- GET /api/agents/<name>/interactions — per-agent incoming/outgoing followers\n\nRequirements:\n- SQL JOINs on existing subscriptions table\n- Limit parameter with bounds checking\n- Flask test_client() integration tests (NOT mock-based)\n- Follow pattern in tests/test_tipping.py",
        "type": "test",
        "complexity": "MODERATE",
        "reward": "5 RTC"
    }
    
    # 初始化深度分析工作流
    workflow = DeepAnalysisWorkflow()
    
    try:
        # 执行完整的深度分析
        analysis_result = workflow.perform_deep_analysis(test_bounty)
        
        print("✅ 深度分析完成!")
        print(f"分析结果: {analysis_result}")
        
        # 验证关键组件
        if "requirements_understanding" in analysis_result:
            print("✅ 需求理解分析完成")
        if "codebase_analysis" in analysis_result:
            print("✅ 代码库分析完成")
        if "test_strategy" in analysis_result:
            print("✅ 测试策略分析完成")
        if "implementation_plan" in analysis_result:
            print("✅ 实现计划分析完成")
            
        return True
        
    except Exception as e:
        print(f"❌ 深度分析失败: {e}")
        return False

if __name__ == "__main__":
    success = test_deep_analysis()
    if success:
        print("\n🎉 深度分析测试通过!")
    else:
        print("\n❌ 深度分析测试失败!")
        sys.exit(1)