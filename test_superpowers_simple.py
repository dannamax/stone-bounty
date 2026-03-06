#!/usr/bin/env python3
"""
Simple test for Superpowers workflow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs2_orchestrator_superpowers import BS2OrchestratorSuperpowers

def test_superpowers_workflow():
    """Test Superpowers workflow integration"""
    print("🚀 Testing Superpowers Workflow Integration...")
    
    try:
        # Initialize orchestrator
        orchestrator = BS2OrchestratorSuperpowers()
        print("✅ Superpowers orchestrator initialized successfully")
        
        # Test configuration loading
        config = orchestrator.config
        if config.get("superpowers", {}).get("mandatory_workflow", False):
            print("✅ Mandatory Superpowers workflow is enabled")
        else:
            print("⚠️  Mandatory Superpowers workflow is not enabled")
            
        # Test status display
        orchestrator.show_status()
        print("✅ Status display working")
        
        return True
        
    except Exception as e:
        print(f"❌ Superpowers workflow test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_superpowers_workflow()
    if success:
        print("\n🎉 Superpowers workflow integration test PASSED!")
    else:
        print("\n❌ Superpowers workflow integration test FAILED!")
        sys.exit(1)