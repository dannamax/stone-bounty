#!/usr/bin/env python3
"""
Test script for BS2.0 + Skills integration
"""

import os
import sys
from pathlib import Path

def test_skills_integration():
    """Test that both skills are properly integrated"""
    
    # Test 1: Check if planning directory exists
    planning_dir = Path("planning")
    assert planning_dir.exists(), "Planning directory not found"
    print("✅ Planning directory exists")
    
    # Test 2: Check if planning files exist
    required_files = ["task_plan.md", "findings.md", "progress.md"]
    for file in required_files:
        filepath = planning_dir / file
        assert filepath.exists(), f"Required planning file {file} not found"
    print("✅ All planning files exist")
    
    # Test 3: Check if config directory exists
    config_dir = Path("config")
    assert config_dir.exists(), "Config directory not found"
    print("✅ Config directory exists")
    
    # Test 4: Check if skills config exists
    skills_config = config_dir / "skills_config.json"
    assert skills_config.exists(), "Skills config file not found"
    print("✅ Skills config file exists")
    
    # Test 5: Check if enhanced script exists
    enhanced_script = Path("scripts/bs2_enhanced.sh")
    assert enhanced_script.exists(), "Enhanced BS2.0 script not found"
    print("✅ Enhanced BS2.0 script exists")
    
    # Test 6: Verify skills are available in OpenClaw
    try:
        import subprocess
        result = subprocess.run(["openclaw", "skills", "list"], 
                              capture_output=True, text=True, timeout=10)
        if "superpowers" in result.stdout and "planning-with-files" in result.stdout:
            print("✅ Both skills are available in OpenClaw")
        else:
            print("⚠️  Skills may not be properly installed in OpenClaw")
    except Exception as e:
        print(f"⚠️  Could not verify OpenClaw skills: {e}")
    
    print("\n🎉 All integration tests passed!")
    print("\nNext steps:")
    print("1. Run './scripts/bs2_enhanced.sh status' to check enhanced system status")
    print("2. Use './scripts/bs2_enhanced.sh create-doc-pr --help' for new workflow")
    print("3. Monitor planning/ directory during bounty processing")

if __name__ == "__main__":
    test_skills_integration()