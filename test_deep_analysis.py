#!/usr/bin/env python3
"""
深度分析功能测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deep_analysis_workflow import DeepAnalysisWorkflow

def test_deep_analysis():
    """测试深度分析功能"""
    
    # 创建测试 bounty
    test_bounty = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "description": "Add social graph API endpoints to BoTTube:\n- GET /api/social/graph — network visualization data\n- GET /api/agents/<name>/interactions — per-agent incoming/outgoing followers\n\nRequirements:\n- SQL JOINs on existing subscriptions table\n- Limit parameter with bounds checking\n- Flask test_client() integration tests (NOT mock-based)\n- Follow pattern in tests/test_tipping.py",
        "type": "test",
        "complexity": "MODERATE"
    }
    
    # 初始化深度分析工作流
    workflow = DeepAnalysisWorkflow()
    
    print("🔍 开始深度分析...")
    
    # 1. 需求理解分析
    print("1️⃣ 需求理解分析...")
    requirements_analysis = workflow.analyze_requirements(test_bounty)
    print(f"✅ 需求分析完成: {len(requirements_analysis)} 个关键点")
    
    # 2. 代码库分析
    print("2️⃣ 代码库分析...")
    codebase_analysis = workflow.analyze_codebase(test_bounty)
    print(f"✅ 代码库分析完成: {len(codebase_analysis)} 个文件分析")
    
    # 3. 测试策略分析
    print("3️⃣ 测试策略分析...")
    test_strategy = workflow.analyze_test_strategy(test_bounty)
    print(f"✅ 测试策略分析完成: {len(test_strategy)} 个测试用例")
    
    # 4. 边界情况分析
    print("4️⃣ 边界情况分析...")
    edge_cases = workflow.analyze_edge_cases(test_bounty)
    print(f"✅ 边界情况分析完成: {len(edge_cases)} 个边界情况")
    
    # 5. 生成深度分析报告
    print("5️⃣ 生成深度分析报告...")
    analysis_report = workflow.generate_analysis_report(
        test_bounty, requirements_analysis, codebase_analysis, 
        test_strategy, edge_cases
    )
    
    # 保存报告
    report_file = "deep_analysis_report_555.md"
    with open(report_file, 'w') as f:
        f.write(analysis_report)
    
    print(f"✅ 深度分析报告已生成: {report_file}")
    
    return True

if __name__ == "__main__":
    success = test_deep_analysis()
    if success:
        print("\n🎉 深度分析功能测试通过!")
    else:
        print("\n❌ 深度分析功能测试失败!")
        sys.exit(1)