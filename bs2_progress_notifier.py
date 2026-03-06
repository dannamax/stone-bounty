#!/usr/bin/env python3
"""
BS2.0 Progress Notifier - Real-time progress updates and alerts
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class BS2ProgressNotifier:
    """Sends real-time progress updates for BS2.0 tasks"""
    
    def __init__(self, base_dir: str = "/home/admin/.openclaw/workspace"):
        self.base_dir = Path(base_dir)
        self.notification_log = self.base_dir / "bs2_tasks" / "notifications.json"
        self.notification_log.parent.mkdir(parents=True, exist_ok=True)
    
    def send_progress_update(self, task_id: str, message: str, 
                           progress_percent: int, status: str = "in_progress"):
        """Send progress update to user"""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "progress",
            "message": message,
            "progress": progress_percent,
            "status": status
        }
        
        self._save_notification(notification)
        self._display_to_user(notification)
        
        return notification
    
    def send_completion_notification(self, task_id: str, pr_url: str, 
                                    success: bool = True):
        """Send task completion notification"""
        if success:
            message = f"✅ Task completed successfully! PR: {pr_url}"
            emoji = "🎉"
        else:
            message = f"❌ Task failed. See logs for details."
            emoji = "💥"
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "completion",
            "emoji": emoji,
            "message": message,
            "status": "completed" if success else "failed",
            "pr_url": pr_url if success else None
        }
        
        self._save_notification(notification)
        self._display_to_user(notification)
        
        return notification
    
    def send_alert(self, task_id: str, alert_type: str, message: str):
        """Send alert for important events"""
        emoji_map = {
            "maintainer_comment": "💬",
            "pr_merged": "✅",
            "pr_closed": "❌",
            "timeout": "⏰",
            "conflict": "⚠️",
            "error": "🚨"
        }
        
        emoji = emoji_map.get(alert_type, "ℹ️")
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "alert",
            "alert_type": alert_type,
            "emoji": emoji,
            "message": message
        }
        
        self._save_notification(notification)
        self._display_to_user(notification)
        
        return notification
    
    def send_manual_fallback(self, task_id: str, manual_steps: List[str]):
        """Send manual fallback instructions when automation fails"""
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(manual_steps)])
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "type": "fallback",
            "emoji": "🔧",
            "message": "Automated workflow encountered an issue. Manual steps required:",
            "manual_steps": manual_steps
        }
        
        self._save_notification(notification)
        self._display_to_user(notification)
        
        return notification
    
    def _save_notification(self, notification: Dict):
        """Save notification to log file"""
        notifications = self._load_notifications()
        notifications.append(notification)
        
        # Keep only last 100 notifications
        notifications = notifications[-100:]
        
        with open(self.notification_log, 'w') as f:
            json.dump(notifications, f, indent=2)
    
    def _load_notifications(self) -> List[Dict]:
        """Load notifications from log file"""
        if not self.notification_log.exists():
            return []
        with open(self.notification_log, 'r') as f:
            return json.load(f)
    
    def _display_to_user(self, notification: Dict):
        """Display notification to user in a formatted way"""
        emoji = notification.get("emoji", "📊")
        message = notification.get("message", "")
        task_id = notification.get("task_id", "")
        progress = notification.get("progress")
        
        # Format progress bar
        if progress:
            progress_bar = self._create_progress_bar(progress)
            output = f"{emoji} [{task_id}] {progress_bar} {progress}%\n{message}"
        else:
            output = f"{emoji} [{task_id}] {message}"
        
        # Print to console (would be replaced with actual messaging in production)
        print(f"\n{output}\n")
    
    def _create_progress_bar(self, percent: int, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(width * percent / 100)
        empty = width - filled
        return "[" + "█" * filled + "░" * empty + "]"

class BS2StatusReporter:
    """Generates status reports for BS2.0 system"""
    
    def __init__(self, base_dir: str = "/home/admin/.openclaw/workspace"):
        self.base_dir = Path(base_dir)
        self.state_file = self.base_dir / "bs2_tasks" / "task_states.json"
    
    def generate_summary(self) -> Dict:
        """Generate summary of all BS2.0 tasks"""
        if not self.state_file.exists():
            return {"status": "No tasks found"}
        
        with open(self.state_file, 'r') as f:
            tasks = json.load(f)
        
        summary = {
            "total_tasks": len(tasks),
            "completed": sum(1 for t in tasks.values() if t["status"] == "completed"),
            "in_progress": sum(1 for t in tasks.values() if t["status"] == "in_progress"),
            "failed": sum(1 for t in tasks.values() if t["status"] == "failed"),
            "pending": sum(1 for t in tasks.values() if t["status"] == "pending"),
            "success_rate": self._calculate_success_rate(tasks),
            "total_bounty": self._calculate_total_bounty(tasks),
            "tasks": list(tasks.values())
        }
        
        return summary
    
    def _calculate_success_rate(self, tasks: Dict) -> float:
        """Calculate success rate of completed tasks"""
        completed = [t for t in tasks.values() if t["status"] in ["completed", "failed"]]
        if not completed:
            return 0.0
        
        successful = sum(1 for t in completed if t["status"] == "completed")
        return round(successful / len(completed) * 100, 2)
    
    def _calculate_total_bounty(self, tasks: Dict) -> str:
        """Calculate total bounty from completed tasks"""
        completed = [t for t in tasks.values() if t["status"] == "completed"]
        
        rtc_bounties = [t["bounty_amount"] for t in completed if "RTC" in t["bounty_amount"]]
        usd_bounties = [t["bounty_amount"] for t in completed if "USD" in t["bounty_amount"]]
        
        return f"{sum(rtc_bounties)} RTC + {sum(usd_bounties)} USD"

if __name__ == "__main__":
    # Test the progress notifier
    notifier = BS2ProgressNotifier()
    
    # Test progress updates
    task_id = "test_task_001"
    notifier.send_progress_update(task_id, "Cloning repository...", 25)
    notifier.send_progress_update(task_id, "Applying changes...", 50)
    notifier.send_progress_update(task_id, "Pushing to fork...", 75)
    
    # Test completion notification
    notifier.send_completion_notification(task_id, "https://github.com/example/pr/1", success=True)
    
    # Test manual fallback
    notifier.send_manual_fallback(task_id, [
        "Step 1: Visit GitHub repository",
        "Step 2: Create new branch",
        "Step 3: Edit files manually",
        "Step 4: Create PR"
    ])