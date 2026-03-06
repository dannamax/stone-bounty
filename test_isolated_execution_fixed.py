#!/usr/bin/env python3
"""
独立会话执行测试脚本（修复版）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs2_orchestrator_enhanced_fixed import BS2OrchestratorEnhanced

def test_isolated_execution():
    """测试独立会话执行功能"""
    print("🧪 开始独立会话执行测试...")
    
    # 初始化增强协调器
    orchestrator = BS2OrchestratorEnhanced()
    
    # 创建测试里程碑
    milestone = {
        "name": "M1: 测试需求分析和环境准备",
        "description": "分析测试需求，准备测试环境",
        "input": "赏金 #555 的详细要求",
        "output": "测试需求清单和环境配置",
        "acceptance_criteria": "所有测试需求已明确记录，测试环境可正常运行"
    }
    
    print("🚀 执行里程碑在独立会话中...")
    
    # 使用 sessions_spawn 直接测试
    from openclaw.tools.sessions import sessions_spawn
    
    milestone_task = f"""
执行赏金 #555 的里程碑: {milestone['name']}

里程碑详情:
- 输入: {milestone.get('input', 'N/A')}
- 输出: {milestone.get('output', 'N/A')}
- 验收标准: {milestone.get('acceptance_criteria', 'N/A')}

执行要求:
1. 使用 Superpowers TDD 工作流
2. 记录进度到 plansuite_plans/progress_555.md  
3. 记录发现到 plansuite_plans/findings_555.md
4. 完成后进行验证检查
    """
    
    try:
        result = sessions_spawn(
            task=milestone_task,
            label=f"bounty-555-milestone-1",
            thinking="on"
        )
        print(f"✅ 独立会话执行已启动: {result}")
        print("🎉 独立会话执行功能测试通过!")
        return True
    except Exception as e:
        print(f"❌ 独立会话执行失败: {e}")
        return False

if __name__ == "__main__":
    success = test_isolated_execution()
    sys.exit(0 if success else 1)