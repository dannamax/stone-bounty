#!/usr/bin/env python3
"""
Bounty Analyzer Module for BS2.0 Automated Bounty System
Analyzes bounty opportunities and assigns BS2.0 scores and priorities
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
import re

@dataclass
class Bounty:
    """Represents a bounty opportunity"""
    issue_number: str
    title: str
    description: str
    reward: str
    url: str
    complexity: str  # LOW, MODERATE, HIGH, VERY_HIGH
    risk: str        # LOW, MEDIUM, HIGH
    time_estimate: str  # 1h, 2h, 6h, 24h, 168h
    type: str        # documentation, bug_fix, feature, test, community
    status: str      # AVAILABLE, IN_PROGRESS, COMPLETED, SKIP
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

class BountyAnalyzer:
    """Analyzes bounty opportunities using BS2.0 scoring system"""
    
    def __init__(self):
        self.bs2_scoring_rules = {
            "complexity": {"LOW": 90, "MODERATE": 60, "HIGH": 45, "VERY_HIGH": 25},
            "risk": {"LOW": 85, "MEDIUM": 60, "HIGH": 30},
            "time_estimate": {"1h": 95, "2h": 80, "6h": 60, "24h": 45, "168h": 35}
        }
        
        self.skip_patterns = [
            r"large.*community.*campaign",
            r"massive.*community.*activity", 
            r"requires.*multiple.*merged.*prs",
            r"needs.*dex.*integration",
            r"requires.*large.*capital"
        ]
    
    def analyze_bounty(self, bounty: Bounty) -> BountyAnalysis:
        """Analyze a bounty and return BS2.0 analysis"""
        # Check if should skip
        if self._should_skip_bounty(bounty):
            return BountyAnalysis(
                bounty=bounty,
                bs2_score=0,
                priority="SKIP",
                recommended_action="Skip - too complex or requires external dependencies",
                estimated_success_rate=0.0
            )
        
        # Calculate BS2 score
        bs2_score = self._calculate_bs2_score(bounty)
        
        # Determine priority
        priority = self._determine_priority(bs2_score)
        
        # Generate recommendation
        recommended_action = self._generate_recommendation(bounty, priority)
        
        # Estimate success rate
        success_rate = self._estimate_success_rate(bs2_score, bounty.complexity, bounty.risk)
        
        return BountyAnalysis(
            bounty=bounty,
            bs2_score=bs2_score,
            priority=priority,
            recommended_action=recommended_action,
            estimated_success_rate=success_rate
        )
    
    def _should_skip_bounty(self, bounty: Bounty) -> bool:
        """Check if bounty should be skipped based on patterns"""
        combined_text = f"{bounty.title} {bounty.description}".lower()
        for pattern in self.skip_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True
        return False
    
    def _calculate_bs2_score(self, bounty: Bounty) -> int:
        """Calculate BS2.0 score based on complexity, risk, and time"""
        complexity_score = self.bs2_scoring_rules["complexity"].get(bounty.complexity, 30)
        risk_score = self.bs2_scoring_rules["risk"].get(bounty.risk, 30)
        time_score = self.bs2_scoring_rules["time_estimate"].get(bounty.time_estimate, 30)
        
        # Weighted average with emphasis on complexity
        weighted_score = (complexity_score * 0.5 + risk_score * 0.3 + time_score * 0.2)
        return int(weighted_score)
    
    def _determine_priority(self, score: int) -> str:
        """Determine priority based on BS2 score"""
        if score >= 75:
            return "HIGH"
        elif score >= 45:
            return "MEDIUM"
        elif score >= 30:
            return "LOW"
        else:
            return "SKIP"
    
    def _generate_recommendation(self, bounty: Bounty, priority: str, bs2_score: int = 0) -> str:
        """Generate action recommendation based on analysis"""
        if priority == "HIGH":
            return f"Immediate start - high score ({bs2_score}/100)"
        elif priority == "MEDIUM":
            return f"Start soon - moderate score ({bs2_score}/100)"
        elif priority == "LOW":
            return f"Consider if time permits - low score ({bs2_score}/100)"
        else:
            return "Skip - not suitable for automation"
    
    def _estimate_success_rate(self, score: int, complexity: str, risk: str) -> float:
        """Estimate success rate based on BS2 score and factors"""
        base_rate = score / 100.0
        
        # Adjust for complexity
        if complexity == "VERY_HIGH":
            base_rate *= 0.6
        elif complexity == "HIGH":
            base_rate *= 0.8
        
        # Adjust for risk
        if risk == "HIGH":
            base_rate *= 0.7
        elif risk == "MEDIUM":
            base_rate *= 0.9
        
        return min(base_rate, 0.95)  # Cap at 95%

    def parse_bounty_from_memory(self, memory_data: Dict[str, Any]) -> List[Bounty]:
        """Parse bounties from MEMORY.md structured data"""
        bounties = []
        
        # Parse high priority tasks
        high_priority = memory_data.get("新发现 Bounty 任务", {}).get("高优先级任务", {})
        for issue_id, task_data in high_priority.items():
            if isinstance(task_data, dict) and "AVAILABLE" in task_data.get("状态", ""):
                bounty = Bounty(
                    issue_number=issue_id.replace("#", ""),
                    title=task_data.get("标题", f"Bounty {issue_id}"),
                    description=task_data.get("描述", ""),
                    reward=task_data.get("赏金", "0 RTC"),
                    url=f"https://github.com/Scottcjn/rustchain-bounties/issues/{issue_id.replace('#', '')}",
                    complexity=self._map_complexity(task_data.get("复杂度", "MODERATE")),
                    risk=self._map_risk(task_data.get("风险等级", "MEDIUM")),
                    time_estimate=self._map_time_estimate(task_data.get("预计工时", "6 小时")),
                    type=self._determine_type(issue_id, task_data),
                    status="AVAILABLE",
                    requirements=[],
                    acceptance_criteria=[]
                )
                bounties.append(bounty)
        
        # Parse medium priority tasks
        medium_priority = memory_data.get("新发现 Bounty 任务", {}).get("中优先级任务", {})
        for issue_id, task_data in medium_priority.items():
            if isinstance(task_data, dict) and "AVAILABLE" in task_data.get("状态", ""):
                bounty = Bounty(
                    issue_number=issue_id.replace("#", ""),
                    title=task_data.get("标题", f"Bounty {issue_id}"),
                    description=task_data.get("描述", ""),
                    reward=task_data.get("赏金", "0 RTC"),
                    url=f"https://github.com/Scottcjn/rustchain-bounties/issues/{issue_id.replace('#', '')}",
                    complexity=self._map_complexity(task_data.get("复杂度", "LOW")),
                    risk=self._map_risk(task_data.get("风险等级", "MEDIUM")),
                    time_estimate=self._map_time_estimate(task_data.get("预计工时", "2 小时")),
                    type=self._determine_type(issue_id, task_data),
                    status="AVAILABLE",
                    requirements=[],
                    acceptance_criteria=[]
                )
                bounties.append(bounty)
        
        return bounties
    
    def _map_complexity(self, complexity_str: str) -> str:
        """Map complexity string to standard values"""
        complexity_map = {
            "低": "LOW", "LOW": "LOW",
            "中": "MODERATE", "MODERATE": "MODERATE",
            "高": "HIGH", "HIGH": "HIGH",
            "非常高": "VERY_HIGH", "VERY HIGH": "VERY_HIGH"
        }
        return complexity_map.get(complexity_str.upper(), "MODERATE")
    
    def _map_risk(self, risk_str: str) -> str:
        """Map risk string to standard values"""
        risk_map = {
            "低": "LOW", "LOW": "LOW",
            "中": "MEDIUM", "MEDIUM": "MEDIUM",
            "高": "HIGH", "HIGH": "HIGH"
        }
        return risk_map.get(risk_str.upper(), "MEDIUM")
    
    def _map_time_estimate(self, time_str: str) -> str:
        """Map time estimate string to standard values"""
        if "1 小时" in time_str or "1h" in time_str:
            return "1h"
        elif "2 小时" in time_str or "2h" in time_str:
            return "2h"
        elif "6 小时" in time_str or "6h" in time_str:
            return "6h"
        elif "24 小时" in time_str or "1 天" in time_str:
            return "24h"
        elif "168 小时" in time_str or "7 天" in time_str:
            return "168h"
        else:
            return "6h"
    
    def _determine_type(self, issue_id: str, task_data: Dict) -> str:
        """Determine bounty type based on issue ID and description"""
        title = task_data.get("标题", "").lower()
        desc = task_data.get("描述", "").lower()
        
        if "文档" in title or "documentation" in title or "guide" in title:
            return "documentation"
        elif "bug" in title or "修复" in title or "fix" in title:
            return "bug_fix"
        elif "测试" in title or "test" in title:
            return "test"
        elif "社区" in title or "community" in title or "friend" in title:
            return "community"
        else:
            return "feature"

if __name__ == "__main__":
    # Test the analyzer
    analyzer = BountyAnalyzer()
    
    # Test bounty
    test_bounty = Bounty(
        issue_number="167",
        title="Bring a Friend to Mine",
        description="Recommend friends to join RustChain mining",
        reward="10 RTC",
        url="https://github.com/Scottcjn/rustchain-bounties/issues/167",
        complexity="LOW",
        risk="MEDIUM", 
        time_estimate="1h",
        type="community",
        status="AVAILABLE",
        requirements=[],
        acceptance_criteria=[]
    )
    
    analysis = analyzer.analyze_bounty(test_bounty)
    print(f"Bounty Analysis:")
    print(f"  Issue: #{analysis.bounty.issue_number}")
    print(f"  BS2 Score: {analysis.bs2_score}/100")
    print(f"  Priority: {analysis.priority}")
    print(f"  Success Rate: {analysis.estimated_success_rate:.1%}")
    print(f"  Recommendation: {analysis.recommended_action}")