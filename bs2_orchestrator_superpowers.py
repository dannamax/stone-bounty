#!/usr/bin/env python3
"""
BS2.0 Orchestrator with Mandatory Superpowers Workflow
This orchestrator enforces the complete Superpowers workflow for all bounty tasks.
"""

import subprocess
import sys
from pathlib import Path

# Add BS2 system to path
bs2_path = Path(__file__).parent
sys.path.insert(0, str(bs2_path))

from bs2_task_queue import BS2TaskQueue, BS2TaskExecutor
from bs2_progress_notifier import BS2ProgressNotifier, BS2StatusReporter
from bs2_timeout_manager import BS2TimeoutManager
from superpowers_workflow import SuperpowersWorkflow

class BS2OrchestratorSuperpowers:
    """BS2.0 Orchestrator with mandatory Superpowers workflow"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.queue = BS2TaskQueue(str(self.workspace_dir))
        self.executor = BS2TaskExecutor(self.queue)
        self.notifier = BS2ProgressNotifier(str(self.workspace_dir))
        self.timeout_mgr = BS2TimeoutManager(str(self.workspace_dir))
        self.reporter = BS2StatusReporter(str(self.workspace_dir))
        self.superpowers = SuperpowersWorkflow(str(self.workspace_dir))
        
        # Load mandatory Superpowers configuration
        self.config = self._load_mandatory_config()
    
    def _load_mandatory_config(self):
        """Load mandatory Superpowers configuration"""
        config_path = self.workspace_dir / "stone-bs2.0" / "config_mandatory_superpowers.json"
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default mandatory configuration
            return {
                "superpowers": {
                    "enabled": True,
                    "mandatory_workflow": True,
                    "workflow_stages": [
                        "brainstorming",
                        "systematic_debugging", 
                        "test_driven_development",
                        "code_review",
                        "finishing_branch"
                    ],
                    "require_approval": True,
                    "enforce_tdd": True,
                    "quality_gates": True
                }
            }
    
    def create_and_execute_task_with_superpowers(self, task_name: str, task_type: str,
                                                issue_url: str, bounty_amount: str,
                                                steps: list) -> str:
        """
        Create and execute a BS2.0 task with mandatory Superpowers workflow
        
        This method enforces the complete Superpowers workflow:
        1. Brainstorming - Deep requirement analysis
        2. Systematic Debugging - Codebase understanding  
        3. Test-Driven Development - Write tests first
        4. Code Review - Quality assurance
        5. Finishing Branch - Complete submission
        """
        
        print(f"🚀 Creating BS2.0 task with MANDATORY Superpowers workflow: {task_name}")
        
        # Step 1: Create task in queue
        task_id = self.queue.create_task(task_name, task_type, issue_url, bounty_amount)
        self.notifier.send_progress_update(task_id, "Task initialized with Superpowers workflow", 5)
        
        # Step 2: Execute mandatory Superpowers workflow
        try:
            # Stage 1: Brainstorming - Deep requirement analysis
            print("🧠 Stage 1: Brainstorming - Deep requirement analysis")
            brainstorming_result = self.superpowers.brainstorming_phase(
                task_name, issue_url, bounty_amount
            )
            if not brainstorming_result["approved"]:
                raise Exception("Brainstorming phase requires user approval")
            
            # Stage 2: Systematic Debugging - Codebase understanding
            print("🔍 Stage 2: Systematic Debugging - Codebase understanding")  
            debugging_result = self.superpowers.systematic_debugging_phase(
                issue_url, brainstorming_result
            )
            
            # Stage 3: Test-Driven Development - Write tests first
            print("🧪 Stage 3: Test-Driven Development - Write tests first")
            tdd_result = self.superpowers.test_driven_development_phase(
                issue_url, debugging_result
            )
            
            # Stage 4: Code Review - Quality assurance
            print("✅ Stage 4: Code Review - Quality assurance")
            review_result = self.superpowers.code_review_phase(tdd_result)
            
            # Stage 5: Finishing Branch - Complete submission
            print("🏁 Stage 5: Finishing Branch - Complete submission")
            finish_result = self.superpowers.finishing_branch_phase(
                issue_url, review_result
            )
            
            # Task completed successfully
            self.notifier.send_completion_notification(task_id, finish_result["pr_url"], success=True)
            self.queue.complete_task(task_id, pr_url=finish_result["pr_url"])
            
            return task_id
            
        except Exception as e:
            # Handle failure with proper error logging
            print(f"❌ Superpowers workflow failed: {e}")
            error_details = {
                "error": str(e),
                "stage": getattr(e, 'stage', 'unknown'),
                "fallback_triggered": True
            }
            
            self.notifier.send_completion_notification(task_id, "", success=False)
            self.queue.complete_task(task_id, error=str(e))
            return task_id
    
    def show_status(self):
        """Display current BS2.0 system status with Superpowers integration"""
        summary = self.reporter.generate_summary()
        
        print("\n📊 BS2.0 System Status (Superpowers Enhanced)")
        print("=" * 60)
        print(f"Superpowers Workflow: {'✅ ENABLED' if self.config['superpowers']['enabled'] else '❌ DISABLED'}")
        print(f"Mandatory Workflow: {'✅ ENFORCED' if self.config['superpowers']['mandatory_workflow'] else '⚠️ OPTIONAL'}")
        
        # Handle both task summary and status message formats
        if 'status' in summary and 'total_tasks' not in summary:
            # No tasks found
            print(f"Status: {summary['status']}")
            print("Use --create-task to create your first Superpowers-enhanced task")
        else:
            # Tasks available
            print(f"Total Tasks: {summary['total_tasks']}")
            print(f"✅ Completed: {summary['completed']}")
            print(f"🔄 In Progress: {summary['in_progress']}")
            print(f"❌ Failed: {summary['failed']}")
            print(f"⏳ Pending: {summary['pending']}")
            print("=" * 60 + "\n")
        
        return summary

def main():
    """Main entry point for BS2.0 Superpowers orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BS2.0 Bounty Hunting System with Mandatory Superpowers")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--create-task", action="store_true", 
                       help="Create task with mandatory Superpowers workflow")
    parser.add_argument("--task-name", type=str, help="Task name")
    parser.add_argument("--task-type", type=str, help="Task type")
    parser.add_argument("--issue-url", type=str, help="Issue URL")
    parser.add_argument("--bounty-amount", type=str, help="Bounty amount")
    
    args = parser.parse_args()
    
    orchestrator = BS2OrchestratorSuperpowers()
    
    if args.status:
        orchestrator.show_status()
    elif args.create_task:
        if not all([args.task_name, args.task_type, args.issue_url, args.bounty_amount]):
            print("❌ Error: All task parameters are required for Superpowers workflow")
            sys.exit(1)
        
        orchestrator.create_and_execute_task_with_superpowers(
            args.task_name, args.task_type, args.issue_url, args.bounty_amount, []
        )
    else:
        print("📋 BS2.0 Superpowers Enhanced System")
        print("Use --status to view system status")
        print("Use --create-task with appropriate arguments to create a Superpowers-enhanced task")

if __name__ == "__main__":
    main()