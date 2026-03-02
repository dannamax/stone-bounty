#!/usr/bin/env python3
"""
BS2.0 Orchestrator - Main entry point for BS2.0 bounty hunting operations
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

class BS2Orchestrator:
    """Main orchestrator for BS2.0 bounty hunting operations"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.queue = BS2TaskQueue(workspace_dir)
        self.executor = BS2TaskExecutor(self.queue)
        self.notifier = BS2ProgressNotifier(workspace_dir)
        self.timeout_mgr = BS2TimeoutManager(workspace_dir)
        self.reporter = BS2StatusReporter(workspace_dir)
    
    def create_and_execute_task(self, task_name: str, task_type: str,
                                issue_url: str, bounty_amount: str,
                                steps: list) -> str:
        """Create and execute a BS2.0 task with full monitoring"""
        
        # Step 1: Create task
        print(f"🚀 Creating BS2.0 task: {task_name}")
        task_id = self.queue.create_task(task_name, task_type, issue_url, bounty_amount)
        self.notifier.send_progress_update(task_id, "Task initialized", 5)
        
        # Step 2: Generate fallback steps
        fallback_steps = self._generate_fallback_steps(task_type, issue_url)
        
        # Step 3: Execute with timeout protection
        print(f"⏱️  Executing task with timeout protection...")
        
        def execute_operation():
            return self.executor.execute_task(task_id, steps)
        
        result = self.timeout_mgr.execute_with_timeout(
            operation=execute_operation,
            timeout=self.timeout_mgr.timeout_config["overall_task"],
            task_id=task_id,
            fallback_steps=fallback_steps
        )
        
        # Step 4: Handle result
        if result["success"] and result["output"]:
            # Task completed successfully
            task = self.queue.get_task(task_id)
            pr_url = task.get("pr_url", "Unknown")
            
            self.notifier.send_completion_notification(task_id, pr_url, success=True)
            self.queue.complete_task(task_id, pr_url=pr_url)
            
            return task_id
        else:
            # Task failed, provide fallback
            print(f"❌ Task failed: {result.get('error')}")
            
            if result.get("fallback_triggered"):
                print("🔧 Providing manual fallback instructions...")
                self.notifier.send_manual_fallback(task_id, fallback_steps)
            
            self.queue.complete_task(task_id, error=result.get("error"))
            return task_id
    
    def _generate_fallback_steps(self, task_type: str, issue_url: str) -> list:
        """Generate manual fallback steps based on task type"""
        issue_id = issue_url.split("/")[-1]
        
        return [
            f"1. Visit issue: {issue_url}",
            "2. Fork repository to your account",
            "3. Clone your fork locally",
            "4. Create a new branch: git checkout -b fix-{issue_id}",
            "5. Make required changes",
            "6. Test your changes",
            "7. Commit: git add . && git commit -m 'fix: resolve issue #{issue_id}'",
            "8. Push: git push origin fix-{issue_id}",
            "9. Create Pull Request on GitHub",
            "10. Reference issue in PR description: Fixes #{issue_id}"
        ]
    
    def show_status(self):
        """Display current BS2.0 system status"""
        summary = self.reporter.generate_summary()
        
        print("\n📊 BS2.0 System Status")
        print("=" * 50)
        
        # Handle both task summary and status message formats
        if 'status' in summary and 'total_tasks' not in summary:
            # No tasks found
            print(f"Status: {summary['status']}")
            print("Use --create-doc-pr to create your first task")
        else:
            # Tasks available
            print(f"Total Tasks: {summary['total_tasks']}")
            print(f"✅ Completed: {summary['completed']}")
            print(f"🔄 In Progress: {summary['in_progress']}")
            print(f"❌ Failed: {summary['failed']}")
            print(f"⏳ Pending: {summary['pending']}")
            print("=" * 50 + "\n")
        
        return summary

def main():
    """Main entry point for BS2.0 orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BS2.0 Bounty Hunting System")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--create-doc-pr", action="store_true", 
                       help="Create documentation PR")
    parser.add_argument("--repo-url", type=str, help="Repository URL")
    parser.add_argument("--issue-url", type=str, help="Issue URL")
    parser.add_argument("--issue-id", type=str, help="Issue ID")
    
    args = parser.parse_args()
    
    orchestrator = BS2Orchestrator()
    
    if args.status:
        orchestrator.show_status()
    elif args.create_doc_pr:
        if not args.repo_url or not args.issue_url or not args.issue_id:
            print("❌ Error: --repo-url, --issue-url, and --issue-id are required for creating PR")
            sys.exit(1)
        
        orchestrator.create_documentation_pr(
            args.repo_url, args.issue_url, args.issue_id, {}
        )
    else:
        print("📋 BS2.0 Bounty Hunting System")
        print("Use --status to view system status")
        print("Use --create-doc-pr with appropriate arguments to create a documentation PR")

if __name__ == "__main__":
    main()