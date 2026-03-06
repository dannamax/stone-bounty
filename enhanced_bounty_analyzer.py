#!/usr/bin/env python3
"""
Enhanced Bounty Analyzer Module for BS2.0 Automated Bounty System
Integrates bounty hunter skill's reward parsing and analysis capabilities
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

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
    reward_rtc: float = 0.0
    reward_usd: float = 0.0
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
    capability_fit: float = 0.0

class EnhancedBountyAnalyzer:
    """Enhanced bounty analyzer with bounty hunter skill integration"""
    
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
        
        # Load historical projects blocklist
        self.historical_blocklist = self._load_historical_blocklist()
        
        # RTC to USD reference rate
        self.RTC_USD_REF = 0.10
    
    def analyze_bounty(self, bounty: Bounty) -> BountyAnalysis:
        """Analyze a bounty and return enhanced BS2.0 analysis"""
        # Parse reward using bounty hunter skill logic
        reward_rtc, reward_usd = self._parse_reward(bounty.description, bounty.title)
        bounty.reward_rtc = reward_rtc
        bounty.reward_usd = reward_usd
        
        # Estimate difficulty using bounty hunter skill logic
        difficulty = self._estimate_difficulty(bounty.title, bounty.description)
        bounty.complexity = difficulty.upper()
        
        # Calculate capability fit
        capability_fit = self._capability_fit(bounty.title, bounty.description)
        
        # Check if should skip
        if self._should_skip_bounty(bounty):
            return BountyAnalysis(
                bounty=bounty,
                bs2_score=0,
                priority="SKIP",
                recommended_action="Skip - too complex or requires external dependencies",
                estimated_success_rate=0.0,
                capability_fit=capability_fit
            )
        
        # Calculate enhanced BS2 score
        bs2_score = self._calculate_enhanced_bs2_score(bounty, capability_fit)
        
        # Determine priority
        priority = self._determine_priority(bs2_score)
        
        # Generate recommendation
        recommended_action = self._generate_recommendation(bounty, priority, bs2_score)
        
        # Estimate success rate
        success_rate = self._estimate_success_rate(bs2_score, bounty.complexity, bounty.risk, capability_fit)
        
        return BountyAnalysis(
            bounty=bounty,
            bs2_score=bs2_score,
            priority=priority,
            recommended_action=recommended_action,
            estimated_success_rate=success_rate,
            capability_fit=capability_fit
        )
    
    def _should_skip_bounty(self, bounty: Bounty) -> bool:
        """Check if bounty should be skipped based on patterns"""
        combined_text = f"{bounty.title} {bounty.description}".lower()
        for pattern in self.skip_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True
        return False
    
    def _calculate_enhanced_bs2_score(self, bounty: Bounty, capability_fit: float) -> int:
        """Calculate enhanced BS2.0 score with capability fit"""
        complexity_score = self.bs2_scoring_rules["complexity"].get(bounty.complexity, 30)
        risk_score = self.bs2_scoring_rules["risk"].get(bounty.risk, 30)
        time_score = self.bs2_scoring_rules["time_estimate"].get(bounty.time_estimate, 30)
        fit_score = int(capability_fit * 100)
        
        # Enhanced weighted average
        weighted_score = (complexity_score * 0.3 + risk_score * 0.2 + 
                         time_score * 0.2 + fit_score * 0.3)
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
    
    def _generate_recommendation(self, bounty: Bounty, priority: str, bs2_score: int) -> str:
        """Generate action recommendation based on analysis"""
        if priority == "HIGH":
            return f"Immediate start - high score ({bs2_score}/100)"
        elif priority == "MEDIUM":
            return f"Start soon - moderate score ({bs2_score}/100)"
        elif priority == "LOW":
            return f"Consider if time permits - low score ({bs2_score}/100)"
        else:
            return "Skip - not suitable for automation"
    
    def _estimate_success_rate(self, score: int, complexity: str, risk: str, capability_fit: float) -> float:
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
        
        # Adjust for capability fit
        base_rate *= (0.5 + capability_fit * 0.5)
        
        return min(base_rate, 0.95)  # Cap at 95%
    
    # Bounty Hunter Skill Integration Functions
    
    def _pick(self, values: List[float], default: float = 0.0) -> float:
        """Pick the maximum value from a list"""
        return max(values) if values else default

    def _suffix_multiplier(self, suffix: str) -> float:
        """Get multiplier for k/m suffixes"""
        s = (suffix or "").lower()
        if s == "k":
            return 1000.0
        if s == "m":
            return 1_000_000.0
        return 1.0

    def _extract_amounts(self, text: str, suffix_pattern: str) -> List[float]:
        """Extract amounts with suffix patterns"""
        values: List[float] = []
        num_token_re = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)([km])?\b", flags=re.IGNORECASE)
        for raw, suffix in re.findall(rf"{num_token_re.pattern}\s*{suffix_pattern}", text, flags=re.IGNORECASE):
            value = float(raw.replace(",", "")) * self._suffix_multiplier(suffix)
            values.append(value)
        return values

    def _extract_usd_amounts(self, text: str) -> List[float]:
        """Extract USD amounts"""
        values: List[float] = []
        num_token_re = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)([km])?\b", flags=re.IGNORECASE)
        for raw, suffix in re.findall(rf"\$\s*{num_token_re.pattern}", text, flags=re.IGNORECASE):
            value = float(raw.replace(",", "")) * self._suffix_multiplier(suffix)
            values.append(value)
        return values

    def _parse_reward(self, body: str, title: str) -> Tuple[float, float]:
        """Parse reward amounts from title and body (bounty hunter skill logic)"""
        text = f"{title}\n{body or ''}"

        # Prefer explicit title declaration, e.g. "(75 RTC)" / "($200)".
        title_rtc = self._extract_amounts(title or "", r"RTC(?:\)|\b)") if "pool" not in (title or "").lower() else []
        title_usd = self._extract_usd_amounts(title or "")

        reward_rtc = self._pick(title_rtc, 0.0)
        reward_usd = self._pick(title_usd, 0.0)

        # Fallback to body/title line cues; avoid "pool/prize pool" overestimation.
        if reward_rtc == 0.0 and reward_usd == 0.0:
            rtc_values: List[float] = []
            usd_values: List[float] = []
            for line in text.splitlines():
                low = line.lower()
                if "pool" in low:
                    continue
                if any(k in low for k in ("reward", "bounty", "earn", "payout", "prize")):
                    rtc_values.extend(self._extract_amounts(line, r"RTC\b"))
                    usd_values.extend(self._extract_usd_amounts(line))
            reward_rtc = self._pick(rtc_values, 0.0)
            reward_usd = self._pick(usd_values, 0.0)

        # Pool-based bounty programs often represent shared budgets, not per-task payout.
        if reward_rtc == 0.0 and reward_usd == 0.0 and "pool" in (title or "").lower():
            return 0.0, 0.0

        # Last resort generic parse.
        if reward_rtc == 0.0 and reward_usd == 0.0:
            reward_rtc = self._pick(self._extract_amounts(text, r"RTC\b"), 0.0)
            reward_usd = self._pick(self._extract_usd_amounts(text), 0.0)
            # If only pool-like language exists, treat as unknown instead of overestimating.
            if "pool" in text.lower() and not re.search(r"(?i)\b(reward|earn|payout)\b", text):
                reward_rtc = 0.0
                reward_usd = 0.0

        if reward_usd == 0 and reward_rtc > 0:
            reward_usd = reward_rtc * self.RTC_USD_REF
        if reward_rtc == 0 and reward_usd > 0:
            reward_rtc = reward_usd / self.RTC_USD_REF

        return reward_rtc, reward_usd

    def _estimate_difficulty(self, title: str, body: str) -> str:
        """Estimate difficulty using bounty hunter skill logic"""
        text = f"{title}\n{body}".lower()
        hard_terms = ["critical", "security", "red team", "hardening", "consensus", "major", "1000", "$1000"]
        mid_terms = ["standard", "dashboard", "tool", "api", "integration", "export"]

        if any(t in text for t in hard_terms):
            return "high"
        if any(t in text for t in mid_terms):
            return "medium"
        return "low"

    def _capability_fit(self, title: str, body: str) -> float:
        """Calculate capability fit score (bounty hunter skill logic)"""
        text = f"{title}\n{body}".lower()
        plus = [
            "documentation",
            "docs",
            "readme",
            "seo",
            "tutorial",
            "python",
            "script",
            "bot",
            "audit",
            "review",
            "markdown",
        ]
        minus = [
            "real hardware",
            "3d",
            "webgl",
            "dos",
            "sparc",
            "windows 3.1",
            "physical",
        ]

        score = 0.5
        for p in plus:
            if p in text:
                score += 0.06
        for m in minus:
            if m in text:
                score -= 0.08
        return max(0.0, min(1.0, score))

    def rank_score(self, reward_usd: float, diff: str, fit: float) -> float:
        """Calculate rank score (bounty hunter skill logic)"""
        diff_penalty = {"low": 0.0, "medium": 0.8, "high": 1.6}[diff]
        return round((reward_usd / 25.0) + (fit * 3.0) - diff_penalty, 3)

if __name__ == "__main__":
    # Test the enhanced analyzer
    analyzer = EnhancedBountyAnalyzer()
    
    # Test bounty
    test_bounty = Bounty(
        issue_number="167",
        title="Bring a Friend to Mine",
        description="Recommend friends to join RustChain mining and earn rewards",
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
    print(f"Enhanced Bounty Analysis:")
    print(f"  Issue: #{analysis.bounty.issue_number}")
    print(f"  Reward: {analysis.bounty.reward_rtc} RTC (${analysis.bounty.reward_usd:.2f})")
    print(f"  Complexity: {analysis.bounty.complexity}")
    print(f"  Capability Fit: {analysis.capability_fit:.3f}")
    print(f"  BS2 Score: {analysis.bs2_score}/100")
    print(f"  Priority: {analysis.priority}")
    print(f"  Success Rate: {analysis.estimated_success_rate:.1%}")
    print(f"  Recommendation: {analysis.recommended_action}")