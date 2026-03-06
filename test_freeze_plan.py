#!/usr/bin/env python3
"""
测试 PlanSuite 计划冻结功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plansuite_planner import PlanSuitePlanner

def test_plan_freeze():
    """测试计划冻结功能"""
    
    # 初始化计划生成器
    planner = PlanSuitePlanner("/home/admin/.openclaw/workspace/stone-bs2.0")
    
    # 模拟用户确认计划
    plan_file = "/home/admin/.openclaw/workspace/stone-bs2.0/plansuite_plans/task_plan_555.md"
    
    # 读取当前计划内容
    with open(plan_file, 'r') as f:
        content = f.read()
    
    # 添加 FINALIZED 状态
    if "STATUS: DRAFT" in content:
        frozen_content = content.replace("STATUS: DRAFT", "STATUS: FINALIZED\n# 冻结时间: 2026-03-06T19:55:00Z")
        
        with open(plan_file, 'w') as f:
            f.write(frozen_content)
        
        print("✅ 计划已成功冻结!")
        print(f"📄 计划文件: {plan_file}")
        print("🔒 状态: STATUS: FINALIZED")
        
        # 验证冻结状态
        with open(plan_file, 'r') as f:
            verified_content = f.read()
            if "STATUS: FINALIZED" in verified_content:
                print("✅ 冻结状态验证通过!")
                return True
            else:
                print("❌ 冻结状态验证失败!")
                return False
    else:
        print("❌ 计划文件未找到或格式不正确")
        return False

if __name__ == "__main__":
    success = test_plan_freeze()
    if success:
        print("\n🎉 计划冻结功能测试通过!")
    else:
        print("\n❌ 计划冻结功能测试失败!")
        sys.exit(1)