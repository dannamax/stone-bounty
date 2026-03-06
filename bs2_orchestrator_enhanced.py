#!/usr/bin/env python3
"""
Enhanced BS2.0 Orchestrator with PlanSuite Integration
Extends the original BS2Orchestrator with PlanSuite milestone management,
plan freezing, and isolated session execution capabilities.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add BS2 system to path
bs2_path = Path(__file__).parent
sys.path.insert(0, str(bs2_path))

from bs2_task_queue import BS2TaskQueue, BS2TaskExecutor
from bs2_progress_notifier import BS2ProgressNotifier, BS2StatusReporter
from bs2_timeout_manager import BS2TimeoutManager
from enhanced_bounty_analyzer import EnhancedBountyAnalyzer, Bounty
from plansuite_planner import PlanSuitePlanner

@dataclass
class Milestone:
    """Represents a PlanSuite milestone"""
    id: str
    name: str
    input: str
    output: str
    acceptance_criteria: str
    plan_steps: List[str]
    risks: str
    rollback_points: str

class BS2OrchestratorEnhanced:
    """Enhanced BS2.0 orchestrator with PlanSuite integration"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.queue = BS2TaskQueue(workspace_dir)
        self.executor = BS2TaskExecutor(self.queue)
        self.notifier = BS2ProgressNotifier(workspace_dir)
        self.timeout_mgr = BS2TimeoutManager(workspace_dir)
        self.reporter = BS2StatusReporter(workspace_dir)
        self.analyzer = EnhancedBountyAnalyzer()
        self.plansuite_planner = PlanSuitePlanner(workspace_dir)
        self.config = self._load_config()
        self.plan_dir = self.workspace_dir / "stone-bs2.0" / "plansuite_plans"
    
    def _load_config(self) -> Dict:
        """Load enhanced configuration"""
        config_path = self.workspace_dir / "stone-bs2.0" / "config_enhanced.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to original config
            original_config = self.workspace_dir / "stone-bs2.0" / "config.json"
            if original_config.exists():
                with open(original_config, 'r') as f:
                    return json.load(f)
            return {}
    
    def should_use_plansuite(self, bounty: Bounty) -> bool:
        """Determine if PlanSuite workflow should be used"""
        plansuite_config = self.config.get("plansuite", {})
        if not plansuite_config.get("enabled", False):
            return False
        
        # Use PlanSuite for moderate/high complexity tasks
        if bounty.complexity in ["MODERATE", "HIGH", "VERY_HIGH"]:
            return True
        
        # Use PlanSuite for feature, bug_fix, and test types
        if bounty.type in ["feature", "bug_fix", "test"]:
            return True
        
        # Skip PlanSuite for simple documentation and community tasks
        if bounty.type in ["documentation", "community"]:
            return False
        
        return False
    
    def create_enhanced_bounty_workflow(self, bounty: Bounty) -> str:
        """
        Create enhanced bounty workflow with PlanSuite integration
        
        Args:
            bounty: The bounty to process
            
        Returns:
            Status message with next steps
        """
        print(f"🧠 Analyzing bounty #{bounty.id}: {bounty.title}")
        
        # Step 1: Enhanced bounty analysis
        analysis = self.analyzer.analyze_bounty(bounty)
        if analysis.priority == "SKIP":
            return f"❌ Skipping bounty #{bounty.id} - {analysis.recommended_action}"
        
        print(f"📊 BS2 Score: {analysis.bs2_score}/100, Priority: {analysis.priority}")
        
        # Step 2: Determine workflow based on complexity and type
        if self.should_use_plansuite(bounty):
            print("📋 Using PlanSuite enhanced workflow...")
            return self._create_plansuite_workflow(bounty, analysis)
        else:
            print("📝 Using traditional BS2.0 workflow...")
            return self._create_traditional_workflow(bounty, analysis)
    
    def _create_plansuite_workflow(self, bounty: Bounty, analysis: 'BountyAnalysis') -> str:
        """Create PlanSuite enhanced workflow"""
        try:
            # Generate detailed design analysis for PlanSuite
            design_analysis = {
                "bounty": bounty.__dict__,
                "analysis": analysis.__dict__,
                "recommendations": analysis.recommended_action,
                "success_rate": analysis.estimated_success_rate
            }
            
            # Create PlanSuite milestone plan
            plan_result = self.plansuite_planner.create_milestone_plan(bounty, design_analysis)
            
            return f"""
✅ PlanSuite enhanced workflow created for bounty #{bounty.id}

{plan_result}

🔒 **WAITING FOR USER CONFIRMATION**
Please review the plan and confirm execution by saying:
"Execute PlanSuite plan for #{bounty.id}" or "按计划执行 #{bounty.id}"

Plan files location:
- Task Plan: stone-bs2.0/plansuite_plans/task_plan_{bounty.id}.md
- Progress: stone-bs2.0/plansuite_plans/progress_{bounty.id}.md  
- Findings: stone-bs2.0/plansuite_plans/findings_{bounty.id}.md
            """
        except Exception as e:
            print(f"❌ Error creating PlanSuite workflow: {e}")
            return f"❌ Failed to create PlanSuite workflow: {str(e)}"
    
    def _create_traditional_workflow(self, bounty: Bounty, analysis: 'BountyAnalysis') -> str:
        """Create traditional BS2.0 workflow"""
        # This would use the original BS2.0 workflow
        # For now, return a placeholder
        return f"📝 Traditional workflow ready for bounty #{bounty.id}"
    
    def execute_frozen_plan(self, bounty_id: str) -> str:
        """
        Execute a frozen PlanSuite plan
        
        Args:
            bounty_id: The bounty ID to execute
            
        Returns:
            Execution status message
        """
        plan_file = self.plan_dir / f"task_plan_{bounty_id}.md"
        
        if not plan_file.exists():
            return f"❌ Plan file not found for bounty #{bounty_id}"
        
        # Check if plan is frozen
        plan_content = plan_file.read_text()
        if "STATUS: FINALIZED" not in plan_content:
            return f"❌ Plan for bounty #{bounty_id} is not frozen. Please confirm the plan first."
        
        print(f"🚀 Executing frozen PlanSuite plan for bounty #{bounty_id}")
        
        # Parse milestones from plan
        milestones = self._parse_milestones_from_plan(plan_content)
        if not milestones:
            return f"❌ No milestones found in plan for bounty #{bounty_id}"
        
        # Execute first milestone in isolated session
        first_milestone = milestones[0]
        execution_result = self.execute_milestone_in_isolated_session(
            first_milestone, bounty_id
        )
        
        # Update progress file
        self._update_progress_file(bounty_id, first_milestone, "in_progress")
        
        return f"""
✅ Started executing PlanSuite plan for bounty #{bounty_id}

Milestone: {first_milestone.name}
Status: In Progress
Isolated session: {execution_result}

Monitor progress in: stone-bs2.0/plansuite_plans/progress_{bounty_id}.md
        """
    
    def _parse_milestones_from_plan(self, plan_content: str) -> List[Milestone]:
        """Parse milestones from PlanSuite plan content"""
        milestones = []
        lines = plan_content.split('\n')
        
        current_milestone = None
        parsing_milestone = False
        
        for line in lines:
            if line.startswith('### M') and ':' in line:
                # Start new milestone
                if current_milestone:
                    milestones.append(current_milestone)
                
                milestone_name = line.split(':', 1)[1].strip()
                milestone_id = line.split('### ')[1].split(':')[0].strip()
                current_milestone = Milestone(
                    id=milestone_id,
                    name=milestone_name,
                    input="",
                    output="",
                    acceptance_criteria="",
                    plan_steps=[],
                    risks="",
                    rollback_points=""
                )
                parsing_milestone = True
                
            elif parsing_milestone and current_milestone:
                if line.startswith('- 输入：') or line.startswith('- Input:'):
                    current_milestone.input = line.split('：', 1)[1].strip() if '：' in line else line.split(':', 1)[1].strip()
                elif line.startswith('- 输出：') or line.startswith('- Output:'):
                    current_milestone.output = line.split('：', 1)[1].strip() if '：' in line else line.split(':', 1)[1].strip()
                elif line.startswith('- 验收标准：') or line.startswith('- Acceptance criteria:'):
                    current_milestone.acceptance_criteria = line.split('：', 1)[1].strip() if '：' in line else line.split(':', 1)[1].strip()
                elif line.startswith('- 风险：') or line.startswith('- Risks:'):
                    current_milestone.risks = line.split('：', 1)[1].strip() if '：' in line else line.split(':', 1)[1].strip()
                elif line.startswith('- 回滚点：') or line.startswith('- Rollback points:'):
                    current_milestone.rollback_points = line.split('：', 1)[1].strip() if '：' in line else line.split(':', 1)[1].strip()
                elif line.startswith('- 计划步骤：') or line.startswith('- Plan steps:'):
                    # Collect plan steps (multi-line)
                    pass
        
        if current_milestone:
            milestones.append(current_milestone)
            
        return milestones
    
    def execute_milestone_in_isolated_session(self, milestone: Milestone, bounty_id: str) -> str:
        """
        Execute a single milestone in an isolated session
        
        Args:
            milestone: The milestone to execute
            bounty_id: The bounty ID
            
        Returns:
            Session spawn result
        """
        from openclaw.tools.sessions import sessions_spawn
        
        milestone_task = f"""
Execute milestone for bounty #{bounty_id}: {milestone.name}

Milestone Details:
- Input: {milestone.input}
- Output: {milestone.output}
- Acceptance Criteria: {milestone.acceptance_criteria}
- Risks: {milestone.risks}
- Rollback Points: {milestone.rollback_points}

Execution Requirements:
1. Use Superpowers TDD workflow for implementation
2. Record progress in plansuite_plans/progress_{bounty_id}.md
3. Record findings in plansuite_plans/findings_{bounty_id}.md
4. Perform validation checks after completion
5. If issues arise, update findings file and pause execution
6. Follow BS2.0 design principles (non-destructive, inline integration)

Workspace: /home/admin/.openclaw/workspace/stone-bs2.0
        """
        
        try:
            result = sessions_spawn(
                task=milestone_task,
                label=f"bounty-{bounty_id}-milestone-{milestone.id}",
                thinking="on"
            )
            return f"Session spawned successfully: {result}"
        except Exception as e:
            return f"Error spawning session: {str(e)}"
    
    def _update_progress_file(self, bounty_id: str, milestone: Milestone, status: str):
        """Update progress file with current milestone status"""
        progress_file = self.plan_dir / f"progress_{bounty_id}.md"
        
        if not progress_file.exists():
            # Create from template
            template_file = self.plan_dir / "templates" / "progress.md"
            if template_file.exists():
                progress_content = template_file.read_text()
            else:
                progress_content = "# progress.md\n\n## 状态\n- 当前阶段：执行\n- 当前子计划：\n\n## Done\n-\n\n## Next\n-\n\n## Blockers / 风险\n-\n\n## 最近一次检查点\n- 时间：\n- 验证：\n- 结果：\n"
        else:
            progress_content = progress_file.read_text()
        
        # Update current milestone
        updated_content = progress_content.replace(
            "- 当前子计划：",
            f"- 当前子计划：{milestone.name} ({status})"
        )
        
        # Update Next section
        updated_content = updated_content.replace(
            "## Next\n-",
            f"## Next\n- {milestone.name}"
        )
        
        progress_file.write_text(updated_content)
    
    def show_enhanced_status(self):
        """Display enhanced status including PlanSuite plans"""
        print("\n📊 BS2.0 Enhanced System Status")
        print("=" * 50)
        
        # Show original BS2 status
        super().show_status() if hasattr(self, 'show_status') else print("Original BS2 status not available")
        
        # Show PlanSuite plans
        print("\n📋 PlanSuite Plans Status:")
        plan_files = list(self.plan_dir.glob("task_plan_*.md"))
        if plan_files:
            for plan_file in plan_files:
                bounty_id = plan_file.stem.replace("task_plan_", "")
                content = plan_file.read_text()
                if "STATUS: FINALIZED" in content:
                    status = "✅ FINALIZED"
                elif "STATUS: DRAFT" in content:
                    status = "📝 DRAFT"
                else:
                    status = "❓ UNKNOWN"
                print(f"  - PR #{bounty_id}: {status}")
        else:
            print("  No PlanSuite plans found")
        
        print("=" * 50)

def main():
    """Main entry point for enhanced BS2.0 orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BS2.0 Enhanced Bounty Hunting System")
    parser.add_argument("--create-enhanced-workflow", action="store_true",
                       help="Create enhanced workflow for a bounty")
    parser.add_argument("--execute-frozen-plan", action="store_true",
                       help="Execute a frozen PlanSuite plan")
    parser.add_argument("--bounty-id", type=str, help="Bounty ID")
    parser.add_argument("--bounty-title", type=str, help="Bounty title")
    parser.add_argument("--bounty-type", type=str, default="feature", 
                       help="Bounty type (feature, bug_fix, test, documentation, community)")
    parser.add_argument("--complexity", type=str, default="MODERATE",
                       help="Bounty complexity (LOW, MODERATE, HIGH, VERY_HIGH)")
    parser.add_argument("--reward", type=str, default="Unknown",
                       help="Bounty reward")
    parser.add_argument("--plansuite-status", action="store_true",
                       help="Show PlanSuite integration status")
    
    args = parser.parse_args()
    
    orchestrator = BS2OrchestratorEnhanced()
    
    if args.plansuite_status:
        print("🔍 PlanSuite Integration Status:")
        config = orchestrator.config.get("plansuite", {})
        print(f"  Enabled: {config.get('enabled', False)}")
        print(f"  Require Plan Freeze: {config.get('require_plan_freeze', False)}")
        print(f"  Use Milestones: {config.get('use_milestones', False)}")
        print(f"  Isolated Execution: {config.get('isolated_execution', False)}")
        print(f"  Plan Directory: {config.get('plan_dir', 'plansuite_plans')}")
        
    elif args.create_enhanced_workflow:
        if not args.bounty_id:
            print("❌ Error: --bounty-id is required for creating enhanced workflow")
            sys.exit(1)
        
        # Create bounty object
        bounty = Bounty(
            id=args.bounty_id,
            title=args.bounty_title or f"Bounty #{args.bounty_id}",
            url=f"https://github.com/Scottcjn/rustchain-bounties/issues/{args.bounty_id}",
            description="",
            reward=args.reward,
            complexity=args.complexity,
            risk="LOW" if args.complexity == "LOW" else "MEDIUM",
            time_estimate="1h" if args.complexity == "LOW" else "6h",
            type=args.bounty_type,
            status="AVAILABLE",
            repository="rustchain-bounties",
            created_at="2026-03-06T00:00:00Z",
            updated_at="2026-03-06T00:00:00Z"
        )
        
        result = orchestrator.create_enhanced_bounty_workflow(bounty)
        print(result)
        
    elif args.execute_frozen_plan:
        if not args.bounty_id:
            print("❌ Error: --bounty-id is required for executing frozen plan")
            sys.exit(1)
        
        result = orchestrator.execute_frozen_plan(args.bounty_id)
        print(result)
        
    else:
        print("📋 BS2.0 Enhanced Bounty Hunting System")
        print("Use --create-enhanced-workflow to create enhanced workflow")
        print("Use --execute-frozen-plan to execute frozen PlanSuite plan")
        print("Use --plansuite-status to check PlanSuite integration status")

if __name__ == "__main__":
    main()