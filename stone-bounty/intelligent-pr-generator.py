#!/usr/bin/env python3
"""
Intelligent PR Generator - High Quality PRs with Minimal Human Intervention
"""

import json
import re
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class IssueAnalysis:
    issue_number: int
    title: str
    body: str
    labels: List[str]
    issue_type: str
    complexity_score: float
    quality_template: str

class IntelligentPRGenerator:
    def __init__(self):
        self.templates_dir = "templates"
        self.quality_threshold = 0.7  # Minimum quality score to auto-submit
        
    def analyze_issue(self, issue_data: Dict) -> IssueAnalysis:
        """Analyze issue and determine if it's suitable for automated PR"""
        
        # Extract issue information
        issue_number = issue_data.get('number')
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        labels = [label.get('name', '') for label in issue_data.get('labels', [])]
        
        # Determine issue type and complexity
        issue_type, complexity_score = self._classify_issue(title, body, labels)
        quality_template = self._select_template(issue_type, complexity_score)
        
        return IssueAnalysis(
            issue_number=issue_number,
            title=title,
            body=body,
            labels=labels,
            issue_type=issue_type,
            complexity_score=complexity_score,
            quality_template=quality_template
        )
    
    def _classify_issue(self, title: str, body: str, labels: List[str]) -> tuple:
        """Classify issue type and estimate complexity"""
        
        title_lower = title.lower()
        body_lower = body.lower()
        labels_lower = [label.lower() for label in labels]
        
        # Check for documentation issues
        doc_keywords = ['doc', 'documentation', 'readme', 'guide', 'tutorial', 'api reference']
        if any(keyword in title_lower or keyword in body_lower for keyword in doc_keywords):
            return 'documentation', 0.2  # Low complexity
            
        # Check for test issues  
        test_keywords = ['test', 'testing', 'coverage', 'unit test', 'integration test']
        if any(keyword in title_lower or keyword in body_lower for keyword in test_keywords):
            return 'test', 0.3  # Low-medium complexity
            
        # Check for good first issue
        if 'good first issue' in labels_lower or 'beginner' in labels_lower:
            return 'small_feature', 0.4  # Medium complexity
            
        # Check for bug fixes (simple ones only)
        bug_keywords = ['fix', 'bug', 'error', 'crash', 'typo']
        if any(keyword in title_lower for keyword in bug_keywords) and len(body) < 500:
            return 'small_feature', 0.5  # Medium complexity
            
        # Everything else is too complex for automation
        return 'complex', 1.0
    
    def _select_template(self, issue_type: str, complexity_score: float) -> str:
        """Select appropriate template based on issue type"""
        
        if complexity_score > 0.6:
            return None  # Too complex, skip automation
            
        template_map = {
            'documentation': 'TEMPLATE_DOCS.md',
            'test': 'TEMPLATE_TESTS.md', 
            'small_feature': 'TEMPLATE_SMALL_FEATURE.md'
        }
        
        return template_map.get(issue_type)
    
    def generate_pr_content(self, analysis: IssueAnalysis, repo_info: Dict) -> Optional[Dict]:
        """Generate high-quality PR content using selected template"""
        
        if not analysis.quality_template:
            return None
            
        # Load template
        template_path = os.path.join(self.templates_dir, analysis.quality_template)
        if not os.path.exists(template_path):
            return None
            
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Fill template with issue-specific information
        pr_content = self._fill_template(template_content, analysis, repo_info)
        
        # Validate quality before returning
        if self._validate_quality(pr_content, analysis):
            return pr_content
        else:
            return None
    
    def _fill_template(self, template: str, analysis: IssueAnalysis, repo_info: Dict) -> str:
        """Fill template with actual issue and repository information"""
        
        # Extract repository info
        repo_name = repo_info.get('name', '')
        main_branch = repo_info.get('default_branch', 'main')
        
        # Fill basic placeholders
        filled_template = template.replace('[issue_number]', str(analysis.issue_number))
        filled_template = filled_template.replace('[repository]', repo_name)
        filled_template = filled_template.replace('[main_branch]', main_branch)
        
        # For documentation template
        if 'API Reference' in analysis.title:
            filled_template = filled_template.replace('[api_endpoints]', self._extract_api_endpoints(analysis.body))
            
        # Add more sophisticated template filling logic here
        # This would include actual code generation, file path detection, etc.
        
        return filled_template
    
    def _extract_api_endpoints(self, issue_body: str) -> str:
        """Extract API endpoints from issue description"""
        # This would parse the actual API endpoints mentioned in the issue
        return "All public and admin endpoints as described in the issue"
    
    def _validate_quality(self, pr_content: str, analysis: IssueAnalysis) -> bool:
        """Validate that generated PR meets quality standards"""
        
        # Quality checks
        quality_checks = [
            len(pr_content) > 500,  # Minimum length
            '[placeholder]' not in pr_content.lower(),  # No placeholders
            'fixes #' + str(analysis.issue_number) in pr_content.lower(),  # References issue
            analysis.complexity_score <= 0.6  # Not too complex
        ]
        
        return all(quality_checks)

def main():
    """Main function to demonstrate intelligent PR generation"""
    generator = IntelligentPRGenerator()
    
    # Example issue data (would come from GitHub API in real usage)
    example_issue = {
        'number': 213,
        'title': '📚 API Reference — Official Endpoint Documentation',
        'body': 'Need comprehensive API documentation covering all endpoints...',
        'labels': [{'name': 'documentation'}, {'name': 'bounty'}]
    }
    
    example_repo = {
        'name': 'Scottcjn/Rustchain',
        'default_branch': 'main'
    }
    
    # Analyze issue
    analysis = generator.analyze_issue(example_issue)
    print(f"Issue Type: {analysis.issue_type}")
    print(f"Complexity Score: {analysis.complexity_score}")
    print(f"Quality Template: {analysis.quality_template}")
    
    # Generate PR content
    if analysis.quality_template:
        pr_content = generator.generate_pr_content(analysis, example_repo)
        if pr_content:
            print("✅ High-quality PR generated successfully!")
            # In real usage, this would create actual files and submit PR
        else:
            print("❌ PR generation failed quality validation")
    else:
        print("❌ Issue too complex for automated PR")

if __name__ == "__main__":
    main()