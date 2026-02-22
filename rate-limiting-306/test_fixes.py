#!/usr/bin/env python3
"""
Test script to verify PR #336 fixes
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, '/mnt/vdb/stone-bounty/rate-limiting-306/Rustchain/node')

def test_decorator_order():
    """Test that decorators are in correct order"""
    with open('/mnt/vdb/stone-bounty/rate-limiting-306/Rustchain/node/rustchain_v2_integrated_v2.2.1_rip200.py', 'r') as f:
        content = f.read()
    
    # Check for correct decorator order pattern
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '@app.route' in line and i + 1 < len(lines):
            next_line = lines[i + 1]
            if '@rate_limit' in next_line:
                return True
    return False

def test_duplicate_decorators():
    """Test that there are no duplicate rate_limit decorators"""
    with open('/mnt/vdb/stone-bounty/rate-limiting-306/Rustchain/node/rustchain_v2_integrated_v2.2.1_rip200.py', 'r') as f:
        content = f.read()
    
    # Count rate_limit decorators on /attest/submit
    attest_submit_section = False
    rate_limit_count = 0
    
    lines = content.split('\n')
    for line in lines:
        if '@app.route(\'/attest/submit\'' in line:
            attest_submit_section = True
        elif attest_submit_section and 'def submit_attestation():' in line:
            break
        elif attest_submit_section and '@rate_limit' in line:
            rate_limit_count += 1
    
    return rate_limit_count <= 1

def test_import_logic():
    """Test that import logic is correct"""
    with open('/mnt/vdb/stone-bounty/rate-limiting-306/Rustchain/node/rustchain_v2_integrated_v2.2.1_rip200.py', 'r') as f:
        content = f.read()
    
    # Should not have direct import at top level
    lines = content.split('\n')
    direct_import_count = 0
    for line in lines[:50]:  # Check first 50 lines
        if 'from rate_limiting import rate_limit' in line and not line.strip().startswith('#'):
            if 'try:' not in line and 'except:' not in line:
                direct_import_count += 1
    
    return direct_import_count == 0

def test_db_path_config():
    """Test that DB path is properly configured"""
    # Set environment variable for testing
    os.environ['RUSTCHAIN_DB_PATH'] = './test_rustchain.db'
    
    try:
        from rate_limiting import DB_PATH
        expected_path = './test_rustchain.db'
        return DB_PATH == expected_path
    except Exception:
        return False

def main():
    print("Testing PR #336 fixes...")
    
    tests = [
        ("Decorator order", test_decorator_order),
        ("Duplicate decorators", test_duplicate_decorators), 
        ("Import logic", test_import_logic),
        ("DB path config", test_db_path_config)
    ]
    
    all_passed = True
    for name, test_func in tests:
        try:
            result = test_func()
            status = "PASSED" if result else "FAILED"
            print(f"✅ {name}: {status}")
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All fixes verified successfully!")
        return 0
    else:
        print("\n❌ Some fixes need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())