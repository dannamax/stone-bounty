#!/usr/bin/env python3
"""
Test script for RustChain Badge API endpoint
"""
import sys
import os

# Add the node directory to Python path
sys.path.insert(0, '/mnt/vdb/stone-bounty/docs-improvement-304/rustchain-docs/node')

try:
    from rustchain_v2_integrated_v2_2_1_rip200 import get_badge_data
    
    # Test with a sample wallet
    test_wallet = "frozen-factorio-ryan"
    badge_data = get_badge_data(test_wallet)
    
    print("✅ Badge API function works correctly!")
    print(f"Badge data: {badge_data}")
    
    # Validate required fields
    required_fields = ["schemaVersion", "label", "message", "color"]
    for field in required_fields:
        if field not in badge_data:
            print(f"❌ Missing required field: {field}")
            sys.exit(1)
    
    print("✅ All required fields present!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("✅ Badge API test passed!")