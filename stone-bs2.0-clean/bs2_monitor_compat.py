#!/usr/bin/env python3
"""
BS2.0 Compatible Monitor Module for Python 3.6+
Integrates bounty hunter skill's monitoring capabilities
"""

import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any

class BS2Monitor:
    """Compatible monitor for Python 3.6+"""
    
    def __init__(self, github_token=""):
        self.token = github_token
        self.RTC_USD_REF = 0.10
    
    def _gh_get(self, path, token=""):
        """GitHub API GET request"""
        base = "https://api.github.com"
        url = path if path.startswith("http") else f"{base}{path}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "bs2-monitor")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    
    def _gh_get_safe(self, path, token="", fallback=None):
        """Safe GitHub API GET request"""
        try:
            return self._gh_get(path, token=token)
        except Exception:
            return fallback
    
    def monitor_submissions(self, owner="Scottcjn", repo="rustchain-bounties", handle="dannamax"):
        """Monitor submissions for a specific handle"""
        try:
            # Search for issues commented by the handle
            search_q = urllib.parse.quote(f"repo:{owner}/{repo} commenter:{handle}")
            found = self._gh_get_safe(f"/search/issues?q={search_q}&per_page=100", self.token, fallback={})
            items = found.get("items", []) if isinstance(found, dict) else []
            
            if not isinstance(items, list):
                return {"error": "Invalid response from GitHub API"}
            
            results = []
            for item in items[:20]:  # Limit to 20 items
                issue_no = item.get("number")
                issue_repo = ((item.get("repository_url", "") or "").split("/repos/")[-1]) if item.get("repository_url") else ""
                
                if not issue_repo or not issue_no:
                    continue
                
                # Get issue details
                issue = self._gh_get_safe(f"/repos/{issue_repo}/issues/{issue_no}", self.token, fallback={})
                issue_state = issue.get("state", "unknown")
                
                # Get comments to check for PR links and payout signals
                comments = self._gh_get_safe(f"/repos/{issue_repo}/issues/{issue_no}/comments?per_page=100", self.token, fallback=[])
                payout_signal = "none"
                pr_links = []
                
                if isinstance(comments, list):
                    comment_text = "\n".join((c.get("body", "") or "").lower() for c in comments)
                    
                    # Check for payout signals
                    if any(k in comment_text for k in ("payout queued", "queued id", "pending id")):
                        payout_signal = "queued"
                    elif any(k in comment_text for k in ("paid", "payout sent", "confirmed payout")):
                        payout_signal = "paid"
                    elif any(k in comment_text for k in ("changes requested", "please update", "partial progress")):
                        payout_signal = "needs_update"
                    
                    # Extract PR links
                    import re
                    pr_urls = re.findall(r"https://github\.com/([^/\s]+/[^/\s]+)/pull/(\d+)", "\n".join(c.get("body", "") or "" for c in comments))
                    for pr_repo, pr_no in pr_urls:
                        pr_links.append(f"https://github.com/{pr_repo}/pull/{pr_no}")
                
                results.append({
                    "issue": f"https://github.com/{issue_repo}/issues/{issue_no}",
                    "issue_state": issue_state,
                    "pr_links": pr_links,
                    "payout_signal": payout_signal,
                    "title": item.get("title", "")
                })
            
            return {"monitoring_results": results, "count": len(results)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def scan_bounties(self, owner="Scottcjn", repo="rustchain-bounties", top=10, min_usd=0.0):
        """Scan and rank open bounties"""
        try:
            labels = urllib.parse.quote("bounty")
            items = self._gh_get(f"/repos/{owner}/{repo}/issues?state=open&labels={labels}&per_page=100", self.token)
            
            if not isinstance(items, list):
                return {"error": "Invalid response from GitHub API"}
            
            # Filter out PRs
            issues = [i for i in items if "pull_request" not in i]
            
            leads = []
            for i in issues:
                title = i.get("title", "")
                body = i.get("body", "") or ""
                
                # Parse reward (simplified version for Python 3.6)
                reward_rtc, reward_usd = self._parse_reward_simple(body, title)
                
                if reward_usd < min_usd:
                    continue
                
                # Simple difficulty estimation
                difficulty = self._estimate_difficulty_simple(title, body)
                fit = self._capability_fit_simple(title, body)
                score = self._rank_score_simple(reward_usd, difficulty, fit)
                
                leads.append({
                    "number": i["number"],
                    "title": title,
                    "url": i["html_url"],
                    "updated_at": i.get("updated_at", ""),
                    "reward_rtc": round(reward_rtc, 3),
                    "reward_usd": round(reward_usd, 2),
                    "difficulty": difficulty,
                    "capability_fit": round(fit, 3),
                    "score": score,
                })
            
            # Sort by score
            leads.sort(key=lambda x: x["score"], reverse=True)
            return {"leads": leads[:top], "count": len(leads[:top])}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_reward_simple(self, body, title):
        """Simple reward parsing for Python 3.6"""
        text = f"{title}\n{body}".lower()
        reward_rtc = 0.0
        reward_usd = 0.0
        
        # Look for RTC amounts
        import re
        rtc_match = re.search(r'(\d+(?:-\d+)?)\s*rtc', text)
        usd_match = re.search(r'\$(\d+)', text)
        
        if rtc_match:
            reward_rtc = float(rtc_match.group(1).split('-')[0])
            reward_usd = reward_rtc * self.RTC_USD_REF
        elif usd_match:
            reward_usd = float(usd_match.group(1))
            reward_rtc = reward_usd / self.RTC_USD_REF
        
        return reward_rtc, reward_usd
    
    def _estimate_difficulty_simple(self, title, body):
        """Simple difficulty estimation"""
        text = f"{title}\n{body}".lower()
        if any(t in text for t in ["critical", "security", "red team", "hardening", "consensus"]):
            return "high"
        elif any(t in text for t in ["standard", "dashboard", "tool", "api", "integration"]):
            return "medium"
        else:
            return "low"
    
    def _capability_fit_simple(self, title, body):
        """Simple capability fit calculation"""
        text = f"{title}\n{body}".lower()
        plus_terms = ["documentation", "docs", "readme", "tutorial", "python", "script"]
        minus_terms = ["real hardware", "3d", "webgl", "physical"]
        
        score = 0.5
        for term in plus_terms:
            if term in text:
                score += 0.06
        for term in minus_terms:
            if term in text:
                score -= 0.08
        
        return max(0.0, min(1.0, score))
    
    def _rank_score_simple(self, reward_usd, diff, fit):
        """Simple rank score calculation"""
        diff_penalty = {"low": 0.0, "medium": 0.8, "high": 1.6}[diff]
        return round((reward_usd / 25.0) + (fit * 3.0) - diff_penalty, 3)

if __name__ == "__main__":
    # Test the monitor
    import sys
    token = sys.argv[1] if len(sys.argv) > 1 else ""
    monitor = BS2Monitor(token)
    
    print("🔍 Scanning bounties...")
    bounty_results = monitor.scan_bounties(top=5)
    print(json.dumps(bounty_results, indent=2))
    
    print("\n📊 Monitoring submissions...")
    monitor_results = monitor.monitor_submissions()
    print(json.dumps(monitor_results, indent=2))