#!/usr/bin/env python3
"""
BS2.0 Monitor Module - Integrates bounty hunter skill's monitoring capabilities
"""

import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
import http.client

# Import from agent_bounty_hunter
from pathlib import Path
import sys

# Add the scripts directory to path to import agent_bounty_hunter functions
scripts_dir = Path("/home/admin/.openclaw/workspace/external_storage/rustchain-bounties-311/scripts")
if scripts_dir.exists():
    sys.path.insert(0, str(scripts_dir))

try:
    from agent_bounty_hunter import (
        gh_get_safe, payout_signal_from_comments, 
        classify_payout_action, discover_monitor_targets,
        monitor_targets
    )
except ImportError:
    # Fallback implementation if agent_bounty_hunter is not available
    def gh_get_safe(path: str, token: str = "", fallback: Any = None) -> Any:
        return fallback
    
    def payout_signal_from_comments(comments: List[Dict[str, Any]]) -> str:
        return "none"
    
    def classify_payout_action(merged: bool, pr_state: str, issue_state: str, payout_signal: str) -> str:
        return "wait_for_review"
    
    def discover_monitor_targets(owner: str, repo: str, handle: str, token: str = "", limit: int = 200) -> List[Dict[str, Any]]:
        return []
    
    def monitor_targets(targets: List[Dict[str, Any]], token: str = "") -> List[Dict[str, Any]]:
        return []

@dataclass
class MonitorResult:
    """Represents a monitoring result"""
    label: str
    issue_url: str
    pr_url: str
    issue_state: str
    pr_state: str
    merged: bool
    payout_signal: str
    payout_action: str

class BS2Monitor:
    """BS2.0 Monitor with bounty hunter skill integration"""
    
    def __init__(self, github_token: str = "", github_username: str = "dannamax"):
        self.token = github_token
        self.github_username = github_username
    
    def monitor_submissions(self, owner: str = "Scottcjn", repo: str = "rustchain-bounties") -> List[MonitorResult]:
        """Monitor all submissions for the given repository and user"""
        try:
            # Discover monitoring targets from claimant comments
            targets = discover_monitor_targets(
                owner=owner,
                repo=repo,
                handle=self.github_username,
                token=self.token,
                limit=200
            )
            
            if not targets:
                print("No monitoring targets found")
                return []
            
            # Monitor the targets
            monitor_results = monitor_targets(targets, token=self.token)
            
            # Convert to MonitorResult objects
            results = []
            for result in monitor_results:
                monitor_result = MonitorResult(
                    label=result.get("label", ""),
                    issue_url=result.get("issue", ""),
                    pr_url=result.get("pr", ""),
                    issue_state=result.get("issue_state", ""),
                    pr_state=result.get("pr_state", ""),
                    merged=result.get("merged", False),
                    payout_signal=result.get("payout_signal", ""),
                    payout_action=result.get("payout_action", "")
                )
                results.append(monitor_result)
            
            return results
            
        except Exception as e:
            print(f"Error monitoring submissions: {e}")
            return []
    
    def get_payout_recommendations(self, monitor_results: List[MonitorResult]) -> Dict[str, List[MonitorResult]]:
        """Get recommendations based on payout actions"""
        recommendations = {
            "request_payout": [],
            "wait_payout_queue": [],
            "address_review": [],
            "check_followup": [],
            "verify_closure": [],
            "complete": [],
            "wait_for_review": []
        }
        
        for result in monitor_results:
            action = result.payout_action
            if action in recommendations:
                recommendations[action].append(result)
            else:
                recommendations["wait_for_review"].append(result)
        
        return recommendations
    
    def print_monitor_report(self, monitor_results: List[MonitorResult]):
        """Print a formatted monitor report"""
        if not monitor_results:
            print("📊 No submissions to monitor")
            return
        
        print(f"📊 Monitoring {len(monitor_results)} submissions")
        print("=" * 80)
        
        recommendations = self.get_payout_recommendations(monitor_results)
        
        for action, results in recommendations.items():
            if results:
                print(f"\n{self._get_action_emoji(action)} {action.replace('_', ' ').title()}: {len(results)} submission(s)")
                for result in results:
                    print(f"  • {result.label}")
                    print(f"    Issue: {result.issue_url}")
                    if result.pr_url:
                        print(f"    PR: {result.pr_url}")
        
        print("\n" + "=" * 80)
    
    def _get_action_emoji(self, action: str) -> str:
        """Get emoji for action type"""
        emojis = {
            "request_payout": "💰",
            "wait_payout_queue": "⏳",
            "address_review": "📝",
            "check_followup": "🔍",
            "verify_closure": "✅",
            "complete": "🎉",
            "wait_for_review": "👀"
        }
        return emojis.get(action, "❓")

if __name__ == "__main__":
    # Test the monitor
    monitor = BS2Monitor(github_username="dannamax")
    results = monitor.monitor_submissions()
    monitor.print_monitor_report(results)