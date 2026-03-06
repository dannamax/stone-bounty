#!/usr/bin/env python3
"""
Main entry point for Automated Bounty Hunter System
"""

import sys
from pathlib import Path

# Add BS2 system to path
bs2_path = Path(__file__).parent
sys.path.insert(0, str(bs2_path))

from auto_bounty_hunter import AutoBountyHunter

def main():
    """Run the automated bounty hunter system"""
    print("🤖 Starting Automated Bounty Hunter System...")
    print("=" * 60)
    
    # Initialize the automated bounty hunter
    hunter = AutoBountyHunter()
    
    # Run the automated cycle
    try:
        hunter.run_automated_cycle()
        print("✅ Automated bounty hunting cycle completed successfully!")
    except Exception as e:
        print(f"❌ Error in automated bounty hunting: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()