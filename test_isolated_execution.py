#!/usr/bin/env python3
"""
测试 PlanSuite 独立会话执行功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs2_orchestrator_enhanced_fixed import BS2OrchestratorEnhanced

def test_isolated_execution():
    """测试独立会话执行"""
    print("🧪 开始独立会话执行测试...")
    
    # 创建测试里程碑
    milestone = {
        "name": "M1: 测试需求分析和环境准备",
        "id": "M1",
        "input": "赏金 #555 的详细要求",
        "output": "测试需求清单和环境配置",
        "acceptance_criteria": "所有测试需求已明确记录，测试环境可正常运行",
        "risks": "测试环境配置复杂，依赖服务不可用"
    }
    
    # 初始化增强协调器
    orchestrator = BS2OrchestratorEnhanced()
    
    # 执行里程碑
    print("🚀 执行里程碑在独立会话中...")
    result = orchestrator.execute_milestone_in_isolated_session(milestone, "555")
    
    print(f"✅ 独立会话执行结果:\n{result}")
    print("🎉 独立会话执行测试完成!")

if __name__ == "__main__":
    test_isolated_execution()