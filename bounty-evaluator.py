#!/usr/bin/env python3
"""
Bounty Opportunity Evaluator
Evaluates bounty opportunities based on project suitability criteria
"""

import json
import sys
from datetime import datetime

def load_config():
    """Load configuration from config.yaml"""
    config = {
        "blacklisted_repos": [
            "rust-lang/rust",
            "torvalds/linux", 
            "microsoft/vscode",
            "vuejs/vue",
            "facebook/react",
            "golang/go",
            "nodejs/node"
        ],
        "preferred_repo_criteria": {
            "max_stars": 10000,
            "min_issues_with_bounties": 1,
            "has_clear_contribution_guide": True,
            "responsive_maintainers": True,
            "accepts_documentation_prs": True
        },
        "issue_type_preferences": {
            "preferred": ["documentation", "good-first-issue", "bug", "enhancement"],
            "avoid": ["compiler", "build-system", "core-architecture", "security-critical"]
        },
        "pr_quality_checks": {
            "require_actual_code_changes": True,
            "avoid_submodule_changes": True,
            "validate_commit_message_format": True,
            "require_tests_for_code_changes": True,
            "check_style_compliance": True
        }
    }
    return config

def evaluate_opportunity(opportunity, config):
    """Evaluate a single opportunity"""
    repo = opportunity.get('repo', '')
    stars = opportunity.get('stars', 0)
    issue_type = opportunity.get('issue_type', '')
    status = opportunity.get('status', '')
    
    # Skip already successful opportunities
    if status == 'SUCCESS':
        return {
            'repo': repo,
            'recommendation': 'KEEP',
            'reason': 'Already successful',
            'score': 100
        }
    
    # Check blacklist
    if repo in config['blacklisted_repos']:
        return {
            'repo': repo,
            'recommendation': 'AVOID',
            'reason': 'Blacklisted repository (too complex/large)',
            'score': 0
        }
    
    # Check star count
    if stars > config['preferred_repo_criteria']['max_stars']:
        return {
            'repo': repo,
            'recommendation': 'AVOID',
            'reason': f'Too many stars ({stars} > {config["preferred_repo_criteria"]["max_stars"]})',
            'score': 20
        }
    
    # Check issue type
    if issue_type in config['issue_type_preferences']['avoid']:
        return {
            'repo': repo,
            'recommendation': 'AVOID',
            'reason': f'Issue type "{issue_type}" should be avoided',
            'score': 10
        }
    
    if issue_type in config['issue_type_preferences']['preferred']:
        score = 80
        reason = f'Preferred issue type: {issue_type}'
    else:
        score = 50
        reason = f'Neutral issue type: {issue_type}'
    
    return {
        'repo': repo,
        'recommendation': 'CONSIDER' if score >= 60 else 'AVOID',
        'reason': reason,
        'score': score
    }

def main():
    print("Bounty Opportunity Evaluator initialized")
    config = load_config()
    print(f"Configuration loaded with {len(config['blacklisted_repos'])} blacklisted repos")
    
    # Load current opportunities
    try:
        with open('current-opportunities.json', 'r') as f:
            data = json.load(f)
            opportunities = data.get('opportunities', [])
    except FileNotFoundError:
        print("No current-opportunities.json found")
        opportunities = []
    
    print(f"Evaluating {len(opportunities)} opportunities...")
    
    results = []
    for opp in opportunities:
        result = evaluate_opportunity(opp, config)
        results.append(result)
        print(f"- {result['repo']}: {result['recommendation']} ({result['score']}/100) - {result['reason']}")
    
    # Save results
    evaluation_result = {
        'timestamp': datetime.now().isoformat(),
        'config_summary': {
            'blacklisted_count': len(config['blacklisted_repos']),
            'max_stars_threshold': config['preferred_repo_criteria']['max_stars']
        },
        'evaluations': results,
        'summary': {
            'keep': len([r for r in results if r['recommendation'] == 'KEEP']),
            'consider': len([r for r in results if r['recommendation'] == 'CONSIDER']),
            'avoid': len([r for r in results if r['recommendation'] == 'AVOID'])
        }
    }
    
    with open('evaluation-results.json', 'w') as f:
        json.dump(evaluation_result, f, indent=2)
    
    print(f"\nEvaluation complete!")
    print(f"Summary: {evaluation_result['summary']['keep']} keep, {evaluation_result['summary']['consider']} consider, {evaluation_result['summary']['avoid']} avoid")
    print("Results saved to evaluation-results.json")

if __name__ == "__main__":
    main()