#!/usr/bin/env python3
"""
PlanSuite 计划生成器 - 为 BS2.0 系统提供里程碑管理能力
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Milestone:
    """里程碑数据结构"""
    id: str
    name: str
    description: str
    input_requirements: List[str]
    output_deliverables: List[str]
    acceptance_criteria: List[str]
    planned_steps: List[str]
    risks: List[str]
    rollback_points: List[str]

class PlanSuitePlanner:
    """PlanSuite 计划生成器"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.plan_dir = self.workspace_dir / "plansuite_plans"
        self.plan_dir.mkdir(exist_ok=True)
    
    def create_milestone_plan(self, bounty: Dict, design_analysis: Dict) -> str:
        """基于 Superpowers 设计分析创建里程碑计划"""
        try:
            # 1. 解析设计分析结果
            milestones = self._extract_milestones_from_design(bounty, design_analysis)
            
            # 2. 生成 task_plan.md
            plan_content = self._generate_task_plan(bounty, milestones)
            plan_file = self.plan_dir / f"task_plan_{bounty['id']}.md"
            plan_file.write_text(plan_content)
            
            # 3. 初始化 progress.md 和 findings.md
            self._init_progress_and_findings(bounty['id'])
            
            return f"PlanSuite 计划已创建: {plan_file}"
            
        except Exception as e:
            return f"❌ PlanSuite 计划创建失败: {str(e)}"
    
    def _extract_milestones_from_design(self, bounty: Dict, design_analysis: Dict) -> List[Milestone]:
        """从 Superpowers 设计分析中提取里程碑"""
        milestones = []
        
        # 根据赏金类型和复杂度自动生成里程碑
        if bounty['type'] == 'test' and bounty['complexity'] == 'MODERATE':
            # 测试类任务的里程碑
            milestones = [
                Milestone(
                    id="M1",
                    name="测试需求分析和环境准备",
                    description="分析测试需求，准备测试环境",
                    input_requirements=[
                        f"赏金 #{bounty['id']} 的详细要求",
                        "现有代码库访问权限",
                        "测试框架文档"
                    ],
                    output_deliverables=[
                        "测试需求清单",
                        "测试环境配置",
                        "测试数据准备"
                    ],
                    acceptance_criteria=[
                        "所有测试需求已明确记录",
                        "测试环境可正常运行",
                        "测试数据符合要求"
                    ],
                    planned_steps=[
                        "分析赏金要求和现有代码",
                        "确定测试覆盖范围",
                        "配置本地测试环境",
                        "准备测试数据和用例"
                    ],
                    risks=[
                        "测试环境配置复杂",
                        "依赖服务不可用",
                        "测试数据不足"
                    ],
                    rollback_points=[
                        "回退到原始代码状态",
                        "清理测试环境",
                        "恢复原始配置"
                    ]
                ),
                Milestone(
                    id="M2", 
                    name="测试实现和集成",
                    description="实现测试代码并集成到项目中",
                    input_requirements=[
                        "测试需求清单",
                        "测试环境",
                        "被测代码访问权限"
                    ],
                    output_deliverables=[
                        "完整的测试代码",
                        "测试配置文件",
                        "集成说明文档"
                    ],
                    acceptance_criteria=[
                        "测试代码通过所有验证",
                        "符合项目编码规范",
                        "集成后不影响现有功能"
                    ],
                    planned_steps=[
                        "编写测试用例",
                        "实现测试逻辑",
                        "集成到项目测试套件",
                        "验证测试执行结果"
                    ],
                    risks=[
                        "测试逻辑错误",
                        "集成冲突",
                        "性能影响"
                    ],
                    rollback_points=[
                        "移除新增测试文件",
                        "恢复原始测试配置",
                        "回退集成变更"
                    ]
                ),
                Milestone(
                    id="M3",
                    name="文档和提交准备",
                    description="创建文档并准备 PR 提交",
                    input_requirements=[
                        "完成的测试代码",
                        "测试结果验证",
                        "PR 模板"
                    ],
                    output_deliverables=[
                        "PR 描述文档",
                        "使用说明",
                        "完整的 PR 内容"
                    ],
                    acceptance_criteria=[
                        "文档清晰完整",
                        "PR 符合赏金要求",
                        "所有文件准备就绪"
                    ],
                    planned_steps=[
                        "编写 PR 描述",
                        "创建使用文档",
                        "整理提交文件",
                        "最终验证和检查"
                    ],
                    risks=[
                        "文档不完整",
                        "遗漏提交文件",
                        "格式不符合要求"
                    ],
                    rollback_points=[
                        "重新整理文档",
                        "补充遗漏文件",
                        "修正格式问题"
                    ]
                )
            ]
        elif bounty['type'] == 'documentation':
            # 文档类任务通常不需要复杂里程碑
            milestones = [
                Milestone(
                    id="M1",
                    name="文档内容创建和验证",
                    description="创建完整的文档内容并进行验证",
                    input_requirements=[
                        f"赏金 #{bounty['id']} 的具体要求",
                        "相关 API 或功能的访问权限",
                        "现有文档参考"
                    ],
                    output_deliverables=[
                        "完整的文档内容",
                        "示例代码（如适用）",
                        "验证结果"
                    ],
                    acceptance_criteria=[
                        "文档内容准确完整",
                        "符合赏金要求",
                        "格式规范"
                    ],
                    planned_steps=[
                        "分析文档需求",
                        "收集相关信息",
                        "撰写文档内容",
                        "验证和校对"
                    ],
                    risks=[
                        "信息不准确",
                        "遗漏重要内容",
                        "格式问题"
                    ],
                    rollback_points=[
                        "重新收集信息",
                        "补充遗漏内容",
                        "修正格式"
                    ]
                )
            ]
        else:
            # 默认通用里程碑
            milestones = [
                Milestone(
                    id="M1",
                    name="需求分析和规划",
                    description="分析需求并制定详细实施计划",
                    input_requirements=[f"赏金 #{bounty['id']} 要求"],
                    output_deliverables=["详细实施计划"],
                    acceptance_criteria=["计划获得确认"],
                    planned_steps=["需求分析", "技术调研", "计划制定"],
                    risks=["需求理解偏差"],
                    rollback_points=["重新分析需求"]
                ),
                Milestone(
                    id="M2",
                    name="实施和测试",
                    description="执行实施并进行测试验证",
                    input_requirements=["实施计划"],
                    output_deliverables=["完成的实现"],
                    acceptance_criteria=["通过所有测试"],
                    planned_steps=["代码实现", "测试验证", "问题修复"],
                    risks=["技术实现困难"],
                    rollback_points=["回退到计划阶段"]
                ),
                Milestone(
                    id="M3", 
                    name="文档和提交",
                    description="创建文档并准备提交",
                    input_requirements=["完成的实现"],
                    output_deliverables=["完整 PR 内容"],
                    acceptance_criteria=["PR 准备就绪"],
                    planned_steps=["文档编写", "PR 准备", "最终检查"],
                    risks=["文档不完整"],
                    rollback_points=["完善文档"]
                )
            ]
        
        return milestones
    
    def _generate_task_plan(self, bounty: Dict, milestones: List[Milestone]) -> str:
        """生成完整的 task_plan.md 内容"""
        plan_lines = []
        
        # 状态标记
        plan_lines.append("STATUS: DRAFT")
        plan_lines.append("")
        
        # 目标和 DoD
        plan_lines.append("## 目标 / DoD")
        plan_lines.append(f"- 目标：完成赏金 #{bounty['id']} - {bounty['title']}")
        plan_lines.append(f"- 完成定义（DoD）：{bounty.get('reward', '赏金要求满足')}")
        plan_lines.append("")
        
        # 范围
        plan_lines.append("## 范围")
        plan_lines.append("- 做：")
        plan_lines.append(f"  - 实现赏金 #{bounty['id']} 的所有要求")
        plan_lines.append("  - 遵循 BS2.0 设计原则")
        plan_lines.append("  - 提供完整的文档和测试")
        plan_lines.append("- 不做：")
        plan_lines.append("  - 超出赏金范围的功能")
        plan_lines.append("  - 破坏性变更")
        plan_lines.append("  - 未经验证的实验性功能")
        plan_lines.append("")
        
        # 约束
        plan_lines.append("## 约束")
        plan_lines.append("- 时间：按赏金要求时间完成")
        plan_lines.append("- 依赖：BS2.0 系统、GitHub API、相关代码库")
        plan_lines.append("- 环境：Linux 环境，Python 3.6+")
        plan_lines.append("")
        
        # 风险和回滚
        plan_lines.append("## 风险 & 回滚")
        plan_lines.append("- 风险：")
        plan_lines.append("  - 维护者反馈需要修改")
        plan_lines.append("  - 技术实现遇到意外困难")
        plan_lines.append("  - 赏金要求发生变化")
        plan_lines.append("- 回滚策略：")
        plan_lines.append("  - 记录所有变更到 findings.md")
        plan_lines.append("  - 保留原始状态备份")
        plan_lines.append("  - 按里程碑粒度回滚")
        plan_lines.append("")
        
        # 里程碑
        plan_lines.append("## 子计划 / 里程碑（Milestones）")
        plan_lines.append("")
        
        for milestone in milestones:
            plan_lines.append(f"### {milestone.id}: {milestone.name}")
            plan_lines.append(f"- 描述：{milestone.description}")
            plan_lines.append("- 输入：")
            for item in milestone.input_requirements:
                plan_lines.append(f"  - {item}")
            plan_lines.append("- 输出：")
            for item in milestone.output_deliverables:
                plan_lines.append(f"  - {item}")
            plan_lines.append("- 验收标准：")
            for item in milestone.acceptance_criteria:
                plan_lines.append(f"  - {item}")
            plan_lines.append("- 计划步骤：")
            for item in milestone.planned_steps:
                plan_lines.append(f"  - {item}")
            plan_lines.append("- 风险：")
            for item in milestone.risks:
                plan_lines.append(f"  - {item}")
            plan_lines.append("- 回滚点：")
            for item in milestone.rollback_points:
                plan_lines.append(f"  - {item}")
            plan_lines.append("")
        
        return "\n".join(plan_lines)
    
    def _init_progress_and_findings(self, bounty_id: str):
        """初始化 progress.md 和 findings.md"""
        # Progress 文件
        progress_content = """# progress.md

## 状态
- 当前阶段：计划
- 当前子计划：等待计划冻结

## Done
- 

## Next
- 

## Blockers / 风险
- 

## 最近一次检查点
- 时间：
- 验证：
- 结果：
"""
        progress_file = self.plan_dir / f"progress_{bounty_id}.md"
        progress_file.write_text(progress_content)
        
        # Findings 文件  
        findings_content = """# findings.md

## 关键发现
- 

## 决策记录
- 

## 验证命令/步骤
- 

## 回滚步骤
- 
"""
        findings_file = self.plan_dir / f"findings_{bounty_id}.md"
        findings_file.write_text(findings_content)

if __name__ == "__main__":
    # 测试 PlanSuitePlanner
    planner = PlanSuitePlanner("/home/admin/.openclaw/workspace/stone-bs2.0")
    
    test_bounty = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "type": "test", 
        "complexity": "MODERATE",
        "reward": "5 RTC"
    }
    
    test_design = {"analysis": "test implementation required"}
    
    result = planner.create_milestone_plan(test_bounty, test_design)
    print(result)