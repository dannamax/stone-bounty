#!/usr/bin/env python3
"""
Debug script to identify the exact location of the error
"""

import sys
from pathlib import Path

# Add BS2 system to path
bs2_path = Path(__file__).parent
sys.path.insert(0, str(bs2_path))

from bounty_discovery import BountyDiscovery
from bounty_analyzer import BountyAnalyzer

def debug_analysis():
    print("🔍 Starting debug analysis...")
    
    # Create discovery and analyzer
    discovery = BountyDiscovery("/home/admin/.openclaw/workspace")
    analyzer = BountyAnalyzer()
    
    # Get bounties
    print("📥 Fetching bounties...")
    bounties = discovery.scan_bounties()
    print(f"✅ Found {len(bounties)} bounties")
    
    # Analyze first few bounties
    for i, bounty in enumerate(bounties[:3]):
        print(f"\n--- Analyzing bounty {i+1} ---")
        print(f"Bounty ID: {bounty.id}")
        print(f"Bounty type: {type(bounty)}")
        
        try:
            analysis = analyzer.analyze_bounty(bounty)
            print(f"Analysis type: {type(analysis)}")
            print(f"BS2 Score: {analysis.bs2_score}")
            print(f"Priority: {analysis.priority}")
        except Exception as e:
            print(f"❌ Error analyzing bounty: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    debug_analysis()