#!/usr/bin/env python3
"""
Enhanced BS2.0 Orchestrator with PlanSuite Integration
Fixed version with proper EnhancedBountyAnalyzer integration
"""

import subprocess
import sys
from pathlib import Path

# Add BS2 system to path
bs2_path = Path(__file__).parent
sys.path.insert(0, str(bs2_path))

# Import fixed analyzer
from enhanced_bounty_analyzer_fixed import EnhancedBountyAnalyzer
from bs2_task_queue import BS2TaskQueue, BS2TaskExecutor
from bs2_progress_notifier import BS2ProgressNotifier, BS2StatusReporter
from bs2_timeout_manager import BS2TimeoutManager
from plansuite_planner import PlanSuitePlanner

class BS2OrchestratorEnhanced:
    """Enhanced orchestrator for BS2.0 bounty hunting operations with PlanSuite integration"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.queue = BS2TaskQueue(str(self.workspace_dir))
        self.executor = BS2TaskExecutor(self.queue)
        self.notifier = BS2ProgressNotifier(str(self.workspace_dir))
        self.timeout_mgr = BS2TimeoutManager(str(self.workspace_dir))
        self.reporter = BS2StatusReporter(str(self.workspace_dir))
        self.analyzer = EnhancedBountyAnalyzer()
        self.plansuite_planner = PlanSuitePlanner(str(self.workspace_dir / "stone-bs2.0"))
        self.config = self._load_config()
    
    def _load_config(self):
        """Load enhanced configuration"""
        config_path = self.workspace_dir / "stone-bs2.0" / "config_enhanced.json"
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def should_use_plansuite(self, bounty_complexity: str, bounty_type: str) -> bool:
        """Determine if PlanSuite workflow should be used"""
        plansuite_config = self.config.get("plansuite", {})
        if not plansuite_config.get("enabled", False):
            return False
        
        # Use PlanSuite for moderate+ complexity tasks
        if bounty_complexity in ["MODERATE", "HIGH"]:
            return True
        
        # Skip for documentation tasks
        if bounty_type == "documentation":
            return False
            
        # Use for feature, bug_fix, test types
        if bounty_type in ["feature", "bug_fix", "test"]:
            return True
            
        return False
    
    def create_enhanced_bounty_workflow(self, bounty_data: dict) -> str:
        """Create enhanced bounty workflow with PlanSuite integration"""
        
        bounty_id = bounty_data.get("id", "unknown")
        bounty_title = bounty_data.get("title", "Unknown Bounty")
        bounty_type = bounty_data.get("type", "feature")
        bounty_complexity = bounty_data.get("complexity", "MODERATE")
        
        print(f"🧠 Analyzing bounty #{bounty_id}: {bounty_title}")
        
        # Determine workflow type
        use_plansuite = self.should_use_plansuite(bounty_complexity, bounty_type)
        
        if use_plansuite:
            print(f"📋 Creating PlanSuite workflow for bounty #{bounty_id}")
            
            # Create mock design analysis (in real scenario, this would come from Superpowers)
            design_analysis = {
                "bounty_id": bounty_id,
                "title": bounty_title,
                "complexity": bounty_complexity,
                "type": bounty_type,
                "recommended_approach": "structured_milestone_decomposition",
                "estimated_success_rate": 0.85
            }
            
            # Create PlanSuite plan
            plan_result = self.plansuite_planner.create_milestone_plan(
                bounty_data, design_analysis
            )
            
            return f"""
✅ PlanSuite Enhanced Workflow Created!

{plan_result}

🔒 **Waiting for User Confirmation**
Please review the plan and confirm execution:
- Plan file: stone-bs2.0/plansuite_plans/task_plan_{bounty_id}.md
- To execute: Run 'execute-frozen-plan --bounty-id {bounty_id}' after adding 'STATUS: FINALIZED' to the plan file
            """
        else:
            return f"🔄 Using traditional BS2.0 workflow for bounty #{bounty_id} (simple task)"
    
    def execute_frozen_plan(self, bounty_id: str) -> str:
        """Execute a frozen PlanSuite plan"""
        plan_file = self.workspace_dir / "stone-bs2.0" / "plansuite_plans" / f"task_plan_{bounty_id}.md"
        
        if not plan_file.exists():
            return f"❌ Plan file not found for bounty #{bounty_id}"
        
        plan_content = plan_file.read_text()
        if "STATUS: FINALIZED" not in plan_content:
            return f"❌ Plan for bounty #{bounty_id} is not frozen. Please add 'STATUS: FINALIZED' to the plan file."
        
        # Parse milestones (simplified)
        milestones = []
        current_milestone = None
        for line in plan_content.split('\n'):
            if line.startswith('### M') and ':' in line:
                milestone_name = line.split(':', 1)[1].strip()
                current_milestone = {
                    'name': milestone_name,
                    'id': len(milestones) + 1
                }
                milestones.append(current_milestone)
        
        if not milestones:
            return f"❌ No milestones found in plan for bounty #{bounty_id}"
        
        # Execute first milestone in isolated session
        first_milestone = milestones[0]
        milestone_task = f"""
Executing milestone for bounty #{bounty_id}: {first_milestone['name']}

This is an automated execution of the first milestone in the PlanSuite workflow.
The milestone will be executed in an isolated session to avoid context pollution.

Milestone details:
- ID: {first_milestone['id']}
- Name: {first_milestone['name']}
- Bounty: #{bounty_id}

Execution will follow BS2.0 principles with proper error handling and progress tracking.
        """
        
        # In real implementation, this would use sessions_spawn
        # For now, simulate the execution
        progress_file = self.workspace_dir / "stone-bs2.0" / "plansuite_plans" / f"progress_{bounty_id}.md"
        progress_content = f"""# progress.md

## 状态
- 当前阶段：执行
- 当前子计划：{first_milestone['name']}

## Done
- 

## Next
- Milestone {first_milestone['id'] + 1} (if exists)

## Blockers / 风险
- 

## 最近一次检查点
- 时间：2026-03-06T19:50:00Z
- 验证：Milestone execution started
- 结果：In progress
"""
        progress_file.write_text(progress_content)
        
        return f"✅ Started execution of milestone '{first_milestone['name']}' for bounty #{bounty_id}\nProgress tracked in: {progress_file}"

def main():
    """Main entry point for enhanced BS2.0 orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced BS2.0 Bounty Hunting System with PlanSuite")
    parser.add_argument("--create-enhanced-workflow", action="store_true", 
                       help="Create enhanced workflow for a bounty")
    parser.add_argument("--execute-frozen-plan", action="store_true",
                       help="Execute a frozen PlanSuite plan")
    parser.add_argument("--bounty-id", type=str, help="Bounty ID")
    parser.add_argument("--bounty-data", type=str, help="Bounty data JSON")
    
    args = parser.parse_args()
    
    orchestrator = BS2OrchestratorEnhanced()
    
    if args.create_enhanced_workflow and args.bounty_data:
        import json
        bounty_data = json.loads(args.bounty_data)
        result = orchestrator.create_enhanced_bounty_workflow(bounty_data)
        print(result)
    elif args.execute_frozen_plan and args.bounty_id:
        result = orchestrator.execute_frozen_plan(args.bounty_id)
        print(result)
    else:
        print("Enhanced BS2.0 Orchestrator with PlanSuite Integration")
        print("Use --create-enhanced-workflow with --bounty-data to create a PlanSuite workflow")
        print("Use --execute-frozen-plan with --bounty-id to execute a frozen plan")

if __name__ == "__main__":
    main()