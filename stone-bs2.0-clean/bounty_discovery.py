#!/usr/bin/env python3
"""
Bounty Discovery Module - Automatically discover new bounty opportunities
"""

import json
import requests
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Bounty:
    """Represents a bounty opportunity"""
    id: str
    title: str
    url: str
    description: str
    reward: str
    complexity: str  # LOW, MODERATE, HIGH, VERY_HIGH
    risk: str        # LOW, MEDIUM, HIGH
    time_estimate: str  # 1h, 2h, 6h, 24h, 168h
    type: str        # documentation, bug_fix, feature, test, community
    status: str      # AVAILABLE, IN_PROGRESS, COMPLETED, SKIPPED
    repository: str
    created_at: str
    updated_at: str
    requirements: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)

@dataclass
class BountyAnalysis:
    """Analysis result for a bounty"""
    bounty: Bounty
    bs2_score: int
    priority: str    # HIGH, MEDIUM, LOW, SKIP
    recommended_action: str
    estimated_success_rate: float

class BountyDiscovery:
    """Discovers new bounty opportunities from various sources"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.bounty_sources = [
            {
                "name": "rustchain-bounties",
                "url": "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues",
                "labels": ["bounty"]
            },
            {
                "name": "openclaw",
                "url": "https://api.github.com/repos/openclaw/openclaw/issues", 
                "labels": ["bounty"]
            }
        ]
        self.bounty_cache_file = self.workspace_dir / "bs2_tasks" / "bounty_cache.json"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        cache_dir = self.workspace_dir / "bs2_tasks"
        cache_dir.mkdir(exist_ok=True)
    
    def scan_bounties(self) -> List[Bounty]:
        """Scan all configured sources for new bounty opportunities"""
        all_bounties = []
        
        for source in self.bounty_sources:
            try:
                bounties = self._fetch_from_github(source)
                all_bounties.extend(bounties)
                print(f"✅ Found {len(bounties)} bounties from {source['name']}")
            except Exception as e:
                print(f"❌ Error fetching from {source['name']}: {e}")
        
        # Cache the results
        self._cache_bounties(all_bounties)
        return all_bounties
    
    def _fetch_from_github(self, source: Dict) -> List[Bounty]:
        """Fetch bounties from GitHub API"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        params = {
            "state": "open",
            "labels": ",".join(source["labels"]),
            "per_page": 100
        }
        
        response = requests.get(source["url"], headers=headers, params=params)
        response.raise_for_status()
        
        issues = response.json()
        bounties = []
        
        for issue in issues:
            bounty = self._parse_issue_to_bounty(issue, source["name"])
            if bounty:
                bounties.append(bounty)
        
        return bounties
    
    def _parse_issue_to_bounty(self, issue: Dict, repository: str) -> Optional[Bounty]:
        """Parse GitHub issue to Bounty object"""
        title = issue["title"]
        body = issue.get("body", "")
        labels = [label["name"] for label in issue.get("labels", [])]
        
        # Extract reward from title or body
        reward = self._extract_reward(title, body)
        if not reward:
            return None
        
        # Determine bounty type and complexity
        bounty_type = self._determine_type(title, body, labels)
        complexity = self._estimate_complexity(title, body, labels)
        risk = self._estimate_risk(complexity, bounty_type)
        time_estimate = self._estimate_time(complexity)
        
        return Bounty(
            id=str(issue["number"]),
            title=title,
            url=issue["html_url"],
            description=body[:500] + "..." if len(body) > 500 else body,
            reward=reward,
            complexity=complexity,
            risk=risk,
            time_estimate=time_estimate,
            type=bounty_type,
            status="AVAILABLE",
            repository=repository,
            created_at=issue["created_at"],
            updated_at=issue["updated_at"]
        )
    
    def _extract_reward(self, title: str, body: str) -> Optional[str]:
        """Extract reward amount from title or body"""
        import re
        
        # Look for RTC amounts
        rtc_pattern = r'(\d+(?:-\d+)?)\s*RTC'
        usd_pattern = r'(\d+)\s*USD'
        
        rtc_match = re.search(rtc_pattern, title + " " + body, re.IGNORECASE)
        usd_match = re.search(usd_pattern, title + " " + body, re.IGNORECASE)
        
        if rtc_match:
            return f"{rtc_match.group(1)} RTC"
        elif usd_match:
            return f"{usd_match.group(1)} USD"
        else:
            return None
    
    def _determine_type(self, title: str, body: str, labels: List[str]) -> str:
        """Determine bounty type based on content"""
        title_lower = title.lower()
        body_lower = body.lower()
        
        if any(word in title_lower for word in ["doc", "document", "readme", "guide"]):
            return "documentation"
        elif any(word in title_lower for word in ["bug", "fix", "error", "issue"]):
            return "bug_fix"
        elif any(word in title_lower for word in ["feature", "implement", "add"]):
            return "feature"
        elif any(word in title_lower for word in ["test", "testing", "coverage"]):
            return "test"
        elif any(word in title_lower for word in ["friend", "share", "community", "social"]):
            return "community"
        else:
            return "feature"
    
    def _estimate_complexity(self, title: str, body: str, labels: List[str]) -> str:
        """Estimate complexity based on bounty description"""
        title_lower = title.lower()
        body_lower = body.lower()
        
        # Very High complexity indicators
        if any(word in title_lower for word in ["governance", "5000", "large", "major architecture"]):
            return "VERY_HIGH"
        # High complexity indicators  
        elif any(word in title_lower for word in ["7 day", "sustained", "hardware", "exotic"]):
            return "HIGH"
        # Low complexity indicators
        elif any(word in title_lower for word in ["quick", "simple", "easy", "test", "doc"]):
            return "LOW"
        else:
            return "MODERATE"
    
    def _estimate_risk(self, complexity: str, bounty_type: str) -> str:
        """Estimate risk based on complexity and type"""
        if complexity == "VERY_HIGH":
            return "HIGH"
        elif complexity == "HIGH":
            return "MEDIUM"
        elif bounty_type == "community":
            return "HIGH"  # Community tasks often have unclear requirements
        else:
            return "LOW"
    
    def _estimate_time(self, complexity: str) -> str:
        """Estimate time based on complexity"""
        time_map = {
            "LOW": "1h",
            "MODERATE": "6h", 
            "HIGH": "24h",
            "VERY_HIGH": "168h"
        }
        return time_map.get(complexity, "6h")
    
    def _cache_bounties(self, bounties: List[Bounty]):
        """Cache discovered bounties to file"""
        bounty_dicts = []
        for bounty in bounties:
            bounty_dict = bounty.__dict__.copy()
            bounty_dict["id"] = str(bounty_dict["id"])  # Ensure string
            bounty_dicts.append(bounty_dict)
        
        with open(self.bounty_cache_file, 'w') as f:
            json.dump(bounty_dicts, f, indent=2)
        
        print(f"💾 Cached {len(bounties)} bounties to {self.bounty_cache_file}")
    
    def load_cached_bounties(self) -> List[Bounty]:
        """Load cached bounties from file"""
        if not self.bounty_cache_file.exists():
            return []
        
        try:
            with open(self.bounty_cache_file, 'r') as f:
                bounty_dicts = json.load(f)
            
            bounties = []
            for bounty_dict in bounty_dicts:
                bounties.append(Bounty(**bounty_dict))
            
            print(f"📂 Loaded {len(bounties)} cached bounties")
            return bounties
        except Exception as e:
            print(f"❌ Error loading cached bounties: {e}")
            return []

if __name__ == "__main__":
    discovery = BountyDiscovery()
    bounties = discovery.scan_bounties()
    print(f"\n📊 Total bounties discovered: {len(bounties)}")
    
    # Print summary
    for bounty in bounties[:5]:  # Show first 5
        print(f"- {bounty.title} ({bounty.reward}) - {bounty.repository}#{bounty.id}")