#!/usr/bin/env python3
"""
Superpowers Workflow Integration Tests
Tests the mandatory Superpowers workflow enforcement in BS2.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs2_orchestrator_superpowers import BS2OrchestratorSuperpowers

def test_mandatory_superpowers_workflow():
    """Test that Superpowers workflow is properly enforced"""
    print("🧪 Testing Mandatory Superpowers Workflow...")
    
    # Create test bounty
    test_bounty = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "type": "test",
        "complexity": "MODERATE",
        "reward": "5 RTC"
    }
    
    # Initialize enhanced orchestrator
    orchestrator = BS2OrchestratorSuperpowers()
    
    try:
        # This should work - Superpowers workflow
        result = orchestrator.process_bounty_with_superpowers(test_bounty)
        print(f"✅ Superpowers workflow executed successfully")
        print(f"Result: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Superpowers workflow failed: {e}")
        return False

def test_mandatory_enforcement():
    """Test that traditional workflow is blocked"""
    print("🧪 Testing Mandatory Enforcement...")
    
    orchestrator = BS2OrchestratorSuperpowers()
    
    try:
        # This should be blocked
        result = orchestrator.create_traditional_workflow({"id": "test"})
        print(f"❌ Traditional workflow should be blocked but succeeded: {result}")
        return False
    except AttributeError:
        print("✅ Traditional workflow properly blocked")
        return True
    except Exception as e:
        print(f"✅ Traditional workflow blocked with error: {e}")
        return True

def main():
    """Run all Superpowers workflow tests"""
    print("🚀 Running Superpowers Workflow Integration Tests...\n")
    
    test1_passed = test_mandatory_superpowers_workflow()
    test2_passed = test_mandatory_enforcement()
    
    if test1_passed and test2_passed:
        print("\n🎉 All Superpowers workflow tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)