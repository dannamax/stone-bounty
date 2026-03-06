#!/usr/bin/env python3
"""
Simple Superpowers workflow test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs2_orchestrator_superpowers import BS2OrchestratorSuperpowers

def test_superpowers():
    """Test Superpowers orchestrator initialization"""
    try:
        print("🚀 Testing Superpowers Workflow Integration...")
        
        # Initialize orchestrator
        orchestrator = BS2OrchestratorSuperpowers()
        print("✅ Superpowers orchestrator initialized successfully")
        
        # Check configuration
        if orchestrator.config.get("superpowers", {}).get("mandatory_workflow", False):
            print("✅ Mandatory Superpowers workflow is enabled")
        else:
            print("⚠️  Mandatory Superpowers workflow is NOT enabled")
            
        print("✅ Superpowers workflow integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Superpowers workflow test failed: {e}")
        print("❌ Superpowers workflow integration test FAILED!")
        return False

if __name__ == "__main__":
    success = test_superpowers()
    sys.exit(0 if success else 1)