#!/usr/bin/env python3
"""
BS2.0 Task Queue System - Asynchronous task processing with progress reporting
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class BS2TaskQueue:
    """Manages asynchronous BS2.0 bounty tasks with progress tracking"""
    
    def __init__(self, base_dir: str = "/home/admin/.openclaw/workspace"):
        self.base_dir = Path(base_dir)
        self.task_dir = self.base_dir / "bs2_tasks"
        self.state_file = self.task_dir / "task_states.json"
        self.task_dir.mkdir(parents=True, exist_ok=True)
        
    def create_task(self, task_name: str, task_type: str, 
                    issue_url: str, bounty_amount: str) -> str:
        """Create a new task and return task ID"""
        task_id = f"{task_type}_{int(time.time())}"
        
        task = {
            "task_id": task_id,
            "task_name": task_name,
            "task_type": task_type,
            "issue_url": issue_url,
            "bounty_amount": bounty_amount,
            "status": "pending",
            "progress": 0,
            "steps_completed": [],
            "current_step": "initialized",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "log_file": str(self.task_dir / f"{task_id}.log")
        }
        
        self._save_task(task)
        return task_id
    
    def update_progress(self, task_id: str, step: str, 
                       progress_percent: int, status: str = "in_progress"):
        """Update task progress and save state"""
        task = self.get_task(task_id)
        if not task:
            return False
            
        task["progress"] = progress_percent
        task["current_step"] = step
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        task["steps_completed"].append({
            "step": step,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_task(task)
        self._log(task_id, f"Progress: {progress_percent}% - {step}")
        return True
    
    def complete_task(self, task_id: str, pr_url: str = None, 
                     error: str = None):
        """Mark task as completed or failed"""
        task = self.get_task(task_id)
        if not task:
            return False
            
        task["progress"] = 100
        task["updated_at"] = datetime.now().isoformat()
        
        if error:
            task["status"] = "failed"
            task["error"] = error
            self._log(task_id, f"FAILED: {error}")
        else:
            task["status"] = "completed"
            task["pr_url"] = pr_url
            self._log(task_id, f"COMPLETED: PR created at {pr_url}")
        
        self._save_task(task)
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Retrieve task by ID"""
        tasks = self._load_all_tasks()
        return tasks.get(task_id)
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active (pending or in_progress) tasks"""
        tasks = self._load_all_tasks()
        return [t for t in tasks.values() if t["status"] in ["pending", "in_progress"]]
    
    def _save_task(self, task: Dict):
        """Save task to state file"""
        tasks = self._load_all_tasks()
        tasks[task["task_id"]] = task
        self._save_all_tasks(tasks)
    
    def _load_all_tasks(self) -> Dict:
        """Load all tasks from state file"""
        if not self.state_file.exists():
            return {}
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _save_all_tasks(self, tasks: Dict):
        """Save all tasks to state file"""
        with open(self.state_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def _log(self, task_id: str, message: str):
        """Log message to task-specific log file"""
        task = self.get_task(task_id)
        if not task:
            return
            
        log_file = Path(task["log_file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {message}\n")

class BS2TaskExecutor:
    """Executes BS2.0 tasks asynchronously"""
    
    def __init__(self, queue: BS2TaskQueue):
        self.queue = queue
    
    def execute_task(self, task_id: str, steps: List[Dict]) -> bool:
        """Execute a series of steps for a task"""
        self.queue.update_progress(task_id, "Starting task execution", 5, "in_progress")
        
        for i, step in enumerate(steps):
            step_name = step["name"]
            step_command = step["command"]
            step_weight = step.get("weight", 1)
            
            try:
                self.queue.update_progress(task_id, f"Executing: {step_name}", 
                                         10 + (i * 80 // len(steps)))
                
                result = subprocess.run(
                    step_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout per step
                )
                
                if result.returncode != 0:
                    error_msg = f"Step '{step_name}' failed: {result.stderr}"
                    self.queue.complete_task(task_id, error=error_msg)
                    return False
                
            except subprocess.TimeoutExpired:
                error_msg = f"Step '{step_name}' timed out after 60 seconds"
                self.queue.complete_task(task_id, error=error_msg)
                return False
            except Exception as e:
                error_msg = f"Step '{step_name}' raised exception: {str(e)}"
                self.queue.complete_task(task_id, error=error_msg)
                return False
        
        self.queue.update_progress(task_id, "Task completed successfully", 95)
        return True

if __name__ == "__main__":
    # Test the task queue system
    queue = BS2TaskQueue()
    
    # Create a test task
    task_id = queue.create_task(
        task_name="Test Documentation PR",
        task_type="documentation",
        issue_url="https://github.com/Scottcjn/Rustchain/issues/304",
        bounty_amount="5 RTC"
    )
    
    print(f"✅ Task created: {task_id}")
    print(f"📊 Task details: {queue.get_task(task_id)}")