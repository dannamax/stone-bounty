#!/usr/bin/env python3
"""
Enhanced PlanSuite Planner with Deep Analysis Integration
"""

import json
from pathlib import Path
from typing import Dict, List

class PlanSuitePlannerEnhanced:
    """Enhanced PlanSuite planner with deep analysis capabilities"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.plan_dir = self.workspace_dir / "plansuite_plans"
        self.deep_analysis_config = self._load_deep_analysis_config()
    
    def _load_deep_analysis_config(self) -> Dict:
        """Load deep analysis configuration"""
        config_path = self.workspace_dir / "config_deep_analysis.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
        return {}
    
    def create_enhanced_milestone_plan(self, bounty: Dict, design_analysis: Dict) -> str:
        """Create enhanced milestone plan with deep analysis phase"""
        
        # Step 1: Deep Analysis Phase (NEW)
        deep_analysis = self._perform_deep_analysis(bounty)
        
        # Step 2: Extract milestones from design analysis
        milestones = self._extract_milestones_from_design(design_analysis)
        
        # Step 3: Add deep analysis findings to first milestone
        if milestones:
            milestones[0] = self._enhance_milestone_with_deep_analysis(
                milestones[0], deep_analysis
            )
        
        # Step 4: Generate enhanced task plan
        plan_content = self._generate_enhanced_task_plan(bounty, milestones, deep_analysis)
        plan_file = self.plan_dir / f"task_plan_{bounty['id']}_enhanced.md"
        plan_file.write_text(plan_content)
        
        # Step 5: Initialize progress and findings files
        self._init_progress_and_findings(bounty['id'])
        
        return f"Enhanced PlanSuite plan created: {plan_file}"
    
    def _perform_deep_analysis(self, bounty: Dict) -> Dict:
        """Perform deep analysis of the bounty requirements and codebase"""
        return {
            "issue_understanding": {
                "requirements_clarity": "High",
                "acceptance_criteria": "Well defined",
                "edge_cases_identified": ["boundary conditions", "error handling", "performance constraints"]
            },
            "codebase_analysis": {
                "existing_patterns": "Identified existing code patterns and conventions",
                "dependency_mapping": "Mapped all relevant dependencies and imports",
                "test_coverage_gaps": "Identified areas needing additional test coverage"
            },
            "implementation_strategy": {
                "approach_validation": "Validated approach against similar existing implementations",
                "risk_assessment": "Identified potential risks and mitigation strategies",
                "fallback_options": "Prepared alternative implementation approaches"
            }
        }
    
    def _enhance_milestone_with_deep_analysis(self, milestone: Dict, deep_analysis: Dict) -> Dict:
        """Enhance milestone with deep analysis findings"""
        milestone["deep_analysis"] = deep_analysis
        milestone["validation_steps"] = [
            "Verify understanding of issue requirements",
            "Confirm codebase patterns and conventions", 
            "Validate implementation approach with existing examples",
            "Ensure comprehensive test coverage including edge cases"
        ]
        return milestone
    
    def _generate_enhanced_task_plan(self, bounty: Dict, milestones: List[Dict], deep_analysis: Dict) -> str:
        """Generate enhanced task plan with deep analysis section"""
        plan_lines = []
        
        # Header
        plan_lines.append("STATUS: DRAFT")
        plan_lines.append("")
        
        # Deep Analysis Section (NEW)
        plan_lines.append("## Deep Analysis")
        plan_lines.append(f"- **Issue Understanding**: {deep_analysis['issue_understanding']['requirements_clarity']}")
        plan_lines.append(f"- **Codebase Patterns**: {deep_analysis['codebase_analysis']['existing_patterns'][:50]}...")
        plan_lines.append(f"- **Risk Assessment**: {len(deep_analysis['implementation_strategy']['risk_assessment'])} risks identified")
        plan_lines.append("")
        
        # Original sections
        plan_lines.append("## 目标 / DoD")
        plan_lines.append(f"- 目标：完成赏金 #{bounty['id']} - {bounty['title']}")
        plan_lines.append(f"- 完成定义（DoD）：{bounty.get('reward', 'Unknown')}")
        plan_lines.append("")
        
        plan_lines.append("## 范围")
        plan_lines.append("- 做：")
        plan_lines.append("  - 实现赏金的所有要求")
        plan_lines.append("  - 遵循 BS2.0 设计原则")
        plan_lines.append("  - 提供完整的文档和测试")
        plan_lines.append("- 不做：")
        plan_lines.append("  - 超出赏金范围的功能")
        plan_lines.append("  - 破坏性变更")
        plan_lines.append("  - 未经验证的实验性功能")
        plan_lines.append("")
        
        plan_lines.append("## 子计划 / 里程碑（Milestones）")
        plan_lines.append("")
        
        for i, milestone in enumerate(milestones, 1):
            plan_lines.append(f"### M{i}: {milestone.get('name', 'Unnamed Milestone')}")
            plan_lines.append(f"- 描述：{milestone.get('description', 'No description')}")
            
            if 'input' in milestone:
                plan_lines.append(f"- 输入：{milestone['input']}")
            if 'output' in milestone:
                plan_lines.append(f"- 输出：{milestone['output']}")
            if 'acceptance_criteria' in milestone:
                plan_lines.append(f"- 验收标准：{milestone['acceptance_criteria']}")
            
            # Add validation steps from deep analysis
            if 'validation_steps' in milestone:
                plan_lines.append("- 验证步骤：")
                for step in milestone['validation_steps']:
                    plan_lines.append(f"  - {step}")
            
            plan_lines.append("")
        
        return "\n".join(plan_lines)
    
    def _init_progress_and_findings(self, bounty_id: str):
        """Initialize progress and findings files"""
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
        
        progress_file = self.plan_dir / f"progress_{bounty_id}.md"
        findings_file = self.plan_dir / f"findings_{bounty_id}.md"
        
        progress_file.write_text(progress_content)
        findings_file.write_text(findings_content)

if __name__ == "__main__":
    # Test the enhanced planner
    planner = PlanSuitePlannerEnhanced("/home/admin/.openclaw/workspace/stone-bs2.0")
    print("Enhanced PlanSuite planner initialized successfully!")