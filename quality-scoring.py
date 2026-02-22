#!/usr/bin/env python3
"""
Quality Scoring System for High-Quality PR Generation
Automatically evaluates PR quality before submission
"""

import json
import re
from typing import Dict, List, Tuple

class QualityScorer:
    def __init__(self):
        self.weights = {
            'issue_relevance': 0.25,
            'code_quality': 0.20,
            'test_coverage': 0.20,
            'documentation': 0.15,
            'maintainer_friendly': 0.20
        }
        
    def score_pr(self, pr_data: Dict) -> Dict:
        """Score PR quality and return detailed analysis"""
        scores = {}
        
        # Issue relevance scoring
        scores['issue_relevance'] = self._score_issue_relevance(pr_data)
        
        # Code quality scoring  
        scores['code_quality'] = self._score_code_quality(pr_data)
        
        # Test coverage scoring
        scores['test_coverage'] = self._score_test_coverage(pr_data)
        
        # Documentation scoring
        scores['documentation'] = self._score_documentation(pr_data)
        
        # Maintainer friendly scoring
        scores['maintainer_friendly'] = self._score_maintainer_friendly(pr_data)
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * self.weights[key] 
            for key in self.weights
        )
        
        # Determine if PR should be auto-submitted
        auto_submit = total_score >= 0.85  # 85% threshold for auto-submit
        
        return {
            'scores': scores,
            'total_score': total_score,
            'auto_submit': auto_submit,
            'recommendations': self._get_recommendations(scores)
        }
    
    def _score_issue_relevance(self, pr_data: Dict) -> float:
        """Score how well PR addresses the issue"""
        issue_desc = pr_data.get('issue_description', '').lower()
        pr_desc = pr_data.get('pr_description', '').lower()
        pr_files = pr_data.get('changed_files', [])
        
        # Check if PR description mentions specific issue requirements
        relevance_indicators = [
            'fixes' in pr_desc,
            'addresses' in pr_desc, 
            'implements' in pr_desc,
            len(pr_files) > 0
        ]
        
        score = sum(relevance_indicators) / len(relevance_indicators)
        
        # Bonus for specific issue references
        if str(pr_data.get('issue_number', '')) in pr_desc:
            score = min(1.0, score + 0.2)
            
        return score
    
    def _score_code_quality(self, pr_data: Dict) -> float:
        """Score code quality based on changes"""
        changed_files = pr_data.get('changed_files', [])
        if not changed_files:
            return 0.0
            
        # Analyze file types and changes
        code_files = [f for f in changed_files if f.endswith(('.js', '.ts', '.py', '.go', '.rs'))]
        doc_files = [f for f in changed_files if f.endswith(('.md', '.txt'))]
        
        if not code_files and not doc_files:
            return 0.3  # Minimal score for unknown file types
            
        # High score for documentation-only changes (safe)
        if doc_files and not code_files:
            return 0.95
            
        # Score based on change complexity
        total_changes = pr_data.get('total_changes', 0)
        if total_changes == 0:
            return 0.0
        elif total_changes < 10:
            return 0.9  # Small, focused changes
        elif total_changes < 50:
            return 0.7  # Moderate changes
        else:
            return 0.4  # Large changes (higher risk)
    
    def _score_test_coverage(self, pr_data: Dict) -> float:
        """Score test coverage inclusion"""
        changed_files = pr_data.get('changed_files', [])
        test_files = [f for f in changed_files if 'test' in f.lower() or f.endswith(('.spec.js', '.test.js', '_test.py'))]
        
        if test_files:
            return 0.9  # Tests included
        elif any(f.endswith(('.md', '.txt')) for f in changed_files):
            return 0.8  # Documentation doesn't need tests
        else:
            return 0.3  # Code changes without tests
    
    def _score_documentation(self, pr_data: Dict) -> float:
        """Score documentation quality"""
        pr_desc = pr_data.get('pr_description', '')
        checklist_items = pr_desc.count('[x]') + pr_desc.count('✅')
        total_checklist = pr_desc.count('[ ]') + pr_desc.count('[x]') + pr_desc.count('✅') + pr_desc.count('❌')
        
        if total_checklist == 0:
            return 0.5  # No checklist, basic description
            
        completion_rate = checklist_items / total_checklist if total_checklist > 0 else 0
        return min(1.0, 0.6 + completion_rate * 0.4)
    
    def _score_maintainer_friendly(self, pr_data: Dict) -> float:
        """Score how maintainer-friendly the PR is"""
        pr_desc = pr_data.get('pr_description', '')
        changed_files = pr_data.get('changed_files', [])
        
        # Check for clear validation steps
        maintainer_friendly_indicators = [
            'validation' in pr_desc.lower(),
            'steps' in pr_desc.lower(),
            'checklist' in pr_desc.lower(),
            len(changed_files) <= 5,  # Not too many files
            pr_desc.count('\n') >= 10  # Detailed description
        ]
        
        return sum(maintainer_friendly_indicators) / len(maintainer_friendly_indicators)
    
    def _get_recommendations(self, scores: Dict) -> List[str]:
        """Get improvement recommendations based on low scores"""
        recommendations = []
        
        if scores['issue_relevance'] < 0.7:
            recommendations.append("Improve issue relevance by explicitly addressing issue requirements in PR description")
            
        if scores['code_quality'] < 0.6:
            recommendations.append("Reduce code changes to focus on minimal, targeted fixes")
            
        if scores['test_coverage'] < 0.5:
            recommendations.append("Add appropriate test coverage for code changes")
            
        if scores['documentation'] < 0.7:
            recommendations.append("Enhance PR description with detailed checklist and validation steps")
            
        if scores['maintainer_friendly'] < 0.6:
            recommendations.append("Make PR more maintainer-friendly with clear validation instructions")
            
        return recommendations

def main():
    """Example usage"""
    scorer = QualityScorer()
    
    # Example PR data
    example_pr = {
        'issue_number': 213,
        'issue_description': 'Create comprehensive API reference documentation',
        'pr_description': '''Fixes #213

This PR provides a complete, up-to-date API reference documentation that covers:

- [x] All public endpoints (/health, /ready, /epoch, /api/miners, /wallet/balance, /explorer)
- [x] Authenticated admin endpoints (/wallet/transfer, /rewards/settle)
- [x] Detailed request/response examples with actual curl commands
- [x] Common mistakes and field name clarifications
- [x] Wallet format rules and validation
- [x] HTTPS certificate handling instructions
- [x] Response status codes and error handling
- [x] Node infrastructure details

Validation Steps:
1. Review documentation accuracy against live API
2. Verify all examples work with actual curl commands
3. Check OpenAPI specification validity
4. Ensure consistent formatting and style''',
        'changed_files': ['docs/API_REFERENCE.md', 'docs/api/openapi.yaml', 'docs/API_REFERENCE_README.md'],
        'total_changes': 1200
    }
    
    result = scorer.score_pr(example_pr)
    print(f"Total Quality Score: {result['total_score']:.2f}")
    print(f"Auto-submit recommended: {result['auto_submit']}")
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    main()