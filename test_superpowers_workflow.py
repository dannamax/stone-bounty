#!/usr/bin/env python3
"""
Superpowers Workflow Integration Test
Tests the complete mandatory Superpowers workflow in BS2.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs2_orchestrator_superpowers import BS2OrchestratorSuperpowers

def test_superpowers_workflow():
    """Test the complete Superpowers workflow"""
    
    print("🧪 Testing Mandatory Superpowers Workflow...")
    
    # Create test bounty
    test_bounty = {
        "id": "555",
        "title": "BoTTube: Social Graph API with Flask Integration Tests",
        "type": "test", 
        "complexity": "MODERATE",
        "reward": "5 RTC"
    }
    
    # Initialize Superpowers orchestrator
    orchestrator = BS2OrchestratorSuperpowers()
    
    # Test mandatory Superpowers workflow
    try:
        result = orchestrator.create_superpowers_workflow(test_bounty)
        print(f"✅ Superpowers workflow result:\n{result}")
        
        # Verify all Superpowers phases are included
        expected_phases = [
            "brainstorming",
            "systematic_debugging", 
            "tdd_implementation",
            "code_review",
            "finishing_branch"
        ]
        
        for phase in expected_phases:
            if phase not in result.lower():
                print(f"❌ Missing Superpowers phase: {phase}")
                return False
        
        print("✅ All Superpowers phases present")
        return True
        
    except Exception as e:
        print(f"❌ Superpowers workflow failed: {e}")
        return False

def test_mandatory_enforcement():
    """Test that Superpowers workflow is mandatory"""
    
    print("🧪 Testing Mandatory Enforcement...")
    
    orchestrator = BS2OrchestratorSuperpowers()
    
    # Try to create traditional workflow (should fail or redirect to Superpowers)
    try:
        result = orchestrator.create_traditional_workflow({"id": "test"})
        if "superpowers" not in result.lower():
            print("❌ Traditional workflow should be disabled")
            return False
        else:
            print("✅ Traditional workflow properly redirected to Superpowers")
            return True
    except Exception as e:
        print(f"✅ Traditional workflow properly blocked: {e}")
        return True

if __name__ == "__main__":
    print("🚀 Running Superpowers Workflow Integration Tests...\n")
    
    success1 = test_superpowers_workflow()
    success2 = test_mandatory_enforcement()
    
    if success1 and success2:
        print("\n🎉 All Superpowers workflow tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)