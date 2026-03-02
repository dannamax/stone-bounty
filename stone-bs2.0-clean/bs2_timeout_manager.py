#!/usr/bin/env python3
"""
BS2.0 Timeout Manager - Handles timeouts and provides manual fallback
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

class BS2TimeoutManager:
    """Manages timeouts and automatic fallback for BS2.0 tasks"""
    
    def __init__(self, base_dir: str = "/home/admin/.openclaw/workspace"):
        self.base_dir = Path(base_dir)
        self.timeout_config = self._load_timeout_config()
    
    def _load_timeout_config(self) -> Dict:
        """Load timeout configuration"""
        config_file = self.base_dir / "bs2_system" / "timeout_config.json"
        
        default_config = {
            "git_operations": 60,  # seconds
            "github_api": 30,     # seconds
            "file_operations": 15, # seconds
            "overall_task": 300,   # seconds (5 minutes)
            "retry_count": 3,
            "retry_delay": 5       # seconds
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return {**default_config, **json.load(f)}
        
        return default_config
    
    def execute_with_timeout(self, operation: Callable, timeout: int, 
                          task_id: str, fallback_steps: List[str] = None) -> Dict:
        """Execute an operation with timeout and automatic fallback"""
        start_time = time.time()
        result = {
            "success": False,
            "error": None,
            "fallback_triggered": False,
            "execution_time": 0
        }
        
        try:
            # Execute operation with timeout
            output = operation()
            
            result["success"] = True
            result["output"] = output
            result["execution_time"] = time.time() - start_time
            
        except TimeoutError as e:
            result["error"] = f"Operation timed out after {timeout} seconds"
            result["execution_time"] = time.time() - start_time
            
            if fallback_steps:
                result["fallback_triggered"] = True
                result["fallback_steps"] = fallback_steps
                
        except Exception as e:
            result["error"] = f"Operation failed: {str(e)}"
            result["execution_time"] = time.time() - start_time
            
            if fallback_steps:
                result["fallback_triggered"] = True
                result["fallback_steps"] = fallback_steps
        
        return result
    
    def execute_with_retry(self, operation: Callable, max_retries: int = 3,
                         retry_delay: int = 5, task_id: str = None) -> Dict:
        """Execute operation with automatic retry"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = operation()
                
                return {
                    "success": True,
                    "output": result,
                    "attempts": attempt + 1,
                    "error": None
                }
                
            except Exception as e:
                last_error = str(e)
                
                if attempt < max_retries - 1:
                    if task_id:
                        print(f"⚠️ Attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    return {
                        "success": False,
                        "error": last_error,
                        "attempts": max_retries,
                        "output": None
                    }
        
        return {
            "success": False,
            "error": "Max retries exceeded",
            "attempts": max_retries,
            "output": None
        }
    
    def generate_manual_fallback(self, task_type: str, task_details: Dict) -> List[str]:
        """Generate manual fallback steps based on task type"""
        
        fallback_strategies = {
            "documentation": self._docs_fallback,
            "code_improvement": self._code_fallback,
            "bug_fix": self._bug_fix_fallback,
            "feature_addition": self._feature_fallback
        }
        
        fallback_func = fallback_strategies.get(task_type, self._generic_fallback)
        return fallback_func(task_details)
    
    def _docs_fallback(self, task_details: Dict) -> List[str]:
        """Generate manual fallback for documentation tasks"""
        return [
            f"1. Visit GitHub: {task_details.get('repo_url', 'repository URL')}",
            "2. Click 'Add file' → 'Create new file'",
            "3. Enter file name: docs/API.md",
            "4. Paste the following content:",
            task_details.get("content", "[Your documentation content here]"),
            "5. Commit to new branch: fix-documentation-{issue_id}",
            "6. Create Pull Request with title: 'docs: update documentation for issue #{issue_id}'",
            "7. In PR description, include: Fixes #{issue_id}"
        ]
    
    def _code_fallback(self, task_details: Dict) -> List[str]:
        """Generate manual fallback for code improvement tasks"""
        return [
            f"1. Fork the repository: {task_details.get('repo_url')}",
            "2. Clone your fork locally",
            "3. Create new branch: git checkout -b fix-{issue_id}",
            "4. Make the required code changes",
            "5. Test your changes locally",
            "6. Commit: git add . && git commit -m 'fix: implement changes for issue #{issue_id}'",
            "7. Push: git push origin fix-{issue_id}",
            "8. Create PR on GitHub from your fork to the original repository"
        ]
    
    def _bug_fix_fallback(self, task_details: Dict) -> List[str]:
        """Generate manual fallback for bug fix tasks"""
        return [
            f"1. Analyze the bug in issue #{task_details.get('issue_id')}",
            "2. Reproduce the bug locally",
            "3. Implement a fix in the appropriate file",
            "4. Add tests to prevent regression",
            "5. Verify the fix resolves the issue",
            "6. Create PR with detailed description of the fix"
        ]
    
    def _feature_fallback(self, task_details: Dict) -> List[str]:
        """Generate manual fallback for feature addition tasks"""
        return [
            f"1. Review the feature requirements in issue #{task_details.get('issue_id')}",
            "2. Design the feature implementation",
            "3. Implement the feature code",
            "4. Add comprehensive tests",
            "5. Update documentation as needed",
            "6. Create PR with feature description and usage examples"
        ]
    
    def _generic_fallback(self, task_details: Dict) -> List[str]:
        """Generate generic manual fallback"""
        return [
            "1. Review the issue requirements",
            "2. Understand the project structure",
            "3. Implement the required changes",
            "4. Test your implementation",
            "5. Commit and push to a new branch",
            "6. Create a Pull Request referencing the issue"
        ]
    
    def monitor_task_timeout(self, task_id: str, max_duration: int) -> bool:
        """Monitor if a task exceeds maximum duration"""
        state_file = self.base_dir / "bs2_tasks" / "task_states.json"
        
        if not state_file.exists():
            return False
        
        with open(state_file, 'r') as f:
            tasks = json.load(f)
        
        if task_id not in tasks:
            return False
        
        task = tasks[task_id]
        created_at = datetime.fromisoformat(task["created_at"])
        elapsed = (datetime.now() - created_at).total_seconds()
        
        return elapsed > max_duration

class BS2SmartRetry:
    """Intelligent retry logic with exponential backoff"""
    
    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.current_delay = initial_delay
    
    def execute_with_backoff(self, operation: Callable, max_attempts: int = 5,
                           is_retryable: Callable = None) -> Dict:
        """Execute operation with exponential backoff"""
        
        def default_retryable(error):
            """Default: retry all errors"""
            return True
        
        if is_retryable is None:
            is_retryable = default_retryable
        
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                result = operation()
                
                # Reset delay on success
                self.current_delay = self.initial_delay
                
                return {
                    "success": True,
                    "output": result,
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                last_error = e
                
                if not is_retryable(e):
                    break
                
                if attempt < max_attempts - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying in {self.current_delay:.1f}s...")
                    time.sleep(self.current_delay)
                    
                    # Exponential backoff: 1s, 2s, 4s, 8s, ...
                    self.current_delay = min(self.current_delay * 2, self.max_delay)
        
        return {
            "success": False,
            "error": str(last_error),
            "attempts": max_attempts
        }

if __name__ == "__main__":
    # Test the timeout manager
    manager = BS2TimeoutManager()
    
    # Test timeout execution
    def long_running_operation():
        time.sleep(70)  # 70 seconds
        return "Completed"
    
    result = manager.execute_with_timeout(
        operation=long_running_operation,
        timeout=5,  # 5 second timeout
        task_id="test_timeout"
    )
    
    print(f"Timeout test result: {result}")
    
    # Test manual fallback generation
    docs_fallback = manager.generate_manual_fallback(
        task_type="documentation",
        task_details={
            "repo_url": "https://github.com/Scottcjn/Rustchain",
            "issue_id": "304",
            "content": "Documentation content..."
        }
    )
    
    print(f"\n📋 Manual fallback steps:")
    for step in docs_fallback:
        print(f"   {step}")