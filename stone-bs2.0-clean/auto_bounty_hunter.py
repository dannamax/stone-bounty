#!/usr/bin/env python3
"""
BS2.0 Automated Bounty Hunter - Main automation controller
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# Add BS2 system to path
bs2_path = Path(__file__).parent
sys.path.insert(0, str(bs2_path))

# Import BS2 components
from bounty_discovery import BountyDiscovery
from enhanced_bounty_analyzer import EnhancedBountyAnalyzer, BountyAnalysis
from automated_scheduler import AutomatedScheduler
from pr_generator import PRGenerator
from auto_config import AutoBountyConfig

class AutoBountyHunter:
    """Main automated bounty hunter controller"""
    
    def __init__(self, config_path: str = None):
        if config_path:
            self.config = AutoBountyConfig.load_from_file(config_path)
        else:
            self.config = AutoBountyConfig()
        
        self.discovery = BountyDiscovery("/home/admin/.openclaw/workspace")
        self.analyzer = EnhancedBountyAnalyzer()
        self.scheduler = AutomatedScheduler(self.config)
        self.pr_generator = PRGenerator()
    
    def run_automated_cycle(self):
        """Run a complete automated bounty hunting cycle"""
        print("🤖 Starting Automated Bounty Hunting Cycle...")
        
        # 1. Discover new bounties
        print("🔍 Discovering new bounties...")
        bounties = self.discovery.scan_bounties()
        print(f"   Found {len(bounties)} potential bounties")
        
        # 2. Analyze bounties
        print("📊 Analyzing bounties...")
        analyzed_bounties = []
        for bounty in bounties:
            analysis = self.analyzer.analyze_bounty(bounty)
            if analysis.bs2_score >= self.config.min_bs2_score:
                analyzed_bounties.append(analysis)
        
        print(f"   {len(analyzed_bounties)} bounties meet minimum score threshold")
        
        # 3. Sort by priority
        analyzed_bounties.sort(key=lambda x: x.bs2_score, reverse=True)
        
        # 4. Process top bounties
        bounties_to_process = analyzed_bounties[:self.config.max_bounties_per_cycle]
        print(f"   Processing top {len(bounties_to_process)} bounties")
        
        results = []
        for analysis in bounties_to_process:
            result = self._process_bounty(analysis)
            results.append(result)
        
        print("✅ Automated cycle completed!")
        return results
    
    def _process_bounty(self, analysis) -> Dict:
        """Process a single bounty"""
        bounty = analysis.bounty
        
        print(f"   Processing: {bounty.title} (Score: {analysis.bs2_score})")
        
        if self.config.dry_run_mode:
            print(f"   🧪 DRY RUN: Would process {bounty.url}")
            return {"status": "dry_run", "bounty": bounty.url, "score": analysis.bs2_score}
        
        # Generate PR content
        pr_content = self.pr_generator.generate_pr_for_bounty(bounty)
        
        # Create and submit PR (if auto PR is enabled)
        if self.config.auto_pr_enabled:
            pr_result = self._submit_pr(bounty, pr_content)
            return {"status": "pr_submitted", "bounty": bounty.url, "pr_url": pr_result}
        else:
            print(f"   ⏸️  Auto PR disabled, manual processing required")
            return {"status": "manual_required", "bounty": bounty.url, "score": analysis.score}
    
    def _submit_pr(self, bounty, pr_content) -> str:
        """Submit PR for bounty"""
        # This would integrate with GitHub API to create PR
        # For now, simulate the process
        print(f"   🚀 Submitting PR for {bounty.title}")
        # Extract repo from URL
        if "rustchain-bounties" in bounty.url:
            repo_name = "rustchain-bounties"
        elif "openclaw" in bounty.url:
            repo_name = "openclaw"
        else:
            repo_name = "unknown-repo"
        return f"https://github.com/dannamax/{repo_name}/pull/NEW"
    
    def get_current_status(self) -> Dict:
        """Get current automation status"""
        return {
            "config": self.config.__dict__,
            "last_run": "2026-02-28T14:30:00Z",
            "active_tasks": 0,
            "completed_cycles": 1
        }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BS2.0 Automated Bounty Hunter")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    if args.dry_run:
        config = AutoBountyConfig()
        config.dry_run_mode = True
        hunter = AutoBountyHunter()
        hunter.config = config
    elif args.config:
        hunter = AutoBountyHunter(args.config)
    else:
        hunter = AutoBountyHunter()
    
    if args.status:
        status = hunter.get_current_status()
        print(json.dumps(status, indent=2))
    else:
        results = hunter.run_automated_cycle()
        print(f"\nResults: {len(results)} bounties processed")

if __name__ == "__main__":
    main()