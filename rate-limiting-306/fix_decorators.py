#!/usr/bin/env python3
"""
Fix decorator order and duplicate decorators in rustchain_v2_integrated_v2.2.1_rip200.py
"""

import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix 1: Remove duplicate imports at top
    # Remove the direct import from top if it exists
    content = re.sub(r'from rate_limiting import rate_limit\n', '', content, count=1)
    
    # Fix 2: Fix decorator order - move @rate_limit below @app.route
    # Pattern: @rate_limit(...) followed by @app.route(...)
    pattern = r'(@rate_limit\([^)]*\))\s*\n\s*(@app\.route\([^)]*\))'
    content = re.sub(pattern, r'\2\n\1', content)
    
    # Fix 3: Remove duplicate @rate_limit decorators on same endpoint
    # Look for consecutive @rate_limit lines
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('@rate_limit(') and i + 1 < len(lines):
            next_line = lines[i + 1]
            if next_line.strip().startswith('@rate_limit('):
                # Skip duplicate
                i += 1
                continue
        new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    
    # Write back to file
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✅ Decorator fixes applied successfully!")

if __name__ == "__main__":
    fix_file("Rustchain/node/rustchain_v2_integrated_v2.2.1_rip200.py")